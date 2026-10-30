"""Tests for the card PDF loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from flashcard_evaluator.loaders import (
    _parse_filename,
    _parse_questions,
    _parse_answers,
    _split_sections,
    match_excel_row_to_cardset,
)
from flashcard_evaluator.models import CardSet, Flashcard


class TestParseFilename:
    def test_level_file(self):
        topic, level, ps, pe = _parse_filename(
            "Flashcards · main (9).pdf · 4–8 level 1.pdf"
        )
        assert level == "Level 1"
        assert ps == 4
        assert pe == 8

    def test_topic_file(self):
        topic, level, ps, pe = _parse_filename(
            "Flashcards · main (9).pdf · 14–19 math induction.pdf"
        )
        assert topic == "Mathematical Induction"
        assert level is None
        assert ps == 14
        assert pe == 19

    def test_proofs_file(self):
        topic, level, ps, pe = _parse_filename(
            "Flashcards · main (9).pdf · 20–21 proofs.pdf"
        )
        assert topic == "Proofs"
        assert ps == 20
        assert pe == 21


class TestParseQuestions:
    def test_basic_parsing(self):
        text = (
            "Questions\n"
            "Card 1\n"
            "What is a set?\n"
            "Card 2\n"
            "What is the empty set?\n"
        )
        result = _parse_questions(text)
        assert 1 in result
        assert 2 in result
        assert "What is a set?" in result[1]
        assert "What is the empty set?" in result[2]


class TestMatchExcelRow:
    def _make_sets(self) -> list[CardSet]:
        return [
            CardSet(topic="Sets", card_type="Flashcards", level="Level 1",
                    page_start=4, page_end=8),
            CardSet(topic="Mathematical Induction", card_type="Flashcards", level=None,
                    page_start=14, page_end=19),
            CardSet(topic="Proofs", card_type="Flashcards", level=None,
                    page_start=20, page_end=21),
        ]

    def test_level_match(self):
        sets = self._make_sets()
        result = match_excel_row_to_cardset("Sets", "Flashcards", "Level 1", sets)
        assert result is not None
        assert result.level == "Level 1"

    def test_topic_match_no_level(self):
        sets = self._make_sets()
        result = match_excel_row_to_cardset(
            "Mathematical Induction", "Flashcards", None, sets
        )
        assert result is not None
        assert result.topic == "Mathematical Induction"

    def test_no_match(self):
        sets = self._make_sets()
        result = match_excel_row_to_cardset("Calculus", "Flashcards", None, sets)
        assert result is None
