# Identical ten-case reviewer comparison

2026-10-31. Ten manually authored function exercises, five valid and five deliberately flawed. Labels and exact narrow arithmetic checks were frozen before paid calls (`cases.json`, `preflight.json`). This evaluates reviewer decisions, not generation quality or source fidelity. Cases cover simplification, injectivity, integer lattice bijection, finite range, surjectivity, function equality, inverse, composition, restricted-domain bijection, and uniqueness.

Both pinned models received exactly the same statements, proposed solutions, order, schema and reviewer prompt, temperature 0, 3000-token output limit. Ground truth, topics and labels were excluded. Each model received the entire ten-case batch in a separate API request. No tools, PDF, prior reviews, corrections or automatic retries. Two paid calls; shared budget $0.05. Total actual usage-based estimated cost $0.007672.

Mini: 9/10 decisions, detected 4/5 flawed cases, falsely accepted case 10. GPT-4.1: 10/10 decisions, detected 5/5 flawed cases, but introduced false algebraic equalities in its explanation of case 1. Decisions are scored automatically; explanations manually examined and concrete defects recorded separately. This is a small selected set and one run, not a statistical model ranking.

Run `run.py mini` then `run.py full` using the research Python environment. Private raw outputs and spending reservations are in ignored `output/`. Re-running an already reserved model is refused. `publish.py` builds the sanitized public result and comparison-data.js without API calls. Production MathPDF is neither imported nor modified.

Rates used: mini $0.40/$0.10/$1.60 per million input/cached/output tokens; GPT-4.1 $2/$0.50/$8. [Official mini documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [GPT-4.1 documentation](https://developers.openai.com/api/docs/models/gpt-4.1). Usage and hashes are preserved in result.json.
