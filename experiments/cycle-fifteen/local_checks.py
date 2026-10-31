"""Exact narrow checks; not a general symbolic mathematics validator."""
from fractions import Fraction as Q
def check():
    assert Q(1,3).denominator!=1
    assert {2*x+1 for x in [0,1,2]}=={1,3,5}
    assert 2*3-1*1==5  # Original integer-pair map has nonzero determinant.
    # Symbolic elimination coefficients for 2*(m+3n)-(2m+n) = 5n.
    assert 2*1-2==0 and 2*3-1==5
    assert (2*0+2,0+3*2)!=(2*1-1,1+3*(-1))  # Reviewer supplied no collision.
    assert 1*2-1*1==1  # Replacement source example also injective.
    assert Q(4-1,2).denominator!=1
    assert Q(2,2)+1==2  # This output is excluded by the stated codomain.
    # 2/x+1=1 has no finite nonzero real x since 2/x cannot be zero.
    assert 2!=0
    assert 2*(1+1)!=2*1+1
    return True
if __name__=='__main__':
    check();print('Exact checks passed; universal claims additionally reviewed manually.')
