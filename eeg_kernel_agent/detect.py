#!/usr/bin/env python3
"""
eeg_kernel_agent — detect: batch check analysis.md and kernel files against semantic rulebook.

Usage:
    python detect.py --dataset openneuro_ds001784
    python detect.py --all
    python detect.py --all --severity error    # only show errors
    python detect.py --rulebook rulebook/semantic_rules.yaml  # custom rulebook

Output: per-dataset report with rule violations and a summary table.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not installed. Run: pip install pyyaml")

# ── Paths ────────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent
BIDS_ROOT = AGENT_DIR.parent
KERNELS_DIR = AGENT_DIR / "kernels"
DEFAULT_RULEBOOK = AGENT_DIR / "rulebook" / "semantic_rules.yaml"


# ── Rule checking engine ──────────────────────────────────────────────────────

def _check_pattern(text: str, rule: dict) -> bool:
    """Return True if rule is violated."""
    require_match = rule.get("require_match", False)
    pattern = rule.get("pattern", "")
    found = bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))
    if require_match:
        return not found  # violation = pattern NOT found
    else:
        return found      # violation = pattern IS found


def _check_section_exists(text: str, rule: dict) -> bool:
    """Return True if rule is violated (section missing)."""
    section = rule.get("section", "")
    return section not in text


def _check_rule(text: str, rule: dict) -> tuple[bool, str]:
    """
    Returns (violated: bool, detail: str).
    """
    check_type = rule.get("check", "pattern")
    violated = False

    if check_type == "pattern":
        violated = _check_pattern(text, rule)
        if violated:
            m = re.search(rule.get("pattern", ""), text, re.IGNORECASE | re.MULTILINE)
            detail = f"matched: {m.group()[:80]!r}" if m and not rule.get("require_match") else "(pattern not found)"
        else:
            detail = ""

    elif check_type == "section_exists":
        violated = _check_section_exists(text, rule)
        detail = f"section '{rule.get('section')}' missing" if violated else ""

    else:
        detail = f"(unknown check type: {check_type})"

    # context_require_absent: skip violation if this string is present in text
    if violated and "context_require_absent" in rule:
        if rule["context_require_absent"] in text:
            violated = False
            detail = ""

    return violated, detail


def check_dataset(dataset_name: str, rules: list[dict], severity_filter: str | None) -> list[dict]:
    """Check one dataset. Returns list of violation dicts."""
    violations = []

    analysis_path = BIDS_ROOT / dataset_name / "analysis.md"
    # Kernel can be in kernels/ flat or kernels/openneuro_specific/
    kernel_path = KERNELS_DIR / f"{dataset_name}.py"
    if not kernel_path.exists():
        # check sub-directories
        for sub in KERNELS_DIR.iterdir():
            if sub.is_dir():
                candidate = sub / f"{dataset_name}.py"
                if candidate.exists():
                    kernel_path = candidate
                    break

    analysis_text = analysis_path.read_text(encoding="utf-8") if analysis_path.exists() else ""
    kernel_text = kernel_path.read_text(encoding="utf-8") if kernel_path.exists() else ""

    for rule in rules:
        sev = rule.get("severity", "warning")
        if severity_filter and sev != severity_filter:
            continue

        target = rule.get("target", "analysis_md")
        texts_to_check: list[tuple[str, str]] = []
        if target in ("analysis_md", "both"):
            if analysis_text:
                texts_to_check.append(("analysis_md", analysis_text))
            elif target == "analysis_md":
                violations.append({
                    "dataset": dataset_name, "rule_id": rule["id"],
                    "severity": sev, "target": "analysis_md",
                    "detail": "analysis.md not found",
                })
                continue
        if target in ("kernel", "both"):
            if kernel_text:
                texts_to_check.append(("kernel", kernel_text))
            elif target == "kernel":
                violations.append({
                    "dataset": dataset_name, "rule_id": rule["id"],
                    "severity": sev, "target": "kernel",
                    "detail": "kernel file not found",
                })
                continue

        for file_type, text in texts_to_check:
            violated, detail = _check_rule(text, rule)
            if violated:
                violations.append({
                    "dataset": dataset_name,
                    "rule_id": rule["id"],
                    "severity": sev,
                    "target": file_type,
                    "desc": rule.get("desc", ""),
                    "detail": detail,
                })

    return violations


# ── Output ────────────────────────────────────────────────────────────────────

def _print_report(all_violations: list[dict], datasets: list[str]) -> None:
    SEV_ORDER = {"error": 0, "warning": 1, "info": 2}
    all_violations.sort(key=lambda v: (v["dataset"], SEV_ORDER.get(v["severity"], 9), v["rule_id"]))

    current_ds = None
    for v in all_violations:
        if v["dataset"] != current_ds:
            current_ds = v["dataset"]
            print(f"\n{'─'*60}")
            print(f"  {current_ds}")
            print(f"{'─'*60}")
        icon = {"error": "✗", "warning": "!", "info": "i"}.get(v["severity"], "?")
        print(f"  [{icon}] [{v['severity'].upper():7}] [{v['target']:11}] {v['rule_id']}")
        if v.get("desc"):
            print(f"          {v['desc']}")
        if v.get("detail"):
            print(f"          → {v['detail']}")

    print(f"\n{'='*60}")
    n_err = sum(1 for v in all_violations if v["severity"] == "error")
    n_warn = sum(1 for v in all_violations if v["severity"] == "warning")
    n_clean = sum(1 for ds in datasets if not any(v["dataset"] == ds for v in all_violations))
    print(f"  Checked: {len(datasets)} datasets | Clean: {n_clean} | "
          f"Errors: {n_err} | Warnings: {n_warn}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="eeg_kernel_agent: semantic rule checker")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dataset", "-d", nargs="+", help="Dataset name(s) to check")
    grp.add_argument("--all", action="store_true", help="Check all datasets with analysis.md")
    parser.add_argument("--severity", choices=["error", "warning", "info"],
                        help="Only show violations of this severity level")
    parser.add_argument("--rulebook", default=str(DEFAULT_RULEBOOK),
                        help=f"Path to rulebook YAML (default: {DEFAULT_RULEBOOK})")
    args = parser.parse_args()

    rulebook_path = Path(args.rulebook)
    if not rulebook_path.exists():
        sys.exit(f"ERROR: Rulebook not found: {rulebook_path}")

    rules = yaml.safe_load(rulebook_path.read_text(encoding="utf-8")).get("rules", [])
    print(f"[detect] Loaded {len(rules)} rules from {rulebook_path.name}")

    if args.all:
        datasets = sorted(
            p.parent.name
            for p in BIDS_ROOT.glob("*/analysis.md")
            if not p.parent.name.startswith(".")
            and p.parent.name not in ("eeg_kernel_agent", "app_kernel", "auto_eeg", "app")
        )
    else:
        datasets = []
        for item in args.dataset:
            datasets.extend(d.strip() for d in item.split(",") if d.strip())
        datasets = list(dict.fromkeys(datasets))

    print(f"[detect] Checking {len(datasets)} dataset(s)...\n")

    all_violations = []
    for ds in datasets:
        viols = check_dataset(ds, rules, args.severity)
        all_violations.extend(viols)

    _print_report(all_violations, datasets)

    # Exit code: 1 if any errors
    if any(v["severity"] == "error" for v in all_violations):
        sys.exit(1)


if __name__ == "__main__":
    main()
