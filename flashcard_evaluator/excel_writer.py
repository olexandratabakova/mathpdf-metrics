"""
Excel writer: reads the original metrics spreadsheet and fills in results.
Never modifies the original — always writes a copy.
Also creates a 'Cards' sheet and a CSV with per-card data.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from .models import CardMetrics, DuplicatePair, SetMetrics


# Column headers for the new set-level columns we add to the right
_NEW_SET_COLS = [
    "self_contained_%",
    "faithfulness_avg",
    "front_leaks_%",
    "atomic_%",
    "understanding_%",
    "trivial_%",
    "dup_rate",
    "dup_pairs",
    "material_type_judged",
    "coverage_%",
    "difficulty_spearman",
    "avg_back_sentences",
    "card_type_dist",
    "n_cards_evaluated",
]

_CARD_COLS = [
    "set_topic",
    "set_level",
    "card_number",
    "front_preview",
    "self_contained_passes",
    "whats_missing",
    "blind_answer_matches",
    "faithfulness_ratio",
    "faithfulness_unsupported",
    "faithfulness_contradicts",
    "front_leaks_answer",
    "atomic",
    "card_type",
    "understanding_vs_rote",
    "trivial",
    "back_length_sentences",
    "difficulty",
    "judge_self_contained_note",
    "judge_faithfulness_note",
]


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _fmt_dup_pairs(pairs: list[DuplicatePair]) -> str:
    if not pairs:
        return ""
    return "; ".join(f"#{p.card_a}&#{p.card_b}({p.similarity:.2f})" for p in pairs)


def _fmt_card_type_dist(dist: dict[str, float]) -> str:
    if not dist:
        return ""
    return ", ".join(f"{k}:{v*100:.0f}%" for k, v in sorted(dist.items(), key=lambda x: -x[1]))


def write_output(
    original_excel: Path,
    set_results: list[SetMetrics],
    output_dir: Path,
    details_log_path: Path | None = None,
    details_log_data: list | None = None,
) -> tuple[Path, Path]:
    """
    Write results to:
    1. A copy of the original Excel with new columns + a 'Cards' sheet
    2. A CSV file with per-card data

    Returns (excel_path, csv_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_excel = output_dir / f"evaluation_results_{timestamp}.xlsx"
    out_csv = output_dir / f"cards_{timestamp}.csv"

    # ── Load original Excel ───────────────────────────────────────────────────
    wb = openpyxl.load_workbook(str(original_excel))
    ws = wb.active

    # ── Find existing columns (row 1 = headers) ───────────────────────────────
    existing_headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

    # Add new columns to the right (only if not already present)
    next_col = ws.max_column + 1
    new_col_indices: dict[str, int] = {}
    for col_name in _NEW_SET_COLS:
        if col_name not in existing_headers:
            ws.cell(1, next_col).value = col_name
            ws.cell(1, next_col).font = Font(bold=True)
            ws.cell(1, next_col).fill = PatternFill("solid", fgColor="D9E1F2")
            new_col_indices[col_name] = next_col
            next_col += 1
        else:
            new_col_indices[col_name] = existing_headers.index(col_name) + 1

    # ── Build lookup: (topic, type, level) → SetMetrics ──────────────────────
    result_map: dict[tuple[str, str, str], SetMetrics] = {}
    for sm in set_results:
        key = (
            sm.topic.strip().lower(),
            sm.card_type.strip().lower(),
            (sm.level or "").strip().lower(),
        )
        result_map[key] = sm

    # ── Fill in set rows ──────────────────────────────────────────────────────
    # Headers are row 1, descriptions are row 2, data starts at row 3
    for row_idx in range(3, ws.max_row + 1):
        topic_val = ws.cell(row_idx, 1).value
        type_val = ws.cell(row_idx, 2).value
        level_val = ws.cell(row_idx, 3).value

        if not topic_val or not type_val:
            continue

        key = (
            str(topic_val).strip().lower(),
            str(type_val).strip().lower(),
            str(level_val or "").strip().lower(),
        )
        sm = result_map.get(key)
        if sm is None:
            continue

        def _set(col_name: str, value):
            col = new_col_indices.get(col_name)
            if col:
                ws.cell(row_idx, col).value = value
                ws.cell(row_idx, col).alignment = Alignment(wrap_text=True)

        _set("self_contained_%", _pct(sm.pct_self_contained))
        _set("faithfulness_avg", _pct(sm.avg_faithfulness))
        _set("front_leaks_%", _pct(sm.pct_front_leaks))
        _set("atomic_%", _pct(sm.pct_atomic))
        _set("understanding_%", _pct(sm.pct_understanding))
        _set("trivial_%", _pct(sm.pct_trivial))
        _set("dup_rate", _pct(sm.duplicate_rate))
        _set("dup_pairs", _fmt_dup_pairs(sm.duplicate_pairs))
        _set("material_type_judged", sm.material_type)
        _set("coverage_%", _pct(sm.coverage_ratio))
        _set("difficulty_spearman", round(sm.difficulty_spearman, 3) if sm.difficulty_spearman is not None else "")
        _set("avg_back_sentences", round(sm.avg_back_length, 1))
        _set("card_type_dist", _fmt_card_type_dist(sm.card_type_distribution))
        _set("n_cards_evaluated", len(sm.card_metrics))

    # ── Auto-size new columns ─────────────────────────────────────────────────
    for col_name, col_idx in new_col_indices.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = 18

    # ── Create 'Cards' sheet ──────────────────────────────────────────────────
    if "Cards" in wb.sheetnames:
        del wb["Cards"]
    ws_cards = wb.create_sheet("Cards")

    # Write header row
    for ci, col_name in enumerate(_CARD_COLS, 1):
        cell = ws_cards.cell(1, ci, col_name)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E2EFDA")

    # Write data rows
    row_num = 2
    for sm in set_results:
        for cm in sm.card_metrics:
            sc = cm.self_contained
            faith = cm.faithfulness

            sc_note = ""
            if sc and not sc.passes:
                sc_note = sc.whats_missing or ("not understandable" if not sc.understandable else "")

            faith_note = ""
            if faith and faith.unsupported + faith.contradicts > 0:
                bads = [
                    f"{c.status}: {c.claim[:50]}"
                    for c in faith.claims
                    if c.status != "supported"
                ][:3]
                faith_note = " | ".join(bads)

            row = [
                sm.topic,
                sm.level or "",
                cm.card_number,
                cm.front[:120],
                int(sc.passes) if sc else "",
                sc.whats_missing if sc else "",
                int(sc.blind_answer_matches) if sc else "",
                round(faith.ratio, 3) if faith else "",
                faith.unsupported if faith else "",
                faith.contradicts if faith else "",
                int(cm.front_leaks_answer) if cm.front_leaks_answer is not None else "",
                int(cm.atomic) if cm.atomic is not None else "",
                cm.card_type_label,
                cm.understanding_vs_rote,
                int(cm.trivial) if cm.trivial is not None else "",
                cm.back_length_sentences,
                cm.difficulty or "",
                sc_note,
                faith_note,
            ]
            for ci, val in enumerate(row, 1):
                ws_cards.cell(row_num, ci, val)
            row_num += 1

    # Auto-size cards columns
    for ci in range(1, len(_CARD_COLS) + 1):
        ws_cards.column_dimensions[get_column_letter(ci)].width = 20

    # ── Save Excel ────────────────────────────────────────────────────────────
    wb.save(str(out_excel))

    # ── Write CSV ─────────────────────────────────────────────────────────────
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_CARD_COLS)
        for sm in set_results:
            for cm in sm.card_metrics:
                sc = cm.self_contained
                faith = cm.faithfulness
                writer.writerow([
                    sm.topic,
                    sm.level or "",
                    cm.card_number,
                    cm.front[:120],
                    int(sc.passes) if sc else "",
                    (sc.whats_missing if sc else ""),
                    int(sc.blind_answer_matches) if sc else "",
                    round(faith.ratio, 3) if faith else "",
                    (faith.unsupported if faith else ""),
                    (faith.contradicts if faith else ""),
                    int(cm.front_leaks_answer) if cm.front_leaks_answer is not None else "",
                    int(cm.atomic) if cm.atomic is not None else "",
                    cm.card_type_label,
                    cm.understanding_vs_rote,
                    int(cm.trivial) if cm.trivial is not None else "",
                    cm.back_length_sentences,
                    cm.difficulty or "",
                    "",  # sc_note
                    "",  # faith_note
                ])

    # ── Write details.jsonl ───────────────────────────────────────────────────
    if details_log_path and details_log_data:
        with open(details_log_path, "w", encoding="utf-8") as f:
            for entry in details_log_data:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return out_excel, out_csv
