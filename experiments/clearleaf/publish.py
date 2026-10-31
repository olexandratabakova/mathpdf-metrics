"""Publish the 20-card pilot and separate local findings. No API requests."""
from collections import Counter
import csv,json
from pathlib import Path
from run import ROOT,PROJECT,W

def manual_review(sets):
    frozen=W.read(ROOT/'local-review-inputs.json')
    assert all(W.sha(json.dumps(s['items'],sort_keys=True,ensure_ascii=False).encode())==frozen[s['id']] for s in sets),'Local notes apply only to the inspected pilot. Review new outputs before publishing.'
    notes={
      'sets-1':(['redundant_explanation'],'The explanation repeats the membership notation already given.'),
      'sets-2':(['redundant_explanation'],'The explanation restates the subset definition.'),
      'sets-4':(['formatting'],'Punctuation and the word “and” are encoded as inline math parts; inspect the rendered sentence.'),
      'sets-5':(['redundant_explanation'],'The explanation repeats the power-set definition.'),
      'induction-2':(['multiple_targets','source_role'],'Combines the definition of divisibility with its use in induction. The generalized method summary is mixed into From notes.'),
      'numbers-2':(['multiple_targets','incomplete_reasoning'],'Asks both existence and irrationality of sqrt(2). Irrationality is asserted as proved elsewhere, rather than explained; page 23 only points to a previous lecture.'),
      'numbers-3':(['extra_claim'],'The explanation calls the midpoint argument density in the reals; proving a rational between two rationals alone does not establish a rational in every real interval.'),
      'numbers-5':(['wrong_citation'],'The base-b uniqueness theorem is on original page 26; the generated card cites page 27. Its mathematics is supported elsewhere in the selected pages, but the exact citation is wrong.'),
      'functions-2':(['multiple_targets'],'Three distinct conditions: injectivity, surjectivity and bijectivity. Split the learning targets.'),
      'functions-4':(['multiple_targets','missing_context'],'Combines two independent composition proofs. The front should specify composable maps or compatible domain/codomain sets.'),
      'functions-5':(['multiple_targets','missing_context'],'A broad request for “key properties” has no defined target list; the back lists six separate image/preimage properties.')
    }
    rows=[]
    for s in sets:
        for i,p in enumerate(s['items'],1):
            key=f'{s["id"]}-{i}';flags,note=notes.get(key,([],''))
            rows.append({'id':key,'atomic':'multiple_targets' not in flags,'self_contained':'missing_context' not in flags,
              'critical_math_error_found':False,'flags':flags,'note':note,
              'item_sha256':W.sha(json.dumps(p,sort_keys=True,ensure_ascii=False).encode())})
    return {'reviewer':'Coding assistant local inspection against cited pages; not an independent expert or a general mathematical verifier.',
      'items':rows,'summary':{'self_contained':sum(r['self_contained'] for r in rows),'atomic':sum(r['atomic'] for r in rows),
        'critical_math_errors_found':0,'wrong_citations':1,'incomplete_reasoning':1,'total':20},
      'regression_scope':'The new sample contains a correctly worded power-of-n subset question, but omits the previous chessboard target. It does not demonstrate that the 2^n→2n failure is fixed.',
      'decision':'Not ready to promote: five multi-target cards, one wrong citation and an incomplete requested explanation. No critical mathematical error was found in this small inspection; this is not a correctness guarantee.'}

def build():
    ledger=W.read(W.OUT/'ledger.json');assert all(c['status']=='completed' for c in ledger['calls'])
    cost=sum(c['cost_usd'] for c in ledger['calls']);assert cost<=.15
    sets=[];manifest={}
    for slug,topic,pages in W.TOPICS:
        gen=W.read(W.OUT/f'{slug}-flashcards.json');ev=W.read(W.OUT/f'{slug}-card-metrics.json');revised=W.read(W.OUT/f'{slug}-revised-self-contained.json')
        assert len(gen['items'])==len(ev['metrics']['card_metrics'])==5
        sets.append({'id':slug,'topic':topic,'pages':pages,'items':gen['items'],'metrics':ev['metrics'],'summary':ev['summary'],'revised_self_contained':revised})
        manifest[slug]={k:gen[k] for k in ['prompt_hashes','source_sha256','selected_pdf_sha256','usage','cost_usd','resolved_model','site_guards_passed']}
    calibration=W.read(W.OUT/'calibration.json')
    calibration['overlaps_prompt_examples']=True
    scores={k:sum(s['summary'][k]*len(s['items']) for s in sets)/20 for k in ['pct_self_contained','avg_faithfulness','pct_atomic','pct_front_leaks','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio']}
    revised_pass=sum(s['revised_self_contained']['passed'] for s in sets)
    a={'id':'clearleaf-2026-10-31','date':'2026-10-31','version':'clearleaf','kind':'isolated_flashcard_prompt_pilot','generator':W.GENERATOR,'judge':W.JUDGE,
       'card_sets':sets,'calibration':calibration,'manual_review':manual_review(sets),
       'metrics':{'cards_generated':20,'cards_requested':20,'cards':scores,'revised_self_contained':{'passed':revised_pass,'total':20}},
       'generation_manifest':manifest,'calls':ledger['calls'],'cost_usd':cost,
       'cost_by_stage':{stage:sum(c['cost_usd'] for c in ledger['calls'] if (c['name'].startswith('generate-') if stage=='generation' else not c['name'].startswith('generate-'))) for stage in ['generation','evaluation']},
       'source':{'name':W.SOURCE.name,'sha256':manifest['sets']['source_sha256'],'full_pdf_uploaded':False},
       'settings':{'count_per_topic':5,'difficulty':3,'budget_usd':.15,'baseline_generation_calls':0,'repair_calls':0,'retrieval':False},
       'production_modified':False,'changed_generator_prompts':['flashcards.md'],
       'evaluation_prompt_hashes':{p.name:W.sha(p.read_text(encoding='utf-8').encode()) for p in (PROJECT/'prompts').glob('*.txt')},
       'revised_self_contained_prompt_sha256':W.sha((ROOT/'self_contained_blind.txt').read_text(encoding='utf-8').encode()),
       'limitations':['20 candidate cards versus the previous 60-card baseline: no paired A/B or causal improvement claim.',
         'Original card metrics are unchanged. Revised self-containment is a separately labelled diagnostic, never substituted into original scores.',
         'Calibration uses eight known hand-labelled fronts overlapping examples in the revised rubric. This checks instruction compliance, not held-out accuracy.',
         'Five cards per topic cannot be compared to fifteen-card topic coverage or duplicate rates as an equal-size experiment.',
         'Local inspection and technical rendering checks do not certify general mathematical correctness. The chessboard regression target was not generated.']}
    if (ROOT/'rendering-checks.json').exists():a['rendering']=W.read(ROOT/'rendering-checks.json')
    return a

def main():
    a=build();W.write(ROOT/'result.json',a)
    (PROJECT/'clearleaf-data.js').write_text('window.MATHPDF_CLEARLEAF = '+json.dumps(a,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    with (ROOT/'cards_clearleaf.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['set_topic','set_level','card_number','front_preview','self_contained_passes','faithfulness_ratio','atomic','front_leaks_answer','trivial','understanding_vs_rote','difficulty']
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
        for s in a['card_sets']:
            for c in s['metrics']['card_metrics']:
                faith=c['faithfulness'];wr.writerow(dict(zip(fields,[s['topic'],'Level 3',c['card_number'],c['front'],int(c['self_contained']['passes']),faith['supported']/faith['total'] if faith['total'] else 1,int(c['atomic']),int(c['front_leaks_answer']),int(c['trivial']),c['understanding_vs_rote'],c['difficulty']])))
    print(json.dumps({'cost_usd':a['cost_usd'],'metrics':a['metrics'],'local':a['manual_review']['summary'],'calibration':a['calibration']['matched']}))
if __name__=='__main__':main()
