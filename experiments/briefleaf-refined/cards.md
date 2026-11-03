# Briefleaf refined · 20 cards and evaluation

Generator: gpt-4.1-mini. Judge: gpt-4o-mini. Cost: $0.05027273. Original outputs retained. Not ready to promote.

| Original metric | Result |
| --- | ---: |
| pct_self_contained | 80.0% |
| avg_faithfulness | 88.4% |
| pct_front_leaks | 0.0% |
| pct_atomic | 75.0% |
| pct_understanding | 80.0% |
| pct_trivial | 0.0% |
| duplicate_rate | 0.0% |
| coverage_ratio | 50.6% |

Revised self-containment diagnostic: 18/20, separate from original rubric. No overall correctness percentage.

## Cards

## Sets

### 1. Set membership notation

**Question:** How do you denote that an object x is an element of a set A?

**From notes:** We write $x \in A$ when $x$ is an element of $A$.

**Explanation:** (empty)

Source page: 4. Skill: recall.

Central formula: $$x \in A$$

**Local finding:** Central membership formula repeats in From notes.

### 2. Definition of Cartesian product of two sets

**Question:** What is the definition of the Cartesian product of two sets A and B?

**From notes:** The Cartesian product of sets $A$ and $B$ is the set of ordered pairs $(a,b)$ where $a \in A$ and $b \in B$$.$

**Explanation:** (empty)

Source page: 5. Skill: meaning.

Central formula: $$A \times B = \{(a,b) : a \in A, b \in B\}$$

**Local finding:** Definition is labelled meaning; a period is encoded as math.

### 3. Number of subsets of a finite set

**Question:** Why does a finite set with n elements have 2 to the power n subsets?

**From notes:** If a finite set $S$ has $n$ elements, then it has $2^{n}$ subsets.

**Explanation:** Each element can either be included or excluded independently in a subset, so the total number of subsets is the product of 2 repeated n times, which equals $2^{n}$.

Source page: 5. Skill: why_justification.

Central formula: $$2^{n}$$

### 4. Set difference operation

**Question:** Given sets A and B, what is the set difference A minus B?

**From notes:** The difference of sets $A$ and $B$ is the set of $x$ such that $x \in A$ and $x \notin B$.

**Explanation:** (empty)

Source page: 6. Skill: application.

Central formula: $$A \setminus B = \{ x : x \in A \text{ and } x \notin B \}$$

**Local finding:** No concrete sets are supplied; this asks for a definition rather than application.

### 5. Distributive law for sets

**Question:** Why does the intersection of A with the union of B and C equal the union of the intersections of A with B and A with C?

**From notes:** For sets $A$, $B$, and $C$, we have the equality $A \cap (B \cup C) = (A \cap B) \cup (A \cap C)$.

**Explanation:** This follows because every element in $A \cap (B \cup C)$ belongs to $A$ and to at least one of $B$ or $C$, so it lies in either $A \cap B$ or $A \cap C$, proving inclusion one way; the other inclusion follows similarly by considering elements in the union.

Source page: 6. Skill: why_justification.

## Mathematical Induction

### 1. Principle of mathematical induction

**Question:** What are the three steps to prove a statement using mathematical induction for all integers greater than or equal to some initial integer?

**From notes:** Suppose we want to prove a statement P(n) for every integer n greater than or equal to n_0. We prove it in three steps: (1) Base case: prove P(n_0). (2) Induction hypothesis: fix an arbitrary integer n greater or equal to n_0 and assume P(n) is true. (3) Induction step: using the induction hypothesis, prove that P(n+1) is true.

**Explanation:** (empty)

Source page: 14. Skill: recall.

**Local finding:** P(n), n_0 and P(n+1) are ordinary strings instead of math objects.

### 2. Inductive proof that the sum of squares formula holds

**Question:** How does one prove by induction that the sum of the first n squares equals n times n plus 1 times 2 n plus 1 divided by 6 for natural numbers n?

**From notes:** To prove that \sum_{k=1}^n k^2=\frac{n(n+1)(2n+1)}{6}, first prove the base case n=1. Then assume the formula for n and use it to prove the formula for n+1 by adding (n+1)^2 and simplifying to match the formula.

**Explanation:** (empty)

Source page: 14. Skill: application.

Central formula: $$\sum_{k=1}^n k^2=\frac{n(n+1)(2n+1)}{6}$$

**Local finding:** Says add and simplify without showing the induction algebra. Front states the formula it asks to prove. Central sigma notation differs from the printed explicit sum on page 14.

### 3. Why is it impossible to prove the inequality sum of 1 over i squared is less than or equal to 2 by direct induction?

**Question:** Why can't the inequality 1 over 1 squared plus 1 over 2 squared plus ... plus 1 over n squared is less than or equal to 2 be proven directly by induction?

**From notes:** It is impossible to prove this inequality directly by induction because the induction step fails; instead, a stronger inequality is proved that allows closing the induction.

**Explanation:** The induction step requires bounding the added term 1 over (n+1)^2 in a way that the weaker inequality doesn’t suffice, so a stronger inequality is used to complete the induction.

Source page: 16. Skill: error_diagnosis.

**Local finding:** Repeats source page 16 phrasing that direct induction is impossible; source faithfulness conflicts with the narrower mathematical claim. Should ask why the naive estimate does not close, or select another target. Explanation paraphrases the first block.

### 4. Definition of factorial

**Question:** What is the definition of factorial for natural numbers including zero?

**From notes:** For n in the natural numbers, n factorial is defined as the product 1 times 2 times ... times n, and 0 factorial is defined to be 1.

**Explanation:** (empty)

Source page: 17. Skill: recall.

**Local finding:** Second explicitly labelled recall in the same five-card induction set; maximum requested was one.

### 5. Application of strong induction to express integers with 3-euro and 5-euro coins

**Question:** How does strong induction prove that every integer greater or equal to 8 can be expressed as a sum of multiples of 3 euros and 5 euros?

**From notes:** The proof uses base cases for 8, 9, and 10. Then for n+1 greater or equal to 11, since n+1 minus 3 is between 8 and n, by induction hypothesis n+1 minus 3 can be expressed as 3 a' plus 5 b'. Adding 3 gives n+1 as 3 (a'+1) plus 5 b', completing the proof.

**Explanation:** (empty)

Source page: 18. Skill: application.

## Numbers

### 1. Definition of an irreducible fraction

**Question:** What does it mean for a fraction to be irreducible or in lowest terms?

**From notes:** A fraction $\frac{m}{n}$ is irreducible, or in lowest terms, if $m$ and $n$ have no common factors greater than 1.

**Explanation:** (empty)

Source page: 22. Skill: recall.

### 2. Existence of an irrational number between two distinct real numbers

**Question:** How can you find an irrational number between any two distinct real numbers 

**From notes:** Between any two distinct real numbers there is an irrational number.

**Explanation:** Given $a < b$, choose a natural number $n$ such that $\frac{\sqrt{2}}{n} < b - a$. If $a$ is rational, then $a + \frac{\sqrt{2}}{n}$ is irrational and lies between $a$ and $b$. Otherwise, choosing $a + \frac{1}{n}$ maintains irrationality and lies between $a$ and $b$.

Source page: 23. Skill: application.

**Local finding:** Question ends without punctuation, but its mathematical request is recoverable. Construction itself supplies both rational/irrational cases.

### 3. Uniqueness of decimal expansions of real numbers

**Question:** Why do two different decimal representations of the same number differ only by a repeating 9-to-0 pattern starting from some digit?

**From notes:** Two decimal representations of the same real number that differ are such that from the $k$th digit onward they are of the form $\cdots a_k 999 \ldots$ and $\cdots (a_k + 1)000 \ldots$ respectively.

**Explanation:** If the digits differ first at position $k$, then assuming $a_k < b_k$, the number is bounded above and below by the two representations, which is only possible if the first has repeating 9s and the second trailing zeros starting at digit $k$.

Source page: 25. Skill: why_justification.

**Local finding:** Decimal uniqueness explanation asserts the decisive tail bound rather than deriving it.

### 4. Eventual periodicity of rational number decimal expansions

**Question:** Why does every rational number have a decimal representation that is eventually periodic?

**From notes:** Every rational number has an eventually periodic decimal representation.

**Explanation:** In the long division of numerator by denominator, remainders come from a finite set. Either the division terminates when a remainder is zero or a remainder repeats, causing the decimals to repeat periodically thereafter.

Source page: 26. Skill: why_justification.

### 5. Uniqueness of base-b representation of natural numbers

**Question:** Under what conditions does a natural number have a unique representation in base b?

**From notes:** For base $b \in \mathbb{N}, b \geq 2$, every natural number $m$ has a unique representation $m = a_k b^k + \cdots + a_1 b + a_0$, with digits $0 \leq a_i < b$ and $a_k \neq 0$.

**Explanation:** (empty)

Source page: 27. Skill: conditions.

**Local finding:** Base-b theorem is on page 26, not cited 27. Nonzero leading digit excludes zero if natural numbers include zero; retain source convention or specify positive integer.

## Functions

### 1. Definition of a function from one set to another

**Question:** What is the formal definition of a function from a set X to a set Y?

**From notes:** A function from $X$ to $Y$ is a relation $f \subset X \times Y$ such that, for every $x \in X$ , there is exactly one $y \in Y$ with $(x,y) \in f$.

**Explanation:** (empty)

Source page: 63. Skill: recall.

### 2. Injective function condition

**Question:** What condition must a function from set X to Y satisfy to be injective?

**From notes:** A function $f : X \to Y$ is injective (one-to-one) if for all $x_1, x_2 \in X$ we have: $f(x_1) = f(x_2) \implies x_1 = x_2$.

**Explanation:** (empty)

Source page: 64. Skill: conditions.

**Local finding:** Asks for injectivity definition, not an actual condition decision on a given case.

### 3. Surjectivity proof strategy

**Question:** How can you prove that a function from X to Y is surjective?

**From notes:** To prove surjectivity, take an arbitrary element $y$ in the codomain and show there exists an element $x$ in the domain such that $f(x) = y$.

**Explanation:** This involves solving the equation $f(x) = y$ for $x$ to demonstrate existence.

Source page: 65. Skill: application.

**Local finding:** Asks for a general proof strategy, not application to specified givens; explanation largely restates existence of a preimage.

### 4. Inverse function of a bijection

**Question:** What is the inverse function of a bijection from X to Y?

**From notes:** If $f : X \to Y$ is a bijection, the inverse function $f^{-1} : Y \to X$ is defined by $f^{-1}(y) = x \iff f(x) = y$.

**Explanation:** (empty)

Source page: 67. Skill: meaning.

**Local finding:** Inverse definition labelled meaning.

### 5. Range of a specific real-valued function

**Question:** Find the range of the function defined from real numbers to real numbers by f of x equals two x divided by one plus x squared.

**From notes:** The range of $f : \mathbb{R} \to \mathbb{R}, f(x) = \frac{2x}{1+x^2}$ is the interval $[-1,1]$.

**Explanation:** The function attains all values between -1 and 1, inclusive.

Source page: 69. Skill: application.

**Local finding:** Range [-1,1] is correct and appears on page 69, but explanation simply repeats the result. It does not show the bound or that every intermediate value is attained.
