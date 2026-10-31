# Real model generation: 40 near +15 changed-condition tasks, checked with SymPy

2026-10-31. Unlike earlier v5 runs, these are **actual model-authored questions, formulas, formal records and worked solutions**, not program-rendered template answers. GPT-4.1 mini received text excerpts of the user's main (12).pdf. It received no program-computed answer key. SymPy 1.14.0 recomputes bounded formal contracts; **no second LLM reviews or repairs them**. Production MathPDF and its environments are unchanged.

## Main results

| Group | Tasks | Formal computation confirmed | Partial | Formal record refuted | Unsupported |
|---|---:|---:|---:|---:|---:|
| Close numerical analogs requested | 40 | 13 | 21 | 1 | 5 |
| Changed conditions requested | 15 | 3 | 9 | 0 | 3 |
| Total | 55 | 16 | 30 | 1 | 8 |

These are **coverage outcomes, not correctness/accuracy scores**. Confirmed is limited to encoded computational claims and parseable equality steps; it does not prove alignment with prose, source fidelity, novelty, or complete pedagogical proof. Partial includes arithmetic with an LLM-selected combinatorial formula, a sum identity without a verified induction proof, or unparsed intermediate steps. Unsupported never implies approval. A refuted formal record may not represent the prose faithfully.

Near7 demonstrates that distinction: the learner-facing factorial sum is correct, but the model encoded a different shifted-index sum. SymPy correctly refutes the encoding; transferring that result to the original prose would be a false rejection. Near21 encodes only `32` for an entire binomial sum, so its arithmetic check is tautological and remains partial. Four source references point to page 32, which was not among the supplied excerpts; none were silently corrected.

Separate local analysis identifies four mathematical defects in unsupported tasks: near39's birthday guarantee, near40's seven-points/nine-cells bound, transfer4's false factorial assertion, and transfer14's false claim about injectivity of the first composition factor. **Those are not SymPy findings.** Exact specific counterexamples are in local_checks.py/local-checks.json, with clear limits. The composition argument is explained directly in manual-notes.json. Original generator outputs and library verdicts remain unchanged.

Changed-condition compliance is also imperfect: transfer1 repeats near3 exactly; transfer11 does not instantiate the requested extraneous-root scenario. No claim that all fifteen are genuinely new unseen conditions. Source copies and weak novelty remain in parts of the near batch.

## Generation attempts and cost

Two first pilots (40+15) copied too much source material and broke the formal language contract. They are preserved in pilots.json and excluded from the main 55, not erased. Two more generation calls used explicit kind allocations and fifteen changed-condition scenarios. All numerical values and final answers were still produced by the model. This is a generation iteration, not paid mathematical review or correction.

Four paid generation calls total **$0.0700304**, shared cap $0.12. Main 55 cost $0.0353724; discarded pilots cost $0.034658. Actual usage is recorded. No paid retry of any reserved slot, no fifth call, no LLM checker. Every request writes its cost reservation before generation. Original source PDF and key are excluded from publication.

## Checker design and limits

Supported adapters: expressions with original domains, equation solution sets, explicit finite integer sets, small matrices, sums, equality-form induction assertions, bounded linear congruences, counting arithmetic, selected one-variable real function properties, and real inequalities. General logical and pigeonhole proofs are unsupported. Matrix capabilities in SymPy exceed the particular one-variable function adapter, so an unsupported Z² map must not be read as a library-wide limitation.

Model expressions pass a bounded AST interpreter: no `eval`, `sympify`, `parse_expr`, attributes, arbitrary functions or comprehensions. Only allowlisted exact arithmetic/functions and named symbols. Each task runs in a separate process with an eight-second wall-time limit. Domain poles are retained even if algebraic simplification cancels them. Unknown results, parsing failures and time limits never turn green. Nonparseable optional steps downgrade an otherwise confirmed computation to partial; they are not silently translated or discarded as proved. Adapter tests include the known wrong simplification, a codomain error, excluded denominator roots, domain-dependent square roots, complete non-coprime congruence classes, proof/partial handling and code-like syntax rejection.

Install the library **only in this experiment** from its directory:

```powershell
python -m pip install --target .deps -r requirements.txt
```

The .deps directory is ignored; production MathPDF dependencies were not changed. run.py additionally needs the existing research OpenAI/Pydantic/pypdf/dotenv environment. Run generation slots near, transfer, near2, transfer2 at most once each. Near2's original parsed response was recovered offline after citation validation rejected four references; the invalid citations remain documented. `verifier.py` checks near2/transfer2 locally and writes output/checks.json. `local_checks.py` provides exact narrow counterexamples. `publish.py` builds sanitized public data without API calls. Tests skip SymPy-specific checks on a clean checkout unless the isolated dependencies are installed.

Browser QA checks all 55 questions/solutions, zero math fallbacks, no JavaScript errors, topic disclosures, 320/390px mobile widths and preservation of 505 historical cards and earlier experiments. Zero renderer errors do not prove mathematical correctness or ideal typography.

References: [SymPy solving guidance](https://docs.sympy.org/latest/guides/solving/solving-guidance.html), [Solveset and explicit domains](https://docs.sympy.org/latest/modules/solvers/solveset.html), [official mini rates](https://developers.openai.com/api/docs/models/gpt-4.1-mini). Rates used per million input/cached/output tokens: $0.40/$0.10/$1.60. JSON evidence includes library/version, exact task records, unchanged verdicts, costs, source/prompt/engine hashes and separate local notes.
