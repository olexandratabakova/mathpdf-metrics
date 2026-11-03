# Briefleaf · 20 generated flashcards

Generator: gpt-4.1-mini. No model evaluator used. Total recorded cost including incomplete first call: $0.02531920.

Original output retained. [U+XXXX] exposes control characters; these are defects, not corrections. Source citations have not been independently verified.

## Sets

### 1. Definition and notation of a set and its elements

**Question:** What is a set and how is membership of an element in a set denoted?

**From notes:** Definition 1.1. A set is a collection of objects. The objects belonging to the set are called its elements. We write x [U+0002]2A A when x is an element of A, and x [U+0002]2A A otherwise.

**Explanation:** (empty)

**Legacy answer (should have been empty):** A set is a collection of objects, called its elements. Membership is denoted by x [U+0002]2A meaning element x is in set A,and x [U+0002]2A otherwise.

Source page: 4. Skill: recall.

### 2. Definition and cardinality of the empty set

**Question:** What is the empty set and how is it distinguished from the set containing the empty set?

**From notes:** Definition 1.2. The empty set is the set with no elements. It is denoted by [U+0002]85 or {}. In particular, [U+0002]85 [U+0002]2A [U+0002]85 : the first set has no elements, whereas the second has one element.

**Explanation:** (empty)

**Legacy answer (should have been empty):** The empty set [U+0002]85 or {} contains no elements, and is not equal to {[U+0002]85} which contains one element: the empty set itself.

Source page: 4. Skill: meaning.

### 3. Number of subsets of a finite set

**Question:** Why does a finite set with n elements have exactly 2 to the power n subsets?

**From notes:** Theorem 1.7. If a finite set S has n elements, then it has 2^{n} subsets. Proof: for each element x_i, there are two choices: include it or exclude it, so the total number of subsets is 2 \cdot 2 \cdots 2 = 2^{n}.

**Explanation:** Each subset corresponds to choosing independently whether to include each element or not, producing 2^{n} distinct subsets that correspond to binary strings of length n.

**Legacy answer (should have been empty):** A finite set with n elements has 2^{n} subsets because each element can either be included or not included independently in a subset.

Source page: 5. Skill: why_justification.

### 4. Set equality conditions

**Question:** Under what condition are two sets A and B equal?

**From notes:** Definition 1.4. Two sets A and B are equal if every element of A is an element of B, and every element of B is an element of A.

**Explanation:** (empty)

**Legacy answer (should have been empty):** Two sets A and B are equal if every element of A is in B, and every element of B is in A.

Source page: 4. Skill: conditions.

### 5. Definition and notation of Cartesian product of sets

**Question:** What is the Cartesian product of sets A and B, and how is it represented?

**From notes:** Definition 1.5. For sets A and B, the Cartesian product is A [U+0000]D7 B = \{ (a,b) : a [U+0002]2A A, b [U+0002]2A B \}.

**Explanation:** (empty)

**Legacy answer (should have been empty):** The Cartesian product A [U+0000]D7 B is the set of ordered pairs (a,b) with a [U+0002]2A A and b [U+0002]2A B.

Source page: 5. Skill: meaning.

## Mathematical Induction

### 1. Basic principle of mathematical induction

**Question:** What are the three essential steps to prove a statement P(n) for all integers n greater or equal to n0 using mathematical induction?

**From notes:** Suppose we want to prove a statement P(n) for every integer n ≥ n0 . We prove it in three steps: 1. Base case: prove P(n0) . 2. Induction hypothesis: fix an arbitrary integer n ≥ n0 and assume that P(n) is true. 3. Induction step: using the induction hypothesis, prove that P(n + 1) is true.

**Explanation:** (empty)

**Legacy answer (should have been empty):** To prove the statement P(n) for all integers n ≥ n0 by induction, we perform (1) base case: prove P(n0), (2) induction hypothesis: fix n ≥ n0 and assume P(n) true, (3) induction step: prove P(n + 1) using the hypothesis.

Source page: 14. Skill: meaning.

### 2. Sum of squares formula proven by induction

**Question:** How can the formula for the sum of the first n squares be proven using induction?

**From notes:** Example 3.1 proves that 1^2 + 2^2 + ... + n^2 = \frac{n(n+1)(2n+1)}{6} by verifying base case n=1, assuming the formula holds for n, then adding (n+1)^2 and simplifying to get the formula for n+1.

**Explanation:** (empty)

**Legacy answer (should have been empty):** The formula n000 \sum_{k=1}^n k^2 = \frac{n(n+1)(2n+1)}{6} is proven by base case check for n=1 and then assuming it for n, proving it for n+1 by algebraic manipulation.

Source page: 14. Skill: application.

### 3. Why direct proof by induction fails for a sum of reciprocals

**Question:** Why is it impossible to prove the inequality 1/1 squared plus 1/2 squared plus ... plus 1/n squared less or equal to 2 by direct induction?

**From notes:** Example 3.4 explains why direct induction fails and instead proves a stronger inequality  \sum_{i=1}^n \frac{1}{i^2} \leq 2-\frac{1}{n}.

**Explanation:** (empty)

**Legacy answer (should have been empty):** It is impossible to prove the inequality directly by induction because the induction step requires a stronger statement to close the argument.

Source page: 16. Skill: why_justification.

### 4. Statement and proof method of the triangle inequality

**Question:** What does the triangle inequality for real numbers x1, ..., xn state and how is it proven by induction?

**From notes:** Theorem 3.7 states for real numbers x1,...,xn, |x1 + · · · + xn| ≤ |x1| + · · · + |xn|. The proof is by induction, using Lemma 3.6 (two-number case) as a base.

**Explanation:** (empty)

**Legacy answer (should have been empty):** The triangle inequality states |x1 + ... + xn| ≤ |x1| + ... + |xn| for real numbers and is proven by induction using the two-number case as the base and inductive step.

Source page: 17. Skill: meaning.

### 5. Strong induction with coin problem example

**Question:** How is strong induction used to prove every integer n greater or equal to 8 can be expressed as 3a plus 5b for nonnegative integers a,b?

**From notes:** Example 3.12 proves every integer n ≥ 8 can be expressed as n=3a+5b by strong induction: base cases 8,9,10, then assuming true for all k ≤ n, proving for n+1 by writing n+1-3 and adding back 3.

**Explanation:** (empty)

**Legacy answer (should have been empty):** Strong induction proves this by verifying base cases n=8,9,10 and assuming all integers k with 8 ≤ k ≤ n can be expressed, then showing n+1 can be expressed using the form of n-2 plus 3.

Source page: 18. Skill: application.

## Numbers

### 1. Definition and properties of irreducible fractions

**Question:** What defines a fraction m/n as irreducible in the rational number system?

**From notes:** Definition 5.1. A fraction $m/n$ is irreducible, or in lowest terms, if $m$ and $n$ have no common factors greater than 1.

**Explanation:** (empty)

**Legacy answer (should have been empty):** A fraction $m/n$ is irreducible, or in lowest terms, if $m$ and $n$ have no common factors greater than 1.

Source page: 22. Skill: meaning.

### 2. Density of rational numbers on the real line

**Question:** Why is there always another rational number between any two distinct rational numbers a and b?

**From notes:** Theorem 5.2. Between any two distinct rational numbers there is another rational number. Proof: If $a,b \in \mathbb{Q}$ and $a < b$ then their midpoint $c=\frac{a+b}{2}$ is rational and satisfies $a < c < b$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** Between any two distinct rational numbers $a < b$, the midpoint $c=\frac{a+b}{2}$ is a rational number that satisfies $a < c < b$.

Source page: 22. Skill: why_justification.

### 3. Existence of irrational numbers between any two real numbers

**Question:** How can one find an irrational number between any two distinct real numbers a and b?

**From notes:** Theorem 5.6. Between any two distinct real numbers there is an irrational number. Proof involves choosing large $n \in \mathbb{N}$ such that $\frac{\sqrt{2}}{n} < b - a$ and constructing the irrational number accordingly.

**Explanation:** (empty)

**Legacy answer (should have been empty):** If $a < b$, choose a large enough natural number $n$ so that $\frac{\sqrt{2}}{n} < b - a$. Then if $a \in \mathbb{Q} $take $a + \frac{\sqrt{2}}{n}$; if $a \notin \mathbb{Q} $take $a + \frac{1}{n}$; these lie between $a$ and $b$ and are irrational.

Source page: 23. Skill: application.

### 4. Uniqueness and non-uniqueness of decimal expansions

**Question:** What explains the non-uniqueness of decimal representations for the same real number?

**From notes:** Theorem 5.9 states: If two decimal representations of the same real number are different, then for some $k$ they agree up to the ($k-1$ )-st digit, and from the $k$-th digit onward they are of the form $\cdots a_k 999\ldots$ and $\cdots (a_k+1) 000\ldots$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** If two decimal representations differ, then at some position $k$ they agree until digit $k-1$ and afterwards one has repeating 9's and the other has the digit $a_k+1$ followed by zeros.

Source page: 25. Skill: error_diagnosis.

### 5. Relationship between rational numbers and periodic decimals

**Question:** How is every rational number related to decimal expansions in terms of periodicity?

**From notes:** Theorem 5.11. Every rational number has an eventually periodic decimal representation.

Theorem 5.12. Every periodic decimal represents a rational number.

**Explanation:** (empty)

**Legacy answer (should have been empty):** Every rational number has an eventually periodic decimal representation, and conversely, every periodic decimal represents a rational number.

Source page: 26. Skill: comparison.

## Functions

### 1. Definition of a function from X to Y

**Question:** What is the definition of a function from a set X to a set Y?

**From notes:** Definition 12.1. A function from $X$ to $Y$ is a relation $f \subset X \times Y$ such that, for every $x \in X$, there is exactly one $y \in Y$ with $(x, y) \in f$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** A function from $X$ to $Y$ is a relation $f\subset X \times Y$ such that, for every $x \in X$, there is exactly one $y \in Y$ with $(x,y) \in f$.

Source page: 63. Skill: meaning.

### 2. Equality of functions with different domains

**Question:** Are the functions defined by f1: R to R, f1(x) equals x plus 2, and f2: R without 2 to R, f2(x) equals x plus 2, equal?

**From notes:** We have $g_2 \neq f_1$, because their domains differ: $\mathbb{R} \setminus \{2\}$ vs. $\mathbb{R}$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** No, $f_1 \neq f_2$ because their domains differ: $\mathbb{R} \neq \mathbb{R} \setminus \{2\}$.

Source page: 64. Skill: error_diagnosis.

### 3. Condition for injectivity of a function f: X to Y

**Question:** What is the definition of an injective function from X to Y?

**From notes:** Definition 12.8. (1) $f$ is injective (one-to-one) if [U+0002]2$\forall x_1,x_2 \in X : f(x_1) = f(x_2) \implies x_1 = x_2$[U+0002]1.

**Explanation:** (empty)

**Legacy answer (should have been empty):** A function $f: X \to Y$ is injective if for all $x_1, x_2 \in X$, $f(x_1) = f(x_2)$ implies $x_1 = x_2$.

Source page: 64. Skill: meaning.

### 4. Inverse function of a bijection f: X to Y

**Question:** What is the definition of the inverse function for a bijection f: X to Y?

**From notes:** Definition 12.18. Let $f: X \to Y$ be a bijection. The inverse function $f^{-1}: Y \to X$ is the inverse relation of $f$: $f^{-1}(y) = x \iff f(x) = y$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** The inverse function $f^{-1}: Y \to X$ is defined by $f^{-1}(y) = x \iff f(x) = y$.

Source page: 67. Skill: meaning.

### 5. Composition of injective and surjective functions

**Question:** Why is the composition g o f injective if both f: X to Y and g: Y to Z are injective?

**From notes:** Proof. (i) Suppose $(g \circ f)(x_1) = (g \circ f)(x_2)$. Then $g(f(x_1)) = g(f(x_2))$ which by injectivity of $g$ implies $f(x_1) = f(x_2)$ which by injectivity of $f$ implies $x_1 = x_2$.

**Explanation:** (empty)

**Legacy answer (should have been empty):** If $(g \circ f)(x_1) = (g \circ f)(x_2)$, then injectivity of $g$ implies $f(x_1) = f(x_2)$, which injectivity of $f$ implies $x_1 = x_2$.

Source page: 66. Skill: why_justification.
