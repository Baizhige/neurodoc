"""auto_eeg Flask server — fully automated EEG kernel + analysis.md generation."""
from __future__ import annotations

import hashlib
import json
import platform
import queue
import re
import sys
import threading
import uuid
from pathlib import Path

from flask import Flask, Response, jsonify, request, stream_with_context

# Ensure scan_engine is importable
APP_KERNEL_DIR = Path(__file__).parent.parent / "app_kernel"
if str(APP_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(APP_KERNEL_DIR))

BIDS_ROOT = Path(__file__).parent.parent
AUTO_EEG_DIR = Path(__file__).parent
CONFIG_DIR = AUTO_EEG_DIR / "machine_config"

EXCLUDE_DIRS = {"Script", "app", "app_kernel", "auto_eeg", ".git", ".claude", "logs"}

app = Flask(__name__, static_folder=None)


# ---------------------------------------------------------------------------
# Machine config
# ---------------------------------------------------------------------------

def _machine_id() -> str:
    raw = f"{platform.node()}_{uuid.getnode()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _config_path() -> Path:
    return CONFIG_DIR / f"{_machine_id()}.json"


def _load_config() -> dict:
    p = _config_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "url": "",
        "key": "",
        "model": "",
        "proxy": "",
        "python_env": sys.executable,
        "eegunity_path": "",
        "dataset_roots": [],
        "num_workers": 2,
        "budget": 500,
    }


def _save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _config_path().write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Active jobs
# ---------------------------------------------------------------------------

_jobs: dict[str, dict] = {}  # dataset_name -> {thread, log_queue, pause_event, status}


def _get_job(dataset_name: str) -> dict:
    return _jobs.get(dataset_name, {})


# ---------------------------------------------------------------------------
# Dataset listing
# ---------------------------------------------------------------------------

def _list_datasets() -> list[dict]:
    result = []
    for entry in sorted(BIDS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        analysis = entry / "analysis.md"
        if not analysis.exists():
            continue
        try:
            content = analysis.read_text(encoding="utf-8", errors="replace")
        except Exception:
            content = ""
        status_m = re.search(r"\*\*Status\*\*:\s*(\S+)", content)
        status = status_m.group(1) if status_m else "unknown"
        has_kernel = (APP_KERNEL_DIR / "kernels" / f"{entry.name}.py").exists()
        has_refs = (entry / "references").is_dir() and any((entry / "references").iterdir())

        from pipeline.runner import load_progress
        progress = load_progress(entry.name)
        progress_phase = progress.get("phase", "")
        progress_status = progress.get("status", "")

        job = _get_job(entry.name)
        running = job.get("thread") is not None and job["thread"].is_alive()

        result.append({
            "name": entry.name,
            "status": status,
            "has_kernel": has_kernel,
            "has_refs": has_refs,
            "progress_phase": progress_phase,
            "progress_status": progress_status,
            "running": running,
        })
    return result


# ---------------------------------------------------------------------------
# Routes — static
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    html = (AUTO_EEG_DIR / "index.html").read_text(encoding="utf-8")
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# ---------------------------------------------------------------------------
# Routes — datasets
# ---------------------------------------------------------------------------

@app.route("/api/datasets")
def api_datasets():
    return jsonify(_list_datasets())


# ---------------------------------------------------------------------------
# Routes — config
# ---------------------------------------------------------------------------

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        cfg = _load_config()
        safe = {k: v for k, v in cfg.items() if k != "key"}
        safe["key_set"] = bool(cfg.get("key"))
        return jsonify(safe)
    data = request.get_json(silent=True) or {}
    cfg = _load_config()
    for field in ("url", "key", "model", "proxy", "python_env",
                  "eegunity_path", "num_workers", "budget"):
        if field in data:
            cfg[field] = data[field]
    if "dataset_roots" in data and isinstance(data["dataset_roots"], list):
        cfg["dataset_roots"] = data["dataset_roots"]
    _save_config(cfg)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — pipeline control
# ---------------------------------------------------------------------------

@app.route("/api/run/<name>", methods=["POST"])
def api_run(name: str):
    data = request.get_json(silent=True) or {}
    fresh = bool(data.get("fresh_start", False))

    job = _get_job(name)
    if job.get("thread") and job["thread"].is_alive():
        return jsonify({"error": "Already running."}), 409

    cfg = _load_config()
    log_queue: "queue.Queue[str | None]" = queue.Queue()
    pause_event = threading.Event()

    from pipeline.runner import Pipeline, clear_progress
    if fresh:
        clear_progress(name)

    pipeline = Pipeline(
        dataset_name=name,
        config=cfg,
        log_queue=log_queue,
        pause_event=pause_event,
        fresh_start=fresh,
    )

    t = threading.Thread(target=pipeline.run, daemon=True, name=f"auto_eeg_{name}")
    _jobs[name] = {
        "thread": t,
        "log_queue": log_queue,
        "pause_event": pause_event,
        "status": "running",
    }
    t.start()
    return jsonify({"ok": True, "dataset": name})


@app.route("/api/pause/<name>", methods=["POST"])
def api_pause(name: str):
    job = _get_job(name)
    if not job:
        return jsonify({"error": "No active job for this dataset."}), 404
    job["pause_event"].set()
    return jsonify({"ok": True})


@app.route("/api/resume/<name>", methods=["POST"])
def api_resume(name: str):
    """Resume a paused pipeline (same as run without fresh_start)."""
    job = _get_job(name)
    if job.get("thread") and job["thread"].is_alive():
        return jsonify({"error": "Already running."}), 409

    cfg = _load_config()
    log_queue: "queue.Queue[str | None]" = queue.Queue()
    pause_event = threading.Event()

    from pipeline.runner import Pipeline
    pipeline = Pipeline(
        dataset_name=name,
        config=cfg,
        log_queue=log_queue,
        pause_event=pause_event,
        fresh_start=False,
    )

    t = threading.Thread(target=pipeline.run, daemon=True, name=f"auto_eeg_{name}")
    _jobs[name] = {
        "thread": t,
        "log_queue": log_queue,
        "pause_event": pause_event,
        "status": "running",
    }
    t.start()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — SSE log stream
# ---------------------------------------------------------------------------

@app.route("/api/log/<name>")
def api_log(name: str):
    """Server-Sent Events stream of log lines for a running job."""

    def generate():
        job = _get_job(name)
        if not job:
            yield "data: [No active job for this dataset]\n\n"
            return

        log_queue = job["log_queue"]
        while True:
            try:
                msg = log_queue.get(timeout=30)
            except queue.Empty:
                yield "data: [heartbeat]\n\n"
                continue

            if msg is None:
                # Pipeline finished
                yield "data: __DONE__\n\n"
                # Update job status
                job["status"] = "done"
                break

            # Escape newlines for SSE
            safe_msg = msg.replace("\n", "\\n")
            yield f"data: {safe_msg}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Routes — progress / status
# ---------------------------------------------------------------------------

@app.route("/api/progress/<name>")
def api_progress(name: str):
    from pipeline.runner import load_progress
    p = load_progress(name)
    job = _get_job(name)
    running = job.get("thread") is not None and job["thread"].is_alive() if job else False
    p["running"] = running
    return jsonify(p)


@app.route("/api/analysis/<name>")
def api_analysis(name: str):
    """Return current analysis.md content."""
    path = BIDS_ROOT / name / "analysis.md"
    if not path.exists():
        return jsonify({"error": "analysis.md not found"}), 404
    return jsonify({"content": path.read_text(encoding="utf-8", errors="replace")})


@app.route("/api/kernel/<name>")
def api_kernel(name: str):
    """Return installed kernel content."""
    kernel_path = APP_KERNEL_DIR / "kernels" / f"{name}.py"
    if not kernel_path.exists():
        return jsonify({"content": "", "exists": False})
    return jsonify({"content": kernel_path.read_text(encoding="utf-8", errors="replace"), "exists": True})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5002)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    print(f"auto_eeg server starting on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
