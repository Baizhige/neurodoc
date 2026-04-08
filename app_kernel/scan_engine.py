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


def load_machine_config() -> Dict:
    import os as _os
    _default_workers = min(32, _os.cpu_count() or 4)
    p = get_config_path()
    if p.exists():
        cfg = json.loads(p.read_text(encoding="utf-8"))
        # Migrate legacy single dataset_root → dataset_roots list
        if "dataset_root" in cfg and "dataset_roots" not in cfg:
            old = cfg.pop("dataset_root")
            cfg["dataset_roots"] = [old] if old else []
        cfg.setdefault("dataset_roots", [])
        cfg.setdefault("num_workers", _default_workers)
        return cfg
    return {
        "dataset_roots": [],
        "eegunity_path": "",
        "num_workers": _default_workers,
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
# Dataset root search
# ---------------------------------------------------------------------------

def find_dataset_path(dataset_name: str, dataset_roots: List[str]) -> Optional[str]:
    """Search dataset_roots in order; return first directory that contains dataset_name."""
    for root in dataset_roots:
        if not root:
            continue
        candidate = Path(root) / dataset_name
        if candidate.is_dir():
            return str(candidate)
    return None


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
    # Back-fill subject columns for stage1 caches that predate this field
    if "description_json" in df.columns:
        if "subject_age" not in df.columns or "subject_sex" not in df.columns:
            _add_subject_columns(df)
    else:
        if "subject_age" not in df.columns:
            df["subject_age"] = None
        if "subject_sex" not in df.columns:
            df["subject_sex"] = None
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

def _add_subject_columns(locator: pd.DataFrame) -> None:
    """Extract subject_age and subject_sex as flat columns from description_json (in-place)."""
    ages, sexes = [], []
    for val in locator.get("description_json", []):
        try:
            desc = json.loads(str(val))
        except Exception:
            try:
                desc = ast.literal_eval(str(val))
            except Exception:
                desc = {}
        eegu = desc.get("eegunity_description", {})
        if isinstance(eegu, str):
            try:
                eegu = json.loads(eegu)
            except Exception:
                eegu = {}
        ages.append(eegu.get("age", None))
        sexes.append(eegu.get("sex", None))
    locator["subject_age"] = ages
    locator["subject_sex"] = sexes


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
    dataset_roots: List[str],
    kernel_path: Optional[str],
    eegunity_path: str,
    progress_cb=None,
    stdout_lines: Optional[List[str]] = None,
    sampled_indices: Optional[List[int]] = None,
    num_workers: int = 1,
) -> pd.DataFrame:
    """
    Run EEGUnity scan for a dataset, return enriched locator DataFrame.

    dataset_roots: list of directories to search for dataset_name (first match used).
    kernel_path: relative or absolute path to kernel .py file, or None for default parser.
    sampled_indices: if set, only process these row indices (quick-run).
    progress_cb: callable(step: str, pct: int)
    stdout_lines: shared list; EEGUnity stdout is appended here in real-time.
    num_workers: parallel workers for UnifiedDataset instantiation.
    """
    if stdout_lines is None:
        stdout_lines = []

    _ensure_eegunity_in_path(eegunity_path)
    from eegunity import UnifiedDataset

    dataset_path = find_dataset_path(dataset_name, dataset_roots)
    if not dataset_path:
        searched = ", ".join(dataset_roots) or "(none configured)"
        raise FileNotFoundError(
            f"Dataset '{dataset_name}' not found in any configured directory: {searched}"
        )

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
            num_workers=num_workers,
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
        _add_subject_columns(ud.get_shared_attr()["locator"])

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

# Legacy AUTO marker constants — kept only for stripping old-format documents
_AUTO_EVENT_START = "<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->"
_AUTO_EVENT_END = "<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->"
_AUTO_SUBJECT_START = "<!-- AUTO-KERNEL-SUBJECT-INFO:START -->"
_AUTO_SUBJECT_END = "<!-- AUTO-KERNEL-SUBJECT-INFO:END -->"

_TABLE_ROW_RE = re.compile(
    r"^\|\s*`?([^`|\n]+?)`?\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|",
    re.MULTILINE,
)


def _strip_auto_markers(content: str) -> str:
    """Remove legacy AUTO HTML comment markers and associated generated lines."""
    content = content.replace(_AUTO_EVENT_START + "\n", "").replace(_AUTO_EVENT_START, "")
    content = content.replace("\n" + _AUTO_EVENT_END, "").replace(_AUTO_EVENT_END, "")
    content = re.sub(r"^> \*\*Meaning Policy\*\*:.*\n?", "", content, flags=re.MULTILINE)
    content = re.sub(
        r"<!-- AUTO-KERNEL-SUBJECT-INFO:START -->.*?<!-- AUTO-KERNEL-SUBJECT-INFO:END -->\n?",
        "", content, flags=re.DOTALL,
    )
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content


def _parse_event_table(md_block: str) -> Dict[str, Dict]:
    result = {}
    for m in _TABLE_ROW_RE.finditer(md_block):
        eid, count, typ, meta, meaning = [x.strip() for x in m.groups()]
        if eid.lower() in ("event id", "---", ""):
            continue
        result[eid] = {"count": count, "type": typ, "meta_level": meta, "meaning": meaning}
    return result


def _event_table_changed(existing: Dict[str, Dict], new_counts: Dict[str, int]) -> bool:
    """Return True if event set or any count differs between existing table and new scan."""
    if set(existing.keys()) != set(new_counts.keys()):
        return True
    for eid, count in new_counts.items():
        try:
            old_str = existing[eid].get("count", "").lstrip("~").strip()
            if int(old_str) != count:
                return True
        except (ValueError, KeyError):
            return True
    return False


def _build_event_table(existing: Dict[str, Dict], new_counts: Dict[str, int], sampled: bool) -> str:
    header = (
        "| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
        "|----------|---------------|------|------------|---------|"
    )
    rows = []
    for eid, count in sorted(new_counts.items(), key=lambda x: -x[1]):
        existing_row = existing.get(eid, {})
        if existing_row:
            # Existing event: preserve Type, Meta Level, Meaning exactly
            typ = existing_row.get("type", "event")
            meta = existing_row.get("meta_level", "raw")
            meaning = existing_row.get("meaning", "")
        else:
            # New event: empty Meaning placeholder
            typ = "event"
            meta = "raw"
            meaning = ""
        count_str = f"~{count}" if sampled else str(count)
        rows.append(f"| `{eid}` | {count_str} | {typ} | {meta} | {meaning} |")
    # Events absent from new scan are simply omitted (deleted)
    return header + "\n" + "\n".join(rows)


def _parse_info_table(md_block: str) -> Dict[str, Dict]:
    """Parse ### Info table rows → {field: {completeness, notes}}."""
    result = {}
    for m in re.finditer(
        r"^\|\s*`?([^`|\n]+?)`?\s*\|\s*([^|\n]*?)\s*\|\s*([^|\n]*?)\s*\|",
        md_block, re.MULTILINE,
    ):
        field, completeness, notes = [x.strip() for x in m.groups()]
        if field.lower() in ("field", "---", ""):
            continue
        result[field] = {"completeness": completeness, "notes": notes}
    return result


def _build_info_table_smart(info: Dict, existing_rows: Dict[str, Dict]) -> str:
    """Build ### Info data rows only (no header), preserving Notes where Completeness is unchanged."""
    n = info["record_count"]
    rows_data = [
        ("subject_age", _completeness_label(info["age_complete"], n)),
        ("subject_sex", _completeness_label(info["sex_complete"], n)),
        ("device", _completeness_label(info["device_complete"], n)),
    ]
    lines = []
    for field, new_comp in rows_data:
        old = existing_rows.get(field, {})
        old_comp = old.get("completeness", "")
        old_notes = old.get("notes", "N/A")
        notes = "N/A" if (old_comp and old_comp != new_comp) else (old_notes or "N/A")
        lines.append(f"| `{field}` | {new_comp} | {notes} |")
    return "\n".join(lines)


def merge_scan_results(
    analysis_content: str,
    scan_result: Dict,
) -> Tuple[str, List[Dict]]:
    """
    Merge scan results into analysis.md content.
    Returns (new_content, diff_list).

    Diff contains at most one entry covering the entire ## File Scan Result block.
    No HTML comment markers are added; legacy markers are stripped on first pass.
    """
    # Strip legacy AUTO markers from old-format documents first
    new_content = _strip_auto_markers(analysis_content)

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

    # Capture old ## File Scan Result block for diff (after marker stripping)
    fsr_m0 = _FILE_SCAN_RE.search(new_content)
    old_fsr_text = fsr_m0.group(0).rstrip() if fsr_m0 else ""

    # ── 1. Update kernel fingerprint header ──────────────────────────────────
    fsr_m = _FILE_SCAN_RE.search(new_content)
    if fsr_m:
        block = fsr_m.group(2)
        new_kernel_line = f"> **Kernel**: EEGUnity {eegunity_version} | {kernel_label}"
        new_sha_line    = f"> **SHA256**: `{kernel_sha256}`"
        new_ver_line    = f"> **EEGUnity Version**: `{eegunity_version}`"
        new_scan_line   = f"> **Scan Type**: {scan_type_str}"

        block = _KERNEL_LINE_RE.sub(new_kernel_line, block) \
            if _KERNEL_LINE_RE.search(block) else new_kernel_line + "\n" + block
        block = _SHA256_LINE_RE.sub(new_sha_line, block) \
            if _SHA256_LINE_RE.search(block) else block + "\n" + new_sha_line

        # EEGUnity Version: update or insert after SHA256
        if _EEGUNITY_VER_RE.search(block):
            block = _EEGUNITY_VER_RE.sub(new_ver_line, block)
        else:
            block = _SHA256_LINE_RE.sub(lambda m: m.group(0) + "\n" + new_ver_line, block)

        # Scan Type: update or insert after EEGUnity Version
        if _SCAN_TYPE_RE.search(block):
            block = _SCAN_TYPE_RE.sub(new_scan_line, block)
        else:
            block = _EEGUNITY_VER_RE.sub(lambda m: m.group(0) + "\n" + new_scan_line, block)

        new_content = new_content[:fsr_m.start(2)] + block + new_content[fsr_m.end(2):]

    # ── 2. Update Event Structure table ─────────────────────────────────────
    es_m = re.search(r"(### Event Structure\s*\n)(.*?)(?=\n###|\n## |\Z)", new_content, re.DOTALL)
    if es_m:
        es_inner = es_m.group(2)
        existing = _parse_event_table(es_inner)
        changed = _event_table_changed(existing, event_counts)
        new_table = _build_event_table(existing, event_counts, sampled)

        if changed:
            # Clear the blockquote Note after the table
            new_es_inner = "\n" + new_table + "\n\n"
        else:
            # Preserve existing blockquote Note (lines starting with "> " after the table)
            note_m = re.search(r"\n((?:> [^\n]*\n?)+)\s*$", es_inner)
            note_str = "\n" + note_m.group(1).rstrip() if note_m else ""
            new_es_inner = "\n" + new_table + note_str + "\n\n"

        new_content = new_content[:es_m.start(2)] + new_es_inner + new_content[es_m.end(2):]

    # ── 3. Update Info table (preserve Notes where Completeness unchanged) ───
    info_m = re.search(
        r"(### Info\s*\n\| Field.*?\n\|[-| ]+\n)(.*?)(?=\n###|\n## |\Z)",
        new_content, re.DOTALL,
    )
    if info_m:
        existing_info = _parse_info_table(info_m.group(2))
        new_info_tbl = _build_info_table_smart(subject_info, existing_info)
        new_content = new_content[:info_m.start(2)] + new_info_tbl + "\n" + new_content[info_m.end(2):]

    # ── Produce single diff for entire File Scan Result block ───────────────
    fsr_m_new = _FILE_SCAN_RE.search(new_content)
    new_fsr_text = fsr_m_new.group(0).rstrip() if fsr_m_new else ""

    diffs = []
    if old_fsr_text != new_fsr_text:
        diffs.append({"section": "File Scan Result", "old": old_fsr_text, "new": new_fsr_text})

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
