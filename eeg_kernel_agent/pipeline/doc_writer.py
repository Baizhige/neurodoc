"""Phase 7: Generate complete analysis.md and merge scan results."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

BIDS_ROOT = Path(__file__).parent.parent.parent
AGENT_DIR = Path(__file__).parent.parent


def _ensure_scan_engine():
    if str(AGENT_DIR) not in sys.path:
        sys.path.insert(0, str(AGENT_DIR))
    import scan_engine
    return scan_engine


_ANALYSIS_SYSTEM = """\
You are an EEG dataset documentation expert. Write a complete analysis.md file for the given dataset.

The file must have exactly this structure (fill in all sections):

```
# <Dataset Full Name>

**Dataset**: `<dataset_name>` | **Year**: <year> | **URL**: <url>
**Category**: <category> | **Subjects**: <n> | **Files (Completed)**: <n> | **Channels**: <n> | **Sampling Rate**: <hz> Hz
**Manual Review**: Pending

## Paradigm

<2-4 sentences describing the experimental paradigm, subjects, tasks, equipment>

## File Scan Result

> **Kernel SHA256**: `<sha>`
> **EEGUnity Version**: `<ver>`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
<rows — Type is "event"|"admin", Meta Level is "raw"|"super", Meaning is a short description>

### MISC Label Summary

<only include this section if there are misc channels, otherwise omit>
- **Route**: `misc`
- **Role**: <describe role>
- **Candidate Labels**: <comma-separated channel names>
- **Kernel Note**: <any notes>

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | <complete|partial|missing> | N/A |
| `subject_sex` | <complete|partial|missing> | N/A |
| `device` | <complete|partial|missing> | N/A |

## Tasks

<paste the tasks_section here>
```

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
) -> str:
    """Generate the full analysis.md using LLM."""
    from .ref_analyzer import _parse_json

    log("[DocWriter] Generating complete analysis.md...")

    event_counts = scan_result.get("event_counts", {})
    subject_info = scan_result.get("subject_info", {})
    misc_channels = scan_result.get("misc_channel_names", [])
    kernel_sha = scan_result.get("kernel_sha256", "N/A")
    eegu_ver = scan_result.get("eegunity_version", "N/A")
    total_n = scan_result.get("total_n", 0)

    event_table_str = "\n".join(
        f"| `{eid}` | {cnt} | event | raw |  |"
        for eid, cnt in sorted(event_counts.items())
    )

    misc_section = ""
    if misc_channels:
        labels_str = ", ".join(f"`{c}`" for c in misc_channels)
        misc_section = (
            f"\n### MISC Label Summary\n\n"
            f"- **Route**: `misc`\n"
            f"- **Role**: Stores continuous or derived channel labels.\n"
            f"- **Candidate Labels**: {labels_str}\n"
            f"- **Kernel Note**: Verify channel roles and units.\n"
        )

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

    # Override age/sex from BIDS participants.tsv if available (Evidence Level ①)
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

    # Build participants block for prompt (BIDS sidecar takes priority)
    participants_block = ""
    if bids_sidecars and bids_sidecars.get("participants_summary"):
        participants_block = (
            f"=== Participants (from participants.tsv — authoritative) ===\n"
            f"{bids_sidecars['participants_summary']}\n\n"
        )

    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Existing analysis.md draft (reference only, may have errors) ===\n"
        f"{context['analysis_md'][:4000]}\n\n"
        f"=== Kernel SHA256 ===\n{kernel_sha}\n\n"
        f"=== EEGUnity Version ===\n{eegu_ver}\n\n"
        f"=== Total files scanned ===\n{total_n}\n\n"
        + participants_block
        + f"=== Event counts from actual scan ===\n{json.dumps(event_counts, indent=2)}\n\n"
        f"=== Subject info completeness ===\n"
        f"age: {age_comp}, sex: {sex_comp}, device: {dev_comp}\n\n"
        f"=== Misc channel names ===\n{', '.join(misc_channels) or '(none)'}\n\n"
        f"=== Event table (fill Meaning column) ===\n"
        f"| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
        f"|---|---|---|---|---|\n"
        f"{event_table_str}\n\n"
        f"=== Tasks section (use exactly as-is) ===\n{tasks_section}\n\n"
        f"=== Misc section to include (if not empty) ===\n{misc_section}\n\n"
        f"Now write the complete analysis.md. "
        f"Use the existing draft only as a reference for metadata (year, URL, category, subjects, etc). "
        f"The event counts and scan results above are authoritative."
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
            tasks_section, misc_section, kernel_sha, eegu_ver,
            age_comp, sex_comp, dev_comp,
        )

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

    out_path = BIDS_ROOT / dataset_name / "analysis.md"
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
    engine = _ensure_scan_engine()

    if existing_md.strip():
        content = existing_md
    else:
        content = f"# {dataset_name}\n\n**Status**: failed\n\n## Paradigm\n\n(Pending)\n\n## File Scan Result\n\n> **Kernel SHA256**: `N/A`\n> **EEGUnity Version**: `N/A`\n> **Scan Type**: N/A\n\n### Event Structure\n\n| Event ID | Count (total) | Type | Meta Level | Meaning |\n|---|---|---|---|---|\n\n### Info\n\n| Field | Completeness | Notes |\n|---|---|---|\n| `subject_age` | missing | N/A |\n| `subject_sex` | missing | N/A |\n| `device` | missing | N/A |\n\n## Tasks\n\n(No tasks synthesized)\n"

    # Update status to failed
    content = re.sub(
        r"(\*\*Status\*\*:\s*)\S+",
        r"\1failed",
        content,
    )
    # Append failure note
    content = content.rstrip() + f"\n\n---\n\n> **auto_eeg FAILED**: {reason}\n"

    out_path = BIDS_ROOT / dataset_name / "analysis.md"
    out_path.write_text(content, encoding="utf-8")
    log(f"[DocWriter] FAILED analysis.md written: {out_path}")


def _fallback_analysis_md(
    dataset_name, existing_md, scan_result, tasks_section,
    misc_section, kernel_sha, eegu_ver, age_comp, sex_comp, dev_comp,
) -> str:
    """Simple string-based fallback when LLM fails to produce doc."""
    event_counts = scan_result.get("event_counts", {})
    event_rows = "\n".join(
        f"| `{eid}` | {cnt} | event | raw |  |"
        for eid, cnt in sorted(event_counts.items())
    )
    # Extract header from existing if possible
    header_match = re.match(r"(#[^\n]+\n[^\n]*\n)", existing_md)
    header = header_match.group(1) if header_match else f"# {dataset_name}\n\n"

    return (
        f"{header}\n"
        f"## Paradigm\n\n(See existing draft)\n\n"
        f"## File Scan Result\n\n"
        f"> **Kernel SHA256**: `{kernel_sha}`\n"
        f"> **EEGUnity Version**: `{eegu_ver}`\n"
        f"> **Scan Type**: Full\n\n"
        f"### Event Structure\n\n"
        f"| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
        f"|---|---|---|---|---|\n"
        f"{event_rows}\n"
        f"{misc_section}\n"
        f"### Info\n\n"
        f"| Field | Completeness | Notes |\n"
        f"|---|---|---|\n"
        f"| `subject_age` | {age_comp} | N/A |\n"
        f"| `subject_sex` | {sex_comp} | N/A |\n"
        f"| `device` | {dev_comp} | N/A |\n\n"
        f"{tasks_section}\n"
    )
