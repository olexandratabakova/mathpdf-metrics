# GPT-4.1 mini generator and separate mini reviewer

2026-10-31. Four new tasks from main (12).pdf, original pages 63–66. Frozen generator and reviewer prompts copied from review-four. Three separate requests: generate, blind statement check, solution audit. Same pinned mini model throughout; audit receives blind results. No corrections or retries. Total usage-based cost $0.0150532; budget $0.035.

Model accepts three, requests revision of one. Local checks identify conflicting domain in task 3 and wrong rational preimage in blind review of task 4; full original decisions preserved in result.json. New tasks preclude a controlled accuracy comparison with the earlier stronger reviewer. Production MathPDF unchanged.

Run experiment.py sequentially with --stage generate/blind/audit, --source PDF, --mathpdf-source read-only checkout, --execute. Each stage refuses duplicate paid calls. Private output ignored. publish_result.py publishes sanitized outputs only.
