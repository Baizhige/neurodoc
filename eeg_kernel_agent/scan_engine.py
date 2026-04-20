"""
scan_engine.py 鈥?Core logic for app_scan.
Handles: machine identity, locator cache, EEGUnity scan, analysis.md merge.
"""

from __future__ import annotations

import ast
import datetime as dt
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

try:
    from .llm_adapter import resolve_llm_config
except ImportError:
    from llm_adapter import resolve_llm_config

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
        # Migrate legacy single dataset_root 鈫?dataset_roots list
        if "dataset_root" in cfg and "dataset_roots" not in cfg:
            old = cfg.pop("dataset_root")
            cfg["dataset_roots"] = [old] if old else []
        cfg.setdefault("dataset_roots", [])
        cfg.setdefault("num_workers", _default_workers)
        cfg.setdefault("BASE_URL", "")
        cfg.setdefault("ANTHROPIC_BASE_URL", "")
        cfg.setdefault("key", "")
        cfg.setdefault("model", "")
        cfg.setdefault("proxy", "")
        return cfg
    return {
        "dataset_roots": [],
        "eegunity_path": "",
        "num_workers": _default_workers,
        "machine_id": get_machine_id(),
        "hostname": platform.node(),
        "BASE_URL": "",
        "ANTHROPIC_BASE_URL": "",
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
    for key in ("BASE_URL", "ANTHROPIC_BASE_URL", "url", "key", "model", "proxy"):
        if mc.get(key):
            cfg[key] = mc[key]
    resolved = resolve_llm_config(cfg)
    # Keep the original shape mostly intact while exposing normalized fields.
    result = dict(cfg)
    result["BASE_URL"] = resolved["BASE_URL"]
    result["ANTHROPIC_BASE_URL"] = resolved["ANTHROPIC_BASE_URL"]
    result["url"] = resolved["active_url"] if resolved["provider"] == "openai" else ""
    return result


# ---------------------------------------------------------------------------
# Dataset root search
# ---------------------------------------------------------------------------

def find_dataset_path(dataset_name: str, dataset_roots: List[str]) -> Optional[str]:
    """Search dataset_roots in order; return first directory that contains dataset_name.

    For openneuro datasets the on-disk directory may omit the 'openneuro_' prefix
    (e.g. analysis folder 'openneuro_ds001785' → disk dir 'ds001785'), so both
    variants are tried.
    """
    _OPENNEURO_PREFIX = "openneuro_"
    names_to_try = [dataset_name]
    if dataset_name.startswith(_OPENNEURO_PREFIX):
        names_to_try.append(dataset_name[len(_OPENNEURO_PREFIX):])

    for root in dataset_roots:
        if not root:
            continue
        for name in names_to_try:
            candidate = Path(root) / name
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
    # Normalize to CRLF before hashing so the result is identical across
    # Linux (LF) and Windows (CRLF) checkouts of the same git file.
    data = p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Locator cache
# ---------------------------------------------------------------------------

LOCATOR_CACHE_DIR = APP_KERNEL_DIR / "locator_cache"
CACHE_SCHEMA_VERSION = 2

# Accept any cache that still has the default EEGUnity locator columns.
# Event/subject columns are treated as derived metadata and may be refreshed later.
REQUIRED_CACHE_COLS = [
    "File Path",
    "Domain Tag",
    "File Type",
    "Data Shape",
    "Channel Names",
    "Number of Channels",
    "Sampling Rate",
    "Duration",
    "Completeness Check",
]
REQUIRED_CACHE_COLS_SET = set(REQUIRED_CACHE_COLS)

def _get_cache_dir() -> Path:
    return LOCATOR_CACHE_DIR / get_machine_id()


def _metadata_cache_stem(dataset_name: str, kernel_sha256: str) -> str:
    return f"{dataset_name}__meta__{kernel_sha256}"


def get_locator_cache_path(dataset_name: str) -> Path:
    return _get_cache_dir() / f"{dataset_name}.csv"


def get_tmp_locator_path(dataset_name: str) -> Path:
    return _get_cache_dir() / f"{dataset_name}_sampled_tmp.csv"


def get_metadata_cache_csv_path(dataset_name: str, kernel_sha256: str) -> Path:
    return _get_cache_dir() / f"{_metadata_cache_stem(dataset_name, kernel_sha256)}.csv"


def get_metadata_cache_meta_path(dataset_name: str, kernel_sha256: str) -> Path:
    return _get_cache_dir() / f"{_metadata_cache_stem(dataset_name, kernel_sha256)}.json"


def locator_cache_exists(dataset_name: str) -> bool:
    p = get_locator_cache_path(dataset_name)
    if not p.exists():
        return False
    try:
        df = pd.read_csv(p, nrows=0)
        return REQUIRED_CACHE_COLS_SET.issubset(set(df.columns))
    except Exception:
        return False

def check_locator_paths(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Check if File Path values in locator exist. Returns (all_ok, missing_list)."""
    missing = []
    for fp in df.get("File Path", []):
        if not os.path.exists(str(fp)):
            missing.append(str(fp))
    return len(missing) == 0, missing


def _ensure_base_locator_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in REQUIRED_CACHE_COLS:
        if col not in result.columns:
            result[col] = None
    return result[[col for col in REQUIRED_CACHE_COLS if col in result.columns]]


def _load_legacy_subject_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "subject_age" not in result.columns or "subject_sex" not in result.columns:
        if "description_json" in result.columns:
            _add_subject_columns(result)
        else:
            result["subject_age"] = None
            result["subject_sex"] = None
    if "description_json" in result.columns:
        result = result.drop(columns=["description_json"])
    return result


def load_locator_cache(dataset_name: str) -> pd.DataFrame:
    """Load the machine-local base locator cache."""
    p = get_locator_cache_path(dataset_name)
    df = pd.read_csv(p)
    return _ensure_base_locator_columns(df)


def save_locator_cache(dataset_name: str, df: pd.DataFrame) -> None:
    """Persist the machine-local base locator cache."""
    p = get_locator_cache_path(dataset_name)
    p.parent.mkdir(parents=True, exist_ok=True)
    _ensure_base_locator_columns(df).to_csv(p, index=False)


def load_metadata_cache(dataset_name: str, kernel_sha256: str) -> pd.DataFrame:
    """Load the full metadata cache for a specific kernel fingerprint."""
    p = get_metadata_cache_csv_path(dataset_name, kernel_sha256)
    df = pd.read_csv(p)
    return _normalize_scan_result_frame(_load_legacy_subject_columns(df))


def save_metadata_cache(
    dataset_name: str,
    kernel_sha256: str,
    eegunity_version: str,
    kernel_path: str,
    dataset_path: str,
    df: pd.DataFrame,
) -> None:
    csv_path = get_metadata_cache_csv_path(dataset_name, kernel_sha256)
    meta_path = get_metadata_cache_meta_path(dataset_name, kernel_sha256)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df = _normalize_scan_result_frame(df)
    clean_df.to_csv(csv_path, index=False)
    meta = {
        "dataset": dataset_name,
        "kernel_sha256": kernel_sha256,
        "kernel_path": kernel_path or "",
        "eegunity_version": eegunity_version,
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "dataset_path": dataset_path,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "row_count": int(len(clean_df)),
        "csv_path": str(csv_path),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def load_metadata_cache_info(dataset_name: str, kernel_sha256: str) -> Optional[Dict[str, Any]]:
    p = get_metadata_cache_meta_path(dataset_name, kernel_sha256)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def metadata_cache_exists(dataset_name: str, kernel_sha256: str, eegunity_version: str) -> bool:
    csv_path = get_metadata_cache_csv_path(dataset_name, kernel_sha256)
    if not csv_path.exists():
        return False
    info = load_metadata_cache_info(dataset_name, kernel_sha256)
    if not info:
        return False
    return (
        info.get("kernel_sha256") == kernel_sha256
        and info.get("eegunity_version") == eegunity_version
        and int(info.get("cache_schema_version", -1)) == CACHE_SCHEMA_VERSION
    )


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

    _MAX_LINES = 20  # rolling cap — keeps memory bounded during long scans

    def write(self, s: str) -> int:
        with self._lock:
            self._buf += s
            # Flush complete lines
            while "\n" in self._buf:
                line, self._buf = self._buf.split("\n", 1)
                stripped = line.strip()
                if stripped:
                    self._lines.append(stripped)
                    if len(self._lines) > self._MAX_LINES:
                        del self._lines[:-self._MAX_LINES]
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
    """Parse subject_age / subject_sex from the 'description' column already in the locator.

    Fast path: when get_meta() has already populated the 'description' column,
    this function is pure-pandas with zero file IO.
    Legacy path: falls back to per-file reload when 'description' column is absent
    (EEGUnity version without get_meta).
    """
    locator = udataset.get_shared_attr()["locator"]

    if "description" in locator.columns:
        # Fast path: pure-pandas, zero file IO
        ages, sexes = [], []
        for _, row in locator.iterrows():
            desc_str = row.get("description", "")
            try:
                desc = json.loads(str(desc_str)) if desc_str else {}
            except Exception:
                try:
                    desc = ast.literal_eval(str(desc_str))
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
        udataset.get_shared_attr()["locator"] = locator
        stdout_lines.append(f"  Subject info parsed from locator ({len(locator)} rows, no reload)")
        return

    # Legacy path: per-file reload (EEGUnity without get_meta)
    total = len(locator)
    ages, sexes, ch_names_list = [], [], []
    for i in range(total):
        try:
            raw = udataset.eeg_parser.get_data(i, preload=False)
            ch_names_list.append(", ".join(raw.ch_names))
            desc_str = raw.info.get("description", "{}")
            try:
                desc = json.loads(str(desc_str))
            except Exception:
                try:
                    desc = ast.literal_eval(str(desc_str))
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
        except Exception:
            ch_names_list.append(locator.iloc[i].get("Channel Names", ""))
            ages.append(None)
            sexes.append(None)
        if (i + 1) % max(1, total // 10) == 0 or i == total - 1:
            stdout_lines.append(f"  Subject info (legacy reload): {i+1}/{total}")
    locator["Channel Names"] = ch_names_list
    locator["subject_age"] = ages
    locator["subject_sex"] = sexes
    udataset.get_shared_attr()["locator"] = locator

def extract_subject_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract age/sex/device completeness from subject_age/subject_sex columns."""
    def _is_valid(v):
        return v is not None and str(v).strip().lower() not in ("", "unknown", "nan", "none")

    ages = list(df.get("subject_age", [None] * len(df)))
    sexes = list(df.get("subject_sex", [None] * len(df)))
    # device is not yet a flat column; default to 0
    n = len(df)
    age_ok = sum(1 for a in ages if _is_valid(a))
    sex_ok = sum(1 for s in sexes if _is_valid(s))

    return {
        "record_count": n,
        "age_complete": age_ok,
        "sex_complete": sex_ok,
        "device_complete": 0,
        "age_examples": list({str(a) for a in ages if _is_valid(a)})[:6],
        "sex_examples": list({str(s) for s in sexes if _is_valid(s)})[:4],
    }


def _coerce_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value


def _coerce_int(value: Any) -> Optional[int]:
    value = _coerce_scalar(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else int(round(value))
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(s)
    except Exception:
        try:
            f = float(s)
            return int(f) if f.is_integer() else int(round(f))
        except Exception:
            return None


def _normalize_mapping_text(text: str) -> str:
    patterns = [
        (r"np\.str_\((\".*?\"|'.*?')\)", r"\1"),
        (r"np\.bytes_\((\".*?\"|'.*?')\)", r"\1"),
        (r"np\.(?:int|uint)\d+\((-?\d+)\)", r"\1"),
        (r"np\.float\d+\((-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\)", r"\1"),
        (r"np\.bool_\((True|False)\)", r"\1"),
    ]
    norm = str(text)
    for pattern, repl in patterns:
        norm = re.sub(pattern, repl, norm)
    return norm


def _parse_mapping_cell(value: Any) -> Dict[str, int]:
    if value is None:
        return {}
    value = _coerce_scalar(value)
    if isinstance(value, dict):
        result: Dict[str, int] = {}
        for k, v in value.items():
            iv = _coerce_int(v)
            if iv is None:
                continue
            result[str(_coerce_scalar(k))] = iv
        return result

    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "{}"):
        return {}

    candidates = [text]
    normalized = _normalize_mapping_text(text)
    if normalized != text:
        candidates.append(normalized)

    for candidate in candidates:
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(candidate)
            except Exception:
                continue
            if isinstance(parsed, dict):
                result = {}
                for k, v in parsed.items():
                    iv = _coerce_int(v)
                    if iv is None:
                        continue
                    result[str(_coerce_scalar(k))] = iv
                return result
    return {}


def _serialize_mapping_cell(value: Any) -> str:
    parsed = _parse_mapping_cell(value)
    if not parsed:
        return "{}"
    return json.dumps(parsed, ensure_ascii=False, sort_keys=True)


def _normalize_scan_result_frame(df: pd.DataFrame) -> pd.DataFrame:
    result = _load_legacy_subject_columns(df)
    for col in ("event_id", "event_id_num"):
        if col in result.columns:
            result[col] = result[col].apply(_serialize_mapping_cell)
    return result


def _normalize_sampled_indices(sampled_indices: Optional[List[int]], n_files: int) -> Optional[List[int]]:
    if sampled_indices is None:
        return None
    cleaned = sorted({int(i) for i in sampled_indices if 0 <= int(i) < n_files})
    return cleaned or None


def _extract_misc_channels(udataset, stdout_lines: List[str]) -> List[str]:
    """Return sorted unique misc channel names by reading the first locator entry.

    Misc channel names are typically uniform across a dataset (all files share the
    same channel layout after the kernel runs), so sampling the first file is enough.
    """
    locator = udataset.get_shared_attr()["locator"]
    if locator.empty:
        return []
    try:
        raw = udataset.eeg_parser.get_data(0, preload=False)
        misc_names = sorted(
            n for n, t in zip(raw.ch_names, raw.get_channel_types()) if t == "misc"
        )
        if misc_names:
            stdout_lines.append(f"  Misc channels detected: {misc_names}")
        return misc_names
    except Exception as exc:
        stdout_lines.append(f"  [WARN] Could not extract misc channels: {exc}")
        return []


def run_full_scan(
    dataset_name: str,
    dataset_roots: List[str],
    kernel_path: Optional[str],
    eegunity_path: str,
    progress_cb=None,
    stdout_lines: Optional[List[str]] = None,
    sampled_indices: Optional[List[int]] = None,
    num_workers: int = 1,
    persist_base_cache: bool = True,
    persist_metadata_cache: bool = False,
    kernel_sha256: str = "",
    eegunity_version: str = "",
) -> pd.DataFrame:
    """
    Run EEGUnity scan and return the locator rows that belong to this scan.

    Full scans can optionally persist:
    - a machine-local base locator cache (no kernel metadata)
    - a kernel-versioned metadata cache

    Sampled scans never persist metadata caches and only return sampled rows.
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

    abs_kernel: Optional[str] = None
    if kernel_path:
        p = Path(kernel_path)
        abs_kernel = str(p) if p.is_absolute() else str(BIDS_ROOT / kernel_path)

    orig_stdout = sys.stdout
    tee = _TeeBuffer(stdout_lines, orig_stdout)
    sys.stdout = tee

    try:
        sampled_requested = sampled_indices is not None
        stdout_lines.append(f"[Scan] Dataset: {dataset_name}, path: {dataset_path}")
        if abs_kernel:
            stdout_lines.append(f"[Scan] Kernel: {abs_kernel}")
        else:
            stdout_lines.append("[Scan] No kernel - using default EEGUnity parser")

        if sampled_requested and locator_cache_exists(dataset_name):
            # Fast path: load pre-built base locator, skip full directory scan.
            if progress_cb:
                progress_cb("Loading base locator cache...", 5)
            base_df = load_locator_cache(dataset_name)
            n_files = len(base_df)
            sampled_indices = _normalize_sampled_indices(sampled_indices, n_files)
            if sampled_indices is None:
                raise ValueError("Sampled scan received no valid locator indices.")

            working_locator = base_df.iloc[sampled_indices].reset_index(drop=True)
            tmp_path = get_tmp_locator_path(dataset_name)
            tmp_path.parent.mkdir(parents=True, exist_ok=True)
            working_locator.to_csv(str(tmp_path), index=False)

            stdout_lines.append(
                f"[Scan] Quick-run (tmp locator): {len(sampled_indices)}/{n_files} files"
            )
            ud_kwargs: dict = dict(
                locator_path=str(tmp_path),
                verbose="WARNING",
                num_workers=num_workers,
            )
            if abs_kernel:
                ud_kwargs["kernel_spec"] = abs_kernel
            ud = UnifiedDataset(**ud_kwargs)
        else:
            # Standard path: full directory scan.
            if progress_cb:
                progress_cb("Scanning dataset directory...", 5)
            ud_kwargs = dict(
                dataset_path=dataset_path,
                domain_tag=dataset_name,
                verbose="WARNING",
                num_workers=num_workers,
            )
            if abs_kernel:
                ud_kwargs["kernel_spec"] = abs_kernel
            ud = UnifiedDataset(**ud_kwargs)

            base_locator = _ensure_base_locator_columns(ud.get_shared_attr()["locator"].copy())
            n_files = len(base_locator)
            stdout_lines.append(f"[Scan] Found {n_files} file(s) in locator")

            if persist_base_cache:
                save_locator_cache(dataset_name, base_locator)
                stdout_lines.append(
                    f"[Scan] Base locator cache saved: {get_locator_cache_path(dataset_name)}"
                )

            sampled_indices = _normalize_sampled_indices(sampled_indices, n_files)
            if sampled_requested and sampled_indices is None:
                raise ValueError("Sampled scan received no valid locator indices.")
            if sampled_indices is not None:
                working_locator = ud.get_shared_attr()["locator"].iloc[sampled_indices].copy()
                stdout_lines.append(
                    f"[Scan] Quick-run (full init): {len(sampled_indices)}/{n_files} files"
                )
                ud.get_shared_attr()["locator"] = working_locator

        if progress_cb:
            progress_cb(f"Extracting events ({len(ud.get_shared_attr()['locator'])} files)...", 20)
        if hasattr(ud.eeg_batch, "get_meta"):
            ud.eeg_batch.get_meta(miss_bad_data=True)
        else:
            ud.eeg_batch.get_events(miss_bad_data=True)

        if progress_cb:
            progress_cb("Extracting subject metadata...", 75)
        _extract_description_batch(ud, stdout_lines)

        misc_channel_names = _extract_misc_channels(ud, stdout_lines)

        result_df = _normalize_scan_result_frame(ud.get_shared_attr()["locator"].copy())

        if persist_metadata_cache and sampled_indices is None:
            if progress_cb:
                progress_cb("Saving metadata cache...", 92)
            save_metadata_cache(
                dataset_name=dataset_name,
                kernel_sha256=kernel_sha256 or get_kernel_sha256(kernel_path or ""),
                eegunity_version=eegunity_version or get_eegunity_version(eegunity_path),
                kernel_path=kernel_path or "",
                dataset_path=dataset_path,
                df=result_df,
            )
            stdout_lines.append(
                f"[Scan] Metadata cache saved: {get_metadata_cache_csv_path(dataset_name, kernel_sha256 or get_kernel_sha256(kernel_path or ''))}"
            )
        elif progress_cb:
            progress_cb("Finalizing scan...", 92)

        if progress_cb:
            progress_cb("Done", 100)

    finally:
        sys.stdout = orig_stdout

    return result_df, misc_channel_names


def _parse_event_id_num(s: Any) -> Dict[str, int]:
    return _parse_mapping_cell(s)


def extract_event_stats(df: pd.DataFrame) -> Dict[str, int]:
    """Aggregate event_id_num across all rows -> {event_id: total_count}."""
    totals: Dict[str, int] = {}
    for val in df.get("event_id_num", []):
        d = _parse_event_id_num(val)
        for k, v in d.items():
            totals[k] = totals.get(k, 0) + int(v)
    return totals


def locator_to_table_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Convert a locator DataFrame into the JSON table payload used by the UI."""
    clean_df = df.fillna("").astype(str)
    return {
        "columns": list(clean_df.columns),
        "rows": clean_df.values.tolist(),
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
# analysis.md 鈥?Status field helpers
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
_KERNEL_LINE_RE = re.compile(r"^> \*\*Kernel\*\*:.*$", re.MULTILINE)  # legacy, for removal
_SHA256_LINE_RE = re.compile(r"^> \*\*(?:Kernel )?SHA256\*\*:.*$", re.MULTILINE)
_EEGUNITY_VER_RE = re.compile(r"^> \*\*EEGUnity Version\*\*:.*$", re.MULTILINE)
_SCAN_TYPE_RE = re.compile(r"^> \*\*Scan Type\*\*:.*$", re.MULTILINE)

# Legacy AUTO marker constants 鈥?kept only for stripping old-format documents
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
    for eid, count in sorted(new_counts.items(), key=lambda x: x[0]):
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
    """Parse ### Info table rows 鈫?{field: {completeness, notes}}."""
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
    misc_channel_names: List[str] = scan_result.get("misc_channel_names", [])
    sampled = scan_result.get("sampled", False)
    sampled_n = scan_result.get("sampled_n", 0)
    total_n = scan_result.get("total_n", 0)

    scan_type_str = f"Sampled ({sampled_n}/{total_n} files)" if sampled else "Full"

    # Capture old ## File Scan Result block for diff (after marker stripping)
    fsr_m0 = _FILE_SCAN_RE.search(new_content)
    old_fsr_text = fsr_m0.group(0).rstrip() if fsr_m0 else ""

    # 鈹€鈹€ 1. Update kernel fingerprint header 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
    fsr_m = _FILE_SCAN_RE.search(new_content)
    if fsr_m:
        block = fsr_m.group(2)
        new_sha_line  = f"> **Kernel SHA256**: `{kernel_sha256}`"
        new_ver_line  = f"> **EEGUnity Version**: `{eegunity_version}`"
        new_scan_line = f"> **Scan Type**: {scan_type_str}"

        # Remove legacy > **Kernel**: line if present
        block = _KERNEL_LINE_RE.sub("", block)
        block = re.sub(r"\n{2,}", "\n", block)  # collapse any blank line left behind

        # Kernel SHA256: update (matches old SHA256 or new Kernel SHA256) or insert at top
        block = _SHA256_LINE_RE.sub(new_sha_line, block) \
            if _SHA256_LINE_RE.search(block) else new_sha_line + "\n" + block.lstrip("\n")

        # EEGUnity Version: update or insert after Kernel SHA256
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

    # 鈹€鈹€ 2. Update Event Structure table 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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

    # 鈹€鈹€ 3. Update Info table (preserve Notes where Completeness unchanged) 鈹€鈹€鈹€
    info_m = re.search(
        r"(### Info\s*\n\| Field.*?\n\|[-| ]+\n)(.*?)(?=\n###|\n## |\Z)",
        new_content, re.DOTALL,
    )
    if info_m:
        existing_info = _parse_info_table(info_m.group(2))
        new_info_tbl = _build_info_table_smart(subject_info, existing_info)
        new_content = new_content[:info_m.start(2)] + new_info_tbl + "\n" + new_content[info_m.end(2):]

    # ── 4. Update MISC Label Summary Candidate Labels (only when misc channels present) ──
    if misc_channel_names:
        misc_m = re.search(
            r"(### MISC Label Summary\s*\n)(.*?)(?=\n###|\n## |\Z)",
            new_content, re.DOTALL,
        )
        if misc_m:
            inner = misc_m.group(2)
            labels_str = ", ".join(f"`{c}`" for c in misc_channel_names)
            new_candidate_line = f"- **Candidate Labels**: {labels_str}"
            # Match any existing "- **Candidate ...**: ..." line (handles label name variants)
            candidate_re = re.compile(r"^- \*\*Candidate[^*]*\*\*:.*$", re.MULTILINE)
            if candidate_re.search(inner):
                inner = candidate_re.sub(new_candidate_line, inner)
            else:
                inner = inner.rstrip("\n") + "\n" + new_candidate_line + "\n"
            new_content = new_content[:misc_m.start(2)] + inner + new_content[misc_m.end(2):]

    # 鈹€鈹€ Produce single diff for entire File Scan Result block 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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
_DOC_SHA256_RE = re.compile(r"^> \*\*(?:Kernel )?SHA256\*\*:\s*`([^`]*)`", re.MULTILINE)


def _read_doc_sha256(content: str) -> str:
    """Extract the Kernel SHA256 recorded in analysis.md content.

    Returns empty string when absent, N/A, or any placeholder that signals
    the document has never been scanned with a kernel.
    """
    m = _DOC_SHA256_RE.search(content)
    if not m:
        return ""
    val = m.group(1).strip()
    if val.lower() in ("n/a", "na", "no_kernel", "file_not_found", ""):
        return ""
    return val


def list_datasets() -> List[Dict]:
    cfg = load_machine_config()
    dataset_roots = cfg.get("dataset_roots", [])

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
        dataset_found = bool(find_dataset_path(entry.name, dataset_roots))

        # Kernel SHA256 staleness check
        kernel_sha256_outdated = False
        if kernel:
            doc_sha = _read_doc_sha256(content)
            cur_sha = get_kernel_sha256(kernel)
            # Outdated when: doc is blank/N/A (never scanned) OR hashes differ
            kernel_sha256_outdated = (doc_sha == "" or doc_sha != cur_sha)

        result.append({
            "name": entry.name,
            "status": status,
            "category": category,
            "has_kernel": kernel is not None,
            "kernel_path": kernel or "",
            "has_cache": cache_ok,
            "dataset_found": dataset_found,
            "kernel_sha256_outdated": kernel_sha256_outdated,
        })
    return result


# ---------------------------------------------------------------------------
# LLM sampling prompt builder
# ---------------------------------------------------------------------------

_GENERIC_PREFIXES = {
    "sub", "subj", "subject", "s", "p", "participant",
    "run", "ses", "session", "file", "data", "eeg", "rec",
}

_TASK_LABELS = {
    "artifact": "Artifact",
    "erp": "ERP",
    "mi": "MI",
    "p300": "P300",
    "ssvep": "SSVEP",
}

_PROTOCOL_LABELS = {
    "5f": "5F",
    "cla": "CLA",
    "freeform": "FREEFORM",
    "freedom": "FREEFORM",
    "halt": "HaLT",
    "nomt": "NoMT",
}


def _normalize_sampling_path(path_str: str) -> str:
    return str(path_str).replace("\\", "/").strip()


def _sampling_path_parts(path_str: str) -> List[str]:
    return [part for part in _normalize_sampling_path(path_str).split("/") if part and part != "."]


def _sampling_common_parts(paths: List[str]) -> List[str]:
    split_paths = [_sampling_path_parts(p) for p in paths if str(p).strip()]
    if not split_paths:
        return []
    common: List[str] = []
    for idx in range(min(len(parts) for parts in split_paths)):
        val = split_paths[0][idx]
        if all(parts[idx] == val for parts in split_paths[1:]):
            common.append(val)
        else:
            break
    return common


def _relative_sampling_parts(path_str: str, common_parts: List[str]) -> List[str]:
    parts = _sampling_path_parts(path_str)
    i = 0
    max_i = min(len(parts), len(common_parts))
    while i < max_i and parts[i] == common_parts[i]:
        i += 1
    return parts[i:] or parts[-1:]


def _format_sampling_number(value: Any) -> str:
    s = str(value).strip()
    if s.lower() in ("", "nan", "none"):
        return ""
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
        return f"{f:g}"
    except Exception:
        return s


def _channel_signature(row: pd.Series) -> Tuple[str, str]:
    nch = _format_sampling_number(row.get("Number of Channels", ""))
    sfreq = _format_sampling_number(row.get("Sampling Rate", ""))
    ch_names = str(row.get("Channel Names", "")).strip().lower()
    ch_names = ",".join(part.strip() for part in ch_names.split(",") if part.strip())
    ch_hash = hashlib.md5(ch_names.encode("utf-8")).hexdigest()[:6] if ch_names else ""
    key = f"{nch}|{sfreq}|{ch_hash}"
    label_bits = []
    if nch:
        label_bits.append(f"{nch}ch")
    if sfreq:
        label_bits.append(f"{sfreq}Hz")
    return key, "@".join(label_bits) if label_bits else "structure-unknown"


def _extract_experiment_label(text: str) -> Optional[str]:
    m = re.search(r"(?i)(?:^|[^a-z0-9])exp(?:eriment)?[_-]?0*(\d+)(?:$|[^a-z0-9])", text)
    return f"Exp{int(m.group(1))}" if m else None


def _extract_task_label(text: str) -> Optional[str]:
    m = re.search(r"(?i)(?:^|[_-])eeg[_-](mi|ssvep|erp|artifact|p300)(?:$|[_-])", text)
    if not m:
        m = re.search(r"(?i)(?:^|[_-])(mi|ssvep|erp|artifact|p300)(?:$|[_-])", text)
    return _TASK_LABELS.get(m.group(1).lower()) if m else None


def _extract_protocol_label(stem: str) -> Optional[str]:
    m = re.match(r"(?i)^(5f|cla|halt|freeform|freedom|nomt)(?=subject|[-_]|[A-Z]|$)", stem)
    return _PROTOCOL_LABELS.get(m.group(1).lower()) if m else None


def _is_noise_part(part: str) -> bool:
    low = part.lower()
    if low in _GENERIC_PREFIXES or low in {"openbmi", "dataset", "raw", "files"}:
        return True
    if re.fullmatch(r"(?:subj(?:ect)?|sub|participant)[a-z0-9]+", low):
        return True
    if re.fullmatch(r"(?:sess(?:ion)?|ses|run|trial|record|rec|block)\d+[a-z]*", low):
        return True
    if re.fullmatch(r"s\d{1,3}", low):
        return True
    if re.fullmatch(r"\d{4,}", low):
        return True
    return False


def _fallback_dir_group(rel_parts: List[str]) -> Optional[str]:
    for part in rel_parts[:-1]:
        if not _is_noise_part(part):
            return part
    return None


def _fallback_stem_group(stem: str) -> Optional[str]:
    m = re.match(r"([A-Za-z][A-Za-z0-9]{1,24})", stem)
    if not m:
        return None
    candidate = m.group(1)
    if _is_noise_part(candidate):
        return None
    return candidate


def _infer_group(rel_parts: List[str], row: pd.Series) -> Tuple[str, str]:
    joined = "/".join(rel_parts)
    stem = Path(rel_parts[-1]).stem

    for text in rel_parts[:-1]:
        label = _extract_experiment_label(text)
        if label:
            return label, "experiment"

    for text in (joined, stem):
        label = _extract_experiment_label(text)
        if label:
            return label, "experiment"

    label = _extract_task_label(stem)
    if label:
        return label, "task"

    label = _extract_protocol_label(stem)
    if label:
        return label, "protocol"

    label = _fallback_dir_group(rel_parts)
    if label:
        return label, "directory"

    label = _fallback_stem_group(stem)
    if label:
        return label, "stem"

    _, structure_label = _channel_signature(row)
    return structure_label, "structure"


def _pick_group_representative(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    fingerprint_counts: Dict[str, int] = {}
    for record in records:
        key = record["structure_key"]
        fingerprint_counts[key] = fingerprint_counts.get(key, 0) + 1
    dominant_key = max(
        fingerprint_counts.items(),
        key=lambda item: (item[1], item[0]),
    )[0]

    def _duration_value(record: Dict[str, Any]) -> float:
        try:
            return float(record["duration_s"])
        except Exception:
            return float("inf")

    return min(
        records,
        key=lambda record: (
            record["structure_key"] != dominant_key,
            record["completeness"] != "Completed",
            len(record["file"]),
            _duration_value(record),
            record["idx"],
        ),
    )


def _select_local_groups(group_list: List[Dict[str, Any]], max_sample: int) -> List[Dict[str, Any]]:
    if len(group_list) <= max_sample:
        return list(group_list)

    remaining = list(group_list)
    selected: List[Dict[str, Any]] = []
    seen_structures = set()

    while remaining and len(selected) < max_sample:
        best = max(
            remaining,
            key=lambda item: (
                sum(1 for label in item["structure_labels"] if label not in seen_structures),
                item["count"],
                -item["first_index"],
            ),
        )
        selected.append(best)
        seen_structures.update(best["structure_labels"])
        remaining.remove(best)

    selected.sort(key=lambda item: (item["first_index"], item["group"]))
    return selected


def _prepare_sampling_records(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    data_mask = df.get("Completeness Check", pd.Series(dtype=str)).astype(str).str.strip() != "Unavailable"
    data_df = df[data_mask].copy()
    if data_df.empty:
        data_df = df.copy()

    paths = data_df.get("File Path", pd.Series([], dtype=str)).astype(str).tolist()
    common_parts = _sampling_common_parts(paths)
    records: List[Dict[str, Any]] = []
    for idx, row in data_df.iterrows():
        path_str = str(row.get("File Path", ""))
        rel_parts = _relative_sampling_parts(path_str, common_parts)
        rel_path = "/".join(rel_parts)
        structure_key, structure_label = _channel_signature(row)
        group_label, group_source = _infer_group(rel_parts, row)
        records.append({
            "idx": idx,
            "file": rel_path,
            "group": group_label,
            "group_source": group_source,
            "shape": str(row.get("Data Shape", "?")),
            "duration_s": str(row.get("Duration", "?")),
            "completeness": str(row.get("Completeness Check", "?")),
            "structure_key": structure_key,
            "structure_label": structure_label,
        })
    return data_df, records


def prepare_sampling_plan(dataset_name: str, df: pd.DataFrame, max_sample: int = 10) -> Dict[str, Any]:
    data_df, records = _prepare_sampling_records(df)
    groups: Dict[str, Dict[str, Any]] = {}
    for record in records:
        bucket = groups.setdefault(record["group"], {
            "group": record["group"],
            "group_source": record["group_source"],
            "records": [],
            "structure_labels": set(),
            "first_index": record["idx"],
        })
        bucket["records"].append(record)
        bucket["structure_labels"].add(record["structure_label"])
        bucket["first_index"] = min(bucket["first_index"], record["idx"])

    group_list: List[Dict[str, Any]] = []
    for group in groups.values():
        rep = _pick_group_representative(group["records"])
        group_list.append({
            "group": group["group"],
            "group_source": group["group_source"],
            "count": len(group["records"]),
            "first_index": group["first_index"],
            "representative": rep,
            "structure_labels": sorted(group["structure_labels"]),
            "example_files": [r["file"] for r in group["records"][:2]],
        })

    group_list.sort(key=lambda item: (item["first_index"], item["group"]))
    local_groups = _select_local_groups(group_list, max_sample)
    plan = {
        "dataset_name": dataset_name,
        "total_rows": len(df),
        "data_rows": len(data_df),
        "group_count": len(group_list),
        "groups": group_list,
        "local_groups": local_groups,
        "sampled_indices": [item["representative"]["idx"] for item in local_groups],
        "groups_covered": [item["group"] for item in local_groups],
    }
    if len(group_list) <= max_sample:
        plan["strategy"] = "local"
        plan["reason"] = (
            f"Local path-aware grouping found {len(group_list)} representative group(s), "
            f"which fits within the sample limit of {max_sample}."
        )
    else:
        plan["strategy"] = "llm"
        plan["reason"] = (
            f"Local grouping found {len(group_list)} candidate group(s), which exceeds "
            f"the sample limit of {max_sample}; an LLM can prioritize the most useful ones."
        )
    return plan


def build_sampling_prompt(dataset_name: str, plan: Dict[str, Any], max_sample: int = 10) -> str:
    group_rows = []
    for item in plan["groups"]:
        rep = item["representative"]
        group_rows.append({
            "group": item["group"],
            "group_source": item["group_source"],
            "count": item["count"],
            "structure": item["structure_labels"],
            "representative_idx": rep["idx"],
            "representative_file": rep["file"],
            "representative_shape": rep["shape"],
            "representative_duration_s": rep["duration_s"],
            "examples": item["example_files"],
        })

    prompt = (
        f"You are helping select a minimal but representative sample of EEG files "
        f"for dataset '{dataset_name}'.\n\n"
        f"Total locator rows: {plan['total_rows']}. EEG data rows: {plan['data_rows']}.\n"
        f"Local path-aware grouping found {plan['group_count']} candidate groups.\n"
        "Each group below already has one locally chosen representative file. "
        "Prefer covering distinct experiments/paradigms/tasks first, and use channel/sampling "
        "structure only as a secondary tie-breaker.\n\n"
        "Group summary:\n"
        + json.dumps(group_rows, indent=2)
        + f"\n\nTask: Select at most {max_sample} representative_idx values.\n"
        "1. Prioritize broad paradigm / experiment coverage.\n"
        "2. Avoid selecting multiple groups that look structurally redundant unless necessary.\n"
        "3. Keep exactly one representative per chosen group.\n\n"
        "Return a JSON object ONLY with:\n"
        '  "sampled_indices": [representative_idx integers]\n'
        '  "groups_covered": [group labels]\n'
        '  "reason": one sentence explanation\n\n'
        'Example: {"sampled_indices": [0, 42, 84], "groups_covered": ["Exp1", "Exp2", "Exp3"], "reason": "..."}'
    )
    return prompt



