# Wildflower · ordinary generation baseline

October 31, 2026 · **60 flashcards + 40 practice problems** · [Open the study](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=wildflower)

This experiment measures regular MathPDF generation, without RAG, a numerical template bank, symbolic answer construction or automatic repair. Production MathPDF, its prompts and user data were not modified.

## Setup

| Topic | Original PDF pages | Cards | Problems | Difficulty |
| --- | --- | ---: | ---: | ---: |
| Sets | 4–7 | 15 | 10 | 3 |
| Mathematical Induction | 14–19 | 15 | 10 | 3 |
| Numbers | 22–27 | 15 | 10 | 3 |
| Functions | 63–70 | 15 | 10 | 3 |

Source: the supplied `main (13).pdf`, 74 pages. Only these selected pages were extracted and sent; the full PDF and full extracted notes are not published. The source hash and selection hashes are retained in [result.json](result.json).

The read-only MathPDF checkout is commit `a3071436f158b09eb783e08fe2a8f98e69f985ec`, verified against its GitHub main branch at execution time. The test uses its actual `load_prompts`, `set_response_format`, item expansion, citation validation and exact-question duplicate guard. The default generator is `gpt-4.1-mini`; responses resolved to the recorded snapshot in each manifest. No user comment or auxiliary context is added. Eight generation calls correspond to four 15-card sets and four 10-problem sets. The experiment runs outside the app server, queue, quotas, account sessions and database.

Frozen prompt text is under [generator-prompts/](generator-prompts/). Request prompt hashes use decoded text with normalized newlines, as `load_prompts` does. Original compact responses, usage and expanded items remain in ignored local output; published evidence preserves the expanded content, including mistakes.

## Flashcard results

The existing evaluator functions, prompt files, schemas and aggregation definitions are reused. The configured judge is **gpt-4o-mini**, temperature 0. A separate budgeted Responses API transport replaces the evaluator's retrying Chat Completions transport. It caches completed calls and never automatically repeats a failed/reserved call. This transport change is disclosed; the test is not claimed to reproduce every historical provider setting.

| Metric | Sets | Induction | Numbers | Functions | Weighted total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Self-contained | 93.3% | 53.3% | 86.7% | 86.7% | **80.0%** |
| Source faithfulness | 88.9% | 80.7% | 89.4% | 79.7% | **84.7%** |
| Atomic | 100% | 100% | 100% | 86.7% | **96.7%** |
| Topic coverage | 93.3% | 86.7% | 66.7% | 86.7% | **83.3%** |
| Involved in duplicate pairs | 0% | 0% | 46.7% | 0% | **11.7%** |
| Answer leakage | 0% | 0% | 0% | 0% | **0%** |
| Understanding | 93.3% | 93.3% | 100% | 100% | **96.7%** |
| Trivial | 0% | 0% | 0% | 0% | **0%** |

All requested counts match. Difficulty-order Spearman coefficients and answer-length/type distributions are retained per topic in the JSON and displayed on the detail page. There is no pooled difficulty-order correlation across independent sets.

Definitions are unchanged: self-contained passes only when `understandable` is true and `whats_missing` is empty; blind-answer agreement is stored separately. Faithfulness is the mean per-card supported-claim ratio, with the original empty-claim behavior retained. Quote verification is stored independently and does not override model support labels. Coverage uses source-derived concepts. Duplicates use `text-embedding-3-small`, cosine threshold 0.85, and the share of cards involved in any qualifying pair within a topic. Seven Numbers cards are involved; this is an embedding signal, not seven independently proven redundant cards. Scores are weighted by card count.

**These scores are fallible judge outputs.** For example, Sets card 3 and Functions card 13 receive matching blind answers but fail self-containedness because the judge demands definitions/conditions which are precisely what the question asks the learner to recall. Those original flags and the resulting aggregate remain unchanged, with local commentary shown separately.

## Problem audit and contradictions

The configured low-cost judge audits all forty original problems in four calls. It checks self-containedness, statements, solutions, completeness, source-supported methods, substantive novelty and formatting. Flashcard atomicity is not substituted for proof completeness.

| Topic | Accept | Revise | Reject |
| --- | ---: | ---: | ---: |
| Sets | 10 | 0 | 0 |
| Induction | 8 | 0 | 2 |
| Numbers | 9 | 0 | 1 |
| Functions | 9 | 0 | 1 |
| Total | **36** | **0** | **4** |

**36/40 is not a mathematical correctness rate.** Targeted local checks expose false approvals and false rejections:

- Sets 5 says `{1}` is not a subset of `{1,{1}}`, although it is even a proper subset. The judge accepts it.
- Sets 10 provides an invalid counterexample to a membership/subset claim. The judge accepts it.
- Induction 2 asks to prove `12 | n³−n` for every positive integer. At `n=2`, the value is 6. The judge accepts it.
- Induction 6 uses a bound greater than 1 to establish a bound of 1 and includes a false equality. The judge accepts it.
- Functions 5 requests surjectivity on `Z²` for `(m,n) ↦ (2m−n,m+4n)`. Target `(1,0)` has unique rational preimage `(4/9,−1/9)`, so the requested positive claim is false. This time the judge rejects it.
- Induction 3 has the correct sum `S_n=3n²` and a valid induction; the judge rejects it while suggesting the very same formula as the correction.
- Induction 8 explicitly asks for a counterexample, supplies a valid one, and is nevertheless rejected.
- Numbers 3 gives a standard lowest-terms proof of irrationality of `sqrt(3)`; the judge incorrectly demands an extra even/even case.

The judge also labels all forty problems substantively novel. That label is not reliable: several items simply ask for source definitions, familiar proofs or substitutions. Original model decisions are preserved rather than rewritten to agree with local review.

See [local-checks.json](local-checks.json) and [check_local.py](check_local.py) for item hashes, narrow witnesses and the distinction between generation errors, incomplete statements and reviewer mistakes. These checks do **not** certify all unlisted tasks.

## Formula fidelity

The browser renders 45 standalone math blocks across the 100 items with zero fallback errors. Inline mathematical content is also rendered; this count is specifically standalone blocks. Mobile/desktop checks at 320, 390 and 1440 pixels have no document overflow or JavaScript errors. [Rendering record](rendering-checks.json).

Zero fallbacks is not semantic fidelity: Induction **card 15** says `2n × 2n` instead of `2^n × 2^n`. For literal `n=3`, a 6×6 board with one square removed has 35 squares, so cannot be tiled by area-three trominoes. Its front changed the theorem even though it displays successfully. Some induction problem fronts also refer to an identity which appears only on the answer side. These original defects are kept for inspection.

## Cost and reproduction

Usage-based total: **$0.14484367** — generation **$0.07707920**, evaluation and embeddings **$0.06776447**. There are 216 completed paid generation/evaluation/embedding calls, with no automatic retries. Input-token counting requests precede the eight PDF generation calls. The local reservation cap is **$0.75**, not an account-wide billing limit or a balance audit.

Rates used per million tokens: generator input/cached/output `0.40/0.10/1.60`, judge `0.15/0.075/0.60`, embeddings `0.02`. Model references: [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini). All usage and cost calculations are retained in the public result.

The runner uses the existing metrics Python environment, and reads provider-only dependencies from the MathPDF checkout without installing into or changing that project. Supply your own credentials in the ignored metrics `.env`. Adjust the runner's source/check-out paths for another machine. `--execute` makes paid calls; without it, the runner only prints its plan.

```sh
python -B experiments/wildflower/run.py --stage generate
python -B experiments/wildflower/run.py --stage generate --execute
python -B experiments/wildflower/run.py --stage evaluate --execute
python -B experiments/wildflower/publish.py
python -B experiments/wildflower/check_local.py
python -B experiments/wildflower/publish.py
python tools/build_experiment_catalog.py
```

The ledger makes the run resumable using completed outputs and prevents automatic repeats of uncertain calls. Do not delete a ledger to retry a charge you have not checked. Local checks and publishing need no API calls. [cards_wildflower.csv](cards_wildflower.csv) uses the original per-card CSV import fields; the JSON retains full text and claim-level evidence.

This is a fresh four-topic baseline, not a paired A/B comparison with historical v1–v4. Historical prompts/judge settings were not fully retained, and source versions/counts/page ranges differ. The historical 505-card snapshot and browser-local user edits are preserved separately.
