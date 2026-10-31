import importlib.util,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/sympy-55'
sys.path.insert(0,str(PATH/'.deps'))
pytest.importorskip('sympy',reason='Install isolated experiments/sympy-55/requirements.txt to run library tests')
spec=importlib.util.spec_from_file_location('sympy_experiment',PATH/'verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def task(kind,p,answer,steps=None):
    return {'kind':kind,'params_json':json.dumps(p),'answer':answer,'steps':steps or []}
def test_known_algebra_errors_and_domain_holes():
    d='Complement(Reals,FiniteSet(0))'
    assert v.one(task('expression',{'expr':'(x**2-1)/x','domain':d},'x+1-1/x'))['status']=='refuted'
    assert v.one(task('expression',{'expr':'(x**2-1)/x','domain':d},'x-1/x'))['status']=='confirmed'
    assert v.one(task('solve',{'expr':'(x**2-9)/(x-3)-6','domain':'Reals'},'EmptySet'))['status']=='confirmed'
    assert v.one(task('expression',{'expr':'1/x','domain':'Reals'},'1/x'))['status']=='refuted'
def test_assumptions_are_not_silently_discarded():
    assert v.one(task('expression',{'expr':'sqrt(x**2)','domain':'Reals'},'x'))['status']=='refuted'
    assert v.one(task('expression',{'expr':'sqrt(x**2)','domain':'Interval(0,oo)'},'x'))['status']=='confirmed'
    assert v.one(task('solve',{'expr':'x**2-2','domain':'Integers'},'EmptySet'))['status']=='confirmed'
def test_function_codomain_error_not_approved():
    p={'expr':'2/x+1','domain':'Complement(Reals,FiniteSet(0))','codomain':'Complement(Reals,FiniteSet(2))','property':'bijective'}
    assert v.one(task('function',p,'True'))['status']=='refuted'
    p['codomain']='Complement(Reals,FiniteSet(1))'
    assert v.one(task('function',p,'True'))['status']=='confirmed'
def test_partial_and_unsupported_are_not_approvals():
    assert v.one(task('proof',{'claim':'Any general theorem'},'True'))['status']=='unsupported'
    assert v.one(task('counting',{'expression':'binomial(7,3)'},'35'))['status']=='partial'
    assert v.one(task('induction',{'term':'k','lower':1,'upper':'n'},'n*(n+1)/2'))['status']=='partial'
    assert v.one(task('summation',{'term':'k','lower':1,'upper':'n'},'n**2'))['status']=='refuted'
def test_wrong_intermediate_equality_not_hidden_by_right_answer():
    t=task('expression',{'expr':'x+1','domain':'Reals'},'x+1',[{'left':'x+1','right':'x+2'}])
    assert v.one(t)['status']=='refuted'
    t['steps']=[{'left':'x \\equiv 1','right':'TeX is not executable'}]
    assert v.one(t)['status']=='partial'
def test_non_coprime_congruence_all_classes():
    p={'a':6,'b':9,'modulus':15}
    assert v.one(task('congruence',p,'FiniteSet(4,9,14)'))['status']=='confirmed'
    assert v.one(task('congruence',p,'FiniteSet(4)'))['status']=='refuted'
@pytest.mark.parametrize('expr',["__import__('os')","x.__class__","open('secret')","[x for x in range(10)]",'2**1000000','0.5'])
def test_model_expression_cannot_execute_code(expr):
    with pytest.raises(Exception):v.parse(expr)

def test_public_results_preserve_scopes_and_local_counterexamples():
    run=json.loads((PATH/'result.json').read_text(encoding='utf-8'))
    assert [len(g['items']) for g in run['groups']]==[40,15]
    assert run['counts']=={'confirmed':16,'partial':30,'refuted':1,'unsupported':8}
    assert run['reviewer_calls']==0 and len(run['calls'])==4
    assert abs(run['cost_usd']-sum(c['cost_usd'] for c in run['calls']))<1e-12
    assert run['cost_usd']<.12
    assert run['groups'][0]['items'][6]['check']['status']=='refuted'
    assert run['manual_notes']['near2:7']['type']=='formalization'
    assert sum(n['type']=='mathematical_error' for n in run['manual_notes'].values())==4
    assert run['rendering']['status']=='passed' and run['rendering']['tasks']==55
    assert run['local_checks']['birthday_counts']==[5,5]+[4]*10
    raw=(ROOT/'symbolic-data.js').read_text(encoding='utf-8')
    assert json.loads(raw.removeprefix('window.MATHPDF_SYMBOLIC = ').strip().removesuffix(';'))==run
    assert 'file_data' not in raw and 'base64,' not in raw and 'OPENAI_API_KEY' not in raw
