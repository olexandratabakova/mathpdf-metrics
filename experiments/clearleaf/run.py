"""20 Clearleaf cards only. Reuses Wildflower's isolated budget transport, not its data.
Original evaluator unchanged; revised self-containment is a separate diagnostic.
"""
import argparse,asyncio,base64,importlib.util,json,os,sys
from dataclasses import asdict
from pathlib import Path
from string import Template

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('wildflower_transport',ROOT.parent/'wildflower/run.py')
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
W.ROOT=ROOT;W.OUT=ROOT/'output';W.BUDGET=.15
sys.path[:0]=[str(W.CHECKOUT),str(PROJECT),str(W.CHECKOUT/'.venv/Lib/site-packages')]
FIXTURES=[
 ('empty-set','What is the empty set and how is it different from the set containing the empty set?',True),
 ('inverse','Under what conditions does the inverse relation of a function define an inverse function?',True),
 ('injective','What does injective mean for a function?',True),
 ('power-set','What is the power set of a set?',True),
 ('hidden-formula','What does this formula mean?',False),
 ('hidden-step','Why does the last step hold?',False),
 ('hidden-function','Is f injective?',False),
 ('hidden-sets','What are the properties of S and T mentioned above?',False)]

async def generate(api):
    from formula_lab.workspace import Document
    from formula_lab.study import GenerateRequest,InputDocument,load_prompts,selected_pdf,GeneratedContent,validate_study,question_fingerprint
    from formula_lab.providers import set_response_format
    from openai import pydantic_function_tool
    candidate=(ROOT/'flashcards.md').read_text(encoding='utf-8')
    source_hash=W.sha(W.SOURCE.read_bytes())
    for slug,topic,pages in W.TOPICS:
        target=W.OUT/f'{slug}-flashcards.json'
        if target.exists():continue
        pdf=selected_pdf(W.SOURCE,pages)
        doc=Document(id='b'*32,filename=W.SOURCE.name,sha256=source_hash,media_type='application/pdf',page_count=74,size=W.SOURCE.stat().st_size)
        req=GenerateRequest(document_id=doc.id,pages=pages,mode='flashcards',count=5,difficulty=3)
        docs=[InputDocument(document=doc,data=pdf,filename=f'{slug}-selected.pdf',role='source',pages=pages)]
        system,task,hashes=load_prompts(req,docs)
        mapping=', '.join(f'{i+1} -> {n}' for i,n in enumerate(pages))
        original=Template((W.CHECKOUT/'formula_lab/prompts/flashcards.md').read_text(encoding='utf-8')).substitute(count=5,page_mapping=mapping)
        replacement=Template(candidate).substitute(count=5,page_mapping=mapping)
        assert task.startswith(original)
        task=replacement+task[len(original):]
        hashes['flashcards.md']=W.sha(candidate.encode())
        frozen=ROOT/'generator-prompts';frozen.mkdir(exist_ok=True)
        for name in hashes:
            text=candidate if name=='flashcards.md' else (W.CHECKOUT/'formula_lab/prompts'/name).read_text(encoding='utf-8')
            dest=frozen/name
            if dest.exists():assert dest.read_text(encoding='utf-8')==text
            else:dest.write_text(text,encoding='utf-8')
        fn=pydantic_function_tool(set_response_format(5,'flashcards'))['function']
        payload={'model':W.GENERATOR,'instructions':system,'input':[{'role':'user','content':[
          {'type':'input_text','text':docs[0].label},{'type':'input_file','filename':docs[0].filename,'file_data':'data:application/pdf;base64,'+base64.b64encode(pdf).decode()},
          {'type':'input_text','text':task}]}],'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
        saved=await api.request(f'generate-{slug}-flashcards',payload,4250)
        parsed=set_response_format(5,'flashcards',permissive=True).model_validate_json(saved['raw_output']).result
        assert parsed.status=='completed','Insufficient source; no forced padding or retry'
        items=[x.expand(doc.id,i,'flashcards') for i,x in enumerate(parsed.items,1)]
        validate_study(GeneratedContent(items=items,notes=[]),'flashcards',doc.id,pages)
        assert len({question_fingerprint(x) for x in items})==5
        W.write(target,{**saved,'items':[x.model_dump(mode='json') for x in items],'compact':parsed.model_dump(mode='json'),
          'prompt_hashes':hashes,'pages':pages,'topic':topic,'difficulty':3,'count':5,'source_sha256':source_hash,'selected_pdf_sha256':W.sha(pdf),'site_guards_passed':True})

async def evaluate(api):
    from openai import pydantic_function_tool
    from pypdf import PdfReader
    import flashcard_evaluator.evaluator as ev
    from flashcard_evaluator.models import CardSet,Flashcard
    revised=(ROOT/'self_contained_blind.txt').read_text(encoding='utf-8')
    async def call(system,user,response_model,model=None,use_cache=True,details_log=None):
        fn=pydantic_function_tool(response_model)['function']
        cap={'_BlindResult':600,'_CompareResult':100,'_FaithfulnessRaw':1800,'_BatchCardProperties':1000,'_DifficultyResult':400,'_MaterialTypeResult':1600,'_CoverageResult':1800}[response_model.__name__]
        saved=await api.request('judge-'+response_model.__name__,{'model':W.JUDGE,'instructions':system,'input':user,'temperature':0,
          'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}},cap)
        result=response_model.model_validate_json(saved['raw_output'])
        if details_log is not None:details_log.append({'schema':response_model.__name__,'input_sha256':saved['input_sha256'],'result':result.model_dump()})
        return result
    async def embeddings(texts):return (await api.request('duplicates',{'model':'text-embedding-3-small','input':texts},embedding=True))['vectors']
    ev.llm_call=call;ev.get_embeddings=embeddings
    # Calibrate only the revised rubric, independently of the source/card answers.
    target=W.OUT/'calibration.json'
    if not target.exists():
        rows=[]
        for id,front,expected in FIXTURES:
            result=await call(revised,'CARD_FRONT:\n'+front,ev._BlindResult)
            passed=result.understandable and not result.whats_missing.strip()
            rows.append({'id':id,'front':front,'expected':expected,'result':result.model_dump(),'matches':passed==expected})
        W.write(target,{'items':rows,'matched':sum(x['matches'] for x in rows),'total':8,'scope':'Eight hand-labelled diagnostics, not independent broad validation.'})
    reader=PdfReader(W.SOURCE)
    for slug,topic,pages in W.TOPICS:
        a=W.read(W.OUT/f'{slug}-flashcards.json')
        target=W.OUT/f'{slug}-card-metrics.json'
        if not target.exists():
            cards=[Flashcard(i,W.text_blocks(p['question']),W.text_blocks(p['answer']),title=p['title']) for i,p in enumerate(a['items'],1)]
            details=[]
            sm=await ev.evaluate_card_set(CardSet(topic,'Flashcards','Level 3',min(pages),max(pages),cards,W.SOURCE.name),{n:reader.pages[n-1].extract_text() or '' for n in pages},details_log=details)
            assert len(sm.card_metrics)==5 and all(c.self_contained and c.faithfulness and c.atomic is not None and c.difficulty is not None for c in sm.card_metrics)
            sm.count_match=True
            keys=['pct_self_contained','avg_faithfulness','pct_front_leaks','pct_atomic','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio','difficulty_spearman','avg_back_length','card_type_distribution','count_match']
            W.write(target,{'metrics':asdict(sm),'summary':{k:getattr(sm,k) for k in keys},'details':details})
        target=W.OUT/f'{slug}-revised-self-contained.json'
        if not target.exists():
            rows=[]
            for i,p in enumerate(a['items'],1):
                result=await call(revised,'CARD_FRONT:\n'+W.text_blocks(p['question']),ev._BlindResult)
                rows.append({'id':i,'result':result.model_dump(),'passes':result.understandable and not result.whats_missing.strip()})
            W.write(target,{'items':rows,'passed':sum(r['passes'] for r in rows),'total':5})

async def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['generate','evaluate'],required=True);p.add_argument('--execute',action='store_true');args=p.parse_args()
    if not args.execute:print(json.dumps({'new_cards':20,'baseline_generation_calls':0,'budget_usd':W.BUDGET,'stage':args.stage}));return
    from dotenv import dotenv_values
    cfg=dotenv_values(PROJECT.parent/'.env');key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    before=W.prompt_hashes();W.OUT.mkdir(exist_ok=True);api=W.BudgetClient(key)
    try:await (generate(api) if args.stage=='generate' else evaluate(api))
    finally:await api.client.close();assert before==W.prompt_hashes(),'Production prompt bytes changed'

if __name__=='__main__':asyncio.run(main())
