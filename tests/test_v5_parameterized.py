import copy, importlib.util, json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/v5-parameterized'
spec=importlib.util.spec_from_file_location('v5_engine',PATH/'engine.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)

def test_all_ten_closed_templates_and_exact_artifacts():
    pp=engine.params()
    assert len(pp)==10
    for t,p in pp.items():
        item=engine.build(t,p)
        assert engine.verify_artifact(item)
        assert item['checks']
        assert any(b['kind']=='math' for b in item['question'])
        assert all(b['source']['page'] in [63,64,65,66] for b in item['question']+item['answer'] if b['kind']=='math')

@pytest.mark.parametrize('template,p',[
 ('relation_missing',{'a':2,'b':3,'c':6}),
 ('relation_total',{'a':2,'b':2,'c':3}),
 ('square_nonnegative',{'k':-1}),
 ('reciprocal_bijection',{'a':0,'b':2}),
 ('composition_order',{'a':1,'b':3}),
 ('finite_range',{'domain':[1,1],'shift':2}),
 ('invented_family',{'a':1})])
def test_invalid_parameters_and_unsupported_tasks_fail_closed(template,p):
    with pytest.raises(ValueError):engine.build(template,p)

def test_tampered_codomain_formula_and_answer_are_rejected():
    original=engine.build('reciprocal_bijection',{'a':2,'b':1})
    for field,index in [('question',1),('answer',1)]:
        changed=copy.deepcopy(original)
        changed[field][index]['latex']='f(x)=0'
        with pytest.raises(ValueError):engine.verify_artifact(changed)
    changed=copy.deepcopy(original)
    changed['question'][1]['latex']=changed['question'][1]['latex'].replace(r'\{1\}',r'\{2\}')
    with pytest.raises(ValueError):engine.verify_artifact(changed)

def test_matrix_family_preserves_integer_inverse_for_many_coefficients():
    for k in range(-20,21):
        assert engine.validate('integer_pair_bijection',{'k':k})

def test_seed_is_reproducible():
    assert engine.params()==engine.params()

def test_public_v5_is_real_one_call_and_preserves_structure():
    run=json.loads((PATH/'result.json').read_text(encoding='utf-8'))
    assert run['version']=='v5' and run['reviewer_calls']==0 and run['generation_calls']==1
    assert len(run['items'])==10 and len({x['template_id'] for x in run['items']})==10
    assert run['rendering']['status']=='passed' and run['rendering']['fallbacks']==0
    assert run['rendering']['rendered_math_blocks']==36
    assert all(x['correct'] for x in run['manual_review']['items'])
    assert 0<run['cost_usd']<.01
    for item in run['items']:
        assert engine.verify_artifact({k:v for k,v in item.items() if k!='id'})
    assert json.loads(run['raw_output'])==run['plan']
    assert 'No repeated API call' in run['offline_validation_note']
    script=(ROOT/'parameterized-data.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_PARAMETERIZED = ').strip().removesuffix(';'))==run
    assert 'base64,' not in script and 'file_data' not in script and 'OPENAI_API_KEY' not in script
