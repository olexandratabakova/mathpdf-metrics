"""Wildflower: ordinary MathPDF generation, unchanged historical card metrics.

Read-only MathPDF imports. No workspace, server, database or production account.
An isolated resumable ledger reserves each request before dispatch, never retries.
"""
import argparse
import asyncio
import base64
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
CHECKOUT=PROJECT.parent/'mathPDF-review'
OUT=ROOT/'output'
SOURCE=Path('C:/Users/kotya/Downloads/main (13).pdf')
BUDGET=.75
GENERATOR='gpt-4.1-mini'
JUDGE='gpt-4o-mini'
RATES={GENERATOR:(.4,.1,1.6),JUDGE:(.15,.075,.6)}
TOPICS=[('sets','Sets',list(range(4,8))),('induction','Mathematical Induction',list(range(14,20))),
        ('numbers','Numbers',list(range(22,28))),('functions','Functions',list(range(63,71)))]

def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def prompt_hashes():return {p.name:sha(p.read_bytes()) for p in (CHECKOUT/'formula_lab/prompts').glob('*.md')}
def text_blocks(blocks):return '\n'.join(b.get('text',b.get('latex','')) for b in blocks)

class BudgetClient:
    def __init__(self,key):
        from openai import AsyncOpenAI
        self.client=AsyncOpenAI(api_key=key,max_retries=0,timeout=150)
        self.lock=asyncio.Lock()
        self.sem=asyncio.Semaphore(3)
        self.path=OUT/'ledger.json'
        self.ledger=read(self.path) if self.path.exists() else {'budget_usd':BUDGET,'calls':[]}
    async def request(self,name,payload,cap=None,embedding=False):
        # Full input/PDF payloads never leave ignored output; public manifests use hashes.
        digest=sha(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode())
        path=OUT/'calls'/f'{name}-{digest}.json'
        if path.exists():
            saved=read(path)
            if saved.get('status')=='completed':return saved
            raise RuntimeError(f'{name}: previous incomplete/failed call; no automatic retry')
        async with self.sem:
            if embedding:
                import tiktoken
                enc=tiktoken.get_encoding('cl100k_base')
                reserve=sum(len(enc.encode(x)) for x in payload['input'])*.02/1e6*1.2+.00001
            elif any(x.get('type')=='input_file' for entry in payload.get('input',[]) if isinstance(entry,dict) for x in entry.get('content',[]) if isinstance(x,dict)):
                counted=await self.client.responses.input_tokens.count(**payload)
                reserve=(counted.input_tokens*1.1*RATES[payload['model']][0]+cap*RATES[payload['model']][2])/1e6
            else:
                import tiktoken
                enc=tiktoken.get_encoding('cl100k_base')
                tokens=len(enc.encode(json.dumps(payload,ensure_ascii=False)))
                reserve=(tokens*1.25*RATES[payload['model']][0]+cap*RATES[payload['model']][2])/1e6
            async with self.lock:
                if any(x['digest']==digest and x['name']==name for x in self.ledger['calls']):raise RuntimeError('Request already reserved')
                spent=sum(x.get('cost_usd',x['reserved_usd']) for x in self.ledger['calls'])
                if spent+reserve>BUDGET:raise RuntimeError(f'Budget cap: ${spent:.4f} + ${reserve:.4f} > ${BUDGET}')
                entry={'name':name,'digest':digest,'reserved_usd':reserve,'status':'reserved','model':payload['model']}
                self.ledger['calls'].append(entry);write(self.path,self.ledger)
                write(path,{'status':'reserved','input_sha256':digest})
            started=time.monotonic()
            try:
                if embedding:
                    response=await self.client.embeddings.create(**payload)
                    usage=response.usage.model_dump();cost=usage['total_tokens']*.02/1e6
                    result={'status':'completed','vectors':[x.embedding for x in sorted(response.data,key=lambda x:x.index)]}
                else:
                    response=await self.client.responses.create(**payload,max_output_tokens=cap,store=False)
                    usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens'];ri,rc,ro=RATES[payload['model']]
                    cost=((usage['input_tokens']-cached)*ri+cached*rc+usage['output_tokens']*ro)/1e6
                    result={'status':response.status,'raw_output':response.output_text,'resolved_model':response.model}
                result.update(usage=usage,cost_usd=cost,input_sha256=digest,duration_seconds=round(time.monotonic()-started,2))
                write(path,result)
                async with self.lock:
                    entry.update(status=result['status'],cost_usd=cost,usage=usage);write(self.path,self.ledger)
                if result['status']!='completed':raise RuntimeError('Incomplete response; original retained, no retry')
                print(json.dumps({'stage':name,'cost_usd':round(cost,6),'total_usd':round(sum(x.get('cost_usd',x['reserved_usd']) for x in self.ledger['calls']),6)}),flush=True)
                return result
            except BaseException as exc:
                async with self.lock:
                    if entry['status']=='reserved':entry.update(status='unknown_or_failed_no_retry',error_type=type(exc).__name__);write(self.path,self.ledger)
                raise

async def generate(api,selected):
    from formula_lab.workspace import Document
    from formula_lab.study import GenerateRequest,InputDocument,load_prompts,selected_pdf,GeneratedContent,validate_study,question_fingerprint
    from formula_lab.providers import set_response_format
    from openai import pydantic_function_tool
    source_hash=sha(SOURCE.read_bytes())
    for slug,topic,pages in TOPICS:
        if selected and selected!=slug:continue
        pdf=selected_pdf(SOURCE,pages)
        doc=Document(id='a'*32,filename=SOURCE.name,sha256=source_hash,media_type='application/pdf',page_count=74,size=SOURCE.stat().st_size)
        for mode,count in [('flashcards',15),('problems',10)]:
            target=OUT/f'{slug}-{mode}.json'
            if target.exists():continue
            request=GenerateRequest(document_id=doc.id,pages=pages,mode=mode,count=count,difficulty=3)
            documents=[InputDocument(document=doc,data=pdf,filename=f'{slug}-selected.pdf',role='source',pages=pages)]
            system,task,hashes=load_prompts(request,documents)
            for name in hashes:
                dest=ROOT/'generator-prompts'/name;dest.parent.mkdir(exist_ok=True)
                data=(CHECKOUT/'formula_lab/prompts'/name).read_bytes()
                if dest.exists():assert dest.read_bytes()==data,'Frozen prompt changed'
                else:dest.write_bytes(data)
            fn=pydantic_function_tool(set_response_format(count,mode))['function']
            payload={'model':GENERATOR,'instructions':system,'input':[{'role':'user','content':[
                {'type':'input_text','text':documents[0].label},
                {'type':'input_file','filename':documents[0].filename,'file_data':'data:application/pdf;base64,'+base64.b64encode(pdf).decode()},
                {'type':'input_text','text':task}]}],
                'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
            saved=await api.request(f'generate-{slug}-{mode}',payload,min(30000,1000+(650 if mode=='flashcards' else 1000)*count))
            parsed=set_response_format(count,mode,permissive=True).model_validate_json(saved['raw_output']).result
            if parsed.status!='completed':raise RuntimeError('Source insufficient; no forced padding')
            items=[x.expand(doc.id,i,mode) for i,x in enumerate(parsed.items,1)]
            validate_study(GeneratedContent(items=items,notes=[]),mode,doc.id,pages)
            assert len({question_fingerprint(x) for x in items})==count,'Site duplicate guard'
            write(target,{**saved,'topic':topic,'pages':pages,'mode':mode,'count':count,'difficulty':3,'prompt_hashes':hashes,
                'compact':parsed.model_dump(mode='json'),'items':[x.model_dump(mode='json') for x in items],
                'source_sha256':source_hash,'selected_pdf_sha256':sha(pdf),'site_guards_passed':True})

async def evaluate(api,selected):
    from openai import pydantic_function_tool
    from pypdf import PdfReader
    import flashcard_evaluator.evaluator as ev
    from flashcard_evaluator.models import CardSet,Flashcard
    reader=PdfReader(SOURCE)
    async def llm_call(system,user,response_model,model=None,use_cache=True,details_log=None):
        fn=pydantic_function_tool(response_model)['function']
        cap={'_BlindResult':500,'_CompareResult':100,'_FaithfulnessRaw':1800,'_BatchCardProperties':2000,
             '_DifficultyResult':700,'_MaterialTypeResult':1600,'_CoverageResult':1800}.get(response_model.__name__,6000)
        payload={'model':JUDGE,'instructions':system,'input':user,'temperature':0,
                 'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
        saved=await api.request('judge-'+response_model.__name__,payload,cap)
        result=response_model.model_validate_json(saved['raw_output'])
        if details_log is not None:details_log.append({'schema':response_model.__name__,'input_sha256':saved['input_sha256'],'result':result.model_dump()})
        return result
    async def embeddings(texts):
        saved=await api.request('duplicates',{'model':'text-embedding-3-small','input':texts},embedding=True)
        return saved['vectors']
    ev.llm_call=llm_call;ev.get_embeddings=embeddings
    from review_schema import ProblemAudit
    task_prompt=(ROOT/'problem-audit.md').read_text(encoding='utf-8')
    for slug,topic,pages in TOPICS:
        if selected and selected!=slug:continue
        page_text={n:reader.pages[n-1].extract_text() or '' for n in pages}
        target=OUT/f'{slug}-card-metrics.json'
        if not target.exists():
            a=read(OUT/f'{slug}-flashcards.json');cards=[Flashcard(i,text_blocks(p['question']),text_blocks(p['answer']),title=p['title']) for i,p in enumerate(a['items'],1)]
            cardset=CardSet(topic,'Flashcards','Level 3',min(pages),max(pages),cards,SOURCE.name)
            details=[];metrics=await ev.evaluate_card_set(cardset,page_text,details_log=details)
            assert len(metrics.card_metrics)==15
            assert all(x.self_contained and x.faithfulness and x.atomic is not None and x.trivial is not None and x.difficulty is not None for x in metrics.card_metrics)
            metrics.count_match=True
            # Expose original SetMetrics properties, not reconstructed/rounded score approximations.
            summary={key:getattr(metrics,key) for key in ['pct_self_contained','avg_faithfulness','pct_front_leaks','pct_atomic','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio','difficulty_spearman','avg_back_length','card_type_distribution','count_match']}
            write(target,{'topic':topic,'pages':pages,'metrics':asdict(metrics),'summary':summary,'details':details})
        target=OUT/f'{slug}-problem-audit.json'
        if not target.exists():
            a=read(OUT/f'{slug}-problems.json')
            user=json.dumps({'source_notes':page_text,'problems':[{'id':i,**p} for i,p in enumerate(a['items'],1)]},ensure_ascii=False)
            result=await llm_call(task_prompt,user,ProblemAudit)
            assert [x.id for x in result.items]==list(range(1,11))
            write(target,{'topic':topic,'pages':pages,'items':result.model_dump()['items'],'judge_model':JUDGE,
                'prompt_sha256':sha(task_prompt.encode()),'repair_calls':0})

async def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',choices=['generate','evaluate'],required=True);parser.add_argument('--topic',choices=[x[0] for x in TOPICS]);parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    sys.path[:0]=[str(CHECKOUT),str(PROJECT)]
    # Read existing provider-only dependencies; do not install into MathPDF.
    sys.path.append(str(CHECKOUT/'.venv/Lib/site-packages'))
    before=prompt_hashes()
    if not args.execute:
        print(json.dumps({'stage':args.stage,'topics':TOPICS,'cards':60,'problems':40,'budget_usd':BUDGET,'generator':GENERATOR,'judge':JUDGE}));return
    from dotenv import dotenv_values
    cfg=dotenv_values(PROJECT.parent/'.env');assert cfg.get('JUDGE_MODEL')==JUDGE
    key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    OUT.mkdir(exist_ok=True);api=BudgetClient(key)
    try:
        await (generate(api,args.topic) if args.stage=='generate' else evaluate(api,args.topic))
    finally:
        await api.client.close()
        assert before==prompt_hashes(),'Production prompt bytes changed'

if __name__=='__main__':asyncio.run(main())
