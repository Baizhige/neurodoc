#!/usr/bin/env python3
"""
app_scan Flask server — EEG Kernel Scan Tool
Run: python app_kernel/server_scan.py
Then open http://127.0.0.1:5001
"""

from __future__ import annotations

import json
import re
import sys
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

APP_KERNEL_DIR = Path(__file__).parent
BIDS_ROOT = APP_KERNEL_DIR.parent
MAIN_APP_CONFIG = BIDS_ROOT / "app" / "config.json"
if str(BIDS_ROOT) not in sys.path:
    sys.path.insert(0, str(BIDS_ROOT))

from app import template_checker
try:
    from app_kernel import scan_engine as engine
except ImportError:
    import scan_engine as engine

app = Flask(__name__, static_folder=str(APP_KERNEL_DIR))


def _template_check_for_dataset(name: str) -> dict:
    analysis_path = BIDS_ROOT / name / "analysis.md"
    if not analysis_path.exists():
        return {
            "ok": False,
            "errors": ["analysis.md not found"],
        }
    content = analysis_path.read_text(encoding="utf-8", errors="replace")
    return template_checker.check_analysis_template(content)


def _invalid_template_map(names):
    result = {}
    for name in names:
        check = _template_check_for_dataset(name)
        if not check.get("ok"):
            result[name] = check.get("errors", [])
    return result

# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------

_jobs: dict = {}  # job_id → {status, progress, message, result, error, stdout_lines}
_jobs_lock = threading.Lock()


def _new_job() -> str:
    jid = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _jobs[jid] = {
            "status": "pending", "progress": 0, "message": "",
            "result": None, "error": None, "stdout_lines": [],
        }
    return jid


def _update_job(jid: str, **kwargs) -> None:
    with _jobs_lock:
        _jobs[jid].update(kwargs)


# ---------------------------------------------------------------------------
# Routes — static
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(APP_KERNEL_DIR, "app_scan.html")


# ---------------------------------------------------------------------------
# Routes — config
# ---------------------------------------------------------------------------

@app.route("/api/config", methods=["GET"])
def api_config_get():
    cfg = engine.load_machine_config()
    cfg["machine_id"] = engine.get_machine_id()
    cfg["eegunity_version"] = engine.get_eegunity_version(cfg.get("eegunity_path", ""))
    # Merge LLM config (machine config takes priority over main app config)
    llm_cfg = engine.load_llm_config()
    cfg.setdefault("url", llm_cfg.get("url", ""))
    cfg.setdefault("key", llm_cfg.get("key", ""))
    cfg.setdefault("model", llm_cfg.get("model", ""))
    cfg.setdefault("proxy", llm_cfg.get("proxy", ""))
    return jsonify(cfg)


@app.route("/api/config", methods=["POST"])
def api_config_post():
    data = request.get_json(silent=True) or {}
    # Machine-local fields (dataset paths + per-machine LLM overrides)
    machine_keys = {"dataset_roots", "eegunity_path", "num_workers", "url", "key", "model", "proxy"}
    machine_data = {k: v for k, v in data.items() if k in machine_keys}
    engine.save_machine_config(machine_data)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — datasets
# ---------------------------------------------------------------------------

@app.route("/api/datasets")
def api_datasets():
    datasets = engine.list_datasets()
    for ds in datasets:
        check = _template_check_for_dataset(ds["name"])
        ds["template_ok"] = check.get("ok", False)
        ds["template_errors"] = check.get("errors", [])
    return jsonify(datasets)


@app.route("/api/dataset/<name>/analysis")
def api_get_analysis(name):
    if ".." in name:
        abort(400)
    p = BIDS_ROOT / name / "analysis.md"
    if not p.exists():
        abort(404)
    content = p.read_text(encoding="utf-8", errors="replace")
    return jsonify({
        "content": content,
        "template_check": template_checker.check_analysis_template(content),
    })


@app.route("/api/dataset/<name>/kernel")
def api_detect_kernel(name):
    kp = engine.detect_kernel_path(name)
    sha = engine.get_kernel_sha256(kp) if kp else None
    return jsonify({"kernel_path": kp, "sha256": sha})


@app.route("/api/dataset/<name>/locator")
def api_locator(name):
    """Return locator cache as JSON table for the viewer."""
    if ".." in name:
        abort(400)
    kernel_sha = request.args.get("kernel_sha", "").strip()
    try:
        if kernel_sha:
            p = engine.get_metadata_cache_csv_path(name, kernel_sha)
            if not p.exists():
                return jsonify({"error": "No metadata locator cache for this dataset/kernel."}), 404
            df = engine.load_metadata_cache(name, kernel_sha)
        else:
            if not engine.locator_cache_exists(name):
                return jsonify({"error": "No locator cache for this dataset."}), 404
            df = engine.load_locator_cache(name)
        return jsonify(engine.locator_to_table_data(df))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/dataset/<name>/cache")
def api_cache_info(name):
    exists = engine.locator_cache_exists(name)
    info = {"exists": exists}
    if exists:
        try:
            import pandas as pd
            df = engine.load_locator_cache(name)
            ok, missing = engine.check_locator_paths(df)
            info["row_count"] = len(df)
            info["paths_ok"] = ok
            info["missing_count"] = len(missing)
            info["missing_sample"] = missing[:3]
        except Exception as e:
            info["error"] = str(e)
    return jsonify(info)


@app.route("/api/dataset/<name>/cache", methods=["DELETE"])
def api_delete_cache(name):
    p = engine.get_locator_cache_path(name)
    if p.exists():
        p.unlink()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — scan job
# ---------------------------------------------------------------------------

@app.route("/api/scan/start", methods=["POST"])
def api_scan_start():
    data = request.get_json(silent=True) or {}
    datasets = data.get("datasets", [])
    mode = data.get("mode", "full")  # "full" or "sampled"
    sampled_indices_map = data.get("sampled_indices_map", {})  # dataset → [indices]
    kernel_overrides = data.get("kernel_overrides", {})  # dataset → kernel_path

    if not datasets:
        return jsonify({"error": "No datasets selected"}), 400

    invalid_templates = _invalid_template_map(datasets)
    if invalid_templates:
        return jsonify({
            "error": "Selected datasets have structural template errors. Fix the template before running scans.",
            "template_errors": invalid_templates,
        }), 400

    cfg = engine.load_machine_config()
    dataset_roots = cfg.get("dataset_roots", [])
    eegunity_path = cfg.get("eegunity_path", "")
    num_workers = int(cfg.get("num_workers", 1))

    if not dataset_roots:
        return jsonify({"error": "No dataset directories configured. Open Settings."}), 400

    jid = _new_job()

    def _run():
        results = {}
        total = len(datasets)
        # Shared stdout capture list for this job
        job_stdout: list = []
        _update_job(jid, stdout_lines=job_stdout)

        for i, ds_name in enumerate(datasets):
            base_pct = int(i / total * 100)
            _update_job(jid, status="running", message=f"[{i+1}/{total}] {ds_name}")

            def _cb(step, pct, _ds=ds_name, _base=base_pct, _total=total):
                abs_pct = _base + int(pct / _total)
                _update_job(jid, progress=abs_pct, message=f"[{i+1}/{total}] {_ds}: {step}")

            try:
                kernel_path = kernel_overrides.get(ds_name) or engine.detect_kernel_path(ds_name)
                # kernel_path may be None — that means use default EEGUnity parser

                sampled_requested = mode == "sampled"
                sampled_indices = sampled_indices_map.get(ds_name) if sampled_requested else None
                if sampled_requested and sampled_indices is None:
                    results[ds_name] = {
                        "error": 'AI Quick Run requires planned sample indices. Click "Get Sample" first.',
                    }
                    continue
                sampled = sampled_indices is not None
                kernel_sha = engine.get_kernel_sha256(kernel_path or "")
                eegu_ver = engine.get_eegunity_version(eegunity_path)
                sampled_total_n = 0

                if sampled and engine.locator_cache_exists(ds_name):
                    try:
                        sampled_total_n = len(engine.load_locator_cache(ds_name))
                    except Exception:
                        sampled_total_n = 0

                misc_channel_names = []
                if sampled:
                    df, misc_channel_names = engine.run_full_scan(
                        ds_name, dataset_roots, kernel_path, eegunity_path,
                        progress_cb=_cb,
                        stdout_lines=job_stdout,
                        sampled_indices=sampled_indices,
                        num_workers=num_workers,
                        persist_base_cache=False,
                        persist_metadata_cache=False,
                        kernel_sha256=kernel_sha,
                        eegunity_version=eegu_ver,
                    )
                    cache_source = "live_sampled_scan"
                elif (
                    not data.get("force_rescan")
                    and engine.metadata_cache_exists(ds_name, kernel_sha, eegu_ver)
                ):
                    df = engine.load_metadata_cache(ds_name, kernel_sha)
                    if not engine.locator_cache_exists(ds_name):
                        engine.save_locator_cache(ds_name, df)
                    _cb("Loaded metadata cache", 80)
                    cache_source = "metadata_cache"
                else:
                    df, misc_channel_names = engine.run_full_scan(
                        ds_name, dataset_roots, kernel_path, eegunity_path,
                        progress_cb=_cb,
                        stdout_lines=job_stdout,
                        sampled_indices=None,
                        num_workers=num_workers,
                        persist_base_cache=True,
                        persist_metadata_cache=True,
                        kernel_sha256=kernel_sha,
                        eegunity_version=eegu_ver,
                    )
                    cache_source = "live_full_scan"

                # Extract structured results
                event_counts = engine.extract_event_stats(df)
                subject_info = engine.extract_subject_info(df)
                total_n = sampled_total_n if sampled else len(df)
                if total_n <= 0:
                    total_n = len(df)
                sampled_n = len(df) if sampled else total_n

                scan_result = {
                    "kernel_path": kernel_path,
                    "kernel_sha256": kernel_sha,
                    "eegunity_version": eegu_ver,
                    "scan_type": "sampled" if sampled else "full",
                    "sampled": sampled and sampled_indices is not None,
                    "sampled_n": sampled_n,
                    "total_n": total_n,
                    "cache_source": cache_source,
                    "event_counts": event_counts,
                    "subject_info": subject_info,
                    "misc_channel_names": misc_channel_names,
                }

                # Compute diff
                analysis_path = BIDS_ROOT / ds_name / "analysis.md"
                if analysis_path.exists():
                    old_content = analysis_path.read_text(encoding="utf-8", errors="replace")
                else:
                    old_content = ""
                new_content, diffs = engine.merge_scan_results(old_content, scan_result)

                results[ds_name] = {
                    "ok": True,
                    "scan_result": scan_result,
                    "old_content": old_content,
                    "new_content": new_content,
                    "diffs": diffs,
                    "event_counts": event_counts,
                    "subject_info": subject_info,
                }
                if sampled:
                    results[ds_name]["locator_preview"] = engine.locator_to_table_data(df)
                _cb("Done", 100)

            except Exception as e:
                import traceback
                results[ds_name] = {"error": str(e), "traceback": traceback.format_exc()}

        _update_job(jid, status="done", progress=100, message="All done", result=results)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"job_id": jid})


@app.route("/api/scan/status/<jid>")
def api_scan_status(jid):
    with _jobs_lock:
        job = _jobs.get(jid)
    if not job:
        abort(404)
    # Return only the last 3 log lines — frontend replaces (not appends)
    payload = dict(job)
    payload["stdout_lines"] = list(job["stdout_lines"])[-3:]
    return jsonify(payload)


# ---------------------------------------------------------------------------
# Routes — commit (write to analysis.md)
# ---------------------------------------------------------------------------

@app.route("/api/scan/commit", methods=["POST"])
def api_scan_commit():
    data = request.get_json(silent=True) or {}
    commits = data.get("commits", [])  # [{dataset, new_content}]
    written = []
    errors = []
    transitions = []
    for item in commits:
        ds = item.get("dataset")
        content = item.get("new_content")
        if not ds or content is None:
            errors.append({"dataset": ds, "error": "missing fields"})
            continue
        check = template_checker.check_analysis_template(content)
        if not check.get("ok"):
            errors.append({
                "dataset": ds,
                "error": "Template validation failed",
                "template_errors": check.get("errors", []),
            })
            continue
        p = BIDS_ROOT / ds / "analysis.md"
        if not p.exists():
            errors.append({"dataset": ds, "error": "analysis.md not found"})
            continue
        try:
            content, did_transition = engine.apply_status_transition(content)
            if did_transition:
                transitions.append(ds)
            p.write_text(content, encoding="utf-8")
            written.append(ds)
        except Exception as e:
            errors.append({"dataset": ds, "error": str(e)})
    return jsonify({"written": written, "errors": errors, "transitions": transitions})


# ---------------------------------------------------------------------------
# Routes — LLM (sampling recommendation + proxy)
# ---------------------------------------------------------------------------

@app.route("/api/llm/sample", methods=["POST"])
def api_llm_sample():
    """Plan quick-run samples with local grouping, optionally refined by LLM."""
    data = request.get_json(silent=True) or {}
    dataset_name = data.get("dataset")
    if not dataset_name:
        return jsonify({"error": "dataset required"}), 400

    if not engine.locator_cache_exists(dataset_name):
        return jsonify({"error": "No locator cache. Run a full scan first or create locator."}), 400

    max_sample = int(data.get("max_sample", 10))

    df = engine.load_locator_cache(dataset_name)
    plan = engine.prepare_sampling_plan(dataset_name, df, max_sample=max_sample)

    if plan["strategy"] == "local":
        return jsonify({
            "prompt": "",
            "sampled_indices": plan["sampled_indices"],
            "groups_covered": plan["groups_covered"],
            "reason": plan["reason"],
            "total": len(df),
            "strategy": "local",
        })

    prompt = engine.build_sampling_prompt(dataset_name, plan, max_sample=max_sample)

    # Proxy to LLM
    cfg = _load_llm_config()
    if not cfg.get("url"):
        return jsonify({
            "prompt": prompt,
            "sampled_indices": plan["sampled_indices"],
            "groups_covered": plan["groups_covered"],
            "reason": plan["reason"] + " LLM not configured, so the local fallback was used.",
            "total": len(df),
            "strategy": "local_fallback",
        })

    messages = [
        {"role": "system", "content": "You are a helpful assistant that returns JSON only."},
        {"role": "user", "content": prompt},
    ]
    resp = _call_llm(cfg, messages)
    if "error" in resp:
        return jsonify({
            "prompt": prompt,
            "sampled_indices": plan["sampled_indices"],
            "groups_covered": plan["groups_covered"],
            "reason": plan["reason"] + f" LLM request failed, so the local fallback was used. ({resp['error']})",
            "total": len(df),
            "strategy": "local_fallback",
        })

    # Try to parse JSON from response
    try:
        text = resp["choices"][0]["message"]["content"]
        # Strip markdown code fences if present
        text = re.sub(r"^```[a-z]*\n?", "", text.strip())
        text = re.sub(r"\n?```$", "", text.strip())
        parsed = json.loads(text)
        return jsonify({
            "prompt": prompt,
            "sampled_indices": parsed.get("sampled_indices", []),
            "groups_covered": parsed.get("groups_covered", []),
            "reason": parsed.get("reason", ""),
            "total": len(df),
            "strategy": "llm",
        })
    except Exception as e:
        return jsonify({
            "prompt": prompt,
            "sampled_indices": plan["sampled_indices"],
            "groups_covered": plan["groups_covered"],
            "reason": plan["reason"] + f" LLM response could not be parsed, so the local fallback was used. ({e})",
            "total": len(df),
            "strategy": "local_fallback",
        })


@app.route("/api/llm/call", methods=["POST"])
def api_llm_call():
    """Generic LLM proxy (reuses main app config)."""
    cfg = _load_llm_config()
    if not cfg.get("url"):
        return jsonify({"error": "LLM not configured. Open Settings in main app."}), 400
    body = request.get_json(silent=True) or {}
    resp = _call_llm(cfg, body.get("messages", []))
    return jsonify(resp)


def _load_llm_config() -> dict:
    return engine.load_llm_config()


def _call_llm(cfg: dict, messages: list) -> dict:
    base_url = cfg.get("url", "").rstrip("/")
    key = cfg.get("key", "")
    model = cfg.get("model", "")
    proxy = cfg.get("proxy", "").strip()

    body = {"model": model, "messages": messages}
    endpoint = f"{base_url}/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}

    try:
        import requests as _req
        proxies = {"http": proxy, "https": proxy} if proxy else None
        r = _req.post(endpoint, headers=headers, json=body, timeout=60, proxies=proxies)
        r.raise_for_status()
        return r.json()
    except ImportError:
        import urllib.request
        req_data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    print("app_scan running at http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001, debug=False)
