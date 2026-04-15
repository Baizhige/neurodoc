"""Phase 2: Analyze reference files (PDF/HTML) in a single batched LLM call.

Uses the model's large context window (~170K) to process all reference files
in one call instead of 2 calls per file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# PDF / HTML parsing (optional deps)
try:
    import fitz as _fitz
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False

try:
    from bs4 import BeautifulSoup as _BS4
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False


_BATCH_SYSTEM = """\
You are an expert EEG neuroscience analyst. Analyze multiple reference files for ONE specific EEG dataset \
and return a JSON ARRAY — one object per file.

For EACH file, output a JSON object:
{
  "filename": "<exact filename as given>",
  "ref": "<DOI / arXiv / URL extracted from content, or empty>",
  "title": "<paper title or empty>",
  "classification": "relevant|partial|irrelevant|uncertain|junk",
  "cot_reasoning": "<2-3 sentence chain-of-thought>",
  "supports_task": false,
  "task_type": "classification|regression|segmentation|none",
  "n_classes": 0,
  "paradigm": "",
  "epoch_method_hint": "event-based|long-event|segmentation|unclear",
  "epoch_params": "",
  "target_events": [],
  "label_mapping": "",
  "meta_level": "raw|super|unclear",
  "super_meta_note": "",
  "evidence_desc": ""
}

Classification rules:
  relevant   : paper EXPLICITLY uses THIS specific dataset AND defines a concrete ML task with labels
  partial    : uses this dataset but task/label definition is vague or incomplete
  irrelevant : related EEG topic but does NOT use this specific dataset
  uncertain  : insufficient text to judge
  junk       : clearly wrong domain

Fill supports_task / task_type / epoch_params etc. only for relevant/partial papers; leave defaults for others.

Output ONLY a valid JSON array, no markdown fences, no surrounding text:
[ {...}, {...}, ... ]"""

_PER_FILE_MAX = 10000    # chars per file in deep-analysis prompt
_MIN_USEFUL_CHARS = 200  # skip files shorter than this after extraction
_CLASSIFY_SNIPPET = 600  # chars per file in the quick classifier pass


# ---------------------------------------------------------------------------
# Two-pass classifier system prompt
# ---------------------------------------------------------------------------

_CLASSIFY_SYSTEM = """\
You are an EEG reference relevance classifier. Given SHORT snippets from multiple reference \
files for ONE specific EEG dataset, quickly classify each file's relevance to that dataset.

Return ONLY a JSON object mapping EXACT filename to classification string:
{
  "filename1.pdf": "relevant",
  "filename2.html": "irrelevant",
  ...
}

Classification values:
  relevant   : paper/page EXPLICITLY mentions or uses THIS specific dataset AND describes \
ML tasks, event codes, or label definitions
  partial    : mentions the dataset or closely related paradigm but task/label info is vague
  irrelevant : EEG-related but clearly does NOT use this specific dataset
  junk       : wrong domain, too short, or clearly uninformative

When in doubt, use "partial" rather than "irrelevant".
Output ONLY valid JSON, no markdown fences:"""


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_ref_text(file_path: Path) -> Tuple[str, str]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        if not _HAS_FITZ:
            return f"[PDF unavailable: install pymupdf — filename: {file_path.name}]", "pdf"
        try:
            doc = _fitz.open(str(file_path))
            parts = [p.get_text("text") for p in doc if p.get_text("text").strip()]
            doc.close()
            return _clean_text("\n".join(parts)), "pdf"
        except Exception as e:
            return f"[PDF error: {e}]", "pdf"
    if suffix in (".html", ".htm"):
        if _HAS_BS4:
            try:
                soup = _BS4(file_path.read_bytes(), "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return _clean_text(soup.get_text(separator="\n")), "html"
            except Exception as e:
                return f"[HTML error: {e}]", "html"
    try:
        return file_path.read_text(encoding="utf-8", errors="replace"), "text"
    except Exception as e:
        return f"[read error: {e}]", "unknown"


def _ref_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.startswith("paper_"):
        doi_raw = stem[6:]
        if doi_raw.startswith("10_"):
            parts = doi_raw.split("_")
            if len(parts) >= 3:
                return f"10.{parts[1]}/{'.'.join(parts[2:])}"
    m = re.search(r"(10\.\d{4,})_([^\s]+)", stem)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return ""


def _parse_json(raw: str) -> Optional[Dict]:
    """Parse a single JSON object from raw string (used by other modules)."""
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```\s*$", "", raw).strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return None


def _parse_batch_response(raw: str, file_texts: List[Dict], log) -> List[Dict[str, Any]]:
    """Parse the batched LLM response (JSON array) and return results."""
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```\s*$", "", raw).strip()

    m = re.search(r"\[[\s\S]*\]", raw)
    if m:
        try:
            items = json.loads(m.group())
            if isinstance(items, list):
                results = []
                for item in items:
                    if isinstance(item, dict):
                        item.setdefault("classification", "uncertain")
                        results.append(item)
                log(f"[RefAnalyzer] Parsed {len(results)} results from batch response")
                return results
        except json.JSONDecodeError as e:
            log(f"[RefAnalyzer] JSON parse error: {e}")

    # Fallback: mark all as uncertain
    log("[RefAnalyzer] Could not parse batch response — marking all as uncertain")
    return [
        {
            "filename": ft["path"].name,
            "classification": "uncertain",
            "ref": ft["doi_hint"],
            "error": "LLM batch parse failed",
        }
        for ft in file_texts
    ]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_references(
    dataset_name: str,
    ref_files: List[Path],
    analysis_md: str,
    call_llm,
    budget,
    log,
) -> List[Dict[str, Any]]:
    """Two-pass reference analysis.

    Pass A (1 LLM): Quick classifier — 600 chars/file, get relevant/partial/irrelevant/junk.
    Pass B (1 LLM/file, parallel-ready): Deep analysis of relevant+partial files only.
    irrelevant/junk files are skipped entirely in pass B.
    """
    if not ref_files:
        return []

    # --- Extract text for all files, skip unreadable/empty ---
    skipped: List[Dict] = []
    file_texts: List[Dict] = []
    for ref_path in ref_files:
        full_text, ftype = _extract_ref_text(ref_path)

        if full_text.startswith("["):
            log(f"[RefAnalyzer] SKIP (unreadable): {ref_path.name}")
            skipped.append({"filename": ref_path.name, "classification": "uncertain",
                            "error": full_text[:200]})
            continue

        if len(full_text.strip()) < _MIN_USEFUL_CHARS:
            log(f"[RefAnalyzer] SKIP (too short, {len(full_text.strip())} chars): {ref_path.name}")
            skipped.append({"filename": ref_path.name, "classification": "uncertain",
                            "ref": _ref_from_filename(ref_path.name),
                            "error": f"Extracted text too short ({len(full_text.strip())} chars) — likely SPA shell."})
            continue

        file_texts.append({
            "path": ref_path,
            "text": full_text,
            "doi_hint": _ref_from_filename(ref_path.name),
        })

    if not file_texts:
        log("[RefAnalyzer] No usable reference files — all skipped.")
        return skipped

    # =========================================================
    # Pass A: Quick classifier (1 LLM, 600 chars/file)
    # =========================================================
    classifications: Dict[str, str] = {}
    if len(file_texts) > 1:
        snippets = []
        for ft in file_texts:
            snippets.append(
                f"--- {ft['path'].name} ---\n"
                f"DOI hint: {ft['doi_hint'] or '(none)'}\n"
                f"{ft['text'][:_CLASSIFY_SNIPPET]}"
            )
        classify_msg = (
            f"Dataset: {dataset_name}\n\n"
            f"analysis.md title/paradigm:\n{analysis_md[:800]}\n\n"
            f"=== Reference snippets ({len(file_texts)} files) ===\n\n"
            + "\n\n".join(snippets)
        )
        try:
            budget.charge("ref_analysis")
            raw = call_llm([
                {"role": "system", "content": _CLASSIFY_SYSTEM},
                {"role": "user", "content": classify_msg},
            ])
            # Parse JSON dict
            raw_clean = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
            raw_clean = re.sub(r"^```(?:json)?\s*", "", raw_clean).strip()
            raw_clean = re.sub(r"\s*```\s*$", "", raw_clean).strip()
            m = re.search(r"\{[\s\S]*\}", raw_clean)
            if m:
                classifications = json.loads(m.group())
                log(f"[RefAnalyzer] Pass A classifications: {classifications}")
        except Exception as e:
            log(f"[RefAnalyzer] Pass A classifier failed ({e}), treating all as partial")
    else:
        # Only 1 file — skip classifier, go straight to deep analysis
        log("[RefAnalyzer] Single file — skipping classifier pass")

    # =========================================================
    # Pass B: Deep analysis of relevant + partial files
    # =========================================================
    to_deep: List[Dict] = []
    skipped_irrelevant: List[Dict] = []

    for ft in file_texts:
        cls = classifications.get(ft["path"].name, "partial")  # default: partial if no classification
        if cls in ("relevant", "partial"):
            to_deep.append(ft)
        else:
            log(f"[RefAnalyzer]   SKIP deep analysis ({cls}): {ft['path'].name}")
            skipped_irrelevant.append({
                "filename": ft["path"].name,
                "classification": cls,
                "ref": ft["doi_hint"],
                "supports_task": False,
                "task_type": "none",
                "evidence_desc": f"Classified as {cls} in pass A — skipped deep analysis.",
            })

    results: List[Dict] = []
    if to_deep:
        log(f"[RefAnalyzer] Pass B: deep analyzing {len(to_deep)} relevant/partial file(s)...")

        # Build batched prompt for deep analysis
        sections = []
        for i, ft in enumerate(to_deep, 1):
            sections.append(
                f"--- FILE {i}: {ft['path'].name} ---\n"
                f"DOI hint: {ft['doi_hint'] or '(none)'}\n\n"
                f"{ft['text'][:_PER_FILE_MAX]}"
            )
        user_msg = (
            f"Dataset: {dataset_name}\n\n"
            f"=== analysis.md (context) ===\n{analysis_md[:3000]}\n\n"
            f"=== Reference files to deep-analyze ({len(to_deep)} files) ===\n\n"
            + "\n\n".join(sections)
        )
        results = _call_batch_with_fallback(
            to_deep, dataset_name, analysis_md, user_msg, call_llm, budget, log
        )

    for r in results:
        log(f"[RefAnalyzer]   {r.get('filename','?')}: {r.get('classification','?')} | task={r.get('supports_task',False)}")

    return skipped + skipped_irrelevant + results


def _call_batch_with_fallback(
    file_texts: List[Dict],
    dataset_name: str,
    analysis_md: str,
    full_user_msg: str,
    call_llm,
    budget,
    log,
) -> List[Dict[str, Any]]:
    """Try full batch first; fall back to chunks of 3 if the full call fails."""
    budget.charge("ref_analysis")
    try:
        raw = call_llm([
            {"role": "system", "content": _BATCH_SYSTEM},
            {"role": "user", "content": full_user_msg},
        ])
        results = _parse_batch_response(raw, file_texts, log)
        if results:
            return results
    except Exception as exc:
        log(f"[RefAnalyzer] Full batch failed ({exc}), falling back to chunks of 3...")

    # Chunked fallback: process 3 files at a time
    chunk_size = 3
    all_results = []
    for i in range(0, len(file_texts), chunk_size):
        chunk = file_texts[i:i + chunk_size]
        sections = []
        for j, ft in enumerate(chunk, 1):
            sections.append(
                f"--- FILE {j}: {ft['path'].name} ---\n"
                f"DOI hint from filename: {ft['doi_hint'] or '(none)'}\n\n"
                f"{ft['text']}"
            )
        chunk_msg = (
            f"Dataset: {dataset_name}\n\n"
            f"=== analysis.md (context) ===\n{analysis_md[:2000]}\n\n"
            f"=== Reference files ({len(chunk)} files) ===\n\n"
            + "\n\n".join(sections)
        )
        try:
            budget.charge("ref_analysis")
            raw = call_llm([
                {"role": "system", "content": _BATCH_SYSTEM},
                {"role": "user", "content": chunk_msg},
            ])
            chunk_results = _parse_batch_response(raw, chunk, log)
            all_results.extend(chunk_results)
        except Exception as exc2:
            log(f"[RefAnalyzer] Chunk {i//chunk_size + 1} failed: {exc2}")
            all_results.extend([
                {"filename": ft["path"].name, "classification": "uncertain", "error": str(exc2)}
                for ft in chunk
            ])

    return all_results
