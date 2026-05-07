"""sleepdata_shhs stage1 kernel for EEGUnity.

Sleep Heart Health Study (SHHS): NIH/NHLBI multi-center cohort PSG dataset.
Dual referential EEG (EEG1=C4-A1, EEG2=C3-A2) plus EOG/EMG/ECG/respiratory/SpO2.

Layout:
- EDFs at polysomnography/edfs/{shhs1,shhs2}/shhs{1,2}-NNNNNN.edf (sfreq 125 Hz)
- NSRR XML annotations at
  polysomnography/annotations-events-nsrr/{shhs1,shhs2}/shhs{1,2}-NNNNNN-nsrr.xml
  (NOT siblings of the EDFs)
- Demographics in datasets/shhs{1,2}-dataset-0.21.0.csv keyed by `nsrrid`
"""

from __future__ import annotations

import csv
import json
import os
import re
import threading
import warnings
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

import mne

KERNEL_ID = "sleepdata-shhs-stage1"


# ---------------------------------------------------------------------------
# Channel rename: EEG → C4, EEG(sec) → C3
# Annotator: LLM (Claude), 2026-04-30 — needs human review (Q1 b1)
# Direct evidence: SHHS1_Manual_of_Operations.pdf p.261 — "EEG1 should link
# C4 and A1; EEG2 should link C3 and A2."
# Inference (NSRR community convention, NOT in local docs): EDF label "EEG"
# is the primary channel (EEG1=C4-A1) and "EEG(sec)" is the secondary
# (EEG2=C3-A2). The "(sec)" suffix literally denotes "secondary".
# ---------------------------------------------------------------------------

_CHANNEL_RENAME: Dict[str, str] = {
    "EEG": "C4",
    "EEG(sec)": "C3",
}

# Channel type assignments. Keys use post-rename names where applicable.
# Channels not listed are left at their default type (usually "misc"
# already from MNE's EDF reader, but we set them explicitly for clarity).
_CHANNEL_TYPE_MAP: Dict[str, str] = {
    "C3": "eeg",
    "C4": "eeg",
    "EOG(L)": "eog",
    "EOG(R)": "eog",
    "EMG": "emg",
    "ECG": "ecg",
}
# Names observed across SHHS-1 and SHHS-2 EDFs that should be "misc":
# - "H.R." (SHHS-1) / "PR" (SHHS-2) — heart-rate / pulse-rate channel
# - "NEW AIR" (SHHS-1) / "AIRFLOW" (SHHS-2)
# - "OX stat" / "OX STAT" — oximeter status flag (case differs across visits)
_MISC_NAMES = frozenset({
    "SaO2", "H.R.", "PR",
    "THOR RES", "ABDO RES",
    "POSITION", "LIGHT",
    "NEW AIR", "AIRFLOW",
    "OX stat", "OX STAT",
})


# ---------------------------------------------------------------------------
# Demographic CSV lookup — SHHS NSRR release 0.21.0 (Q5b: hardcoded version)
# Bump _CSV_VERSION when the dataset advances.
# Per data dictionary domain `gender12`: 1=Male, 2=Female.
# ---------------------------------------------------------------------------

_CSV_VERSION = "0.21.0"
_CSV_REL_PATH: Dict[str, str] = {
    "shhs1": f"datasets/shhs1-dataset-{_CSV_VERSION}.csv",
    "shhs2": f"datasets/shhs2-dataset-{_CSV_VERSION}.csv",
}
_GENDER_MAP: Dict[str, str] = {"1": "male", "2": "female"}

_DEMO_CACHE: Dict[str, Dict[int, Dict[str, str]]] = {}
_DEMO_LOCK = threading.Lock()


def _load_demographics(dataset_root: str, visit: str) -> Dict[int, Dict[str, str]]:
    """Lazy-load and cache the per-visit demographic table keyed by nsrrid.

    Reads only the columns we actually surface so the in-memory footprint
    stays around a few hundred KB even though the source CSV has ~1271 cols.
    """
    cache_key = f"{dataset_root}|{visit}"
    cached = _DEMO_CACHE.get(cache_key)
    if cached is not None:
        return cached
    with _DEMO_LOCK:
        cached = _DEMO_CACHE.get(cache_key)
        if cached is not None:
            return cached
        rel = _CSV_REL_PATH.get(visit)
        if rel is None:
            _DEMO_CACHE[cache_key] = {}
            return {}
        csv_path = os.path.join(dataset_root, rel)
        if not os.path.isfile(csv_path):
            warnings.warn(f"[sleepdata_shhs] demographics CSV not found: {csv_path}")
            _DEMO_CACHE[cache_key] = {}
            return {}

        age_col = "age_s1" if visit == "shhs1" else "age_s2"
        bmi_col = "bmi_s1" if visit == "shhs1" else "bmi_s2"
        wanted = ["nsrrid", "gender", "race", age_col, bmi_col, "weight", "height"]

        table: Dict[int, Dict[str, str]] = {}
        with open(csv_path, "r", newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh)
            header = next(reader)
            idx = {c: header.index(c) for c in wanted if c in header}
            nsrrid_i = idx.get("nsrrid")
            if nsrrid_i is None:
                _DEMO_CACHE[cache_key] = {}
                return {}
            for row in reader:
                try:
                    nsrrid = int(float(row[nsrrid_i]))
                except (ValueError, IndexError):
                    continue
                entry: Dict[str, str] = {}
                age_v = _norm_int(row, idx.get(age_col))
                if age_v:
                    entry["age"] = age_v
                gender_v = _norm_int(row, idx.get("gender"))
                if gender_v in _GENDER_MAP:
                    entry["sex"] = _GENDER_MAP[gender_v]
                for src, dst in (("race", "race"), (bmi_col, "bmi"),
                                 ("weight", "weight"), ("height", "height")):
                    v = _norm_str(row, idx.get(src))
                    if v:
                        entry[dst] = v
                table[nsrrid] = entry
        _DEMO_CACHE[cache_key] = table
        return table


def _norm_str(row: List[str], i: Optional[int]) -> str:
    if i is None or i >= len(row):
        return ""
    return (row[i] or "").strip()


def _norm_int(row: List[str], i: Optional[int]) -> str:
    """Normalize numeric CSV cells: '55' or '55.0' → '55'; blank → ''."""
    s = _norm_str(row, i)
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except ValueError:
        return s


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

_EDF_NAME_RE = re.compile(r"^(shhs[12])-(\d+)$")


def _parse_edf_id(edf_path: str) -> Tuple[Optional[str], Optional[int]]:
    stem = os.path.splitext(os.path.basename(edf_path))[0]
    m = _EDF_NAME_RE.match(stem)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def _find_dataset_root(edf_path: str) -> Optional[str]:
    """Walk upward from the EDF until we find an SHHS root that contains
    both `polysomnography/` and `datasets/` siblings."""
    cur = os.path.dirname(os.path.abspath(edf_path))
    for _ in range(8):
        if (os.path.isdir(os.path.join(cur, "polysomnography"))
                and os.path.isdir(os.path.join(cur, "datasets"))):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


def _xml_path_for(dataset_root: str, visit: str, nsrrid: int) -> Optional[str]:
    p = os.path.join(
        dataset_root, "polysomnography", "annotations-events-nsrr", visit,
        f"{visit}-{nsrrid}-nsrr.xml",
    )
    return p if os.path.isfile(p) else None


# ---------------------------------------------------------------------------
# NSRR XML parsing — Q2(a): pass-through EventConcept verbatim;
# Q3: emit ALL ScoredEvent (Stages, Arousals, Respiratory, etc.).
# ---------------------------------------------------------------------------

def _parse_nsrr_xml(xml_path: str) -> List[Tuple[float, float, str]]:
    out: List[Tuple[float, float, str]] = []
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        warnings.warn(f"[sleepdata_shhs] NSRR XML parse failed: {xml_path}: {e}")
        return out
    for ev in tree.getroot().findall(".//ScoredEvent"):
        concept_el = ev.find("EventConcept")
        if concept_el is None:
            continue
        description = (concept_el.text or "").strip()
        if not description:
            continue
        start_el = ev.find("Start")
        dur_el = ev.find("Duration")
        try:
            onset = float((start_el.text if start_el is not None else "0") or 0)
            duration = float((dur_el.text if dur_el is not None else "0") or 0)
        except (AttributeError, ValueError, TypeError):
            continue
        out.append((onset, duration, description))
    return out


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------

class SleepdataShhsKernel:
    """SHHS stage-1 kernel (see module docstring for layout)."""

    KERNEL_ID = KERNEL_ID

    def apply(self, udataset, raw, row):
        edf_path = ""
        if hasattr(row, "get"):
            edf_path = row.get("File Path", "") or row.get("filepath", "") or ""
        if not edf_path:
            edf_path = str(getattr(row, "File Path", "") or getattr(row, "filepath", "") or "")

        visit, nsrrid = _parse_edf_id(edf_path)
        dataset_root = _find_dataset_root(edf_path)

        # 1. Channel rename (EEG → C4, EEG(sec) → C3).
        rename = {ch: _CHANNEL_RENAME[ch]
                  for ch in raw.ch_names if ch in _CHANNEL_RENAME}
        if rename:
            raw.rename_channels(rename)

        # 2. Channel types — set without synthesizing new misc channels (Q4).
        new_types: Dict[str, str] = {}
        for ch in raw.ch_names:
            if ch in _CHANNEL_TYPE_MAP:
                new_types[ch] = _CHANNEL_TYPE_MAP[ch]
            elif ch in _MISC_NAMES:
                new_types[ch] = "misc"
        if new_types:
            raw.set_channel_types(new_types)

        # 3. Annotations from the per-file NSRR XML (verbatim EventConcept,
        #    all ScoredEvent types — Q2(a) + Q3).
        if visit and nsrrid is not None and dataset_root:
            xml_path = _xml_path_for(dataset_root, visit, nsrrid)
            if xml_path:
                events = _parse_nsrr_xml(xml_path)
                if events:
                    annot = mne.Annotations(
                        onset=[e[0] for e in events],
                        duration=[e[1] for e in events],
                        description=[e[2] for e in events],
                    )
                    raw.set_annotations(annot)

        # 4. eegunity_description with required fields + extras (Q5c).
        # Annotator: LLM (Claude), 2026-04-30 — needs human review.
        # `amplifier` from SHHS1 Manual of Operations p.99 ("Compumedics").
        # `cap`: SHHS used a minimal discrete-electrode PSG montage (no cap).
        # `handedness`: SHHS questionnaire does not collect handedness.
        eegunity_description: Dict[str, str] = {
            "age": "",
            "sex": "",
            "amplifier": "Compumedics",
            "cap": "minimal PSG montage (C3/C4, A1/A2 referential)",
            "handedness": "",
        }
        if visit and nsrrid is not None and dataset_root:
            entry = _load_demographics(dataset_root, visit).get(nsrrid, {})
            eegunity_description.update(entry)

        original_description = raw.info.get("description") or ""
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = SleepdataShhsKernel()
