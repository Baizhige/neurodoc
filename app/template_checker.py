"""Shared structural template checker for dataset analysis.md files."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from app import template_spec


_TOP_LEVEL_RE = re.compile(r"(?m)^##\s+([^\n#][^\n]*)\s*$")
_THIRD_LEVEL_RE = re.compile(r"(?m)^###\s+([^\n#][^\n]*)\s*$")
_FILE_SCAN_BLOCK_RE = re.compile(
    r"(?ms)^##\s+File Scan Result\s*$\n?(.*?)(?=^##\s+|\Z)"
)


def _normalize_heading(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).strip())


def _find_headings(pattern: re.Pattern[str], content: str) -> List[Tuple[str, int]]:
    return [(_normalize_heading(match.group(1)), match.start()) for match in pattern.finditer(content)]


def _order_error(present: List[str], expected_order: List[str]) -> bool:
    present_known = [name for name in present if name in expected_order]
    expected_known = [name for name in expected_order if name in present_known]
    return present_known != expected_known


def _format_errors(errors: List[str]) -> List[str]:
    seen = set()
    result = []
    for err in errors:
        if err not in seen:
            seen.add(err)
            result.append(err)
    return result


def check_analysis_template(content: str) -> Dict[str, object]:
    errors: List[str] = []
    content = str(content or "")

    top_headings = _find_headings(_TOP_LEVEL_RE, content)
    top_names = [name for name, _ in top_headings]
    top_counts = Counter(top_names)

    for name in template_spec.REQUIRED_TOP_LEVEL_SECTIONS:
        count = top_counts.get(name, 0)
        if count == 0:
            errors.append(f"Missing required section: {template_spec.top_level_heading(name)}")
        elif count > 1:
            errors.append(f"Duplicate section: {template_spec.top_level_heading(name)}")

    for name in template_spec.FORBIDDEN_TOP_LEVEL_SECTIONS:
        if top_counts.get(name, 0):
            errors.append(f"Forbidden/deprecated section: {template_spec.top_level_heading(name)}")

    for name in top_names:
        if (
            name not in template_spec.REQUIRED_TOP_LEVEL_SECTIONS
            and name not in template_spec.FORBIDDEN_TOP_LEVEL_SECTIONS
        ):
            errors.append(f"Unexpected section: {template_spec.top_level_heading(name)}")

    if _order_error(top_names, template_spec.REQUIRED_TOP_LEVEL_SECTIONS):
        errors.append(
            "Top-level sections are out of order. Expected: "
            f"{template_spec.format_top_level_order()}"
        )

    file_scan_match = _FILE_SCAN_BLOCK_RE.search(content)
    file_scan_headings: List[Tuple[str, int]] = []
    file_scan_names: List[str] = []
    if file_scan_match:
        file_scan_headings = _find_headings(_THIRD_LEVEL_RE, file_scan_match.group(1))
        file_scan_names = [name for name, _ in file_scan_headings]
        file_scan_counts = Counter(file_scan_names)

        for name in template_spec.FILE_SCAN_REQUIRED_SUBSECTIONS:
            count = file_scan_counts.get(name, 0)
            if count == 0:
                errors.append(
                    "Missing required subsection under ## File Scan Result: "
                    f"{template_spec.subsection_heading(name)}"
                )
            elif count > 1:
                errors.append(
                    "Duplicate subsection under ## File Scan Result: "
                    f"{template_spec.subsection_heading(name)}"
                )

        for name in file_scan_names:
            if name not in template_spec.ALLOWED_FILE_SCAN_SUBSECTIONS:
                errors.append(
                    "Unexpected subsection under ## File Scan Result: "
                    f"{template_spec.subsection_heading(name)}"
                )

        if _order_error(file_scan_names, template_spec.FILE_SCAN_SUBSECTION_ORDER):
            errors.append(
                "File Scan Result subsections are out of order. Expected: "
                f"{template_spec.format_file_scan_subsection_order()}"
            )

    global_third_level = _find_headings(_THIRD_LEVEL_RE, content)
    file_scan_span = None
    if file_scan_match:
        file_scan_span = (file_scan_match.start(1), file_scan_match.end(1))

    for required_name in template_spec.FILE_SCAN_REQUIRED_SUBSECTIONS:
        outside_file_scan = False
        for name, pos in global_third_level:
            if name != required_name:
                continue
            if not file_scan_span or not (file_scan_span[0] <= pos < file_scan_span[1]):
                outside_file_scan = True
                break
        if outside_file_scan and required_name not in file_scan_names:
            errors.append(
                "Misplaced subsection: "
                f"{template_spec.subsection_heading(required_name)} must be inside "
                "## File Scan Result"
            )

    errors = _format_errors(errors)
    return {
        "ok": not errors,
        "errors": errors,
        "top_level_sections": top_names,
        "file_scan_subsections": file_scan_names,
    }


def check_analysis_template_file(path: Path) -> Dict[str, object]:
    p = Path(path)
    content = p.read_text(encoding="utf-8", errors="replace")
    result = check_analysis_template(content)
    result["path"] = str(p)
    return result


def build_template_repair_messages(
    dataset_name: str,
    content: str,
    errors: List[str],
) -> Dict[str, str]:
    numbered_errors = "\n".join(f"{idx}. {err}" for idx, err in enumerate(errors, 1))
    system_prompt = f"""You are an EEG dataset documentation repair assistant. Fix structural template errors in an analysis.md file.

The valid top-level sections (## headings) are EXACTLY these five, in this order:
1. ## Paradigm
2. ## File Scan Result
3. ## Tasks
4. ## Data Quality Notes
5. ## Kernel Responsibilities

Inside ## File Scan Result, the valid ### subsections are:
1. ### Event Structure
2. ### MISC Label Summary (optional)
3. ### Info

Rules:
- If a required section is missing, add it with minimal placeholder content.
- If a section has a wrong name, rename it to the closest valid section title.
- If a forbidden/deprecated section exists, remove it or merge its content into the appropriate valid section.
- If an unexpected section exists, either rename it to the closest valid section or remove it.
- If a required File Scan Result subsection is missing, add it with minimal placeholder content.
- Preserve all existing content as much as possible. Fix structure only.
- Do not rewrite facts, field values, tables, task definitions, or narrative content unless needed to restore the required structure.
- Return ONLY valid JSON, no markdown fences:
{{"fixed_content": "<complete fixed analysis.md as a single string with \\n for newlines>"}}"""

    user_prompt = f"""Dataset: {dataset_name}

=== Structural template errors ===
{numbered_errors}

=== Current analysis.md ===
{content}"""

    return {
        "system": system_prompt,
        "user": user_prompt,
    }
