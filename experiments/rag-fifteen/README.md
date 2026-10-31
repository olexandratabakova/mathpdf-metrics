# Theory-only retrieval-backed constrained generation: fifteen tasks

2026-10-31. Public algorithm in [algorithm.md](algorithm.md), rendered as eight steps on the metrics site. Production MathPDF is unchanged.

## What was actually tested

Fifteen handwritten learning goals and topic/domain/prerequisite profiles were paired with real theory-only fragments extracted from the user's main (12).pdf. Marker-based extraction rejects chunks containing Example/Exercise headings. These profiles and expected families were prepared before retrieval/model evaluation; expected labels never enter the model request.

A separate local bank contains forty curated v5 task families, with full generated exemplar questions/solutions, domains, prerequisites and source provenance. Hard topic/domain/prerequisite filters run before a real BM25 lexical ranker (k1=1.2, b=0.75). The top three surviving candidates and theory go to one GPT-4.1 mini request. The model selects an example family and explains the choice; it cannot invent a template or modify math. The program generates fresh admissible numbers from the chosen family and verifies the artifact with the existing mathematical checks. This is **retrieval-backed constrained generation**, not free-form LLM mathematical generation.

The bank and theory share the same original notes lineage. Only the input fragments exclude worked examples. This simulates a theory-only input, but is **not an independent unseen-document benchmark** or a demonstration of automatic syllabus extraction. Queries are in English and use a curated vocabulary. Filters leave only one candidate in two cases. Those are material limits on interpreting retrieval metrics.

## Results

- Expected family at rank one: **14/15**.
- Expected family in top three: **15/15**.
- Model selects the expected compatible family: **15/15**.
- New numerical tasks built and passed supported-family checks: **15/15**.
- **50/50 structured formulas** render with KaTeX, zero fallbacks; desktop and 320/390px checked.
- Three negative controls return no_coverage: unknown topic, missing prerequisites, wrong domain. No model call or task generation is attempted for these controls.

Case 13 matters: lexical rank one is reciprocal_not_onto, while reciprocal_bijection is rank two. The model chooses rank two for the requested bijection with the excluded output. A high search score is not a mathematical validator.

The request for a negative dividend was already present in frozen goal 5, but its first local parameter draw was positive. Before publication a typed parameter constraint was added to preserve that existing request. This did not change retrieval, expected labels or the model plan, and required no repeated API call. Both pre-model and current request hashes, plus this correction, are recorded. Numerical questions are guaranteed to differ from the selected exemplar; repeated local draws, if needed, are deterministic and recorded by seed. They are not paid model retries.

One paid generation-plan call **$0.0078148**, budget $0.02, no retries, no embeddings API, no second LLM reviewer. It does not measure a model's ability to write correct arbitrary proofs: math and learner-facing statements are compiled from vetted families. A template bug is still possible. All fifteen compiled cases were inspected locally; negative constraints, integer preimages and induction transitions are preserved.

## Files and reproduction

`requests.json` contains curated goals, source extraction markers, evaluation labels and parameter constraints. `pipeline.py` builds the bank, filters and ranks, extracts theory, compiles variants and defines controls. `prompt.md` defines model authority. `run.py` freezes search evidence before a single reserved paid call; `publish.py` rebuilds numerical tasks from the stored plan offline and writes result.json, bank.json and rag-data.js. Neither the source PDF nor credentials are published. Full search traces include rejected documents and reasons. Local output/ is ignored.

Run using the existing research Python environment with pypdf/OpenAI/Pydantic/dotenv. The source PDF path is the user-provided Downloads/main (12).pdf. The mathematical engines from previous isolated metrics experiments are imported read-only; no MathPDF application modules or data are instantiated. Re-running the paid slot is refused. Re-running publish.py makes no provider calls.

Tests cover exact frozen retrieval results, domain/prerequisite gating, unsupported family rejection, corrupted formula rejection, preservation of a negative-dividend constraint, and public output provenance. History's 505 cards and earlier experiments are preserved. The algorithm proposes larger-scale or hybrid retrieval as future work; no dense vector retrieval was tested here.

Research context: [Lewis et al., RAG](https://arxiv.org/abs/2005.11401). The mathematical pipeline is our bounded engineering adaptation, not a reproduction of that paper's results. [Official model rates](https://developers.openai.com/api/docs/models/gpt-4.1-mini): $0.40/M input, $0.10/M cached input, $1.60/M output tokens. Usage and hashes are retained in result.json.
