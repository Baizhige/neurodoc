#!/usr/bin/env python3
"""
EEG Audit Tool - Flask server
Run: python app/server.py
Then open http://127.0.0.1:5000
"""

import json
import re
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    _HAS_REQUESTS = False

APP_DIR = Path(__file__).parent
BASE_DIR = APP_DIR.parent
CONFIG_FILE = APP_DIR / "config.json"
RULEBOOK_FILE = APP_DIR / "rulebook.md"
EXCLUDE_DIRS = {"Script", "app"}
EXCLUDE_NAME_RE = re.compile(r"\.(py|pdf|md|txt|json|csv)$", re.IGNORECASE)

app = Flask(__name__, static_folder=str(APP_DIR))


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


def _list_datasets():
    result = []
    for entry in sorted(BASE_DIR.iterdir()):
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
        result.append({"name": entry.name, "category": category or "Unknown", "status": status or "unknown"})
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
    path = BASE_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    content = path.read_text(encoding="utf-8", errors="replace")
    return jsonify({"name": name, "content": content})


@app.route("/api/dataset/<name>", methods=["PUT"])
def api_put_dataset(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    path = BASE_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    data = request.get_json(silent=True)
    if not data or "content" not in data:
        abort(400)
    path.write_text(data["content"], encoding="utf-8")
    return jsonify({"ok": True})


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
            cfg = {"url": "", "key": "", "model": "", "proxy": ""}
        return jsonify(cfg)
    data = request.get_json(silent=True) or {}
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify({"ok": True})


@app.route("/api/llm", methods=["POST"])
def api_llm():
    cfg = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    base_url = cfg.get("url", "").rstrip("/")
    key = cfg.get("key", "")
    model = cfg.get("model", "")
    proxy = cfg.get("proxy", "").strip()
    if not base_url:
        return jsonify({"error": "LLM URL not configured. Open Settings to configure."}), 400

    body = request.get_json(silent=True) or {}
    body["model"] = model
    # remove stream flag — some providers reject it
    body.pop("stream", None)

    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }

    if _HAS_REQUESTS:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            resp = _requests.post(endpoint, headers=headers, json=body,
                                  timeout=90, proxies=proxies)
            resp.raise_for_status()
            return jsonify(resp.json())
        except _requests.HTTPError as e:
            return jsonify({"error": f"HTTP {e.response.status_code}: {e.response.text}"}), 502
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # fallback: urllib (no proxy support)
        import urllib.request, urllib.error
        req_data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return jsonify(json.loads(r.read().decode("utf-8")))
        except urllib.error.HTTPError as e:
            return jsonify({"error": f"HTTP {e.code}: {e.read().decode('utf-8','replace')}"}), 502
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("EEG Audit Tool running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
