import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_cycle_preserves_real_outputs_and_disagreement():
    run=json.loads((ROOT/'experiments/cycle-fifteen/result.json').read_text(encoding='utf-8'))
    assert len(run['before'])==len(run['after'])==15
    assert [x['id'] for x in run['review']['items']]==list(range(1,16))
    assert [x['id'] for x in run['final']['items']]==list(range(1,16))
    assert run['metrics']['before_accepts']==14 and run['metrics']['after_accepts']==15
    assert run['metrics']['local_before_correct']==run['metrics']['local_after_correct']==14
    assert not run['review']['items'][8]['accept']  # False rejection retained, never rewritten.
    assert run['review']['items'][12]['accept'] and run['final']['items'][12]['accept']
    assert not run['local_review']['items'][12]['after_correct']
    assert run['metrics']['structured_math_before']==124
    assert run['metrics']['structured_math_after']==0
    assert run['review_prompt_identical']
    assert 'original_items' not in json.loads(run['stage_tasks']['final'])
    assert 'review' not in json.loads(run['stage_tasks']['final'])
    assert len(run['calls'])==4 and 0<run['cost_usd']<.20
    assert abs(run['cost_usd']-sum(c['cost_usd'] for c in run['calls']))<1e-12
    for side in ['before','after']:
        assert run['rendering_checks'][side]['fallbacks']==0
    assert 'file_data' not in json.dumps(run) and 'base64,' not in json.dumps(run)
    raw=(ROOT/'cycle-data.js').read_text(encoding='utf-8')
    assert json.loads(raw.removeprefix('window.MATHPDF_CYCLE = ').strip().removesuffix(';'))==run

def test_cycle_exact_counterexamples():
    path=ROOT/'experiments/cycle-fifteen/local_checks.py'
    spec=importlib.util.spec_from_file_location('cycle_checks',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert mod.check()
