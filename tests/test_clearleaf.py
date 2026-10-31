"""The pilot must preserve changed-prompt provenance and contradictory assessments."""
import hashlib,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'experiments/clearleaf'
def read():return json.loads((FOLDER/'result.json').read_text(encoding='utf-8'))

def test_exactly_twenty_candidate_cards_and_one_generator_prompt_changed():
    a=read();assert len(a['card_sets'])==4 and all(len(s['items'])==5 for s in a['card_sets'])
    assert a['settings']['baseline_generation_calls']==0 and a['settings']['repair_calls']==0
    assert a['production_modified'] is False and a['source']['full_pdf_uploaded'] is False
    assert a['changed_generator_prompts']==['flashcards.md']
    for p in (FOLDER/'generator-prompts').glob('*.md'):
        old=(ROOT/'experiments/wildflower/generator-prompts'/p.name).read_text(encoding='utf-8')
        assert (p.read_text(encoding='utf-8')!=old)==(p.name=='flashcards.md')
    for m in a['generation_manifest'].values():
        for name,digest in m['prompt_hashes'].items():
            assert hashlib.sha256((FOLDER/'generator-prompts'/name).read_text(encoding='utf-8').encode()).hexdigest()==digest
    script=(ROOT/'clearleaf-data.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_CLEARLEAF = ').strip().removesuffix(';'))==a

def test_original_and_revised_metrics_are_not_replaced_by_each_other():
    a=read();original=sum(c['self_contained']['passes'] for s in a['card_sets'] for c in s['metrics']['card_metrics'])
    assert original==14 and a['metrics']['cards']['pct_self_contained']==.7
    assert a['metrics']['revised_self_contained']=={'passed':18,'total':20}
    assert a['calibration']['matched']==8 and a['calibration']['total']==8
    assert a['calibration']['overlaps_prompt_examples'] is True
    assert len(a['calibration']['items'])==8
    assert a['metrics']['cards']['avg_faithfulness']==pytest.approx(.8358333333333332)
    assert a['metrics']['cards']['pct_atomic']==.7
    assert a['manual_review']['summary']['atomic']==15
    assert a['manual_review']['summary']['self_contained']==18
    assert a['manual_review']['summary']['wrong_citations']==1
    assert 'Not ready' in a['manual_review']['decision']

def test_usage_is_complete_budgeted_and_has_no_extra_baseline_generation():
    a=read();calls=a['calls'];assert len(calls)==112
    assert all(c['status']=='completed' for c in calls)
    assert sum(c['name'].startswith('generate-') for c in calls)==4
    assert len({(c['name'],c['digest']) for c in calls})==112
    assert a['cost_usd']==pytest.approx(sum(c['cost_usd'] for c in calls))
    assert a['cost_usd']<.06<a['settings']['budget_usd']
    assert sum(a['cost_by_stage'].values())==pytest.approx(a['cost_usd'])
    raw=(FOLDER/'result.json').read_text(encoding='utf-8')
    assert 'file_data' not in raw and 'base64,' not in raw and 'OPENAI_API_KEY' not in raw

def test_local_review_is_tied_to_frozen_items_and_missing_regression_is_disclosed():
    a=read();frozen=json.loads((FOLDER/'local-review-inputs.json').read_text(encoding='utf-8'))
    for s in a['card_sets']:
        assert hashlib.sha256(json.dumps(s['items'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()==frozen[s['id']]
        for i,p in enumerate(s['items'],1):
            note=next(r for r in a['manual_review']['items'] if r['id']==f'{s["id"]}-{i}')
            assert note['item_sha256']==hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    numbers=next(s for s in a['card_sets'] if s['id']=='numbers')
    refs=[b['source']['page'] for b in numbers['items'][4]['answer'] if b.get('source')]
    if numbers['items'][4].get('source'):refs.append(numbers['items'][4]['source']['page'])
    assert 27 in refs
    note=next(r for r in a['manual_review']['items'] if r['id']=='numbers-5')
    assert 'wrong_citation' in note['flags'] and '26' in note['note']
    assert 'omits' in a['manual_review']['regression_scope']
