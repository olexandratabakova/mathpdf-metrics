"""Narrow reproducible witnesses attached to human review; not a general verifier."""
from fractions import Fraction
from run import ROOT,read,write,sha

def build():
    published=read(ROOT/'result.json') if (ROOT/'result.json').exists() else None
    def items(slug):
        return next(s['items'] for s in published['problem_sets'] if s['id']==slug) if published else read(ROOT/f'output/{slug}-problems.json')['items']
    sets=items('sets');induction=items('induction');functions=items('functions');numbers=items('numbers')
    findings=[]
    def add(topic,n,kind,finding,witness):
        items={'sets':sets,'induction':induction,'functions':functions,'numbers':numbers}[topic]
        item=items[n-1]
        findings.append({'id':f'problem-{topic}-{n}','kind':kind,'finding':finding,'witness':witness,
                         'item_sha256':sha(__import__('json').dumps(item,sort_keys=True,ensure_ascii=False).encode())})
    A={1,frozenset({1})};singleton={1}
    assert singleton < A
    add('sets',5,'incorrect_solution','The answer declares {1} not a subset of A={1,{1}}, although its only element, 1, belongs to A. It is even a proper subset.',{'singleton_is_subset':singleton<=A,'singleton_is_proper_subset':singleton<A})
    A={1,frozenset({2})}
    assert 1 in A and {1}<A
    add('sets',10,'invalid_counterexample','The proposed counterexample A={1,{2}} does not refute the requested implication: 1 belongs to A and {1} is a proper subset of A. The answer confuses subset with membership.',{'hypothesis':1 in A,'claimed_failed_conclusion_actually_true':{1}<A})
    add('sets',9,'ill_typed_statement','The question equates the number of subsets with both the number 2^n and the set 2^S. It should distinguish a power set from its cardinality. The solution silently supplies the cardinality interpretation.',{'scope':'Statement/type inspection, not a numerical refutation.'})
    for n in [1,4]:
        assert all(x['kind']=='text' for x in induction[n-1]['question'])
        assert any(x['kind']=='math' for x in induction[n-1]['answer'])
        add('induction',n,'missing_statement_formula','The question asks to prove a formula/identity but does not state it. The required formula appears only in the answer, so the front is incomplete.',{'question_math_blocks':0,'question_text':induction[n-1]['question'][0]['text']})
    assert (2**3-2)%12==6
    add('induction',2,'false_theorem','The claim 12 divides n^3−n for all n≥1 is false: n=2 gives 6. The proof incorrectly treats an even multiple of 6 as necessarily divisible by 12.',{'n':2,'expression':6,'remainder_mod_12':6})
    lhs=2-Fraction(1,4)+Fraction(1,16);rhs=2-Fraction(1,16)
    assert lhs!=rhs
    add('induction',6,'invalid_proof','The proposed bound 2−1/4^n is weaker than S_n≤1 and cannot establish that goal. Its displayed equality is also false: for n=1 the sides are 29/16 and 31/16.',{'n':1,'left':str(lhs),'right':str(rhs),'claimed_bound_at_1':'7/4 > 1'})
    m=Fraction(4,9);n=Fraction(-1,9)
    assert 2*m-n==1 and m+4*n==0 and m.denominator!=1
    add('functions',5,'false_requested_surjectivity','The task asks for surjectivity of (m,n)↦(2m−n,m+4n) on Z². Target (1,0) requires (4/9,−1/9), so has no integer preimage. The solution notices the restriction but does not make the positive proof request valid.',{'target':[1,0],'unique_rational_preimage':[str(m),str(n)],'determinant':9})
    # Three distinct cases where the examiner rejects valid mathematical reasoning.
    add('induction',3,'model_false_rejection','The reviewer rejects the correct sum S_n=3n², then proposes exactly the same formula as its correction. The displayed induction is valid: base S_1=3 and 3n²+(6n+3)=3(n+1)².',{'base':3,'left_polynomial_coefficients':[3,6,3],'right_polynomial_coefficients':[3,6,3]})
    assert (1**3+4*1)%6==5
    add('induction',8,'model_false_rejection','The question explicitly asks to disprove the claim. Its n=1 counterexample gives 5, not divisible by 6, exactly as required. The reviewer repeats that valid disproof while labelling the solution incorrect.',{'counterexample_n':1,'value':5,'remainder_mod_6':5})
    assert [k*k%3 for k in range(3)]==[0,1,1]
    add('numbers',3,'model_false_rejection','The standard lowest-terms proof that sqrt(3) is irrational is valid: 3 divides m² implies 3 divides m; substitution forces 3 to divide n, contradicting coprimality. The reviewer incorrectly demands an additional even/even case already excluded by lowest terms.',{'squares_mod_3':[0,1,1],'coprimality_assumption_present':True})
    if published:
        def card_note(topic,n,kind,finding,witness):
            s=next(s for s in published['card_sets'] if s['id']==topic);item=s['items'][n-1]
            findings.append({'id':f'card-{topic}-{n}','kind':kind,'finding':finding,'witness':witness,
                             'item_sha256':sha(__import__('json').dumps(item,sort_keys=True,ensure_ascii=False).encode())})
        assert ((2*3)**2-1)%3==2
        card_note('induction',15,'front_changes_theorem','The front says a 2n×2n board, rather than the source theorem’s 2^n×2^n board. For literal n=3, a 6×6 board minus one square has 35 squares, which cannot be tiled by area-three trominoes. This is a semantic formula-to-prose failure despite zero renderer fallbacks.',{'n':3,'remaining_area':35,'remainder_mod_3':2})
        for topic,n in [('sets',3),('functions',13)]:
            s=next(s for s in published['card_sets'] if s['id']==topic);sc=s['metrics']['card_metrics'][n-1]['self_contained']
            assert not sc['passes'] and sc['blind_answer_matches']
            card_note(topic,n,'self_contained_judge_error','The judge supplies a matching blind answer but rejects the front for omitting the definition/conditions that the question is explicitly asking the learner to recall. Requiring that answer on the front conflicts with the recall task. The original failure and aggregate score are preserved.',{'blind_answer_matches':True,'passes':False,'original_missing_reason':sc['whats_missing']})
    return {'scope':'Targeted deterministic witnesses and statement inspection, supplemented by human reading. This does not label all other tasks correct.',
            'summary':'Separate local review identifies false claims, invalid reasoning and incomplete statements. These findings must not be replaced by model acceptance counts.',
            'items':findings}

if __name__=='__main__':
    data=build();write(ROOT/'local-checks.json',data);print(f"Saved {len(data['items'])} separate local findings; no API calls.")
