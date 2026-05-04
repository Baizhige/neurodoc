"""Phase 1: Collect all static context for the pipeline."""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from ..paths import APP_DIR, DATASET_DOCUMENT_DIR, KERNELS_DIR
except ImportError:
    from paths import APP_DIR, DATASET_DOCUMENT_DIR, KERNELS_DIR

BIDS_ROOT = DATASET_DOCUMENT_DIR
SKILLS_DIR = KERNELS_DIR / "skills"


def _ls_tree(path: Path, max_depth: int = 3, _depth: int = 0) -> List[str]:
    lines = []
    try:
        entries = sorted(path.iterdir())
    except PermissionError:
        return []
    for e in entries:
        indent = "  " * _depth
        if e.is_dir():
            lines.append(f"{indent}{e.name}/")
            if _depth < max_depth - 1:
                lines.extend(_ls_tree(e, max_depth, _depth + 1))
        else:
            size = e.stat().st_size
            lines.append(f"{indent}{e.name}  ({size} bytes)")
    return lines


def _read_file(p: Path, max_chars: int = 12000) -> str:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n\n...[truncated, total {len(text)} chars]"
        return text
    except Exception as e:
        return f"[read error: {e}]"


def _list_refs(dataset_name: str) -> List[Path]:
    refs_dir = BIDS_ROOT / dataset_name / "references"
    if not refs_dir.is_dir():
        return []
    return sorted(refs_dir.iterdir())


def _find_kernel(dataset_name: str) -> Optional[Path]:
    candidates = [KERNELS_DIR / f"{dataset_name}.py"]
    specific = KERNELS_DIR / "openneuro_specific"
    if specific.is_dir():
        candidates.append(specific / f"{dataset_name}.py")
    for c in candidates:
        if c.exists():
            return c
    return None


def _select_example_kernels(n: int = 3) -> List[Path]:
    candidates = []
    for p in sorted(KERNELS_DIR.glob("*.py")):
        if p.name.startswith("__"):
            continue
        candidates.append(p)
    return candidates[:n]


# =============================================================================
# NEW V2: BIDS sidecar reading (evidence level ①)
# =============================================================================

def _detect_format(data_path: Path) -> str:
    """Detect dataset format type from directory structure."""
    if (data_path / "dataset_description.json").exists():
        return "bids"
    if list(data_path.rglob("*.mat"))[:1]:
        return "mat"
    if list(data_path.rglob("*.bdf"))[:1]:
        return "bdf"
    if list(data_path.rglob("*.edf"))[:1]:
        return "edf"
    return "other"


def _read_bids_sidecars(data_path: Path, log) -> Dict[str, Any]:
    """Read BIDS sidecar files from raw data directory.

    These are evidence level ① — highest priority, directly verified from data.
    """
    result: Dict[str, Any] = {}

    # --- participants.tsv: age/sex ground truth ---
    p = data_path / "participants.tsv"
    if p.exists():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            lines = text.strip().split("\n")
            rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
            n_total = len(rows)

            ages = []
            for r in rows:
                try:
                    ages.append(float(r.get("age", "")))
                except (ValueError, TypeError):
                    pass

            sexes = [
                (r.get("sex") or r.get("gender") or "").strip()
                for r in rows
                if (r.get("sex") or r.get("gender") or "").strip()
            ]
            sex_counts = dict(Counter(sexes)) if sexes else {}

            summary_parts = [f"N={n_total}"]
            if ages:
                summary_parts.append(f"age={min(ages):.1f}–{max(ages):.1f}")
            if sex_counts:
                summary_parts.append(f"sex={sex_counts}")

            result["participants_summary"] = ", ".join(summary_parts)
            result["participants_tsv_sample"] = "\n".join(lines[:8])  # header + 7 rows
            result["participants_full"] = text[:4000]

            # v3: enumerate all columns with completeness + dtype inference
            fields: List[Dict[str, Any]] = []
            if rows:
                columns = list(rows[0].keys())
                # Skip participant_id — it's an identifier, not a label field
                for col in columns:
                    if col in ("participant_id", "subject_id", ""):
                        continue
                    values = [(r.get(col) or "").strip() for r in rows]
                    non_empty = [v for v in values if v and v.lower() not in ("n/a", "na", "null", "none", "nan")]
                    k = len(non_empty)
                    # Determine completeness
                    if n_total == 0:
                        completeness = "missing"
                    elif k == 0:
                        completeness = "missing"
                    elif k >= n_total * 0.99:
                        completeness = "complete"
                    elif k >= n_total * 0.5:
                        completeness = f"partial ({k}/{n_total})"
                    else:
                        completeness = f"incomplete ({k}/{n_total})"
                    # Infer dtype
                    numeric = 0
                    for v in non_empty[:50]:
                        try:
                            float(v)
                            numeric += 1
                        except ValueError:
                            pass
                    if non_empty and numeric >= 0.9 * len(non_empty[:50]):
                        dtype = "numeric"
                    else:
                        dtype = "categorical"
                    # Sample up to 3 unique values
                    uniq = []
                    for v in non_empty:
                        if v not in uniq:
                            uniq.append(v)
                        if len(uniq) >= 3:
                            break
                    fields.append({
                        "name": col,
                        "completeness": completeness,
                        "dtype": dtype,
                        "sample_values": uniq,
                    })
            result["participants_fields"] = fields
        except Exception as e:
            result["participants_tsv_error"] = str(e)
        log(f"[Context] participants.tsv: {result.get('participants_summary', 'error')}")
        if result.get("participants_fields"):
            names = [f["name"] for f in result["participants_fields"]]
            log(f"[Context] participants.tsv columns discovered: {names}")

    # --- dataset_description.json: DOI, name, authors ---
    p = data_path / "dataset_description.json"
    if p.exists():
        try:
            result["dataset_description"] = p.read_text(encoding="utf-8", errors="replace")[:2000]
        except Exception:
            pass

    # --- task-level events.json: event semantic definitions (highest value) ---
    events_jsons: Dict[str, str] = {}
    for ep in sorted(data_path.glob("task-*_events.json")):
        try:
            content = ep.read_text(encoding="utf-8", errors="replace")[:2500]
            events_jsons[ep.name] = content
        except Exception:
            pass
    # Also check sub-level events.json if no root-level ones
    if not events_jsons:
        for ep in sorted(data_path.rglob("*_events.json"))[:2]:
            try:
                content = ep.read_text(encoding="utf-8", errors="replace")[:2500]
                events_jsons[ep.name] = content
            except Exception:
                pass
    if events_jsons:
        result["events_jsons"] = events_jsons
        log(f"[Context] events.json: {list(events_jsons.keys())}")

    # --- events.tsv samples: value→instruction mapping (critical for avoiding hallucination) ---
    # Read actual event rows to show LLM what trigger values MEAN (e.g. 1=rest, 2=task)
    # This prevents confusing trial-phase codes with MI class labels.
    events_tsv_samples: Dict[str, str] = {}
    # First try root-level task-*_events.tsv
    for ep in sorted(data_path.glob("task-*_events.tsv"))[:2]:
        try:
            lines = ep.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            events_tsv_samples[ep.name] = "\n".join(lines[:12])  # header + 11 rows
        except Exception:
            pass
    # If none at root, sample one per unique task from sub-level
    if not events_tsv_samples:
        seen_tasks: set = set()
        for ep in sorted(data_path.rglob("*_events.tsv")):
            # Extract task name from filename
            parts = ep.name.split("_")
            task_part = next((p for p in parts if p.startswith("task-")), "unknown")
            if task_part in seen_tasks:
                continue
            seen_tasks.add(task_part)
            try:
                lines = ep.read_text(encoding="utf-8", errors="replace").strip().split("\n")
                events_tsv_samples[ep.name] = "\n".join(lines[:12])
            except Exception:
                pass
            if len(seen_tasks) >= 3:  # max 3 tasks sampled
                break
    if events_tsv_samples:
        result["events_tsv_samples"] = events_tsv_samples
        log(f"[Context] events.tsv samples: {list(events_tsv_samples.keys())}")

    # v3: discover non-canonical numeric columns in events.tsv for misc candidates
    # Canonical columns (onset, duration, value, trial_type, sample, response_time*) are
    # special; numeric *_time / *_score / *_rt columns become misc candidate label fields.
    events_numeric_columns: Dict[str, List[str]] = {}
    _CANONICAL_EVENT_COLS = {"onset", "duration", "sample", "value", "trial_type", "stim_type",
                              "description", "hed", "block"}
    for fname, sample in events_tsv_samples.items():
        try:
            rows = list(csv.DictReader(io.StringIO(sample), delimiter="\t"))
            if not rows:
                continue
            candidates = []
            for col in rows[0].keys():
                if col in _CANONICAL_EVENT_COLS or not col:
                    continue
                vals = [(r.get(col) or "").strip() for r in rows]
                non_empty = [v for v in vals if v and v.lower() not in ("n/a", "na", "null", "none")]
                if not non_empty:
                    continue
                numeric = 0
                for v in non_empty:
                    try:
                        float(v)
                        numeric += 1
                    except ValueError:
                        pass
                if numeric == len(non_empty):
                    candidates.append(col)
            if candidates:
                events_numeric_columns[fname] = candidates
        except Exception:
            pass
    if events_numeric_columns:
        result["events_numeric_columns"] = events_numeric_columns
        log(f"[Context] events.tsv numeric columns: {events_numeric_columns}")

    # --- first eeg.json: device/amplifier info ---
    for ep in sorted(data_path.glob("task-*_eeg.json"))[:1]:
        try:
            result["eeg_json"] = ep.read_text(encoding="utf-8", errors="replace")[:1500]
        except Exception:
            pass
    if "eeg_json" not in result:
        for ep in sorted(data_path.rglob("*_eeg.json"))[:1]:
            try:
                result["eeg_json"] = ep.read_text(encoding="utf-8", errors="replace")[:1500]
            except Exception:
                pass

    # --- README ---
    for name in ["README", "README.md", "README.txt"]:
        p = data_path / name
        if p.exists():
            try:
                result["readme"] = p.read_text(encoding="utf-8", errors="replace")[:3000]
            except Exception:
                pass
            break

    log(f"[Context] BIDS sidecars loaded: {[k for k in result if not k.endswith('_error')]}")
    return result


def _extract_urls_from_analysis(analysis_md: str) -> List[str]:
    """Extract URLs from existing analysis.md.

    These are trusted even when the rest of analysis.md content is ignored.
    """
    urls = re.findall(r'https?://[^\s\)\]"\'>]+', analysis_md)
    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def _sample_eeg_headers(data_path: Path, log) -> str:
    """Sample EEG file headers without loading data body.

    Returns a human-readable summary of channel names, sampling rate, etc.
    """
    try:
        import mne
        mne.set_log_level("ERROR")
    except ImportError:
        return ""

    skip_suffixes = ("-proj.fif", "-fwd.fif", "-cov.fif", "-eve.fif", "-ave.fif")
    eeg_exts = [".set", ".bdf", ".edf", ".fif", ".vhdr", ".cnt"]

    found: List[Path] = []
    for ext in eeg_exts:
        candidates = [
            p for p in sorted(data_path.rglob(f"*{ext}"))
            if not any(str(p).endswith(s) for s in skip_suffixes)
        ]
        if candidates:
            found = candidates[:2]
            break

    if not found:
        return ""

    def _load_raw(p: Path):
        ext = p.suffix.lower()
        if ext == ".set":
            return mne.io.read_raw_eeglab(p, preload=False, verbose=False)
        if ext == ".bdf":
            return mne.io.read_raw_bdf(p, preload=False, verbose=False)
        if ext in (".edf", ".rec"):
            return mne.io.read_raw_edf(p, preload=False, verbose=False)
        if ext == ".fif":
            return mne.io.read_raw_fif(p, preload=False, verbose=False)
        if ext == ".vhdr":
            return mne.io.read_raw_brainvision(p, preload=False, verbose=False)
        return None

    summaries = []
    for p in found:
        try:
            raw = _load_raw(p)
            if raw is None:
                continue
            ch_names = raw.ch_names[:12]
            lines = [
                f"File: {p.name}",
                f"  Channels ({raw.info['nchan']}): {ch_names}",
                f"  Sfreq: {raw.info['sfreq']} Hz",
                f"  Duration: {raw.times[-1]:.1f}s",
            ]
            if hasattr(raw, "annotations") and len(raw.annotations) > 0:
                unique = list(dict.fromkeys(raw.annotations.description))[:10]
                lines.append(f"  Annotations (sample): {unique}")
            raw.close()
            summaries.append("\n".join(lines))
        except Exception as e:
            summaries.append(f"File: {p.name}\n  Header error: {e}")

    if summaries:
        log(f"[Context] EEG header sample: {len(summaries)} file(s)")
        return "\n\n".join(summaries)
    return ""


# =============================================================================
# Main build_context
# =============================================================================

def build_context(dataset_name: str, log, data_dir: str = "") -> Dict[str, Any]:
    """Collect all static context. Returns a dict used by all pipeline phases."""
    log(f"[Context] Building context for {dataset_name}...")

    ds_dir = BIDS_ROOT / dataset_name
    if not ds_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {ds_dir}")

    # 1. analysis.md (existing draft)
    analysis_path = ds_dir / "analysis.md"
    analysis_md = _read_file(analysis_path) if analysis_path.exists() else ""
    log(f"[Context] analysis.md: {len(analysis_md)} chars")

    # 2. URLs from analysis.md (trusted even when content is stale)
    analysis_urls = _extract_urls_from_analysis(analysis_md)

    # 3. Dataset directory tree
    tree_lines = _ls_tree(ds_dir, max_depth=3)
    ds_tree = "\n".join(tree_lines[:200])
    log(f"[Context] Directory tree: {len(tree_lines)} entries")

    # 4. References list
    ref_files = _list_refs(dataset_name)
    log(f"[Context] References: {len(ref_files)} files")

    # 5. Existing kernel
    kernel_path = _find_kernel(dataset_name)
    existing_kernel = _read_file(kernel_path) if kernel_path else ""
    log(f"[Context] Existing kernel: {kernel_path.name if kernel_path else 'none'}")

    # 6. KERNEL_RULEBOOK
    rulebook_path = KERNELS_DIR / "KERNEL_RULEBOOK.md"
    rulebook = _read_file(rulebook_path) if rulebook_path.exists() else ""
    log(f"[Context] RULEBOOK: {len(rulebook)} chars")

    # 7. SKILL files
    skill_texts: Dict[str, str] = {}
    if SKILLS_DIR.is_dir():
        for sf in sorted(SKILLS_DIR.glob("SKILL_*.md")):
            skill_texts[sf.name] = _read_file(sf, max_chars=6000)
    log(f"[Context] SKILL files: {len(skill_texts)}")

    # 8. Example kernels
    example_kernels: Dict[str, str] = {}
    for ep in _select_example_kernels(3):
        example_kernels[ep.name] = _read_file(ep, max_chars=5000)
    log(f"[Context] Example kernels: {list(example_kernels.keys())}")

    # 9. neuroaudit/rulebook.md
    app_rulebook_path = APP_DIR / "rulebook.md"
    app_rulebook = _read_file(app_rulebook_path, max_chars=8000) if app_rulebook_path.exists() else ""

    # 10. Category SKILL
    category = ""
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]+)", analysis_md)
    if m:
        category = m.group(1).strip()
    category_skill = ""
    if category:
        skill_map = {
            "Action/Output": "action_output.md",
            "Biological State": "biological_state.md",
            "Complex Applied": "complex_applied.md",
            "High-level Mental": "high_level_mental.md",
            "Sensory/Response": "sensory_response.md",
        }
        for k, v in skill_map.items():
            if k.lower() in category.lower():
                sp = APP_DIR / "skills" / v
                if sp.exists():
                    category_skill = _read_file(sp, max_chars=5000)
                break
    log(f"[Context] Category: {category or '(unknown)'}")

    # 11. V2: BIDS sidecar reading from raw data directory (evidence ①)
    bids_sidecars: Dict[str, Any] = {}
    format_type = "unknown"
    eeg_header_summary = ""

    if data_dir:
        data_path = Path(data_dir)
        if data_path.is_dir():
            format_type = _detect_format(data_path)
            log(f"[Context] Format type: {format_type}")
            bids_sidecars = _read_bids_sidecars(data_path, log)
            eeg_header_summary = _sample_eeg_headers(data_path, log)
        else:
            log(f"[Context] data_dir not found: {data_dir}")
    else:
        log("[Context] No data_dir provided — skipping BIDS sidecar reading")

    return {
        "dataset_name": dataset_name,
        "ds_dir": str(ds_dir),
        "analysis_md": analysis_md,
        "analysis_urls": analysis_urls,
        "ds_tree": ds_tree,
        "ref_files": ref_files,
        "existing_kernel": existing_kernel,
        "existing_kernel_path": str(kernel_path) if kernel_path else "",
        "rulebook": rulebook,
        "skill_texts": skill_texts,
        "example_kernels": example_kernels,
        "app_rulebook": app_rulebook,
        "category": category,
        "category_skill": category_skill,
        # V2 additions
        "data_dir": data_dir,
        "format_type": format_type,
        "bids_sidecars": bids_sidecars,
        "eeg_header_summary": eeg_header_summary,
    }
