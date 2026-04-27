"""Phase 7: Generate complete analysis.md and merge scan results."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from ..paths import DATASET_DOCUMENT_DIR, NEURODOC_DIR
except ImportError:
    from paths import DATASET_DOCUMENT_DIR, NEURODOC_DIR


def _ensure_scan_engine():
    if str(NEURODOC_DIR) not in sys.path:
        sys.path.insert(0, str(NEURODOC_DIR))
    import scan_engine
    return scan_engine


_ANALYSIS_SYSTEM = """\
You are an EEG dataset documentation expert. Write a complete analysis.md file for the given dataset.

The file must have exactly this structure (5 top-level ## sections, in this exact order):

```
# <Dataset Full Name>

**Dataset**: `<dataset_name>` | **Year**: <year> | **URL**: <url>
**Category**: <category> | **Subjects**: <n> | **Files (Completed)**: <n> | **Channels**: <n> | **Sampling Rate**: <hz> Hz
**Manual Review**:

## Paradigm

<2-4 sentences describing the experimental paradigm, subjects, tasks, equipment>

## File Scan Result

<INSERT the File Scan Result block provided below AS-IS. Do NOT modify.>

## Tasks

<INSERT the tasks_section provided below AS-IS. Do NOT modify.>

## Data Quality Notes

<Bullet points using "- " prefix. Note data quality issues, conflicts, or limitations.
If no issues are known, write exactly: "- No known data quality issues.">

## Kernel Responsibilities

<INSERT the Kernel Responsibilities block provided below AS-IS. Do NOT modify.>
```

RULES:
1. The ## File Scan Result, ## Tasks, and ## Kernel Responsibilities blocks are provided
   pre-built. Copy each exactly — do NOT alter any content in these sections.
2. You write ONLY: the # heading + meta area, ## Paradigm, ## Data Quality Notes.
3. ## Data Quality Notes must use "- " bullet format for every line of content.
4. Do NOT add any extra ## sections beyond these 5.
5. Do NOT invent event IDs, counts, or meanings not present in the provided data.

Output ONLY valid JSON:
{
  "analysis_md": "<complete markdown content as a single string, \\n for newlines>",
  "reasoning": "<1-2 sentences>"
}"""


def _parse_participants_summary(summary: str):
    """Parse participants_summary string into (age_comp, sex_comp).

    Returns (None, None) if parsing fails or info not available.
    E.g. "N=136, age=5.2–21.7, sex={'F': 46, 'M': 90}" -> ("complete", "complete")
    """
    if not summary:
        return None, None
    age_comp = sex_comp = None

    # Extract N
    n_match = re.search(r"N=(\d+)", summary)
    n_total = int(n_match.group(1)) if n_match else 0

    # Extract age range — if present, assume complete
    if re.search(r"age=", summary):
        age_comp = "complete"

    # Extract sex counts
    sex_match = re.search(r"sex=\{([^}]+)\}", summary)
    if sex_match and n_total:
        try:
            sex_dict = {}
            for pair in re.findall(r"'(\w+)':\s*(\d+)", sex_match.group(1)):
                sex_dict[pair[0]] = int(pair[1])
            sex_total = sum(sex_dict.values())
            if sex_total == 0:
                sex_comp = "missing"
            elif sex_total >= n_total * 0.99:
                sex_comp = "complete"
            else:
                sex_comp = f"partial ({sex_total}/{n_total})"
        except Exception:
            pass
    elif re.search(r"sex=", summary) and n_total:
        sex_comp = "complete"  # counts listed but no dict match

    return age_comp, sex_comp


def _build_event_table(event_counts: Dict, event_annotations: Optional[Dict]) -> str:
    """Build the Event Structure table rows.

    Data fields (Event ID, Count) come from scan. Semantic fields (Type, Meta Level,
    Meaning) come from locked event_annotations when available.
    """
    ann_map: Dict[str, Dict] = {}
    if event_annotations:
        for ann in event_annotations.get("annotations", []):
            ann_map[str(ann.get("event_id", ""))] = ann

    rows = []
    for eid, cnt in sorted(event_counts.items()):
        eid_str = str(eid)
        if eid_str in ann_map:
            a = ann_map[eid_str]
            etype = a.get("event_type", "event")
            meta = a.get("meta_level", "raw")
            meaning = a.get("meaning", "")
        else:
            etype, meta, meaning = "event", "raw", ""
        rows.append(f"| `{eid}` | {cnt} | {etype} | {meta} | {meaning} |")
    return "\n".join(rows)


def _build_file_scan_result_block(
    scan_result: Dict[str, Any],
    event_annotations: Optional[Dict],
    misc_channels: list,
    age_comp: str, sex_comp: str, dev_comp: str,
    participants_fields: Optional[list] = None,
    derived_misc_fields: Optional[list] = None,
) -> str:
    """Build the complete ## File Scan Result block programmatically."""
    kernel_sha = scan_result.get("kernel_sha256", "N/A")
    eegu_ver = scan_result.get("eegunity_version", "N/A")
    event_counts = scan_result.get("event_counts", {})

    event_table = _build_event_table(event_counts, event_annotations)

    parts = [
        "## File Scan Result\n",
        f"> **Kernel SHA256**: `{kernel_sha}`",
        f"> **EEGUnity Version**: `{eegu_ver}`",
        "> **Scan Type**: Full\n",
        "### Event Structure\n",
        "| Event ID | Count (total) | Type | Meta Level | Meaning |",
        "|---|---|---|---|---|",
        event_table,
    ]

    # v3: MISC Label Summary as a four-column table (Channel | Source | Meta | Notes)
    misc_rows = []
    for c in (misc_channels or []):
        misc_rows.append(f"| `{c}` | native (raw misc in EEG file) | raw | Verify channel role and unit |")
    for d in (derived_misc_fields or []):
        # d = {"field", "source", "notes"}
        misc_rows.append(
            f"| `{d['field']}` | {d.get('source', 'derived')} | super | {d.get('notes', '')} |"
        )
    if misc_rows:
        parts += [
            "",
            "### MISC Label Summary\n",
            "| Channel | Source | Meta | Notes |",
            "|---|---|---|---|",
            *misc_rows,
        ]

    # v3: Info subsection — canonical fields + all discovered participants.tsv columns
    CANONICAL = ("subject_age", "subject_sex", "device")
    info_rows = [
        f"| `subject_age` | {age_comp} | N/A |",
        f"| `subject_sex` | {sex_comp} | N/A |",
        f"| `device` | {dev_comp} | N/A |",
    ]
    if participants_fields:
        # Append any column not in canonical, mapping age/sex aliases into canonical rows
        for f in participants_fields:
            name = f.get("name", "")
            if name in CANONICAL or name in ("age", "sex", "gender"):
                continue
            comp = f.get("completeness", "missing")
            dtype = f.get("dtype", "")
            samples = f.get("sample_values", [])
            notes_parts = []
            if dtype:
                notes_parts.append(dtype)
            if samples:
                samples_display = ", ".join(str(s) for s in samples[:3])
                notes_parts.append(f"e.g. {samples_display}")
            notes = "; ".join(notes_parts) if notes_parts else "N/A"
            info_rows.append(f"| `{name}` | {comp} | {notes} |")

    parts += [
        "",
        "### Info\n",
        "| Field | Completeness | Notes |",
        "|---|---|---|",
        *info_rows,
    ]

    return "\n".join(parts)


def _build_kr_block(super_meta_required: str, status: str) -> str:
    """Build the ## Kernel Responsibilities blockquote section programmatically."""
    return (
        "## Kernel Responsibilities\n\n"
        f"> **Super Meta Required**: {super_meta_required}\n"
        f"> **Status**: {status}"
    )


def _enforce_manual_review_blank(analysis_md: str) -> str:
    """Force the Manual Review field to be blank (rulebook 第30条之三).

    LLM often copies `**Manual Review**: Pending` from an existing draft even when the
    template says leave it blank. This regex replaces any value (including blank) with
    a canonical blank form, preserving the trailing newline.
    """
    return re.sub(
        r"\*\*Manual Review\*\*:[^\n]*",
        "**Manual Review**:",
        analysis_md,
    )


def _extract_derived_misc_fields(tasks_section: str) -> list:
    """Scan Tasks for Route=misc + Meta Level=super → derived misc fields.

    Returns a list of dicts: {field, source, notes} to seed MISC Label Summary.
    """
    derived = []
    blocks = re.split(r"(?=###\s+(?:Classical|Potential)\s+Task\s+\d+:)", tasks_section)
    for block in blocks:
        if not block.strip().startswith("###"):
            continue
        route_m = re.search(r"\*\*Label Route\*\*:\s*`?(\w+)`?", block)
        meta_m = re.search(r"\*\*Meta Level\*\*:\s*`?(\w+)`?", block)
        field_m = re.search(r"\*\*Label Field\*\*:\s*`?([^`\n]+?)`?\s*$", block, re.MULTILINE)
        if not (route_m and meta_m and field_m):
            continue
        if route_m.group(1).lower() == "misc" and meta_m.group(1).lower() == "super":
            derived.append({
                "field": field_m.group(1).strip(),
                "source": "derived (per Task Notes)",
                "notes": "Super Meta — kernel derives per-segmentation value",
            })
    # dedupe by field
    seen = set()
    out = []
    for d in derived:
        if d["field"] not in seen:
            seen.add(d["field"])
            out.append(d)
    return out


def _enforce_kr_block(analysis_md: str, kr_block: str) -> str:
    """Replace the ## Kernel Responsibilities section with the pre-built block."""
    m = re.search(r"^## Kernel Responsibilities\s*$", analysis_md, re.MULTILINE)
    if not m:
        return analysis_md.rstrip() + "\n\n" + kr_block + "\n"
    start = m.start()
    next_section = re.search(r"^## ", analysis_md[m.end():], re.MULTILINE)
    if next_section:
        end = m.end() + next_section.start()
    else:
        end = len(analysis_md)
    return analysis_md[:start] + kr_block + "\n" + analysis_md[end:]


def _detect_super_meta(tasks_section: str) -> str:
    """Return 'Yes' if any task has Meta Level = super, else 'No'."""
    # Bullet format: "- **Meta Level**: super"
    if re.search(r"\*\*Meta Level\*\*:\s*super\b", tasks_section, re.IGNORECASE):
        return "Yes"
    # Table format fallback: "| Meta Level | super |"
    if re.search(r"\|\s*Meta Level\s*\|\s*super\s*\|", tasks_section, re.IGNORECASE):
        return "Yes"
    return "No"


def generate_analysis_md(
    dataset_name: str,
    context: Dict[str, Any],
    scan_result: Dict[str, Any],
    tasks_section: str,
    kernel_path: str,
    call_llm,
    budget,
    log,
    bids_sidecars: Optional[Dict] = None,
    event_annotations: Optional[Dict] = None,
    status: str = "wait_manual_review",
) -> str:
    """Generate the full analysis.md using LLM."""
    from .ref_analyzer import _parse_json

    log("[DocWriter] Generating complete analysis.md...")

    subject_info = scan_result.get("subject_info", {})
    misc_channels = scan_result.get("misc_channel_names", [])
    total_n = scan_result.get("total_n", 0)

    def _comp(ok, total):
        if total == 0:
            return "missing"
        pct = ok / total
        if pct >= 0.99:
            return "complete"
        if pct > 0:
            return f"partial ({ok}/{total})"
        return "missing"

    n = subject_info.get("record_count", total_n) or total_n
    age_comp = _comp(subject_info.get("age_complete", 0), n)
    sex_comp = _comp(subject_info.get("sex_complete", 0), n)
    dev_comp = _comp(subject_info.get("device_complete", 0), n)

    participants_fields = None
    if bids_sidecars:
        bids_age, bids_sex = _parse_participants_summary(
            bids_sidecars.get("participants_summary", "")
        )
        if bids_age is not None:
            log(f"[DocWriter] age_comp overridden by participants.tsv: {bids_age}")
            age_comp = bids_age
        if bids_sex is not None:
            log(f"[DocWriter] sex_comp overridden by participants.tsv: {bids_sex}")
            sex_comp = bids_sex
        participants_fields = bids_sidecars.get("participants_fields") or None

    derived_misc_fields = _extract_derived_misc_fields(tasks_section)
    if derived_misc_fields:
        log(f"[DocWriter] Derived misc fields detected: {[d['field'] for d in derived_misc_fields]}")

    file_scan_block = _build_file_scan_result_block(
        scan_result, event_annotations, misc_channels,
        age_comp, sex_comp, dev_comp,
        participants_fields=participants_fields,
        derived_misc_fields=derived_misc_fields,
    )

    super_meta = _detect_super_meta(tasks_section)
    kr_block = _build_kr_block(super_meta, status)
    log(f"[DocWriter] KR block: Super Meta Required={super_meta}, Status={status}")

    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Existing analysis.md draft (reference for metadata only) ===\n"
        f"{context['analysis_md'][:4000]}\n\n"
        f"=== File Scan Result block (COPY AS-IS into ## File Scan Result) ===\n"
        f"{file_scan_block}\n\n"
        f"=== Tasks section (COPY AS-IS into ## Tasks) ===\n{tasks_section}\n\n"
        f"=== Kernel Responsibilities block (COPY AS-IS into ## Kernel Responsibilities) ===\n"
        f"{kr_block}\n\n"
        f"Now write the complete analysis.md.\n"
        f"Use the existing draft only as a reference for metadata (year, URL, category, subjects, etc).\n"
        f"The File Scan Result, Tasks, and Kernel Responsibilities blocks above are authoritative — copy them unchanged."
    )

    budget.charge("doc_write")
    raw = call_llm([
        {"role": "system", "content": _ANALYSIS_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    analysis_md = result.get("analysis_md", "")

    if not analysis_md:
        log("[DocWriter] WARNING: LLM returned empty analysis_md, using template fallback.")
        analysis_md = _fallback_analysis_md(
            dataset_name, context["analysis_md"], scan_result,
            tasks_section, file_scan_block, kr_block,
        )

    analysis_md = _enforce_kr_block(analysis_md, kr_block)
    before_mr = analysis_md
    analysis_md = _enforce_manual_review_blank(analysis_md)
    if analysis_md != before_mr:
        log("[DocWriter] Manual Review field was non-blank; forced to blank per 第30条之三.")

    log(f"[DocWriter] analysis.md: {len(analysis_md)} chars")
    return analysis_md


def merge_and_write(
    dataset_name: str,
    analysis_md_new: str,
    scan_result: Dict[str, Any],
    log,
    bids_sidecars: Optional[Dict] = None,
) -> str:
    """
    Apply the scan result merge (event table + info table updates) on top of the
    LLM-generated analysis.md, then write to disk.
    """
    engine = _ensure_scan_engine()

    # Patch subject_info with BIDS participants.tsv data if available (Evidence Level ①)
    # scan_engine.merge_scan_results overwrites the Info table from subject_info,
    # so we must inject the BIDS-derived completeness here before calling it.
    if bids_sidecars:
        bids_age, bids_sex = _parse_participants_summary(
            bids_sidecars.get("participants_summary", "")
        )
        if bids_age is not None or bids_sex is not None:
            scan_result = dict(scan_result)  # shallow copy — don't mutate caller's dict
            subject_info = dict(scan_result.get("subject_info", {}))
            n = subject_info.get("record_count", scan_result.get("total_n", 0)) or 1
            if bids_age == "complete":
                subject_info["age_complete"] = n
            if bids_sex == "complete":
                subject_info["sex_complete"] = n
            elif bids_sex and bids_sex.startswith("partial"):
                # extract numerator from "partial (X/N)"
                import re as _re
                m = _re.search(r"partial \((\d+)/", bids_sex)
                if m:
                    subject_info["sex_complete"] = int(m.group(1))
            scan_result["subject_info"] = subject_info
            log(f"[DocWriter] Patched subject_info from participants.tsv: age={bids_age}, sex={bids_sex}")

    # The LLM-generated doc is the new authoritative content.
    # Run merge_scan_results to apply final fingerprint + table updates.
    final_content, diffs = engine.merge_scan_results(analysis_md_new, scan_result)

    out_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    out_path.write_text(final_content, encoding="utf-8")
    log(f"[DocWriter] Written: {out_path} ({len(final_content)} chars, {len(diffs)} diff sections)")
    return final_content


def write_failed_analysis(
    dataset_name: str,
    existing_md: str,
    reason: str,
    log,
) -> None:
    """Write a FAILED-status analysis.md preserving existing content."""

    if existing_md.strip():
        content = existing_md
    else:
        kr_block = _build_kr_block("No", "wait_kernel_update")
        content = (
            f"# {dataset_name}\n\n"
            f"**Manual Review**:\n\n"
            f"## Paradigm\n\n(Pending)\n\n"
            f"## File Scan Result\n\n"
            f"> **Kernel SHA256**: `N/A`\n"
            f"> **EEGUnity Version**: `N/A`\n"
            f"> **Scan Type**: N/A\n\n"
            f"### Event Structure\n\n"
            f"| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
            f"|---|---|---|---|---|\n\n"
            f"### Info\n\n"
            f"| Field | Completeness | Notes |\n"
            f"|---|---|---|\n"
            f"| `subject_age` | missing | N/A |\n"
            f"| `subject_sex` | missing | N/A |\n"
            f"| `device` | missing | N/A |\n\n"
            f"## Tasks\n\n(No tasks synthesized)\n\n"
            f"## Data Quality Notes\n\n- Pipeline failed — no quality assessment available.\n\n"
            f"{kr_block}\n"
        )

    content = content.rstrip() + f"\n\n---\n\n> **Pipeline FAILED**: {reason}\n"

    out_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    out_path.write_text(content, encoding="utf-8")
    log(f"[DocWriter] FAILED analysis.md written: {out_path}")


def _fallback_analysis_md(
    dataset_name, existing_md, scan_result, tasks_section,
    file_scan_block, kr_block,
) -> str:
    """Simple string-based fallback when LLM fails to produce doc."""
    header_match = re.match(r"(#[^\n]+\n[^\n]*\n)", existing_md)
    header = header_match.group(1) if header_match else f"# {dataset_name}\n\n"

    return (
        f"{header}\n"
        f"## Paradigm\n\n(See existing draft)\n\n"
        f"{file_scan_block}\n\n"
        f"{tasks_section}\n\n"
        f"## Data Quality Notes\n\n- No quality assessment available (LLM fallback).\n\n"
        f"{kr_block}\n"
    )
