"""Freeze retrieval, one <=$0.02 planning call, then checked numerical generation."""
import asyncio,hashlib,json,os,time
from pathlib import Path
from pydantic import BaseModel,ConfigDict,Field
from openai import AsyncOpenAI,pydantic_function_tool
from dotenv import dotenv_values
import pipeline as P
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
class Choice(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:int
    template_id:str
    reason:str
class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid')
    items:list[Choice]=Field(min_length=15,max_length=15)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
async def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'ledger.json').exists(),'Already reserved; no repeats'
    prepared=P.prepare()
    frozen={'requests':prepared,'bank_sha256':P.hashjson(P.bank()),'requests_sha256':P.hashjson(json.loads((ROOT/'requests.json').read_text(encoding='utf-8'))),'controls':P.controls()}
    write(OUT/'retrieval-before-model.json',frozen)
    # Evaluation labels are deliberately excluded from the model input.
    contexts=[{'id':x['request']['id'],'goal':x['request']['goal'],'domain':x['request']['domain'],
       'available_prerequisites':P.CONCEPTS[x['request']['topic']],'theory_only':x['theory'],
       'retrieved':[{'id':m['id'],'score':m['score'],'requires':m['doc']['requires'],'domain':m['doc']['domain'],
         'example':{'title':m['doc']['example']['title'],'question':m['doc']['example']['question'],'answer':m['doc']['example']['answer']}} for m in x['retrieval']['matches']]} for x in prepared]
    prompt=(ROOT/'prompt.md').read_text(encoding='utf-8');task=json.dumps(contexts,ensure_ascii=False)
    fn=pydantic_function_tool(Plan)['function']
    payload={'model':'gpt-4.1-mini-2025-04-14','instructions':prompt,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    cfg=dotenv_values(ROOT.parents[2]/'.env');key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=120) as client:
        count=await client.responses.input_tokens.count(**payload);reserve=(count.input_tokens*.4*1.1+2200*1.6)/1e6;assert reserve<=.02
        write(OUT/'ledger.json',{'budget_usd':.02,'reserved_usd':reserve,'status':'reserved','paid_calls':1})
        print(json.dumps({'input_tokens':count.input_tokens,'reserve_usd':reserve}),flush=True);start=time.monotonic()
        response=await client.responses.create(**payload,max_output_tokens=2200,store=False,temperature=0)
        u=response.usage.model_dump();cached=u['input_tokens_details']['cached_tokens'];cost=((u['input_tokens']-cached)*.4+cached*.1+u['output_tokens']*1.6)/1e6
        result={'status':response.status,'raw_output':response.output_text,'model':response.model,'usage':u,'cost_usd':cost,'duration_seconds':round(time.monotonic()-start,2),
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'model_input_sha256':hashlib.sha256(task.encode()).hexdigest(),'expected_labels_sent':False}
        write(OUT/'response.json',result);write(OUT/'ledger.json',{'budget_usd':.02,'reserved_usd':reserve,'status':response.status,'paid_calls':1,'cost_usd':cost})
        assert response.status=='completed'
        result['plan']=Plan.model_validate_json(response.output_text).model_dump();assert [x['id'] for x in result['plan']['items']]==list(range(1,16))
        write(OUT/'response.json',result);print(json.dumps({'cost_usd':cost,'choices':15}),flush=True)
if __name__=='__main__':asyncio.run(main())
