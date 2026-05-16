"""Phase 1: Locate.

Deterministic, no-LLM directory survey that produces a LocatorReport (JSON):
- raw EEG file inventory by extension and group
- annotation/sidecar file inventory with pairing rules
- BIDS sidecar parses (participants.tsv, *_events.json, channels.tsv)
- group detection (path/filename rules)
- tree summary for LLM prompts

Reuses scan_engine's base locator cache when available so we don't re-walk
huge datasets like SHHS (~26k files).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from ..paths import LOCATOR_CACHE_DIR
except ImportError:
    from paths import LOCATOR_CACHE_DIR


RAW_EXTS = (".edf", ".bdf", ".gdf", ".set", ".vhdr", ".cnt", ".mat", ".fif", ".fdt")
ANNOT_EXTS = (".xml", ".tsv", ".json", ".csv", ".evt", ".sto", ".txt")
DOC_EXTS = (".md", ".rst", ".txt", ".pdf")

# Sidecar filenames we recognise (BIDS + common variants)
SIDECAR_PATTERNS = {
    "participants_tsv": re.compile(r"^participants\.tsv$", re.I),
    "participants_json": re.compile(r"^participants\.json$", re.I),
    "dataset_description": re.compile(r"^dataset_description\.json$", re.I),
    "channels_tsv": re.compile(r".*_channels\.tsv$", re.I),
    "events_tsv": re.compile(r".*_events\.tsv$", re.I),
    "events_json": re.compile(r".*_events\.json$", re.I),
    "eeg_json": re.compile(r".*_eeg\.json$", re.I),
    "readme": re.compile(r"^README(\.[A-Za-z]+)?$", re.I),
    "changelog": re.compile(r"^CHANGES?(\.[A-Za-z]+)?$", re.I),
}


@dataclass
class RawFileEntry:
    rel_path: str
    size: int
    group_key: str = ""


@dataclass
class AnnotationFileEntry:
    rel_path: str
    kind: str                    # nsrr_xml | bids_events_tsv | bids_events_json | rpoint_csv | edf_annot | other
    pairs_with: Optional[str]    # rel_path of paired raw, or None
    pairing_rule: str            # stem_match | sibling | rooted_at:<dir> | none


@dataclass
class GroupEntry:
    key: str
    n_files: int
    annot_dir: Optional[str]
    source: str                  # path | filename | sidecar | none


@dataclass
class LocatorReport:
    dataset_name: str
    root: str
    format: str                  # heuristic: bids | edf+xml-sidecar | mat | set | mixed
    raw_files: Dict[str, List[RawFileEntry]] = field(default_factory=dict)
    annotation_files: List[AnnotationFileEntry] = field(default_factory=list)
    sidecars: Dict[str, Any] = field(default_factory=dict)
    groups: List[GroupEntry] = field(default_factory=list)
    tree_summary: str = ""
    rename_evidence: Dict[str, str] = field(default_factory=dict)
    cache_key: str = ""
    scanned_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def total_raw_files(self) -> int:
        return sum(len(v) for v in self.raw_files.values())


# -----------------------------------------------------------------------------
# Group detection
# -----------------------------------------------------------------------------

def _detect_group_key(rel_path: str) -> Tuple[str, str]:
    """Return (group_key, source).

    Order of precedence (first match wins):
    1. Path segment ses-XX  → "ses-XX" (BIDS session)
    2. Path segment task-XX → "task-XX" (BIDS task; only if no ses-)
    3. Path segment train|eval|test|valid → that segment
    4. Path segment ExpN | ExperimentN → that segment
    5. Path segment shhsN → that segment
    6. Filename suffix `_T.gdf` / `_E.gdf` → "T" or "E"
    7. Otherwise: ""
    """
    parts = rel_path.replace("\\", "/").split("/")

    for p in parts:
        m = re.match(r"^(ses-[A-Za-z0-9]+)$", p)
        if m:
            return m.group(1), "path"
    for p in parts:
        m = re.match(r"^(task-[A-Za-z0-9_]+)$", p)
        if m:
            return m.group(1), "path"
    for p in parts:
        if p.lower() in ("train", "eval", "test", "valid", "validation"):
            return p.lower(), "path"
    for p in parts:
        m = re.match(r"^(Exp(?:eriment)?[-_]?\d+)$", p, re.I)
        if m:
            return m.group(1), "path"
    for p in parts:
        m = re.match(r"^(shhs\d+)$", p, re.I)
        if m:
            return m.group(1).lower(), "path"

    # Filename heuristics
    name = parts[-1]
    base = os.path.splitext(name)[0]

    # BIDS-style task-XX or ses-XX inside the filename (most common case for
    # OpenNeuro datasets where each subject directory holds many task files).
    m = re.search(r"_(task-[A-Za-z0-9]+)", base)
    if m:
        return m.group(1), "filename"
    m = re.search(r"_(ses-[A-Za-z0-9]+)", base)
    if m:
        return m.group(1), "filename"

    # Train/Eval split: A01T / A01E (BCI Competition IV) — single trailing T or E
    m = re.match(r"^[A-Za-z]\d+([TE])$", base)
    if m:
        return f"split-{m.group(1)}", "filename"
    m = re.search(r"_([TE])$", base)
    if m:
        return f"split-{m.group(1)}", "filename"
    m = re.search(r"_(Exp\d+)\.?", base, re.I)
    if m:
        return m.group(1), "filename"

    return "", "none"


# -----------------------------------------------------------------------------
# Annotation pairing
# -----------------------------------------------------------------------------

def _classify_annotation(rel_path: str) -> str:
    name = os.path.basename(rel_path).lower()
    if name.endswith("-nsrr.xml") or name.endswith("-profusion.xml"):
        return "nsrr_xml"
    if name.endswith("_events.tsv"):
        return "bids_events_tsv"
    if name.endswith("_events.json"):
        return "bids_events_json"
    if "rpoint" in name and name.endswith(".csv"):
        return "rpoint_csv"
    if name.endswith(".xml"):
        return "xml_other"
    if name.endswith(".tsv") and "channels" in name:
        return "bids_channels_tsv"
    return "other"


def _find_pairing(annot_rel: str, raw_index: Dict[str, str], root: Path) -> Tuple[Optional[str], str]:
    """Given an annotation rel path and an index of raw {stem -> rel_path},
    return (paired_raw_rel, pairing_rule).

    Strategies tried in order:
    1. Sibling stem match (annot.parent == raw.parent and stems share prefix)
    2. Cross-directory stem match (annot stem strips suffix like '-nsrr', '_events')
    3. Rooted-at: annot lives under '*-nsrr/<group>/<stem>...' and raw lives under 'edfs/<group>/<stem>...'
    """
    annot = Path(annot_rel)
    annot_stem = annot.stem
    # Strip common suffixes
    cleaned = re.sub(r"(-nsrr|-profusion|-rpoint|_events|_channels|_eeg)$", "", annot_stem, flags=re.I)

    # Direct stem match
    if cleaned in raw_index:
        raw_rel = raw_index[cleaned]
        if Path(raw_rel).parent == annot.parent:
            return raw_rel, "sibling"
        # Detect rooted_at pattern
        annot_parts = annot.parts
        raw_parts = Path(raw_rel).parts
        # find first differing segment
        diff_idx = next(
            (i for i in range(min(len(annot_parts), len(raw_parts))) if annot_parts[i] != raw_parts[i]),
            min(len(annot_parts), len(raw_parts)),
        )
        if diff_idx > 0 and diff_idx < len(annot_parts):
            return raw_rel, f"rooted_at:{annot_parts[diff_idx]}"
        return raw_rel, "stem_match"

    return None, "none"


# -----------------------------------------------------------------------------
# Sidecar reading
# -----------------------------------------------------------------------------

def _safe_read_text(p: Path, max_chars: int = 8000) -> str:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n...[truncated; total {len(text)} chars]"
        return text
    except Exception as e:
        return f"[read error: {e}]"


def _read_tsv_summary(p: Path, nrows: int = 20) -> Dict[str, Any]:
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)
        if not rows:
            return {"columns": [], "n_rows": 0, "rows": []}
        header = rows[0]
        body = rows[1:]
        return {
            "columns": header,
            "n_rows": len(body),
            "rows": body[:nrows],
        }
    except Exception as e:
        return {"error": str(e)}


def _read_json(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}


# -----------------------------------------------------------------------------
# Format detection
# -----------------------------------------------------------------------------

def _detect_format(raw_files: Dict[str, List[RawFileEntry]],
                   sidecars: Dict[str, Any],
                   annotation_files: List[AnnotationFileEntry]) -> str:
    has_bids = bool(sidecars.get("dataset_description"))
    has_events_tsv = any(a.kind == "bids_events_tsv" for a in annotation_files)
    has_nsrr_xml = any(a.kind == "nsrr_xml" for a in annotation_files)
    nonempty_exts = [e for e, v in raw_files.items() if v]

    if has_bids or has_events_tsv:
        return "bids"
    if has_nsrr_xml:
        return "edf+xml-sidecar"
    if nonempty_exts == [".mat"]:
        return "mat"
    if nonempty_exts == [".set"] or nonempty_exts == [".set", ".fdt"]:
        return "set"
    if len(nonempty_exts) > 1:
        return "mixed"
    if nonempty_exts:
        return nonempty_exts[0].lstrip(".")
    return "unknown"


# -----------------------------------------------------------------------------
# Tree summary
# -----------------------------------------------------------------------------

def _tree_summary(root: Path, max_depth: int = 3, max_entries_per_dir: int = 50) -> str:
    lines: List[str] = []

    def _walk(d: Path, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(d.iterdir())
        except (PermissionError, FileNotFoundError):
            return
        if depth == max_depth and len(entries) > max_entries_per_dir:
            head = entries[:max_entries_per_dir]
            tail_n = len(entries) - max_entries_per_dir
            for e in head:
                lines.append(f"{'  ' * depth}{e.name}{'/' if e.is_dir() else ''}")
            lines.append(f"{'  ' * depth}... [+{tail_n} more]")
            return
        for e in entries[:max_entries_per_dir if len(entries) > max_entries_per_dir else None]:
            if e.is_dir():
                lines.append(f"{'  ' * depth}{e.name}/")
                _walk(e, depth + 1)
            else:
                lines.append(f"{'  ' * depth}{e.name}")

    _walk(root, 0)
    return "\n".join(lines[:2000])  # hard cap


# -----------------------------------------------------------------------------
# Walking
# -----------------------------------------------------------------------------

def _walk_dataset(root: Path) -> Tuple[List[Path], List[Path], List[Path]]:
    """Return (raw_files, annot_files, doc_files) — sorted absolute paths."""
    raws, annots, docs = [], [], []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Skip hidden/derivative dirs commonly seen
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in (
            "__pycache__", ".git", "derivatives", "code"
        )]
        for fn in filenames:
            if fn.startswith("._"):  # macOS metadata
                continue
            p = Path(dirpath) / fn
            ext = p.suffix.lower()
            if ext in RAW_EXTS:
                raws.append(p)
            elif ext in ANNOT_EXTS:
                annots.append(p)
            elif ext in DOC_EXTS or fn.upper().startswith("README"):
                docs.append(p)
    return sorted(raws), sorted(annots), sorted(docs)


# -----------------------------------------------------------------------------
# Cache helpers
# -----------------------------------------------------------------------------

def _manifest_hash(files: List[Path]) -> str:
    h = hashlib.sha256()
    for f in files:
        try:
            st = f.stat()
            h.update(f"{f}|{st.st_size}|{int(st.st_mtime)}\n".encode())
        except OSError:
            pass
    return h.hexdigest()[:16]


def _cache_path(dataset_name: str, workspace: Optional[Path] = None) -> Path:
    if workspace is not None:
        return Path(workspace) / dataset_name / "locator.json"
    return Path(LOCATOR_CACHE_DIR) / f"{dataset_name}_locate.json"


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

def build_locator_report(
    dataset_name: str,
    dataset_root: str,
    workspace: Optional[Path] = None,
    use_cache: bool = True,
) -> LocatorReport:
    """Build (or load from cache) a LocatorReport for one dataset.

    workspace, if given, redirects the JSON output (used by the test harness
    to land artefacts in Script/claudecodeWP/<dataset>/ instead of the
    runtime cache dir).
    """
    import datetime as dt

    root = Path(dataset_root)
    if not root.is_dir():
        raise FileNotFoundError(f"dataset_root does not exist: {root}")

    cache_path = _cache_path(dataset_name, workspace)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    raws, annots, docs = _walk_dataset(root)
    cache_key = _manifest_hash(raws + annots + docs)

    if use_cache and cache_path.exists():
        try:
            existing = json.loads(cache_path.read_text(encoding="utf-8"))
            if existing.get("cache_key") == cache_key:
                return _from_dict(existing)
        except Exception:
            pass

    # ---- raw_files grouped by extension, with group_key per file ----
    raw_files: Dict[str, List[RawFileEntry]] = {ext: [] for ext in RAW_EXTS}
    for f in raws:
        rel = str(f.relative_to(root))
        gk, _ = _detect_group_key(rel)
        raw_files[f.suffix.lower()].append(
            RawFileEntry(rel_path=rel, size=f.stat().st_size, group_key=gk)
        )
    raw_files = {k: v for k, v in raw_files.items() if v}

    # ---- raw stem index for pairing ----
    raw_index: Dict[str, str] = {}
    for ext_files in raw_files.values():
        for r in ext_files:
            stem = Path(r.rel_path).stem
            raw_index[stem] = r.rel_path

    # ---- annotation files with pairing ----
    annotation_files: List[AnnotationFileEntry] = []
    for f in annots:
        rel = str(f.relative_to(root))
        kind = _classify_annotation(rel)
        if kind in ("xml_other", "other"):
            # skip noisy generic XMLs unless they look like NSRR
            if kind == "xml_other" and "annotations" not in rel.lower():
                continue
        paired, rule = _find_pairing(rel, raw_index, root)
        annotation_files.append(
            AnnotationFileEntry(rel_path=rel, kind=kind, pairs_with=paired, pairing_rule=rule)
        )

    # ---- sidecars ----
    sidecars: Dict[str, Any] = {}
    for f in annots + docs:
        rel = str(f.relative_to(root))
        name = f.name
        for key, pat in SIDECAR_PATTERNS.items():
            if pat.match(name):
                if key in ("participants_tsv", "channels_tsv", "events_tsv"):
                    sidecars.setdefault(key, []).append({
                        "rel_path": rel, **_read_tsv_summary(f)
                    })
                elif key in ("participants_json", "dataset_description", "events_json", "eeg_json"):
                    sidecars.setdefault(key, []).append({
                        "rel_path": rel, "data": _read_json(f)
                    })
                else:  # readme, changelog
                    sidecars.setdefault(key, []).append({
                        "rel_path": rel, "text": _safe_read_text(f)
                    })
                break

    # ---- groups: aggregate by group_key ----
    group_counts: Dict[str, int] = {}
    group_source: Dict[str, str] = {}
    for ext_files in raw_files.values():
        for r in ext_files:
            gk = r.group_key or "(default)"
            group_counts[gk] = group_counts.get(gk, 0) + 1
            if gk not in group_source:
                _, src = _detect_group_key(r.rel_path)
                group_source[gk] = src

    # Map annotation_dir per group (best-effort)
    group_annot_dir: Dict[str, str] = {}
    for a in annotation_files:
        for ext_files in raw_files.values():
            for r in ext_files:
                if a.pairs_with == r.rel_path:
                    gk = r.group_key or "(default)"
                    group_annot_dir.setdefault(gk, str(Path(a.rel_path).parent))

    groups = [
        GroupEntry(
            key=gk,
            n_files=cnt,
            annot_dir=group_annot_dir.get(gk),
            source=group_source.get(gk, "none"),
        )
        for gk, cnt in sorted(group_counts.items(), key=lambda kv: -kv[1])
    ]

    report = LocatorReport(
        dataset_name=dataset_name,
        root=str(root),
        format=_detect_format(raw_files, sidecars, annotation_files),
        raw_files=raw_files,
        annotation_files=annotation_files,
        sidecars=sidecars,
        groups=groups,
        tree_summary=_tree_summary(root),
        rename_evidence={},  # populated later if explicit evidence found
        cache_key=cache_key,
        scanned_at=dt.datetime.utcnow().isoformat(),
    )

    cache_path.write_text(json.dumps(report.to_dict(), indent=2, default=str), encoding="utf-8")
    return report


# -----------------------------------------------------------------------------
# Loading from JSON
# -----------------------------------------------------------------------------

def _from_dict(d: Dict[str, Any]) -> LocatorReport:
    rep = LocatorReport(
        dataset_name=d["dataset_name"],
        root=d["root"],
        format=d.get("format", "unknown"),
        sidecars=d.get("sidecars", {}),
        tree_summary=d.get("tree_summary", ""),
        rename_evidence=d.get("rename_evidence", {}),
        cache_key=d.get("cache_key", ""),
        scanned_at=d.get("scanned_at", ""),
    )
    rep.raw_files = {
        k: [RawFileEntry(**e) for e in v] for k, v in d.get("raw_files", {}).items()
    }
    rep.annotation_files = [AnnotationFileEntry(**a) for a in d.get("annotation_files", [])]
    rep.groups = [GroupEntry(**g) for g in d.get("groups", [])]
    return rep


def load_locator_report(path: Path) -> LocatorReport:
    return _from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
