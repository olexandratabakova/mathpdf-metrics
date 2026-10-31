"""Publish the expanded set and its equal-count, original-rubric comparison."""
import csv,json
from run import ROOT,PROJECT,PILOT,OLD,W

def build():
    baseline=W.read(ROOT.parent/'wildflower/result.json')
    ledger=W.read(W.OUT/'ledger.json');assert all(c['status']=='completed' for c in ledger['calls'])
    cost=sum(c['cost_usd'] for c in ledger['calls']);assert cost<=.20
    sets=[];manifest={}
    for slug,topic,pages in W.TOPICS:
        g=W.read(W.OUT/f'{slug}-flashcards.json');e=W.read(W.OUT/f'{slug}-metrics.json')
        old=next(s for s in OLD['card_sets'] if s['id']==slug)
        base=next(s for s in baseline['card_sets'] if s['id']==slug)
        assert g['items'][:5]==old['items'] and len(g['items'])==15
        assert len(e['metrics']['card_metrics'])==15 and pages==base['pages']==old['pages']
        assert g['prompt_hashes']==OLD['generation_manifest'][slug]['prompt_hashes']
        sets.append({'id':slug,'topic':topic,'pages':pages,'items':g['items'],'metrics':e['metrics'],'summary':e['summary'],
          'origins':['clearleaf-20']*5+['clearleaf-extension']*10,'exact_duplicate_item_indices':g['exact_duplicate_item_indices']})
        manifest[slug]={k:g[k] for k in ['prompt_hashes','source_sha256','selected_pdf_sha256','resolved_model','usage','cost_usd','continuation_context_sha256']}
    keys=['pct_self_contained','avg_faithfulness','pct_atomic','pct_front_leaks','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio']
    scores={k:sum(s['summary'][k]*15 for s in sets)/60 for k in keys}
    old_scores=baseline['metrics']['cards']
    assert OLD['source']['sha256']==baseline['source']['sha256']==manifest['sets']['source_sha256']
    # The original rubric and reference pages remain frozen.
    assert {p.name:W.sha(p.read_bytes()) for p in (PROJECT/'prompts').glob('*.txt')}==baseline['evaluation_prompt_hashes']
    comparison={'baseline_id':'wildflower','baseline_count':60,'candidate_count':60,'baseline_scores':old_scores,'candidate_scores':scores,
       'delta_percentage_points':{k:(scores[k]-old_scores[k])*100 for k in keys},
       'per_topic':[{'id':s['id'],'topic':s['topic'],'count_each':15,'baseline':next(b['summary'] for b in baseline['card_sets'] if b['id']==s['id']),'candidate':s['summary']} for s in sets],
       'matched':['source PDF hash','selected pages per topic','15 cards per topic','difficulty 3','generator model alias','judge model, temperature and original rubric','embedding model and threshold'],
       'confounds':['Wildflower generated 15 per topic in one call; Clearleaf retains 5 and appends 10 with the prior cards in context.',
          'Only one run per condition; not randomized, independently repeated or paired by preassigned learning target.',
          'Model judge metrics are fallible. Revised 20-card self-containment diagnostics are not used in this comparison.']}
    reused=list(W.read(W.OUT/'reused.json').values()) if (W.OUT/'reused.json').exists() else []
    a={'id':'clearleaf-sixty-2026-10-31','date':'2026-10-31','version':'clearleaf-60','kind':'continued_flashcard_prompt_evaluation',
       'generator':W.GENERATOR,'judge':W.JUDGE,'card_sets':sets,'generation_manifest':manifest,
       'metrics':{'cards_requested':60,'cards_generated':60,'new_cards_generated':40,'preserved_cards':20,'cards':scores},
       'comparison':comparison,'carried_local_review':OLD['manual_review'],
       'cost_usd':cost,'pilot_cost_usd':OLD['cost_usd'],'cumulative_cost_usd':cost+OLD['cost_usd'],
       'calls':ledger['calls'],'reused_calls':reused,
       'settings':{'count_per_topic':15,'retained_per_topic':5,'generated_per_topic':10,'difficulty':3,'new_budget_usd':.20,
                   'repair_calls':0,'baseline_generation_calls':0,'original_rubric_only':True,'continuation_context_given':True},
       'source':baseline['source'],'production_modified':False,
       'evaluation_prompt_hashes':baseline['evaluation_prompt_hashes'],
       'limitations':comparison['confounds']}
    if (ROOT/'local-review.json').exists():
        review=W.read(ROOT/'local-review.json')
        for row in review['items']:
            slug,number=row['id'].rsplit('-',1);item=next(s['items'][int(number)-1] for s in sets if s['id']==slug)
            assert W.sha(json.dumps(item,sort_keys=True,ensure_ascii=False).encode())==row['item_sha256'],'Re-review changed outputs'
        a['local_review']=review
    if (ROOT/'rendering-checks.json').exists():a['rendering']=W.read(ROOT/'rendering-checks.json')
    return a

def main():
    a=build();W.write(ROOT/'result.json',a)
    (PROJECT/'clearleaf-sixty-data.js').write_text('window.MATHPDF_CLEARLEAF_SIXTY = '+json.dumps(a,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    fields=['set_topic','set_level','card_number','front_preview','self_contained_passes','faithfulness_ratio','atomic','front_leaks_answer','trivial','understanding_vs_rote','difficulty']
    with (ROOT/'cards_clearleaf_sixty.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
        for s in a['card_sets']:
            for c in s['metrics']['card_metrics']:
                faith=c['faithfulness'];wr.writerow(dict(zip(fields,[s['topic'],'Level 3',c['card_number'],c['front'],int(c['self_contained']['passes']),faith['supported']/faith['total'] if faith['total'] else 1,int(c['atomic']),int(c['front_leaks_answer']),int(c['trivial']),c['understanding_vs_rote'],c['difficulty']])))
    print(json.dumps({'new_cost_usd':a['cost_usd'],'cumulative_cost_usd':a['cumulative_cost_usd'],'scores':a['metrics']['cards'],'delta_pp':a['comparison']['delta_percentage_points'],'reused_calls':len(a['reused_calls'])}))
if __name__=='__main__':main()
