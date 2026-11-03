# Briefleaf refined · 20-card experiment

Generation and original evaluator: gpt-4.1-mini and gpt-4o-mini, respectively. Five cards each for Sets pages 4–7, Induction 14–19, Numbers 22–27 and Functions 63–70 of the same local main (13).pdf. Difficulty 3, unchanged schema, full formula-guide.md and math-patterns.md. No production edits, repair calls or baseline reruns. Budget cap $0.15, cached completed calls, no automatic retries.

## Prompt changes and motivation

- Prior multi-target cards: explicit negative examples and one independent target; distinguish necessary definition conditions from independent questions.
- Redundant or absent reasoning: state when explanation is empty versus required, and show the actual inferential chain rather than describe a proof.
- Formula/glyph/JSON corruption: full technical context retained; explicitly prohibit prose/serialized JSON inside math, raw TeX in prose/titles and ambiguous powers on fronts.
- Overstated proof impossibility: distinguish one failed estimate from impossibility of the method; require stronger bounds or an accurate local diagnosis.
- Recall labelled meaning: classify actual reasoning; two applied/condition/error targets and at most one recall per five-card set.
- Source-role confusion: preserve source excerpts and exact citations, put derived direct answers in explanation when absent from the source.

## Evaluation

Original evaluator prompts/functions unchanged. Higher transport caps for batch properties/difficulty prevent avoidable truncation. Original self-containment and revised diagnostic remain separate; eight overlapping known controls only check revised-instruction compliance, not held-out calibration. Local inspection is separate from model scores. Different generated targets and one run per version do not establish causal gains or a general correctness percentage.

Run run.py --stage generate --execute, then run.py --stage evaluate --execute. Credentials come from the ignored project .env. Never publish source PDF, keys or full input payloads.

## Recorded result

All 20 cards generated and evaluated; 112 paid calls completed, no retries. Total cost $0.05027273: generation $0.02251200, evaluation/embeddings/diagnostics $0.02776073. Original self-containment 80%, source faithfulness 88.4%, atomicity 75%, embedding duplicate involvement 0%, front leakage 0%. Revised self-containment diagnostic 18/20, kept separate. Average question length 18.25 whitespace-separated words. These metrics are model signals, not correctness percentages.

Strict KaTeX parsing passes all 76 typed fragments; heuristic inspection flags raw mathematical strings in seven cards. This does not establish full rendered fidelity. Local review finds incomplete induction proofs, raw notation, skill-quota violations and a wrong page citation (Numbers 5: page 26 rather than 27). Source page 16 itself says direct induction is impossible; verbatim transcription and the narrower intended mathematical framing conflict here. Original outputs and local findings are preserved in cards.md, result.json, local-review.json and rendering-checks.json. Not ready to promote.

The old 20-card Clearleaf pilot scored 70% self-contained, 83.6% faithfulness and 70% atomicity with the original evaluator. The new sample is descriptively higher on these measures, but different learning targets/full instructions prevent claiming a paired improvement. No original-evaluator scores exist for the preceding two Briefleaf runs, so they are not assigned inferred percentages.
