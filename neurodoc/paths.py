"""Shared repository paths for NeuroDoc and NeuroAudit."""
from __future__ import annotations

from pathlib import Path


NEURODOC_DIR = Path(__file__).resolve().parent
ROOT_DIR = NEURODOC_DIR.parent
NEUROAUDIT_DIR = ROOT_DIR / "neuroaudit"
APP_DIR = NEUROAUDIT_DIR
DATASET_DOCUMENT_DIR = ROOT_DIR / "dataset_document"
SCRIPT_DIR = ROOT_DIR / "Script"
RUNTIME_DIR = SCRIPT_DIR / "neurodoc_runtime"

KERNELS_DIR = NEURODOC_DIR / "kernels"
RULEBOOK_DIR = NEURODOC_DIR / "rulebook"

LOCATOR_CACHE_DIR = RUNTIME_DIR / "locator_cache"
MACHINE_CONFIG_DIR = RUNTIME_DIR / "machine_config"
PROGRESS_DIR = RUNTIME_DIR / "progress"
EVIDENCE_CACHE_DIR = RUNTIME_DIR / "evidence_cache"
LOGS_DIR = RUNTIME_DIR / "logs"
SANDBOX_DIR = RUNTIME_DIR / "sandbox"
