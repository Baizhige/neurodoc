"""Read-only tool surface exposed to the LLM during Phase 1/4.

Every tool takes the LocatorReport (and optionally a ProbeReport) and a
relative path within the dataset root. The LLM never sees absolute paths
and cannot escape the dataset root.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# -----------------------------------------------------------------------------
# Path safety
# -----------------------------------------------------------------------------

def _safe_join(root: str, rel: str) -> Path:
    rel = (rel or "").lstrip("/").lstrip("\\")
    p = (Path(root) / rel).resolve()
    root_resolved = Path(root).resolve()
    if not str(p).startswith(str(root_resolved)):
        raise ValueError(f"path escapes dataset root: {rel}")
    return p


# -----------------------------------------------------------------------------
# Tools
# -----------------------------------------------------------------------------

def find_files(locator, ext: str, max_results: int = 200) -> List[str]:
    """Return list of rel_paths matching extension."""
    ext = ext.lower()
    if not ext.startswith("."):
        ext = "." + ext
    files = locator.raw_files.get(ext, [])
    return [f.rel_path for f in files[:max_results]]


def list_tree(locator, subpath: str = "", depth: int = 2, max_lines: int = 200) -> str:
    """Return tree summary rooted at subpath."""
    target = _safe_join(locator.root, subpath)
    if not target.is_dir():
        return f"[not a directory: {subpath}]"
    lines: List[str] = []

    def _walk(d: Path, _depth: int):
        if _depth > depth:
            return
        try:
            entries = sorted(d.iterdir())
        except (PermissionError, FileNotFoundError):
            return
        for e in entries[:50]:
            indent = "  " * _depth
            if e.is_dir():
                lines.append(f"{indent}{e.name}/")
                _walk(e, _depth + 1)
            else:
                lines.append(f"{indent}{e.name}")
            if len(lines) >= max_lines:
                return

    _walk(target, 0)
    return "\n".join(lines[:max_lines])


def read_tsv(locator, rel_path: str, nrows: int = 20) -> Dict[str, Any]:
    """Read TSV/CSV; auto-detect delimiter. Returns header + first nrows."""
    p = _safe_join(locator.root, rel_path)
    if not p.is_file():
        return {"error": "file not found"}
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        first = text.splitlines()[0] if text else ""
        delim = "\t" if "\t" in first else ","
        import csv
        rows = list(csv.reader(text.splitlines(), delimiter=delim))
        if not rows:
            return {"columns": [], "n_rows": 0, "rows": []}
        return {
            "columns": rows[0],
            "n_rows": len(rows) - 1,
            "rows": rows[1:1 + nrows],
        }
    except Exception as e:
        return {"error": str(e)}


def read_json(locator, rel_path: str) -> Any:
    p = _safe_join(locator.root, rel_path)
    if not p.is_file():
        return {"_error": "file not found"}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def read_text(locator, rel_path: str, max_chars: int = 8000) -> str:
    p = _safe_join(locator.root, rel_path)
    if not p.is_file():
        return "[file not found]"
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n...[truncated; total {len(text)} chars]"
        return text
    except Exception as e:
        return f"[read error: {e}]"


def peek_edf_header(locator, rel_path: str) -> Dict[str, Any]:
    """Inspect EDF/BDF header without preloading data."""
    p = _safe_join(locator.root, rel_path)
    if not p.is_file():
        return {"error": "file not found"}
    try:
        import mne
        if p.suffix.lower() == ".edf":
            raw = mne.io.read_raw_edf(str(p), preload=False, verbose="ERROR")
        elif p.suffix.lower() == ".bdf":
            raw = mne.io.read_raw_bdf(str(p), preload=False, verbose="ERROR")
        elif p.suffix.lower() == ".gdf":
            raw = mne.io.read_raw_gdf(str(p), preload=False, verbose="ERROR")
        else:
            return {"error": f"unsupported ext: {p.suffix}"}
        try:
            annot = list(raw.annotations.description)[:50]
        except Exception:
            annot = []
        return {
            "ch_names": list(raw.ch_names)[:50],
            "n_channels": len(raw.ch_names),
            "sfreq": float(raw.info["sfreq"]),
            "n_times": int(raw.n_times),
            "annotations": annot,
        }
    except Exception as e:
        return {"error": str(e)}


def peek_xml_events(locator, rel_path: str, max_events: int = 50) -> Dict[str, Any]:
    """Summarise an NSRR / EDF+ XML annotation file."""
    p = _safe_join(locator.root, rel_path)
    if not p.is_file():
        return {"error": "file not found"}
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(str(p))
        root = tree.getroot()
        events: List[Dict[str, Any]] = []
        type_counter: Dict[str, int] = {}
        concept_counter: Dict[str, int] = {}
        for ev in root.iter():
            tag = ev.tag.split("}")[-1]  # strip namespace
            if tag.lower() in ("scoredevent", "event"):
                etype = ""
                econcept = ""
                for child in ev:
                    ctag = child.tag.split("}")[-1].lower()
                    if ctag == "eventtype":
                        etype = (child.text or "").strip()
                    elif ctag == "eventconcept":
                        econcept = (child.text or "").strip()
                type_counter[etype] = type_counter.get(etype, 0) + 1
                concept_counter[econcept] = concept_counter.get(econcept, 0) + 1
                if len(events) < max_events:
                    events.append({"type": etype, "concept": econcept})
        return {
            "n_events_sampled": len(events),
            "type_counts_top": sorted(type_counter.items(), key=lambda kv: -kv[1])[:20],
            "concept_counts_top": sorted(concept_counter.items(), key=lambda kv: -kv[1])[:20],
            "sample": events,
        }
    except Exception as e:
        return {"error": str(e)}


def query_locator(locator, field: str) -> Any:
    """Direct accessor to a top-level LocatorReport field."""
    return locator.to_dict().get(field)


def query_probe(probe, field: str) -> Any:
    """Direct accessor to a top-level ProbeReport field."""
    if probe is None:
        return None
    if isinstance(probe, dict):
        return probe.get(field)
    return getattr(probe, field, None)


# -----------------------------------------------------------------------------
# Tool registry (for LLM-driven tool calls in Phase 4)
# -----------------------------------------------------------------------------

def get_tool_registry(locator, probe=None) -> Dict[str, Any]:
    """Bind tools to the current locator/probe; return name → callable."""
    return {
        "find_files":      lambda ext, max_results=200: find_files(locator, ext, max_results),
        "list_tree":       lambda subpath="", depth=2, max_lines=200: list_tree(locator, subpath, depth, max_lines),
        "read_tsv":        lambda rel_path, nrows=20: read_tsv(locator, rel_path, nrows),
        "read_json":       lambda rel_path: read_json(locator, rel_path),
        "read_text":       lambda rel_path, max_chars=8000: read_text(locator, rel_path, max_chars),
        "peek_edf_header": lambda rel_path: peek_edf_header(locator, rel_path),
        "peek_xml_events": lambda rel_path, max_events=50: peek_xml_events(locator, rel_path, max_events),
        "query_locator":   lambda field: query_locator(locator, field),
        "query_probe":     lambda field: query_probe(probe, field),
    }
