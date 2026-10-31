"""Bounded, fail-closed SymPy adapters. No eval, sympify, model code or model reviewer.

Confirmed means a formal computational contract, never all learner-facing prose.
Each task runs in a child process with an eight-second wall-time limit.
"""
import ast,itertools,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
import sympy as s
from sympy.calculus.util import continuous_domain,function_range
X=s.Symbol('x',real=True);Y=s.Symbol('y',real=True);N=s.Symbol('n',integer=True,positive=True);K=s.Symbol('k',integer=True)
NAMES={'x':X,'y':Y,'n':N,'k':K,'pi':s.pi,'E':s.E,'oo':s.oo,'EmptySet':s.EmptySet,'Reals':s.S.Reals,'Integers':s.S.Integers,'Naturals':s.S.Naturals,'True':True,'False':False}
FUNCS={n:getattr(s,n) for n in ['sqrt','sin','cos','exp','log','factorial','binomial','Abs','FiniteSet','Interval','Union','Complement','Range']}
FUNCS.update({'gcd':s.gcd,'lcm':s.lcm,'Mod':s.Mod})
class Unsupported(Exception):pass
def parse(text):
    if not isinstance(text,str) or len(text)>2500:raise Unsupported('Expression length limit')
    tree=ast.parse(text,mode='eval')
    if sum(1 for _ in ast.walk(tree))>250:raise Unsupported('Expression complexity limit')
    def visit(n,depth=0):
        if depth>30:raise Unsupported('Expression depth limit')
        if isinstance(n,ast.Constant):
            if type(n.value) is bool:return n.value
            if type(n.value) is int and abs(n.value)<=10**9:return s.Integer(n.value)
            raise Unsupported('Only bounded exact integer literals allowed')
        if isinstance(n,ast.Name) and n.id in NAMES:return NAMES[n.id]
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            a=visit(n.operand,depth+1);return -a if isinstance(n.op,ast.USub) else a
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left,depth+1),visit(n.right,depth+1)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Mod):return s.Mod(a,b)
            if isinstance(n.op,ast.Pow):
                if b.is_number and (not b.is_real or abs(b)>200):raise Unsupported('Power limit')
                return a**b
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in FUNCS and not n.keywords:
            args=[visit(a,depth+1) for a in n.args]
            if n.func.id in ['factorial','binomial'] and any(getattr(a,'is_number',False) and abs(a)>200 for a in args):raise Unsupported('Combinatorial bound')
            return FUNCS[n.func.id](*args)
        if isinstance(n,ast.Tuple):return s.Tuple(*(visit(a,depth+1) for a in n.elts))
        if isinstance(n,ast.List):return [visit(a,depth+1) for a in n.elts]
        raise Unsupported('Unsupported expression syntax; no attributes, arbitrary functions or code')
    return visit(tree.body)
def poles(text,domain):
    result=s.EmptySet
    for node in ast.walk(ast.parse(text,mode='eval')):
        denominator=None
        if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div):denominator=node.right
        if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Pow):
            exponent=parse(ast.unparse(node.right))
            if getattr(exponent,'is_negative',False):denominator=node.left
        if denominator is not None:
            value=parse(ast.unparse(denominator))
            if X in value.free_symbols:
                zeros=s.solveset(value,X,domain=domain)
                if isinstance(zeros,s.ConditionSet):raise Unsupported('Unknown denominator roots')
                result=s.Union(result,zeros)
            elif value==0:raise Unsupported('Zero denominator')
    return result
def compare(a,b,domain=s.S.Reals):
    if isinstance(a,s.Set) or isinstance(b,s.Set):
        if not isinstance(a,s.Set) or not isinstance(b,s.Set):return False,'Answer types differ'
        if a==b:return True,'Exact sets coincide'
        delta=s.SymmetricDifference(a,b)
        if delta.is_empty is True:return True,'Empty symmetric difference'
        if delta.is_empty is False:return False,'Nonempty symmetric difference: '+str(delta)
        return None,'Set equality undecided'
    d=s.simplify(a-b)
    if d==0:return True,'Symbolic difference is exactly zero'
    if isinstance(domain,s.Set) and domain.is_subset(s.Interval(0,s.oo)) is True:
        d=s.refine(d,s.Q.nonnegative(X))
        if d==0:return True,'Difference zero under original nonnegative domain'
    symbols=sorted(d.free_symbols,key=str)
    if not symbols and d.is_zero is False:return False,'Exact nonzero difference: '+str(d)
    vals=[s.Integer(-3),s.Integer(-1),s.Integer(0),s.Rational(1,2),s.Integer(1),s.Integer(2),s.Integer(3),s.Integer(5)]
    for vv in itertools.islice(itertools.product(vals,repeat=len(symbols)),120):
        sub=dict(zip(symbols,vv))
        if any(sym==N and (val<1 or val.is_integer is not True) for sym,val in sub.items()):continue
        if any(sym==K and val.is_integer is not True for sym,val in sub.items()):continue
        if X in sub and domain.contains(sub[X])!=s.true:continue
        value=s.simplify(d.subs(sub))
        if not value.free_symbols and value.is_finite is True and value.is_zero is False:
            return False,'Exact counterexample '+str(sub)+': difference '+str(value)
    return None,'Could not prove identity or find a valid counterexample'
def domain_ok(expr,text,domain):
    pp=poles(text,domain)
    if pp.is_empty is False:return False,'Original allowed domain contains denominator zero(s): '+str(pp)
    actual=continuous_domain(expr,X,s.S.Reals)
    ok=domain.is_subset(actual)
    return ok,'Expression domain '+str(actual)+'; allowed '+str(domain)
def result(status,evidence,actual=None,scope='formal_computation_only'):
    return {'status':status,'evidence':evidence,'actual':str(actual) if actual is not None else None,'actual_latex':s.latex(actual) if isinstance(actual,s.Basic) else None,'scope':scope,'sympy_version':s.__version__}
def verify(task):
    kind=task['kind'];p=json.loads(task['params_json'])
    if not isinstance(p,dict):raise Unsupported('Formal parameters must be an object')
    if kind=='proof':return result('unsupported','General proof outside implemented SymPy contracts; no approval inferred',scope='none')
    domain=parse(p.get('domain','Reals'));actual=None;partial=False
    if not isinstance(domain,s.Set):raise Unsupported('Domain must be a set')
    if kind=='expression':
        expr=parse(p['expr']);ok,ev=domain_ok(expr,p['expr'],domain)
        if ok is False:return result('refuted',ev)
        if ok is not True:raise Unsupported('Original domain could not be established')
        answer=parse(task['answer'])
        if poles(task['answer'],domain).is_empty is False:return result('refuted','Proposed expression introduces a pole in original allowed domain')
        verdict,ev=compare(expr,answer,domain);actual=s.simplify(expr)
    elif kind=='solve':
        expr=parse(p['expr']);actual=s.solveset(expr,X,domain=domain)-poles(p['expr'],domain)
        if actual.has(s.ConditionSet):raise Unsupported('Solver returned an unresolved ConditionSet')
        verdict,ev=compare(actual,parse(task['answer']),domain)
    elif kind=='finite_set':
        if not all(type(x) is int for name in ['A','B','U'] for x in p[name]):raise Unsupported('Only explicit integer sets')
        A=s.FiniteSet(*p['A']);B=s.FiniteSet(*p['B']);U=s.FiniteSet(*p['U'])
        if len(A)+len(B)+len(U)>100:raise Unsupported('Set-size bound')
        op=p['operation']
        if op=='union':actual=A|B
        elif op=='intersection':actual=A&B
        elif op=='difference':actual=A-B
        elif op=='complement':
            if A.is_subset(U) is not True:return result('refuted','Subset does not belong to stated universe')
            actual=U-A
        elif op=='symmetric_difference':actual=s.SymmetricDifference(A,B)
        elif op=='cartesian':actual=s.FiniteSet(*(s.Tuple(a,b) for a in A for b in B))
        else:raise Unsupported('Unknown set operation')
        verdict,ev=compare(actual,parse(task['answer']))
    elif kind=='matrix':
        values=[[parse(str(v)) for v in row] for row in p['matrix']];mat=s.Matrix(values)
        if mat.rows>4 or mat.cols>4 or mat.rows!=mat.cols:raise Unsupported('Square matrices of size at most four only')
        if p['operation']=='determinant':actual=mat.det();verdict,ev=compare(actual,parse(task['answer']))
        elif p['operation']=='inverse':
            if mat.det()==0:
                if task['answer'] in ['None','undefined','does not exist']:return result('confirmed','Singular matrix has no inverse')
                return result('refuted','Matrix is singular; proposed inverse cannot exist')
            actual=mat.inv();raw=json.loads(task['answer']);claim=s.Matrix([[parse(str(v)) for v in row] for row in raw])
            verdict=actual==claim;ev='Exact inverse matrix comparison; '+str(mat*claim)
        else:raise Unsupported('Unknown matrix operation')
    elif kind in ['summation','induction']:
        lower=p['lower'];upper=parse(p['upper']);term=parse(p['term'])
        if type(lower) is not int or abs(lower)>100:raise Unsupported('Sum bound')
        actual=s.summation(term,(K,lower,upper))
        if actual.has(s.Sum):raise Unsupported('Symbolic sum remains unevaluated')
        verdict,ev=compare(actual,parse(task['answer']));partial=kind=='induction'
        if partial:ev+='; identity checked, entire induction proof not verified'
    elif kind=='congruence':
        a,b,m=(p[n] for n in ['a','b','modulus'])
        if any(type(v) is not int for v in [a,b,m]) or not 2<=m<=300:raise Unsupported('Bounded integer congruence only')
        actual=s.FiniteSet(*(r for r in range(m) if s.Mod(a*r-b,m)==0));verdict,ev=compare(actual,parse(task['answer']))
    elif kind=='counting':
        actual=s.simplify(parse(p['expression']));verdict,ev=compare(actual,parse(task['answer']));partial=True
        ev+='; arithmetic only, combinatorial model chosen by LLM is not verified against prose'
    elif kind=='inequality':
        lhs,rhs=parse(p['lhs']),parse(p['rhs'])
        allowed=domain-poles(p['lhs'],domain)-poles(p['rhs'],domain)
        if allowed!=domain:return result('refuted','Claimed universal inequality includes undefined points')
        solution=s.reduce_inequalities([lhs<=rhs],X).as_set();truth=domain.is_subset(solution)
        if truth is None:raise Unsupported('Inequality containment undecided')
        actual=s.true if truth else s.false;claim=parse(task['answer']);verdict=bool(claim)==bool(truth) if type(claim) is bool else None;ev='Exact satisfying set: '+str(solution)
    elif kind=='function':
        expr=parse(p['expr']);codomain=parse(p['codomain']);prop=p['property']
        ok,ev=domain_ok(expr,p['expr'],domain)
        if ok is False:return result('refuted','Rule is not defined throughout its stated domain. '+ev)
        if ok is not True:raise Unsupported('Function domain undecided')
        image=function_range(expr,X,domain)
        belongs=image.is_subset(codomain)
        if belongs is None:
            outside=image-codomain
            if outside.is_empty is True:belongs=True
            elif outside.is_empty is False:belongs=False
        if belongs is False:return result('refuted','Rule leaves its stated codomain; image '+str(image),image)
        if belongs is not True:raise Unsupported('Codomain containment undecided')
        onto=image==codomain
        if not onto:
            eq,_=compare(image,codomain)
            if eq is None:raise Unsupported('Surjectivity undecided')
            onto=eq
        inj=None
        num,den=s.fraction(s.cancel(expr))
        try:
            pn,pd=s.Poly(num,X),s.Poly(den,X)
            if pn.degree()<=1 and pd.degree()<=1:
                det=pn.coeff_monomial(X)*pd.coeff_monomial(1)-pn.coeff_monomial(1)*pd.coeff_monomial(X)
                if det!=0:inj=True
        except s.PolynomialError:pass
        # A polynomial with a globally nonnegative, nonzero derivative is strictly
        # increasing on an interval (isolated zeros do not create constant intervals).
        if inj is None and expr.is_polynomial(X) and isinstance(domain,s.Interval):
            derivative=s.diff(expr,X);z=s.Symbol('z',nonnegative=True)
            d=derivative.subs(X,z+domain.start) if domain.start.is_finite and domain.end==s.oo else derivative
            if d!=0 and (d.is_nonnegative is True or (-d).is_nonnegative is True):inj=True
        if inj is None:
            candidates=[s.Integer(i) for i in [-3,-2,-1,0,1,2,3]]
            for a,b in itertools.combinations(candidates,2):
                if domain.contains(a)==s.true and domain.contains(b)==s.true and s.simplify(expr.subs(X,a)-expr.subs(X,b))==0:inj=False;break
        truth=onto if prop=='surjective' else inj if prop=='injective' else (False if inj is False or onto is False else True if inj is True and onto is True else None) if prop=='bijective' else None
        if truth is None:raise Unsupported('Injectivity/property not supported for this function')
        actual=s.true if truth else s.false;claim=parse(task['answer']);verdict=(claim is truth) if type(claim) is bool else None;ev=f'Image={image}; injective={inj}; onto={onto}; rule belongs to codomain'
    else:raise Unsupported('Unknown kind')
    if verdict is False:return result('refuted',ev,actual)
    if verdict is None:return result('unsupported',ev,actual)
    for step in task.get('steps',[]):
        try:
            a,b=parse(step['left']),parse(step['right'])
            ok,reason=compare(a,b,domain)
        except Exception as error:
            partial=True;ev+='; unparsed intermediate step ('+type(error).__name__+'), not validated'
            continue
        if ok is False:return result('refuted','Invalid supplied equality step: '+reason,actual)
        if ok is None:partial=True;ev+='; an equality step could not be established'
    return result('partial' if partial else 'confirmed',ev,actual)
def one(task):
    try:return verify(task)
    except Unsupported as e:return result('unsupported',str(e),scope='none')
    except Exception as e:return result('unsupported',type(e).__name__+': '+str(e)[:220],scope='none')
def main():
    if '--one' in sys.argv:
        print(json.dumps(one(json.load(sys.stdin)),ensure_ascii=False));return
    groups={}
    for group in ['near2','transfer2']:
        raw=json.loads((ROOT/'output'/f'{group}.json').read_text(encoding='utf-8'));items=[]
        for i,task in enumerate(raw['parsed']['items'],1):
            try:
                proc=subprocess.run([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--one'],input=json.dumps(task),capture_output=True,text=True,encoding='utf-8',timeout=8)
                verdict=json.loads(proc.stdout) if proc.returncode==0 else result('unsupported','Checker process failed',scope='none')
            except subprocess.TimeoutExpired:verdict=result('unsupported','Eight-second checker time limit',scope='none')
            items.append({'task':task,'check':verdict});print(group,i,task['kind'],verdict['status'],flush=True)
        groups[group]=items
    (ROOT/'output/checks.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
