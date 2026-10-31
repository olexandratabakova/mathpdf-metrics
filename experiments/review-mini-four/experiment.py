"""Three-call, budget-gated experiment; never starts or modifies MathPDF.

Generate with mini -> blind statement check with mini -> solution audit with
mini. No automatic retries or paid corrections. Raw artifacts stay in output/.
"""
import argparse
import asyncio
import base64
import hashlib
import io
import json
import os
from pathlib import Path
from string import Template
import sys
import time
from typing import Literal

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
PROJECT=ROOT.parents[1]
PAGES=[63,64,65,66]
BUDGET=.035
RATES={'gpt-4.1-mini-2025-04-14':(.4,.1,1.6),'gpt-4.1-2025-04-14':(2,.5,8)}


def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def schema_for(stage):
    from pydantic import BaseModel, ConfigDict, Field
    class Strict(BaseModel):
        model_config=ConfigDict(extra='forbid')
    if stage=='blind':
        class Item(Strict):
            problem_id:int=Field(ge=1,le=4)
            statement_status:Literal['well_posed','false_claim','ambiguous','not_supported']
            independent_result:str
            evidence:list[str]
            source_pages:list[int]
    else:
        class Item(Strict):
            problem_id:int=Field(ge=1,le=4)
            decision:Literal['accept','revise','reject']
            statement_correct:bool
            solution_correct:bool
            source_supported:bool
            novelty:Literal['substantive','cosmetic','copied','uncertain']
            formatting_issue:bool
            explanation:str
            issues:list[str]
            suggested_fix:str
    class Review(Strict):
        items:list[Item]=Field(min_length=4,max_length=4)
    return Review


def payload_for(stage,source,checkout):
    from pypdf import PdfReader,PdfWriter
    from openai import pydantic_function_tool
    from formula_lab.providers import set_response_format
    pdf=PdfReader(source);writer=PdfWriter()
    for number in PAGES:writer.add_page(pdf.pages[number-1])
    buffer=io.BytesIO();writer.write(buffer);selected=buffer.getvalue()
    mapping=', '.join(f'{i+1} -> {number}' for i,number in enumerate(PAGES))
    metadata={'document_id':'f'*32,'filename':'selected-pages.pdf','original_filename':source.name,'role':'source','original_pages':PAGES}
    prompt_hashes={}
    if stage=='generate':
        resources={p.name:p.read_text(encoding='utf-8') for p in (ROOT/'generator-prompts').glob('*.md')}
        instructions='\n\n'.join(resources[n] for n in ['study-system.md','formula-guide.md','math-patterns.md'])
        task=Template(resources['problems.md']).substitute(count=4,page_mapping=mapping)
        task+='\n\n'+Template(resources['difficulty.md']).substitute(difficulty=3)
        task+='\n\n'+Template(resources['context.md']).substitute(attachments=json.dumps([metadata],ensure_ascii=False))
        schema=set_response_format(4,'problems')
        model='gpt-4.1-mini-2025-04-14';cap=5000
        prompt_hashes={n:sha(t.encode()) for n,t in resources.items()}
    else:
        instructions=(ROOT/('blind-review.md' if stage=='blind' else 'solution-audit.md')).read_text(encoding='utf-8')
        generation=json.loads((OUT/'generate.json').read_text(encoding='utf-8'))
        items=generation['parsed']['result']['items']
        if stage=='blind':
            task=json.dumps({'page_mapping':mapping,'problems':[{'problem_id':i,'title':x['title'],'question':x['question']} for i,x in enumerate(items,1)]},ensure_ascii=False)
        else:
            task=json.dumps({'page_mapping':mapping,'problems':[{'problem_id':i,**x} for i,x in enumerate(items,1)],
                'independent_statement_review':json.loads((OUT/'blind.json').read_text(encoding='utf-8'))['parsed']},ensure_ascii=False)
        schema=schema_for(stage)
        model='gpt-4.1-mini-2025-04-14';cap=2600 if stage=='blind' else 3600
        prompt_hashes={stage:sha(instructions.encode())}
    function=pydantic_function_tool(schema)['function']
    payload={'model':model,'instructions':instructions,'input':[{'role':'user','content':[
        {'type':'input_text','text':json.dumps({'source':metadata,'page_mapping':mapping},ensure_ascii=False)},
        {'type':'input_file','filename':'selected-pages.pdf','file_data':'data:application/pdf;base64,'+base64.b64encode(selected).decode()},
        {'type':'input_text','text':task}]}],
        'text':{'format':{'type':'json_schema','name':function['name'],'strict':True,'schema':function['parameters']}}}
    manifest={'stage':stage,'model':model,'source_name':source.name,'source_sha256':sha(source.read_bytes()),'selected_pdf_sha256':sha(selected),
        'pages':PAGES,'count':4,'difficulty':3,'max_output_tokens':cap,'prompt_hashes':prompt_hashes,
        'instructions':instructions,'task':task,'blind_has_proposed_answers':False if stage=='blind' else None}
    return payload,manifest,schema,cap


async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['generate','blind','audit'],required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--mathpdf-source',type=Path,required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args();checkout=args.mathpdf_source.resolve()
    sys.path.insert(0,str(checkout))
    from dotenv import dotenv_values
    from openai import AsyncOpenAI
    production_hashes={p.name:sha(p.read_bytes()) for p in (checkout/'formula_lab/prompts').glob('*.md')}
    payload,manifest,schema,cap=payload_for(args.stage,args.source.resolve(),checkout)
    print(json.dumps({k:manifest[k] for k in ['stage','model','pages','count','max_output_tokens']}),flush=True)
    if not args.execute:
        print('DRY RUN: nothing sent.');return
    OUT.mkdir(exist_ok=True)
    ledger_path=OUT/'ledger.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'budget_usd':BUDGET,'calls':[],'token_count_calls':0}
    if (OUT/(args.stage+'.json')).exists() or any(x['stage']==args.stage for x in ledger['calls']):
        raise SystemExit('This stage is already reserved/completed; no automatic repeats.')
    spent=sum(x.get('cost_usd',x['reserved_usd']) for x in ledger['calls'])
    if len(ledger['calls'])>=3:raise SystemExit('Maximum three calls reached.')
    cfg=dotenv_values(PROJECT.parent/'.env')
    key=os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or cfg.get('OPENAI_API_KEY') or cfg.get('OPENAI_KEY')
    if not key:raise SystemExit('No API key; nothing sent.')
    rate_in,rate_cached,rate_out=RATES[manifest['model']]
    async with AsyncOpenAI(api_key=key,max_retries=0,timeout=150) as client:
        ledger['token_count_calls']+=1;write(ledger_path,ledger)
        counted=await client.responses.input_tokens.count(**payload)
        reserve=(counted.input_tokens*rate_in*1.10+cap*rate_out)/1_000_000
        print(json.dumps({'counted_input_tokens':counted.input_tokens,'reserve_usd':round(reserve,6),'spent_usd':round(spent,6)}),flush=True)
        if reserve+spent>BUDGET:raise SystemExit('Would exceed budget; generation/review NOT started.')
        entry={'stage':args.stage,'model':manifest['model'],'reserved_usd':reserve,'status':'reserved'}
        ledger['calls'].append(entry);write(ledger_path,ledger)
        manifest.update({'counted_input_tokens':counted.input_tokens,'reserved_usd':reserve,'production_prompt_hashes':production_hashes})
        write(OUT/(args.stage+'.json'),{'manifest':manifest,'status':'reserved'})
        start=time.monotonic()
        try:
            response=await client.responses.create(**payload,max_output_tokens=cap,store=False)
        except Exception as error:
            entry.update(status='unknown_or_failed_no_retry',error_type=type(error).__name__);write(ledger_path,ledger)
            print('Call failed; reservation kept, no retry: '+type(error).__name__);return
        usage=response.usage.model_dump() if response.usage else None
        result={'manifest':manifest,'resolved_model':response.model,'status':response.status,'raw_output':response.output_text,
            'usage':usage,'duration_seconds':round(time.monotonic()-start,2)}
        write(OUT/(args.stage+'.json'),result)
        if usage:
            cached=(usage.get('input_tokens_details') or {}).get('cached_tokens',0)
            entry.update(cost_usd=((usage['input_tokens']-cached)*rate_in+cached*rate_cached+usage['output_tokens']*rate_out)/1_000_000,
                input_tokens=usage['input_tokens'],cached_tokens=cached,output_tokens=usage['output_tokens'])
        entry['status']=response.status;write(ledger_path,ledger)
        if response.status=='completed':
            parsed=schema.model_validate_json(response.output_text)
            result['parsed']=parsed.model_dump(mode='json')
            if args.stage=='generate':
                if parsed.result.status!='completed':raise SystemExit('Source insufficient; no automatic regeneration.')
                result['expanded']=[x.expand('f'*32,i,'problems').model_dump(mode='json') for i,x in enumerate(parsed.result.items,1)]
            else:
                assert [x.problem_id for x in parsed.items]==[1,2,3,4]
            write(OUT/(args.stage+'.json'),result)
        assert production_hashes=={p.name:sha(p.read_bytes()) for p in (checkout/'formula_lab/prompts').glob('*.md')}
        print(json.dumps({'stage':args.stage,'status':response.status,'cost_usd':entry.get('cost_usd'),'seconds':result['duration_seconds']}),flush=True)


if __name__=='__main__':asyncio.run(main())
