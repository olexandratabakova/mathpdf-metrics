"""Specific local counterexamples, separate from general SymPy adapter verdicts."""
import itertools,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
import sympy as s
def check():
    birthdays=[5,5]+[4]*10
    assert len(birthdays)==12 and sum(birthdays)==50 and max(birthdays)<6
    # All points are strictly inside the unit square, not just on its boundary.
    a,b,c=s.Rational(1,100),s.Rational(1,2),s.Rational(99,100)
    points=[(a,a),(a,b),(a,c),(b,a),(b,c),(c,a),(c,b)]
    distances=[sum((u[i]-v[i])**2 for i in range(2)) for u,v in itertools.combinations(points,2)]
    assert all(0<x<1 and 0<y<1 for x,y in points)
    assert min(distances)==s.Rational(2401,10000)>s.Rational(2,9)
    assert s.factorial(2)!=s.factorial(3)-2
    # Near7 prose is correct at n=1; its distinct formal encoding is wrong.
    assert 2*s.factorial(2)==s.factorial(3)-2
    assert 3*s.factorial(3)!=s.factorial(3)-2
    return {'birthday_counts':birthdays,'square_points':[[str(x),str(y)] for x,y in points],
      'minimum_squared_distance':str(min(distances)),'claimed_squared_bound':'2/9',
      'transfer_4_n_2':{'left':2,'right':4},'near_7_formal_n_1':{'left':18,'right':4},
      'limits':'These are specific exact counterexamples, not an automatic general proof reader.'}
if __name__=='__main__':
    import json
    (ROOT/'local-checks.json').write_text(json.dumps(check(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
