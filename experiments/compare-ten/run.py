"""One identical ten-case batch per model, two paid calls maximum, $0.05 budget."""
import asyncio, hashlib, json, os, sys, time
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from openai import AsyncOpenAI, pydantic_function_tool
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
MODELS={'mini':('gpt-4.1-mini-2025-04-14',(.4,.1,1.6)), 'full':('gpt-4.1-2025-04-14',(2,.5,8))}
class Item(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:int
    accept:bool
    explanation:str
class Review(BaseModel):
    model_config=ConfigDict(extra='forbid')
    items:list[Item]=Field(min_length=10,max_length=10)
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
async def main():
    arm=sys.argv[1]; model,rates=MODELS[arm]
    cases=json.loads((ROOT/'cases.json').read_text(encoding='utf-8'))
    # Ground truth and labels never enter a model request.
    task=json.dumps([{k:c[k] for k in ['id','question','solution']} for c in cases],ensure_ascii=False)
    instructions=(ROOT/'reviewer.md').read_text(encoding='utf-8')
    fn=pydantic_function_tool(Review)['function']
    payload={'model':model,'instructions':instructions,'input':task,'text':{'format':{'type':'json_schema','name':fn['name'],'strict':True,'schema':fn['parameters']}}}
    OUT.mkdir(exist_ok=True); lp=OUT/'ledger.json'
    ledger=json.loads(lp.read_text()) if lp.exists() else {'budget_usd':.05,'calls':[]}
    assert len(ledger['calls'])<2 and not any(x['arm']==arm for x in ledger['calls']), 'Already reserved; no repeats'
    cfg=dotenv_values(ROOT.parents[2]/'.env')
    key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY')
    assert key,'No API key'
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=150) as client:
        count=await client.responses.input_tokens.count(**payload)
        reserve=(count.input_tokens*rates[0]*1.1+3000*rates[2])/1e6
        spent=sum(x.get('cost_usd',x['reserved_usd']) for x in ledger['calls'])
        assert spent+reserve<=.05,'Budget exceeded; not sent'
        entry={'arm':arm,'model':model,'reserved_usd':reserve,'status':'reserved'}
        ledger['calls'].append(entry);write(lp,ledger)
        print(json.dumps({'model':model,'reserve_usd':reserve}),flush=True)
        start=time.monotonic()
        response=await client.responses.create(**payload,max_output_tokens=3000,store=False,temperature=0)
        usage=response.usage.model_dump();cached=usage['input_tokens_details']['cached_tokens']
        entry.update(status=response.status,cost_usd=((usage['input_tokens']-cached)*rates[0]+cached*rates[1]+usage['output_tokens']*rates[2])/1e6)
        write(lp,ledger)
        result={'status':response.status,'model':response.model,'usage':usage,'cost_usd':entry['cost_usd'],'duration_seconds':round(time.monotonic()-start,2),'raw_output':response.output_text,'input_sha256':sha(task),'prompt_sha256':sha(instructions),'cases_sha256':sha((ROOT/'cases.json').read_text(encoding='utf-8'))}
        write(OUT/f'{arm}.json',result)
        assert response.status=='completed'
        result['parsed']=Review.model_validate_json(response.output_text).model_dump()
        assert [i['id'] for i in result['parsed']['items']]==list(range(1,11))
        write(OUT/f'{arm}.json',result)
        print(json.dumps({'model':model,'cost_usd':entry['cost_usd'],'status':response.status}),flush=True)
if __name__=='__main__':asyncio.run(main())
