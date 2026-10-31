# Clearleaf · 20-card pilot

[Study](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=clearleaf) · [Candidate prompt](flashcards.md) · [Full record](result.json) · [Metrics CSV](cards_clearleaf.csv)

**Decision: not ready to promote.** Five multi-target cards, one wrong citation and an incomplete requested explanation remain. Production MathPDF was not changed.

## Setup

- Five cards each: Sets pages 4–7, Induction 14–19, Numbers 22–27, Functions 63–70 of the supplied `main (13).pdf`.
- Difficulty 3; generator `gpt-4.1-mini`; configured judge `gpt-4o-mini`.
- Only `flashcards.md` changed. Other generator instructions, schema and expansion match the read-only MathPDF checkout used by Wildflower (`a3071436f158b09eb783e08fe2a8f98e69f985ec`). Frozen instructions are under `generator-prompts/`.
- No RAG, repairs, task generation or fresh baseline generation. Four generation calls produced exactly twenty cards.

The candidate emphasizes one learning target, explicit givens, faithful formula-to-word conversion, source/explanation separation and reduced paraphrasing.

## Results

| Measure | Result | Meaning |
| --- | ---: | --- |
| Original judge self-contained | 14/20 · 70% | Unchanged evaluator rubric |
| Original source faithfulness | 83.6% | Mean supported-claim ratio; not mathematical accuracy |
| Original judge atomicity | 14/20 · 70% | One assessable idea per card |
| Revised self-contained diagnostic | 18/20 · 90% | Separate rubric; never substituted into the original score |
| Local self-contained inspection | 18/20 | Coding-assistant inspection, not independent expert validation |
| Local atomicity inspection | 15/20 | Five cards combine independent targets |
| Exact page citation defects found | 1 | Numbers 5 cites page 27; its theorem is on page 26 |
| Incomplete explanation found | 1 | Numbers 2 asks why sqrt(2) is irrational but points to an earlier proof |

The original evaluator also reports 0% leakage, 0% triviality, 0% within-topic embedding duplicates and 49.4% coverage. Five cards per topic cannot be compared with Wildflower’s fifteen-card topic coverage/duplicate scores as equal-size runs. Per-topic metrics and claim-level evidence are retained in JSON.

The revised rubric stops treating the requested definition/conditions as missing givens. It matches **8/8 known labelled fronts**, but these overlap the examples in its instructions: this checks instruction compliance, not held-out accuracy. It is not a calibrated correctness guarantee.

## Concrete findings

- Functions 2 asks for three definitions; Functions 4 combines two composition proofs; Functions 5 lists six image/preimage properties.
- Induction 2 combines divisibility and its use in induction. Numbers 2 combines existence and irrationality and leaves the latter unexplained.
- Numbers 5 has the wrong exact citation, even though the theorem is elsewhere in the selected pages.
- Several explanations still restate source content. Sets 4 encodes punctuation/“and” as inline math.
- No critical mathematical error was found in this small local inspection. The old chessboard target was not generated; therefore **the 2^n→2n regression remains untested**. A subset-count card does correctly say “2 to the power n”.

Original generated cards and judge decisions are unchanged. Local notes are tied to item hashes; publishing new generations with these notes is rejected until the new outputs are reviewed.

## Cost and reproduction

Total usage-based cost: **$0.05439118**, against a local **$0.15** reservation cap. There are **112 completed paid calls**: 4 generation, 80 original metric/embedding calls, and 28 revised self-containment diagnostics including the 8 controls. No automatic paid retries. This is not an account balance audit.

The runner reuses Wildflower’s isolated budget transport and existing dependency environments. It does not modify Wildflower or MathPDF. Full PDFs, extracted source notes and credentials are excluded from public output. Supply your own source path/credentials; `--execute` makes paid calls.

```sh
python -B experiments/clearleaf/run.py --stage generate
python -B experiments/clearleaf/run.py --stage generate --execute
python -B experiments/clearleaf/run.py --stage evaluate --execute
python -B experiments/clearleaf/publish.py
python tools/build_experiment_catalog.py
```

`local-review-inputs.json` freezes the inspected responses. Fresh model responses require fresh local review before publication. The site retains the original metric series alongside the revised diagnostic. **Twenty candidate cards versus sixty old baseline cards is not a paired A/B test or evidence of a causal gain.**
