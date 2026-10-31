# Clearleaf · 60-card continuation

[Study](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=clearleaf-sixty) · [Full evidence](result.json) · [CSV](cards_clearleaf_sixty.csv) · [Original 20-card pilot](../clearleaf/README.md)

The first twenty Clearleaf cards are unchanged. Forty cards were added: ten per topic, giving **15 each in Sets, Induction, Numbers and Functions**. The complete sixty-card set is evaluated against Wildflower’s sixty cards with the **original evaluator only**.

## Results

| Original metric | Wildflower 60 | Clearleaf 60 | Change |
| --- | ---: | ---: | ---: |
| Self-contained | 80.0% | 78.3% | −1.7 pp |
| Source faithfulness | 84.7% | 90.8% | +6.1 pp |
| Atomic | 96.7% | 88.3% | −8.3 pp |
| Coverage | 83.3% | 83.1% | −0.2 pp |
| Embedding duplicate involvement | 11.7% | 11.7% | 0.0 pp |
| Answer leakage | 0% | 0% | 0.0 pp |
| Understanding | 96.7% | 95.0% | −1.7 pp |
| Trivial | 0% | 0% | 0.0 pp |

**Assessment:** mixed. The judge finds better source support, but atomicity is lower and duplicate signals do not improve. Keep the candidate experimental. These are fallible model/embedding measures, not mathematical correctness rates.

## What is controlled

The source PDF hash, original selected pages, 15 cards per topic, difficulty 3, generator/judge model aliases, original evaluation prompts, temperature and duplicate threshold match the baseline. Source: the supplied `main (13).pdf`; topic pages remain 4–7, 14–19, 22–27 and 63–70. Production MathPDF was not changed.

The [Clearleaf core prompt](../clearleaf/flashcards.md) is unchanged. Continuation requests include the five existing cards and ask for ten distinct additional targets. Wildflower used a single fifteen-card generation per topic; Clearleaf used five plus ten with prior-card context. **Equal size removes the count imbalance but not this batching/context confound.** This is one run per condition, not randomized or paired by preassigned learning targets.

The complete fifteen-card topic sets get new batch-property, difficulty, coverage and duplicate checks. Sixty original per-card checks plus four material/concept calls are reused only when the full request hash matches. The previous revised-rubric 90% diagnostic and calibration are not used in this comparison.

## Local findings

All forty added cards were inspected by the coding assistant; this is not independent expert verification. Item hashes bind the findings to the actual responses in [local-review.json](local-review.json).

- Six added cards combine independent learning targets, including domain/codomain/range and sum/product notation.
- Two clear semantic repeats remain: Induction 15 repeats Induction 5; Numbers 13 repeats Numbers 4. Other cards partially overlap earlier broad cards. Exact question fingerprints do not detect these overlaps.
- The graph-reflection card omits the real-valued scope of the source exercise. An identity-composition answer is put under From notes although the cited page poses it as a question.
- The chessboard target is now present: its front correctly says “2 to the power n by 2 to the power n”. This one correct occurrence does not establish a general fix. Rendered output is retained as generated.
- The initial twenty cards, including their previously identified defects, were neither repaired nor removed.

## Cost and reproduction

**Additional cost: $0.07336855. Clearleaf cumulative cost: $0.12775973**, including the earlier pilot. This extension has 144 completed new paid calls and 64 zero-new-cost cache reuses. Its local reservation cap is $0.20. No automatic paid retries or new baseline generation. Wildflower’s full run also included forty problems, so its total cost is not an equivalent card-only cost comparison.

```sh
python -B experiments/clearleaf-sixty/run.py --stage generate
python -B experiments/clearleaf-sixty/run.py --stage generate --execute
python -B experiments/clearleaf-sixty/run.py --stage evaluate --execute
python -B experiments/clearleaf-sixty/publish.py
python tools/build_experiment_catalog.py
```

`--execute` makes paid calls. Supply your own credentials and local source/check-out paths. Exact cache reuse needs the pilot’s ignored local call outputs; without those, evaluation may make additional calls within the same cap. New generations need fresh local review; stale item hashes prevent publishing old findings against changed cards. Full PDFs, extracted source notes and API credentials are excluded from publication.
