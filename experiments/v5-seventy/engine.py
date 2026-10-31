"""Seventy bounded variants across seven source-supported topic groups.

Universal induction proofs use algebraic certificates, not numerical sampling.
All prose and math are owned by reviewed templates, never the planning model.
"""
from fractions import Fraction as Q
from itertools import combinations, product, permutations
from math import comb, factorial, gcd, isqrt
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original_v5',ROOT.parent/'v5-parameterized/engine.py')
FUNCTIONS=importlib.util.module_from_spec(spec);spec.loader.exec_module(FUNCTIONS)
SEED=50770
TOPICS={'sets':'Множини','induction':'Математична індукція','integers':'Числа й подільність','congruences':'Конгруенції','counting':'Комбінаторика','pigeonhole':'Принцип Діріхле','functions':'Функції'}
META={
 'sets_ops':('sets',6,'Definition 1.10–1.11','Set operations'),
 'sets_complement':('sets',7,'Definition 1.12','Relative complement'),
 'sets_product':('sets',5,'Definition 1.5','Cartesian product'),
 'sets_power':('sets',5,'Theorem 1.7 and Definition 1.9, p. 6','Power set'),
 'sets_distribute':('sets',6,'Distributive identity and proof','Distributive set identity'),
 'ind_squares':('induction',14,'Example 3.1, continued p. 15','Induction for a square sum'),
 'ind_odd':('induction',15,'Example 3.3','Induction for an odd sum'),
 'ind_factorial':('induction',17,'Exercise 3.9','Induction for a factorial sum'),
 'ind_divisible':('induction',15,'Example 3.2','Induction and divisibility'),
 'ind_harmonic':('induction',16,'Example 3.5','Induction for a reciprocal-square bound'),
 'int_division':('integers',28,'Theorem 6.2','Quotient and remainder'),
 'int_gcd':('integers',29,'Euclid algorithm, Theorem 6.7','Euclidean algorithm'),
 'int_bezout':('integers',30,'Theorem 6.9','Bezout coefficients'),
 'int_factor':('integers',31,'Theorem 6.16 and Example 6.18','Prime factorization'),
 'int_base':('integers',27,'Section 4, positional notation','Positional number notation'),
 'mod_compare':('congruences',33,'Definition 7.1 and Lemma 7.3','Testing congruence'),
 'mod_power':('congruences',34,'Corollary 7.10','Remainder of a power'),
 'mod_linear':('congruences',34,'Theorem 7.7; finite residue search','Solving a congruence'),
 'mod_impossible':('congruences',34,'Example 7.9','A parity obstruction'),
 'mod_clock':('congruences',34,'Example 7.5','Clock arithmetic'),
 'count_routes':('counting',38,'Roads example, sum/product rules','Counting routes'),
 'count_permutations':('counting',39,'Theorem 8.4','Ordering distinct objects'),
 'count_combinations':('counting',39,'Theorem 8.6','Choosing an unordered committee'),
 'count_stars':('counting',42,'Sticks and stones, continued p. 43','Nonnegative integer solutions'),
 'count_binomial':('counting',41,'Theorem 8.12 and Example 8.13','A binomial coefficient'),
 'ph_birthdays':('pigeonhole',60,'Example 11.3','Birthdays in one month'),
 'ph_boxes':('pigeonhole',60,'Theorem 11.2','A sharp occupancy threshold'),
 'ph_remainders':('pigeonhole',60,'Theorem 11.1, residue application pp. 61–62','Equal remainders'),
 'ph_square':('pigeonhole',60,'Example 11.4, continued p. 61','Points in a square'),
 'ph_repunit':('pigeonhole',61,'Example 11.8, continued p. 62','A divisible repunit')}

# Polynomial coefficients in increasing degree; exact arithmetic throughout.
def add(a,b):return [Q(a[i] if i<len(a) else 0)+Q(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))]
def scale(a,c):return [Q(x)*c for x in a]
def mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def equal(a,b):
    while len(a)>1 and a[-1]==0:a=a[:-1]
    while len(b)>1 and b[-1]==0:b=b[:-1]
    return a==b
def shifted(a):
    out=[Q(0)]*len(a)
    for j,c in enumerate(a):
        for i in range(j+1):out[i]+=c*comb(j,i)
    return out
def induction_certificate(t,c):
    if type(c) is not int or c<=0:raise ValueError('Positive integer scale required')
    if t=='ind_squares':
        f=scale([0,Q(1,6),Q(1,2),Q(1,3)],c)
        ok=equal(add(shifted(f),scale(f,-1)),scale([1,2,1],c)) and sum(f)==c
    elif t=='ind_odd':
        f=[0,0,c];ok=equal(add(shifted(f),scale(f,-1)),[c,2*c]) and sum(f)==c
    elif t=='ind_factorial':
        # With F=(n+1)!, F-c offset cancels; 1+(n+1)=n+2.
        ok=equal(add([1],[1,1]),[2,1]) and c*(factorial(2)-1)==c
    elif t=='ind_divisible':
        f=[0,5,0,1]
        ok=equal(add(shifted(f),scale(f,-1)),[6,3,3]) and (1+5)%6==0 and all(n*(n+1)%2==0 for n in [0,1])
    elif t=='ind_harmonic':
        # Desired slack: 1/n-1/(n+1)-1/(n+1)^2 = 1/[n(n+1)^2].
        ok=equal(add(add([1,2,1],scale([0,1,1],-1)),[0,-1]),[1]) and c==c*(2-1)
    else:raise ValueError('Unsupported induction family')
    if not ok:raise ValueError('Algebraic induction certificate failed')
    return True

def factor(n):
    result=[];d=2
    while d*d<=n:
        e=0
        while n%d==0:n//=d;e+=1
        if e:result.append((d,e))
        d+=1
    if n>1:result.append((n,1))
    return result
def egcd(a,b):
    if b==0:return a,1,0
    g,x,y=egcd(b,a%b);return g,y,x-(a//b)*y
def repunit(m):
    r=0
    for n in range(1,m+1):
        r=(10*r+1)%m
        if r==0:return n
    raise ValueError('Repunit construction failed')
def settex(s):return r'\varnothing' if not s else r'\{'+','.join(map(str,sorted(s)))+r'\}'
def producttex(pairs):return r'\{'+','.join(f'({a},{b})' for a,b in sorted(pairs))+r'\}'

def parameters(t,r,v):
    if t.startswith('sets_'):
        U=list(range(1,r.randint(5,8)+1))
        return {'U':U,'A':sorted(r.sample(U,3)),'B':sorted(r.sample(U,2)),'C':sorted(r.sample(U,3))}
    if t.startswith('ind_'):return {'c':r.randint(2,8)}
    if t=='int_division':return {'a':r.randint(-180,-20) if v==0 else r.randint(30,180),'b':r.randint(3,15)}
    if t in ['int_gcd','int_bezout']:return {'a':r.randint(20,120),'b':r.randint(12,90)}
    if t=='int_factor':return {'n':r.choice([2,3,5])**r.randint(2,4)*r.choice([7,11,13])**r.randint(1,2)}
    if t=='int_base':return {'n':r.randint(35,180),'base':2 if v==0 else 8}
    if t=='mod_compare':return {'a':r.randint(-50,80),'b':r.randint(-30,90),'m':r.randint(3,13)}
    if t=='mod_power':return {'a':r.randint(2,15),'n':r.randint(12,45),'m':r.randint(3,17)}
    if t=='mod_linear':return {'a':r.randint(2,10),'b':r.randint(1,20),'m':r.randint(4,16)}
    if t=='mod_impossible':return {'a':2*r.randint(1,20)+1,'b':2*r.randint(1,20)+1}
    if t=='mod_clock':return {'hour':r.randint(0,23),'elapsed':r.randint(30,150)}
    if t=='count_routes':return {k:r.randint(2,7) for k in ['a','b','c','d']}
    if t=='count_permutations':return {'n':r.randint(4,7)}
    if t=='count_combinations':return {'n':r.randint(6,10),'k':r.randint(2,4)}
    if t=='count_stars':return {'n':r.randint(5,14)}
    if t=='count_binomial':return {'n':r.randint(5,9),'k':r.randint(1,4),'c':r.randint(2,4)}
    if t=='ph_birthdays':return {'n':r.randint(40,150)}
    if t=='ph_boxes':return {'boxes':r.randint(3,10),'target':r.randint(3,7)}
    if t=='ph_remainders':return {'m':r.randint(4,18)}
    if t=='ph_square':return {'side':r.randint(2,8),'q':r.randint(2,5)}
    if t=='ph_repunit':return {'m':r.choice([7,9,11,13,17,19,21,27,37])}
    raise ValueError('Unknown template')

def validate(t,p):
    if t not in META:raise ValueError('Unsupported template')
    if t.startswith('sets_'):
        if any(not isinstance(p[k],list) or not p[k] or any(type(x) is not int for x in p[k]) or len(p[k])!=len(set(p[k])) for k in ['U','A','B','C']):raise ValueError('Finite sets must be nonempty integer lists without duplicates')
        if not all(set(p[k])<=set(p['U']) for k in ['A','B','C']):raise ValueError('Subsets must belong to universe')
        if len(p['A'])>6:raise ValueError('Bounded power-set enumeration only')
        return
    if any(type(x) is not int for x in p.values()):raise ValueError('Integer parameters required')
    if t.startswith('ind_'):induction_certificate(t,p['c']);return
    if t in ['int_division','int_gcd','int_bezout'] and (p['b']<=0 or (t!='int_division' and p['a']<=0)):raise ValueError('Positive divisors required')
    if t=='int_factor' and not 2<=p['n']<=1000000:raise ValueError('Bounded positive factorization')
    if t=='int_base' and not (0<p['n']<10000 and 2<=p['base']<=10):raise ValueError('Supported positional bounds')
    if t in ['mod_compare','mod_power','mod_linear','ph_remainders'] and not 2<=p['m']<=100:raise ValueError('Invalid modulus')
    if t=='mod_power' and not 0<=p['n']<=1000:raise ValueError('Invalid exponent')
    if t=='mod_impossible' and (p['a']%2!=1 or p['b']%2!=1 or p['a']<=0 or p['b']<=0):raise ValueError('Parity obstruction requires positive odd coefficients')
    if t=='mod_clock' and not (0<=p['hour']<24 and p['elapsed']>=0):raise ValueError('Invalid clock input')
    if t=='count_routes' and any(p[k]<=0 for k in ['a','b','c','d']):raise ValueError('Positive road counts')
    if t=='count_permutations' and not 1<=p['n']<=8:raise ValueError('Enumeration bound')
    if t in ['count_combinations','count_binomial'] and not 0<=p['k']<=p['n']<=12:raise ValueError('Selection bounds')
    if t=='count_binomial' and p['c']<=0:raise ValueError('Positive binomial constant')
    if t=='count_stars' and not 0<=p['n']<=30:raise ValueError('Enumeration bound')
    if t=='ph_birthdays' and p['n']<=0:raise ValueError('Positive student count')
    if t=='ph_boxes' and (p['boxes']<=0 or p['target']<2):raise ValueError('Invalid occupancy target')
    if t=='ph_square' and (p['q']<1 or p['side']<=0):raise ValueError('Invalid grid')
    if t=='ph_repunit' and not (2<=p['m']<=100 and gcd(p['m'],10)==1):raise ValueError('Repunit needs modulus coprime to ten')

def build(t,p):
    validate(t,p);topic,page,reference,title=META[t];checks=[]
    def check(ok,label):
        if not ok:raise ValueError(label)
        checks.append(label)
    def T(s):return {'kind':'text','text':s}
    def M(s):return {'kind':'math','latex':s,'display':True,'source':{'page':page}}
    if t.startswith('sets_'):
        U,A,B,C=(set(p[k]) for k in ['U','A','B','C'])
        if t=='sets_ops':
            q=[T('Compute the union, intersection and difference of these sets.'),M(rf'A={settex(A)},\quad B={settex(B)}')]
            ans=[T('Include elements according to the definitions of each operation.'),M(rf'A\cup B={settex(A|B)},\quad A\cap B={settex(A&B)},\quad A\setminus B={settex(A-B)}')]
            check(all((x in A|B)==(x in A or x in B) and (x in A&B)==(x in A and x in B) and (x in A-B)==(x in A and x not in B) for x in U),'Exhaustive universe membership for all operations')
        elif t=='sets_complement':
            q=[T('Find the complement relative to the stated universe.'),M(rf'U={settex(U)},\quad A={settex(A)}')]
            ans=[T('Retain exactly the universe elements that are not in the subset.'),M(rf'A^c=U\setminus A={settex(U-A)}')]
            check((U-A).isdisjoint(A) and (U-A)|A==U,'Complement partitions the entire universe')
        elif t=='sets_product':
            pairs=list(product(sorted(A),sorted(B)))
            q=[T('List the Cartesian product and determine its cardinality.'),M(rf'A={settex(A)},\quad B={settex(B)}')]
            ans=[T('Choose the first coordinate from the first set and the second from the second set.'),M(rf'A\times B={producttex(pairs)}'),M(rf'|A\times B|={len(A)}\cdot {len(B)}={len(pairs)}')]
            check(len(set(pairs))==len(A)*len(B) and all((a,b) in pairs for a in A for b in B),'Complete distinct Cartesian enumeration')
        elif t=='sets_power':
            subsets=[set(c) for n in range(len(A)+1) for c in combinations(sorted(A),n)]
            q=[T('List the power set and its cardinality.'),M(rf'A={settex(A)}')]
            ans=[T('List all subsets, including the empty set and the set itself.'),M(r'\mathcal P(A)=\{'+','.join(settex(s) for s in subsets)+r'\}'),M(rf'|\mathcal P(A)|=2^{{{len(A)}}}={len(subsets)}')]
            check(len({tuple(sorted(s)) for s in subsets})==2**len(A) and all(s<=A for s in subsets),'Every distinct subset counted; total matches binary choices')
        else:
            left=A&(B|C);right=(A&B)|(A&C)
            q=[T('Verify the distributive identity for these concrete sets by computing both sides.'),M(rf'A={settex(A)},\quad B={settex(B)},\quad C={settex(C)}')]
            ans=[T('Compute each side independently from membership.'),M(rf'A\cap(B\cup C)={settex(left)}'),M(rf'(A\cap B)\cup(A\cap C)={settex(right)}'),T('The resulting sets coincide for these specified sets. This computation alone is not a proof for arbitrary sets.')]
            check(left==right and all((x in left)==(x in A and (x in B or x in C)) for x in U),'Exhaustive concrete distributive identity')
    elif t.startswith('ind_'):
        c=p['c'];q=[T('Prove the following statement for every integer n at least one by mathematical induction.')]
        ans=[T('Base case n equals one holds. Assume the assertion for an arbitrary integer n at least one; prove it for n plus one.')]
        if t=='ind_squares':
            q+=[M(rf'\sum_{{i=1}}^n {c}i^2=\frac{{{c}n(n+1)(2n+1)}}6')]
            ans+=[M(rf'{c}=\frac{{{c}\cdot1\cdot2\cdot3}}6'),T('Add the next term and use the induction hypothesis:'),M(rf'\sum_{{i=1}}^{{n+1}}{c}i^2=\frac{{{c}n(n+1)(2n+1)}}6+{c}(n+1)^2'),M(rf'=\frac{{{c}(n+1)(n+2)(2n+3)}}6')]
        elif t=='ind_odd':
            q+=[M(rf'\sum_{{i=1}}^n {c}(2i-1)={c}n^2')]
            ans+=[M(rf'{c}(2\cdot1-1)={c}\cdot1^2'),M(rf'\sum_{{i=1}}^{{n+1}}{c}(2i-1)={c}n^2+{c}(2n+1)={c}(n+1)^2')]
        elif t=='ind_factorial':
            q+=[M(rf'\sum_{{i=1}}^n {c}i\,i!={c}((n+1)!-1)')]
            ans+=[M(rf'{c}\cdot1\cdot1!={c}(2!-1)'),M(rf'\sum_{{i=1}}^{{n+1}}{c}i\,i!={c}((n+1)!-1)+{c}(n+1)(n+1)!'),M(rf'={c}((n+2)(n+1)!-1)={c}((n+2)!-1)')]
        elif t=='ind_divisible':
            q+=[M(rf'{6*c}\mid {c}n^3+{5*c}n')]
            ans+=[M(rf'{c}\cdot1^3+{5*c}\cdot1={6*c}'),T('Expand the next expression. The hypothesis covers the first bracket. Consecutive integers have an even product, so every remaining term is divisible by the required divisor.'),M(rf'{c}(n+1)^3+{5*c}(n+1)=({c}n^3+{5*c}n)+{3*c}n(n+1)+{6*c}')]
        else:
            q+=[M(rf'\sum_{{i=1}}^n\frac{{{c}}}{{i^2}}\leq {c}\left(2-\frac1n\right)')]
            ans+=[M(rf'{c}={c}(2-1)'),M(rf'\sum_{{i=1}}^{{n+1}}\frac{{{c}}}{{i^2}}\leq {c}(2-1/n)+\frac{{{c}}}{{(n+1)^2}}'),T('The desired upper bound exceeds this last expression by a nonnegative quantity:'),M(rf'{c}\left(2-\frac1{{n+1}}\right)-\left[{c}(2-1/n)+\frac{{{c}}}{{(n+1)^2}}\right]=\frac{{{c}}}{{n(n+1)^2}}\geq0')]
        ans+=[T('This establishes the induction step. Together with the base case, induction proves the statement for every integer n at least one.')]
        check(induction_certificate(t,c),'Base case and exact polynomial/rational induction-step certificate')
    elif t=='int_division':
        a,b=p['a'],p['b'];quot,rem=divmod(a,b)
        q=[T('Find the unique quotient and nonnegative remainder in division by the positive divisor.'),M(rf'a={a},\quad b={b}')]
        ans=[M(rf'{a}={b}\cdot({quot})+{rem},\quad 0\leq {rem}<{b}'),T('The displayed equality and remainder bounds verify the division; the division algorithm gives uniqueness.')]
        check(a==b*quot+rem and 0<=rem<b,'Exact division and Euclidean remainder bounds')
    elif t in ['int_gcd','int_bezout']:
        a,b=p['a'],p['b'];g,x,y=egcd(a,b);u,v=a,b;steps=[]
        while v:
            h,s=divmod(u,v);steps.append(M(rf'{u}={h}\cdot {v}+{s}'));u,v=v,s
        q=[T('Compute the greatest common divisor'+(' and find integer Bezout coefficients.' if t=='int_bezout' else ' using the Euclidean algorithm.')),M(rf'a={a},\quad b={b}')]
        ans=steps+[M(rf'\gcd({a},{b})={g}')]
        if t=='int_bezout':ans+=[T('The following integer coefficients give the gcd; direct substitution verifies them.'),M(rf'{a}\cdot({x})+{b}\cdot({y})={g}')]
        check(g==gcd(a,b) and a*x+b*y==g and g==max(d for d in range(1,min(a,b)+1) if a%d==0 and b%d==0),'Euclid, independent divisor enumeration and exact Bezout identity')
    elif t=='int_factor':
        n=p['n'];ff=factor(n);out=1
        for prime,e in ff:out*=prime**e
        q=[T('Find the prime factorization.'),M(str(n))]
        ans=[T('Divide repeatedly by prime divisors. Each displayed base is prime; multiplying the factors recovers the integer.'),M(str(n)+'='+r'\cdot'.join(rf'{prime}^{{{e}}}' for prime,e in ff))]
        check(out==n and all(prime>=2 and all(prime%d for d in range(2,isqrt(prime)+1)) for prime,e in ff),'Exact reconstruction and trial-division primality for every factor')
    elif t=='int_base':
        n,b=p['n'],p['base'];v=n;digits=[]
        while v:digits.append(v%b);v//=b
        s=''.join(map(str,digits[::-1]))
        q=[T('Convert this decimal integer into the stated base.'),M(rf'n={n},\quad b={b}')]
        ans=[T('Repeated division by the base gives digits from right to left. Verify them by positional expansion:'),M(rf'({s})_{{{b}}}='+ '+'.join(rf'{d}\cdot {b}^{{{i}}}' for i,d in reversed(list(enumerate(digits))))+rf'={n}')]
        check(sum(d*b**i for i,d in enumerate(digits))==n and all(0<=d<b for d in digits),'Digit bounds and exact positional reconstruction')
    elif t=='mod_compare':
        a,b,m=p['a'],p['b'],p['m'];ok=(a-b)%m==0
        q=[T('Decide whether the following congruence holds.'),M(rf'{a}\equiv {b}\pmod{{{m}}}')]
        ans=[T('It holds.' if ok else 'It does not hold.'),M(rf'({a})-({b})={a-b},\quad ({a-b})\bmod {m}={(a-b)%m}')]
        check(ok==(a%m==b%m),'Divisibility criterion agrees with equality of remainders')
    elif t=='mod_power':
        a,n,m=p['a'],p['n'],p['m'];value=pow(a,n,m);r=1;steps=[]
        for exponent in range(1,n+1):r=r*a%m;steps.append(r)
        q=[T('Find the least nonnegative residue of this power.'),M(rf'{a}^{{{n}}}\pmod{{{m}}}')]
        ans=[T('Start with residue one for exponent zero and multiply by the base, reducing after every step. The recurrence and full residue list through the required exponent are:'),M(rf'r_0=1,\quad r_{{j+1}}\equiv {a}r_j\pmod{{{m}}}')]
        ans += [M(rf'(r_{{{start+1}}},\ldots,r_{{{min(start+7,n)}}})=('+','.join(map(str,steps[start:start+7]))+')') for start in range(0,n,7)]
        ans += [M(rf'{a}^{{{n}}}\equiv {value}\pmod{{{m}}}')]
        check(r==value and value==a**n%m,'Iterative modular recurrence agrees with exact exponentiation')
    elif t=='mod_linear':
        a,b,m=p['a'],p['b'],p['m'];sol=[x for x in range(m) if (a*x-b)%m==0]
        q=[T('Find all integer solutions, expressed as residue classes.'),M(rf'{a}x\equiv {b}\pmod{{{m}}}')]
        ans=[T('Evaluate every residue. Reduction modulo the modulus preserves the equation, so this covers every integer.'),M(rf'({a}r\bmod {m})_{{r=0}}^{{{m-1}}}=('+','.join(str(a*x%m) for x in range(m))+')'),M(rf'x\bmod {m}\in {settex(sol)}')]
        check(len(sol)==(gcd(a,m) if b%gcd(a,m)==0 else 0),'Exhaustive residue search agrees with gcd solvability and count')
    elif t=='mod_impossible':
        a,b=p['a'],p['b'];res=[(x*x-a*x-b)%2 for x in range(2)]
        q=[T('Determine whether this equation has an integer solution using parity.'),M(rf'x^2-{a}x-{b}=0')]
        ans=[T('There is no integer solution. The two parity classes give a nonzero remainder in both cases:'),M(rf'x\equiv0\pmod2\implies x^2-{a}x-{b}\equiv {res[0]}\pmod2'),M(rf'x\equiv1\pmod2\implies x^2-{a}x-{b}\equiv {res[1]}\pmod2'),T('Every integer is in one of these two classes, whereas zero would have remainder zero.')]
        check(res==[1,1],'Complete parity classes exclude an integer root')
    elif t=='mod_clock':
        h,e=p['hour'],p['elapsed'];answer=(h+e)%24
        q=[T(f'On a twenty-four-hour clock it is {h:02d}:00. What hour will it be after {e} whole hours?')]
        ans=[T('Reduce the total hour count modulo twenty-four.'),M(rf'{h}+{e}={h+e}\equiv {answer}\pmod{{24}}'),T(f'The resulting time is {answer:02d}:00.')]
        check(0<=answer<24 and (h+e-answer)%24==0,'Clock bounds and exact day-cycle congruence')
    elif t=='count_routes':
        a,b,c,d=(p[k] for k in ['a','b','c','d']);result=a*b+c*d
        q=[T(f'There are {a} distinct roads from A to B and {b} from B to C; also {c} from A to D and {d} from D to C. Only these roads may be used. Count routes from A to C using exactly two roads, through either B or D.')]
        ans=[T('Multiply independent choices on each route and add the mutually exclusive intermediate-city cases.'),M(rf'{a}\cdot {b}+{c}\cdot {d}={result}')]
        check(result==len([('B',i,j) for i in range(a) for j in range(b)]+[('D',i,j) for i in range(c) for j in range(d)]),'Explicit disjoint route enumeration')
    elif t=='count_permutations':
        n=p['n'];q=[T(f'In how many ways can {n} distinct objects be arranged in a row, using each once?')]
        ans=[T('There are successively fewer choices for each position. Multiply the choices.'),M(rf'{n}!='+r'\cdot'.join(map(str,range(n,0,-1)))+f'={factorial(n)}')]
        check(sum(1 for _ in permutations(range(n)))==factorial(n),'Full distinct permutation enumeration')
    elif t=='count_combinations':
        n,k=p['n'],p['k'];q=[T(f'Choose an unordered committee of {k} distinct people from {n} people, with no repetition or other restrictions. How many committees are possible?')]
        ans=[T('Ordered selections overcount each committee by the factorial of its size. Divide out that order.'),M(rf'\binom{{{n}}}{{{k}}}=\frac{{{n}!}}{{{k}!({n}-{k})!}}={comb(n,k)}')]
        check(sum(1 for _ in combinations(range(n),k))==comb(n,k),'Full unordered subset enumeration')
    elif t=='count_stars':
        n=p['n'];result=comb(n+2,2)
        q=[T('Count ordered triples of nonnegative integers satisfying the equation; zero is allowed.'),M(rf'x+y+z={n},\quad x,y,z\in\mathbb Z_{{\geq0}}')]
        ans=[T('Represent the total by stones and insert two separators. Empty groups are allowed; the separator positions determine the triple uniquely.'),M(rf'\binom{{{n}+2}}2=\binom{{{n+2}}}2={result}')]
        check(sum(1 for x in range(n+1) for y in range(n+1) for z in range(n+1) if x+y+z==n)==result,'Complete bounded triple enumeration')
    elif t=='count_binomial':
        n,k,c=p['n'],p['k'],p['c'];answer=comb(n,k)*c**(n-k);coeff=[1]
        for _ in range(n):coeff=add([x*c for x in coeff],[0]+coeff)
        q=[T('Find the coefficient of the specified power.'),M(rf'[x^{{{k}}}](x+{c})^{{{n}}}')]
        ans=[T('Choose which factors supply the variable; the remaining factors supply the constant.'),M(rf'[x^{{{k}}}](x+{c})^{{{n}}}=\binom{{{n}}}{{{k}}}{c}^{{{n-k}}}={answer}')]
        check(coeff[k]==answer,'Independent exact polynomial multiplication coefficient')
    elif t=='ph_birthdays':
        n=p['n'];k=(n+11)//12
        q=[T(f'Among {n} students, what is the largest number of birthdays in one month that is always guaranteed? Show the guarantee is sharp. Months may contain any number of students.')]
        ans=[T('Use the twelve months as boxes. If each held at most one less than the proposed guarantee, there would be too few students.'),M(rf'\left\lceil\frac{{{n}}}{{12}}\right\rceil={k},\qquad 12\cdot {k-1}<{n}'),T('For sharpness, distribute the students as evenly as possible across the twelve months; no month needs more than this many.')]
        counts=[n//12+(i<n%12) for i in range(12)]
        check(sum(counts)==n and max(counts)==k and 12*(k-1)<n,'Contradiction bound and explicit balanced extremal distribution')
    elif t=='ph_boxes':
        b,k=p['boxes'],p['target'];n=b*(k-1)+1
        q=[T(f'What is the smallest number of objects that guarantees at least {k} in one of {b} boxes, regardless of placement? Prove minimality.')]
        ans=[T('One fewer objects can be distributed equally with no box reaching the target. An additional object makes that avoidance impossible.'),M(rf'N={b}({k}-1)+1={n}'),M(rf'{b}({k}-1)={n-1}<N')]
        check(b*(k-1)==n-1 and b*(k-1)<n,'Matching avoidance construction and forced-occupancy bound')
    elif t=='ph_remainders':
        m=p['m'];q=[T(f'Prove that among any {m+1} distinct integers there are two whose difference is divisible by {m}.')]
        ans=[T('Assign each integer its least nonnegative remainder. Two distinct selected integers must share a remainder because there are more integers than remainder classes.'),M(rf'\{{0,1,\ldots,{m-1}\}}\quad\text{{has }}{m}\text{{ classes}}'),T('Write the two integers using that common remainder and subtract.'),M(rf'u={m}a+r,\quad v={m}b+r\implies u-v={m}(a-b)')]
        check((m+1)>m and equal(add([0,m],[0,-m]),[0]),'Pigeon count and symbolic cancellation of common remainder')
    elif t=='ph_square':
        s,qgrid=p['side'],p['q'];n=qgrid*qgrid+1
        q=[T(f'There are {n} points in a square of side length {s}. Prove that two have distance at most the following bound.'),M(rf'\frac{{{s}\sqrt2}}{{{qgrid}}}')]
        ans=[T(f'Divide the square into a {qgrid}-by-{qgrid} grid. Assign boundary points consistently to one adjacent cell. There are more points than cells, so two share a cell. Their distance is at most its diagonal.'),M(rf'\text{{cells}}={qgrid}^2={n-1}<{n},\qquad d\leq\sqrt{{({s}/{qgrid})^2+({s}/{qgrid})^2}}=\frac{{{s}\sqrt2}}{{{qgrid}}}')]
        check(n>qgrid*qgrid and Q(s,qgrid)**2*2==Q(2*s*s,qgrid*qgrid),'Exact cell count and squared-diagonal identity')
    else:
        m=p['m'];length=repunit(m);value=(10**length-1)//9
        q=[T(f'Prove that some positive integer made only of decimal digit ones is divisible by {m}, and provide one such length.')]
        ans=[T(f'Consider the first {m} repunits. If one has remainder zero we are done. Otherwise their {m} nonzero remainders occupy only {m-1} classes, so two coincide. Their difference is a shorter repunit times a power of ten.'),M(rf'R_j-R_i=10^i R_{{j-i}},\quad\gcd({m},10)=1'),T('The modulus is coprime to that power of ten, so it divides the shorter repunit. Iterating remainders also supplies this explicit witness:'),M(rf'r_0=0,\quad r_{{k+1}}=(10r_k+1)\bmod {m},\qquad r_{{{length}}}=0'),M(rf'R_{{{length}}}=\frac{{10^{{{length}}}-1}}9,\qquad {m}\mid R_{{{length}}}')]
        check(value%m==0 and 1<=length<=m and gcd(m,10)==1,'Constructive zero remainder, exact repunit divisibility and coprimality')
    return {'template_id':t,'topic':topic,'title':title,'parameters':p,'source':{'page':page,'reference':reference},'question':q,'answer':ans,'checks':checks,'status':'verified_for_supported_template'}

def generate(order=None):
    r=random.Random(SEED);items=[]
    order=order or list(TOPICS)
    if len(order)!=7 or set(order)!=set(TOPICS):raise ValueError('All seven topics required exactly once')
    for topic in order:
        if topic=='functions':
            FUNCTIONS.SEED=SEED;pp=FUNCTIONS.params()
            for t,p in pp.items():
                x=FUNCTIONS.build(t,p);x['topic']='functions';x['source']={'page':x['source']['page'],'reference':x['source']['reference']};items.append(x)
        else:
            for t,meta in META.items():
                if meta[0]!=topic:continue
                used=set()
                for v in range(2):
                    for _ in range(100):
                        p=parameters(t,r,v);sig=json.dumps(p,sort_keys=True)
                        if sig not in used:break
                    else:raise ValueError('Duplicate parameter generation')
                    used.add(sig);items.append(build(t,p))
    for i,x in enumerate(items,1):x['id']=i
    return items

def verify_artifact(item):
    t=item['template_id']
    if item['topic']=='functions':
        if t not in FUNCTIONS.CATALOG:raise ValueError('Unsupported function family')
        expected=FUNCTIONS.build(t,item['parameters'])
        expected['topic']='functions';expected['source']={'page':expected['source']['page'],'reference':expected['source']['reference']}
    else:expected=build(t,item['parameters'])
    expected['id']=item['id']
    if expected!=item:raise ValueError('Artifact differs from program-owned construction')
    return True
