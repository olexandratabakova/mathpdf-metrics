"""Fifty bounded families; two numeric/finite variants each, not free-form proofs."""
import importlib.util,itertools,math,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('hundred_base',ROOT.parent/'v5-seventy/engine.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
EXCLUDED={'sets_distribute','int_base','composition_order'}
NEW={
 'logic_table':('logic','Complete truth table','book',60),
 'logic_equivalence':('logic','Logical equivalence','book',62),
 'logic_quantifiers':('logic','Quantifiers on a finite universe','book',65),
 'logic_negation':('logic','Negating a quantified statement','book',73),
 'rel_properties':('relations','Properties of a finite relation','book',217),
 'rel_classes':('relations','Congruence equivalence classes','book',222),
 'rel_between':('relations','Relation between finite sets','book',233),
 'order_extrema':('orders','Extrema under divisibility','notes',52),
 'order_bounds':('orders','Bounds in a divisibility poset','notes',54),
 'order_subsets':('orders','Extrema under inclusion','notes',52),
 'world_parity':('functions','Parity of a polynomial function','notes',71),
 'world_monotonic':('functions','Weak and strict monotonicity','notes',72),
 'world_domain':('functions','Domain of a rational function','notes',73)}
TOPICS={**E.TOPICS,'logic':'Логіка','relations':'Відношення','orders':'Частковий порядок'}
SEED=100731
def templates():return [t for t in E.META if t not in EXCLUDED]+[t for t in E.FUNCTIONS.CATALOG if t not in EXCLUDED]+list(NEW)
def params(t,variant,seed=SEED):
    r=random.Random(seed+100*templates().index(t)+variant)
    if t in E.META:return E.parameters(t,r,variant)
    if t in E.FUNCTIONS.CATALOG:
        old=E.FUNCTIONS.SEED;E.FUNCTIONS.SEED=seed+100*templates().index(t)+variant
        p=E.FUNCTIONS.params()[t];E.FUNCTIONS.SEED=old;return p
    if t in ['logic_table','logic_equivalence']:return {'variant':variant,'label':r.randint(2,30)}
    if t in ['logic_quantifiers','logic_negation']:return {'U':list(range(-r.randint(2,4),r.randint(3,5)+1)),'bound':r.randint(1,5)}
    if t=='rel_properties':return {'S':list(range(r.randint(2,8),r.randint(12,16)))[:4],'mode':variant}
    if t=='rel_classes':return {'start':r.randint(-5,1),'length':r.randint(6,9),'modulus':r.randint(2,4)}
    if t=='rel_between':return {'A':sorted(r.sample(range(1,12),3)),'B':sorted(r.sample(range(2,14),3)),'offset':r.randint(-3,3)}
    if t=='order_extrema':return {'a':r.randint(2,7),'mode':variant}
    if t=='order_bounds':return {'p':r.choice([2,3]),'q':r.choice([5,7])}
    if t=='order_subsets':return {'U':sorted(r.sample(range(1,15),3)),'mode':variant}
    if t=='world_parity':return {'coefficients':[r.randint(1,6),0,r.randint(2,7)] if variant==0 else [0,r.randint(1,6),0,r.randint(2,7)]}
    if t=='world_monotonic':return {'a':r.randint(2,8) if variant==0 else 0,'b':r.randint(-8,8)}
    if t=='world_domain':return {'a':r.randint(2,7),'c':r.randint(2,9)}
    raise ValueError('Unsupported family')
def relation_properties(S,R):
    reflex=next((a for a in S if (a,a) not in R),None)
    sym=next(((a,b) for a,b in R if (b,a) not in R),None)
    anti=next(((a,b) for a,b in R if a!=b and (b,a) in R),None)
    trans=next(((a,b,c) for a,b,c in itertools.product(S,repeat=3) if (a,b) in R and (b,c) in R and (a,c) not in R),None)
    witnesses={'reflexive':reflex,'symmetric':sym,'antisymmetric':anti,'transitive':trans}
    return {k:v is None for k,v in witnesses.items()},witnesses
def extrema(S,le):
    return {'least':[a for a in S if all(le(a,b) for b in S)],'greatest':[a for a in S if all(le(b,a) for b in S)],
      'minimal':[a for a in S if not any(a!=b and le(b,a) for b in S)],'maximal':[a for a in S if not any(a!=b and le(a,b) for b in S)]}
def polynomial(c,minus=False):
    terms=[]
    for i,v in reversed(list(enumerate(c))):
        n=v*((-1)**i if minus else 1)
        if n:terms.append(f'{n:+d}'+('x' if i==1 else rf'x^{{{i}}}' if i>1 else ''))
    return ''.join(terms).lstrip('+') or '0'
def build(t,p):
    if t in E.META:
        if t in EXCLUDED:raise ValueError('Family excluded from this run')
        return E.build(t,p)
    if t in E.FUNCTIONS.CATALOG:
        if t in EXCLUDED:raise ValueError('Family excluded from this run')
        x=E.FUNCTIONS.build(t,p);x['topic']='functions';x['source']={'page':x['source']['page'],'reference':x['source']['reference']};return x
    if t not in NEW:raise ValueError('Unsupported family')
    topic,title,doc,page=NEW[t];checks=[]
    def check(ok,message):
        if not ok:raise ValueError(message)
        checks.append(message)
    def T(text):return {'kind':'text','text':text}
    def M(latex):return {'kind':'math','latex':latex,'display':True,'source':{'page':page,'document':doc}}
    def seqset(values):return E.settex(values)
    def truth(v):return r'\mathrm{T}' if v else r'\mathrm{F}'
    if t in ['logic_table','logic_equivalence']:
        check(type(p['variant']) is int and p['variant'] in [0,1] and type(p['label']) is int,'Closed Boolean variant and integer label')
        variant=p['variant'];rows=list(itertools.product([True,False],repeat=2))
        if t=='logic_table':
            formula=r'(P\land Q)\Rightarrow P' if variant==0 else r'(P\lor Q)\Rightarrow Q'
            evaluate=(lambda a,b:not(a and b) or a) if variant==0 else (lambda a,b:not(a or b) or b)
            values=[evaluate(a,b) for a,b in rows]
            q=[T('Construct a complete truth table for the statement. The statement label is only a name.'),M(rf'F_{{{p["label"]}}}={formula}')]
            ans=[T('Enumerate every assignment of the two Boolean variables; an implication is false only for a true premise and false conclusion.'),M(r'\begin{array}{cc|c}P&Q&F\\'+r'\\'.join('&'.join([truth(a),truth(b),truth(v)]) for (a,b),v in zip(rows,values))+r'\end{array}')]
            check(len(rows)==4 and len(set(rows))==4,'Complete Boolean assignment enumeration')
        else:
            f=(lambda a,b:not a or b) if variant==0 else (lambda a,b:(a or b) and not(a and b))
            g=(lambda a,b:not a or b) if variant==0 else (lambda a,b:a==b)
            left=r'P\Rightarrow Q' if variant==0 else r'(P\lor Q)\land\neg(P\land Q)'
            right=r'\neg P\lor Q' if variant==0 else r'P\Leftrightarrow Q'
            values=[(f(a,b),g(a,b)) for a,b in rows];equivalent=all(a==b for a,b in values)
            q=[T('Decide logical equivalence using all assignments, not a single example.'),M(rf'F_{{{p["label"]}}}={left},\quad G_{{{p["label"]}}}={right}')]
            ans=[M(r'\begin{array}{cc|cc}P&Q&F&G\\'+r'\\'.join('&'.join(map(truth,[a,b,c,d])) for (a,b),(c,d) in zip(rows,values))+r'\end{array}'),T('They are logically equivalent: every row agrees.' if equivalent else 'They are not logically equivalent: the displayed rows give differing truth values.')]
            check(equivalent==(variant==0),'Full truth-table comparison agrees with direct Boolean laws')
    elif t in ['logic_quantifiers','logic_negation']:
        U=p['U'];bound=p['bound'];check(isinstance(U,list) and 1<=len(U)<=15 and all(type(x) is int for x in U) and type(bound) is int,'Bounded explicit integer universe')
        if t=='logic_quantifiers':
            values=[x*x<=bound for x in U];allv=all(values);anyv=any(values)
            q=[T('Determine both truth values over the stated finite universe. Give a witness or counterexample when applicable.'),M(rf'U={seqset(U)},\quad (\forall x\in U:x^2\leq {bound}),\quad(\exists x\in U:x^2\leq {bound})')]
            ans=[T('Evaluate the predicate at every universe element.'),M(r'\begin{array}{c|c}x&x^2\leq '+str(bound)+r'\\'+r'\\'.join(f'{x}&{truth(v)}' for x,v in zip(U,values))+r'\end{array}'),T(f'Universal statement: {allv}. Existential statement: {anyv}.')]
            if not allv:ans.append(M(rf'x={next(x for x in U if x*x>bound)}\quad\text{{is a counterexample}}'))
            if anyv:ans.append(M(rf'x={next(x for x in U if x*x<=bound)}\quad\text{{is a witness}}'))
            check(allv==(not any(x*x>bound for x in U)) and anyv==(len([x for x in U if x*x<=bound])>0),'Exhaustive finite universal/existential duality')
        else:
            original=all(x>=bound for x in U);negative=any(x<bound for x in U)
            q=[T('Negate this statement and determine whether the negation is true on the stated universe.'),M(rf'U={seqset(U)},\qquad \forall x\in U:x\geq {bound}')]
            ans=[T('Negation changes the universal quantifier to an existential and reverses the predicate.'),M(rf'\neg(\forall x\in U:x\geq {bound})\iff\exists x\in U:x<{bound}'),T(f'The negation is {negative}.')]
            if negative:ans.append(M(rf'x={next(x for x in U if x<bound)}<{bound}'))
            check(negative==not_bool(original),'Quantifier negation checked against every finite input')
    elif t=='rel_properties':
        S=p['S'];check(len(S)==4 and len(set(S))==4 and all(type(x) is int for x in S) and p['mode'] in [0,1],'Four distinct integer relation vertices and closed mode')
        a,b,c,d=S
        R=set(itertools.product(S[:3],repeat=2)) if p['mode']==0 else {(x,x) for x in S}|{(a,b),(b,c)}
        props,witnesses=relation_properties(S,R)
        q=[T('Determine whether the relation is reflexive, symmetric, antisymmetric and transitive. Justify failures with explicit witnesses.'),M(rf'S={seqset(S)},\quad R={E.producttex(R)}')]
        ans=[T('Check the diagonal, reverse pairs and every possible composable triple on this finite universe.'),M(r'\begin{array}{c|c}'+r'\\'.join(r'\text{'+name+'}&'+truth(v) for name,v in props.items())+r'\end{array}')]
        for name,w in witnesses.items():
            if w is not None:ans.append(T(f'Failure of {name}: witness {w}. The relation listed above contains the premise pairs but lacks the required diagonal, reverse or resulting pair (or has a distinct mutually related pair for antisymmetry).'))
        if p['mode']==0:ans.append(T('All related inputs lie in the same three-element block; every pair within that block is present, so symmetry and transitivity hold. The fourth vertex lacks its loop.'))
        check(props==({'reflexive':False,'symmetric':True,'antisymmetric':False,'transitive':True} if p['mode']==0 else {'reflexive':True,'symmetric':False,'antisymmetric':True,'transitive':False}),'Complete finite relation property enumeration matches construction certificate')
    elif t=='rel_classes':
        start,length,m=p['start'],p['length'],p['modulus'];check(all(type(x) is int for x in [start,length,m]) and 1<=length<=12 and 2<=m<=6,'Bounded congruence equivalence universe')
        S=list(range(start,start+length));classes=[{x for x in S if x%m==r} for r in range(m)];classes=[C for C in classes if C]
        q=[T('Show this is an equivalence relation and list all distinct classes on the finite stated universe.'),M(rf'S={seqset(S)},\quad a\sim b\iff {m}\mid(a-b)')]
        ans=[T('Reflexivity uses that the difference of an element with itself is zero. Symmetry uses negation of a multiple; transitivity uses addition of multiples. Group the finite universe by equal remainders:'),M(r'\{'+','.join(seqset(C) for C in classes)+r'\}')]
        check(set.union(*classes)==set(S) and sum(map(len,classes))==len(S),'Classes form a disjoint complete partition')
        check(all(((a-b)%m==0)==any(a in C and b in C for C in classes) for a,b in itertools.product(S,repeat=2)),'Every pair agrees with its equivalence class membership')
    elif t=='rel_between':
        A,B,h=p['A'],p['B'],p['offset'];check(len(A)<=5 and len(B)<=5 and A and B and all(type(x) is int for x in A+B+[h]),'Bounded integer relation between two sets')
        R={(a,b) for a,b in itertools.product(A,B) if a<=b+h}
        q=[T('List every ordered pair in the relation and determine its cardinality.'),M(rf'A={seqset(A)},\quad B={seqset(B)},\quad R=\{{(a,b)\in A\times B:a\leq b{h:+d}\}}')]
        ans=[T('Check the defining comparison for every pair in the Cartesian product.'),M(rf'R={E.producttex(R) if R else E.settex([])},\quad |R|={len(R)}')]
        check(len(R)==sum(a<=b+h for a in A for b in B),'Full Cartesian pair predicate enumeration')
    elif t.startswith('order_'):
        if t=='order_subsets':
            U=p['U'];check(len(U)==3 and len(set(U))==3 and all(type(x) is int for x in U) and p['mode'] in [0,1],'Three-element set universe')
            a,b,c=U;S=[frozenset([a]),frozenset([b]),frozenset([a,b]),frozenset([b,c])] if p['mode']==0 else [frozenset(z) for k in range(4) for z in itertools.combinations(U,k)]
            le=lambda a,b:a<=b;fmt=lambda a:seqset(a)
            q=[T('Find all minimal and maximal elements, and decide whether a least or greatest element exists, under inclusion.'),M(r'S=\{'+','.join(fmt(a) for a in S)+r'\},\quad A\preceq B\iff A\subseteq B')]
        else:
            if t=='order_extrema':
                a=p['a'];check(type(a) is int and a>0 and p['mode'] in [0,1],'Positive divisibility-poset scale')
                S=[a,2*a,3*a,(6 if p['mode']==0 else 5)*a]
            else:
                prime,qprime=p['p'],p['q'];check(prime in [2,3] and qprime in [5,7],'Distinct prime construction')
                total=prime*prime*qprime;S=[d for d in range(1,total+1) if total%d==0]
            le=lambda a,b:b%a==0;fmt=str
            q=[T('Find extrema under divisibility, not the usual numerical ordering.') if t=='order_extrema' else T('Find all lower/upper bounds of A in S and determine its infimum and supremum under divisibility.'),M(rf'S={seqset(S)},\quad a\preceq b\iff a\mid b')]
        props,_=relation_properties(S,{(a,b) for a,b in itertools.product(S,repeat=2) if le(a,b)})
        check(props['reflexive'] and props['antisymmetric'] and props['transitive'],'Relation satisfies all partial-order axioms on the complete finite set')
        if t=='order_bounds':
            A=[p['p'],p['q']];lower=[x for x in S if all(le(x,a) for a in A)];upper=[x for x in S if all(le(a,x) for a in A)]
            inf=[x for x in lower if all(le(y,x) for y in lower)];sup=[x for x in upper if all(le(x,y) for y in upper)]
            q.append(M(rf'A={seqset(A)}'))
            ans=[T('Bounds are taken in S. Enumerate the common divisors and common multiples available in that universe.'),M(rf'\text{{lower bounds}}={seqset(lower)},\quad\text{{upper bounds}}={seqset(upper)}'),M(rf'\inf A={inf[0]},\qquad\sup A={sup[0]}')]
            check(inf==[math.gcd(*A)] and sup==[math.lcm(*A)],'Finite order-theoretic definitions agree with independent gcd/lcm')
        else:
            ex=extrema(S,le);ans=[T('Least/greatest must compare with every element; minimal/maximal require no strictly smaller/larger element. Apply these separate definitions to the entire finite poset.')]
            for name,values in ex.items():
                ans.append(T(f'{name}: none exists.') if not values else M(r'\text{'+name+r'}:\quad '+r',\quad '.join(fmt(x) for x in values)))
            check(all(x in ex['minimal'] for x in ex['least']) and all(x in ex['maximal'] for x in ex['greatest']),'Least/greatest are included among minimal/maximal without conflating them')
    elif t=='world_parity':
        c=p['coefficients'];check(isinstance(c,list) and 1<=len(c)<=6 and all(type(x) is int for x in c),'Exact bounded polynomial coefficients')
        even=all(v==0 for i,v in enumerate(c) if i%2);odd=all(v==0 for i,v in enumerate(c) if i%2==0)
        q=[T('Decide whether this function is even, odd, both, or neither. Include the domain condition.'),M(rf'f:\mathbb R\to\mathbb R,\quad f(x)={polynomial(c)}')]
        ans=[T('The real domain is symmetric about zero. Substitute the negative input and compare coefficients:'),M(rf'f(-x)={polynomial(c,True)}'),T(f'Even: {even}. Odd: {odd}.')]
        check(even==all(v*((-1)**i)==v for i,v in enumerate(c)) and odd==all(v*((-1)**i)==-v for i,v in enumerate(c)),'Exact coefficient identities f(-x)=f(x) and f(-x)=-f(x)')
    elif t=='world_monotonic':
        a,b=p['a'],p['b'];check(type(a) is int and type(b) is int,'Exact affine coefficients')
        q=[T('Classify increasing/decreasing in the non-strict sense and strictly increasing/decreasing separately.'),M(rf'f:\mathbb R\to\mathbb R,\quad f(x)={a}x{b:+d}')]
        ans=[T('For any two inputs in increasing order, use the sign of their output difference.'),M(rf'x_1<x_2\implies f(x_2)-f(x_1)={a}(x_2-x_1)'),T(f'Nondecreasing: {a>=0}. Strictly increasing: {a>0}. Nonincreasing: {a<=0}. Strictly decreasing: {a<0}.'),T('If the slope is zero, the function is constant, both nondecreasing and nonincreasing, but neither strict property holds.')]
        check((a==0 and not a>0 and not a<0) or a!=0,'Strictness and zero-slope boundary are kept distinct')
    else:
        a,c=p['a'],p['c'];check(type(a) is int and type(c) is int and a>0 and c>0,'Positive exact rational-rule parameters')
        q=[T('Find the largest real domain of this rational rule.'),M(rf'f(x)=\frac{{x^3+{c}x}}{{x^2-{a*a}}}')]
        ans=[T('A rational rule excludes every zero of its original denominator. Factor it to find all such points.'),M(rf'x^2-{a*a}=(x-{a})(x+{a})=0\iff x\in\{{-{a},{a}\}}'),M(rf'D=\mathbb R\setminus\{{-{a},{a}\}}')]
        check(a*a-a*a==0 and (-a)**2-a*a==0 and a*(a*a+c)!=0,'Exact denominator factorization and no canceled numerator roots')
    return {'template_id':t,'topic':topic,'title':title,'parameters':p,'source':{'document':doc,'page':page},'question':q,'answer':ans,'checks':checks,'status':'verified_for_supported_template'}
def not_bool(value):return not value
def verify(item):
    expected=build(item['template_id'],item['parameters'])
    if item!=expected:raise ValueError('Mathematical artifact changed after construction')
    return True
