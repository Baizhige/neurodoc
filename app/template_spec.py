"""Machine-readable template specification for dataset analysis.md files."""

from __future__ import annotations

REQUIRED_TOP_LEVEL_SECTIONS = [
    "Paradigm",
    "File Scan Result",
    "Tasks",
    "Data Quality Notes",
    "Kernel Responsibilities",
]

FORBIDDEN_TOP_LEVEL_SECTIONS = [
    "STIM Label Summary",
]

FILE_SCAN_REQUIRED_SUBSECTIONS = [
    "Event Structure",
    "Info",
]

FILE_SCAN_OPTIONAL_SUBSECTIONS = [
    "MISC Label Summary",
]

FILE_SCAN_SUBSECTION_ORDER = [
    "Event Structure",
    "MISC Label Summary",
    "Info",
]

ALLOWED_FILE_SCAN_SUBSECTIONS = (
    FILE_SCAN_REQUIRED_SUBSECTIONS + FILE_SCAN_OPTIONAL_SUBSECTIONS
)


def top_level_heading(name: str) -> str:
    return f"## {name}"


def subsection_heading(name: str) -> str:
    return f"### {name}"


def format_top_level_order() -> str:
    return " -> ".join(top_level_heading(name) for name in REQUIRED_TOP_LEVEL_SECTIONS)


def format_file_scan_subsection_order() -> str:
    parts = []
    for name in FILE_SCAN_SUBSECTION_ORDER:
        heading = subsection_heading(name)
        if name in FILE_SCAN_OPTIONAL_SUBSECTIONS:
            heading += " (optional)"
        parts.append(heading)
    return " -> ".join(parts)

