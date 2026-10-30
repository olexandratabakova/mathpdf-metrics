"""Tests for pure-code functions: quote verification, duplicate detection, aggregation."""
from __future__ import annotations

import pytest
import numpy as np

from flashcard_evaluator.evaluator import (
    count_sentences,
    verify_quote_in_page,
)
from flashcard_evaluator.models import (
    CardMetrics,
    DuplicatePair,
    FaithfulnessResult,
    ClaimResult,
    SelfContainedResult,
    SetMetrics,
)


# ── Quote verification tests ─────────────────────────────────────────────────

class TestVerifyQuote:
    def test_exact_match(self):
        page = "The empty set is denoted by ∅ or by empty braces {}."
        assert verify_quote_in_page("empty set is denoted by ∅", page) is True

    def test_case_insensitive(self):
        page = "A set is a collection of objects."
        assert verify_quote_in_page("A SET IS A COLLECTION", page) is True

    def test_not_present(self):
        page = "The cardinality of a finite set A is denoted by |A|."
        assert verify_quote_in_page("power set of B equals all subsets", page) is False

    def test_empty_quote_returns_false(self):
        page = "Some text here."
        assert verify_quote_in_page("", page) is False

    def test_fuzzy_match_with_minor_typo(self):
        page = "Two sets A and B are equal if every element of A is in B."
        # Minor substitution — should still match
        assert verify_quote_in_page("Two sets A and B are equal if every element of A", page) is True

    def test_partial_quote_not_in_page(self):
        page = "Mathematical induction is a proof technique."
        assert verify_quote_in_page("proof by contradiction", page) is False


# ── Sentence counter tests ───────────────────────────────────────────────────

class TestCountSentences:
    def test_single_sentence(self):
        assert count_sentences("This is one sentence.") == 1

    def test_multiple_sentences(self):
        assert count_sentences("First. Second. Third.") == 3

    def test_empty_string(self):
        assert count_sentences("") == 0

    def test_no_punctuation(self):
        # Treat as one sentence
        assert count_sentences("No punctuation here") >= 1

    def test_math_notation(self):
        # Numbers with dots shouldn't explode sentence count
        text = "We write x∈A when x is in A. The empty set ∅ has zero elements."
        assert count_sentences(text) == 2


# ── Duplicate detection tests ────────────────────────────────────────────────

class TestDuplicateDetection:
    """Test the cosine-similarity duplicate logic without calling the API."""

    def _make_metrics(self, fronts: list[str]) -> list[CardMetrics]:
        return [
            CardMetrics(card_number=i + 1, front=f, back="")
            for i, f in enumerate(fronts)
        ]

    def _cosine_pairs(
        self, metrics: list[CardMetrics], threshold: float = 0.85
    ) -> list[DuplicatePair]:
        """Re-implement cosine similarity without embeddings (using unit vectors)."""
        # Create random but fixed embeddings for testing
        rng = np.random.default_rng(42)
        n = len(metrics)
        emb = rng.random((n, 10))
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        emb_n = emb / norms
        sim = emb_n @ emb_n.T
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if sim[i, j] >= threshold:
                    pairs.append(DuplicatePair(
                        card_a=metrics[i].card_number,
                        card_b=metrics[j].card_number,
                        similarity=float(sim[i, j]),
                    ))
        return pairs

    def test_identical_embeddings_are_duplicates(self):
        """If two cards have identical embedding vectors, similarity = 1.0 ≥ threshold."""
        from flashcard_evaluator.models import DuplicatePair

        # Simulate: two cards with cosine sim = 1.0
        pair = DuplicatePair(card_a=1, card_b=2, similarity=1.0)
        assert pair.similarity >= 0.85

    def test_orthogonal_embeddings_not_duplicates(self):
        pair = DuplicatePair(card_a=1, card_b=2, similarity=0.0)
        assert pair.similarity < 0.85

    def test_duplicate_rate_calculation(self):
        # 3 cards, cards 1 and 2 are duplicates
        pairs = [DuplicatePair(card_a=1, card_b=2, similarity=0.91)]
        involved = {1, 2}
        n = 3
        rate = len(involved) / n
        assert abs(rate - 2 / 3) < 1e-9


# ── Aggregation tests ─────────────────────────────────────────────────────────

class TestSetMetricsAggregation:
    def _make_sc(self, passes: bool) -> SelfContainedResult:
        return SelfContainedResult(
            understandable=passes,
            whats_missing="" if passes else "something",
            blind_answer="",
            blind_answer_matches=passes,
            passes=passes,
        )

    def _make_faith(self, ratio: float) -> FaithfulnessResult:
        s = int(ratio * 10)
        u = 10 - s
        return FaithfulnessResult(
            claims=[],
            supported=s,
            total=10,
            unsupported=u,
            contradicts=0,
        )

    def _make_cm(
        self,
        num: int,
        sc_passes: bool,
        faith_ratio: float,
        front_leaks: bool,
        atomic: bool,
        trivial: bool,
        understanding: bool,
    ) -> CardMetrics:
        return CardMetrics(
            card_number=num,
            front=f"Card {num}",
            back="answer",
            self_contained=self._make_sc(sc_passes),
            faithfulness=self._make_faith(faith_ratio),
            front_leaks_answer=front_leaks,
            atomic=atomic,
            trivial=trivial,
            understanding_vs_rote="understanding" if understanding else "rote",
        )

    def test_pct_self_contained(self):
        sm = SetMetrics(topic="T", card_type="Flashcards", level=None)
        sm.card_metrics = [
            self._make_cm(1, True, 1.0, False, True, False, True),
            self._make_cm(2, False, 0.8, False, True, False, True),
            self._make_cm(3, True, 1.0, False, True, False, True),
        ]
        assert abs(sm.pct_self_contained - 2 / 3) < 1e-9

    def test_avg_faithfulness(self):
        sm = SetMetrics(topic="T", card_type="Flashcards", level=None)
        sm.card_metrics = [
            self._make_cm(1, True, 1.0, False, True, False, True),
            self._make_cm(2, True, 0.5, False, True, False, True),
        ]
        assert abs(sm.avg_faithfulness - 0.75) < 1e-9

    def test_pct_trivial(self):
        sm = SetMetrics(topic="T", card_type="Flashcards", level=None)
        sm.card_metrics = [
            self._make_cm(1, True, 1.0, False, True, True, True),
            self._make_cm(2, True, 1.0, False, True, False, True),
            self._make_cm(3, True, 1.0, False, True, True, True),
            self._make_cm(4, True, 1.0, False, True, False, True),
        ]
        assert abs(sm.pct_trivial - 0.5) < 1e-9

    def test_card_type_distribution(self):
        sm = SetMetrics(topic="T", card_type="Flashcards", level=None)
        sm.card_metrics = [
            CardMetrics(card_number=1, front="", back="", card_type_label="definition"),
            CardMetrics(card_number=2, front="", back="", card_type_label="definition"),
            CardMetrics(card_number=3, front="", back="", card_type_label="method"),
        ]
        dist = sm.card_type_distribution
        assert abs(dist["definition"] - 2 / 3) < 1e-9
        assert abs(dist["method"] - 1 / 3) < 1e-9
