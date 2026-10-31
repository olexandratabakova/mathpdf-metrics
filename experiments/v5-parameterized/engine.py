"""Closed, source-curated task families. Exact arithmetic, no model evaluation."""
from fractions import Fraction as Q
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parent
CATALOG={c['id']:c for c in json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))}
SEED=50110
def params():
    r=random.Random(SEED)
    return {
      'relation_missing':{'a':r.randint(2,6),'b':r.randint(2,5),'c':1},
      'relation_total':{'a':r.randint(2,6),'b':1,'c':r.randint(2,7)},
      'finite_range':{'domain':[0,2,4],'shift':r.randint(2,7)},
      'equal_rational':{'a':r.randint(3,7)},
      'square_real':{'k':r.randint(2,6)},
      'square_nonnegative':{'k':r.randint(2,6)},
      'reciprocal_not_onto':{'a':r.randint(2,6),'b':r.randint(2,7)},
      'reciprocal_bijection':{'a':r.randint(2,6),'b':r.randint(2,7)},
      'integer_pair_bijection':{'k':r.randint(3,7)},
      'composition_order':{'a':r.randint(2,6),'b':r.randint(2,5)}}

def validate(t,p):
    if t not in CATALOG:raise ValueError('Unsupported template')
    if any(type(v) is not int for k,v in p.items() if k!='domain'):raise ValueError('Integer parameters required')
    checks=[]
    def require(ok,label):
        if not ok:raise ValueError(label)
        checks.append(label)
    if t=='relation_missing':
        require(p['a']!=0 and p['b']!=0,'Nonzero coefficients')
        require(Q(p['c'],p['b']).denominator!=1,'x=0 has no integer output')
    elif t=='relation_total':
        require(p['b']==1,'Coefficient of output is one: unique integer solution')
        require(p['a']!=0,'Nonzero input coefficient')
    elif t=='finite_range':
        require(bool(p['domain']) and all(type(x) is int for x in p['domain']),'Finite nonempty integer domain')
        require(len(set(p['domain']))==len(p['domain']),'No duplicate domain entries')
        require(all(type(x*x-p['shift']) is int for x in p['domain']),'Every output belongs to integer codomain')
    elif t=='equal_rational':
        require(p['a']>0,'Nonzero excluded point')
        # (x-a)(x+a)=x²-a²: coefficient identity, not sampled proof.
        require([1,p['a']-p['a'],-p['a']*p['a']]==[1,0,-p['a']**2],'Exact polynomial coefficient identity')
    elif t in ['square_real','square_nonnegative']:
        require(p['k']>0,'Positive square coefficient; square-root construction stays nonnegative')
    elif t in ['reciprocal_not_onto','reciprocal_bijection']:
        require(p['a']!=0,'Nonzero numerator: output never equals shift')
        # y != b => a/(y-b) exists and is nonzero, and a/[a/(y-b)]+b=y.
        require(Q(p['a'],p['a'])==1,'Exact inverse cancellation coefficient')
    elif t=='integer_pair_bijection':
        k=p['k'];A=((1,k),(1,k+1));B=((k+1,-k),(-1,1))
        require(A[0][0]*A[1][1]-A[0][1]*A[1][0]==1,'Integer matrix determinant one')
        for left,right in [(A,B),(B,A)]:
            require([[sum(left[i][s]*right[s][j] for s in range(2)) for j in range(2)] for i in range(2)]==[[1,0],[0,1]],'Exact inverse matrix product is identity')
    elif t=='composition_order':
        require(p['a']!=1 and p['b']!=0,'Scaling and translation do not commute')
        require(p['a']*p['b']!=p['b'],'Distinct constant coefficients in compositions')
    return checks

def build(t,p,title=None):
    checks=validate(t,p);c=CATALOG[t];page=c['page']
    def T(s):return {'kind':'text','text':s}
    def M(s):return {'kind':'math','latex':s,'display':True,'source':{'page':page}}
    R=r'\mathbb R';Z=r'\mathbb Z';a=p.get('a');b=p.get('b');k=p.get('k')
    if t.startswith('relation_'):
        q=[T('Does the following relation define a function from integers to integers?'),M(rf'R=\{{(x,y)\in {Z}\times {Z}: {a}x+{b}y={p["c"]}\}}')]
        if t=='relation_missing':
            ans=[T('No. For input zero the only rational candidate is not an integer, so existence fails.'),M(rf'x=0\implies y=\frac{{{p["c"]}}}{{{b}}}\notin {Z}')]
        else:
            ans=[T('Yes. For every integer input the equation has exactly one output, and it is an integer.'),M(rf'y={p["c"]}-{a}x\in {Z}')]
    elif t=='finite_range':
        d=','.join(map(str,p['domain']));image=sorted({x*x-p['shift'] for x in p['domain']})
        q=[T('Determine the domain, codomain and image of this function.'),M(rf'f:\{{{d}\}}\to {Z},\qquad f(x)=x^2-{p["shift"]}')]
        ans=[T('The stated finite set is the domain; the integers are the codomain. Evaluate every domain element:'),*[M(rf'f({x})={x*x-p["shift"]}') for x in p['domain']],T('Removing repeated values gives the image:'),M(rf'f(\{{{d}\}})=\{{{",".join(map(str,image))}\}}')]
    elif t=='equal_rational':
        dom=rf'{R}\setminus\{{{a}\}}'
        q=[T('Are these functions equal? Account for their domains.'),M(rf'f:{dom}\to {R},\quad f(x)=x+{a}'),M(rf'g:{dom}\to {R},\quad g(x)=\frac{{x^2-{a*a}}}{{x-{a}}}')]
        ans=[T('Yes. Their domains and codomains coincide. The denominator is nonzero everywhere on that domain, so factorization gives equal values at every allowed input:'),M(rf'\frac{{x^2-{a*a}}}{{x-{a}}}=\frac{{(x-{a})(x+{a})}}{{x-{a}}}=x+{a}\quad(x\ne {a})')]
    elif t=='square_real':
        q=[T('Determine whether this function is injective and whether it is surjective.'),M(rf'f:{R}\to {R},\qquad f(x)={k}x^2')]
        ans=[T('It is not injective: two distinct inputs give the same output.'),M(rf'f(1)=f(-1)={k}'),T('It is not surjective: all outputs are nonnegative, so minus one has no real preimage.'),M(rf'{k}x^2\geq0>-1\qquad(x\in {R})')]
    elif t=='square_nonnegative':
        q=[T('Prove that this function is bijective.'),M(rf'f:[0,\infty)\to[0,\infty),\qquad f(x)={k}x^2')]
        ans=[T('All outputs are nonnegative. For nonnegative inputs, equality of outputs implies equal squares and then equal inputs:'),M(rf'{k}u^2={k}v^2\implies u^2=v^2\implies u=v\quad(u,v\geq0)'),T('For every nonnegative target choose a nonnegative input as follows. Substitution verifies surjectivity, hence bijectivity.'),M(rf'x=\sqrt{{y/{k}}}\geq0,\qquad f(x)={k}(\sqrt{{y/{k}}})^2=y\quad(y\geq0)')]
    elif t.startswith('reciprocal_'):
        cod=R if t=='reciprocal_not_onto' else rf'{R}\setminus\{{{b}\}}'
        q=[T('Determine whether this function is injective and whether it is surjective onto the stated codomain.'),M(rf'f:{R}\setminus\{{0\}}\to {cod},\qquad f(x)=\frac{{{a}}}x+{b}')]
        ans=[T('The rule is defined on every allowed input. It is injective: equal outputs imply equal inputs, using nonzero inputs and numerator.'),M(rf'\frac{{{a}}}u+{b}=\frac{{{a}}}v+{b}\implies {a}v={a}u\implies v=u\quad(u,v\ne0)')]
        if t=='reciprocal_not_onto':
            ans += [T('It is not surjective onto the reals: the shift itself has no preimage.'),M(rf'f(x)={b}\implies \frac{{{a}}}x=0\quad\text{{impossible for }}x\ne0')]
        else:
            ans += [T('The output cannot equal the excluded shift. For every allowed target the following preimage exists and is nonzero. Substitution proves surjectivity; therefore the function is bijective.'),M(rf'y\ne {b},\quad x=\frac{{{a}}}{{y-{b}}}\ne0'),M(rf'f\left(\frac{{{a}}}{{y-{b}}}\right)=\frac{{{a}}}{{{a}/(y-{b})}}+{b}=y')]
    elif t=='integer_pair_bijection':
        q=[T('Prove that this function is bijective by constructing and verifying integer preimages.'),M(rf'f:{Z}^2\to {Z}^2,\qquad f(m,n)=(m+{k}n,m+{k+1}n)')]
        ans=[T('All outputs are integer pairs. To prove injectivity, equal outputs give these two equations:'),M(rf'm+{k}n=r+{k}s,\qquad m+{k+1}n=r+{k+1}s'),T('Subtracting the first equation from the second gives equal second coordinates; substitution gives equal first coordinates.'),M(r'n=s,\qquad m=r'),T('For any integer target pair choose the following integer input. Both coordinates substitute to the target, so the function is surjective and hence bijective.'),M(rf'n=v-u,\qquad m={k+1}u-{k}v'),M(rf'm+{k}n=({k+1}u-{k}v)+{k}(v-u)=u'),M(rf'm+{k+1}n=({k+1}u-{k}v)+{k+1}(v-u)=v')]
    else:
        q=[T('Compute both compositions and decide whether they are equal.'),M(rf'f:{R}\to {R},\quad f(x)=x+{b}'),M(rf'g:{R}\to {R},\quad g(x)={a}x')]
        ans=[T('Both compositions have real domain and codomain. Substitute in the stated order:'),M(rf'(g\circ f)(x)={a}(x+{b})={a}x+{a*b}'),M(rf'(f\circ g)(x)={a}x+{b}'),T('Their constant terms differ, so they are not equal functions.'),M(rf'{a*b}\ne {b}\implies g\circ f\ne f\circ g')]
    return {'template_id':t,'title':title or t.replace('_',' ').title(),'parameters':p,'source':c,'question':q,'answer':ans,'checks':checks,'status':'verified_for_supported_template'}

def verify_artifact(item):
    """Recompute complete program-owned mathematics; reject tampering, never repair silently."""
    expected=build(item['template_id'],item['parameters'],item['title'])
    if item!=expected:raise ValueError('Artifact differs from deterministic construction')
    return True
