"""Evidence integrity and exact original metric definitions, without API calls."""
import hashlib
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'experiments/wildflower'

def result():return json.loads((FOLDER/'result.json').read_text(encoding='utf-8'))

def test_sample_and_generation_provenance():
    a=result()
    assert sum(len(s['items']) for s in a['card_sets'])==60
    assert sum(len(s['items']) for s in a['problem_sets'])==40
    assert all(len(s['items'])==15 for s in a['card_sets'])
    assert all(len(s['items'])==10 and [x['id'] for x in s['audit']]==list(range(1,11)) for s in a['problem_sets'])
    assert a['settings']['difficulty']==3 and a['settings']['repair_calls']==0
    assert a['production_modified'] is False and a['source']['full_pdf_uploaded'] is False
    assert len(a['generation_manifest'])==8
    for manifest in a['generation_manifest'].values():
        assert manifest['site_guards_passed']
        for name,digest in manifest['prompt_hashes'].items():
            # load_prompts hashes decoded prompt text, normalizing CRLF to LF.
            assert hashlib.sha256((FOLDER/'generator-prompts'/name).read_text(encoding='utf-8').encode()).hexdigest()==digest
    data=(ROOT/'wildflower-data.js').read_text(encoding='utf-8')
    assert json.loads(data.removeprefix('window.MATHPDF_WILDFLOWER = ').strip().removesuffix(';'))==a

def test_metrics_follow_original_evaluator_definitions():
    a=result()
    for s in a['card_sets']:
        cards=s['metrics']['card_metrics'];scores=s['summary'];assert len(cards)==15
        assert scores['pct_self_contained']==sum(c['self_contained']['passes'] for c in cards)/15
        assert scores['avg_faithfulness']==sum(c['faithfulness']['supported']/c['faithfulness']['total'] if c['faithfulness']['total'] else 1 for c in cards)/15
        assert scores['pct_atomic']==sum(c['atomic'] for c in cards)/15
        assert scores['pct_front_leaks']==sum(c['front_leaks_answer'] for c in cards)/15
        for c in cards:
            sc=c['self_contained']
            assert sc['passes']==(sc['understandable'] and sc['whats_missing'].strip()=='')
        involved={n for pair in s['metrics']['duplicate_pairs'] for n in [pair['card_a'],pair['card_b']]}
        assert scores['duplicate_rate']==len(involved)/15
        assert scores['coverage_ratio']==len(s['metrics']['coverage_covered'])/len(s['metrics']['coverage_key_concepts'])
    assert a['metrics']['cards']['pct_self_contained']==.8
    assert a['metrics']['cards']['avg_faithfulness']==pytest.approx(.8466666666666666)
    assert a['metrics']['problem_decisions']=={'accept':36,'reject':4}

def test_usage_costs_and_no_hidden_paid_retries():
    a=result();calls=a['calls'];assert len(calls)==216
    assert all(c['status']=='completed' for c in calls)
    assert len({(c['name'],c['digest']) for c in calls})==216
    assert sum(c['name'].startswith('generate-') for c in calls)==8
    assert a['cost_usd']==pytest.approx(sum(c['cost_usd'] for c in calls))
    assert a['cost_usd']<.15<a['settings']['budget_usd']
    assert sum(a['cost_by_stage'].values())==pytest.approx(a['cost_usd'])
    for c in calls:
        u=c['usage']
        if c['model']=='text-embedding-3-small':expected=u['total_tokens']*.02/1e6
        else:
            ri,rc,ro=(.4,.1,1.6) if c['model']=='gpt-4.1-mini' else (.15,.075,.6)
            cached=u['input_tokens_details']['cached_tokens']
            expected=((u['input_tokens']-cached)*ri+cached*rc+u['output_tokens']*ro)/1e6
        assert c['cost_usd']==pytest.approx(expected)

def test_local_contradictions_remain_separate_from_judge_approval():
    a=result();notes=a['local_checks']['items'];assert len(notes)==14
    for x in notes:
        kind,topic,n=x['id'].split('-');s=next(s for s in a['card_sets' if kind=='card' else 'problem_sets'] if s['id']==topic);item=s['items'][int(n)-1]
        assert x['item_sha256']==hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    refs={x['id']:x for x in notes}
    assert refs['problem-induction-2']['witness']['remainder_mod_12']==6
    assert refs['problem-functions-5']['witness']['unique_rational_preimage']==['4/9','-1/9']
    sets=next(s for s in a['problem_sets'] if s['id']=='sets')
    assert sets['audit'][4]['decision']=='accept'  # Original erroneous approval retained.
    assert refs['problem-sets-5']['kind']=='incorrect_solution'
    assert sum(x['kind']=='model_false_rejection' for x in notes)==3

def test_public_evidence_excludes_input_payloads_and_history_is_preserved():
    text=(FOLDER/'result.json').read_text(encoding='utf-8')
    assert 'file_data' not in text and 'base64,' not in text
    assert 'OPENAI_API_KEY' not in text and 'sk-proj-' not in text
    history=json.loads((ROOT/'data/history.json').read_text(encoding='utf-8'))
    assert len(history['cards'])==505 and len(history['issues'])==19
