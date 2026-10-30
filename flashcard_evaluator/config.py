"""Configuration: load environment variables and validate required settings."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / ".env")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(
            f"\n[ERROR] Environment variable '{name}' is not set.\n"
            f"  1. Copy .env.example → .env in the project root:\n"
            f"       {_ROOT / '.env'}\n"
            f"  2. Paste your OpenAI API key as OPENAI_API_KEY=sk-...\n"
            f"  3. Re-run the command.\n",
            file=sys.stderr,
        )
        sys.exit(1)
    return value


def get_api_key() -> str:
    """Return the OpenAI API key, exiting with a clear message if missing."""
    return _require("OPENAI_API_KEY")


# Read at import time — but only exit if missing when the key is actually used.
# We expose it as a module-level name for convenience; tests that don't call
# the LLM can import this module without needing a real key by setting a dummy env var.
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
DUPLICATE_THRESHOLD: float = float(os.getenv("DUPLICATE_THRESHOLD", "0.85"))
MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "4"))
MAX_COST: float = float(os.getenv("MAX_COST", "1.0"))

PROMPTS_DIR: Path = _ROOT / "prompts"
CACHE_DIR: Path = _ROOT / "cache"
OUTPUT_DIR: Path = _ROOT / "output"
RESULTS_DIR: Path = _ROOT / "results"
