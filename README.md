# MathPDF · Quality Lab

A small, offline-capable workspace for tracking prompt versions, reviewing flashcard quality and keeping mathematical issues visible. The interface is in Ukrainian.

## Open the dashboard

Open **[index.html](index.html)** in a browser. No installation, API key, build step or internet connection is needed. Alternatively:

```sh
python -m http.server 8894 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8894`. Use a stable URL/browser to keep your local edits together.

## Your regular workflow

1. Generate a test set separately from the production MathPDF application.
2. Run the Python evaluator to produce `cards_*.csv`.
3. Choose **Нова версія**. Give it a name, record the exact prompt, describe the hypothesis and attach the CSV.
4. Fill in the source filename and page range for each set. These must match the baseline to enable a fair comparison. Keep level labels consistent.
5. Review the cards, record manual mathematical findings, and update their verification status.
6. **Експорт JSON** saves a complete backup of your changes. Keep that file before clearing browser data or changing devices.

**Storage:** additions and notes live in browser localStorage, not in GitHub. There is no login, server database or automatic synchronization. The public website always starts from the committed `data.js` snapshot. Import combines records by ID; imported matching IDs replace local matching records. An invalid import leaves the existing dataset intact.

## Publish a new data snapshot

After exporting a backup from the dashboard:

```sh
python tools/publish_snapshot.py path/to/mathpdf-metrics-backup.json
git add data.js data/history.json
git commit -m "Record latest evaluation"
git push
```

Review the backup before publishing: notes and prompt snapshots you add will become public if committed to this public repository. Never include API keys, private source documents or account information. Browser-local changes do not become public unless you export and publish them.

## What is in the history

| Version | Evaluated cards | Scope |
| --- | ---: | --- |
| v1 | 160 | Initial evaluation corpus |
| v2 | 180 | Revised corpus; source page ranges differ for some sets |
| v3 | 130 | Includes a separately preserved repeat of Sets Level 1 |
| v4 | 35 | Sets Level 4 and Mathematical Induction Level 4 |

The 27 set rows and 505 per-card rows come from the existing v1–v3 comparison export plus the v4 rows from the later comparison. Historical rows already repeated in the v4 workbook are not imported twice. The 19 manual findings are separate from automated flashcard metrics. Later function PDFs were not quantitatively evaluated in this corpus and are not invented as v5 results.

Historical prompt snapshots and the judge configuration for every run were not retained in these exports. Their exact prompts/models are therefore **not claimed**. `prompts/` contains the current **evaluation** prompts, not verified historical generation prompts.

## Reading the numbers

- Comparison includes only unambiguous matches on source filename, topic, level and source pages. Different card counts are displayed. The source documents themselves are not bundled or independently hash-matched.
- Summary percentages are weighted by evaluated card count. Coverage is a card-count-weighted average of set coverage, not deduplicated global concept coverage.
- Changes are percentage **points**, not relative percentages.
- Faithfulness measures support in the source and is not proof of mathematical truth.
- CSV imports contain per-card results but not source pages, duplicate rate or concept coverage. Missing values stay missing; they are never filled with zero or invented.
- Manual issue statuses are your own verification notes. A new prompt alone does not mark a historical issue as fixed.

## Python evaluator

The evaluator is retained as a separate CLI; opening the dashboard never calls an AI provider or spends API credit. See **[Evaluator instructions](docs/evaluator.md)** for configuration and commands. Source PDFs and the metrics workbook remain local and are not bundled here. Supply their paths using `evaluate run --help`.

```sh
uv sync
uv run evaluate run --help
uv run pytest -q
```

Copy `.env.example` to an ignored `.env` only if you want to run paid evaluation. Always review the dry-run cost estimate before running it.

## Project layout

```text
index.html, style.css, app.js  Dashboard, without frontend dependencies
data.js                       Public snapshot loaded offline
data/history.json             Same snapshot as readable JSON
tools/publish_snapshot.py      Validate and publish a local JSON backup
flashcard_evaluator/           Existing Python evaluator
prompts/                      Evaluation prompts
tests/                        Evaluator unit tests
docs/                         Detailed CLI and data provenance notes
```

The original working directory and historical outputs were preserved. This repository is a curated copy: caches, API credentials, duplicate screenshots, temporary logs and source PDFs are excluded.
