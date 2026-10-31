# V5 across seven topics: seventy numerical variants

2026-10-31. An isolated extension of the closed-template v5 experiment. Production MathPDF, its prompts, persisted data and running service are unchanged.

**70 tasks, 40 template families, seven topics with ten tasks each.** Sets, induction, numbers/divisibility, congruences, counting and pigeonhole each use five curated families with two distinct parameter sets. Functions reuse ten v5 families with a new seed. These are numerical variants, not seventy independent mathematical ideas or unconstrained model-generated tasks.

Source: user-provided main (12).pdf (69 pages). Curated methods reference sets pp. 5–7, induction pp. 14–17, numbers pp. 27–31, congruences pp. 33–34, counting pp. 38–43, pigeonhole pp. 60–62, functions pp. 63–66. Citations identify supporting methods, not literal quotations of constructed formulas. The source PDF is never published or sent to the planning model.

One GPT-4.1 mini request chooses **only topic order**. All titles, questions, coefficients, domains, formulas, answers and proofs are deterministic program output. Seed 50770. No second model, reviewer, repair call or paid retry. Actual usage cost **$0.0002144**, cap $0.01. Full plan, usage, input/prompt/engine hashes and source SHA-256 are public in result.json; credentials and private reservation ledger remain ignored.

New families:

- Sets: union/intersection/difference, relative complement, Cartesian product, power-set enumeration, concrete distributivity.
- Induction: scaled sum of squares, odd-number sum, factorial sum, cubic divisibility, reciprocal-square upper bound. Positive scale is checked; base cases and symbolic polynomial/rational transition identities are checked exactly. Consecutive-integer parity handles divisibility; positivity handles inequality. First few numerical examples are not treated as universal proof.
- Numbers/divisibility: Euclidean division (including a negative dividend), gcd, Bezout coefficients, prime factorization, base conversion.
- Congruences: testing congruence, modular exponentiation, all solutions of a linear congruence (including no solutions), parity obstruction, clock arithmetic.
- Counting: routes with explicit mutually exclusive paths, permutations, unordered committees, nonnegative integer triples, binomial coefficients.
- Pigeonhole: sharp birthday occupancy, minimal occupancy threshold, common remainders, square-grid distance bound, repunits with modulus coprime to ten.

Checks use exact integers/Fractions, independent enumerations, polynomial multiplication, inverse-matrix products and constructive witnesses. Pigeonhole and induction explanations are hand-authored source-supported proofs, not Lean/Coq certificates. Artifact checks additionally reject changed formulas or statements, but recomputing the same builder alone would not detect a mathematical bug in that builder. Tests and local review complement that structural check; template bugs remain possible.

Results: **70/70 supported artifacts passed their program checks; 201/201 structured formula blocks rendered with KaTeX**, zero math fallbacks, zero raw TeX in prose. Desktop, 320/390px mobile widths, direct route/reload, topic/solution disclosure and preservation of earlier experiments/505 historical cards checked in Chromium. Screenshots of induction, sets and repunits inspected locally. Source citation for factorization was corrected to Theorem 6.16 before publication by reprocessing the stored plan offline; no extra API call or mathematical answer replacement.

Run `run.py` once with the research Python environment; repeat calls are refused by the prewritten spending reservation. `--finalize-only` rebuilds from the stored response offline. `publish.py` validates all artifacts and creates result.json/seventy-data.js without provider calls. Unsupported task families, invalid integer conventions, invalid moduli, non-coprime repunit moduli and other out-of-scope parameters fail closed. Historical v1–v4 flashcard scores and previous v5 tests remain separate.

This is a bounded construction/validation test, not an estimate of arbitrary generation accuracy, source extraction reliability, substantive novelty or teaching quality. Prompt v5 coordinates templates; a prompt alone cannot provide these guarantees. [Official mini rate reference](https://developers.openai.com/api/docs/models/gpt-4.1-mini): $0.40/M input, $0.10/M cached input, $1.60/M output.
