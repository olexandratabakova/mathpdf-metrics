"""Build a local reviewable report from original outputs; no API calls."""
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def prose(value):
    if isinstance(value, str): return value
    if isinstance(value, list): return '\n\n'.join(prose(v) for v in value)
    if 'parts' in value: return ''.join(prose(v) for v in value['parts'])
    if 'math' in value: return '$'+value['math']+'$'
    if 'latex' in value: return '$$'+value['latex']+'$$'
    return ''

def main():
    ledger=read(ROOT/'output/ledger.json')
    assert all(c['status']=='completed' for c in ledger['calls'])
    local=read(ROOT/'local-review.json'); review={r['id']:r for r in local['items']}
    sets=[]
    for slug in ['sets','induction','numbers','functions']:
        a=read(ROOT/'output'/f'{slug}-flashcards.json')
        ev=read(ROOT/'output'/f'{slug}-card-metrics.json')
        revised=read(ROOT/'output'/f'{slug}-revised-self-contained.json')
        assert len(a['compact']['items'])==len(ev['metrics']['card_metrics'])==5
        for i,c in enumerate(a['compact']['items'],1):
            assert hashlib.sha256(json.dumps(c,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==review[f'{slug}-{i}']['item_sha256']
        sets.append({'id':slug,**{k:a[k] for k in ['topic','pages','compact','items','usage','cost_usd','resolved_model','prompt_hashes','source_sha256','selected_pdf_sha256','site_guards_passed']},'evaluation':ev,'revised_self_contained':revised})
    keys=['pct_self_contained','avg_faithfulness','pct_front_leaks','pct_atomic','pct_understanding','pct_trivial','duplicate_rate','coverage_ratio','avg_back_length']
    metrics={k:sum(s['evaluation']['summary'][k]*5 for s in sets)/20 for k in keys}
    items=[c for s in sets for c in s['compact']['items']]
    cost=sum(c['cost_usd'] for c in ledger['calls'])
    result={'id':'briefleaf-refined','status':'not_ready_to_promote','generator':'gpt-4.1-mini','judge':'gpt-4o-mini','cards':20,'cost_usd':cost,'generation_cost_usd':sum(s['cost_usd'] for s in sets),'metrics':metrics,'revised_self_contained':{'passed':sum(s['revised_self_contained']['passed'] for s in sets),'total':20},'calibration':read(ROOT/'output/calibration.json'),'mechanical_summary':{'front_words_mean':sum(len(' '.join(c['question']).split()) for c in items)/20,'nonempty_explanation':sum(bool(c['explanation']) for c in items),'nonempty_legacy_answer':sum(bool(c['answer']) for c in items)},'card_sets':sets,'local_review':local,'rendering':read(ROOT/'rendering-checks.json'),'ledger':ledger,'limitations':['Original model metrics are fallible signals, not mathematical correctness.','Revised diagnostic is separate; overlapping known controls do not establish broad calibration.','No paired baseline, automatic repair, production changes or website publication.','Coverage is a card-weighted set mean; duplicates are within-topic embedding signals.']}
    write(ROOT/'result.json',result)
    lines=['# Briefleaf refined · 20 cards and evaluation','',f'Generator: gpt-4.1-mini. Judge: gpt-4o-mini. Cost: ${cost:.8f}. Original outputs retained. Not ready to promote.','', '| Original metric | Result |','| --- | ---: |']
    lines += [f'| {k} | {v*100:.1f}% |' for k,v in metrics.items() if k!='avg_back_length']
    lines += ['',f'Revised self-containment diagnostic: {result["revised_self_contained"]["passed"]}/20, separate from original rubric. No overall correctness percentage.','','## Cards','']
    for s in sets:
        lines+=['## '+s['topic'],'']
        for i,c in enumerate(s['compact']['items'],1):
            r=review[f'{s["id"]}-{i}']
            lines += [f'### {i}. {c["title"]}','','**Question:** '+prose(c['question']),'','**From notes:** '+(prose(c['from_notes']) or '(empty)'),'','**Explanation:** '+(prose(c['explanation']) or '(empty)'),'',f'Source page: {c["formula"]["page"]}. Skill: {c["skill"]}.','']
            if 'latex' in c['formula']: lines+=['Central formula: '+prose(c['formula']),'']
            if r['note']: lines+=['**Local finding:** '+r['note'],'']
    (ROOT/'cards.md').write_text('\n'.join(lines),encoding='utf-8')
    with (ROOT/'cards_briefleaf_refined.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['set_topic','set_level','card_number','front_preview','self_contained_passes','faithfulness_ratio','atomic','front_leaks_answer','trivial','understanding_vs_rote','difficulty']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for s in sets:
            for c in s['evaluation']['metrics']['card_metrics']:
                faith=c['faithfulness']
                writer.writerow(dict(zip(fields,[s['topic'],'Level 3',c['card_number'],c['front'],int(c['self_contained']['passes']),faith['supported']/faith['total'] if faith['total'] else 1,int(c['atomic']),int(c['front_leaks_answer']),int(c['trivial']),c['understanding_vs_rote'],c['difficulty']])))
    print(json.dumps({k:result[k] for k in ['cost_usd','metrics','revised_self_contained','mechanical_summary']}))

if __name__=='__main__': main()
