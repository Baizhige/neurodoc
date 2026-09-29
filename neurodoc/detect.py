"""
neurodoc - detect: batch check analysis.md and kernel files against semantic rulebook.

Usage:
    python detect.py --dataset openneuro_ds001784
    python detect.py --completed-only
    python detect.py --completed-only --severity error    # released / paper subset
    python detect.py --all                                # maintainer-only full sweep
    python detect.py --rulebook rulebook/semantic_rules.yaml  # custom rulebook

Output: per-dataset report with rule violations and a summary table.

Notes:
    --completed-only is the default review surface for the released corpus.
    --all is intended for maintainers performing repository-wide audits and may
    include draft / unreleased documents that are not part of the paper subset.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Callable

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not installed. Run: pip install pyyaml")

# ── Paths ──────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent
sys.path.insert(0, str(AGENT_DIR))
from paths import DATASET_DOCUMENT_DIR, KERNELS_DIR, PROGRESS_DIR, ROOT_DIR, RULEBOOK_DIR

BIDS_ROOT = ROOT_DIR
DEFAULT_RULEBOOK = RULEBOOK_DIR / "semantic_rules.yaml"

# Required top-level sections in mandatory order
_REQUIRED_SECTIONS = [
    "Paradigm",
    "File Scan Result",
    "Tasks",
    "Data Quality Notes",
    "Kernel Responsibilities",
]


# ── Section extraction helper ───────────────────────────────────────────────

def _extract_section(text: str, section_name: str) -> str:
    """Return the text of a ## section (from heading to next ## heading)."""
    start_m = re.search(
        rf"^##\s+{re.escape(section_name)}\s*$", text, re.MULTILINE
    )
    if not start_m:
        return ""
    rest = text[start_m.start():]
    # Find next ## heading (skip the first 3 chars "## " of the current section)
    end_m = re.search(r"^##\s+\S", rest[3:], re.MULTILINE)
    return rest[: end_m.start() + 3] if end_m else rest


# ── Cross-check registry ────────────────────────────────────────────────────

_CROSS_CHECKS: dict[str, Callable] = {}


def _cc(fn: Callable) -> Callable:
    """Decorator: register a function as a named cross-check."""
    _CROSS_CHECKS[fn.__name__] = fn
    return fn


# ── Cross-check implementations ─────────────────────────────────────────────
# Signature: (analysis_text, *, dataset_name="", kernel_text="") -> (violated, detail)


@_cc
def section_order(analysis_text: str, **_) -> tuple[bool, str]:
    """Top-level sections must appear in the required order."""
    positions: dict[str, int] = {}
    for name in _REQUIRED_SECTIONS:
        m = re.search(rf"^##\s+{re.escape(name)}\s*$", analysis_text, re.MULTILINE)
        if m:
            positions[name] = m.start()
    present = [n for n in _REQUIRED_SECTIONS if n in positions]
    sorted_by_pos = sorted(present, key=lambda n: positions[n])
    if sorted_by_pos != present:
        return True, f"out of order: got {sorted_by_pos}, expected {present}"
    return False, ""


@_cc
def no_extra_sections(analysis_text: str, **_) -> tuple[bool, str]:
    """Only the 5 required top-level ## sections are allowed."""
    allowed = set(_REQUIRED_SECTIONS)
    found = re.findall(r"^##\s+([^\n#][^\n]*?)\s*$", analysis_text, re.MULTILINE)
    extra = [s for s in found if s not in allowed]
    if extra:
        return True, f"unexpected ## sections: {extra}"
    return False, ""


@_cc
def super_meta_consistency(analysis_text: str, **_) -> tuple[bool, str]:
    """Super Meta Required must match actual Meta Level values in Tasks."""
    smr_m = re.search(r">\s*\*\*Super Meta Required\*\*:\s*(\S+)", analysis_text)
    if not smr_m:
        return False, ""  # missing field caught by field_value rule

    smr = smr_m.group(1).strip()
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""

    meta_levels = re.findall(
        r"\*\*Meta Level\*\*[^\n`]*`?(\braw\b|\bsuper\b)", tasks_text, re.IGNORECASE
    )
    has_super = any(ml.lower() == "super" for ml in meta_levels)

    if smr == "Yes" and not has_super:
        return True, "Super Meta Required=Yes but no task has Meta Level=super"
    if smr == "No" and has_super:
        return True, "Super Meta Required=No but at least one task has Meta Level=super"
    return False, ""


@_cc
def target_events_exist(analysis_text: str, **_) -> tuple[bool, str]:
    """Event IDs in Tasks Target Definition tables must appear in Event Structure.

    v3: only applied to tasks with Label Route = event. For misc/info routes, the
    first TD column holds the source channel/field name, not an event ID.
    """
    es_text = _extract_section(analysis_text, "File Scan Result")
    structure_ids: set[str] = set()
    for row_m in re.finditer(r"^\s*\|\s*`([^`\n]+)`\s*\|", es_text, re.MULTILINE):
        structure_ids.add(row_m.group(1).strip())

    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""

    referenced: set[str] = set()
    for block in _split_task_blocks(tasks_text):
        route = _task_field(block, "Label Route")
        if route.lower() != "event":
            continue
        for td_block in re.findall(
            r"(?:\*\*Target Definition\*\*:|####\s+Target Definition).*?(?=\n- \*\*\w|^####|^###|^##|\Z)",
            block, re.MULTILINE | re.DOTALL,
        ):
            for row_m in re.finditer(r"^\s*\|\s*`([^`\n]+)`\s*\|", td_block, re.MULTILINE):
                referenced.add(row_m.group(1).strip())

    missing = referenced - structure_ids
    if missing:
        return True, f"event IDs in Target Definition not in Event Structure: {sorted(missing)}"
    return False, ""


# ── v3 helpers: task-block extraction ───────────────────────────────────────

def _split_task_blocks(tasks_text: str) -> list[str]:
    """Split '## Tasks' section into Classical/Potential Task blocks."""
    parts = re.split(r"(?=^###\s+(?:Classical|Potential)\s+Task\s+\d+)", tasks_text,
                     flags=re.MULTILINE)
    return [p for p in parts if re.match(r"###\s+(Classical|Potential)\s+Task", p)]


def _task_field(block: str, field: str) -> str:
    """Return the value following `- **Field**: ` bullet (empty if absent)."""
    m = re.search(
        rf"-\s*\*\*{re.escape(field)}\*\*\s*:\s*([^\n]*)",
        block,
    )
    if not m:
        return ""
    val = m.group(1).strip()
    # Strip backticks wrapping a single token
    return val.strip("`").strip()


def _task_title(block: str) -> str:
    m = re.match(r"###\s+([^\n]+)", block)
    return m.group(1).strip() if m else "(unnamed)"


def _task_has_field(block: str, field: str) -> bool:
    return bool(re.search(rf"-\s*\*\*{re.escape(field)}\*\*\s*:", block))


def _task_target_def_table(block: str) -> tuple[list[str], list[list[str]]]:
    """Return (header_cells, body_rows) of the Target Definition table, empty if absent.

    Header and each body row are lists of trimmed cell strings (outer pipes stripped).
    Skips the markdown separator row.
    """
    lines = block.splitlines()
    in_td = False
    seen_header = False
    header: list[str] = []
    body: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- **Target Definition**"):
            in_td = True
            continue
        if in_td:
            if stripped.startswith("- **") and not stripped.startswith("|"):
                break
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                # Separator row
                if all(re.fullmatch(r":?-+:?", c or "") for c in cells if c):
                    continue
                if not seen_header:
                    header = cells
                    seen_header = True
                else:
                    body.append(cells)
    return header, body


def _extract_subsection(text: str, name: str) -> str:
    """Return text under a ### subsection heading until the next ### or ## heading."""
    m = re.search(rf"^###\s+{re.escape(name)}\s*\n", text, re.MULTILINE)
    if not m:
        return ""
    rest = text[m.end():]
    end_m = re.search(r"^(###\s+\S|##\s+\S)", rest, re.MULTILINE)
    return rest[: end_m.start()] if end_m else rest


def _first_column_backticked(table_text: str) -> set[str]:
    """Collect first-column values in markdown tables (stripping backticks)."""
    names: set[str] = set()
    for row_m in re.finditer(r"^\s*\|\s*`?([^|`\n]+)`?\s*\|", table_text, re.MULTILINE):
        val = row_m.group(1).strip()
        # Skip header row / separator
        if val.lower() in ("field", "channel", "event id"):
            continue
        if re.fullmatch(r":?-+:?", val):
            continue
        names.add(val)
    return names


# Expected Target Definition headers per Route × Task Type.
# Each entry is a canonical tuple of normalized column names (lowercased, unit-stripped).
_TD_HEADERS: dict[tuple[str, str], tuple[list[str], ...]] = {
    ("event", "classification"): (["event id", "y", "meaning"],),
    ("event", "regression"):     (["event id", "value", "meaning"],),
    ("misc", "classification"):  (["misc channel name", "y mapping notes"],),
    ("misc", "regression"):      (["misc channel name", "y mapping notes"],),
    ("info", "classification"):  (["info field", "y mapping notes"],),
    ("info", "regression"):      (["info field", "y mapping notes"],),
}


def _normalize_td_header(cells: list[str]) -> list[str]:
    """Normalize a TD header row for schema matching."""
    normalized = []
    for c in cells:
        c = c.lower().strip()
        # Strip parenthetical units, e.g. "value (unit)" → "value"
        c = re.sub(r"\s*\([^)]*\)", "", c).strip()
        normalized.append(c)
    return normalized


# ── v3 cross-checks ─────────────────────────────────────────────────────────


# ── v3.1 dispatchability cross-checks (participants.tsv + factory dry-run) ──


def _locate_participants_tsv(dataset_name: str) -> Path | None:
    """Best-effort search for <dataset>/participants.tsv using machine config roots."""
    if not dataset_name:
        return None
    try:
        import sys as _sys
        if str(AGENT_DIR) not in _sys.path:
            _sys.path.insert(0, str(AGENT_DIR))
        import scan_engine  # type: ignore
        cfg = scan_engine.load_machine_config()
        roots = cfg.get("dataset_roots") or []
        path = scan_engine.find_dataset_path(dataset_name, roots)
        if path:
            p = Path(path) / "participants.tsv"
            if p.exists():
                return p
    except Exception:
        pass
    return None


def _read_participants_columns(dataset_name: str) -> set[str] | None:
    """Return the set of column names in participants.tsv, or None if unreadable."""
    tsv = _locate_participants_tsv(dataset_name)
    if tsv is None:
        return None
    try:
        first_line = tsv.read_text(encoding="utf-8").splitlines()[0]
        return {c.strip() for c in first_line.split("\t") if c.strip()}
    except Exception:
        return None


def _parse_task_block_for_factory(block: str) -> dict:
    """Convert a markdown task block into the dict shape expected by build_dataset_from_task."""
    route = _task_field(block, "Label Route").lower() or None
    ttype = _task_field(block, "Task Type").lower() or None
    header, body = _task_target_def_table(block)
    norm = _normalize_td_header(header) if header else []

    td_source: str | None = None  # first TD row's first column (misc/info source field)
    rows: list[dict] = []
    for raw_cells in body:
        cells = [c.strip().strip("`").strip() for c in raw_cells]
        if not cells or not any(cells):
            continue
        if td_source is None and cells:
            td_source = cells[0]
        row: dict = {}
        for key, val in zip(norm, cells):
            if key == "event id":
                row["event_id"] = val
            elif key == "info field":
                row["info_field"] = val
                row["label_field"] = val  # backward compat for dataset_api
            elif key in ("misc channel name", "misc channel"):
                row["misc_channel"] = val
                row["label_field"] = val  # backward compat for dataset_api
            elif key == "y":
                try:
                    row["y"] = int(val)
                except (ValueError, TypeError):
                    row["y"] = val
            elif key == "y mapping notes":
                row["y_mapping_notes"] = val
            elif key == "value":
                if ttype == "regression" and route == "event":
                    try:
                        row["value"] = float(val)
                    except (ValueError, TypeError):
                        row["value"] = val
                else:
                    row["value"] = val
            elif key == "meaning":
                row["meaning"] = val
            elif key == "range":
                row["range"] = val
            elif key == "notes":
                row["notes"] = val
        rows.append(row)

    # label_field: for misc/info routes derive from TD first column; for event route it's None
    label_field = td_source if route in ("misc", "info") else None

    return {
        "label_route": route,
        "task_type": ttype,
        "label_field": label_field,
        "target_rows": rows,
    }


def _collect_kernel_misc_channels(dataset_name: str) -> set[str] | None:
    """Read kernel_requirements from progress JSON (if present) to get declared misc channels.

    Returns None when no progress file is available; the caller should treat
    missing data as 'cannot verify' rather than 'violated'.
    """
    if not dataset_name:
        return None
    progress_path = PROGRESS_DIR / f"{dataset_name}.json"
    if not progress_path.exists():
        return None
    try:
        data = __import__("json").loads(progress_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    req = (data.get("kernel_requirements") or {}) if isinstance(data, dict) else {}
    channels: set[str] = set()
    for n in (req.get("required_native_misc") or []):
        if isinstance(n, str) and n:
            channels.add(n)
    for d in (req.get("derived_misc_channels") or []):
        name = d.get("name") if isinstance(d, dict) else None
        if name:
            channels.add(name)
    return channels


@_cc
def task_dataset_dispatchable(analysis_text: str, **_) -> tuple[bool, str]:
    """Every Task must dispatch via build_dataset_from_task(dry_run=True)."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    try:
        try:
            from .dataset_api import DatasetDispatchError, build_dataset_from_task
        except Exception:
            from dataset_api import DatasetDispatchError, build_dataset_from_task
    except Exception as exc:
        return False, f"(dataset_api import failed: {exc})"

    problems: list[str] = []
    for block in _split_task_blocks(tasks_text):
        task = _parse_task_block_for_factory(block)
        try:
            build_dataset_from_task(task, dry_run=True)
        except DatasetDispatchError as exc:
            problems.append(f"{_task_title(block)} [{exc.kind}]: {exc.message}")
        except Exception as exc:
            problems.append(f"{_task_title(block)} [unexpected]: {exc}")
    if problems:
        return True, "; ".join(problems)
    return False, ""


@_cc
def target_def_schema_matches_route(analysis_text: str, **_) -> tuple[bool, str]:
    """TD table header must match the Route × Task Type canonical schema."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    problems: list[str] = []
    for block in _split_task_blocks(tasks_text):
        route = _task_field(block, "Label Route").lower()
        task_type = _task_field(block, "Task Type").lower()
        if not route or not task_type:
            continue
        expected_variants = _TD_HEADERS.get((route, task_type))
        if expected_variants is None:
            continue  # route/type combo not in schema matrix; skip
        header, _body = _task_target_def_table(block)
        if not header:
            problems.append(f"{_task_title(block)}: Target Definition table missing")
            continue
        normalized = _normalize_td_header(header)
        if not any(normalized == list(v) for v in expected_variants):
            expected_str = " | ".join(expected_variants[0])
            problems.append(
                f"{_task_title(block)} ({route}/{task_type}): header {header} "
                f"!= expected [{expected_str}]"
            )
    if problems:
        return True, "; ".join(problems)
    return False, ""


@_cc
def single_target_per_task(analysis_text: str, **_) -> tuple[bool, str]:
    """Target Definition first column (source field/channel) must have exactly one unique value per misc/info task."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    problems: list[str] = []
    for block in _split_task_blocks(tasks_text):
        route = _task_field(block, "Label Route").lower()
        if route not in ("misc", "info"):
            continue
        _header, body = _task_target_def_table(block)
        if not body:
            continue
        firsts = {row[0].strip("`").strip() for row in body if row and row[0]}
        if len(firsts) > 1:
            problems.append(
                f"{_task_title(block)}: multiple source values in TD first column — {sorted(firsts)}"
            )
    if problems:
        return True, "; ".join(problems)
    return False, ""


@_cc
def classification_task_has_multiple_classes(analysis_text: str, **_) -> tuple[bool, str]:
    """Classification tasks must have ≥2 distinct y values in Target Definition."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    bad: list[str] = []
    for block in _split_task_blocks(tasks_text):
        task_type = _task_field(block, "Task Type").lower()
        if task_type != "classification":
            continue
        route = _task_field(block, "Label Route").lower()
        if route in ("misc", "info"):
            continue  # misc/info use Y Mapping Notes; no discrete y column to validate
        header, body = _task_target_def_table(block)
        if not header or not body:
            bad.append(f"{_task_title(block)}: no TD rows")
            continue
        # Locate y column index
        normalized = _normalize_td_header(header)
        if "y" in normalized:
            y_idx = normalized.index("y")
        elif route == "event":
            y_idx = 1
        elif route == "info":
            y_idx = 2
        else:
            continue
        y_values = {row[y_idx].strip("`").strip() for row in body if y_idx < len(row) and row[y_idx].strip()}
        if len(y_values) < 2:
            bad.append(f"{_task_title(block)}: y values={sorted(y_values) or '[]'}")
    if bad:
        return True, f"classification tasks with <2 distinct y: {bad}"
    return False, ""


@_cc
def classification_y_zero_indexed_sequential(analysis_text: str, **_) -> tuple[bool, str]:
    """Classification tasks: distinct y values must be exactly {0, 1, ..., N-1}.

    Applies to event classification (col 'y') and info classification (col 'y').
    Many-to-one mapping is allowed (multiple Event IDs / Info values → same y).
    Rejects: string y labels, gapped y (e.g. {0, 2}), 1-based y (e.g. {1, 2}).
    """
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    bad: list[str] = []
    for block in _split_task_blocks(tasks_text):
        if _task_field(block, "Task Type").lower() != "classification":
            continue
        route = _task_field(block, "Label Route").lower()
        if route in ("misc", "info"):
            continue  # misc/info use Y Mapping Notes; no y column to validate
        header, body = _task_target_def_table(block)
        if not header or not body:
            continue
        normalized = _normalize_td_header(header)
        if "y" in normalized:
            y_idx = normalized.index("y")
        elif route == "event":
            y_idx = 1
        elif route == "info":
            y_idx = 2
        else:
            continue
        y_ints: set[int] = set()
        non_int: list[str] = []
        for row in body:
            if y_idx >= len(row):
                continue
            raw = row[y_idx].strip("`").strip()
            if not raw:
                continue
            try:
                y_ints.add(int(raw))
            except (ValueError, TypeError):
                non_int.append(raw)
        if non_int:
            bad.append(f"{_task_title(block)}: non-int y values {non_int}")
            continue
        if not y_ints:
            continue
        expected = set(range(len(y_ints)))
        if y_ints != expected:
            bad.append(
                f"{_task_title(block)}: y={sorted(y_ints)} != expected 0..{len(y_ints)-1} "
                f"(y must be 0-based sequential; many-to-one merges OK but no gaps or offset)"
            )
    if bad:
        return True, "; ".join(bad)
    return False, ""


@_cc
def derived_misc_requires_super_meta(analysis_text: str, **_) -> tuple[bool, str]:
    """Route=misc TD channel not listed as native in MISC Label Summary → Meta Level must be super."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    misc_text = _extract_subsection(_extract_section(analysis_text, "File Scan Result"),
                                     "MISC Label Summary")
    native_names: set[str] = set()
    for row_m in re.finditer(r"^\s*\|\s*`([^`\n]+)`\s*\|\s*native", misc_text,
                              re.MULTILINE | re.IGNORECASE):
        native_names.add(row_m.group(1).strip())
    bad: list[str] = []
    for block in _split_task_blocks(tasks_text):
        route = _task_field(block, "Label Route").lower()
        if route != "misc":
            continue
        _header, body = _task_target_def_table(block)
        if not body or not body[0]:
            continue
        channel = body[0][0].strip().strip("`").strip()
        if not channel:
            continue
        meta = _task_field(block, "Meta Level").lower()
        if channel not in native_names and meta != "super":
            bad.append(f"{_task_title(block)}: channel={channel!r} is derived but Meta Level={meta!r}")
    if bad:
        return True, "; ".join(bad)
    return False, ""


@_cc
def segmentation_requires_empty_target_events(analysis_text: str, **_) -> tuple[bool, str]:
    """epoch_by_segmentation_hdf5 => target_events must be empty."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    bad: list[str] = []
    for block in _split_task_blocks(tasks_text):
        method = _task_field(block, "Epoch Method").lower()
        if "segmentation" not in method:
            continue
        params = _task_field(block, "Epoch Parameters")
        # Look for target_events = [ ... ] with any non-whitespace, non-empty content
        m = re.search(r"target_events\s*=\s*\[([^\]]*)\]", params)
        if not m:
            continue
        inner = m.group(1).strip()
        if inner:
            bad.append(f"{_task_title(block)}: target_events={inner!r}")
    if bad:
        return True, f"segmentation tasks with non-empty target_events: {bad}"
    return False, ""


_EPOCH_METHOD_REQUIRED_KEYS: dict[str, set[str]] = {
    "epoch_by_event_hdf5": {"tmin", "tmax", "target_events"},
    "epoch_by_long_event_hdf5": {"tmin", "tmax", "overlap", "target_events"},
    "epoch_by_segmentation_hdf5": {"segment_length", "overlap"},
}


@_cc
def epoch_parameters_complete(analysis_text: str, **_) -> tuple[bool, str]:
    """Each Task's Epoch Parameters must contain the minimum keys for its Epoch Method
    (rulebook Articles 49–52). Extra MNE keys are allowed; only the minimum set is enforced."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""
    missing: list[str] = []
    for block in _split_task_blocks(tasks_text):
        raw_method = _task_field(block, "Epoch Method")
        method = raw_method.strip().strip("`").lower()
        required = _EPOCH_METHOD_REQUIRED_KEYS.get(method)
        if not required:
            # Unknown/absent Epoch Method — a different rule already flags this; skip.
            continue
        params = _task_field(block, "Epoch Parameters")
        present = {m.group(1) for m in re.finditer(r"\b(\w+)\s*=", params)}
        absent = sorted(required - present)
        if absent:
            missing.append(f"{_task_title(block)}: [{method}] missing {absent}")
    if missing:
        return True, "; ".join(missing)
    return False, ""


@_cc
def misc_route_requires_section(analysis_text: str, **_) -> tuple[bool, str]:
    """Label Route=misc requires ### MISC Label Summary to exist."""
    has_misc_route = bool(
        re.search(r"\*\*Label Route\*\*[^\n]*\bmisc\b", analysis_text, re.IGNORECASE)
    )
    has_misc_section = bool(
        re.search(r"^###\s+MISC Label Summary", analysis_text, re.MULTILINE)
    )
    if has_misc_route and not has_misc_section:
        return True, "Label Route=misc used but ### MISC Label Summary is absent"
    return False, ""


@_cc
def classical_task_evidence(analysis_text: str, **_) -> tuple[bool, str]:
    """Every Classical Task must have a non-empty Evidence field."""
    tasks_text = _extract_section(analysis_text, "Tasks")
    if not tasks_text:
        return False, ""

    blocks = re.split(r"(?=^###\s+Classical Task)", tasks_text, flags=re.MULTILINE)
    missing: list[str] = []

    for block in blocks:
        if not re.match(r"###\s+Classical Task", block):
            continue
        title_m = re.match(r"###\s+(Classical Task[^\n]+)", block)
        title = title_m.group(1).strip() if title_m else "unknown"

        ev_m = re.search(
            r"\*\*Evidence\*\*:\s*(.+?)(?=\n>\s*\*\*|\n###|\n##|\Z)", block, re.DOTALL
        )
        if not ev_m:
            missing.append(title)
            continue
        content = ev_m.group(1).strip()
        if not content or content in ("N/A", "none", "TODO", "-"):
            missing.append(title)

    if missing:
        return True, f"Classical Tasks without Evidence: {missing}"
    return False, ""


@_cc
def info_completeness_values(analysis_text: str, **_) -> tuple[bool, str]:
    """### Info table Completeness column must use valid values only."""
    partial_re = re.compile(r"^partial \(\d+/\d+\)$")

    info_m = re.search(
        r"###\s+Info\s*\n(.*?)(?=^###|^##|\Z)", analysis_text, re.MULTILINE | re.DOTALL
    )
    if not info_m:
        return False, ""  # missing section caught elsewhere

    info_text = info_m.group(1)
    invalid: list[str] = []

    for row_m in re.finditer(
        r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|", info_text, re.MULTILINE
    ):
        field = row_m.group(1).strip()
        completeness = row_m.group(2).strip().lower()
        # Skip header / separator rows
        if "---" in completeness or completeness in ("completeness",):
            continue
        if "---" in field or field.lower() in ("field",):
            continue
        if completeness in {"complete", "incomplete", "missing"}:
            continue
        if partial_re.match(completeness):
            continue
        else:
            invalid.append(f"{field!r}: {completeness!r}")

    if invalid:
        return True, f"invalid Completeness values in ### Info: {invalid}"
    return False, ""


@_cc
def kernel_sha256_matches(
    analysis_text: str, dataset_name: str = "", **_
) -> tuple[bool, str]:
    """Kernel SHA256 in document must match the effective scan kernel file."""
    if not dataset_name:
        return False, ""

    field_m = re.search(
        r">\s*\*\*Kernel SHA256\*\*:\s*`?([^`\n]+)`?", analysis_text
    )
    if not field_m:
        return False, ""  # missing fingerprint caught by kernel_fingerprint_exists

    doc_value = field_m.group(1).strip()

    specific_kernel: Path | None = None
    direct_kernel = KERNELS_DIR / f"{dataset_name}.py"
    if direct_kernel.exists():
        specific_kernel = direct_kernel
    else:
        for sub in KERNELS_DIR.iterdir():
            if sub.is_dir():
                candidate = sub / f"{dataset_name}.py"
                if candidate.exists():
                    specific_kernel = candidate
                    break

    if not kernel_path.exists():
        return True, f"kernel file not found — cannot verify SHA256 (doc: {doc_sha[:16]}…)"

    raw = kernel_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != doc_sha:
        return (
            True,
            f"SHA256 mismatch: doc={doc_sha[:16]}… file={actual_sha[:16]}…"
            f"— rerun scan to update fingerprint",
        )
    return False, ""


@_cc
def kernel_sha256_matches(
    analysis_text: str, dataset_name: str = "", **_
) -> tuple[bool, str]:
    """Kernel SHA256 in document must match the effective scan kernel file."""
    if not dataset_name:
        return False, ""

    field_m = re.search(
        r">\s*\*\*Kernel SHA256\*\*:\s*`?([^`\n]+)`?", analysis_text
    )
    if not field_m:
        return False, ""

    doc_value = field_m.group(1).strip()

    specific_kernel: Path | None = None
    direct_kernel = KERNELS_DIR / f"{dataset_name}.py"
    if direct_kernel.exists():
        specific_kernel = direct_kernel
    else:
        for sub in KERNELS_DIR.iterdir():
            if sub.is_dir():
                candidate = sub / f"{dataset_name}.py"
                if candidate.exists():
                    specific_kernel = candidate
                    break

    effective_kernel = specific_kernel
    if effective_kernel is None:
        try:
            from scan_engine import detect_kernel_path as _detect_kernel_path
        except Exception:
            _detect_kernel_path = None
        if _detect_kernel_path is not None:
            kernel_path = _detect_kernel_path(dataset_name)
            if kernel_path:
                candidate = Path(kernel_path)
                if not candidate.is_absolute():
                    candidate = ROOT_DIR / kernel_path
                if candidate.exists():
                    effective_kernel = candidate

    generic_ok = effective_kernel is None or effective_kernel.name == "bids.py"

    if doc_value == "N/A":
        if specific_kernel is not None:
            return True, "Kernel SHA256 is `N/A` but a dataset-specific kernel file exists"
        if generic_ok:
            return False, ""
        return True, "Kernel SHA256 is `N/A` but scan uses a concrete shared kernel file"

    if not re.fullmatch(r"[a-f0-9]{64}", doc_value):
        return True, f"invalid Kernel SHA256 value: {doc_value!r}"

    if effective_kernel is None:
        return True, f"kernel file not found; cannot verify SHA256 (doc: {doc_value[:16]}...)"

    raw = effective_kernel.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != doc_value:
        return (
            True,
            f"SHA256 mismatch: doc={doc_value[:16]}... file={actual_sha[:16]}... rerun scan to update fingerprint",
        )
    return False, ""


@_cc
def no_mi_on_phase_markers(analysis_text: str, **_) -> tuple[bool, str]:
    """Event Structure must not assign MI labels to trial-phase-marker events."""
    PHASE_KW = {
        "trial phase", "rest", "ready", "task onset", "interval onset",
        "inter-trial", "fixation", "baseline",
    }
    MI_KW = {
        "left hand mi", "right hand mi", "feet mi", "tongue mi",
        "motor imagery cue", "mi - class", "mi class",
    }

    es_m = re.search(
        r"###\s+Event Structure\s*\n(.*?)(?=^###|^##|\Z)",
        analysis_text, re.MULTILINE | re.DOTALL,
    )
    if not es_m:
        return False, ""

    violations: list[str] = []
    for row_m in re.finditer(r"^\|([^\n]+)\|", es_m.group(1), re.MULTILINE):
        cols = [c.strip() for c in row_m.group(0).split("|")]
        if len(cols) < 6:
            continue
        meaning = cols[5].lower()
        has_phase = any(kw in meaning for kw in PHASE_KW)
        has_mi = any(kw in meaning for kw in MI_KW)
        if has_phase and has_mi:
            violations.append(f"{cols[1]}: {cols[5][:70]}")

    if violations:
        return True, f"phase-marker events with MI labels: {violations}"
    return False, ""


@_cc
def kr_has_super_meta(analysis_text: str, **_) -> tuple[bool, str]:
    """KR section must contain > **Super Meta Required**: field."""
    kr = _extract_section(analysis_text, "Kernel Responsibilities")
    if kr is None:
        return False, ""
    if not re.search(r">\s*\*\*Super Meta Required\*\*:", kr):
        return True, "## Kernel Responsibilities missing > **Super Meta Required**: field"
    return False, ""


@_cc
def kr_has_status(analysis_text: str, **_) -> tuple[bool, str]:
    """KR section must contain > **Status**: field."""
    kr = _extract_section(analysis_text, "Kernel Responsibilities")
    if kr is None:
        return False, ""
    if not re.search(r">\s*\*\*Status\*\*:", kr):
        return True, "## Kernel Responsibilities missing > **Status**: field"
    return False, ""


@_cc
def kr_only_blockquote_fields(analysis_text: str, **_) -> tuple[bool, str]:
    """KR section should only contain blockquote fields, no extra prose."""
    kr = _extract_section(analysis_text, "Kernel Responsibilities")
    if kr is None:
        return False, ""
    extra_lines = []
    for line in kr.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith(">"):
            continue
        extra_lines.append(stripped[:60])
    if extra_lines:
        return True, f"extra content in KR section (should be blockquote only): {extra_lines[:3]}"
    return False, ""


@_cc
def dqn_bullet_format(analysis_text: str, **_) -> tuple[bool, str]:
    """DQN content must use '- ' bullet format."""
    dqn = _extract_section(analysis_text, "Data Quality Notes")
    if dqn is None:
        return False, ""
    bad_lines = []
    for line in dqn.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            continue
        bad_lines.append(stripped[:60])
    if bad_lines:
        return True, f"non-bullet lines in DQN (use '- ' prefix): {bad_lines[:3]}"
    return False, ""


@_cc
def completed_manual_review_required(analysis_text: str, **_) -> tuple[bool, str]:
    """Completed documents must record at least one reviewer name."""
    status_m = re.search(r">\s*\*\*Status\*\*:\s*([^\n]+)", analysis_text)
    review_m = re.search(r"\*\*Manual Review\*\*:\s*([^\n]*)", analysis_text)
    if not status_m or not review_m:
        return False, ""

    status = status_m.group(1).strip()
    reviewer = review_m.group(1).strip()
    if status == "completed" and not reviewer:
        return True, "Status=completed but Manual Review is blank"
    return False, ""


@_cc
def task_order_classical_first(analysis_text: str, **_) -> tuple[bool, str]:
    """All Classical Tasks must appear before all Potential Tasks."""
    headings = re.findall(
        r"###\s+(Classical|Potential)\s+Task\s+\d+", analysis_text
    )
    if not headings:
        return False, ""
    seen_potential = False
    for kind in headings:
        if kind == "Potential":
            seen_potential = True
        elif kind == "Classical" and seen_potential:
            return True, "Classical Task appears after Potential Task"
    return False, ""


@_cc
def task_numbering_from_one(analysis_text: str, **_) -> tuple[bool, str]:
    """Each task type must be numbered from 1 consecutively."""
    headings = re.findall(
        r"###\s+(Classical|Potential)\s+Task\s+(\d+)", analysis_text
    )
    if not headings:
        return False, ""
    by_type: dict[str, list[int]] = {}
    for kind, num_str in headings:
        by_type.setdefault(kind, []).append(int(num_str))
    problems = []
    for kind, nums in by_type.items():
        expected = list(range(1, len(nums) + 1))
        if nums != expected:
            problems.append(f"{kind}: got {nums}, expected {expected}")
    if problems:
        return True, "; ".join(problems)
    return False, ""


# ── Core check engine ───────────────────────────────────────────────────────

def _check_pattern(text: str, rule: dict) -> bool:
    """Return True if rule is violated."""
    require_match = rule.get("require_match", False)
    flags = re.MULTILINE
    if not rule.get("case_sensitive", False):
        flags |= re.IGNORECASE
    found = bool(re.search(rule.get("pattern", ""), text, flags))
    return not found if require_match else found


def _check_section_exists(text: str, rule: dict) -> bool:
    """Return True if rule is violated (section missing)."""
    return rule.get("section", "") not in text


def _check_field_value(text: str, rule: dict) -> tuple[bool, str]:
    """Extract a named field value and check it against allowed_values."""
    allowed = [str(v).strip() for v in rule.get("allowed_values", [])]
    m = re.search(rule.get("field_pattern", ""), text, re.MULTILINE)
    if not m:
        return False, ""  # absent field handled by section_exists rules

    value = m.group(1).strip()
    # Strip trailing pipe (inline meta: "**Category**: X | **Subjects**: 30")
    value = value.split("|")[0].strip()

    if value not in allowed:
        return True, f"invalid value: {value!r} — allowed: {', '.join(allowed)}"
    return False, ""


def _check_rule(
    text: str,
    rule: dict,
    dataset_name: str = "",
    kernel_text: str = "",
) -> tuple[bool, str]:
    """Dispatch to the appropriate check. Returns (violated, detail)."""
    check_type = rule.get("check", "pattern")

    if check_type == "pattern":
        violated = _check_pattern(text, rule)
        if violated:
            pat_flags = re.MULTILINE
            if not rule.get("case_sensitive", False):
                pat_flags |= re.IGNORECASE
            m = re.search(rule.get("pattern", ""), text, pat_flags)
            detail = (
                f"matched: {m.group()[:80]!r}"
                if m and not rule.get("require_match")
                else "(pattern not found)"
            )
        else:
            detail = ""

    elif check_type == "section_exists":
        violated = _check_section_exists(text, rule)
        detail = f"section '{rule.get('section')}' missing" if violated else ""

    elif check_type == "field_value":
        violated, detail = _check_field_value(text, rule)

    elif check_type == "cross_check":
        fn_name = rule.get("function", "")
        fn = _CROSS_CHECKS.get(fn_name)
        if fn is None:
            return False, f"(cross_check '{fn_name}' not yet implemented — add to detect.py)"
        violated, detail = fn(
            text, dataset_name=dataset_name, kernel_text=kernel_text
        )

    else:
        return False, f"(unknown check type: {check_type!r})"

    # context_require_absent: suppress violation if sentinel string is in text
    if violated and "context_require_absent" in rule:
        if rule["context_require_absent"] in text:
            violated = False
            detail = ""

    return violated, detail


def _analysis_allows_no_dataset_kernel(analysis_text: str, dataset_name: str) -> bool:
    """Return True when kernel-target rules may be skipped for this dataset."""
    if not analysis_text or not dataset_name:
        return False

    field_m = re.search(
        r">\s*\*\*Kernel SHA256\*\*:\s*`?([^`\n]+)`?", analysis_text
    )
    if not field_m or field_m.group(1).strip() != "N/A":
        return False

    direct_kernel = KERNELS_DIR / f"{dataset_name}.py"
    if direct_kernel.exists():
        return False
    for sub in KERNELS_DIR.iterdir():
        if sub.is_dir() and (sub / f"{dataset_name}.py").exists():
            return False

    try:
        from scan_engine import detect_kernel_path as _detect_kernel_path
    except Exception:
        _detect_kernel_path = None

    if _detect_kernel_path is None:
        return True

    kernel_path = _detect_kernel_path(dataset_name)
    if not kernel_path:
        return True
    return Path(kernel_path).name == "bids.py"


# ── In-memory checker (used by NeuroAudit server) ───────────────────────────

def load_rules(rulebook_path: Path | str | None = None) -> list[dict]:
    """Load the semantic rulebook. Caller-friendly wrapper around yaml.safe_load."""
    path = Path(rulebook_path) if rulebook_path else DEFAULT_RULEBOOK
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("rules", []) or []


def check_analysis_text(
    analysis_text: str,
    dataset_name: str = "",
    kernel_text: str = "",
    severity_filter: str | None = None,
    rules: list[dict] | None = None,
    rulebook_path: Path | str | None = None,
) -> list[dict]:
    """Run rules against an in-memory analysis.md string (no disk I/O).

    Used by neuroaudit/server.py to validate unsaved content. Skips rules whose
    `target` is `kernel` when no kernel_text is supplied.
    """
    if rules is None:
        rules = load_rules(rulebook_path)

    violations: list[dict] = []
    for rule in rules:
        sev = rule.get("severity", "warning")
        if severity_filter and sev != severity_filter:
            continue

        target = rule.get("target", "analysis_md")
        texts_to_check: list[tuple[str, str]] = []
        if target in ("analysis_md", "both") and analysis_text:
            texts_to_check.append(("analysis_md", analysis_text))
        if target in ("kernel", "both") and kernel_text:
            texts_to_check.append(("kernel", kernel_text))
        elif target in ("kernel", "both") and _analysis_allows_no_dataset_kernel(analysis_text, dataset_name):
            continue

        for file_type, text in texts_to_check:
            violated, detail = _check_rule(
                text, rule, dataset_name=dataset_name, kernel_text=kernel_text
            )
            if violated:
                violations.append({
                    "dataset": dataset_name,
                    "rule_id": rule["id"],
                    "severity": sev,
                    "target": file_type,
                    "desc": rule.get("desc", ""),
                    "detail": detail,
                })
    return violations


# ── Dataset checker ─────────────────────────────────────────────────────────

def check_dataset(
    dataset_name: str, rules: list[dict], severity_filter: str | None
) -> list[dict]:
    """Check one dataset. Returns list of violation dicts."""
    violations: list[dict] = []

    analysis_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    kernel_path = KERNELS_DIR / f"{dataset_name}.py"
    if not kernel_path.exists():
        for sub in KERNELS_DIR.iterdir():
            if sub.is_dir():
                candidate = sub / f"{dataset_name}.py"
                if candidate.exists():
                    kernel_path = candidate
                    break

    analysis_text = (
        analysis_path.read_text(encoding="utf-8") if analysis_path.exists() else ""
    )
    kernel_text = (
        kernel_path.read_text(encoding="utf-8") if kernel_path.exists() else ""
    )

    for rule in rules:
        sev = rule.get("severity", "warning")
        if severity_filter and sev != severity_filter:
            continue

        target = rule.get("target", "analysis_md")
        texts_to_check: list[tuple[str, str]] = []

        if target in ("analysis_md", "both"):
            if analysis_text:
                texts_to_check.append(("analysis_md", analysis_text))
            elif target == "analysis_md":
                violations.append({
                    "dataset": dataset_name,
                    "rule_id": rule["id"],
                    "severity": sev,
                    "target": "analysis_md",
                    "detail": "analysis.md not found",
                })
                continue

        if target in ("kernel", "both"):
            if kernel_text:
                texts_to_check.append(("kernel", kernel_text))
            elif _analysis_allows_no_dataset_kernel(analysis_text, dataset_name):
                continue
            elif target == "kernel":
                violations.append({
                    "dataset": dataset_name,
                    "rule_id": rule["id"],
                    "severity": sev,
                    "target": "kernel",
                    "detail": "kernel file not found",
                })
                continue

        for file_type, text in texts_to_check:
            violated, detail = _check_rule(
                text, rule, dataset_name=dataset_name, kernel_text=kernel_text
            )
            if violated:
                violations.append({
                    "dataset": dataset_name,
                    "rule_id": rule["id"],
                    "severity": sev,
                    "target": file_type,
                    "desc": rule.get("desc", ""),
                    "detail": detail,
                })

    return violations


# ── Report output ───────────────────────────────────────────────────────────

def _print_report(all_violations: list[dict], datasets: list[str]) -> None:
    SEV_ORDER = {"error": 0, "warning": 1, "info": 2}
    all_violations.sort(
        key=lambda v: (v["dataset"], SEV_ORDER.get(v["severity"], 9), v["rule_id"])
    )

    current_ds = None
    for v in all_violations:
        if v["dataset"] != current_ds:
            current_ds = v["dataset"]
            print(f"\n{'─' * 60}")
            print(f"  {current_ds}")
            print(f"{'─' * 60}")
        icon = {"error": "X", "warning": "!", "info": "i"}.get(v["severity"], "?")
        print(
            f"  [{icon}] [{v['severity'].upper():7}] [{v['target']:11}] {v['rule_id']}"
        )
        if v.get("desc"):
            print(f"          {v['desc']}")
        if v.get("detail"):
            print(f"          → {v['detail']}")

    print(f"\n{'=' * 60}")
    n_err = sum(1 for v in all_violations if v["severity"] == "error")
    n_warn = sum(1 for v in all_violations if v["severity"] == "warning")
    n_clean = sum(
        1 for ds in datasets
        if not any(v["dataset"] == ds for v in all_violations)
    )
    print(
        f"  Checked: {len(datasets)} datasets | Clean: {n_clean} | "
        f"Errors: {n_err} | Warnings: {n_warn}"
    )
    print()


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "neurodoc: semantic rule checker. Use --completed-only for the "
            "released / paper subset; reserve --all for maintainer-wide audits."
        )
    )
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dataset", "-d", nargs="+", help="Dataset name(s) to check")
    grp.add_argument(
        "--completed-only",
        action="store_true",
        help="Check only documents whose Status is completed (recommended for released corpus review)",
    )
    grp.add_argument(
        "--all",
        action="store_true",
        help="Maintainer mode: check every dataset document with analysis.md, including draft / unreleased entries",
    )
    parser.add_argument(
        "--severity", choices=["error", "warning", "info"],
        help="Only show violations of this severity level",
    )
    parser.add_argument(
        "--rulebook", default=str(DEFAULT_RULEBOOK),
        help=f"Path to rulebook YAML (default: {DEFAULT_RULEBOOK})",
    )
    args = parser.parse_args()

    rulebook_path = Path(args.rulebook)
    if not rulebook_path.exists():
        sys.exit(f"ERROR: Rulebook not found: {rulebook_path}")

    rules: list[dict] = (
        yaml.safe_load(rulebook_path.read_text(encoding="utf-8")).get("rules", [])
    )

    cross_check_rules = [r for r in rules if r.get("check") == "cross_check"]
    implemented = sum(
        1 for r in cross_check_rules if r.get("function") in _CROSS_CHECKS
    )
    print(
        f"[detect] Loaded {len(rules)} rules from {rulebook_path.name} "
        f"({implemented}/{len(cross_check_rules)} cross-checks implemented)"
    )

    if args.all:
        datasets = sorted(
            p.parent.name
            for p in DATASET_DOCUMENT_DIR.glob("*/analysis.md")
            if not p.parent.name.startswith(".")
        )
    elif args.completed_only:
        datasets = []
        for p in DATASET_DOCUMENT_DIR.glob("*/analysis.md"):
            if p.parent.name.startswith("."):
                continue
            text = p.read_text(encoding="utf-8")
            if re.search(r">\s*\*\*Status\*\*:\s*completed\b", text):
                datasets.append(p.parent.name)
        datasets = sorted(datasets)
    else:
        datasets = []
        for item in args.dataset:
            datasets.extend(d.strip() for d in item.split(",") if d.strip())
        datasets = list(dict.fromkeys(datasets))

    print(f"[detect] Checking {len(datasets)} dataset(s)…\n")

    all_violations: list[dict] = []
    for ds in datasets:
        viols = check_dataset(ds, rules, args.severity)
        all_violations.extend(viols)

    _print_report(all_violations, datasets)

    if any(v["severity"] == "error" for v in all_violations):
        sys.exit(1)


if __name__ == "__main__":
    main()
