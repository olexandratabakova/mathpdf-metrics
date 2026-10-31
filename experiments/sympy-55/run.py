"""Two pilots then two main generation calls, shared <=$0.12; no LLM reviewer."""
import asyncio,hashlib,json,os,sys,time
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,create_model
from openai import AsyncOpenAI,pydantic_function_tool
from dotenv import dotenv_values
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
PAGES=[5,6,7,14,15,16,17,28,29,30,31,33,34,39,41,42,43,60,61,62,63,64,65,66]
class Step(BaseModel):
    model_config=ConfigDict(extra='forbid')
    left:str
    right:str
class Task(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:int
    topic:str
    source_page:int
    title:str
    question:str
    solution:str
    condition_change:str
    kind:Literal['expression','solve','finite_set','matrix','summation','induction','congruence','counting','function','inequality','proof']
    params_json:str
    answer:str
    steps:list[Step]
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
async def main():
    group=sys.argv[1];assert group in ['near','transfer','near2','transfer2'];count=40 if group.startswith('near') else 15
    OUT.mkdir(exist_ok=True);lp=OUT/'ledger.json'
    ledger=json.loads(lp.read_text()) if lp.exists() else {'budget_usd':.12,'calls':[]}
    assert len(ledger['calls'])<4 and not any(x['group']==group for x in ledger['calls']),'Already reserved; no repeated slot'
    pdfpath=Path('C:/Users/kotya/Downloads/main (12).pdf');pdf=PdfReader(pdfpath)
    excerpts='\n\n'.join(f'ORIGINAL PAGE {n}\n'+(pdf.pages[n-1].extract_text() or '') for n in PAGES)
    prompt=(ROOT/'prompt.md').read_text(encoding='utf-8')
    if group.endswith('2'):prompt+='\n\n'+(ROOT/('near-contract.md' if group=='near2' else 'transfer-contract.md')).read_text(encoding='utf-8')
    task=f'Generate group={group}, exactly {count} tasks, ids 1 through {count}, in one response. '+('condition_change must be empty for near tasks.' if group=='near' else 'Every task must have nonempty condition_change showing a real changed condition.')+'\n\nUSER NOTES EXCERPTS:\n'+excerpts
    schema=create_model('Batch',__config__=ConfigDict(extra='forbid'),items=(list[Task],Field(min_length=count,max_length=count)))
    fn=pydantic_function_tool(schema)['function']
    payload={'model':'gpt-4.1-mini-2025-04-14','instructions':prompt,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    cfg=dotenv_values(ROOT.parents[2]/'.env');key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    cap=24000 if count==40 else 12000
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=240) as client:
        counted=await client.responses.input_tokens.count(**payload)
        reserve=(counted.input_tokens*.4*1.1+cap*1.6)/1e6
        spent=sum(c.get('cost_usd',c['reserved_usd']) for c in ledger['calls']);assert spent+reserve<=.12,'Budget cap exceeded'
        entry={'group':group,'reserved_usd':reserve,'status':'reserved'};ledger['calls'].append(entry);write(lp,ledger)
        print(json.dumps({'group':group,'count':count,'reserve_usd':reserve,'counted_input_tokens':counted.input_tokens}),flush=True)
        start=time.monotonic();response=await client.responses.create(**payload,max_output_tokens=cap,store=False,temperature=0)
        usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens']
        cost=((usage['input_tokens']-cached)*.4+cached*.1+usage['output_tokens']*1.6)/1e6
        entry.update(status=response.status,cost_usd=cost);write(lp,ledger)
        result={'group':group,'status':response.status,'model':response.model,'usage':usage,'cost_usd':cost,'raw_output':response.output_text,'duration_seconds':round(time.monotonic()-start,2),
          'source_name':pdfpath.name,'source_sha256':hashlib.sha256(pdfpath.read_bytes()).hexdigest(),'source_pages':PAGES,
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'excerpts_sha256':hashlib.sha256(excerpts.encode()).hexdigest()}
        write(OUT/f'{group}.json',result);assert response.status=='completed'
        parsed=schema.model_validate_json(response.output_text).model_dump();assert [x['id'] for x in parsed['items']]==list(range(1,count+1))
        result['citation_warnings']=[{'id':x['id'],'source_page':x['source_page']} for x in parsed['items'] if x['source_page'] not in PAGES]
        result['parsed']=parsed;write(OUT/f'{group}.json',result)
        print(json.dumps({'group':group,'tasks':count,'cost_usd':cost,'status':response.status}),flush=True)
if __name__=='__main__':asyncio.run(main())
