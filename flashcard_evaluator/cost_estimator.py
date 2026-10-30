"""
Token and cost estimation before running the full evaluation.
Uses tiktoken to count tokens; no API calls are made.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tiktoken

from . import config
from .loaders import pages_to_text_with_markers
from .models import CardSet, Flashcard

# ── Pricing table (USD per 1K tokens, input / output) ─────────────────────────
# Update these when OpenAI changes prices.
_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o-mini":          {"input": 0.000150, "output": 0.000600},
    "gpt-4o":               {"input": 0.005000, "output": 0.015000},
    "gpt-4.1":              {"input": 0.002000, "output": 0.008000},
    "gpt-4.1-mini":         {"input": 0.000400, "output": 0.001600},
    "gpt-4.1-nano":         {"input": 0.000100, "output": 0.000400},
    "text-embedding-3-small": {"input": 0.000020, "output": 0.0},
}

# Average output tokens per call type (rough estimates)
_OUTPUT_TOKENS: dict[str, int] = {
    "blind":       120,   # understandable, whats_missing, blind_answer
    "compare":      20,   # blind_answer_matches
    "faithfulness": 200,  # 3-5 claims × ~40 tokens each
    "batch_props":  60,   # per card: 5 bool/enum fields
    "difficulty":   40,   # per card: card_number + difficulty
    "material":    150,   # material_type + ~10 key_concepts
    "coverage":    100,   # per concept: concept + covered + card_number
}


@dataclass
class CostEstimate:
    model: str
    n_cards: int            # total cards across all sets
    n_sets: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    embedding_tokens: int = 0
    call_breakdown: dict[str, int] = field(default_factory=dict)  # call_type → count

    @property
    def judge_cost(self) -> float:
        p = _PRICING.get(self.model, {"input": 0.002, "output": 0.008})
        return (
            self.prompt_tokens / 1000 * p["input"]
            + self.completion_tokens / 1000 * p["output"]
        )

    @property
    def embedding_cost(self) -> float:
        p = _PRICING.get(config.EMBEDDING_MODEL, {"input": 0.00002, "output": 0.0})
        return self.embedding_tokens / 1000 * p["input"]

    @property
    def total_cost(self) -> float:
        return self.judge_cost + self.embedding_cost

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def _get_encoder(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("o200k_base")


def _count(enc: tiktoken.Encoding, text: str) -> int:
    return len(enc.encode(text))


def _load_prompt(name: str) -> str:
    p = config.PROMPTS_DIR / f"{name}.txt"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def estimate_cost(
    card_sets_with_pages: list[tuple[CardSet, dict[int, str]]],
    limit: int | None = None,
    model: str | None = None,
) -> CostEstimate:
    """
    Estimate tokens and cost for evaluating the given card sets.
    card_sets_with_pages: list of (CardSet, pages_dict) pairs.
    """
    model = model or config.JUDGE_MODEL
    enc = _get_encoder(model)

    est = CostEstimate(
        model=model,
        n_cards=0,
        n_sets=len(card_sets_with_pages),
    )
    breakdown: dict[str, int] = {}

    # Pre-load prompts once
    prompts = {
        "blind":        _load_prompt("self_contained_blind"),
        "compare":      _load_prompt("self_contained_compare"),
        "faithfulness": _load_prompt("faithfulness"),
        "batch_props":  _load_prompt("card_properties_batch"),
        "difficulty":   _load_prompt("difficulty_gradient"),
        "material":     _load_prompt("material_type"),
        "coverage":     _load_prompt("coverage"),
    }

    for cs, pages in card_sets_with_pages:
        cards = cs.cards[:limit] if limit else cs.cards
        n = len(cards)
        est.n_cards += n
        notes_text = pages_to_text_with_markers(pages)
        notes_tokens = _count(enc, notes_text)

        # ── Per-card: blind test (2 calls each) ──────────────────────────────
        for card in cards:
            front_tok = _count(enc, card.front)
            back_tok = _count(enc, card.back)

            # Call 1: blind
            p_tok = _count(enc, prompts["blind"]) + front_tok + 10
            est.prompt_tokens += p_tok
            est.completion_tokens += _OUTPUT_TOKENS["blind"]
            breakdown["blind"] = breakdown.get("blind", 0) + 1

            # Call 2: compare (blind_answer ~ 80 tokens average)
            p_tok = _count(enc, prompts["compare"]) + 80 + back_tok + 10
            est.prompt_tokens += p_tok
            est.completion_tokens += _OUTPUT_TOKENS["compare"]
            breakdown["compare"] = breakdown.get("compare", 0) + 1

            # Call 3: faithfulness
            p_tok = _count(enc, prompts["faithfulness"]) + notes_tokens + back_tok + 15
            est.prompt_tokens += p_tok
            est.completion_tokens += _OUTPUT_TOKENS["faithfulness"]
            breakdown["faithfulness"] = breakdown.get("faithfulness", 0) + 1

        # ── Set-level: batch card properties (1 call per set) ────────────────
        card_listing = "\n\n".join(
            f"Card {c.number} FRONT: {c.front}\nCard {c.number} BACK: {c.back}"
            for c in cards
        )
        p_tok = _count(enc, prompts["batch_props"]) + _count(enc, card_listing) + 15
        est.prompt_tokens += p_tok
        est.completion_tokens += _OUTPUT_TOKENS["batch_props"] * n
        breakdown["batch_props"] = breakdown.get("batch_props", 0) + 1

        # ── Set-level: difficulty (1 call per set) ────────────────────────────
        fronts_listing = "\n\n".join(f"Card {c.number}: {c.front}" for c in cards)
        p_tok = _count(enc, prompts["difficulty"]) + _count(enc, fronts_listing) + 10
        est.prompt_tokens += p_tok
        est.completion_tokens += _OUTPUT_TOKENS["difficulty"] * n
        breakdown["difficulty"] = breakdown.get("difficulty", 0) + 1

        # ── Set-level: material type + key concepts (1 call per set) ─────────
        p_tok = _count(enc, prompts["material"]) + notes_tokens + 10
        est.prompt_tokens += p_tok
        est.completion_tokens += _OUTPUT_TOKENS["material"]
        breakdown["material"] = breakdown.get("material", 0) + 1

        # ── Set-level: coverage (1 call per set, assume ~12 key concepts) ─────
        p_tok = _count(enc, prompts["coverage"]) + 200 + _count(enc, fronts_listing) + 10
        est.prompt_tokens += p_tok
        est.completion_tokens += _OUTPUT_TOKENS["coverage"]
        breakdown["coverage"] = breakdown.get("coverage", 0) + 1

        # ── Embeddings for duplicate detection ────────────────────────────────
        for card in cards:
            est.embedding_tokens += _count(enc, card.front)

    est.call_breakdown = breakdown
    return est


def format_estimate(est: CostEstimate) -> str:
    """Return a human-readable estimate string."""
    lines = [
        f"  Model:              {est.model}",
        f"  Sets:               {est.n_sets}",
        f"  Cards:              {est.n_cards}",
        f"  Prompt tokens:      {est.prompt_tokens:>10,}",
        f"  Completion tokens:  {est.completion_tokens:>10,}",
        f"  Embedding tokens:   {est.embedding_tokens:>10,}",
        f"  ─────────────────────────────────",
        f"  Judge cost:         ${est.judge_cost:>9.4f}",
        f"  Embedding cost:     ${est.embedding_cost:>9.4f}",
        f"  TOTAL ESTIMATE:     ${est.total_cost:>9.4f}",
        "",
        "  API calls by type:",
    ]
    for call_type, count in sorted(est.call_breakdown.items()):
        lines.append(f"    {call_type:<20} {count:>4} calls")
    return "\n".join(lines)
