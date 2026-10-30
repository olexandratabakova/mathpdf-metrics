"""
Core evaluation logic: per-card and per-set metrics.

Call structure (minimised for cost):
  Per card:
    1. self_contained_blind  — front only, no notes, no back
    2. self_contained_compare — blind_answer vs back
    3. faithfulness          — notes + back
  Per set (1 call each):
    4. card_properties_batch — all cards: front_leaks, atomic, card_type, u_v_r, trivial
    5. difficulty_gradient   — all card fronts → difficulty 1-5
    6. material_type         — notes text → material_type + key_concepts
    7. coverage              — key_concepts + all fronts
  Embeddings (1 batch per set):
    8. duplicate detection
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Literal, Optional

import numpy as np
from pydantic import BaseModel
from rapidfuzz import fuzz
from scipy.stats import spearmanr

from . import config
from .llm_client import get_embeddings, llm_call
from .models import (
    CardMetrics,
    CardSet,
    ClaimResult,
    DuplicatePair,
    FaithfulnessResult,
    SelfContainedResult,
    SetMetrics,
)


# ── Pydantic schemas for structured outputs ───────────────────────────────────

class _BlindResult(BaseModel):
    understandable: bool
    whats_missing: str
    blind_answer: str


class _CompareResult(BaseModel):
    blind_answer_matches: bool


class _Claim(BaseModel):
    claim: str
    status: Literal["supported", "unsupported", "contradicts"]
    page: Optional[int] = None
    quote: str = ""


class _FaithfulnessRaw(BaseModel):
    claims: list[_Claim]


# Batched schema: one call for all cards in a set
class _CardPropertiesItem(BaseModel):
    card_number: int
    front_leaks_answer: bool
    atomic: bool
    card_type: Literal[
        "definition", "theorem_condition", "why_question",
        "counterexample", "application", "method", "procedure", "other",
    ]
    understanding_vs_rote: Literal["understanding", "rote"]
    trivial: bool


class _BatchCardProperties(BaseModel):
    cards: list[_CardPropertiesItem]


class _DifficultyRating(BaseModel):
    card_number: int
    difficulty: int


class _DifficultyResult(BaseModel):
    ratings: list[_DifficultyRating]


class _MaterialTypeResult(BaseModel):
    material_type: Literal["theoretical", "practical", "mixed"]
    key_concepts: list[str]


class _CoverageItem(BaseModel):
    concept: str
    covered: bool
    covered_by_card: Optional[int] = None


class _CoverageResult(BaseModel):
    coverage: list[_CoverageItem]


# ── Prompt loading ─────────────────────────────────────────────────────────────

_prompt_cache: dict[str, str] = {}


def _load_prompt(name: str) -> str:
    if name not in _prompt_cache:
        p = config.PROMPTS_DIR / f"{name}.txt"
        if not p.exists():
            raise FileNotFoundError(f"Prompt file not found: {p}")
        _prompt_cache[name] = p.read_text(encoding="utf-8").strip()
    return _prompt_cache[name]


# ── Quote verification ────────────────────────────────────────────────────────

def verify_quote_in_page(quote: str, page_text: str, threshold: int = 75) -> bool:
    """
    Check whether the quote appears (approximately) in the page text.
    Uses sliding-window fuzzy match; ratio >= threshold counts as found.
    """
    if not quote or not quote.strip():
        return False

    quote_clean = quote.strip()
    page_clean = page_text.strip()

    if quote_clean.lower() in page_clean.lower():
        return True

    words = page_clean.split()
    quote_words = quote_clean.split()
    window = len(quote_words)
    if window == 0:
        return False

    best_ratio = 0
    for i in range(max(1, len(words) - window + 1)):
        window_text = " ".join(words[i : i + window + 2])
        ratio = fuzz.partial_ratio(quote_clean, window_text)
        if ratio > best_ratio:
            best_ratio = ratio
        if best_ratio >= threshold:
            return True

    return best_ratio >= threshold


# ── Per-card: self-contained blind test ──────────────────────────────────────

async def evaluate_self_contained(
    card_front: str,
    card_back: str,
    use_cache: bool = True,
    details_log: list | None = None,
) -> SelfContainedResult:
    """
    BLIND TEST: Call 1 receives ONLY the card front — no notes, no back.
    Call 2 compares the blind answer to the card back.
    """
    # Call 1: blind — NO notes, NO back, ONLY front
    blind = await llm_call(
        system=_load_prompt("self_contained_blind"),
        user=f"CARD_FRONT:\n{card_front}",
        response_model=_BlindResult,
        use_cache=use_cache,
        details_log=details_log,
    )

    # Call 2: compare blind answer to actual back
    compare = await llm_call(
        system=_load_prompt("self_contained_compare"),
        user=(
            f"BLIND_ANSWER:\n{blind.blind_answer}\n\n"
            f"CARD_BACK:\n{card_back}"
        ),
        response_model=_CompareResult,
        use_cache=use_cache,
        details_log=details_log,
    )

    passes = blind.understandable and blind.whats_missing.strip() == ""

    return SelfContainedResult(
        understandable=blind.understandable,
        whats_missing=blind.whats_missing,
        blind_answer=blind.blind_answer,
        blind_answer_matches=compare.blind_answer_matches,
        passes=passes,
    )


# ── Per-card: faithfulness ────────────────────────────────────────────────────

async def evaluate_faithfulness(
    card_back: str,
    pages: dict[int, str],
    use_cache: bool = True,
    details_log: list | None = None,
) -> FaithfulnessResult:
    """
    Split card back into atomic claims and verify each against source notes.
    Quotes verified with fuzzy matching against the cited page.
    """
    from .loaders import pages_to_text_with_markers

    notes_text = pages_to_text_with_markers(pages)

    raw = await llm_call(
        system=_load_prompt("faithfulness"),
        user=(
            f"SOURCE_NOTES:\n{notes_text}\n\n"
            f"CARD_BACK:\n{card_back}"
        ),
        response_model=_FaithfulnessRaw,
        use_cache=use_cache,
        details_log=details_log,
    )

    claims: list[ClaimResult] = []
    for c in raw.claims:
        quote_verified = False
        if c.quote and c.page and c.page in pages:
            quote_verified = verify_quote_in_page(c.quote, pages[c.page])
        elif c.quote and not c.page:
            quote_verified = any(
                verify_quote_in_page(c.quote, pt) for pt in pages.values()
            )

        claims.append(ClaimResult(
            claim=c.claim,
            status=c.status,
            page=c.page,
            quote=c.quote,
            quote_verified=quote_verified,
        ))

    supported = sum(1 for c in claims if c.status == "supported")
    unsupported = sum(1 for c in claims if c.status == "unsupported")
    contradicts = sum(1 for c in claims if c.status == "contradicts")

    return FaithfulnessResult(
        claims=claims,
        supported=supported,
        total=len(claims),
        unsupported=unsupported,
        contradicts=contradicts,
    )


# ── Set-level: batch card properties (1 call per set) ────────────────────────

_BATCH_CHUNK_SIZE = 10  # max cards per batch call to stay within completion token limit


async def evaluate_batch_card_properties(
    cards: list,
    use_cache: bool = True,
    details_log: list | None = None,
) -> dict[int, _CardPropertiesItem]:
    """
    Evaluate front_leaks_answer, atomic, card_type, understanding_vs_rote, trivial
    for ALL cards. Processes in chunks of _BATCH_CHUNK_SIZE to avoid hitting the
    completion token limit on large sets.  Returns {card_number: item}.
    """
    all_items: dict[int, _CardPropertiesItem] = {}

    # Split into chunks
    chunks = [cards[i : i + _BATCH_CHUNK_SIZE] for i in range(0, len(cards), _BATCH_CHUNK_SIZE)]

    async def _call_chunk(chunk):
        card_listing = "\n\n".join(
            f"Card {c.number}\nFRONT: {c.front}\nBACK: {c.back}"
            for c in chunk
        )
        result = await llm_call(
            system=_load_prompt("card_properties_batch"),
            user=f"CARDS:\n{card_listing}",
            response_model=_BatchCardProperties,
            use_cache=use_cache,
            details_log=details_log,
        )
        return {item.card_number: item for item in result.cards}

    chunk_results = await asyncio.gather(*[_call_chunk(chunk) for chunk in chunks])
    for chunk_dict in chunk_results:
        all_items.update(chunk_dict)

    return all_items


def count_sentences(text: str) -> int:
    """Count sentences using simple punctuation heuristic."""
    sentences = re.split(r"[.!?]+(?:\s|$)", text.strip())
    return len([s for s in sentences if s.strip()])


# ── Set-level: difficulty gradient ───────────────────────────────────────────

async def evaluate_difficulty_gradient(
    card_metrics_list: list[CardMetrics],
    use_cache: bool = True,
    details_log: list | None = None,
) -> float | None:
    """
    Rate each card's difficulty 1-5 in one set-level call,
    then compute Spearman correlation of card order vs difficulty.
    """
    fronts = "\n\n".join(
        f"Card {m.card_number}: {m.front}" for m in card_metrics_list
    )

    result = await llm_call(
        system=_load_prompt("difficulty_gradient"),
        user=f"CARD_FRONTS:\n{fronts}",
        response_model=_DifficultyResult,
        use_cache=use_cache,
        details_log=details_log,
    )

    difficulty_map = {r.card_number: r.difficulty for r in result.ratings}
    for m in card_metrics_list:
        m.difficulty = difficulty_map.get(m.card_number)

    pairs = [
        (i + 1, difficulty_map[m.card_number])
        for i, m in enumerate(card_metrics_list)
        if m.card_number in difficulty_map
    ]
    if len(pairs) < 3:
        return None
    orders, difficulties = zip(*pairs)
    corr, _ = spearmanr(orders, difficulties)
    return float(corr) if not np.isnan(corr) else None


# ── Set-level: duplicate detection via embeddings ────────────────────────────

async def evaluate_duplicates(
    card_metrics_list: list[CardMetrics],
    threshold: float | None = None,
    details_log: list | None = None,
) -> tuple[list[DuplicatePair], float]:
    """Embed all card fronts, compute cosine similarity, flag pairs >= threshold."""
    threshold = threshold or config.DUPLICATE_THRESHOLD
    fronts = [m.front for m in card_metrics_list]
    if len(fronts) < 2:
        return [], 0.0

    embeddings = await get_embeddings(fronts)
    emb_matrix = np.array(embeddings)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-9, norms)
    emb_normalized = emb_matrix / norms
    sim_matrix = emb_normalized @ emb_normalized.T

    pairs: list[DuplicatePair] = []
    n = len(card_metrics_list)
    for i in range(n):
        for j in range(i + 1, n):
            sim = float(sim_matrix[i, j])
            if sim >= threshold:
                pairs.append(DuplicatePair(
                    card_a=card_metrics_list[i].card_number,
                    card_b=card_metrics_list[j].card_number,
                    similarity=sim,
                ))

    involved = set()
    for p in pairs:
        involved.add(p.card_a)
        involved.add(p.card_b)
    rate = len(involved) / n if n > 0 else 0.0

    if details_log is not None:
        details_log.append({
            "metric": "duplicates",
            "threshold": threshold,
            "pairs": [(p.card_a, p.card_b, round(p.similarity, 4)) for p in pairs],
        })

    return pairs, rate


# ── Set-level: material type + key concepts ───────────────────────────────────

async def evaluate_material_type(
    notes_text: str,
    use_cache: bool = True,
    details_log: list | None = None,
) -> _MaterialTypeResult:
    return await llm_call(
        system=_load_prompt("material_type"),
        user=f"SOURCE_NOTES:\n{notes_text}",
        response_model=_MaterialTypeResult,
        use_cache=use_cache,
        details_log=details_log,
    )


async def evaluate_coverage(
    key_concepts: list[str],
    card_metrics_list: list[CardMetrics],
    use_cache: bool = True,
    details_log: list | None = None,
) -> _CoverageResult:
    concepts_text = "\n".join(f"- {c}" for c in key_concepts)
    fronts_text = "\n".join(
        f"Card {m.card_number}: {m.front}" for m in card_metrics_list
    )
    return await llm_call(
        system=_load_prompt("coverage"),
        user=(
            f"KEY_CONCEPTS:\n{concepts_text}\n\n"
            f"CARD_FRONTS:\n{fronts_text}"
        ),
        response_model=_CoverageResult,
        use_cache=use_cache,
        details_log=details_log,
    )


# ── Main evaluation entry point ───────────────────────────────────────────────

async def evaluate_card_set(
    card_set: CardSet,
    pages: dict[int, str],
    limit: int | None = None,
    use_cache: bool = True,
    details_log: list | None = None,
) -> SetMetrics:
    """
    Evaluate all cards in a set, then run set-level metrics.

    Call plan per set:
      • Per card (concurrent): blind (2 calls) + faithfulness (1 call)
      • 1 call: batch card properties for ALL cards
      • 1 call: difficulty gradient for ALL cards
      • 1 call: material type + key concepts
      • 1 call: coverage
      • 1 embedding batch: duplicates
    """
    from .loaders import pages_to_text_with_markers

    cards = card_set.cards[:limit] if limit else card_set.cards

    set_metrics = SetMetrics(
        topic=card_set.topic,
        card_type=card_set.card_type,
        level=card_set.level,
    )

    print(
        f"  Evaluating {len(cards)} cards for "
        f"{card_set.topic} / {card_set.level or '(no level)'}..."
    )

    # ── Step 1: per-card calls (blind + faithfulness) — all concurrent ────────
    async def _eval_card_core(card) -> tuple[SelfContainedResult, FaithfulnessResult]:
        sc, faith = await asyncio.gather(
            evaluate_self_contained(card.front, card.back,
                                    use_cache=use_cache, details_log=details_log),
            evaluate_faithfulness(card.back, pages,
                                  use_cache=use_cache, details_log=details_log),
        )
        return sc, faith

    core_results = await asyncio.gather(*[_eval_card_core(c) for c in cards])

    # ── Step 2: batch card properties (1 call for the whole set) ─────────────
    batch_props = await evaluate_batch_card_properties(
        cards, use_cache=use_cache, details_log=details_log
    )

    # ── Step 3: assemble CardMetrics ─────────────────────────────────────────
    card_metrics_list: list[CardMetrics] = []
    for i, card in enumerate(cards):
        sc, faith = core_results[i]
        props = batch_props.get(card.number)

        card_metrics_list.append(CardMetrics(
            card_number=card.number,
            front=card.front,
            back=card.back,
            self_contained=sc,
            faithfulness=faith,
            front_leaks_answer=props.front_leaks_answer if props else None,
            atomic=props.atomic if props else None,
            card_type_label=props.card_type if props else "",
            understanding_vs_rote=props.understanding_vs_rote if props else "",
            trivial=props.trivial if props else None,
            back_length_sentences=count_sentences(card.back),
        ))

    set_metrics.card_metrics = card_metrics_list

    # ── Step 4-7: set-level calls concurrently ────────────────────────────────
    notes_text = pages_to_text_with_markers(pages)

    difficulty_coro = evaluate_difficulty_gradient(
        card_metrics_list, use_cache=use_cache, details_log=details_log
    )
    duplicates_coro = evaluate_duplicates(
        card_metrics_list, details_log=details_log
    )
    material_coro = evaluate_material_type(
        notes_text, use_cache=use_cache, details_log=details_log
    )

    diff_corr, (dup_pairs, dup_rate), mat_result = await asyncio.gather(
        difficulty_coro, duplicates_coro, material_coro
    )

    set_metrics.difficulty_spearman = diff_corr
    set_metrics.duplicate_pairs = dup_pairs
    set_metrics.duplicate_rate = dup_rate
    set_metrics.material_type = mat_result.material_type

    # Coverage (depends on key_concepts from material call)
    if mat_result.key_concepts and card_metrics_list:
        cov = await evaluate_coverage(
            mat_result.key_concepts, card_metrics_list,
            use_cache=use_cache, details_log=details_log,
        )
        set_metrics.coverage_key_concepts = mat_result.key_concepts
        set_metrics.coverage_covered = [
            item.concept for item in cov.coverage if item.covered
        ]
        total = len(mat_result.key_concepts)
        covered = len(set_metrics.coverage_covered)
        set_metrics.coverage_ratio = covered / total if total > 0 else 0.0

    return set_metrics
