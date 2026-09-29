# NeuroDoc

`neurodoc/` is the automated generation engine for EEG dataset kernel files and `analysis.md` documents. It drives a three-phase LLM pipeline: **(1) Build Context** from local dataset evidence and academic sources, **(2) Task Synthesis** to propose ML task candidates and derive kernel requirements, and **(3) Kernel Coding** to generate and iteratively validate the data-loading kernel in a sandbox, then reconcile synthesized tasks against real scan results.

---

## Directory Structure

```
neurodoc/
|-- README.md                   # This file
|-- api.py                      # Stable public interface for NeuroAudit (only allowed external import point)
|-- paths.py                    # Global path constants (NEURODOC_DIR, RUNTIME_DIR, etc.)
|
|-- generate.py                 # CLI: parallel generation of kernel + analysis.md for multiple datasets
|-- detect.py                   # CLI: semantic rule validation against analysis.md and kernel files
|-- full_scan.py                # CLI: re-scan with existing kernel and refresh analysis.md
|-- upgrade.py                  # CLI: incremental kernel/document updates via [to_agent:...] tags
|
|-- llm_adapter.py              # LLM config normalization + HTTP retry adapter (Anthropic / OpenAI)
|-- scan_engine.py              # EEGUnity scan core: machine config, locator cache, scan execution,
|                               #   analysis.md merge logic, sampling plan
|
|-- pipeline/                   # Per-phase implementation of the generation pipeline
|   |-- runner.py               # Pipeline orchestrator: 3-phase framework with 10 internal steps
|   |-- budget.py               # LLM call budget tracking (Budget / BudgetExhausted)
|   |-- context_builder.py      # Phase 1 (local evidence): load kernel, BIDS sidecars, EEG header
|   |-- ref_analyzer.py         # Phase 1 (academic sources): LLM extracts info from papers/docs
|   |-- task_synthesizer.py     # Phase 2 (entry): LLM feasibility judgment
|   |-- scan_bridge.py          # Phase 1 + Phase 3: invoke scan_engine to run EEGUnity scan
|   |-- event_annotator.py      # Phase 1 (local evidence): isolated event semantic annotation
|   |-- task_synthesizer_v2.py  # Phase 2: propose task candidates + list kernel requirements
|   |-- kernel_builder.py       # Phase 3 (coding loop): generate kernel.py + sandbox validation
|   |-- reconcile.py            # Phase 3 (reconcile): prune hallucinated tasks after scan
|   |-- doc_writer.py           # Phase 3: write final analysis.md
|   `-- file_scan_result_builder.py  # Build File Scan Result section from scan output
|
|-- kernels/                    # Version-controlled kernel implementations (400+ datasets)
|   |-- KERNEL_RULEBOOK.md      # Kernel writing standards (detailed specification)
|   |-- bids.py                 # Generic BIDS parser (fallback)
|   |-- openneuro.py            # Generic OpenNeuro parser (fallback)
|   |-- openneuro_ds*.py        # OpenNeuro dataset-specific kernels (200+)
|   |-- openneuro_specific/     # Specialized kernel subdirectory for complex cases
|   |-- bcic_*.py               # BCI Competition datasets
|   |-- physionet_*.py          # PhysioNet datasets
|   |-- tuh_eeg_*.py            # TUH EEG datasets
|   |-- figshare_*.py           # Figshare datasets
|   |-- zenodo_*.py             # Zenodo datasets
|   `-- skills/                 # LLM prompt templates for kernel synthesis (SKILL_*.md)
|
|-- rulebook/
|   `-- semantic_rules.yaml     # Semantic validation rules used by detect.py
|
|-- skills/                     # Agent skill definitions for Claude Code and Codex
|   |-- CLAUDE.md               # Dialog-driven skill loaded via @neurodoc/skills/CLAUDE.md
|   |-- AGENTS.md               # Codex / OpenAI Agents equivalent
|   |-- install.py              # One-command installer: python -m neurodoc.skills.install
|   `-- README.md               # Installation guide
|
|-- dataset_api/                # PyTorch Dataset wrappers (read EEGUnity-generated HDF5)
|   |-- base.py                 # BaseHDF5Dataset: lazy file handles, epoch truncation/padding
|   |-- factory.py              # build_dataset_from_task(): dispatch Dataset by label_route
|   |-- event_dataset.py        # EventDataset (label_route = event)
|   |-- misc_dataset.py         # MISCDataset (label_route = misc)
|   |-- info_dataset.py         # InfoDataset (label_route = info)
|   `-- tests/                  # Dataset unit tests
|
`-- tools/
    |-- migrate_to_v3.py        # Document version migration tool (upgrade to v3 format)
    `-- __init__.py
```

---

## Runtime Directory (not version-controlled)

Machine-specific runtime state is stored under `Script/neurodoc_runtime/` (gitignored):

```
Script/neurodoc_runtime/
|-- machine_config/     # Per-machine JSON config (LLM keys, dataset roots, EEGUnity path)
|-- locator_cache/      # EEGUnity locator CSV cache (subdirectory per machine ID)
|-- progress/           # Per-dataset pipeline progress JSON (supports resume from checkpoint)
|-- evidence_cache/     # LLM cache for event annotation
|-- logs/               # Per-dataset run logs
`-- sandbox/            # Temporary directory for kernel code execution
```

---

## Inputs and Outputs

| Type | Path |
|------|------|
| Raw EEG data | Located in `dataset_roots` from `machine_config` |
| Reference materials | PDF/TXT files under `dataset_document/<dataset>/` |
| Existing analysis.md | `dataset_document/<dataset>/analysis.md` |
| **Output: kernel** | `neurodoc/kernels/<dataset>.py` |
| **Output: analysis.md** | `dataset_document/<dataset>/analysis.md` |

---

## CLI Entry Points

### `generate.py` - Full pipeline (generate kernel + analysis.md)

```bash
# Single dataset
python -m neurodoc.generate --dataset openneuro_ds001784

# Multiple datasets (parallel, default 4 workers)
python -m neurodoc.generate --dataset openneuro_ds001784 openneuro_ds002578 --workers 4

# Ignore existing progress and restart from scratch
python -m neurodoc.generate --dataset openneuro_ds001784 --fresh

# Specify machine_config
python -m neurodoc.generate --dataset openneuro_ds001784 --config path/to/config.json
```

Prints a summary table on completion: `DATASET | STATUS | PHASE | BUDGET | KERNEL | TIME`.
Supports Ctrl-C graceful pause (progress saved, resumable).

### `detect.py` - Semantic rule validation

```bash
# Validate single dataset
python -m neurodoc.detect --dataset openneuro_ds001784

# Validate all datasets
python -m neurodoc.detect --all

# Show only error severity
python -m neurodoc.detect --all --severity error

# Use custom rulebook
python -m neurodoc.detect --dataset openneuro_ds001784 --rulebook custom.yaml
```

### `full_scan.py` - Re-scan with existing kernel (no LLM calls)

```bash
python -m neurodoc.full_scan --dataset openneuro_ds005505
python -m neurodoc.full_scan --dataset openneuro_ds005505 --workers 4
```

Refreshes only the `File Scan Result` and `Kernel Responsibilities` sections; task definitions are not changed.

### `upgrade.py` - Incremental updates via `[to_agent: ...]` tags

```bash
python -m neurodoc.upgrade --dataset openneuro_ds001784
```

Reads `[to_agent: ...]` directives in analysis.md and applies targeted LLM modifications to the kernel or document.

### `tools/migrate_to_v3.py` - Document format migration

```bash
python -m neurodoc.tools.migrate_to_v3 --all --dry-run
python -m neurodoc.tools.migrate_to_v3 --dataset openneuro_ds001784
```

---

## Generation Pipeline

`generate.py` drives a three-phase pipeline implemented in `pipeline/runner.py`. All phases execute sequentially with pause-and-resume support via a progress checkpoint.

### Phase 1 — Build Context

Collects all available evidence about the dataset before any task or kernel decisions are made. Evidence comes from two sources:

**From dataset local evidence** — scan the raw data files, collect event IDs and channel metadata:

| Step | Phase key | Module | Description |
|---|---|---|---|
| 1.1 | `context` | `context_builder.py` | Load existing kernel, BIDS sidecars, EEG file headers, and directory tree |
| 1.2 | `pre_scan` | `scan_bridge.py` | Pre-scan with existing or default kernel to collect event ID preview |
| 1.3 | `event_annotation` | `event_annotator.py` | LLM independently annotates the semantic meaning of each observed event ID |

**From academic sources** — extract structured information from papers and documentation:

| Step | Phase key | Module | Description |
|---|---|---|---|
| 1.4 | `ref_analysis` | `ref_analyzer.py` | LLM extracts experiment design, event descriptions, and subject info from PDFs/docs |

---

### Phase 2 — Task Synthesis

Using the accumulated context, the LLM proposes ML task candidates and derives the kernel requirements needed to support them:

| Step | Phase key | Module | Description |
|---|---|---|---|
| 2.1 | `feasibility` | `task_synthesizer.py` | LLM judges dataset feasibility; writes failure doc and exits if infeasible |
| 2.2 | `task_synthesis` | `task_synthesizer_v2.py` | LLM proposes task candidates and lists kernel requirements (aggregate → fill → gate → repair) |

---

### Phase 3 — Kernel Coding

A kernel Python file is generated and validated in a sandbox environment, then synthesized tasks are reconciled against real scan results:

| Step | Phase key | Module | Description |
|---|---|---|---|
| 3.1 | `kernel_loop` | `kernel_builder.py` | LLM generates `kernel.py`; iterative static + runtime validation in sandbox (up to 9 versions) |
| 3.2 | `scan` | `scan_bridge.py` | Final EEGUnity scan with the new kernel |
| 3.3 | `reconcile` | `reconcile.py` | Reconcile synthesized tasks against scan results; prune hallucinated tasks |
| 3.4 | `doc_write` | `doc_writer.py` | Write final `analysis.md` |

---

**Budget mechanism**: Each LLM call consumes 1 budget unit (default total: 500). When exhausted, `BudgetExhausted` is raised; partial output is written and progress is saved for resume.

---

## analysis.md Document Structure

Each dataset's analysis.md contains the following top-level sections (fixed order, validated by `detect.py`'s `section_order` rule):

```markdown
## Paradigm           -- Experiment design, subjects, event semantic description
## File Scan Result   -- Scan output: event structure table, Info table, MISC Label Summary
## Tasks              -- ML task definitions (directly consumable by dataset_api)
## Data Quality Notes -- Data quality issues (for manual review)
## Kernel Responsibilities -- Kernel capability declaration (auto-maintained)
```

The document header metadata includes `Status` (`wait_manual_review` / `completed` / etc.) and `Kernel SHA256` (used to detect whether the kernel has been updated).

---

## dataset_api - PyTorch Dataset Wrappers

`dataset_api/` provides interfaces for building PyTorch Datasets directly from HDF5 (EEGUnity v2.0/v2.1 format).

```python
from neurodoc.dataset_api.factory import build_dataset_from_task

dataset = build_dataset_from_task(
    task=task_dict,     # parsed from analysis.md Tasks section
    h5_path="data.h5",
    dry_run=False,
)
# dataset[i] -> (data: Tensor, label: Tensor, meta: dict)
```

**Dispatch rules (label_route x task_type):**

| label_route | task_type | Class | Label source |
|---|---|---|---|
| `event` | `classification` | `EventDataset` | `/epoch_meta/event_code` -> `events_map` -> int y |
| `event` | `regression` | `EventDataset` | `/epoch_meta/event_code` -> float value |
| `misc` | `classification` | `MISCDataset` | `/misc_meta/<channel>` -> kernel-encoded int y (torch.long) |
| `misc` | `regression` | `MISCDataset` | `/misc_meta/<channel>` -> float value |
| `info` | `classification` | `InfoDataset` | `/source_meta/<group>/attrs[field]` -> `info_map` -> int y |
| `info` | `regression` | `InfoDataset` | `/source_meta/<group>/attrs[field]` -> float |

---

## Kernel Specification

Each kernel is a Python module exposing a module-level `KERNEL` object compatible with EEGUnity's `UnifiedDataset.eeg_parser` interface. Core responsibilities:

1. **Channel restoration**: Convert generic channel names like `EEG-0` back to correct names (e.g., `FC3`)
2. **Metadata writing**: Write age, sex, device info into `raw.info["description"]` (JSON format)
3. **Label standardization**:
   - **raw meta**: Direct mapping from original event codes to readable labels
   - **super meta**: Semantically derived labels (must match task declarations in analysis.md)
   - Multi-paradigm datasets: distinguish with paradigm ID prefix (e.g., `CLA: left hand MI`)

See [`kernels/KERNEL_RULEBOOK.md`](kernels/KERNEL_RULEBOOK.md) for full specification.

---

## Semantic Validation Rules (detect.py)

`detect.py` loads rules from `rulebook/semantic_rules.yaml`, supporting four rule types:

- `pattern`: regex match
- `section_exists`: require a section to be present
- `field_value`: extract a field value and validate against an allowed set
- `cross_check`: custom function (20+, registered with `@_cc` decorator)

**Key cross-checks:**

| Function | Check |
|---|---|
| `section_order` | Top-level sections appear in the required order |
| `super_meta_consistency` | Task Meta Level matches Super Meta Required |
| `target_events_exist` | Event IDs in Target Definition appear in Event Structure |
| `classification_y_zero_indexed_sequential` | Classification task y values form `{0, 1, ..., N-1}` |
| `task_dataset_dispatchable` | All tasks pass `dataset_api.factory` dry_run |
| `kernel_sha256_matches` | SHA256 recorded in document matches current kernel file |
| `classical_task_evidence` | Every Classical Task has a non-empty Evidence field |

Violation output format:
```python
{"dataset": str, "rule_id": str, "severity": "error|warning|info",
 "target": "analysis_md|kernel", "desc": str, "detail": str}
```

---

## scan_engine.py Responsibilities

`scan_engine.py` is a multi-purpose module currently handling:

- **Machine identity**: `get_machine_id()` generates a 12-char hash from hostname
- **Machine config**: `load_machine_config()` / `save_machine_config()` (read/write `machine_config/<hash>.json`)
- **Dataset path lookup**: `find_dataset_path()` (supports stripping `openneuro_` prefix)
- **Kernel path detection**: `detect_kernel_path()` (priority: dataset-specific > generic fallback)
- **Kernel SHA256**: `get_kernel_sha256()` (cross-platform CRLF-normalized hash)
- **Locator cache**: CSV format, layered by machine ID and kernel SHA256
- **EEGUnity scan execution**: `run_full_scan()`, supports full and sampled scans
- **Subject info extraction**: parse age/sex from `raw.info["description"]` JSON
- **MISC channel detection**: `_extract_misc_channels()`, probes multiple files until stable
- **analysis.md merge**: `merge_scan_results()`, updates Event Structure / Info / MISC tables
- **Dataset listing**: `list_datasets()`, scans `dataset_document/` and returns status summary
- **Sampling plan**: `prepare_sampling_plan()` / `build_sampling_prompt()`, for LLM-assisted sampling

---

## llm_adapter.py - LLM Adapter

Supports both Anthropic and OpenAI-compatible interfaces with a unified config format:

```python
from neurodoc.llm_adapter import resolve_llm_config, post_llm_json, call_llm_text

cfg = resolve_llm_config({
    "ANTHROPIC_BASE_URL": "https://...",  # or BASE_URL (OpenAI)
    "key": "sk-...",
    "model": "claude-opus-4-7",
})
# cfg["provider"] = "anthropic" | "openai"
# cfg["active_url"] = final request URL
```

**Retry policy**: up to 5 retries, exponential backoff on 429/5xx (5s * 2^n, max 120s), honors `Retry-After` header.

---

## NeuroAudit Integration Interface

The audit UI (`neuroaudit/`) **may only** import from:

```python
import neurodoc.api       # check_analysis_text, load_rules, call_llm_text, ...
import neurodoc.paths     # NEURODOC_DIR, DATASET_DOCUMENT_DIR, RUNTIME_DIR, ...
import neurodoc.scan_engine  # list_datasets, run_full_scan, merge_scan_results, ...
```

Direct imports from internal `pipeline/` modules are not permitted.

`neurodoc.api` currently exposes:

```python
check_analysis_text(text, dataset, kernel_text, severity_filter, rules)
load_rules(rulebook_path)
call_llm_text(config, messages)
post_llm_json(config, messages)
anthropic_to_openai_response(response)
resolve_llm_config(config)
```

---

## Agent Skill System (Claude Code / Codex)

`neurodoc/skills/` provides dialog-driven agent skills that let users process datasets
without memorizing any commands. Install once per repo:

```bash
python -m neurodoc.skills.install
```

This creates (or updates) a root `CLAUDE.md` and `AGENTS.md`:
- **Claude Code** reads `CLAUDE.md` → auto-loads `@neurodoc/skills/CLAUDE.md`
- **Codex / OpenAI Agents** reads `AGENTS.md` → inline skill content

After installation, open a new session and say:
> "I want to process dataset openneuro_ds001784"

The agent guides through the full workflow: machine config setup → generate → scan →
validate → fix errors → done. See [`skills/README.md`](skills/README.md) for details.

---

## machine_config JSON Format

```json
{
  "dataset_roots": ["/path/to/eeg_data"],
  "eegunity_path": "/path/to/eegunity",
  "python_env": "python3",
  "num_workers": 4,
  "budget": 500,
  "model": "claude-opus-4-7",
  "BASE_URL": "",
  "ANTHROPIC_BASE_URL": "https://...",
  "key": "sk-ant-..."
}
```

File name format: `<machine_id>.json` (machine_id = MD5(hostname + MAC)[:12]).
