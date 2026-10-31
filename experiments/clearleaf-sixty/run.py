"""Append forty cards without changing the original twenty or the core prompt.
Evaluate complete 15-card topic sets with the original rubric; reuse exact cached calls.
"""
import argparse,asyncio,base64,importlib.util,json,os,sys
from dataclasses import asdict
from pathlib import Path
from string import Template

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'wildflower/run.py')
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
W.ROOT=ROOT;W.OUT=ROOT/'output';W.BUDGET=.20
sys.path[:0]=[str(W.CHECKOUT),str(PROJECT),str(W.CHECKOUT/'.venv/Lib/site-packages')]
PILOT=ROOT.parent/'clearleaf'
OLD=W.read(PILOT/'result.json')

class ReuseClient(W.BudgetClient):
    async def request(self,name,payload,cap=None,embedding=False):
        digest=W.sha(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode())
        cached=PILOT/'output/calls'/f'{name}-{digest}.json'
        if not name.startswith('generate-') and cached.exists():
            saved=W.read(cached)
            if saved['status']=='completed':
                async with self.lock:
                    path=W.OUT/'reused.json';entries=W.read(path) if path.exists() else {}
                    entries[name+':'+digest]={'name':name,'input_sha256':digest,'origin':'clearleaf-20','new_cost_usd':0,'original_cost_usd':saved['cost_usd']}
                    W.write(path,entries)
                return saved
        return await super().request(name,payload,cap,embedding)

async def generate(api):
    from formula_lab.workspace import Document
    from formula_lab.study import GenerateRequest,InputDocument,load_prompts,selected_pdf,GeneratedContent,validate_study,question_fingerprint
    from formula_lab.providers import set_response_format
    from openai import pydantic_function_tool
    candidate=(PILOT/'flashcards.md').read_text(encoding='utf-8')
    assert W.sha(candidate.encode())==OLD['generation_manifest']['sets']['prompt_hashes']['flashcards.md']
    source_hash=W.sha(W.SOURCE.read_bytes());assert source_hash==OLD['source']['sha256']
    for slug,topic,pages in W.TOPICS:
        target=W.OUT/f'{slug}-flashcards.json'
        if target.exists():continue
        previous=next(s['items'] for s in OLD['card_sets'] if s['id']==slug)
        pdf=selected_pdf(W.SOURCE,pages)
        doc=Document(id='b'*32,filename=W.SOURCE.name,sha256=source_hash,media_type='application/pdf',page_count=74,size=W.SOURCE.stat().st_size)
        req=GenerateRequest(document_id=doc.id,pages=pages,mode='flashcards',count=10,difficulty=3)
        docs=[InputDocument(document=doc,data=pdf,filename=f'{slug}-selected.pdf',role='source',pages=pages)]
        system,task,hashes=load_prompts(req,docs)
        mapping=', '.join(f'{i+1} -> {n}' for i,n in enumerate(pages))
        original=Template((W.CHECKOUT/'formula_lab/prompts/flashcards.md').read_text(encoding='utf-8')).substitute(count=10,page_mapping=mapping)
        replacement=Template(candidate).substitute(count=10,page_mapping=mapping)
        assert task.startswith(original);task=replacement+task[len(original):];hashes['flashcards.md']=W.sha(candidate.encode())
        # Continuation is disclosed separately; the frozen candidate prompt is unchanged.
        continuation={'already_generated_cards':previous,'instruction':'Continue this topic with exactly ten additional distinct learning targets. Do not repeat any learning target or question already covered above. Keep the same selected-page scope and difficulty. Return only the ten new cards.'}
        fn=pydantic_function_tool(set_response_format(10,'flashcards'))['function']
        payload={'model':W.GENERATOR,'instructions':system,'input':[{'role':'user','content':[
            {'type':'input_text','text':docs[0].label},{'type':'input_file','filename':docs[0].filename,'file_data':'data:application/pdf;base64,'+base64.b64encode(pdf).decode()},
            {'type':'input_text','text':task},{'type':'input_text','text':json.dumps(continuation,ensure_ascii=False)}]}],
            'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
        saved=await api.request(f'generate-{slug}-append-ten',payload,7500)
        parsed=set_response_format(10,'flashcards',permissive=True).model_validate_json(saved['raw_output']).result
        assert parsed.status=='completed','Source insufficient; no forced padding or automatic retry'
        new=[x.expand(doc.id,i+5,'flashcards') for i,x in enumerate(parsed.items,1)]
        validate_study(GeneratedContent(items=new,notes=[]),'flashcards',doc.id,pages)
        # Keep all outputs for inspection even if a duplicate guard would reject a set.
        from formula_lab.study import StudyItem
        items=previous+[x.model_dump(mode='json') for x in new]
        fingerprints=[question_fingerprint(StudyItem.model_validate(x)) for x in items]
        duplicates=[i+1 for i,x in enumerate(fingerprints) if x in fingerprints[:i]]
        W.write(target,{**saved,'items':items,'new_items':items[5:],'original_item_count':5,'new_item_count':10,'topic':topic,'pages':pages,
          'prompt_hashes':hashes,'continuation_context_sha256':W.sha(json.dumps(continuation,sort_keys=True,ensure_ascii=False).encode()),
          'exact_duplicate_item_indices':duplicates,'source_sha256':source_hash,'selected_pdf_sha256':W.sha(pdf),'compact_new':parsed.model_dump(mode='json')})

async def evaluate(api):
    from openai import pydantic_function_tool
    from pypdf import PdfReader
    import flashcard_evaluator.evaluator as ev
    from flashcard_evaluator.models import CardSet,Flashcard
    async def call(system,user,response_model,model=None,use_cache=True,details_log=None):
        fn=pydantic_function_tool(response_model)['function']
        caps={'_BlindResult':600,'_CompareResult':100,'_FaithfulnessRaw':1800,'_BatchCardProperties':2000,'_DifficultyResult':700,'_MaterialTypeResult':1600,'_CoverageResult':1800}
        saved=await api.request('judge-'+response_model.__name__,{'model':W.JUDGE,'instructions':system,'input':user,'temperature':0,
          'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}},caps[response_model.__name__])
        result=response_model.model_validate_json(saved['raw_output'])
        if details_log is not None:details_log.append({'schema':response_model.__name__,'input_sha256':saved['input_sha256'],'result':result.model_dump()})
        return result
    async def embeddings(texts):return (await api.request('duplicates',{'model':'text-embedding-3-small','input':texts},embedding=True))['vectors']
    ev.llm_call=call;ev.get_embeddings=embeddings
    reader=PdfReader(W.SOURCE)
    for slug,topic,pages in W.TOPICS:
        target=W.OUT/f'{slug}-metrics.json'
        if target.exists():continue
        gen=W.read(W.OUT/f'{slug}-flashcards.json')
        cards=[Flashcard(i,W.text_blocks(p['question']),W.text_blocks(p['answer']),title=p['title']) for i,p in enumerate(gen['items'],1)]
        details=[]
        sm=await ev.evaluate_card_set(CardSet(topic,'Flashcards','Level 3',min(pages),max(pages),cards,W.SOURCE.name),{n:reader.pages[n-1].extract_text() or '' for n in pages},details_log=details)
        assert len(sm.card_metrics)==15 and all(c.self_contained and c.faithfulness and c.atomic is not None and c.difficulty is not None for c in sm.card_metrics)
        sm.count_match=True
        keys=['pct_self_contained','avg_faithfulness','pct_front_leaks','pct_atomic','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio','difficulty_spearman','avg_back_length','card_type_distribution','count_match']
        W.write(target,{'metrics':asdict(sm),'summary':{k:getattr(sm,k) for k in keys},'details':details})

async def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['generate','evaluate'],required=True);p.add_argument('--execute',action='store_true');args=p.parse_args()
    if not args.execute:print(json.dumps({'additional_cards':40,'combined_cards':60,'new_budget_usd':.20,'stage':args.stage}));return
    from dotenv import dotenv_values
    cfg=dotenv_values(PROJECT.parent/'.env');key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    before=W.prompt_hashes();api=ReuseClient(key)
    try:await (generate(api) if args.stage=='generate' else evaluate(api))
    finally:await api.client.close();assert before==W.prompt_hashes()

if __name__=='__main__':asyncio.run(main())
