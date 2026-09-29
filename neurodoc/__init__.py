"""NeuroDoc package."""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "anthropic_to_openai_response",
    "call_llm_text",
    "check_analysis_text",
    "load_rules",
    "post_llm_json",
    "resolve_llm_config",
]

if TYPE_CHECKING:
    from .api import (
        anthropic_to_openai_response,
        call_llm_text,
        check_analysis_text,
        load_rules,
        post_llm_json,
        resolve_llm_config,
    )


def __getattr__(name: str):
    if name in __all__:
        return getattr(import_module(".api", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
