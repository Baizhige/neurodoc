# eeg_kernel_agent

Automated pipeline for generating EEG dataset kernel files and `analysis.md` documentation from BIDS datasets, plus a torch `Dataset` API that turns the resulting HDF5 files into (data, label, meta) batches.

---

## Directory Structure

```
eeg_kernel_agent/
├── generate.py          # Entry point — full pipeline runner
├── detect.py            # Semantic rule checker for analysis.md / kernel files
├── scan_engine.py       # EEGUnity scan core (machine identity, locator cache, HDF5 scan)
├── llm_adapter.py       # Dual-provider LLM adapter (OpenAI-compatible + Anthropic)
├── upgrade.py           # Placeholder (not yet implemented)
├── pipeline/            # Modular pipeline stages
│   ├── runner.py           # Phase orchestrator with resume logic (PHASES list)
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
├── dataset_api/         # Torch Dataset classes that read v2.1 HDF5 files
│   ├── base.py             # BaseHDF5Dataset (lazy per-worker file handle)
│   ├── event_dataset.py    # EventDataset — label route = event
│   ├── misc_dataset.py     # MISCDataset — label route = misc (regression-only)
│   ├── info_dataset.py     # InfoDataset — label route = info
│   ├── factory.py          # build_dataset_from_task(task, h5_path, dry_run=...)
│   └── tests/              # pytest suite (37 tests)
├── tools/
│   └── migrate_to_v3.py # Non-LLM batch migration: pre-v3 analysis.md → v3 schema
├── rulebook/
│   └── semantic_rules.yaml  # Cross-check rule definitions consumed by detect.py
├── kernels/             # Generated kernel files (one .py per dataset)
├── progress/            # Per-dataset pipeline state JSON (resume checkpoints)
├── evidence_cache/      # Cached LLM evidence from Phase 3 event annotation
├── locator_cache/       # Scan locator CSVs keyed by machine id
├── logs/                # Per-dataset run logs (<dataset>.log)
├── machine_config/      # Machine-specific config JSON (API key, model, paths)
├── sandbox/             # Temporary kernel testing sandbox
└── design_old.md        # Legacy design notes
```

---

## Quick Start

### Prerequisites

```bash
pip install openai anthropic pyyaml pymupdf h5py torch pytest
```

A machine config file must exist in `machine_config/` (any `.json` file). Actual schema:

```json
{
  "url": "https://api.minimax.io/v1",
  "key": "sk-...",
  "model": "MiniMax-M2.7",
  "proxy": "",
  "python_env": "/path/to/python/bin/python",
  "eegunity_path": "/path/to/Script",
  "dataset_roots": ["/path/to/BIDS/datasets"],
  "num_workers": 2,
  "budget": 500
}
```

`url`/`key`/`model` (OpenAI-compatible) and `ANTHROPIC_BASE_URL` (Anthropic) are both handled by `llm_adapter.py`; whichever is configured takes precedence.

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

Output: `<BIDS_ROOT>/<dataset>/analysis.md` + `kernels/<dataset>.py`.

### Check a dataset with detect.py

```bash
python detect.py --dataset openneuro_ds001784
python detect.py --all
python detect.py --all --severity error
python detect.py --dataset openneuro_ds001784 --rulebook rulebook/semantic_rules.yaml
```

### Load a dataset for training

```python
from eeg_kernel_agent.dataset_api import build_dataset_from_task

task = {
    "label_route": "info",
    "task_type": "regression",
    "label_field": "p_factor",
}
ds = build_dataset_from_task(task, h5_path="<BIDS>/openneuro_ds005505/ds005505.hdf5", max_len=800)
for data, label, meta in ds:  # data: (n_ch, n_times), label: float32, meta: {source_group}
    ...
```

See §`dataset_api/` below for the full route × task-type matrix.

---

## Pipeline Flow (`generate.py`)

Each dataset runs through `pipeline/runner.py`, which orchestrates the `PHASES` list:

| Phase | Module | Description |
|-------|--------|-------------|
| **1. context** | `context_builder.py` | Collect static metadata: BIDS `dataset_description.json`, existing `analysis.md`, kernel file, events/channels TSV files, participants, README. |
| **2. ref_analysis** | `ref_analyzer.py` | Batched LLM call over all reference PDFs/HTML in one large-context pass. Extracts paradigm description, task definitions, and DOI-tagged evidence snippets. |
| **3. feasibility** | `task_synthesizer.py` | Single LLM call deciding whether a concrete ML task is feasible. Pipeline aborts here for "no". |
| **3.5. pre_scan** | `scan_bridge.py` | Lightweight EEGUnity scan before kernel generation to collect real event IDs. |
| **3b. event_annotation** | `event_annotator.py` | **Isolation-guaranteed**: dataset files only (no paper content). P3a multi-turn evidence collection → P3b single annotation call. |
| **4. task_synthesis** | `task_synthesizer_v2.py` | Aggregate → fill → detect gate (up to 2 repair rounds). Emits `tasks_section` and `kernel_requirements`. |
| **5. kernel_loop** | `kernel_builder.py` | Iterative LLM + subprocess loop (`MAX_VERSIONS=5`): generate a kernel, run it in `sandbox/`, feed errors back. **Hardened static validator** (see below) rejects kernels that don't honour `kernel_requirements`. |
| **6. scan** | `scan_bridge.py` | Full EEGUnity scan with the new kernel. Produces event tables, MISC summary, info fields. |
| **6.5. reconcile** | `reconcile.py` | Validate each task against a scan whitelist = events ∪ native misc ∪ (CANONICAL_INFO_FIELDS ∪ participants.tsv header ∪ sidecar fields). Missing event/info/misc → drop or one-shot kernel patch (see below). |
| **7. doc_write** | `doc_writer.py` | Assemble and write the final `analysis.md`. |
| **8. done** | — | Terminal state. `status` ∈ `{wait_manual_review, wait_kernel_update, failed}`. |

### Resume logic

Progress is saved in `progress/<dataset>.json` after each phase. Re-running without `--fresh` resumes from the last completed phase.

### Budget tracking

`pipeline/budget.py` charges each LLM call by phase name. Hitting the cap raises `BudgetExhausted`; the pipeline saves state and exits cleanly for that dataset.

### Task ↔ Kernel co-synthesis (Phase 4 contract)

Phase 4 produces two artifacts that travel together:

1. **`tasks_section`** — human-readable markdown ready for `analysis.md`.
2. **`kernel_requirements`** — structured JSON contract handed to `kernel_builder`:
   ```jsonc
   {
     "required_event_ids":   ["left_target", "right_target", "trialResponse"],
     "required_native_misc": [],
     "required_info_fields": ["age", "p_factor"],
     "derived_misc_channels": [
       {"name": "accuracy",
        "source_field": "trialResponse:user_answer + correct_answer",
        "derivation": "accuracy = 1 if user_answer == correct_answer else 0",
        "groundable_evidence": "task-symbolSearch_events.json defines both columns",
        "used_by": ["2-class symbol search trial accuracy"]}
     ],
     "_dropped_candidates": [...]
   }
   ```

The aggregate step drops any derived-misc candidate whose source field is not present in `bids_sidecars` / reference evidence, and logs rejected paradigms in `_dropped_candidates` with an explicit reason.

### Defence-in-depth

1. **Phase 4 aggregate** — reject derived-misc whose source isn't in `bids_sidecars` or reference evidence.
2. **Phase 5 static validator** (`kernel_builder._static_validate`) — reject kernels that don't honour `kernel_requirements`:
   - `apply()` body must contain `raw.info["description"] = json.dumps({...})` (not class-level static dict, not `.update()`)
   - every name in `required_info_fields` must appear verbatim in the source
   - every name in `derived_misc_channels[*].name` must appear verbatim in the source
   - every name in `required_native_misc` must appear verbatim in the source
3. **Phase 6.5 reconcile** — final scan validated against the whitelist (events ∪ misc ∪ info). Info whitelist is built by reading `<data_dir>/participants.tsv` directly — so kernels cannot silently rely on a stale sidecar cache. Unrecoverable misses (event/info) → drop the task; missing derived-misc that was declared in `kernel_requirements.derived_misc_channels` → one LLM kernel patch + rescan.

---

## `dataset_api/` — HDF5 v2.1 → torch Dataset

The epoch method writes a v2.1 HDF5 file per dataset (schema: see `Script/eegunity/utils/h5.py` → `h5EpochDatasetV2`). `dataset_api` reads that file and produces `(tensor, label, meta)` for the training loop.

### Factory dispatch

```python
from eeg_kernel_agent.dataset_api import (
    build_dataset_from_task,
    DatasetDispatchError,
    EventDataset, MISCDataset, InfoDataset,
)

# dry_run validates task schema without opening HDF5 — used by detect.py
build_dataset_from_task(task, dry_run=True)

# non-dry-run: returns a ready-to-use torch Dataset
ds = build_dataset_from_task(task, h5_path="file.hdf5", max_len=800)
```

### Route × Task Type matrix

| Route | Task Type | Class | Required task fields | Reads |
|-------|-----------|-------|----------------------|-------|
| event | classification | `EventDataset` | `target_rows=[{event_id, y, meaning}...]` | `/epoch_meta/event_code` + root `label_map` |
| event | regression | `EventDataset` | `target_rows=[{event_id, value, meaning}...]` | same |
| misc | regression | `MISCDataset` | `label_field` (the misc channel name) | `/misc_meta/<name>` (NaN rows excluded) |
| misc | classification | — | **forbidden** (rulebook §77条之六) | — |
| info | classification | `InfoDataset` | `label_field`, `target_rows=[{info_field, value, y, meaning}...]` → `info_map` | `/source_meta/<group>/.attrs[<field>]` broadcast per source |
| info | regression | `InfoDataset` | `label_field` | same, float-parsed |

`DatasetDispatchError.kind` ∈ `{schema, bad_target_def, missing_event, missing_misc, missing_info}`. Reconcile and detect both reuse the dry-run path to prove a Task block is dispatchable before accepting it.

### HDF5 v2.1 schema (`Script/eegunity/utils/h5.py`)

```
/
├─ attrs: version="2.1", sfreq, ch_names, n_channels, n_times,
│         label_map, n_epochs_total,
│         info_fields (JSON list[str]; v2.1)
├─ data (N, C, T) float32
├─ epoch_meta/{source_group, event_code}
├─ misc_meta/                           (v2.1, optional)
│  ├─ <misc_name> (N,) float32
│  └─ attrs.names
└─ source_meta/<group>/
   └─ attrs: file_path, age, gender, amplifier, cap, handedness,
             <any participants.tsv column captured by the kernel>
   └─ info (uint8): pickled mne.Info bytes
```

v2.0 files (pre-`misc_meta`, pre-`info_fields` root attr) are still readable by `EventDataset`.

---

## `detect.py` — Semantic Rule Checker

Validates `analysis.md` and the kernel file against `rulebook/semantic_rules.yaml`. Standalone CLI or imported by `app/server.py`.

### How it works

1. **Load rules** — parses `semantic_rules.yaml` into rule metadata.
2. **Cross-checks** — 29 Python functions registered via `@_cc` decorator. Each receives `analysis_text` + optional `kernel_text`, `dataset_name`.
3. **YAML rule checks** — simple pattern/absence checks defined entirely in YAML.
4. **Severity** — `error`, `warning`, `info`. CLI `--severity` filters.

### In-memory API

```python
from eeg_kernel_agent import detect
rules = detect.load_rules()
violations = detect.check_analysis_text(
    analysis_text=content,
    dataset_name="openneuro_ds005505",
    kernel_text=None,
    severity_filter=None,
    rules=rules,
)
```

### Key cross-checks

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `label_field_required_for_nonevent` | error | Label Field required when Route ∈ {misc, info} |
| `label_field_absent_for_event` | error | Label Field absent when Route = event |
| `misc_classification_forbidden` | error | misc route is regression-only |
| `classification_task_has_multiple_classes` | error | classification needs ≥2 distinct y |
| `segmentation_requires_empty_target_events` | error | segmentation ⇒ `target_events=[]` |
| `epoch_parameters_complete` | error | Epoch Parameters must list required keys (see below) |
| `target_def_schema_matches_route` | error | TD header must match Route × Task Type |
| `info_label_field_in_participants` | error | info-route Label Field must be a column in `participants.tsv` (authoritative) |
| `misc_label_field_has_misc_channel` | error | misc-route Label Field must be declared in `kernel_requirements` (native or derived) |
| `task_dataset_dispatchable` | error | Every Task must dispatch via `build_dataset_from_task(dry_run=True)` |
| `info_label_field_in_info_section` | warning | Label Field should also appear in `### Info` (downgraded; the authoritative check is against participants.tsv) |
| `manual_review_blank` | warning | Manual Review field must be blank in generated docs |

**Minimum Epoch Parameters keys by method:**

| Epoch Method | Required Keys |
|---|---|
| `epoch_by_event_hdf5` | `tmin`, `tmax`, `target_events` |
| `epoch_by_long_event_hdf5` | `tmin`, `tmax`, `overlap`, `target_events` |
| `epoch_by_segmentation_hdf5` | `segment_length`, `overlap` |

---

## `scan_engine.py` — EEGUnity Scan Core

Used in Phases 3.5 and 6:

- **Machine identity** — stable UUID from hardware fingerprint, cached per-machine.
- **Locator cache** (`locator_cache/<machine_id>/`) — dataset name → data file list, avoids re-discovery on subsequent scans.
- **EEGUnity integration** — spawns the EEGUnity scan subprocess, captures structured results (event counts, channel names, participant info).
- **Dual-config loader** — machine config + `app/config.json` (main app config is a fallback for LLM fields only).

---

## `llm_adapter.py` — Dual-provider LLM Adapter

- `resolve_llm_config(cfg)` → normalises OpenAI-compatible (`BASE_URL`) vs Anthropic (`ANTHROPIC_BASE_URL`) into a single provider-selected dict.
- `call_llm_text(...)` / `post_llm_json(...)` / `extract_text_from_response(...)` — provider-agnostic wrappers used by every pipeline stage.

---

## `tools/migrate_to_v3.py` — Schema Migration

Non-LLM rule-based rewriter: pre-v3 `analysis.md` → v3 Task schema.

1. Adds `**Label Field**:` bullet when Route ∈ {misc, info}.
2. Rewrites Target Definition headers to match Route × Task Type.
3. Splits tasks with multiple first-column values into N separate tasks.
4. Marks single-class classifications with `<!-- MIGRATION: ... -->` review comments.
5. Normalises `**Manual Review**:` to blank.
6. Inserts `### MISC Label Summary` when any task uses misc route.
7. Renames `**Kernel Notes**:` → `**Notes**:` at the Task level.

```bash
python -m eeg_kernel_agent.tools.migrate_to_v3 openneuro_ds001784 --dry-run
python -m eeg_kernel_agent.tools.migrate_to_v3 openneuro_ds001784
python -m eeg_kernel_agent.tools.migrate_to_v3 --all
```

---

## `rulebook/semantic_rules.yaml`

Every semantic rule is defined here. Types:

- **cross_check** — paired with a Python function in `detect.py` (matched by `function:` key).
- **pattern / section_exists / field_value** — fully defined in YAML, no Python needed.

Each rule entry has `id`, `desc`, `severity` (`error`/`warning`), and `check` type.

---

## `kernels/`

One Python file per dataset generated by the kernel build loop. Each kernel defines `apply(self, udataset, raw, row) -> mne.io.BaseRaw` with EXACT signature. The hardened static validator rejects kernels that miss any `kernel_requirements` name or don't dynamically write `raw.info["description"] = json.dumps(...)`.

---

## `progress/`

JSON checkpoint per dataset. Fields: `phase` (last completed phase), `budget_used`, `budget_breakdown`, and phase-specific output (`ref_extractions`, `pre_scan_result`, `event_annotations`, `tasks_section`, `kernel_requirements`, `scan_result`, `kernel_ok`, `status`, …). Delete or use `--fresh` to restart. Edit `phase` manually to rewind (e.g. set `phase="task_synthesis"` + `kernel_ok=false` to re-enter kernel_loop without rescanning).

---

## `machine_config/`

One JSON per machine, auto-detected at runtime (alphabetically last if multiple exist). See `Quick Start → Prerequisites` above for the full schema.

---

## `upgrade.py`

Placeholder — exits with an informational message. Use `generate.py --fresh` (or the progress-rewind trick above) in the meantime.
