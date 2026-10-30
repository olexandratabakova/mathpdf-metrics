# Flashcard Evaluator

A Python CLI tool that evaluates LLM-generated flashcards against source study notes, using the OpenAI API as a judge, and fills in a metrics spreadsheet.

## Setup

### 1. Prerequisites

- Python 3.12
- `uv` (installed automatically below, or manually from https://docs.astral.sh/uv/)

### 2. Install uv (if not already installed)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Then add to PATH:
$env:Path = "C:\Users\<you>\.local\bin;$env:Path"
```

### 3. Install dependencies

```powershell
cd metrics_cards
uv sync
```

### 4. Set your API key

```powershell
Copy-Item .env.example .env
# Open .env and replace 'your-key-here' with your actual key:
notepad .env
```

`.env` contents:
```
OPENAI_API_KEY=sk-...your-key-here...
JUDGE_MODEL=gpt-4.1
EMBEDDING_MODEL=text-embedding-3-small
DUPLICATE_THRESHOLD=0.85
MAX_CONCURRENCY=4
```

**Never commit `.env` to git.** It is already in `.gitignore`.

If the key is missing or blank when you run the tool, you will see a clear error message with instructions.

## Running

### Quick test (first 3 cards per set)

```powershell
uv run evaluate run --limit 3
```

### Full evaluation

```powershell
uv run evaluate run
```

### Evaluate specific topics only

```powershell
uv run evaluate run --sets "Mathematical Induction,Proofs"
```

### Disable cache (force fresh LLM calls)

```powershell
uv run evaluate run --no-cache
```

### Compare two card sets (user_comment_effect metric)

```powershell
uv run evaluate compare cards/set_a.pdf cards/set_b.pdf
```

### All options

```powershell
uv run evaluate run --help
uv run evaluate compare --help
```

## Output

All output goes to the `output/` directory:

| File | Contents |
|------|----------|
| `evaluation_results_<timestamp>.xlsx` | Copy of the metrics spreadsheet with new columns filled in, plus a "Cards" sheet |
| `cards_<timestamp>.csv` | One row per card with 0/1 values for each metric |
| `details.jsonl` | Raw judge responses for debugging |

The terminal also prints a summary table and token/cost stats.

## Running Tests

```powershell
uv run pytest
```

Tests cover pure-code logic (no API calls):
- Quote verification (fuzzy matching)
- Sentence counting
- Duplicate pair detection
- Set-level aggregation (percentages, averages)
- PDF filename parsing
- Excel row matching

## File Layout

```
metrics_cards/
├── pyproject.toml
├── .env.example          ← copy to .env and add your key
├── .env                  ← gitignored, your real key goes here
├── .gitignore
├── README.md
│
├── flashcard_evaluator/  ← main package
│   ├── __init__.py
│   ├── cli.py            ← typer CLI (run, compare commands)
│   ├── config.py         ← .env loading, exits with clear error if key missing
│   ├── models.py         ← dataclass models
│   ├── loaders.py        ← PDF loaders (cards + notes)
│   ├── llm_client.py     ← async OpenAI client, disk cache, backoff
│   ├── evaluator.py      ← per-card and set-level metric functions
│   └── excel_writer.py   ← output writing (Excel + CSV)
│
├── prompts/              ← editable prompt text files (one per metric)
│   ├── self_contained_blind.txt
│   ├── self_contained_compare.txt
│   ├── faithfulness.txt
│   ├── card_properties.txt
│   ├── trivial.txt
│   ├── difficulty_gradient.txt
│   ├── material_type.txt
│   └── coverage.txt
│
├── tests/
│   ├── test_evaluator.py
│   └── test_loaders.py
│
├── cards/                ← card PDFs (your input)
├── notes/                ← source notes PDF (your input)
├── metrics/              ← original Excel (never modified)
├── cache/                ← LLM call cache (auto-created, gitignored)
└── output/               ← results (auto-created, gitignored)
```

## Assumptions

1. **Card PDF format**: Each card PDF has a "Questions" section first (listing "Card N\n<front text>") followed by an "Answers" section (listing "N. <Title>\nmain...pdf · page P\n<back text>"). This was confirmed by inspecting the provided PDFs.

2. **Excel structure**: Row 1 = column headers, Row 2 = descriptions (skipped), Rows 3+ = one row per card set. The original file is never modified; all results go to a timestamped copy.

3. **File mapping**: Card PDFs are matched to Excel rows by parsing the filename (e.g., `· 14–19 math induction.pdf` → topic="Mathematical Induction", pages 14-19). The "Sets" rows (Level 1-5) map to the `4-8 level N` files. The "Mathematical Induction (Problems)" row in the Excel has no corresponding card PDF and is skipped.

4. **Page range**: The page range is taken from the card PDF filename (`14-19`, `4-8`, etc.). If no range is available, all notes pages are used.

5. **Quote verification**: Uses fuzzy string matching (rapidfuzz) with a threshold of 75% similarity. Math formulas may not match exactly due to PDF extraction artifacts; claims are kept as "supported" even if the quote doesn't fuzzy-match, since math notation often doesn't survive plain-text extraction.

6. **`user_comment_effect`**: Implemented as the `compare` command. It takes two card PDFs for the same notes and reports differences in card_type distribution and average difficulty.

7. **`count_match`**: The Excel doesn't specify a requested card count per set, so this field is left blank. If your workflow adds a "requested count" column, let me know and I'll wire it in.

## Editing Prompts

All judge prompts are plain text files in `prompts/`. Edit them freely — changes take effect on the next run (cache is keyed by prompt content, so edited prompts automatically bypass the cache for those calls).
