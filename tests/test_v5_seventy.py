import copy,importlib.util,json
from collections import Counter
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/v5-seventy'
spec=importlib.util.spec_from_file_location('seventy_engine',PATH/'engine.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)

def test_seventy_unique_variants_across_seven_topics():
    items=e.generate()
    assert len(items)==70 and Counter(x['topic'] for x in items)=={t:10 for t in e.TOPICS}
    assert len({(x['template_id'],str(x['parameters'])) for x in items})==70
    assert len({x['template_id'] for x in items})==40
    assert all(e.verify_artifact(x) for x in items)
    assert e.generate()==items

@pytest.mark.parametrize('t,p',[
 ('ind_squares',{'c':0}),('ind_harmonic',{'c':-3}),
 ('ph_repunit',{'m':10}),('ph_repunit',{'m':5}),
 ('ph_square',{'q':0,'side':3}),('ph_boxes',{'boxes':0,'target':3}),
 ('mod_impossible',{'a':2,'b':3}),('mod_linear',{'a':2,'b':3,'m':1}),
 ('count_combinations',{'n':3,'k':4}),('count_stars',{'n':-1}),
 ('int_division',{'a':-5,'b':0}),('sets_complement',{'U':[1,2],'A':[3],'B':[1],'C':[2]}),
 ('unknown',{'n':3})])
def test_invalid_or_unsupported_parameters_rejected(t,p):
    with pytest.raises(ValueError):e.build(t,p)

def test_induction_algebra_is_exact_not_a_finite_example_claim():
    for t in ['ind_squares','ind_odd','ind_factorial','ind_divisible','ind_harmonic']:
        for c in [1,2,7,101]:assert e.induction_certificate(t,c)
    assert not e.equal([0,1],[0,2])
    assert e.equal(e.mul([1,1],[1,1]),[1,2,1])

def test_false_answer_and_domain_mutations_rejected():
    for topic in e.TOPICS:
        x=next(x for x in e.generate() if x['topic']==topic)
        bad=copy.deepcopy(x);bad['answer'][0]={'kind':'text','text':'All integers are prime.'}
        with pytest.raises(ValueError):e.verify_artifact(bad)
    x=next(x for x in e.generate() if x['template_id']=='ind_squares')
    bad=copy.deepcopy(x);bad['question'][-1]['latex']+=' + 1'
    with pytest.raises(ValueError):e.verify_artifact(bad)

def test_negative_division_and_noninvertible_congruence():
    x=e.build('int_division',{'a':-17,'b':5});assert any('-4' in b.get('latex','') and '+3' in b.get('latex','') for b in x['answer'])
    no=e.build('mod_linear',{'a':2,'b':1,'m':4})
    assert '\\varnothing' in no['answer'][-1]['latex']
    two=e.build('mod_linear',{'a':2,'b':2,'m':4})
    assert '\\{1,3\\}' in two['answer'][-1]['latex']

def test_published_seventy_results_are_real_and_separate():
    run=json.loads((PATH/'result.json').read_text(encoding='utf-8'))
    assert len(run['items'])==70 and run['families']==40
    assert Counter(x['topic'] for x in run['items'])=={t:10 for t in e.TOPICS}
    assert run['reviewer_calls']==0 and run['generation_calls']==1
    assert json.loads(run['raw_output'])==run['plan']
    assert all(e.verify_artifact(x) for x in run['items'])
    assert e.generate(run['plan']['topic_order'])==run['items']
    assert 0<run['cost_usd']<.01
    assert run['rendering']['status']=='passed'
    assert run['rendering']['rendered_math_blocks']==201
    assert run['rendering']['fallbacks']==0 and run['rendering']['history_cards']==505
    script=(ROOT/'seventy-data.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_SEVENTY = ').strip().removesuffix(';'))==run
    assert 'file_data' not in script and 'base64,' not in script and 'OPENAI_API_KEY' not in script
