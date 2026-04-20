"""Shared LLM config normalization and HTTP adapter utilities."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

DEFAULT_ANTHROPIC_MAX_TOKENS = 32768
_ANTHROPIC_VERSION = "2023-06-01"


def _clean_str(value: Any) -> str:
    return str(value or "").strip()


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _stringify_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, Mapping):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(p for p in parts if p)
    if isinstance(content, (dict, list)):
        return json.dumps(content, ensure_ascii=False)
    return str(content)


def resolve_llm_config(raw_config: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    cfg = dict(raw_config or {})

    base_url = _clean_str(cfg.get("BASE_URL"))
    anthropic_base_url = _clean_str(cfg.get("ANTHROPIC_BASE_URL"))
    legacy_url = _clean_str(cfg.get("url"))

    if legacy_url:
        if base_url or anthropic_base_url:
            raise ValueError(
                "Configure only one of BASE_URL or ANTHROPIC_BASE_URL. "
                "Legacy key 'url' cannot be combined with them."
            )
        base_url = legacy_url

    provided_keys = [
        key_name for key_name, value in (
            ("BASE_URL", base_url),
            ("ANTHROPIC_BASE_URL", anthropic_base_url),
        )
        if value
    ]
    if len(provided_keys) > 1:
        raise ValueError("Configure exactly one of BASE_URL or ANTHROPIC_BASE_URL, not both.")

    provider = ""
    active_url = ""
    active_url_key = ""
    if base_url:
        provider = "openai"
        active_url = base_url.rstrip("/")
        active_url_key = "BASE_URL"
    elif anthropic_base_url:
        provider = "anthropic"
        active_url = anthropic_base_url.rstrip("/")
        active_url_key = "ANTHROPIC_BASE_URL"

    return {
        "provider": provider,
        "active_url": active_url,
        "active_url_key": active_url_key,
        "BASE_URL": base_url.rstrip("/") if base_url else "",
        "ANTHROPIC_BASE_URL": anthropic_base_url.rstrip("/") if anthropic_base_url else "",
        "key": _clean_str(cfg.get("key") or cfg.get("api_key")),
        "model": _clean_str(cfg.get("model")),
        "proxy": _clean_str(cfg.get("proxy")),
        "max_tokens": _coerce_int(
            cfg.get("max_tokens", cfg.get("max_output_tokens")),
            DEFAULT_ANTHROPIC_MAX_TOKENS,
        ),
    }


def get_display_url(raw_config: Optional[Mapping[str, Any]]) -> str:
    return resolve_llm_config(raw_config).get("active_url", "")


def _normalize_anthropic_messages(messages: Iterable[Mapping[str, Any]]) -> Tuple[str, List[Dict[str, str]]]:
    system_parts: List[str] = []
    normalized: List[Dict[str, str]] = []

    for msg in messages:
        role = _clean_str(msg.get("role"))
        content = _stringify_content(msg.get("content"))
        if role == "system":
            if content:
                system_parts.append(content)
            continue
        if role not in ("user", "assistant"):
            role = "user"
        normalized.append({"role": role, "content": content})

    if not normalized:
        normalized.append({"role": "user", "content": ""})

    return "\n\n".join(p for p in system_parts if p), normalized


def build_llm_request(
    raw_config: Optional[Mapping[str, Any]],
    messages: Iterable[Mapping[str, Any]],
    extra_body: Optional[Mapping[str, Any]] = None,
) -> Tuple[Dict[str, Any], str, Dict[str, str], Dict[str, Any]]:
    cfg = resolve_llm_config(raw_config)
    if not cfg["active_url"]:
        raise ValueError("LLM URL not configured. Set BASE_URL or ANTHROPIC_BASE_URL.")

    extra = dict(extra_body or {})
    extra.pop("model", None)
    extra.pop("messages", None)
    extra.pop("stream", None)

    if cfg["provider"] == "anthropic":
        system, anthropic_messages = _normalize_anthropic_messages(messages)
        body: Dict[str, Any] = {
            "model": cfg["model"],
            "messages": anthropic_messages,
            "max_tokens": _coerce_int(extra.pop("max_tokens", None), cfg["max_tokens"]),
        }
        for key in ("temperature", "top_p", "top_k", "metadata", "stop_sequences"):
            if key in extra:
                body[key] = extra.pop(key)
        if system:
            body["system"] = system
        endpoint = f"{cfg['active_url']}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": cfg["key"],
            "anthropic-version": _ANTHROPIC_VERSION,
        }
        return cfg, endpoint, headers, body

    body = dict(extra)
    body["model"] = cfg["model"]
    body["messages"] = list(messages)
    endpoint = f"{cfg['active_url']}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['key']}",
    }
    return cfg, endpoint, headers, body


def post_llm_json(
    raw_config: Optional[Mapping[str, Any]],
    messages: Iterable[Mapping[str, Any]],
    timeout: int = 240,
    extra_body: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    cfg, endpoint, headers, body = build_llm_request(raw_config, messages, extra_body=extra_body)

    try:
        import requests  # type: ignore
    except ImportError:
        requests = None

    if requests is not None:
        proxies = {"http": cfg["proxy"], "https": cfg["proxy"]} if cfg["proxy"] else None
        resp = requests.post(endpoint, headers=headers, json=body, timeout=timeout, proxies=proxies)
        resp.raise_for_status()
        return resp.json()

    import urllib.request

    req_data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def extract_text_from_response(data: Mapping[str, Any], provider: str) -> str:
    if provider == "anthropic":
        blocks = data.get("content") or []
        texts = []
        for block in blocks:
            if isinstance(block, Mapping) and block.get("type") == "text":
                texts.append(_clean_str(block.get("text")))
        content = "\n".join(t for t in texts if t).strip()
        if not content:
            raise ValueError(f"Empty Anthropic content in response: {data}")
        return content

    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"Empty choices in response: {data}")
    content = _stringify_content((choices[0].get("message") or {}).get("content")).strip()
    if not content:
        raise ValueError(f"Null content in response: {data}")
    return content


def call_llm_text(
    raw_config: Optional[Mapping[str, Any]],
    messages: Iterable[Mapping[str, Any]],
    timeout: int = 240,
) -> str:
    cfg = resolve_llm_config(raw_config)
    data = post_llm_json(cfg, messages, timeout=timeout)
    return extract_text_from_response(data, cfg["provider"])


def anthropic_to_openai_response(data: Mapping[str, Any]) -> Dict[str, Any]:
    text = extract_text_from_response(data, "anthropic")
    usage = data.get("usage") or {}
    return {
        "id": data.get("id", ""),
        "object": "chat.completion",
        "model": data.get("model", ""),
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": text},
            "finish_reason": data.get("stop_reason", "stop"),
        }],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
    }
