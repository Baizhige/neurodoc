"""Stable public entry points consumed by NeuroAudit."""
from __future__ import annotations

from .detect import check_analysis_text, load_rules
from .llm_adapter import (
    anthropic_to_openai_response,
    call_llm_text,
    post_llm_json,
    resolve_llm_config,
)

__all__ = [
    "anthropic_to_openai_response",
    "call_llm_text",
    "check_analysis_text",
    "load_rules",
    "post_llm_json",
    "resolve_llm_config",
]
