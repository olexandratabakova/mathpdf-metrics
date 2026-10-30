"""Data models for cards, notes, and evaluation results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class Flashcard:
    """A single flashcard with front (question) and back (answer)."""
    number: int          # 1-based index within the set
    front: str           # Question text
    back: str            # Answer text
    page_ref: int | None = None  # Page number from the source notes (if parsed)
    title: str = ""      # Short answer title (if the PDF includes one)


@dataclass
class CardSet:
    """A collection of flashcards from one card PDF, linked to an Excel row."""
    topic: str
    card_type: str        # e.g. "Flashcards", "Problems"
    level: str | None     # e.g. "Level 1" or None
    page_start: int | None
    page_end: int | None
    cards: list[Flashcard] = field(default_factory=list)
    source_file: str = ""


# ── Per-card metric results ──────────────────────────────────────────────────

@dataclass
class SelfContainedResult:
    understandable: bool
    whats_missing: str
    blind_answer: str
    blind_answer_matches: bool
    passes: bool          # understandable AND whats_missing == ""


@dataclass
class ClaimResult:
    claim: str
    status: Literal["supported", "unsupported", "contradicts"]
    page: int | None
    quote: str
    quote_verified: bool   # did we find the quote in the page text?


@dataclass
class FaithfulnessResult:
    claims: list[ClaimResult]
    supported: int
    total: int
    unsupported: int
    contradicts: int

    @property
    def ratio(self) -> float:
        return self.supported / self.total if self.total else 1.0


@dataclass
class CardMetrics:
    card_number: int
    front: str
    back: str
    self_contained: SelfContainedResult | None = None
    faithfulness: FaithfulnessResult | None = None
    front_leaks_answer: bool | None = None
    atomic: bool | None = None
    card_type_label: str = ""   # definition | theorem_condition | ...
    understanding_vs_rote: str = ""
    trivial: bool | None = None
    back_length_sentences: int = 0
    difficulty: int | None = None    # 1-5, from set-level call


# ── Set-level results ────────────────────────────────────────────────────────

@dataclass
class DuplicatePair:
    card_a: int   # 1-based
    card_b: int
    similarity: float


@dataclass
class SetMetrics:
    topic: str
    card_type: str
    level: str | None
    card_metrics: list[CardMetrics] = field(default_factory=list)

    # Set-level
    duplicate_pairs: list[DuplicatePair] = field(default_factory=list)
    duplicate_rate: float = 0.0
    material_type: str = ""          # theoretical | practical | mixed
    count_match: bool | None = None  # did card count match request?
    coverage_key_concepts: list[str] = field(default_factory=list)
    coverage_covered: list[str] = field(default_factory=list)
    coverage_ratio: float = 0.0
    difficulty_spearman: float | None = None

    # Aggregated per-card booleans (percentages)
    @property
    def pct_self_contained(self) -> float:
        vals = [m.self_contained.passes for m in self.card_metrics if m.self_contained]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def pct_front_leaks(self) -> float:
        vals = [m.front_leaks_answer for m in self.card_metrics if m.front_leaks_answer is not None]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def pct_atomic(self) -> float:
        vals = [m.atomic for m in self.card_metrics if m.atomic is not None]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def pct_trivial(self) -> float:
        vals = [m.trivial for m in self.card_metrics if m.trivial is not None]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def pct_understanding(self) -> float:
        vals = [m.understanding_vs_rote == "understanding" for m in self.card_metrics if m.understanding_vs_rote]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def avg_faithfulness(self) -> float:
        vals = [m.faithfulness.ratio for m in self.card_metrics if m.faithfulness]
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def card_type_distribution(self) -> dict[str, float]:
        labels = [m.card_type_label for m in self.card_metrics if m.card_type_label]
        if not labels:
            return {}
        counts: dict[str, int] = {}
        for lb in labels:
            counts[lb] = counts.get(lb, 0) + 1
        n = len(labels)
        return {k: v / n for k, v in counts.items()}

    @property
    def avg_back_length(self) -> float:
        vals = [m.back_length_sentences for m in self.card_metrics if m.back_length_sentences]
        return sum(vals) / len(vals) if vals else 0.0
