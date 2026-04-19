# eeg_kernel_agent

Automated pipeline for generating EEG dataset kernel files and `analysis.md` documentation from BIDS datasets.

---

## Directory Structure

```
eeg_kernel_agent/
├── generate.py          # Entry point — full pipeline runner
├── detect.py            # Semantic rule checker for analysis.md / kernel files
├── scan_engine.py       # EEGUnity scan core (machine identity, locator cache, HDF5 scan)
├── upgrade.py           # Placeholder (not yet implemented)
├── pipeline/            # Modular pipeline stages
│   ├── runner.py           # Phase orchestrator with resume logic
│   ├── context_builder.py
│   ├── ref_analyzer.py
│   ├── event_annotator.py
│   ├── task_synthesizer.py    # Legacy single-call synthesis (kept for feasibility judge only)
│   ├── task_synthesizer_v2.py # Current per-ref aggregate → per-task fill → detect gate
│   ├── kernel_builder.py      # Consumes kernel_requirements JSON from v2 synthesis
│   ├── reconcile.py           # Whitelist check + 1-shot kernel patch for derived misc
│   ├── scan_bridge.py
│   ├── doc_writer.py
│   └── budget.py
├── tools/
│   └── migrate_to_v3.py # Non-LLM batch migration: pre-v3 analysis.md → v3 schema
├── rulebook/
│   └── semantic_rules.yaml  # Cross-check rule definitions consumed by detect.py
├── kernels/             # Generated kernel files (one .py per dataset)
├── progress/            # Per-dataset pipeline state JSON (resume checkpoints)
├── evidence_cache/      # Cached LLM evidence from Phase 3 event annotation
├── logs/                # Per-dataset run logs (<dataset>.log)
├── machine_config/      # Machine-specific config JSON (API key, model, paths)
├── sandbox/             # Temporary kernel testing sandbox
└── design.md            # Architecture and design notes
```

---

## Quick Start

### Prerequisites

```bash
pip install openai anthropic pyyaml fitz  # fitz = PyMuPDF for PDF parsing
```

A machine config file must exist in `machine_config/` (any `.json` file). Minimum fields:

```json
{
  "api_key": "sk-...",
  "model": "claude-opus-4-7",
  "data_root": "/path/to/BIDS/datasets"
}
```

### Generate a dataset

```bash
# Generate (or resume) a single dataset
python generate.py --dataset openneuro_ds001784

# Generate multiple datasets in parallel
python generate.py --dataset openneuro_ds001784 openneuro_ds002578 --workers 4

# Force restart from scratch (ignore existing progress)
python generate.py --dataset openneuro_ds001784 --fresh

# Use a specific machine config
python generate.py --dataset openneuro_ds001784 --config machine_config/my_machine.json
```

Output: `<BIDS_ROOT>/<dataset>/analysis.md` + `kernels/<dataset>.py`

### Check a dataset with detect.py

```bash
# Check one dataset
python detect.py --dataset openneuro_ds001784

# Check all datasets
python detect.py --all

# Filter to errors only
python detect.py --all --severity error

# Use a custom rulebook
python detect.py --dataset openneuro_ds001784 --rulebook rulebook/semantic_rules.yaml
```

Output: per-dataset violation report + summary table printed to stdout.

---

## Pipeline Flow (`generate.py`)

`generate.py` loads a machine config, resolves the list of datasets, then spawns one thread per dataset (up to `--workers`). Each dataset runs through `pipeline/runner.py`.

### Phases (in order)

| Phase | Module | Description |
|-------|--------|-------------|
| **1. context** | `context_builder.py` | Collect static metadata: BIDS `dataset_description.json`, existing `analysis.md`, kernel file, events/channels TSV files, participants, README. Builds the full context dict passed to all later phases. |
| **2. ref_analysis** | `ref_analyzer.py` | Batched LLM call over all reference PDFs/HTML in one large-context pass (~170 K tokens). Extracts paradigm description, task definitions, and DOI-tagged evidence snippets. |
| **3. feasibility** | `task_synthesizer.py` | Single LLM call: given the dataset description and reference extractions, decide whether a concrete ML task is feasible (yes/partial/no + rationale). Pipeline aborts here for "no". |
| **3.5. pre_scan** | `scan_bridge.py` | Run a lightweight EEGUnity scan before kernel generation to collect real event IDs. These IDs are passed to task synthesis so `target_events` lists are grounded in actual data. |
| **3b. event_annotation** | `event_annotator.py` | **Isolation-guaranteed**: reads dataset files only (no paper content, no paradigm labels). Multi-turn evidence collection (P3a) followed by a single annotation call (P3b) to assign meanings to each event code. |
| **4. task_synthesis** | `task_synthesizer_v2.py` | Two-step per-reference synthesis: (a) aggregate — one LLM call per ref extraction to propose task candidates + kernel_needs, deduped across refs; (b) fill — one LLM call per candidate to produce the v3 Task block (Epoch Method/Parameters, Label Route/Field, Meta Level, Target Definition, Evidence, Notes). Runs `detect.py` as a gate on a shell analysis.md and repairs up to 2 rounds. Emits both `tasks_section` and a `kernel_requirements` JSON contract (must-have events / native misc / info fields / derived-misc specs). |
| **5. kernel_loop** | `kernel_builder.py` | Iterative LLM + subprocess loop: generate a Python kernel that satisfies `kernel_requirements`, run it in `sandbox/`, capture errors/output, feed back to LLM, repeat until the scan passes or budget is exhausted. |
| **6. scan** | `scan_bridge.py` | Full EEGUnity scan with the new kernel. Produces structured scan results (event tables, MISC summary, info fields). |
| **6.5. reconcile** | `reconcile.py` | Validate each task's referenced fields (target_events, label_field) against a scan whitelist (events ∪ native misc ∪ info fields ∪ participants columns). Rules: missing event IDs → drop (kernels cannot invent events); missing info fields → drop (kernels cannot synthesize participants columns); missing misc channel that the task's `kernel_requirements.must_derive_misc` covers → one kernel patch + rescan attempt; otherwise drop. Prevents misc-channel hallucinations from leaking through. |
| **7. doc_write** | `doc_writer.py` | Assemble and write the final `analysis.md`. Merges the reconciled Tasks section, post-reconcile scan results (Event Structure, MISC Label Summary, Info), Paradigm section from ref analysis, and Kernel Responsibilities. |

### Resume logic

Progress is saved as JSON in `progress/<dataset>.json` after each phase. On re-run (without `--fresh`), the pipeline skips all completed phases and resumes from the last saved phase. Use `--fresh` to restart from scratch.

### Budget tracking

`pipeline/budget.py` implements a simple prompt-count budget (`Budget` class). Each LLM call charges the budget by phase name. If the budget is exhausted (`BudgetExhausted`), the pipeline saves its current state and exits cleanly for that dataset.

### Task ↔ Kernel co-synthesis

Phase 4 produces two artifacts that travel together:

1. **`tasks_section`** — human-readable markdown ready for `analysis.md`.
2. **`kernel_requirements`** — structured JSON contract handed to `kernel_builder`:
   ```jsonc
   {
     "required_event_ids":     ["left_target", "right_target", "trialResponse"],
     "required_native_misc":   ["trialResponse"],
     "required_info_fields":   ["age", "p_factor"],
     "derived_misc_channels": [
       {"name": "accuracy",
        "source_field": "trialResponse:user_answer + correct_answer",
        "derivation": "accuracy = 1 if user_answer == correct_answer else 0",
        "groundable_evidence": "task-symbolSearch_events.json defines both columns",
        "used_by": ["2-class symbol search trial accuracy"]}
     ],
     "_dropped_candidates": [
       {"paradigm": "surround suppression classification",
        "reason": "stim_ON events (13278) have no per-trial label distinguishing stimulus conditions"}
     ]
   }
   ```

The aggregate step is told to drop any derived-misc candidate whose source field is not actually present in `bids_sidecars` / reference evidence, and to log rejected paradigms in `_dropped_candidates` with an explicit reason. This is the anti-hallucination line of defense in Phase 4.

The reconcile phase (6.5) is the second line of defense: even if the kernel was built to the requirements, it then validates the produced scan output against every field the Tasks section references. Missing event IDs or info fields are unrecoverable (kernels cannot invent rows in `events.tsv` or columns in `participants.tsv`) and cause the task to be dropped. Missing derived-misc channels that *were* declared in `derived_misc_channels` get one LLM-driven kernel patch + rescan attempt.

---

## `detect.py` — Semantic Rule Checker

`detect.py` validates `analysis.md` and the kernel file against rules defined in `rulebook/semantic_rules.yaml`. It can be used standalone or imported by `app/server.py` for in-app validation.

### How it works

1. **Load rules** — parses `semantic_rules.yaml` into a dict of rule metadata (id, description, severity, type).
2. **Cross-checks** — ~26 Python functions registered via `@_cc` decorator implement the actual checks. Each function receives `analysis_text` and optional `kernel_text`, `dataset_name`.
3. **YAML rule checks** — simple pattern/absence checks defined purely in YAML (no Python code needed).
4. **Severity levels** — `error`, `warning`, `info`. CLI `--severity` filters output.

### In-memory API (for app/server.py)

```python
from eeg_kernel_agent import detect

rules = detect.load_rules()                      # load and cache rulebook
result = detect.check_analysis_text(
    analysis_text=content,
    dataset_name="openneuro_ds001784",
    kernel_text=None,
    severity_filter=None,                        # or "error"
    rules=rules,
)
# result: list of {"rule_id": ..., "severity": ..., "message": ...}
```

### Key cross-checks implemented

| Rule ID | Description |
|---------|-------------|
| `label_field_required_for_nonevent` | Label Field is required when Label Route ∈ {misc, info} |
| `label_field_absent_for_event` | Label Field must be absent when Label Route = event |
| `misc_classification_forbidden` | misc route is regression-only |
| `classification_task_has_multiple_classes` | classification needs ≥2 distinct y values in Target Definition |
| `segmentation_requires_empty_target_events` | segmentation epoch method → target_events = [] |
| `epoch_parameters_complete` | Each task's Epoch Parameters must contain all required keys for its Epoch Method (see table below) |
| `target_def_schema_matches_route` | Target Definition table header must match Route × Task Type |
| `manual_review_blank` | Manual Review field must be left blank |

**Minimum Epoch Parameters keys by method:**

| Epoch Method | Required Keys |
|---|---|
| `epoch_by_event_hdf5` | `tmin`, `tmax`, `target_events` |
| `epoch_by_long_event_hdf5` | `tmin`, `tmax`, `overlap`, `target_events` |
| `epoch_by_segmentation_hdf5` | `segment_length`, `overlap` |

---

## `scan_engine.py` — EEGUnity Scan Core

Handles the low-level EEG data scanning used in Phases 3.5 and 6:

- **Machine identity** — stable UUID derived from hardware fingerprint, cached in `locator_cache/`.
- **Locator cache** — maps dataset names to data file paths so scans do not require re-discovery.
- **EEGUnity integration** — spawns the EEGUnity scan subprocess, captures structured results (event counts, channel names, participant info).
- **HDF5 output** — manages the scan output HDF5 files written to the BIDS dataset directory.

---

## `tools/migrate_to_v3.py` — Schema Migration

Non-LLM rule-based rewriter that upgrades pre-v3 `analysis.md` files to the v3 Task schema:

1. Adds `**Label Field**:` bullet when Label Route ∈ {misc, info}.
2. Rewrites Target Definition table headers to match Route × Task Type matrix.
3. Splits tasks with multiple first-column values into N separate tasks.
4. Marks single-class classifications with `<!-- MIGRATION: ... -->` review comments.
5. Normalizes `**Manual Review**:` to blank.
6. Inserts `### MISC Label Summary` block when any task uses misc route.
7. Renames `**Kernel Notes**:` → `**Notes**:` at the Task level.

For batch migration of Status=Completed datasets, see `Script/migrate_completed_to_v3.py`.

```bash
# Dry-run (print diff, no writes)
python -m eeg_kernel_agent.tools.migrate_to_v3 openneuro_ds001784 --dry-run

# Apply to one dataset
python -m eeg_kernel_agent.tools.migrate_to_v3 openneuro_ds001784

# Apply to all datasets
python -m eeg_kernel_agent.tools.migrate_to_v3 --all
```

---

## `rulebook/semantic_rules.yaml`

Defines every semantic rule checked by `detect.py`. Two types:

- **cross_check** — rule has a matching Python function in `detect.py` (identified by `id` matching the function name).
- **pattern / absence** — rule is fully defined in YAML via a regex pattern or a required-string check.

Each rule entry has: `id`, `description`, `severity` (`error`/`warning`/`info`), `type`.

---

## `kernels/`

One Python file per dataset, generated by the kernel build loop. Each kernel defines how to load and preprocess the raw EEG data into HDF5 format for the EEGUnity scanner. Kernels are named `<dataset>.py` (e.g., `openneuro_ds001784.py`).

---

## `progress/`

JSON checkpoint files (`<dataset>.json`) written after each pipeline phase. Fields include `phase` (last completed phase name), `budget_used`, `budget_breakdown`, and phase-specific output data. Delete or use `--fresh` to restart.

---

## `machine_config/`

One JSON file per machine. Auto-detected at runtime (uses the alphabetically last file if multiple exist). Must contain at minimum:

```json
{
  "api_key": "...",
  "model": "claude-opus-4-7",
  "data_root": "/absolute/path/to/datasets"
}
```

---

## `upgrade.py`

Placeholder — not yet implemented. Intended for incremental updates to existing kernels or analysis.md without a full re-run. Currently exits immediately with an informational message; use `generate.py --fresh` in the meantime.
