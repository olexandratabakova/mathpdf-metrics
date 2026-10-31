import copy,importlib.util,sys,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/rag-hundred'
# Distinct module name avoids collision with other experiments' engine modules.
spec=importlib.util.spec_from_file_location('hundred_engine_test',PATH/'engine.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
def test_fifty_supported_families_produce_one_hundred_bounded_variants():
    assert len(E.templates())==50
    items=[E.build(t,E.params(t,v)) for t in E.templates() for v in [0,1]]
    assert len(items)==100 and len({x['topic'] for x in items})==10
    assert all(E.verify(x) for x in items)
def test_zero_polynomial_is_both_even_and_odd_and_constant_is_not_strict():
    p=E.build('world_parity',{'coefficients':[0]})
    assert any('Even: True. Odd: True.' in b.get('text','') for b in p['answer'])
    m=E.build('world_monotonic',{'a':0,'b':7})
    text=' '.join(b.get('text','') for b in m['answer'])
    assert 'Strictly increasing: False' in text and 'Strictly decreasing: False' in text
def test_poset_extrema_do_not_conflate_maximal_and_greatest():
    x=E.build('order_extrema',{'a':2,'mode':1})
    assert any('greatest: none' in b.get('text','') for b in x['answer'])
    assert any('4' in b.get('latex','') and '6' in b.get('latex','') and '10' in b.get('latex','') for b in x['answer'])
    y=E.build('order_subsets',{'U':[1,2,3],'mode':1})
    assert any(r'least}:\quad \varnothing' in b.get('latex','') for b in y['answer'])
def test_relation_properties_find_missing_diagonal_and_transitive_witness():
    S=[1,2,3];props,w=E.relation_properties(S,{(1,1),(2,2),(1,2),(2,3)})
    assert not props['reflexive'] and w['reflexive']==3
    assert not props['transitive'] and w['transitive']==(1,2,3)
def test_new_family_tampering_and_invalid_domains_fail():
    x=E.build('world_domain',{'a':3,'c':2});bad=copy.deepcopy(x);bad['answer'][-1]['latex']=r'D=\mathbb R'
    with pytest.raises(ValueError):E.verify(bad)
    with pytest.raises(ValueError):E.build('world_domain',{'a':0,'c':2})
    with pytest.raises(ValueError):E.build('order_bounds',{'p':2,'q':2})
    with pytest.raises(ValueError):E.build('unknown_family',{})

def test_published_hundred_preserves_first_rejection_and_bounded_repair():
    run=json.loads((PATH/'result.json').read_text(encoding='utf-8'))
    assert len(run['tasks'])==100 and len(run['profiles'])==50 and len(run['topics'])==10
    assert run['metrics']['first_pass_task_accepts']==98
    assert run['metrics']['program_verified']==100 and run['metrics']['repaired_profiles']==1
    assert [x['id'] for x in run['tasks']]==list(range(1,101))
    assert len({json.dumps(t['artifact']['question'],sort_keys=True) for t in run['tasks']})==100
    for t in run['tasks']:assert E.verify(t['artifact'])
    fixed=[p for p in run['profiles'] if p['repaired']]
    assert len(fixed)==1 and fixed[0]['id']==14 and not fixed[0]['original_in_context']
    assert fixed[0]['final_choice']['template_id'] in [d['id'] for d in fixed[0]['final_ranking']]
    assert run['reviewer_calls']==0 and run['generation_plan_calls']==2
    assert not run['expected_labels_sent'] and not run['full_pdf_uploaded']
    assert abs(run['cost_usd']-sum(run['costs'].values()))<1e-12 and run['cost_usd']<.05
    assert run['rendering']['status']=='passed' and run['rendering']['rendered_math_blocks']==294
    for src in run['sources']:
        assert not src['full_document_text_extracted']
        assert len(src['unique_pages_accessed'])<src['pages_total']
    assert run['sources'][0]['pages_total']==74 and run['sources'][1]['pages_total']==380
    raw=(ROOT/'hundred-data.js').read_text(encoding='utf-8')
    assert json.loads(raw.removeprefix('window.MATHPDF_HUNDRED = ').strip().removesuffix(';'))==run
    assert 'selected_excerpt' not in raw and 'file_data' not in raw and 'base64,' not in raw

def test_optional_sympy_spot_checks_new_polynomial_and_domain_families():
    sys.path.insert(0,str(ROOT/'experiments/sympy-55/.deps'))
    s=pytest.importorskip('sympy')
    x=s.Symbol('x',real=True)
    for variant in [0,1]:
        p=E.params('world_parity',variant);coeff=p['coefficients'];poly=sum(c*x**i for i,c in enumerate(coeff))
        item=E.build('world_parity',p);even=s.expand(poly.subs(x,-x)-poly)==0;odd=s.expand(poly.subs(x,-x)+poly)==0
        assert any(f'Even: {even}. Odd: {odd}.' in b.get('text','') for b in item['answer'])
        p=E.params('world_domain',variant)
        assert s.solveset(x*x-p['a']**2,x,domain=s.S.Reals)==s.FiniteSet(-p['a'],p['a'])
