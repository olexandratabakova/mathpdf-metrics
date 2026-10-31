# MathPDF · Quality Lab

A public notebook for mathematical task generation, formula rendering and flashcard evaluation. **The interface and editorial explanations are in English.** Original model responses are preserved unchanged in the evidence files.

**[Explore the experiments](https://olexandratabakova.github.io/mathpdf-metrics/#reviews)** · [Flashcard metrics](https://olexandratabakova.github.io/mathpdf-metrics/#overview) · [Methods & guide](https://olexandratabakova.github.io/mathpdf-metrics/#guide)

The overview gives each attempt a short description, a chart explaining its scope and one main finding. Each study has a separate detail page with its method, limitations, tasks and original evidence. Opening the site makes **no AI-provider calls** and spends no API credit. This repository is separate from production MathPDF.

## Experiment map

| Attempt | Method / sample | Main finding | Recorded API cost |
| --- | --- | --- | ---: |
| [01 · GPT-4.1 reviewer](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=review-four) | Mini generation → independent solving → GPT-4.1 audit; 4 tasks | All approved; an algebra error was missed | $0.048080 |
| [02 · Mini reviewer](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=review-mini-four) | Separate mini calls; 4 new tasks | False bijection detected; domain conflict missed | $0.015053 |
| [03 · Same ten controls](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=compare-ten) | Two reviewers; 5 valid + 5 flawed solutions | Mini 9/10, GPT-4.1 10/10 decisions; a full-model explanation still had errors | $0.007672 |
| [04 · Generate → review → repair](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=cycle-fifteen) | One repair cycle; 15 tasks | Approval 14→15; local mathematical correctness 14→14; structured math regressed | $0.064010 |
| [05 · Task V5 pilot](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=v5-parameterized) | Code owns parameters, formulas and solutions; 10 variants | All supported-family checks passed | $0.000656 |
| [06 · Task V5 expansion](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=v5-seventy) | 70 variants, 40 families, 7 topics | Wider controlled coverage, not free-form generation accuracy | $0.000214 |
| [07 · SymPy](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=sympy-55) | Actual LLM generation; 40 close + 15 changed-condition requests | 16 formal records confirmed, 30 partial, 1 encoding refuted, 8 unsupported | $0.070030 |
| [08 · Theory-only RAG](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=rag-fifteen) | 15 goals → retrieval → family choice → compilation | Expected top-1 14/15, top-3 15/15; supported variants passed checks | $0.007815 |
| [09 · Two-PDF RAG](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=rag-hundred) | 50 goals, 50 families, 100 numeric variants | 98 initially admitted; 100 after a retrieval fix and short retry | $0.027301 |
| [10 · Wildflower](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=wildflower) | Ordinary site generation: 60 cards + 40 problems | Cards: 80% self-contained, 84.7% faithfulness; task judge approval is contradicted by local findings | $0.144844 |

Costs describe these recorded runs, not current price quotes or forecasts. The SymPy total includes two exploratory pilots; the main 55-task sample cost $0.0353724. Requests, outputs, usage and limitations are retained under [experiments/](experiments/).

## Latest baseline: Wildflower

[Wildflower study](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=wildflower) · [Method and reproduction](experiments/wildflower/README.md) · [60-card metrics CSV](experiments/wildflower/cards_wildflower.csv)

Four topics at difficulty 3: Sets, Mathematical Induction, Numbers and Functions. Unchanged site prompts and normal model generation produce 15 cards and 10 problems per topic. No RAG, code-owned mathematical templates or repair is applied. The original card evaluator functions and prompts are reused with the configured `gpt-4o-mini` judge.

Card scores: **80.0% self-contained**, **84.7% source faithfulness**, **96.7% atomic**, **83.3% coverage**, **11.7% involved in within-topic embedding duplicate pairs**. These are judge/embedding signals, not verified truth. The task reviewer accepts 36/40, but local checks expose missed errors and three erroneous rejections of mathematically valid solutions. The original approvals and contradictions are preserved separately. This is a new baseline, not a paired comparison with v1–v4. Total usage-based cost: approximately **$0.145**.

## Methods used

### Model generation and review

Separate calls generate tasks, solve them without seeing the proposed answer, and audit the result. The controlled comparison gives both reviewers the same labelled cases. The repair experiment adds a revision call and fresh final audit. Approval can rise without improving mathematical correctness; reviewers can also introduce erroneous explanations.

### Controlled parameterized families — task V5

The model selects supported families or their order. Python chooses admissible numbers and builds the statement, structured formulas and solution from one representation. Family-specific checks verify the construction. This controls numerical variation within supported families; it does not cover arbitrary new mathematical structures.

### Symbolic verification — SymPy

An LLM supplies prose and a machine-readable mathematical record. A SymPy adapter checks supported calculations and encoded steps. Connecting the encoding to the prose remains a separate obligation. A refuted encoding can coexist with correct prose; a confirmed calculation can coexist with a flawed task. Partial and unsupported results are not approval.

### Retrieval-augmented selection and compilation

1. **Profile selected theory:** record topic, domain, prerequisites, methods and source pages. Prototype profiles are manually authored.
2. **Maintain a curated bank:** exemplars, solutions, parameter constraints, verifiers and versions.
3. **Filter compatibility:** reject wrong topics/domains or missing prerequisites before ranking.
4. **Retrieve with BM25:** rank compatible families; no embedding service is used in these tests.
5. **Constrain model choice:** select only a retrieved family or refuse. Test reference labels are hidden from the model.
6. **Compile a variant:** code supplies admissible numbers, formulas and a matching solution.
7. **Check separately:** goal alignment, mathematical constraints and rendering are distinct checks.
8. **Retain provenance:** source pages, candidates, selection, parameters, failures, retries and cost. Refuse unsupported requests.

The 15-goal prototype uses a 40-family bank with shared source lineage. The two-PDF test expands to 50 families: 37 reused and 13 new. Only targeted PDF pages were inspected. Full PDFs are neither uploaded to the model nor included here. These tests cover controlled retrieval and compilation, not unrestricted invention or broad unseen-course accuracy.

### Formula rendering

Structured text/math blocks use the local KaTeX bundle. Rendering checks count math blocks and fallbacks. **Zero rendering fallbacks does not mean correct mathematics.** Legacy recovery can hide lost structure, as the repair experiment demonstrates.

## Reading the charts

| Chart | Measures | Does not establish |
| --- | --- | --- |
| Reviewer accept / revise | Model decisions | Mathematical correctness |
| Reference-label agreement | Accept/reject decisions on known controls | Correct reasoning in every explanation |
| Before / after repair | Change within each separately named measure | A shared accuracy scale across measures |
| Family checks passed | Properties covered by prepared verifiers | Coverage of arbitrary mathematics |
| Topic distribution | Composition of the sample | Correctness rate |
| SymPy statuses | Formal adapter coverage and encoded results | Full prose correctness |
| Retrieval top-k | Expected family among candidates | A valid final task |
| Context admission | Whether the plan stays in retrieved context | Mathematical accuracy |

Each bar shows its denominator. Attempt 01 has overlapping bars: an approved task can also be locally refuted. Do not add those bars or average unrelated experiment percentages.

## Historical flashcards: v1–v4

| Version | Cards | Scope |
| --- | ---: | --- |
| [v1](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=cards-v1) | 160 | Initial corpus; Sets pages 4–8 |
| [v2](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=cards-v2) | 180 | Revised corpus; some page ranges differ |
| [v3](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=cards-v3) | 130 | Includes a separately preserved Sets Level 1 repeat |
| [v4](https://olexandratabakova.github.io/mathpdf-metrics/experiment.html?id=cards-v4) | 35 | Sets Level 4 and Mathematical Induction Level 4 |

There are 27 set records, 505 per-card rows and 19 separate manual findings. Task V5 is a different track, not a fifth comparable flashcard sample. Historical generation prompts and every judge configuration were not retained. [prompts/](prompts/) contains evaluator prompts, not verified historical generation prompts.

Compare only unambiguous matches on **source file, topic, level and page range**. Scores are card-count-weighted averages over available values; missing values stay missing. Coverage is a weighted set average, not deduplicated global concept coverage. Changes are percentage points. Source faithfulness is not mathematical truth. Manual findings do not become correctness percentages; a new prompt does not mark old findings as fixed.

## Run locally

No frontend installation or build step is needed:

```sh
python -m http.server 8894 --bind 127.0.0.1
```

Open `http://127.0.0.1:8894`. Directly opening `index.html` also works through local script bundles; use a stable URL/browser for consistent storage. Experiment evidence loads only on its detail page. Vendor assets are local.

## Your version notebook

1. Generate and evaluate separately from production MathPDF.
2. Choose **New version**; save the hypothesis and exact prompt, and attach evaluator `cards_*.csv` if available.
3. Specify source filenames and page ranges.
4. Compare matching sets, inspect cards and record manual findings.
5. **Export JSON** for backup. **Import** merges by ID; imported matching records replace local ones. Invalid imports leave current data intact.

Additions and statuses stay in browser localStorage under `mathpdf-quality-lab-v1`. There is no login, server database or automatic GitHub sync. English display translations do not overwrite evidence or user edits. Export before clearing browser storage or changing devices.

To publish a reviewed snapshot:

```sh
python tools/publish_snapshot.py path/to/backup.json
git add data.js data/history.json
git commit -m "Record latest evaluation"
git push
```

This repository is public. Review exported notes and prompts before committing them. Credentials and private source PDFs are excluded.

## Repository map

| Path | Purpose |
| --- | --- |
| `index.html`, `research.js` | Lightweight catalogue |
| `experiment.html?id=…` | Directly linkable study details |
| `workspace.js`, `app.js` | English historical views, local editing and import/export |
| `history-english.js` | Display translations of historical manual findings |
| `style.css`, `vendor/` | Responsive styles and local math renderer |
| `experiments-catalog.js`, `data/experiments.json` | Small overview metadata derived from evidence |
| `*-data.js`, `experiments/*/result.json` | Original experiment evidence |
| `data.js`, `data/history.json` | Historical public snapshot |
| `tools/build_experiment_catalog.py` | Rebuild catalogue without API calls |
| `tools/publish_snapshot.py` | Validate and publish a browser backup |
| `flashcard_evaluator/`, `prompts/` | Separate evaluator and evaluation prompts |
| `tests/`, `docs/` | Regression tests, CLI instructions and provenance |

## Verification and reproduction

```sh
uv sync
uv run pytest -q
python tools/build_experiment_catalog.py
uv run evaluate run --help
```

See [evaluator instructions](docs/evaluator.md) for the separate paid CLI. Opening or testing the static site does not invoke it. Experiment folders retain prompts, seeds, usage, checks and reproduction scripts where available. Rerunning a model generation is a separate paid operation and need not reproduce the exact output; historical exports have the provenance limitations described above.

The current revision passes **96 Python tests**. With Playwright available in your Python environment and a local server running, the optional browser regression check is:

```sh
python tools/check_site.py --url http://127.0.0.1:8894 --chrome "/path/to/chrome"
```

It covers all ten studies and four historical versions, lazy evidence loading, formula rendering, English page text, 320/390/1440-pixel layouts, preservation of existing browser data, version editing, JSON import/export, CSV import and direct file opening. Reports and screenshots are written to ignored `output/site-checks/`.
