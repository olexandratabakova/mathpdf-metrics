# Generate → review → repair → fresh review: 15 tasks

2026-10-31. Real four-request experiment, not handwritten output. Source: main (12).pdf, original pages 63–66. Generator prompts frozen from the earlier isolated candidate, count 15, level 3. No MathPDF production modifications.

1. GPT-4.1 mini generates 15 complete structured problems from selected PDF pages.
2. GPT-4.1 reviews all original statements and solutions with the source.
3. Mini receives originals and the report for one repair pass. The prompt requires checking criticisms and preserving correct items.
4. GPT-4.1 receives only the repaired set and source in a fresh request, with the same review prompt, not the earlier report or originals.

Budget $0.20, actual usage-based cost **$0.0640096**. Four paid calls, no retries, no second repair. All stage reservations and raw artifacts stay in ignored output/. Reviewer is the same model in separate contexts, not an independent mathematical authority. Local analysis was not supplied to any model.

Model accepts: **14/15 → 15/15**. Local mathematical review: **14/15 → 14/15**. Task 13 retains an invalid codomain: h(2)=2 but 2 is excluded. Target 1 is also unattainable. Both reviews accept it. Task 9 originally correctly proves injectivity; reviewer falsely rejects, providing distinct outputs as if they refuted injectivity. Mini unnecessarily replaces its map with the source's own example. All 15 serialized items change, primarily because repair converts every explicit math/latex object to plain strings. This is not 15 successful corrections.

Explicit mathematical objects **124 → 0**; standalone rendered formula blocks **25 → 0**. Shared MathPDF renderer gives zero technical math fallbacks both times due partly to legacy recovery. This does not establish improved formula typography or correctness. Local Chromium desktop/mobile checks and screenshots confirm rendering; source and repaired outputs are preserved unmodified. `rendering-checks.json` records the counts.

`local-review.json` records mathematical review for every before/after pair; `local_checks.py` provides narrow exact arithmetic checks. These do not form a general symbolic validator. Several tasks copy source definitions/theorems or change only constants; novelty and difficulty are not established. One sample is not a statistical reliability estimate.

Run experiment.py sequentially with --stage generate/review/fix/final, --source PDF, --mathpdf-source read-only checkout, --execute. The ledger refuses repeated stages. `publish.py` produces sanitized result.json and cycle-data.js without API calls. Input PDF, base64 request payloads and key are never published. Stage tasks, hashes, exact outputs and usage remain in public result.json for audit.

Rates per million input/cached/output tokens: mini $0.40/$0.10/$1.60; GPT-4.1 $2/$0.50/$8. [Mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [GPT-4.1](https://developers.openai.com/api/docs/models/gpt-4.1).
