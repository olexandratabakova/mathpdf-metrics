"""One mini planning call, <= $0.01. Program supplies all mathematics. No reviewer LLM."""
import asyncio, hashlib, json, os, re, time, sys
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from openai import AsyncOpenAI,pydantic_function_tool
from dotenv import dotenv_values
from engine import CATALOG,params,build,verify_artifact,SEED
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
MODEL='gpt-4.1-mini-2025-04-14'
class Choice(BaseModel):
    model_config=ConfigDict(extra='forbid')
    template_id:str
    title:str
class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid')
    items:list[Choice]=Field(min_length=10,max_length=10)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def finalize(result):
    plan=Plan.model_validate_json(result['raw_output'])
    assert len({c.template_id for c in plan.items})==10 and {c.template_id for c in plan.items}==set(CATALOG)
    assert all(re.fullmatch(r"[A-Za-z][A-Za-z '\-]{2,119}",c.title) for c in plan.items),'Invalid title; no silent fallback'
    pp=params();items=[{'id':i,**build(c.template_id,pp[c.template_id],c.title)} for i,c in enumerate(plan.items,1)]
    for item in items:verify_artifact({k:v for k,v in item.items() if k!='id'})
    result['plan']=plan.model_dump();result['items']=items
    write(OUT/'response.json',result)
    return result
async def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'ledger.json').exists(),'Already reserved; no retries'
    prompt=(ROOT/'prompt.md').read_text(encoding='utf-8')
    task=json.dumps(list(CATALOG.values()),ensure_ascii=False)
    fn=pydantic_function_tool(Plan)['function']
    payload={'model':MODEL,'instructions':prompt,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    cfg=dotenv_values(ROOT.parents[2]/'.env')
    key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY')
    assert key,'No API key'
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=120) as client:
        counted=await client.responses.input_tokens.count(**payload)
        reserve=(counted.input_tokens*.4*1.1+1200*1.6)/1e6
        assert reserve<=.01
        write(OUT/'ledger.json',{'budget_usd':.01,'model':MODEL,'reserved_usd':reserve,'status':'reserved'})
        print(json.dumps({'model':MODEL,'reserved_usd':reserve}),flush=True)
        start=time.monotonic()
        response=await client.responses.create(**payload,max_output_tokens=1200,temperature=0,store=False)
        usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens']
        cost=((usage['input_tokens']-cached)*.4+cached*.1+usage['output_tokens']*1.6)/1e6
        result={'status':response.status,'model':response.model,'usage':usage,'cost_usd':cost,'duration_seconds':round(time.monotonic()-start,2),'raw_output':response.output_text,
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'catalog_sha256':hashlib.sha256((ROOT/'catalog.json').read_bytes()).hexdigest(),'seed':SEED}
        write(OUT/'response.json',result);write(OUT/'ledger.json',{'budget_usd':.01,'model':MODEL,'reserved_usd':reserve,'status':response.status,'cost_usd':cost})
        assert response.status=='completed'
        finalize(result)
        print(json.dumps({'status':response.status,'tasks':10,'cost_usd':cost,'reviewer_calls':0}),flush=True)
if __name__=='__main__':
    if '--finalize-only' in sys.argv:
        result=json.loads((OUT/'response.json').read_text(encoding='utf-8'))
        assert result['status']=='completed'
        # Initial local 80-character title limit rejected a benign long title.
        # Reprocess the SAME paid response offline with a 120-character bound.
        result['offline_validation_note']='Initial 80-character title guard rejected one benign title. Bound raised to 120; original titles and raw response preserved. No repeated API call.'
        finalize(result);print('Finalized existing response offline; zero API calls.')
    else:asyncio.run(main())
