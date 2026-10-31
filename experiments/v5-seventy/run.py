"""One mini planning call, <=$0.01; all seventy math tasks built and checked locally."""
import asyncio, hashlib,json,os,time,sys
from pathlib import Path
from pydantic import BaseModel,ConfigDict,Field
from openai import AsyncOpenAI,pydantic_function_tool
from dotenv import dotenv_values
from engine import TOPICS,META,generate,verify_artifact,SEED
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid')
    topic_order:list[str]=Field(min_length=7,max_length=7)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def finalize(result):
    plan=Plan.model_validate_json(result['raw_output'])
    assert len(set(plan.topic_order))==7 and set(plan.topic_order)==set(TOPICS)
    items=generate(plan.topic_order)
    assert len(items)==70
    for x in items:verify_artifact(x)
    result.update(plan=plan.model_dump(),items=items)
    write(OUT/'response.json',result)
async def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'ledger.json').exists(),'Already reserved; no repeated API request'
    prompt=(ROOT/'prompt.md').read_text(encoding='utf-8')
    catalog=[{'topic_id':t,'name':name,'count':10,'template_count':10 if t=='functions' else 5} for t,name in TOPICS.items()]
    task=json.dumps(catalog,ensure_ascii=False);fn=pydantic_function_tool(Plan)['function']
    payload={'model':'gpt-4.1-mini-2025-04-14','instructions':prompt,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    cfg=dotenv_values(ROOT.parents[2]/'.env')
    key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=120) as client:
        count=await client.responses.input_tokens.count(**payload)
        reserve=(count.input_tokens*.4*1.1+400*1.6)/1e6;assert reserve<.01
        write(OUT/'ledger.json',{'budget_usd':.01,'reserved_usd':reserve,'status':'reserved','paid_calls':1})
        print(json.dumps({'reserve_usd':reserve}),flush=True);start=time.monotonic()
        response=await client.responses.create(**payload,max_output_tokens=400,store=False,temperature=0)
        usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens']
        cost=((usage['input_tokens']-cached)*.4+cached*.1+usage['output_tokens']*1.6)/1e6
        result={'status':response.status,'model':response.model,'usage':usage,'cost_usd':cost,'raw_output':response.output_text,
         'seed':SEED,'duration_seconds':round(time.monotonic()-start,2),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'input_sha256':hashlib.sha256(task.encode()).hexdigest()}
        write(OUT/'response.json',result);write(OUT/'ledger.json',{'budget_usd':.01,'reserved_usd':reserve,'cost_usd':cost,'status':response.status,'paid_calls':1})
        assert response.status=='completed'
        finalize(result);print(json.dumps({'tasks':70,'cost_usd':cost,'reviewer_calls':0}),flush=True)
if __name__=='__main__':
    if '--finalize-only' in sys.argv:finalize(json.loads((OUT/'response.json').read_text(encoding='utf-8')))
    else:asyncio.run(main())
