"""One retrieved-context plan call; 50 families x2 program-built task attempts."""
import asyncio,hashlib,json,os,time
from pathlib import Path
from pydantic import BaseModel,ConfigDict,Field
from openai import AsyncOpenAI,pydantic_function_tool
from dotenv import dotenv_values
import retrieval as R
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
class Choice(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:int
    template_id:str
    reason:str
class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid')
    items:list[Choice]=Field(min_length=50,max_length=50)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
async def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'ledger.json').exists(),'Paid slot already reserved, no automatic repeats'
    frozen=R.prepare();frozen['controls']=R.controls(frozen['bank'])
    write(OUT/'retrieval-before-model.json',frozen)
    # Expected test labels are not passed to the planning model.
    requests=[{'id':x['request']['id'],'goal':x['request']['goal'],'domain':x['request']['domain'],
      'available':x['request']['available'],'source_support':x['request']['sources'],
      'candidate_ids':[m['id'] for m in x['retrieved']['matches']]} for x in frozen['retrieval']]
    candidates={m['id']:m['doc'] for x in frozen['retrieval'] for m in x['retrieved']['matches']}
    bank=[{'id':d['id'],'topic':d['topic'],'domain':d['domain'],'requires':d['requires'],'method':d['text'],
      'sources':d['sources'],'question':d['example']['question'],'answer':d['example']['answer']} for d in candidates.values()]
    task=json.dumps({'requests':requests,'candidate_bank':bank,'topic_selected_source_packets':frozen['source_packets']},ensure_ascii=False)
    prompt=(ROOT/'prompt.md').read_text(encoding='utf-8');fn=pydantic_function_tool(Plan)['function']
    payload={'model':'gpt-4.1-mini-2025-04-14','instructions':prompt,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    cfg=dotenv_values(ROOT.parents[2]/'.env');key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY');assert key
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=150) as client:
        counted=await client.responses.input_tokens.count(**payload);reserve=(counted.input_tokens*.4*1.1+5000*1.6)/1e6
        assert reserve<=.05,'Budget cap; nothing generated'
        write(OUT/'ledger.json',{'budget_usd':.05,'reserved_usd':reserve,'status':'reserved','paid_calls':1})
        print(json.dumps({'input_tokens':counted.input_tokens,'reserve_usd':reserve,'families':50,'task_attempts':100}),flush=True)
        start=time.monotonic();response=await client.responses.create(**payload,max_output_tokens=5000,temperature=0,store=False)
        usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens'];cost=((usage['input_tokens']-cached)*.4+cached*.1+usage['output_tokens']*1.6)/1e6
        data={'status':response.status,'model':response.model,'usage':usage,'cost_usd':cost,'duration_seconds':round(time.monotonic()-start,2),'raw_output':response.output_text,
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'input_sha256':hashlib.sha256(task.encode()).hexdigest(),'expected_labels_sent':False,'full_pdf_uploaded':False}
        write(OUT/'response.json',data);write(OUT/'ledger.json',{'budget_usd':.05,'reserved_usd':reserve,'paid_calls':1,'status':response.status,'cost_usd':cost})
        assert response.status=='completed'
        data['plan']=Plan.model_validate_json(response.output_text).model_dump();assert [x['id'] for x in data['plan']['items']]==list(range(1,51))
        write(OUT/'response.json',data);print(json.dumps({'cost_usd':cost,'choices':50}),flush=True)
if __name__=='__main__':asyncio.run(main())
