"""Equal-size comparison must retain the pilot, rubric and batch confounds."""
import hashlib,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'experiments/clearleaf-sixty'
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def test_sixty_cards_preserve_all_twenty_originals_and_append_exactly_forty():
    a=read(FOLDER/'result.json');old=read(ROOT/'experiments/clearleaf/result.json')
    assert len(a['card_sets'])==4 and sum(len(s['items']) for s in a['card_sets'])==60
    assert a['metrics']['new_cards_generated']==40 and a['metrics']['preserved_cards']==20
    for s in a['card_sets']:
        original=next(x for x in old['card_sets'] if x['id']==s['id'])
        assert len(s['items'])==15 and s['items'][:5]==original['items']
        assert s['origins']==['clearleaf-20']*5+['clearleaf-extension']*10
        assert s['pages']==original['pages']
        assert a['generation_manifest'][s['id']]['prompt_hashes']==old['generation_manifest'][s['id']]['prompt_hashes']
    script=(ROOT/'clearleaf-sixty-data.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_CLEARLEAF_SIXTY = ').strip().removesuffix(';'))==a

def test_equal_count_original_rubric_comparison_has_exact_deltas_and_limits():
    a=read(FOLDER/'result.json');b=read(ROOT/'experiments/wildflower/result.json');comparison=a['comparison']
    assert comparison['baseline_count']==comparison['candidate_count']==60
    assert a['settings']['original_rubric_only'] and a['settings']['continuation_context_given']
    assert a['evaluation_prompt_hashes']==b['evaluation_prompt_hashes']
    assert a['source']['sha256']==b['source']['sha256']
    for key,value in a['metrics']['cards'].items():
        assert comparison['delta_percentage_points'][key]==pytest.approx((value-b['metrics']['cards'][key])*100)
    assert a['metrics']['cards']['pct_self_contained']==47/60
    assert a['metrics']['cards']['pct_atomic']==53/60
    assert a['metrics']['cards']['avg_faithfulness']==pytest.approx(.9077777777777778)
    assert 'revised_self_contained' not in a['metrics']
    assert any('prior cards in context' in text for text in comparison['confounds'])

def test_reused_checks_cost_nothing_again_and_new_calls_stay_bounded():
    a=read(FOLDER/'result.json')
    assert len(a['calls'])==144 and len(a['reused_calls'])==64
    assert all(c['status']=='completed' for c in a['calls'])
    assert sum(c['name'].startswith('generate-') for c in a['calls'])==4
    assert all(c['new_cost_usd']==0 for c in a['reused_calls'])
    assert a['cost_usd']==pytest.approx(sum(c['cost_usd'] for c in a['calls']))
    assert a['cost_usd']<.08<a['settings']['new_budget_usd']
    assert a['cumulative_cost_usd']==pytest.approx(a['pilot_cost_usd']+a['cost_usd'])
    assert a['production_modified'] is False
    raw=(FOLDER/'result.json').read_text(encoding='utf-8')
    assert 'file_data' not in raw and 'base64,' not in raw and 'OPENAI_API_KEY' not in raw

def test_local_findings_are_tied_to_actual_new_cards_and_duplicate_evidence():
    a=read(FOLDER/'result.json');review=a['local_review'];assert review['added_cards_inspected']==40
    assert len(review['items'])==40
    for row in review['items']:
        slug,n=row['id'].rsplit('-',1);item=next(s['items'][int(n)-1] for s in a['card_sets'] if s['id']==slug)
        assert row['item_sha256']==hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    assert review['summary']['definite_additional_semantic_duplicate_cards']==2
    for slug,old_n,new_n in [('numbers',4,13),('induction',5,15)]:
        s=next(s for s in a['card_sets'] if s['id']==slug)
        assert s['items'][old_n-1]['question']!=s['items'][new_n-1]['question']
        assert 'semantic_duplicate' in next(r['flags'] for r in review['items'] if r['id']==f'{slug}-{new_n}')
    s=next(s for s in a['card_sets'] if s['id']=='induction')
    assert '2 to the power n by 2 to the power n' in s['items'][13]['question'][0]['text']
