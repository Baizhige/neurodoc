"""
scan_engine.py — Core logic for app_scan.
Handles: machine identity, locator cache, EEGUnity scan, analysis.md merge.
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import platform
import re
import sys
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Machine identity
# ---------------------------------------------------------------------------

def get_machine_id() -> str:
    raw = f"{platform.node()}_{uuid.getnode()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Config (per-machine)
# ---------------------------------------------------------------------------

APP_KERNEL_DIR = Path(__file__).parent
BIDS_ROOT = APP_KERNEL_DIR.parent
MAIN_APP_CONFIG = BIDS_ROOT / "app" / "config.json"


def get_config_path() -> Path:
    return APP_KERNEL_DIR / "machine_config" / f"{get_machine_id()}.json"


def load_machine_config() -> Dict[str, str]:
    p = get_config_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "dataset_root": "",
        "eegunity_path": "",
        "machine_id": get_machine_id(),
        "hostname": platform.node(),
        "url": "",
        "key": "",
        "model": "",
        "proxy": "",
    }


def save_machine_config(cfg: Dict) -> None:
    p = get_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    cfg["machine_id"] = get_machine_id()
    cfg["hostname"] = platform.node()
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def load_llm_config() -> Dict[str, str]:
    """Load LLM config: merge machine config and main app config (machine config takes priority)."""
    cfg = {}
    # Fallback: main app config
    if MAIN_APP_CONFIG.exists():
        try:
            cfg.update(json.loads(MAIN_APP_CONFIG.read_text(encoding="utf-8")))
        except Exception:
            pass
    # Override: machine config (allows per-machine LLM settings)
    mc = load_machine_config()
    for key in ("url", "key", "model", "proxy"):
        if mc.get(key):
            cfg[key] = mc[key]
    return cfg


# ---------------------------------------------------------------------------
# EEGUnity path management
# ---------------------------------------------------------------------------

def _ensure_eegunity_in_path(eegunity_path: str) -> None:
    if eegunity_path and eegunity_path not in sys.path:
        sys.path.insert(0, eegunity_path)


def get_eegunity_version(eegunity_path: str) -> str:
    try:
        _ensure_eegunity_in_path(eegunity_path)
        from eegunity._version import __version__
        return __version__
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Kernel detection
# ---------------------------------------------------------------------------

KERNELS_DIR = APP_KERNEL_DIR / "kernels"


def detect_kernel_path(dataset_name: str) -> Optional[str]:
    """Return relative path (from repo root) of the best-matching kernel, or None."""
    candidates = [
        KERNELS_DIR / f"{dataset_name}.py",
        KERNELS_DIR / "openneuro_specific" / f"{dataset_name}.py",
        KERNELS_DIR / "openneuro.py" if dataset_name.startswith("openneuro") else None,
        KERNELS_DIR / "bids.py",
    ]
    for c in candidates:
        if c and c.exists():
            try:
                return str(c.relative_to(BIDS_ROOT)).replace("\\", "/")
            except ValueError:
                return str(c).replace("\\", "/")
    return None


def get_kernel_sha256(kernel_path: str) -> str:
    if not kernel_path:
        return "no_kernel"
    p = Path(kernel_path)
    if not p.is_absolute():
        p = BIDS_ROOT / kernel_path
    if not p.exists():
        return "file_not_found"
    data = p.read_bytes()
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Locator cache
# ---------------------------------------------------------------------------

LOCATOR_CACHE_DIR = APP_KERNEL_DIR / "locator_cache"

REQUIRED_CACHE_COLS = {"event_id", "event_id_num", "description_json"}


def get_locator_cache_path(dataset_name: str) -> Path:
    mid = get_machine_id()
    return LOCATOR_CACHE_DIR / mid / f"{dataset_name}.csv"


def locator_cache_exists(dataset_name: str) -> bool:
    p = get_locator_cache_path(dataset_name)
    if not p.exists():
        return False
    try:
        df = pd.read_csv(p, nrows=1)
        return REQUIRED_CACHE_COLS.issubset(set(df.columns))
    except Exception:
        return False


def load_locator_cache(dataset_name: str) -> pd.DataFrame:
    p = get_locator_cache_path(dataset_name)
    df = pd.read_csv(p)
    return df


def save_locator_cache(dataset_name: str, df: pd.DataFrame) -> None:
    p = get_locator_cache_path(dataset_name)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)


def check_locator_paths(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Check if File Path values in locator exist. Returns (all_ok, missing_list)."""
    missing = []
    for fp in df.get("File Path", []):
        if not os.path.exists(str(fp)):
            missing.append(str(fp))
    return len(missing) == 0, missing


# ---------------------------------------------------------------------------
# Stdout capture helper
# ---------------------------------------------------------------------------

class _TeeBuffer(io.StringIO):
    """Captures writes and appends them to a shared list (thread-safe)."""
    def __init__(self, lines_list: List[str], original):
        super().__init__()
        self._lines = lines_list
        self._original = original
        self._lock = threading.Lock()
        self._buf = ""

    def write(self, s: str) -> int:
        with self._lock:
            self._buf += s
            # Flush complete lines
            while "\n" in self._buf:
                line, self._buf = self._buf.split("\n", 1)
                stripped = line.strip()
                if stripped:
                    self._lines.append(stripped)
        # Also write to original
        try:
            self._original.write(s)
        except Exception:
            pass
        return len(s)

    def flush(self):
        try:
            self._original.flush()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# EEGUnity scan
# ---------------------------------------------------------------------------

def _extract_description_batch(udataset, stdout_lines: List[str]) -> None:
    """Add description_json column to locator from raw.info['description']."""
    locator = udataset.get_shared_attr()["locator"]
    total = len(locator)
    results = []
    for i, (_, row) in enumerate(locator.iterrows()):
        try:
            raw = udataset.eeg_parser.get_data_row(row, preload=False)
            desc = raw.info.get("description", "{}")
            results.append(str(desc))
        except Exception:
            results.append("{}")
        if (i + 1) % max(1, total // 10) == 0 or i == total - 1:
            stdout_lines.append(f"  Subject info: {i+1}/{total} files")
    locator["description_json"] = results
    udataset.get_shared_attr()["locator"] = locator


def run_full_scan(
    dataset_name: str,
    dataset_root: str,
    kernel_path: Optional[str],
    eegunity_path: str,
    progress_cb=None,
    stdout_lines: Optional[List[str]] = None,
    sampled_indices: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Run EEGUnity scan for a dataset, return enriched locator DataFrame.

    kernel_path: relative or absolute path to kernel .py file, or None for default parser.
    sampled_indices: if set, only process these row indices (quick-run).
    progress_cb: callable(step: str, pct: int)
    stdout_lines: shared list; EEGUnity stdout is appended here in real-time.
    """
    if stdout_lines is None:
        stdout_lines = []

    _ensure_eegunity_in_path(eegunity_path)
    from eegunity import UnifiedDataset

    dataset_path = str(Path(dataset_root) / dataset_name)

    # Resolve kernel path
    abs_kernel: Optional[str] = None
    if kernel_path:
        p = Path(kernel_path)
        abs_kernel = str(p) if p.is_absolute() else str(BIDS_ROOT / kernel_path)

    # --- Redirect stdout to capture EEGUnity output ---
    orig_stdout = sys.stdout
    tee = _TeeBuffer(stdout_lines, orig_stdout)
    sys.stdout = tee

    try:
        if progress_cb:
            progress_cb("Scanning dataset directory...", 5)
        stdout_lines.append(f"[Scan] Dataset: {dataset_name}, path: {dataset_path}")
        if abs_kernel:
            stdout_lines.append(f"[Scan] Kernel: {abs_kernel}")
        else:
            stdout_lines.append("[Scan] No kernel — using default EEGUnity parser")

        ud_kwargs = dict(
            dataset_path=dataset_path,
            domain_tag=dataset_name,
            verbose="WARNING",
        )
        if abs_kernel:
            ud_kwargs["kernel_spec"] = abs_kernel

        ud = UnifiedDataset(**ud_kwargs)
        n_files = len(ud.get_shared_attr()["locator"])
        stdout_lines.append(f"[Scan] Found {n_files} file(s) in locator")

        if progress_cb:
            progress_cb(f"Extracting events ({n_files} files)...", 20)

        if sampled_indices is not None:
            locator = ud.get_shared_attr()["locator"].copy()
            full_locator = locator.copy()
            sampled = locator.iloc[sampled_indices].copy()
            stdout_lines.append(f"[Scan] Quick-run: processing {len(sampled_indices)}/{n_files} files")
            ud.get_shared_attr()["locator"] = sampled
            ud.eeg_batch.get_events(miss_bad_data=True)
            sampled_result = ud.get_shared_attr()["locator"]
            full_locator.loc[sampled_indices, "event_id"] = sampled_result["event_id"].values
            full_locator.loc[sampled_indices, "event_id_num"] = sampled_result["event_id_num"].values
            ud.get_shared_attr()["locator"] = full_locator
        else:
            ud.eeg_batch.get_events(miss_bad_data=True)

        if progress_cb:
            progress_cb("Extracting subject metadata...", 75)

        _extract_description_batch(ud, stdout_lines)

        if progress_cb:
            progress_cb("Saving locator cache...", 92)

        result_df = ud.get_shared_attr()["locator"].copy()
        save_locator_cache(dataset_name, result_df)
        stdout_lines.append(f"[Scan] Cache saved: {get_locator_cache_path(dataset_name)}")

        if progress_cb:
            progress_cb("Done", 100)

    finally:
        sys.stdout = orig_stdout

    return result_df


# ---------------------------------------------------------------------------
# Structured result extraction from locator
# ---------------------------------------------------------------------------

def _parse_event_id_num(s: str) -> Dict[str, int]:
    try:
        return ast.literal_eval(str(s))
    except Exception:
        return {}


def _parse_description_json(s: str) -> Dict:
    try:
        return json.loads(str(s))
    except Exception:
        try:
            return ast.literal_eval(str(s))
        except Exception:
            return {}


def extract_event_stats(df: pd.DataFrame) -> Dict[str, int]:
    """Aggregate event_id_num across all rows → {event_id: total_count}."""
    totals: Dict[str, int] = {}
    for val in df.get("event_id_num", []):
        d = _parse_event_id_num(val)
        for k, v in d.items():
            totals[k] = totals.get(k, 0) + v
    return totals


def extract_subject_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract age/sex/device completeness from description_json column."""
    ages, sexes, devices = [], [], []
    for val in df.get("description_json", []):
        desc = _parse_description_json(val)
        eegu = desc.get("eegunity_description", {})
        if isinstance(eegu, str):
            try:
                eegu = json.loads(eegu)
            except Exception:
                eegu = {}
        ages.append(eegu.get("age", None))
        sexes.append(eegu.get("sex", None))
        devices.append(eegu.get("amplifier", None))

    def _is_valid(v):
        return v is not None and str(v).strip().lower() not in ("", "unknown", "nan", "none")

    n = len(df)
    age_ok = sum(1 for a in ages if _is_valid(a))
    sex_ok = sum(1 for s in sexes if _is_valid(s))
    dev_ok = sum(1 for d in devices if _is_valid(d))

    return {
        "record_count": n,
        "age_complete": age_ok,
        "sex_complete": sex_ok,
        "device_complete": dev_ok,
        "age_examples": list({str(a) for a in ages if _is_valid(a)})[:6],
        "sex_examples": list({str(s) for s in sexes if _is_valid(s)})[:4],
    }


def _completeness_label(ok: int, total: int) -> str:
    if total == 0:
        return "missing"
    pct = ok / total
    if pct >= 0.99:
        return "complete"
    if pct > 0:
        return f"partial ({ok}/{total})"
    return "missing"


# ---------------------------------------------------------------------------
# analysis.md — Status field helpers
# ---------------------------------------------------------------------------

_STATUS_RE = re.compile(r"^(> \*\*Status\*\*:\s*)(\S+)\s*$", re.MULTILINE)
_VALID_STATUSES = {"wait_kernel_update", "wait_manual_review", "completed", "hallucination"}


def read_analysis_status(content: str) -> str:
    """Read the Status field value from analysis.md content."""
    m = _STATUS_RE.search(content)
    return m.group(2) if m else ""


def update_analysis_status(content: str, new_status: str) -> str:
    """Replace Status field value. Only modifies the Status line, nothing else."""
    assert new_status in _VALID_STATUSES
    return _STATUS_RE.sub(lambda m: m.group(1) + new_status, content)


# ---------------------------------------------------------------------------
# analysis.md merge logic
# ---------------------------------------------------------------------------

_FILE_SCAN_RE = re.compile(
    r"(## File Scan Result\s*\n)(.*?)(?=\n## |\Z)",
    re.DOTALL,
)
_KERNEL_LINE_RE = re.compile(r"^> \*\*Kernel\*\*:.*$", re.MULTILINE)
_SHA256_LINE_RE = re.compile(r"^> \*\*SHA256\*\*:.*$", re.MULTILINE)
_EEGUNITY_VER_RE = re.compile(r"^> \*\*EEGUnity Version\*\*:.*$", re.MULTILINE)
_SCAN_TYPE_RE = re.compile(r"^> \*\*Scan Type\*\*:.*$", re.MULTILINE)

_AUTO_EVENT_START = "<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->"
_AUTO_EVENT_END = "<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->"
_AUTO_SUBJECT_START = "<!-- AUTO-KERNEL-SUBJECT-INFO:START -->"
_AUTO_SUBJECT_END = "<!-- AUTO-KERNEL-SUBJECT-INFO:END -->"

_TABLE_ROW_RE = re.compile(
    r"^\|\s*`?([^`|\n]+?)`?\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|",
    re.MULTILINE,
)


def _parse_event_table(md_block: str) -> Dict[str, Dict]:
    result = {}
    for m in _TABLE_ROW_RE.finditer(md_block):
        eid, count, typ, meta, meaning = [x.strip() for x in m.groups()]
        if eid.lower() in ("event id", "---", ""):
            continue
        result[eid] = {"count": count, "type": typ, "meta_level": meta, "meaning": meaning}
    return result


def _build_event_table(existing: Dict[str, Dict], new_counts: Dict[str, int], sampled: bool) -> str:
    header = (
        "| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
        "|----------|---------------|------|------------|---------|"
    )
    rows = []
    for eid, count in sorted(new_counts.items(), key=lambda x: -x[1]):
        existing_row = existing.get(eid, {})
        old_meaning = existing_row.get("meaning", "")
        meaning = old_meaning if (old_meaning and "unresolved" not in old_meaning.lower()) else "Unresolved from kernel scan"
        typ = existing_row.get("type", "event")
        meta = existing_row.get("meta_level", "raw")
        count_str = f"~{count}" if sampled else str(count)
        rows.append(f"| `{eid}` | {count_str} | {typ} | {meta} | {meaning} |")
    for eid, row in existing.items():
        if eid not in new_counts:
            rows.append(
                f"| `{eid}` | {row['count']} | {row['type']} | {row['meta_level']} "
                f"| {row['meaning']} *(not seen in scan)* |"
            )
    return header + "\n" + "\n".join(rows)


def _build_subject_info_block(info: Dict) -> str:
    n = info["record_count"]
    age_ex = ", ".join(f"`{x}`" for x in info["age_examples"]) or "N/A"
    sex_ex = ", ".join(f"`{x}`" for x in info["sex_examples"]) or "N/A"
    return (
        f"{_AUTO_SUBJECT_START}\n"
        f"- **Record Count**: {n}\n"
        f"- **Age Completeness**: {info['age_complete']}/{n} ({_completeness_label(info['age_complete'], n)})\n"
        f"- **Sex Completeness**: {info['sex_complete']}/{n} ({_completeness_label(info['sex_complete'], n)})\n"
        f"- **Observed Age Examples**: {age_ex}\n"
        f"- **Observed Sex Examples**: {sex_ex}\n"
        f"{_AUTO_SUBJECT_END}"
    )


def _build_info_table(info: Dict) -> str:
    n = info["record_count"]
    return (
        "| Field | Completeness | Notes |\n"
        "|---|---|---|\n"
        f"| `subject_age` | {_completeness_label(info['age_complete'], n)} | N/A |\n"
        f"| `subject_sex` | {_completeness_label(info['sex_complete'], n)} | N/A |\n"
        f"| `device` | {_completeness_label(info['device_complete'], n)} | N/A |"
    )


def merge_scan_results(
    analysis_content: str,
    scan_result: Dict,
) -> Tuple[str, List[Dict]]:
    """
    Merge scan results into analysis.md content.
    Returns (new_content, diff_list).
    """
    new_content = analysis_content
    diffs = []

    kernel_path = scan_result.get("kernel_path") or ""
    kernel_sha256 = scan_result["kernel_sha256"]
    eegunity_version = scan_result["eegunity_version"]
    event_counts = scan_result["event_counts"]
    subject_info = scan_result["subject_info"]
    sampled = scan_result.get("sampled", False)
    sampled_n = scan_result.get("sampled_n", 0)
    total_n = scan_result.get("total_n", 0)

    scan_type_str = f"Sampled ({sampled_n}/{total_n} files)" if sampled else "Full"
    kernel_label = f"`{kernel_path}`" if kernel_path else "*(no kernel — default parser)*"

    # --- File Scan Result header ---
    file_scan_m = _FILE_SCAN_RE.search(new_content)
    if file_scan_m:
        block = file_scan_m.group(2)
        old_block = block
        new_kernel_line = f"> **Kernel**: EEGUnity {eegunity_version} | {kernel_label}"
        new_sha_line = f"> **SHA256**: `{kernel_sha256}`"
        new_ver_line = f"> **EEGUnity Version**: `{eegunity_version}`"
        new_scan_line = f"> **Scan Type**: {scan_type_str}"

        block = _KERNEL_LINE_RE.sub(new_kernel_line, block) if _KERNEL_LINE_RE.search(block) else new_kernel_line + "\n" + block
        block = _SHA256_LINE_RE.sub(new_sha_line, block) if _SHA256_LINE_RE.search(block) else block + "\n" + new_sha_line
        block = _EEGUNITY_VER_RE.sub(new_ver_line, block) if _EEGUNITY_VER_RE.search(block) else block.rstrip() + "\n" + new_ver_line
        block = _SCAN_TYPE_RE.sub(new_scan_line, block) if _SCAN_TYPE_RE.search(block) else block.rstrip() + "\n" + new_scan_line

        if old_block != block:
            diffs.append({"section": "File Scan Header", "old": old_block.strip(), "new": block.strip()})
        new_content = new_content[:file_scan_m.start(2)] + block + new_content[file_scan_m.end(2):]

    # --- Event Structure ---
    auto_start = new_content.find(_AUTO_EVENT_START)
    auto_end = new_content.find(_AUTO_EVENT_END)

    if auto_start != -1 and auto_end != -1:
        existing = _parse_event_table(new_content[auto_start: auto_end + len(_AUTO_EVENT_END)])
    else:
        es_m = re.search(r"### Event Structure\s*\n(.*?)(?=\n###|\n## |\Z)", new_content, re.DOTALL)
        existing = _parse_event_table(es_m.group(1)) if es_m else {}

    new_table = _build_event_table(existing, event_counts, sampled)
    new_auto_block = (
        f"{_AUTO_EVENT_START}\n"
        f"> **Meaning Policy**: `Meaning` is interpretive; "
        f"`Event ID / Count / Type / Meta Level` are kernel-derived facts.\n\n"
        f"{new_table}\n"
        f"{_AUTO_EVENT_END}"
    )

    if auto_start != -1 and auto_end != -1:
        old_auto = new_content[auto_start: auto_end + len(_AUTO_EVENT_END)]
        if old_auto != new_auto_block:
            diffs.append({"section": "Event Structure", "old": old_auto, "new": new_auto_block})
        new_content = new_content[:auto_start] + new_auto_block + new_content[auto_end + len(_AUTO_EVENT_END):]
    else:
        es_m2 = re.search(r"(### Event Structure\s*\n)(.*?)(?=\n###|\n## |\Z)", new_content, re.DOTALL)
        if es_m2:
            old_inner = es_m2.group(2)
            # Preserve any Manual Review Notes outside the AUTO block
            manual_notes = re.findall(r"(> \*\*Manual Review Note\*\*:.*?)(?=\n>|\n\n|\Z)", old_inner, re.DOTALL)
            notes_str = "\n\n" + "\n\n".join(n.strip() for n in manual_notes) if manual_notes else ""
            new_inner = "\n" + new_auto_block + notes_str + "\n\n"
            diffs.append({"section": "Event Structure", "old": old_inner, "new": new_inner})
            new_content = new_content[:es_m2.start(2)] + new_inner + new_content[es_m2.end(2):]

    # --- Subject Info block (AUTO markers, optional) ---
    new_subj = _build_subject_info_block(subject_info)
    subj_start = new_content.find(_AUTO_SUBJECT_START)
    subj_end = new_content.find(_AUTO_SUBJECT_END)
    if subj_start != -1 and subj_end != -1:
        old_subj = new_content[subj_start: subj_end + len(_AUTO_SUBJECT_END)]
        if old_subj != new_subj:
            diffs.append({"section": "Subject Info", "old": old_subj, "new": new_subj})
        new_content = new_content[:subj_start] + new_subj + new_content[subj_end + len(_AUTO_SUBJECT_END):]

    # --- Info table ---
    info_tbl = _build_info_table(subject_info)
    info_m = re.search(
        r"(### Info\s*\n\| Field.*?\n\|[-| ]+\n)(.*?)(?=\n###|\n## |\Z)",
        new_content, re.DOTALL,
    )
    if info_m:
        old_info = info_m.group(2).strip()
        if old_info != info_tbl:
            diffs.append({"section": "Info Table", "old": old_info, "new": info_tbl})
        new_content = new_content[:info_m.start(2)] + info_tbl + "\n" + new_content[info_m.end(2):]

    return new_content, diffs


def apply_status_transition(content: str) -> Tuple[str, bool]:
    """
    If Status is wait_kernel_update, transition to wait_manual_review on commit.
    Returns (new_content, did_change).
    """
    current = read_analysis_status(content)
    if current == "wait_kernel_update":
        return update_analysis_status(content, "wait_manual_review"), True
    return content, False


# ---------------------------------------------------------------------------
# Dataset listing helpers
# ---------------------------------------------------------------------------

EXCLUDE_DIRS = {"Script", "app", "app_kernel", ".git", ".claude"}

_META_STATUS_RE = re.compile(r"\*\*Status\*\*:\s*(\S+)")
_META_CATEGORY_RE = re.compile(r"\*\*Category\*\*:\s*([^|*\n]+)")


def list_datasets() -> List[Dict]:
    result = []
    for entry in sorted(BIDS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        analysis = entry / "analysis.md"
        if not analysis.exists():
            continue
        try:
            content = analysis.read_text(encoding="utf-8", errors="replace")
        except Exception:
            content = ""

        sm = _META_STATUS_RE.search(content)
        status = sm.group(1).strip() if sm else "unknown"
        cm = _META_CATEGORY_RE.search(content)
        category = cm.group(1).strip() if cm else ""

        kernel = detect_kernel_path(entry.name)
        cache_ok = locator_cache_exists(entry.name)
        result.append({
            "name": entry.name,
            "status": status,
            "category": category,
            "has_kernel": kernel is not None,
            "kernel_path": kernel or "",
            "has_cache": cache_ok,
        })
    return result


# ---------------------------------------------------------------------------
# LLM sampling prompt builder
# ---------------------------------------------------------------------------

def build_sampling_prompt(dataset_name: str, df: pd.DataFrame) -> str:
    """Build prompt for LLM to recommend which files to sample for quick-run."""
    n = len(df)
    paths = df.get("File Path", pd.Series([], dtype=str)).tolist()
    common = os.path.commonprefix([str(p) for p in paths]) if paths else ""
    short_paths = [str(p)[len(common):] for p in paths]

    rows_info = []
    for i, (_, row) in enumerate(df.iterrows()):
        rows_info.append({
            "idx": i,
            "path_suffix": short_paths[i] if i < len(short_paths) else "",
            "size_shape": str(row.get("Data Shape", "?")),
            "duration_s": str(row.get("Duration", "?")),
            "completeness": str(row.get("Completeness Check", "?")),
            "has_events": bool(str(row.get("event_id", "")).strip() not in ("", "nan")),
        })

    return (
        f"You are helping select a minimal but representative sample of EEG files "
        f"to quickly scan event statistics for dataset '{dataset_name}' ({n} total files).\n\n"
        f"File list (path suffixes only, common prefix removed):\n"
        + json.dumps(rows_info, indent=2)
        + "\n\nSelect the minimal set of file indices that:\n"
        "1. Covers all distinct event types likely present\n"
        "2. Represents variation in file structure (different shapes/durations)\n"
        "3. Prefers files with 'Completed' completeness check\n"
        "4. Skips files that already have events cached (has_events=true) unless necessary\n\n"
        "Return a JSON object ONLY with key 'sampled_indices' (list of integers) "
        "and 'reason' (one sentence explanation).\n"
        "Example: {\"sampled_indices\": [0, 5, 12], \"reason\": \"...\"}"
    )
