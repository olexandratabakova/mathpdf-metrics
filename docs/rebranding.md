# Acadence Metrics branding and repository rename

## Scope and compatibility

The public project name is **Acadence Metrics**, associated with the main product Acadence (formerly MathPDF). The website has a purple theme, updated monogram/favicon, page titles, metadata, navigation shell and JSON download filename. Layout, evaluation methods and interactions are unchanged.

No historical data, experiment results, datasets, archived prompts or metric definitions were rewritten. `experiments/`, `data/`, `data.js`, `*-data.js`, `experiments-catalog.js`, evaluator modules and lockfiles remain unchanged. Original study descriptions may name MathPDF because that was the product tested at the time. This is provenance, not stale current branding.

Intentional technical references:

| Reference | Reason retained |
| --- | --- |
| `mathpdf-quality-lab-v1` | Existing localStorage key; preserve browser-local versions, notes and edits on the same origin. |
| `window.MATHPDF_*`, `MathPDF` | Script data contracts and shared math renderer; changing them is unnecessary and risks breaking evidence rendering. |
| `flashcard-evaluator`, `flashcard_evaluator`, `evaluate` | Existing package, imports and CLI; no Python rename or schema migration is needed. |
| `evaluation MathPDF_all lecture notes.xlsx` | Existing input filename used by the evaluator CLI; renaming it would break default file discovery. |
| Historical source paths, `mathPDF-review` and old product/repository mentions in experiments | Reproduction instructions and recorded provenance. |
| `https://github.com/olexandratabakova/mathpdf-metrics` and existing Pages links | Remain valid until the owner performs the rename. Do not point users to an assumed future repository. |

The main product repository and its deployment are outside this change. No API calls or new paid evaluations are needed to verify branding.

## Manual repository rename

1. Export browser data using **Export JSON** before moving the website. Browser storage is origin-scoped; keep this backup even if the new Pages URL stays on the same origin.
2. Open the existing `olexandratabakova/mathpdf-metrics` GitHub repository as an administrator. Go to **Settings → General → Repository name**, enter `acadence-metrics`, then select **Rename**. Do not create a separate replacement repository.
3. After confirming the rename, update local remotes:

   ```sh
   git remote set-url origin https://github.com/olexandratabakova/acadence-metrics.git
   git remote -v
   git ls-remote origin HEAD
   ```

4. Update current repository links in **`index.html` and `experiment.html`**, and all current Pages links in **`README.md`**. The future repository URL is `https://github.com/olexandratabakova/acadence-metrics`; the expected project Pages URL is `https://olexandratabakova.github.io/acadence-metrics/`. Verify Pages actually publishes there before treating it as live.
5. Review **Settings → Pages**, retaining the existing publication method, and trigger/review its deployment. Update the repository description to “Acadence Metrics — evaluation and research for AI-assisted student learning” and the About website URL to the verified new Pages address. Check external bookmarks, badges or integrations; no repository badges are currently present in the README.
6. Open the new site, check experiments and formulas, and confirm local versions/notes remain. If storage is missing, **Import** the exported JSON. The application deliberately does not switch its storage key. Relative asset and evidence links require no code changes for the new base path.
7. Preserve old URLs inside immutable experiment evidence and historical documentation. This checklist records both old and intended addresses by design; it is not a request for global replacement.

Files needing URL edits after rename: **`README.md`, `index.html`, `experiment.html`**. This checklist can then record the confirmed rename/deployment. No current workflow file, package name, Python module, dataset path or evaluator command needs renaming.

## Modified files

- `index.html`, `experiment.html`: branded shell, titles, metadata and cache versions.
- `favicon.svg`, `style.css`: purple visual theme and Acadence monogram.
- `research.js`: dynamically generated browser titles only.
- `workspace.js`, `version-comparison.js`: current guidance names Acadence; historical records untouched.
- `app.js`: exported JSON filename only; storage key and export schema unchanged.
- `README.md`, `docs/rebranding.md`: project branding, audit and manual instructions.

## Verification commands

From the repository root, using the existing environment:

```sh
python -B -X utf8 -m pytest -q
python -B -X utf8 -m flashcard_evaluator.cli --help
python -B -X utf8 -m flashcard_evaluator.cli run --help
python -B -X utf8 -m flashcard_evaluator.cli compare --help
```

Help commands import the evaluator without running a paid evaluation. Existing tests exercise calculations, loading, snapshot generation and experiment consistency. Full historical model reruns would spend API credit and are outside this branding change.

For browser verification, serve the repository and run the existing optional regression suite:

```sh
python -m http.server 8894 --bind 127.0.0.1
python tools/check_site.py --url http://127.0.0.1:8894 --chrome "/path/to/chrome"
```

### Results (1 November 2026)

- Existing Python suite: **106 passed**. One existing pytest-asyncio fixture-scope deprecation warning remains.
- Evaluator imports and CLI/root, `run` and `compare` help commands: passed; no paid calls.
- Browser suite: passed across all 12 studies, 4 historical versions and 320/390/1440-pixel layouts; no page errors. JSON/CSV import, export, existing local records, direct-file opening and mathematical rendering passed. Desktop/mobile screenshots were visually inspected.
- `git diff --check`: passed. Evaluator code, data, archived experiments and generated evidence have no changes in this patch.
- This is a buildless static website; no frontend build or configured lint/type-check step is required. The historical catalogue is not regenerated for a cosmetic change.
