"""Shared structural template checker for dataset analysis.md files."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from neuroaudit import template_spec


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


def _check_manual_review_inline(content: str) -> List[str]:
    errors: List[str] = []
    first_section = re.search(r"^##\s+\S", content, flags=re.MULTILINE)
    header = content[: first_section.start()] if first_section else content
    category_line_match = re.search(r"^\*\*Category\*\*[^\n]*$", header, flags=re.MULTILINE)
    standalone_match = re.search(r"^\*\*Manual Review\*\*:[^\n]*$", header, flags=re.MULTILINE)

    if standalone_match:
        errors.append("Manual Review must be inline on the second meta line, not a standalone line.")

    if not category_line_match:
        return errors

    category_line = category_line_match.group(0)
    if "**Manual Review**:" not in category_line:
        errors.append("Manual Review must appear inline on the second meta line.")
    return errors


def check_analysis_template(content: str) -> Dict[str, object]:
    errors: List[str] = []
    content = str(content or "")
    errors.extend(_check_manual_review_inline(content))

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
