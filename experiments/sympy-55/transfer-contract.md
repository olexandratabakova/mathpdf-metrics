# Main transfer batch: fifteen explicit changes of mathematical conditions

Generate exactly these fifteen changed-condition scenarios, choosing your own new numerical givens and complete worked solutions. Every condition_change must accurately identify the source condition and the modified mathematical condition. A changed constant alone is insufficient. Do not copy the previous pilot or its titles. Use the following IDs and kinds; the program does not supply final answers.

1 finite_set: relative complement after changing the finite universe; include the exact universe and subset.
2 finite_set: Cartesian product when one factor is empty, unlike a nonempty source example. Integer factors only.
3 summation: odd-type sum including the index zero rather than starting at one; use positive integer n.
4 induction: factorial-type equality with the first term removed; state the new starting n and give its correct base and full step.
5 congruence: coefficient and modulus not coprime and right side incompatible, so existence must be decided rather than assuming an inverse.
6 congruence: coefficient and modulus not coprime with a compatible right side; find ALL residue classes, not only one.
7 counting: integer solutions to a sum when every variable must be positive instead of merely nonnegative.
8 counting: committee with an additional at-least-two-members-from-a-specified-subgroup requirement; clearly state subgroup sizes and committee size.
9 function: square-type map with nonnegative domain but codomain all reals, rather than restricting both to nonnegative reals; ask surjectivity.
10 expression: simplify sqrt(x**2) after removing a positivity assumption, with ALL real inputs; preserve the changed domain.
11 solve: rational equation where an algebraic candidate is an excluded denominator root; preserve the hole when giving the complete real solution set.
12 solve: square-type equation on the INTEGERS instead of the reals, choosing a nonsquare positive target.
13 inequality: a polynomial inequality that fails for some reals but holds after restricting to a specified interval; decide the universal assertion on that interval.
14 proof: reverse a composition implication; decide whether injectivity of the composition forces injectivity of its first map without assuming the second map injective; give a full argument.
15 proof: remove coprimality-to-ten from the repunit source problem by using a modulus with factor two or five; decide whether a positive all-ones decimal can be divisible by it.

params_json and answer use exact machine expressions, NOT TeX. Use Complement(Reals,FiniteSet(...)), not a textual set difference; use k for the summation variable. gcd, lcm and Mod are additionally permitted. No comprehensions or arbitrary Python code. expression expr is not an equation. finite_set asks only its encoded operation. Any intermediate equality steps must be identities under original restrictions; do not encode induction hypotheses or temporary equal-output assumptions as identities. These conditions constrain scenarios, not the numerical answers: compute and justify every answer yourself.
