import json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_controlled_comparison():
    run=json.loads((ROOT/'experiments/compare-ten/result.json').read_text(encoding='utf-8'))
    assert len(run['cases'])==10
    assert sum(c['expected_accept'] for c in run['cases'])==5
    assert run['results']['mini']['input_sha256']==run['results']['full']['input_sha256']
    assert run['results']['mini']['prompt_sha256']==run['results']['full']['prompt_sha256']
    for arm in ['mini','full']:
        items=run['results'][arm]['parsed']['items']
        assert [i['id'] for i in items]==list(range(1,11))
        assert run['scores'][arm]['correct_decisions']==sum(i['accept']==c['expected_accept'] for i,c in zip(items,run['cases']))
    assert run['scores']['mini']['false_accepts']==1
    assert run['scores']['full']['correct_decisions']==10
    assert 'full:1' in run['explanation_notes']
    assert 0<run['cost_usd']<.05
    assert abs(run['cost_usd']-sum(r['cost_usd'] for r in run['results'].values()))<1e-12
    assert Fraction(2**2-1,2)!=2+1-Fraction(1,2)
    assert 2*Fraction(3,5)-Fraction(1,5)==1
    assert Fraction(3,5)-3*Fraction(1,5)==0
    raw=(ROOT/'comparison-data.js').read_text(encoding='utf-8')
    assert json.loads(raw.removeprefix('window.MATHPDF_COMPARISON = ').strip().removesuffix(';'))==run
