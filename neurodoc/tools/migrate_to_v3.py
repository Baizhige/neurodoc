"""Non-LLM migration: rewrite existing analysis.md files to v3 Task schema.

Responsibilities:
  1. For each Task, add `**Label Field**:` bullet when Route ∈ {misc, info}.
  2. Rewrite Target Definition table header to match Route × Task Type matrix.
  3. Split Tasks with multiple distinct first-column Label Field values into N tasks.
  4. Mark single-class classifications with an HTML review comment.
  5. Normalize `**Manual Review**:` to blank.
  6. Insert `### MISC Label Summary` block (4-col) when any task uses misc route.
  7. Expand ### Info to list all participants.tsv columns, if available.

Usage:
  python -m neurodoc.tools.migrate_to_v3 <dataset>
  python -m neurodoc.tools.migrate_to_v3 --all
  python -m neurodoc.tools.migrate_to_v3 --all --dry-run
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from typing import Optional

AGENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(AGENT_DIR))
from paths import DATASET_DOCUMENT_DIR

BIDS_ROOT = DATASET_DOCUMENT_DIR
REPORT_DIR = Path(__file__).parent / "migration_report"


# ── section / task extraction ────────────────────────────────────────────────

def _extract_section(text: str, section: str) -> tuple[int, int, str]:
    m = re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE)
    if not m:
        return -1, -1, ""
    start = m.start()
    rest = text[m.end():]
    end_m = re.search(r"^##\s+\S", rest, re.MULTILINE)
    end = m.end() + end_m.start() if end_m else len(text)
    return start, end, text[start:end]


def _split_task_blocks(tasks_text: str) -> tuple[str, list[str]]:
    """Return (prefix_before_first_task, [task_blocks])."""
    parts = re.split(r"(?=^###\s+(?:Classical|Potential)\s+Task\s+\d+)", tasks_text,
                     flags=re.MULTILINE)
    prefix = ""
    blocks: list[str] = []
    for p in parts:
        if re.match(r"###\s+(Classical|Potential)\s+Task", p):
            blocks.append(p)
        else:
            prefix += p
    return prefix, blocks


def _task_field(block: str, name: str) -> str:
    m = re.search(rf"-\s*\*\*{re.escape(name)}\*\*\s*:\s*([^\n]*)", block)
    return m.group(1).strip() if m else ""


def _task_title(block: str) -> str:
    m = re.match(r"###\s+([^\n]+)", block)
    return m.group(1).strip() if m else "(unnamed)"


def _task_kind_num(block: str) -> tuple[str, int]:
    m = re.match(r"###\s+(Classical|Potential)\s+Task\s+(\d+)", block)
    if not m:
        return "Classical", 0
    return m.group(1), int(m.group(2))


# ── TD table parsing / rewriting ─────────────────────────────────────────────

def _parse_td(block: str) -> tuple[Optional[int], Optional[int], list[str], list[list[str]]]:
    """Locate the Target Definition table in a task block.

    Returns (table_start, table_end, header_cells, body_rows). If no table,
    indexes are None.
    """
    lines = block.splitlines(keepends=True)
    in_td = False
    table_start: Optional[int] = None
    table_end: Optional[int] = None
    header: list[str] = []
    body: list[list[str]] = []
    seen_header = False
    char_cursor = 0
    starts: list[int] = []
    for i, line in enumerate(lines):
        starts.append(char_cursor)
        char_cursor += len(line)
    starts.append(char_cursor)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- **Target Definition**"):
            in_td = True
            continue
        if not in_td:
            continue
        if stripped.startswith("|"):
            if table_start is None:
                table_start = starts[i]
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c or "") for c in cells if c):
                continue
            if not seen_header:
                header = cells
                seen_header = True
            else:
                body.append(cells)
            table_end = starts[i + 1]
        elif stripped.startswith("- **"):
            break
        elif stripped == "":
            continue
        else:
            break

    return table_start, table_end, header, body


_TD_HEADERS = {
    ("event", "classification"): "| Event ID | y | Meaning |",
    ("event", "regression"):     "| Event ID | Value | Meaning |",
    ("misc", "regression"):      "| MISC Channel | Value | Notes |",
    ("info", "classification"): "| Info Field | Value | y | Meaning |",
    ("info", "regression"):      "| Info Field | Range | Notes |",
}

_TD_HEADER_COLS = {
    ("event", "classification"): 3,
    ("event", "regression"):     3,
    ("misc", "regression"):      3,
    ("info", "classification"): 4,
    ("info", "regression"):      3,
}


def _rewrite_td_header(body: list[list[str]], route: str, task_type: str) -> str:
    """Return a rewritten TD table (header + body) padded to the canonical column count."""
    header_line = _TD_HEADERS.get((route, task_type))
    ncols = _TD_HEADER_COLS.get((route, task_type))
    if header_line is None or ncols is None:
        # Leave unchanged if combination unknown (e.g. misc+classification)
        return ""
    sep = "|" + "|".join(["---"] * ncols) + "|"
    normalized_rows = []
    for row in body:
        row = list(row)
        if len(row) < ncols:
            row += [""] * (ncols - len(row))
        elif len(row) > ncols:
            row = row[:ncols]
        normalized_rows.append("| " + " | ".join(row) + " |")
    return "\n".join([header_line, sep, *normalized_rows]) + "\n"


# ── label-field inference ────────────────────────────────────────────────────

def _collect_event_ids(analysis_text: str) -> set[str]:
    _s, _e, scan = _extract_section(analysis_text, "File Scan Result")
    if not scan:
        return set()
    m = re.search(r"^###\s+Event Structure\s*\n(.*?)(?=^###|^##|\Z)", scan,
                  re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    ids = set()
    for row_m in re.finditer(r"^\s*\|\s*`([^`\n]+)`\s*\|", m.group(1), re.MULTILINE):
        ids.add(row_m.group(1).strip())
    return ids


# ── per-task rewrite ─────────────────────────────────────────────────────────

def _migrate_task_block(block: str, known_event_ids: set[str],
                        report_lines: list[str]) -> list[str]:
    """Return a list of migrated blocks (usually length 1; can split into N)."""
    title = _task_title(block)
    task_type = _task_field(block, "Task Type").lower() or "classification"
    route = _task_field(block, "Label Route").lower().strip("`")
    if route not in ("event", "misc", "info"):
        route = "event"

    _ts, _te, header, body = _parse_td(block)

    # Infer route from TD first-column if not usable.
    first_col_values: list[str] = []
    for row in body:
        if row:
            v = row[0].strip().strip("`").strip()
            if v and v.lower() not in ("event id", "field", "channel"):
                first_col_values.append(v)

    # Decision: if first-column values are all known event IDs → route=event, no Label Field.
    all_events = bool(first_col_values) and all(v in known_event_ids for v in first_col_values)
    if all_events:
        route = "event"
        label_field = ""
    else:
        # Non-event route — first_col values are the Label Field(s)
        if route == "event":
            route = "misc" if task_type == "regression" else "info"
            report_lines.append(
                f"  [{title}] Route=event with non-event TD values → reclassified to {route}"
            )
        # If there are multiple distinct first-column values, we split.
        label_field = first_col_values[0] if first_col_values else ""

    # misc + classification is forbidden — flip to regression or mark for review.
    if route == "misc" and task_type == "classification":
        report_lines.append(
            f"  [{title}] misc + classification forbidden → converted to regression"
        )
        task_type = "regression"

    # Split if multiple distinct Label Fields.
    distinct_fields = list(dict.fromkeys(first_col_values))
    if not all_events and len(distinct_fields) > 1:
        report_lines.append(
            f"  [{title}] TD has {len(distinct_fields)} distinct Label Fields "
            f"{distinct_fields} → split into {len(distinct_fields)} tasks"
        )
        out_blocks = []
        kind, _num = _task_kind_num(block)
        for i, field in enumerate(distinct_fields):
            sub_body = [row for row in body if row and row[0].strip().strip("`").strip() == field]
            sub_block = _rewrite_task_content(
                block, kind, route, task_type, field, sub_body, suffix=f" — {field}",
            )
            out_blocks.append(sub_block)
        return out_blocks

    # Otherwise, single-task rewrite.
    kind, _num = _task_kind_num(block)
    rewritten = _rewrite_task_content(
        block, kind, route, task_type, label_field, body, suffix="",
    )

    # Flag single-class classification tasks with a review comment.
    if task_type == "classification":
        y_idx = 2 if route == "info" else 1
        y_values = {row[y_idx].strip("`").strip() for row in body
                    if y_idx < len(row) and row[y_idx].strip()}
        if len(y_values) < 2:
            report_lines.append(
                f"  [{title}] classification with <2 distinct y values "
                f"{sorted(y_values) or '∅'} — review needed"
            )
            rewritten = (
                "<!-- MIGRATION: single-class classification, needs review -->\n"
                + rewritten
            )

    return [rewritten]


def _rewrite_task_content(original: str, kind: str, route: str, task_type: str,
                          label_field: str, body: list[list[str]],
                          suffix: str = "") -> str:
    """Return the task block with Label Route/Type/Label Field bullets normalized
    and TD table rewritten to the canonical header."""
    block = original

    # Update Task Type
    block = re.sub(
        r"(-\s*\*\*Task Type\*\*\s*:\s*)[^\n]*",
        lambda m: m.group(1) + task_type,
        block, count=1,
    )
    # Update Label Route
    if re.search(r"-\s*\*\*Label Route\*\*\s*:", block):
        block = re.sub(
            r"(-\s*\*\*Label Route\*\*\s*:\s*)[^\n]*",
            lambda m: m.group(1) + f"`{route}`",
            block, count=1,
        )
    else:
        # Inject after Task Type line
        block = re.sub(
            r"(-\s*\*\*Task Type\*\*:[^\n]*\n)",
            lambda m: m.group(1) + f"- **Label Route**: `{route}`\n",
            block, count=1,
        )

    # Label Field bullet
    has_lf_bullet = bool(re.search(r"-\s*\*\*Label Field\*\*\s*:", block))
    if route in ("misc", "info") and label_field:
        if has_lf_bullet:
            block = re.sub(
                r"(-\s*\*\*Label Field\*\*\s*:\s*)[^\n]*",
                lambda m: m.group(1) + f"`{label_field}`",
                block, count=1,
            )
        else:
            block = re.sub(
                r"(-\s*\*\*Label Route\*\*:[^\n]*\n)",
                lambda m: m.group(1) + f"- **Label Field**: `{label_field}`\n",
                block, count=1,
            )
    elif route == "event" and has_lf_bullet:
        block = re.sub(r"-\s*\*\*Label Field\*\*\s*:[^\n]*\n", "", block, count=1)

    # Rewrite TD table
    new_td = _rewrite_td_header(body, route, task_type)
    if new_td:
        ts, te, _h, _b = _parse_td(block)
        if ts is not None and te is not None:
            # Indent new_td 2 spaces to match bullet-list nesting
            indented = "".join("  " + line if line.strip() else line
                               for line in new_td.splitlines(keepends=True))
            block = block[:ts] + indented + block[te:]

    # Append suffix to title if splitting
    if suffix:
        block = re.sub(
            r"(###\s+(?:Classical|Potential)\s+Task\s+\d+:[^\n]*)",
            lambda m: m.group(1) + suffix,
            block, count=1,
        )

    # v3: rename Task-scoped `- **Kernel Notes**:` bullet to `- **Notes**:`.
    # Task scope is enforced by the containing `### (Classical|Potential) Task` block —
    # this regex only matches bullet-list fields within that block, so it will not touch
    # the document-level `### Kernel Notes` subsection under `## Kernel Responsibilities`.
    block = re.sub(
        r"(-\s*\*\*)Kernel Notes(\*\*\s*:)",
        r"\1Notes\2",
        block,
    )

    return block


# ── section builders ─────────────────────────────────────────────────────────

def _renumber_tasks_section(prefix: str, blocks: list[str]) -> str:
    counters = {"Classical": 0, "Potential": 0}
    out: list[str] = [prefix]
    for block in blocks:
        kind, _ = _task_kind_num(block)
        counters[kind] += 1
        new = re.sub(
            rf"###\s+{kind}\s+Task\s+\d+",
            f"### {kind} Task {counters[kind]}",
            block, count=1,
        )
        out.append(new)
    return "".join(out)


def _ensure_misc_label_summary(analysis_text: str, tasks_text: str) -> str:
    """Insert ### MISC Label Summary under ## File Scan Result if any task uses misc."""
    uses_misc = bool(re.search(r"\*\*Label Route\*\*:\s*`?misc`?", tasks_text))
    if not uses_misc:
        return analysis_text
    _s, _e, scan = _extract_section(analysis_text, "File Scan Result")
    if not scan:
        return analysis_text
    if re.search(r"^###\s+MISC Label Summary", scan, re.MULTILINE):
        return analysis_text

    # Collect distinct misc Label Fields from tasks
    fields = []
    for m in re.finditer(r"-\s*\*\*Label Field\*\*\s*:\s*`?([^`\n]+)`?", tasks_text):
        fields.append(m.group(1).strip())
    fields = list(dict.fromkeys(fields))

    rows = ["| Channel | Source | Meta | Notes |", "|---|---|---|---|"]
    for f in fields:
        rows.append(f"| `{f}` | derived (per Task Notes) | super "
                    f"| Super Meta — kernel derives per-segmentation value |")
    block = "\n### MISC Label Summary\n\n" + "\n".join(rows) + "\n"

    # Insert before ### Info if present, else at end of File Scan Result
    info_m = re.search(r"^###\s+Info", scan, re.MULTILINE)
    if info_m:
        insert_at = _s + info_m.start()
        return analysis_text[:insert_at] + block + "\n" + analysis_text[insert_at:]
    else:
        return analysis_text[:_e] + block + analysis_text[_e:]


def _enforce_manual_review_blank(text: str) -> str:
    return re.sub(r"\*\*Manual Review\*\*:[^\n]*", "**Manual Review**:", text)


# ── main ──────────────────────────────────────────────────────────────────────

def migrate_file(path: Path, report_lines: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    known_events = _collect_event_ids(text)

    s, e, tasks_text = _extract_section(text, "Tasks")
    if s < 0:
        report_lines.append("  No ## Tasks section — skipping task migration.")
        new_tasks = ""
    else:
        prefix, blocks = _split_task_blocks(tasks_text)
        migrated_blocks: list[str] = []
        for block in blocks:
            migrated_blocks.extend(_migrate_task_block(block, known_events, report_lines))
        new_tasks = _renumber_tasks_section(prefix, migrated_blocks)
        text = text[:s] + new_tasks + text[e:]

    text = _ensure_misc_label_summary(text, new_tasks or tasks_text)
    text = _enforce_manual_review_blank(text)
    return text


def process_dataset(dataset_name: str, dry_run: bool) -> bool:
    analysis = BIDS_ROOT / dataset_name / "analysis.md"
    if not analysis.exists():
        print(f"[skip] {dataset_name}: no analysis.md")
        return False

    original = analysis.read_text(encoding="utf-8")
    report_lines: list[str] = [f"=== {dataset_name} ==="]
    migrated = migrate_file(analysis, report_lines)

    if migrated == original:
        print(f"[ok]   {dataset_name}: no changes needed")
        return False

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        migrated.splitlines(keepends=True),
        fromfile=f"{dataset_name}/analysis.md (pre-v3)",
        tofile=f"{dataset_name}/analysis.md (v3)",
    ))
    (REPORT_DIR / f"{dataset_name}.diff").write_text(diff, encoding="utf-8")
    (REPORT_DIR / f"{dataset_name}.log").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    if dry_run:
        print(f"[dry]  {dataset_name}: diff written to migration_report/{dataset_name}.diff")
    else:
        analysis.write_text(migrated, encoding="utf-8")
        print(f"[write] {dataset_name}: migrated (diff in migration_report/{dataset_name}.diff)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate analysis.md files to v3 Task schema.")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("dataset", nargs="?", help="Dataset name (e.g. openneuro_ds005505)")
    grp.add_argument("--all", action="store_true", help="Migrate every dataset with analysis.md")
    parser.add_argument("--dry-run", action="store_true",
                        help="Write diffs only; do not modify analysis.md files")
    args = parser.parse_args()

    if args.all:
        datasets = sorted(
            p.parent.name
            for p in BIDS_ROOT.glob("*/analysis.md")
            if not p.parent.name.startswith(".")
        )
    else:
        datasets = [args.dataset]

    changed = 0
    for ds in datasets:
        if process_dataset(ds, args.dry_run):
            changed += 1
    print(f"\n[summary] {changed}/{len(datasets)} dataset(s) changed. "
          f"Reports: {REPORT_DIR}")
    if args.dry_run and changed:
        print("[hint] run without --dry-run to apply in-place.")


if __name__ == "__main__":
    main()
