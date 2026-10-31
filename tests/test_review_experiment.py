"""Published evidence must preserve model decisions and contradictory local facts."""
from fractions import Fraction
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def test_published_experiment_evidence():
    run=json.loads((ROOT/'experiments/review-four/result.json').read_text(encoding='utf-8'))
    assert len(run['problems'])==4
    assert [i['problem_id'] for i in run['blind']['items']]==[1,2,3,4]
    assert [i['problem_id'] for i in run['audit']['items']]==[1,2,3,4]
    assert all(i['decision']=='accept' for i in run['audit']['items'])
    assert run['manual_notes']['2']['severity']=='critical'
    assert Fraction(2**2-1,2)!=2+1-Fraction(1,2)
    assert abs(sum(c['cost_usd'] for c in run['calls'])-run['cost_usd'])<1e-12
    assert len(run['calls'])==3 and run['cost_usd']<.10
    assert run['source']['pages']==[63,64,65,66]
    assert run['source']['sha256']
    script=(ROOT/'reviews-data.js').read_text(encoding='utf-8')
    assert run in json.loads(script.removeprefix('window.MATHPDF_REVIEWS = ').strip().removesuffix(';'))


def test_public_result_contains_no_input_attachment_or_secrets():
    raw=(ROOT/'experiments/review-four/result.json').read_text(encoding='utf-8')
    assert 'file_data' not in raw and 'base64,' not in raw
    assert 'OPENAI_API_KEY' not in raw and 'production_prompt_hashes' in raw


def test_mini_run_preserves_review_and_local_findings():
    run=json.loads((ROOT/'experiments/review-mini-four/result.json').read_text(encoding='utf-8'))
    assert len(run['problems'])==4
    assert [x['decision'] for x in run['audit']['items']]==['accept','accept','accept','revise']
    assert set(run['manual_notes'])=={'3','4'}
    assert all('mini' in c['model'] for c in run['calls'])
    assert abs(sum(c['cost_usd'] for c in run['calls'])-run['cost_usd'])<1e-12
    assert run['cost_usd']<.035
    assert 'file_data' not in json.dumps(run)
