# Briefleaf · compressed-prompt 20-card pilot

Status: generation completed; 20 cards; no model evaluator, as requested. Total recorded cost $0.02531920, including an incomplete 4,250-token first call; four successful calls use an 8,000-token cap. See cards.md and result.json. Not ready to promote: corrupted PDF glyphs, formula defects and incomplete explanations remain.

Candidate prompt stack: system.md + flashcards.md, 464 whitespace-separated words versus 6,101 across the five corresponding Wildflower files (92.4% shorter). This is a focused flashcard/level-3 replacement, not a full replacement for every problem mode and difficulty. Long technical examples and repeated instructions are removed; behavior preservation requires the experiment.

Plan: five flashcards each for Sets (4–7), Induction (14–19), Numbers (22–27), Functions (63–70), from local main (13).pdf. Same gpt-4.1-mini generator, difficulty 3, existing schema, gpt-4o-mini original evaluator and separate revised self-containment diagnostic as the Clearleaf pilot. Local reservation cap $0.15; no automatic retries. Credentials are read from the ignored Acadence Metrics .env, never published.

New style: short self-contained question; direct source answer first; essential reasoning below. Preserve source/AI separation. Inferred answers begin explanation; the existing renderer still places source content first. No production prompt or schema changes.

Run from the metrics workspace with its dependency environment:

```
python -B mathpdf-metrics/experiments/briefleaf/run.py --stage generate
python -B mathpdf-metrics/experiments/briefleaf/run.py --stage generate --execute
python -B mathpdf-metrics/experiments/briefleaf/run.py --stage evaluate --execute
```

Inspect all 20 outputs for correctness, single target, direct answer, concision, source citation, duplication and complete reasoning before publishing findings. Retain original judge scores. Compare descriptively with the original 20-card Clearleaf pilot; different targets and changed full prompt stack prevent attributing differences to brevity alone. Do not copy old local findings to this sample.
