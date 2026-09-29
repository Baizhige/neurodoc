#!/usr/bin/env python3
"""
EEG Audit Tool - Flask server
Run: python -m neuroaudit
Then open http://127.0.0.1:5000
"""

import json
import re
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort

APP_DIR = Path(__file__).parent
from . import template_checker
from .strict_tasks import generate_tasks_phase2_strict
from neurodoc.api import (
    anthropic_to_openai_response,
    call_llm_text,
    post_llm_json,
    resolve_llm_config,
)
from neurodoc.paths import DATASET_DOCUMENT_DIR

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    _HAS_REQUESTS = False

CONFIG_FILE = APP_DIR / "config.json"
RULEBOOK_FILE = APP_DIR / "rulebook.md"
DATASET_DIR = DATASET_DOCUMENT_DIR
EXCLUDE_DIRS: set[str] = set()
EXCLUDE_NAME_RE = re.compile(r"\.(py|pdf|md|txt|json|csv)$", re.IGNORECASE)

app = Flask(__name__, static_folder=str(APP_DIR))

# ── Optional deps for reference text extraction ────────────────────────────────
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

# ── SKILL directory ────────────────────────────────────────────────────────────
SKILLS_DIR = APP_DIR / "skills"
CATEGORY_SKILL_MAP = {
    "Action/Output":      "action_output.md",
    "Sensory/Response":   "sensory_response.md",
    "Biological State":   "biological_state.md",
    "High-level Mental":  "high_level_mental.md",
    "Complex Applied":    "complex_applied.md",
    "Others":             "complex_applied.md",
}

def _load_skill(category: str) -> str:
    fname = CATEGORY_SKILL_MAP.get(category, "")
    if not fname:
        return ""
    p = SKILLS_DIR / fname
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""

def _category_from_md(analysis_md: str) -> str:
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]+)", analysis_md)
    return m.group(1).strip() if m else ""

# ── Phase-0 system prompt (DOI/URL/ref extraction per paper) ──────────────────
_P0_SYSTEM = """\
You are a research paper metadata extractor. Given the first two pages of a paper,
extract the primary reference identifier (DOI, URL, or arXiv ID) and the paper title.

Rules:
- Prefer DOI (format: 10.XXXX/...) over URL over arXiv ID
- arXiv ID format: arXiv:XXXX.XXXXX or https://arxiv.org/abs/XXXX.XXXXX
- If multiple DOIs appear, use the one for THIS paper (usually in header/footer, not in references)
- title: full paper title as it appears on the first page
- If nothing found, return empty strings

Output ONLY valid JSON, no markdown fences:
{"ref": "<doi or url or arxiv>", "ref_type": "doi|url|arxiv|none", "title": "<paper title>"}"""

# ── Phase-1 system prompt (relevance + task extraction per paper) ──────────────
_P1_SYSTEM = """\
You are an expert EEG neuroscience analyst. For a given EEG dataset and one reference paper,
perform TWO tasks in a single pass.

TASK A — Relevance classification (one of):
  relevant   : paper (a) explicitly uses/describes THIS specific dataset AND (b) defines a concrete ML task.
  partial    : paper uses this dataset but task definition is vague/incomplete (e.g. no class count,
               no epoch params, dataset only mentioned in passing). Can support Potential Tasks.
  irrelevant : related topic but does NOT use this dataset.
  uncertain  : insufficient text to judge.
  junk       : clearly wrong domain.

TASK B — Task extraction (fill for relevant/partial; leave empty only for irrelevant/junk):
  supports_task      : true if classification=relevant AND a concrete ML task with labels is defined.
  task_type          : "classification" | "regression" | "none"
                       (v3: Task Type is the learning target type, NOT the epoch method.
                        segmentation is an Epoch Method, not a Task Type.)
  n_classes          : integer number of classes, or 0 if unclear
  paradigm           : brief paradigm description (e.g. "4-class MI left/right fist, both fists, feet")
  epoch_method_hint  : "event-based" | "long-event" | "segmentation" | "unclear"
  epoch_params       : exact values stated in paper, e.g. "tmin=0s tmax=3s" or "unclear". Include
                       whether marker is cue onset or offset if stated.
  target_events      : list of class/event names using the paper's own terms (not raw IDs)
  label_mapping      : e.g. "left hand->0, right hand->1"
  meta_level         : "raw" | "super" | "unclear"
  super_meta_note    : how labels are derived if super; "" otherwise
  evidence_desc      : 2-4 sentences covering: (1) what task was performed on this dataset,
                       (2) number of classes and which classes, (3) epoch window if stated,
                       (4) any deviation from standard protocol or ambiguity. Be specific.
  ref                : the paper's DOI (10.xxxx/...), URL, or arXiv ID. Use value from Phase-0 if provided.

Output ONLY valid JSON, no surrounding text or markdown fences:
{
  "classification": "relevant|partial|irrelevant|uncertain|junk",
  "cot_reasoning": "<3-6 sentence chain-of-thought>",
  "supports_task": true|false,
  "task_type": "classification|regression|none",
  "n_classes": 0,
  "paradigm": "",
  "epoch_method_hint": "event-based|long-event|segmentation|unclear",
  "epoch_params": "",
  "target_events": [],
  "label_mapping": "",
  "meta_level": "raw|super|unclear",
  "super_meta_note": "",
  "evidence_desc": "",
  "ref": ""
}"""

# ── Reference pipeline helpers ─────────────────────────────────────────────────
_P1_REF_MAX   = 100_000
_P0_PAGE_MAX  = 6_000    # first ~2 pages for Phase-0
_P1_ANALYSIS_MAX = 5_000
_REF_EXTENSIONS = {'.pdf', '.html', '.htm', '.txt', '.md'}


def _clean_ref_text(text):
    text = re.sub(
        r"You may also like\n.*?This content was downloaded from IP address[^\n]*\n?",
        "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d{3,4}\s*$", "", text)
    blocks = re.split(r"\n{2,}", text)
    merged = []
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 4 and lines and sum(len(l) for l in lines) / len(lines) < 45:
            merged.append(" ".join(lines))
        else:
            merged.append(block)
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(merged)).strip()


def _extract_ref_text(file_path):
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        if not _HAS_FITZ:
            return f"[PDF unavailable: install pymupdf — filename: {file_path.name}]", "pdf"
        try:
            doc = _fitz.open(str(file_path))
            parts = [p.get_text("text") for p in doc if p.get_text("text").strip()]
            doc.close()
            return _clean_ref_text("\n".join(parts)), "pdf"
        except Exception as e:
            return f"[PDF error: {e}]", "pdf"
    if suffix in (".html", ".htm"):
        if _HAS_BS4:
            try:
                soup = _BS4(file_path.read_bytes(), "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return _clean_ref_text(soup.get_text(separator="\n")), "html"
            except Exception as e:
                return f"[HTML error: {e}]", "html"
    try:
        return file_path.read_text(encoding="utf-8", errors="replace"), "text"
    except Exception as e:
        return f"[read error: {e}]", "unknown"


def _ref_from_filename(filename):
    """Extract DOI hint from structured filenames like paper_10_1109_tnsre_..."""
    stem = Path(filename).stem
    if stem.startswith("paper_"):
        doi_raw = stem[6:]
        if doi_raw.startswith("10_"):
            parts = doi_raw.split("_")
            if len(parts) >= 3:
                return f"10.{parts[1]}/{'.'.join(parts[2:])}", "doi"
    m = re.search(r"(10\.\d{4,})_([^\s]+)", stem)
    if m:
        return f"{m.group(1)}/{m.group(2)}", "doi"
    return "", ""

# Keep old name as alias for backward compat
def _doi_from_filename(filename):
    ref, _ = _ref_from_filename(filename)
    return ref


def _ref_from_text_regex(text):
    """Fast regex extraction of DOI/URL/arXiv from text. Returns (ref, ref_type)."""
    # DOI pattern
    m = re.search(r'\b(10\.\d{4,}/[^\s,;"\'\]>\)]+)', text)
    if m:
        return m.group(1).rstrip('.'), "doi"
    # arXiv
    m = re.search(r'arXiv[:\s]+(\d{4}\.\d{4,})', text, re.IGNORECASE)
    if m:
        return f"https://arxiv.org/abs/{m.group(1)}", "arxiv"
    # URL
    m = re.search(r'(https?://[^\s,;"\'\]>]+)', text)
    if m:
        return m.group(1).rstrip('.'), "url"
    return "", "none"


def _call_llm(messages, timeout=180):
    """Internal LLM call using the stored /api/config credentials."""
    cfg = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return call_llm_text(cfg, messages, timeout=timeout)


def _parse_llm_json(raw):
    """Strip <think> blocks, fences, then extract the outermost JSON object."""
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```\s*$", "", raw).strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None, raw
    try:
        return json.loads(m.group()), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}\nRaw (first 400 chars): {raw[:400]}"


def _read_meta(content):
    category = ""
    status = ""
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]+)", content)
    if m:
        category = m.group(1).strip()
    m = re.search(r"\*\*Status\*\*:\s*(\S+)", content)
    if m:
        status = m.group(1).strip()
    return category, status


def _template_payload(content):
    result = template_checker.check_analysis_template(content)
    return {
        "template_ok": result["ok"],
        "template_errors": result["errors"],
        "template_check": result,
    }


def _list_datasets():
    result = []
    for entry in sorted(DATASET_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        if EXCLUDE_NAME_RE.search(entry.name):
            continue
        analysis = entry / "analysis.md"
        if not analysis.exists():
            continue
        try:
            content = analysis.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        category, status = _read_meta(content)
        template_info = _template_payload(content)
        result.append({
            "name": entry.name,
            "category": category or "Unknown",
            "status": status or "unknown",
            "template_ok": template_info["template_ok"],
            "template_errors": template_info["template_errors"],
        })
    return result


@app.route("/")
def index():
    return send_from_directory(APP_DIR, "index.html")


@app.route("/api/datasets")
def api_datasets():
    return jsonify(_list_datasets())


@app.route("/api/dataset/<name>", methods=["GET"])
def api_get_dataset(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    path = DATASET_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    content = path.read_text(encoding="utf-8", errors="replace")
    payload = {"name": name, "content": content}
    payload.update(_template_payload(content))
    return jsonify(payload)


@app.route("/api/dataset/<name>", methods=["PUT"])
def api_put_dataset(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    path = DATASET_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    data = request.get_json(silent=True)
    if not data or "content" not in data:
        abort(400)
    check = template_checker.check_analysis_template(data["content"])
    if not check["ok"]:
        return jsonify({
            "ok": False,
            "error": "Template validation failed",
            "template_check": check,
        }), 400
    path.write_text(data["content"], encoding="utf-8")
    return jsonify({"ok": True, "template_check": check})


@app.route("/api/rulebook")
def api_rulebook():
    if not RULEBOOK_FILE.exists():
        return jsonify({"content": "# Rulebook not found"})
    content = RULEBOOK_FILE.read_text(encoding="utf-8", errors="replace")
    return jsonify({"content": content})


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        else:
            cfg = {"BASE_URL": "", "ANTHROPIC_BASE_URL": "", "key": "", "model": "", "proxy": ""}
        try:
            normalized = resolve_llm_config(cfg)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        result = dict(cfg)
        result["BASE_URL"] = normalized["BASE_URL"]
        result["ANTHROPIC_BASE_URL"] = normalized["ANTHROPIC_BASE_URL"]
        result.setdefault("key", "")
        result.setdefault("model", "")
        result.setdefault("proxy", "")
        return jsonify(result)
    data = request.get_json(silent=True) or {}
    try:
        normalized = resolve_llm_config(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    to_save = {
        "BASE_URL": normalized["BASE_URL"],
        "ANTHROPIC_BASE_URL": normalized["ANTHROPIC_BASE_URL"],
        "key": normalized["key"],
        "model": normalized["model"],
        "proxy": normalized["proxy"],
    }
    CONFIG_FILE.write_text(json.dumps(to_save, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify({"ok": True})


@app.route("/api/llm", methods=["POST"])
def api_llm():
    cfg = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    try:
        resolved_cfg = resolve_llm_config(cfg)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not resolved_cfg.get("active_url"):
        return jsonify({"error": "LLM URL not configured. Open Settings to configure."}), 400

    body = request.get_json(silent=True) or {}
    messages = body.get("messages") or []
    # remove stream flag — some providers reject it
    body.pop("stream", None)

    try:
        data = post_llm_json(resolved_cfg, messages, timeout=90, extra_body=body)
        if resolved_cfg["provider"] == "anthropic":
            return jsonify(anthropic_to_openai_response(data))
        return jsonify(data)
    except Exception as e:
        response = getattr(e, "response", None)
        status = getattr(response, "status_code", None)
        if status is not None:
            return jsonify({"error": f"HTTP {status}: {getattr(response, 'text', '')}"}), 502
        return jsonify({"error": str(e)}), 500


@app.route("/api/refs/<name>")
def api_refs_list(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    refs_dir = DATASET_DIR / name / "references"
    if not refs_dir.is_dir():
        return jsonify({"files": [], "error": "No references/ directory found for this dataset."})
    files = sorted(
        f.name for f in refs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in _REF_EXTENSIONS
    )
    return jsonify({"files": files})


@app.route("/api/refs/phase0/<name>", methods=["POST"])
def api_refs_phase0(name):
    """Phase-0: extract DOI/URL/ref from a single reference file (regex + LLM fallback)."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    ref_file = data.get("file", "")
    if not ref_file or ".." in ref_file:
        abort(400)
    ref_path = DATASET_DIR / name / "references" / ref_file
    if not ref_path.exists():
        return jsonify({"error": f"File not found: {ref_file}"}), 404

    # 1. Filename-based hint
    filename_ref, filename_ref_type = _ref_from_filename(ref_file)
    if filename_ref_type == "doi":
        return jsonify({"ref": filename_ref, "ref_type": "doi",
                        "title": "", "reference_file": ref_file, "source": "filename"})

    # 2. Extract text and try regex on first portion
    ref_text, _ = _extract_ref_text(ref_path)
    first_chunk = ref_text[:_P0_PAGE_MAX]
    regex_ref, regex_type = _ref_from_text_regex(first_chunk)
    if regex_ref and regex_type == "doi":
        return jsonify({"ref": regex_ref, "ref_type": "doi",
                        "title": "", "reference_file": ref_file, "source": "regex"})

    # 3. LLM fallback for title + any ref type
    try:
        raw = _call_llm([
            {"role": "system", "content": _P0_SYSTEM},
            {"role": "user",   "content": f"File: {ref_file}\n\n{first_chunk}"},
        ], timeout=60)
        parsed, _ = _parse_llm_json(raw)
        if parsed and parsed.get("ref"):
            parsed["reference_file"] = ref_file
            parsed["source"] = "llm"
            return jsonify(parsed)
    except Exception:
        pass

    # 4. Use regex result even if not DOI, or empty
    return jsonify({"ref": regex_ref, "ref_type": regex_type or "none",
                    "title": "", "reference_file": ref_file, "source": "regex_fallback"})


@app.route("/api/refs/phase1/<name>", methods=["POST"])
def api_refs_phase1(name):
    """Phase-1: relevance classification + task extraction for one reference file."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    ref_file = data.get("file", "")
    p0_result = data.get("p0", {})   # Phase-0 result passed in from frontend
    if not ref_file or ".." in ref_file:
        abort(400)
    ref_path = DATASET_DIR / name / "references" / ref_file
    if not ref_path.exists():
        return jsonify({"error": f"File not found: {ref_file}"}), 404

    ref_text, _ = _extract_ref_text(ref_path)
    ref_text = ref_text[:_P1_REF_MAX]

    analysis_draft = data.get("analysis_md")
    analysis_brief = analysis_draft if isinstance(analysis_draft, str) and analysis_draft.strip() else ""
    analysis_path = DATASET_DIR / name / "analysis.md"
    if not analysis_brief and analysis_path.exists():
        analysis_brief = analysis_path.read_text(encoding="utf-8", errors="replace")[:_P1_ANALYSIS_MAX]
    else:
        analysis_brief = analysis_brief[:_P1_ANALYSIS_MAX]

    # Ref hint: Phase-0 result takes priority over filename
    ref_hint = p0_result.get("ref") or _doi_from_filename(ref_file)
    ref_hint_line = f"Reference identifier (DOI/URL/arXiv): {ref_hint}\n" if ref_hint else ""

    user_msg = (
        f"Dataset: {name}\n\n"
        f"=== Dataset context (current online draft; fallback is analysis.md) ===\n{analysis_brief}\n\n"
        f"=== Reference file: {ref_file} ===\n"
        f"{ref_hint_line}"
        f"{ref_text}\n\n"
        f"Classify and extract task information for dataset '{name}' from the above reference."
    )

    try:
        raw = _call_llm([
            {"role": "system", "content": _P1_SYSTEM},
            {"role": "user",   "content": user_msg},
        ])
        parsed, err = _parse_llm_json(raw)
        if parsed is None:
            return jsonify({"error": f"Phase-1 parse failed: {err}",
                            "reference_file": ref_file,
                            "classification": "uncertain",
                            "supports_task": False}), 200

        parsed["reference_file"] = ref_file
        # Resolve ref: LLM output > Phase-0 > filename
        parsed["ref"] = parsed.get("ref") or ref_hint
        parsed["doi"] = parsed["ref"]  # backward compat alias
        parsed["extraction"] = {k: parsed.get(k) for k in (
            "supports_task", "task_type", "n_classes", "paradigm",
            "epoch_method_hint", "epoch_params", "target_events",
            "label_mapping", "meta_level", "super_meta_note",
            "evidence_desc", "ref",
        )}
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e), "reference_file": ref_file,
                        "classification": "uncertain", "supports_task": False}), 500


@app.route("/api/tasks/phase2/<name>", methods=["POST"])
def api_tasks_phase2(name):
    """Strict Phase-2 task regeneration using the doc-only/reference-only synthesis pipeline."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    extractions = data.get("extractions", data.get("supporting", []))

    analysis_path = DATASET_DIR / name / "analysis.md"
    if not analysis_path.exists():
        abort(404)
    analysis_draft = data.get("analysis_md")
    analysis_md = (
        analysis_draft
        if isinstance(analysis_draft, str) and analysis_draft.strip()
        else analysis_path.read_text(encoding="utf-8", errors="replace")
    )

    category = _category_from_md(analysis_md)
    skill_text = _load_skill(category)

    try:
        result = generate_tasks_phase2_strict(
            dataset_name=name,
            extractions=extractions,
            analysis_md=analysis_md,
            skill_text=skill_text,
            llm_config_path=CONFIG_FILE,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "ok": False,
            "tasks_section": "",
            "summary": "",
            "semantic_errors": [],
            "hard_fail_reason": str(e),
            "grounding_summary": {"logs": []},
            "generation_mode": "doc_only_rulebook_v1_0_strict",
            "error": str(e),
        }), 500

if __name__ == "__main__":
    print("EEG Audit Tool running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
