"""
Lightweight patcher: reads participants.tsv → patches ### Info table in analysis.md.
No LLM calls needed. Run after the doc_writer.py fix is applied.
"""
from __future__ import annotations
import csv, io, re, sys
from collections import Counter
from pathlib import Path

BIDS_ROOT = Path(__file__).parent.parent
RAW_BASE = Path("/home/public/eeg_dataset/openneuro_raw")

sys.path.insert(0, str(BIDS_ROOT / "app_kernel"))
import scan_engine  # noqa: E402


def _parse_participants_tsv(tsv_path: Path):
    """Returns (age_comp_str, sex_comp_str) or (None, None)."""
    try:
        text = tsv_path.read_text(encoding="utf-8", errors="replace")
        rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
        n = len(rows)
        if n == 0:
            return None, None

        ages = []
        for r in rows:
            try:
                ages.append(float(r.get("age", "")))
            except (ValueError, TypeError):
                pass

        sexes = [r.get("sex", r.get("gender", "")).strip() for r in rows]
        sexes = [s for s in sexes if s]
        sex_counts = dict(Counter(sexes))
        sex_total = sum(sex_counts.values())

        age_comp = "complete" if ages else None
        if sex_total == 0:
            sex_comp = "missing"
        elif sex_total >= n * 0.99:
            sex_comp = "complete"
        elif sex_total > 0:
            sex_comp = f"partial ({sex_total}/{n})"
        else:
            sex_comp = None

        return age_comp, sex_comp
    except Exception as e:
        print(f"  WARN: {e}")
        return None, None


def patch_analysis_md(analysis_path: Path, age_comp: str, sex_comp: str) -> bool:
    """Patch ### Info table in analysis.md. Returns True if changed."""
    content = analysis_path.read_text(encoding="utf-8")

    info_m = re.search(
        r"(### Info\s*\n\| Field.*?\n\|[-| ]+\n)(.*?)(?=\n###|\n## |\Z)",
        content, re.DOTALL,
    )
    if not info_m:
        return False

    rows_text = info_m.group(2)
    changed = False

    def _patch_row(rows_text, field, new_comp):
        nonlocal changed
        pattern = re.compile(
            r"(\|\s*`" + re.escape(field) + r"`\s*\|)\s*\S+\s*(\|[^|]*\|)",
            re.MULTILINE
        )
        m = pattern.search(rows_text)
        if m:
            old_comp = rows_text[m.start():m.end()].split("|")[2].strip()
            if old_comp != new_comp:
                rows_text = pattern.sub(lambda x: f"{x.group(1)} {new_comp} {x.group(2)}", rows_text)
                changed = True
        return rows_text

    if age_comp:
        rows_text = _patch_row(rows_text, "subject_age", age_comp)
    if sex_comp and sex_comp != "missing":
        rows_text = _patch_row(rows_text, "subject_sex", sex_comp)

    if changed:
        new_content = content[:info_m.start(2)] + rows_text + content[info_m.end(2):]
        analysis_path.write_text(new_content, encoding="utf-8")
    return changed


def main():
    progress_dir = BIDS_ROOT / "auto_eeg" / "progress"
    patched = 0
    skipped = 0
    no_tsv = 0

    for pf in sorted(progress_dir.glob("openneuro_*.json")):
        ds_name = pf.stem  # e.g. openneuro_ds001784
        raw_name = ds_name.replace("openneuro_", "")  # ds001784
        raw_dir = RAW_BASE / raw_name
        tsv = raw_dir / "participants.tsv"

        analysis_md = BIDS_ROOT / ds_name / "analysis.md"
        if not analysis_md.exists():
            skipped += 1
            continue
        if not tsv.exists():
            no_tsv += 1
            continue

        age_comp, sex_comp = _parse_participants_tsv(tsv)
        if age_comp is None and sex_comp is None:
            skipped += 1
            continue

        changed = patch_analysis_md(analysis_md, age_comp or "", sex_comp or "")
        if changed:
            patched += 1
            print(f"  PATCHED {ds_name}: age={age_comp}, sex={sex_comp}")
        else:
            skipped += 1

    print(f"\nDone: {patched} patched, {skipped} skipped, {no_tsv} no participants.tsv")


if __name__ == "__main__":
    main()
