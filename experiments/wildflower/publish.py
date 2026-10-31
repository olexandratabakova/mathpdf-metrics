"""Build public Wildflower evidence from completed, budget-ledgered outputs. No API calls."""
from collections import Counter
import csv
import json
from pathlib import Path
from run import ROOT,PROJECT,CHECKOUT,TOPICS,GENERATOR,JUDGE,BUDGET,read,write,sha,prompt_hashes

def build():
    out=ROOT/'output';ledger=read(out/'ledger.json')
    assert all(c['status']=='completed' and 'cost_usd' in c for c in ledger['calls'])
    cost=sum(c['cost_usd'] for c in ledger['calls']);assert cost<=BUDGET
    card_sets=[];problem_sets=[]
    for slug,topic,pages in TOPICS:
        cards=read(out/f'{slug}-flashcards.json');problems=read(out/f'{slug}-problems.json')
        metrics=read(out/f'{slug}-card-metrics.json');audit=read(out/f'{slug}-problem-audit.json')
        assert len(cards['items'])==15 and len(problems['items'])==10 and len(audit['items'])==10
        card_sets.append({'id':slug,'topic':topic,'pages':pages,'items':cards['items'],'metrics':metrics['metrics'],'summary':metrics['summary']})
        problem_sets.append({'id':slug,'topic':topic,'pages':pages,'items':problems['items'],'audit':audit['items']})
    scores={key:sum(s['summary'][key]*len(s['items']) for s in card_sets)/60 for key in
            ['pct_self_contained','avg_faithfulness','pct_front_leaks','pct_atomic','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio']}
    verdicts=[x for s in problem_sets for x in s['audit']]
    counts=dict(Counter(x['decision'] for x in verdicts))
    flags={key:sum(bool(x[key]) for x in verdicts) for key in ['self_contained','statement_correct','solution_correct','complete_solution','source_method_supported','formatting_issue']}
    frozen={p.name:sha(p.read_bytes()) for p in (ROOT/'generator-prompts').glob('*.md')}
    assert all(prompt_hashes()[name]==value for name,value in frozen.items())
    manifest={}
    for slug,_,pages in TOPICS:
        for mode in ['flashcards','problems']:
            row=read(out/f'{slug}-{mode}.json');manifest[f'{slug}-{mode}']={k:row[k] for k in
                ['prompt_hashes','source_sha256','selected_pdf_sha256','resolved_model','usage','cost_usd','site_guards_passed','count','difficulty']}
    raw={
      'id':'wildflower-2026-10-31','date':'2026-10-31','version':'wildflower','title':'Wildflower · ordinary generation baseline',
      'kind':'production_prompt_baseline','generator':GENERATOR,'judge':JUDGE,'embedding_model':'text-embedding-3-small',
      'source':{'name':'main (13).pdf','sha256':manifest['sets-flashcards']['source_sha256'],'total_pages':74,
                'selected_pages':sorted({n for _,_,pages in TOPICS for n in pages}),'full_pdf_uploaded':False},
      'mathpdf_commit':'a3071436f158b09eb783e08fe2a8f98e69f985ec','production_modified':False,
      'settings':{'difficulty':3,'comment':'','retrieval':False,'template_generation':False,'repair_calls':0,
                  'judge_temperature':0,'duplicate_threshold':.85,'budget_usd':BUDGET},
      'metrics':{'cards_requested':60,'cards_generated':60,'problems_requested':40,'problems_generated':40,
                 'cards':scores,'problem_decisions':counts,'problem_flags':flags,
                 'problem_novelty':dict(Counter(x['novelty'] for x in verdicts))},
      'card_sets':card_sets,'problem_sets':problem_sets,'generation_manifest':manifest,
      'evaluation_prompt_hashes':{p.name:sha(p.read_bytes()) for p in (PROJECT/'prompts').glob('*.txt')},
      'problem_audit_prompt_sha256':sha((ROOT/'problem-audit.md').read_bytes()),
      'calls':ledger['calls'],'cost_usd':cost,
      'cost_by_stage':{stage:sum(x['cost_usd'] for x in ledger['calls'] if (x['name'].startswith('generate-') if stage=='generation' else not x['name'].startswith('generate-'))) for stage in ['generation','evaluation']},
      'limits':[
        'Fresh samples from four topics at difficulty 3; not a paired A/B test against historical v1–v4.',
        'Generation uses unchanged checked-in site prompts, schemas, default model and expansion; app accounts, quotas, server queue and persisted user data are not exercised.',
        'The original flashcard evaluator functions and prompts are reused. A budgeted Responses API transport replaces retrying Chat Completions; prompt/schema semantics and temperature 0 are retained.',
        'The configured judge is gpt-4o-mini. Historical judge configurations were not fully retained; do not claim identical-judge longitudinal accuracy.',
        'Faithfulness measures source support, not mathematical truth. Quote matching is a separate fuzzy check and does not override the judge status.',
        'Duplicate rate is the share of cards involved in thresholded embedding pairs within each topic, averaged by card count; it is not a cross-topic semantic audit.',
        'Task verdicts and novelty labels are fallible model judgements, not deterministic proof checks. No LLM repair, RAG bank or program-owned numerical templates were used.',
        'The source PDF and full extracted notes are excluded from public output. Original generated answers and mistakes are preserved.'
      ]}
    local=ROOT/'local-checks.json'
    if local.exists():raw['local_checks']=read(local)
    rendering=ROOT/'rendering-checks.json'
    if rendering.exists():raw['rendering']=read(rendering)
    return raw

def main():
    a=build();write(ROOT/'result.json',a)
    (PROJECT/'wildflower-data.js').write_text('window.MATHPDF_WILDFLOWER = '+json.dumps(a,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    # CSV matches the original evaluator's per-card import fields. Keep full text in JSON.
    columns=['set_topic','set_level','card_number','front_preview','self_contained_passes','whats_missing','blind_answer_matches','faithfulness_ratio','faithfulness_unsupported','faithfulness_contradicts','front_leaks_answer','atomic','card_type','understanding_vs_rote','trivial','back_length_sentences','difficulty','judge_self_contained_note','judge_faithfulness_note']
    with (ROOT/'cards_wildflower.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for s in a['card_sets']:
            for c in s['metrics']['card_metrics']:
                sc=c['self_contained'];faith=c['faithfulness']
                writer.writerow(dict(zip(columns,[s['topic'],'Level 3',c['card_number'],c['front'][:120],int(sc['passes']),sc['whats_missing'],int(sc['blind_answer_matches']),faith['supported']/faith['total'] if faith['total'] else 1,faith['unsupported'],faith['contradicts'],int(c['front_leaks_answer']),int(c['atomic']),c['card_type_label'],c['understanding_vs_rote'],int(c['trivial']),c['back_length_sentences'],c['difficulty'],sc['whats_missing'],' | '.join(x['claim'] for x in faith['claims'] if x['status']!='supported')])) )
    print(json.dumps({'cards':60,'problems':40,'cost_usd':a['cost_usd'],'scores':a['metrics']},ensure_ascii=False))
if __name__=='__main__':main()
