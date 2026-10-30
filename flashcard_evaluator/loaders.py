"""
PDF loaders for both card PDFs and the source notes PDF.

Card PDF format (confirmed by inspection):
  - First N pages: "Questions" section
      Page header: <title line>
      "Card N"
      <question text>
      "Card N+1"
      ...
  - Later pages: "Answers" section
      "N. <answer title>"
      "main (9).pdf · page P"
      <answer text>
      (repeat for each card)

  The first two lines of page 1 are: title + "main (9).pdf · source pages X, Y, Z, ..."
  After "Questions" (implicit), cards are listed.
  The answers section starts with the word "Answers" (sometimes at the top of a page).

Notes PDF: standard text pages; we insert "[Page N]" markers.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pymupdf  # type: ignore

from .models import CardSet, Flashcard


# ── Notes PDF ────────────────────────────────────────────────────────────────

def load_notes_text(
    notes_path: Path,
    page_start: int | None = None,
    page_end: int | None = None,
) -> dict[int, str]:
    """
    Returns {page_number: page_text} for the given page range (1-indexed, inclusive).
    If page_start/page_end are None, loads all pages.
    """
    doc = pymupdf.open(str(notes_path))
    result: dict[int, str] = {}

    start = (page_start or 1) - 1   # convert to 0-indexed
    end = (page_end or len(doc)) - 1

    for idx in range(start, min(end + 1, len(doc))):
        page_num = idx + 1  # 1-indexed
        text = doc[idx].get_text()
        result[page_num] = text

    doc.close()
    return result


def pages_to_text_with_markers(pages: dict[int, str]) -> str:
    """Concatenate pages with [Page N] markers."""
    parts = []
    for page_num in sorted(pages.keys()):
        parts.append(f"[Page {page_num}]\n{pages[page_num]}")
    return "\n\n".join(parts)


# ── Card PDF ─────────────────────────────────────────────────────────────────

# Matches "Card 3" or "Card 3\n" at start of a line (questions section)
_CARD_HEADER_RE = re.compile(r"^Card\s+(\d+)\s*$", re.MULTILINE)

# Matches answer block header like "3. Some Answer Title"
_ANSWER_HEADER_RE = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)

# Matches page reference in answer block "main ... · page 5"
_PAGE_REF_RE = re.compile(r"·\s*page\s+(\d+)", re.IGNORECASE)

# Matches source pages header "main (9).pdf · source pages 4, 5, 6, 7, 8"
_SOURCE_PAGES_RE = re.compile(r"source pages?\s+([\d,\s]+)", re.IGNORECASE)

# Filename pattern: "Flashcards · main (9).pdf · 4–8 level 1.pdf"
_FILENAME_RE = re.compile(
    r"(\d+)[–\-](\d+)\s+(.+?)(?:\s+level\s+(\d+))?$",
    re.IGNORECASE,
)

_TOPIC_MAP = {
    "math induction": "Mathematical Induction",
    "mathematical induction": "Mathematical Induction",
    "proofs": "Proofs",
    "numbers": "Numbers",
    "pigeonhole principle": "Pigeonhole Principle",
    "sets": "Sets",
    "sets easy": "Sets",
}


def _parse_filename(filename: str) -> tuple[str, str | None, int | None, int | None]:
    """
    Parse the card PDF filename into (topic, level, page_start, page_end).
    E.g. "Flashcards · main (9).pdf · 4–8 level 1.pdf"
      → ("Sets", "Level 1", 4, 8)
    """
    stem = Path(filename).stem
    # Strip "Flashcards · main (9).pdf · " prefix
    stem = re.sub(r"^Flashcards\s*·\s*main.*?·\s*", "", stem, flags=re.IGNORECASE).strip()

    m = re.match(r"(\d+)[–\-](\d+)\s+(.*)", stem)
    if not m:
        return stem, None, None, None

    page_start = int(m.group(1))
    page_end = int(m.group(2))
    rest = m.group(3).strip().lower()

    # Check for level suffix
    level_m = re.search(r"level\s+(\d+)", rest)
    level = f"Level {level_m.group(1)}" if level_m else None

    # Derive topic from the rest (without level)
    topic_key = re.sub(r"\s*level\s+\d+", "", rest).strip()
    # topic_key may be empty or 'sets easy' for the sets files
    topic = _TOPIC_MAP.get(topic_key, topic_key.title() if topic_key else "")

    return topic, level, page_start, page_end


def _read_pdf_title(pdf_path: Path) -> str:
    """Read the first two lines of the first page to get the document title."""
    try:
        doc = pymupdf.open(str(pdf_path))
        first_page_text = doc[0].get_text()
        doc.close()
        # Title is typically the first non-empty line
        for line in first_page_text.splitlines():
            line = line.strip()
            if line and not line.startswith("main"):
                return line
    except Exception:
        pass
    return ""


def load_card_pdf(pdf_path: Path) -> CardSet:
    """
    Parse a card PDF file into a CardSet with Flashcard objects.
    The PDF has two sections:
      - Questions: lists "Card N\\n<front text>"
      - Answers: lists "N. <title>\\nmain · page P\\n<back text>"
    """
    doc = pymupdf.open(str(pdf_path))
    all_text = ""
    for page in doc:
        all_text += page.get_text() + "\n<<<PAGE_BREAK>>>\n"

    # Read the PDF title from page 1 for topic fallback
    first_page_text = doc[0].get_text() if len(doc) > 0 else ""
    doc.close()

    topic, level, page_start, page_end = _parse_filename(pdf_path.name)

    # If topic is empty (e.g. '4-8 level N' files), extract it from the PDF title
    if not topic:
        # First line of the PDF is e.g. "Flashcards · main (9).pdf · 4–8 sets easy"
        for line in first_page_text.splitlines():
            line = line.strip()
            if line and not line.lower().startswith("main"):
                # Remove the filename-style prefix
                cleaned = re.sub(r"^Flashcards\s*·\s*main.*?·\s*", "", line, flags=re.IGNORECASE).strip()
                # Remove page range and level
                cleaned = re.sub(r"^\d+[–\-]\d+\s*", "", cleaned).strip()
                cleaned = re.sub(r"\s*level\s+\d+", "", cleaned, flags=re.IGNORECASE).strip().lower()
                topic = _TOPIC_MAP.get(cleaned, cleaned.title() if cleaned else "Sets")
                break
        if not topic:
            topic = "Sets"  # fallback for pages 4-8

    # ── Split into Questions and Answers sections ────────────────────────────
    # The answers section starts with a page that begins with "Answers"
    # (sometimes it's the first word on a fresh page)
    questions_text, answers_text = _split_sections(all_text)

    fronts = _parse_questions(questions_text)
    answers = _parse_answers(answers_text)

    # Merge
    cards: list[Flashcard] = []
    for num, front in fronts.items():
        ans = answers.get(num, {})
        cards.append(Flashcard(
            number=num,
            front=front.strip(),
            back=ans.get("back", "").strip(),
            page_ref=ans.get("page"),
            title=ans.get("title", ""),
        ))

    cards.sort(key=lambda c: c.number)

    return CardSet(
        topic=topic,
        card_type="Flashcards",
        level=level,
        page_start=page_start,
        page_end=page_end,
        cards=cards,
        source_file=pdf_path.name,
    )


def _split_sections(all_text: str) -> tuple[str, str]:
    """Split the full document text into questions and answers portions."""
    # Look for "Answers" standing alone on a line (possibly after a page break)
    split_re = re.compile(
        r"(?:<<<PAGE_BREAK>>>\s*)?Answers\s*\n",
        re.IGNORECASE,
    )
    m = split_re.search(all_text)
    if m:
        return all_text[: m.start()], all_text[m.end():]
    # Fallback: split at roughly halfway (shouldn't happen)
    mid = len(all_text) // 2
    return all_text[:mid], all_text[mid:]


def _parse_questions(text: str) -> dict[int, str]:
    """Extract {card_number: front_text} from the questions section."""
    # Remove page-break markers
    text = text.replace("<<<PAGE_BREAK>>>", "")

    matches = list(_CARD_HEADER_RE.finditer(text))
    fronts: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        front = text[start:end].strip()
        fronts[num] = front
    return fronts


def _parse_answers(text: str) -> dict[int, dict]:
    """Extract {card_number: {title, back, page}} from the answers section."""
    text = text.replace("<<<PAGE_BREAK>>>", "")
    matches = list(_ANSWER_HEADER_RE.finditer(text))
    answers: dict[int, dict] = {}

    for i, m in enumerate(matches):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        # Extract page reference
        page_m = _PAGE_REF_RE.search(block)
        page = int(page_m.group(1)) if page_m else None

        # Remove the page-reference line from the answer text
        back = _PAGE_REF_RE.sub("", block)
        # Remove lines starting with "main ... .pdf" (source file references)
        # These appear as "main (9).pdf \n" or "main (9).pdf · page N\n"
        back = re.sub(
            r"^main\s*\(?\d*\)?\.pdf.*",
            "",
            back,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        back = back.strip()

        answers[num] = {"title": title, "back": back, "page": page}

    return answers


def load_all_card_pdfs(cards_dir: Path) -> list[CardSet]:
    """Load every card PDF in the given directory."""
    sets = []
    for pdf in sorted(cards_dir.glob("*.pdf")):
        try:
            cs = load_card_pdf(pdf)
            sets.append(cs)
        except Exception as exc:
            print(f"[WARN] Failed to load {pdf.name}: {exc}")
    return sets


def match_excel_row_to_cardset(
    topic: str,
    card_type: str,
    level: str | None,
    card_sets: list[CardSet],
) -> CardSet | None:
    """Find the CardSet that matches an Excel row's (topic, type, level)."""
    topic_l = topic.strip().lower()
    type_l = card_type.strip().lower()
    level_l = (level or "").strip().lower()

    for cs in card_sets:
        cs_topic_l = cs.topic.strip().lower()
        cs_type_l = cs.card_type.strip().lower()
        cs_level_l = (cs.level or "").strip().lower()

        # Topic matching: allow partial matches for robustness
        topic_ok = (cs_topic_l == topic_l) or (topic_l in cs_topic_l) or (cs_topic_l in topic_l)
        type_ok = cs_type_l == type_l
        level_ok = cs_level_l == level_l

        if topic_ok and type_ok and level_ok:
            return cs

    # Fallback: topic + type only (if level is empty on both sides)
    if not level_l:
        for cs in card_sets:
            cs_topic_l = cs.topic.strip().lower()
            cs_type_l = cs.card_type.strip().lower()
            if cs_topic_l == topic_l and cs_type_l == type_l and not cs.level:
                return cs

    return None
