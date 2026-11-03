# Briefleaf with full technical context · 20 cards

Generator: gpt-4.1-mini. No model evaluator. Cost: $0.02325440. Original output, including defects, retained.

## Local findings

- Numbers 1 contains repeated serialized JSON-like text inside math fields; invalid mathematical payload despite schema acceptance.
- Induction cards contain raw TeX in prose, ambiguous powers on card 3, and raw notation in titles.
- Induction 3 repeats the overstatement that direct induction is impossible; it should identify failure of a naive induction estimate.
- Sets 4 bundles union and intersection; Functions 3 bundles three definitions; Functions 5 bundles image/preimage properties.
- Functions explanations often paraphrase their source answers. Sets 3 repeats the argument in both sections.
- Recall questions labelled meaning and insufficient application/error-diagnosis targets remain; skill labels alone do not establish level-3 compliance.

## Sets

### 1. Set membership notation

**Question:** How is it written that an object x is an element of a set A?

**From notes:** We write $x \in A$ when $x$ is an element of $A$.

**Explanation:** (empty)

Source page: 4. Skill: recall.

Central formula: $$x \in A$$

### 2. Definition of the Cartesian product of two sets

**Question:** What is the Cartesian product of two sets A and B?

**From notes:** The Cartesian product $A \times B$ is the set of all ordered pairs $(a,b)$, where $a \in A$ and $b \in B$.

**Explanation:** (empty)

Source page: 5. Skill: meaning.

### 3. Cardinality of power set of a finite set

**Question:** Why does a finite set S with n elements have exactly 2 to the power n subsets?

**From notes:** If a finite set $S = \{x_1, \ldots, x_n\}$ has $n$ elements, each element can either be included or not in a subset, giving $2^n$ subsets.

**Explanation:** Each element $x_i$ has two independent choices: include it or exclude it. Multiplying these for all $n$ elements gives $2^n$ subsets in total.

Source page: 5. Skill: why_justification.

### 4. Definition of union and intersection of sets A and B

**Question:** How are the union and intersection of sets A and B defined?

**From notes:** The union $A \cup B$ is the set of elements in $A$ or $B$. The intersection $A \cap B$ is the set of elements in both $A$ and $B$.

**Explanation:** (empty)

Source page: 6. Skill: meaning.

### 5. Complement of a set with respect to a universal set U

**Question:** What is the complement of a set A relative to a universal set U?

**From notes:** The complement of $A$ is $A^c = U \setminus A$; it contains all elements in $U$ not in $A$.

**Explanation:** (empty)

Source page: 7. Skill: meaning.

## Mathematical Induction

### 1. What is the principle of mathematical induction?

**Question:** What are the key steps in the principle of mathematical induction for proving a statement  P(n)  for every integer  n  greater or equal to  n0?

**From notes:** Suppose we want to prove a statement  P(n)  for every integer  n \geq n_0 . We prove it in three steps: Base case: prove  P(n_0) ; Induction hypothesis: assume  P(n)  is true for arbitrary  n \geq n_0 ; Induction step: prove  P(n+1)  using the induction hypothesis.

**Explanation:** (empty)

Source page: 14. Skill: meaning.

### 2. How is the divisibility notation  a|b  defined for integers?

**Question:** What does it mean for an integer  a  to divide another integer  b ?

**From notes:**  For integers  a  and  b , the notation  a|b  means that  a  divides  b . Equivalently,  a|b \iff \exists c \in \mathbb{Z} : b = c a .

**Explanation:** (empty)

Source page: 15. Skill: recall.

### 3. Why can't the inequality 1/1^2 + 1/2^2 + ... + 1/n^2 \leq 2  be proved directly by induction?

**Question:** Explain why it is impossible to prove the inequality  1/1 2  plus 1/2 2  plus  ... plus 1/n 2  is less or equal to 2  directly by induction.

**From notes:** 

**Explanation:** The direct induction step does not close because adding 1/(n+1) 2  is not sufficient to maintain the inequality; a stronger inequality is needed for a successful induction proof as shown in Example 3.5.

Source page: 16. Skill: error_diagnosis.

### 4. State the triangle inequality for the sum of  n  real numbers.

**Question:** What does the triangle inequality say about the absolute value of the sum of real numbers  x1, x2, ..., xn ?

**From notes:** For real numbers  x_1, \ldots, x_n , \left\lvert x_1 + \cdots + x_n \right\rvert \leq \lvert x_1 \rvert + \cdots + \lvert x_n \rvert .

**Explanation:** (empty)

Source page: 17. Skill: recall.

### 5. How does strong induction differ from ordinary induction?

**Question:** What is the difference between strong induction and ordinary induction in proving  P(n) ?

**From notes:** Ordinary induction assumes  P(n)  to prove  P(n+1) . Strong induction assumes  P(k)  holds for all  k  with initial value up to  n, and uses these to prove  P(n+1) .

**Explanation:** (empty)

Source page: 18. Skill: meaning.

## Numbers

### 1. Definition of irreducible fraction

**Question:** What does it mean for a fraction to be irreducible or in lowest terms?

**From notes:** A fraction $\frac{m}{n}$$ is irreducible or in lowest terms if m and n have no common factors greater than 1.}]}],$explanation:[]},{

A fraction $\frac{m}{n}$$ is irreducible or in lowest terms if m and n have no common factors greater than 1.}]}],$explanation:[]},{

A fraction $\frac{m}{n}$$ is irreducible or in lowest terms if m and n have no common factors greater than 1.}]}],$explanation:[]},{

A fraction $\frac{m}{n}$$ is irreducible or in lowest terms if m and n have no common factors greater than 1.}]}],$explanation:[]},{

A fraction $\frac{m}{n}$$ is irreducible or in lowest terms if m and n have no common factors greater than 1.}]}],$explanation:[]}{

**Explanation:** (empty)

Source page: 22. Skill: recall.

### 2. Density of rational numbers

**Question:** Why is there always a rational number between any two distinct rational numbers?

**From notes:** Between any two distinct rational numbers there is another rational number.

**Explanation:** The midpoint of two rationals is rational and lies strictly between them.

Source page: 22. Skill: meaning.

### 3. Irrational numbers and their relation to rationals

**Question:** Can the sum of a rational number and an irrational number ever be rational?

**From notes:** The sum of a rational and an irrational number is never rational.

**Explanation:** If the sum were rational, subtracting the rational from it would make the irrational rational, which is a contradiction.

Source page: 23. Skill: conditions.

### 4. Decimal representation construction

**Question:** How can we construct the decimal representation of any real number in (0,1)?

**From notes:** Every x in (0,1) can be approximated by decimal digits a1,a2,a3,... chosen inductively based on successive partitions of intervals.

**Explanation:** At step n, choose digit a_n so that x lies in the corresponding tenth subinterval of size 10^{-n}.

Source page: 24. Skill: application.

### 5. Periodic decimals and rational numbers

**Question:** Why does every periodic decimal represent a rational number?

**From notes:** Every periodic decimal represents a rational number.

**Explanation:** Shifting the decimal by the length of the period shows that the decimal satisfies a linear equation with integer coefficients, hence equals a rational number.

Source page: 26. Skill: why_justification.

## Functions

### 1. Definition of a function between sets

**Question:** What is the definition of a function from a set X to a set Y?

**From notes:** A function from $X$ to $Y$ is a relation $f \subset X \times Y$ such that for every $x \in X$, there is exactly one $y \in Y$ with $(x,y) \in f$.

**Explanation:** Each element of the domain $X$ is associated with a unique element in the codomain $Y$, ensuring a well-defined output for each input.

Source page: 63. Skill: meaning.

### 2. Equality of functions

**Question:** Under what conditions are two functions equal?

**From notes:** Two functions $f: X_1 \to Y_1$ and $g: X_2 \to Y_2$ are equal if $X_1 = X_2$ and $f(x) = g(x)$ for all $x \in X_1$.

**Explanation:** Equality requires identical domains and matching values for all elements in the domain. The codomain equality may or may not be required depending on definitions.

Source page: 63. Skill: conditions.

### 3. When is a function injective, surjective, and bijective?

**Question:** What characterizes an injective, surjective, and bijective function from X to Y?

**From notes:** A function $f:X \to Y$ is: (1) injective if distinct inputs map to distinct outputs; (2) surjective if every element of $Y$ is an image of some element in $X$; (3) bijective if it is both injective and surjective.

**Explanation:** Injectivity means no two different inputs share the same output; surjectivity means the function covers the entire codomain; bijection means a perfect one-to-one correspondence between domain and codomain.

Source page: 64. Skill: meaning.

### 4. What does the inverse function of a bijection represent?

**Question:** What is the inverse function of a bijection and when does it exist?

**From notes:** If $f: X \to Y$ is a bijection, its inverse function $f^{-1}: Y \to X$ is defined by $f^{-1}(y) = x \iff f(x) = y$.

**Explanation:** The inverse function swaps the roles of inputs and outputs and exists only if $f$ is bijective, guaranteeing each output comes from exactly one input.

Source page: 67. Skill: meaning.

### 5. How does image and preimage of sets under a function behave with unions and intersections?

**Question:** What are the relations between images and preimages of unions and intersections of subsets under a function f?

**From notes:** For $f: X \to Y$, and subsets $A,B \subset X$, $C,D \subset Y$: (i) $f(A \cap B) \subset f(A) \cap f(B)$, (ii) $f(A \cup B) = f(A) \cup f(B)$, (iii) $A \subset f^{-1}(f(A))$, (iv) $f^{-1}(C \cap D) = f^{-1}(C) \cap f^{-1}(D)$ and (v) $f^{-1}(C \cup D) = f^{-1}(C) \cup f^{-1}(D)$.

**Explanation:** The image of a union equals the union of images, but the image of an intersection is contained in (not necessarily equal to) the intersection of images. Preimages preserve unions and intersections exactly.

Source page: 69. Skill: application.
