# NeuroDoc Agent Skill

This skill activates whenever the user mentions an EEG dataset, asks about analysis
documents, kernels, or anything related to the NeuroDoc pipeline.

---

## Activation Triggers

Activate this skill when the user says anything like:
- "I want to process dataset X"
- "generate / update / scan / validate [dataset name]"
- "fix the kernel for X"
- "why does detect.py report an error for X"
- "add a task to X"
- any string matching `openneuro_ds\d+`, `bcic_`, `physionet_`, `tuh_eeg_`, `figshare_`, `zenodo_`

---

## Preflight: Confirm Machine Config

Before starting any workflow, verify the machine config exists and is complete.

1. Run:
   ```
   python -m neurodoc.scan_engine --check-config
   ```
   If this fails (no `--check-config` flag), instead read the machine config manually:
   ```python
   from neurodoc.scan_engine import get_machine_id, load_machine_config
   cfg = load_machine_config()
   print(cfg)
   ```

2. Required keys: `dataset_roots`, `eegunity_path`, `key` (or `BASE_URL`), `model`

3. If any key is missing or empty, run the **Machine Config Setup** flow below before
   doing anything else.

---

## Machine Config Setup (run once per machine)

Ask the user for each missing value:

| Key | Question to ask |
|-----|----------------|
| `dataset_roots` | "Where is your EEG data stored? (full path, e.g. D:/eeg_data)" |
| `eegunity_path` | "Where is the EEGUnity library installed? (full path to the repo)" |
| `model` | "Which LLM model do you want to use? (default: claude-opus-4-7)" |
| `key` | "Please paste your Anthropic API key (sk-ant-...)" |
| `ANTHROPIC_BASE_URL` | "Do you use a custom Anthropic endpoint? (leave blank for default)" |
| `BASE_URL` | "Do you use an OpenAI-compatible endpoint? (leave blank if using Anthropic)" |

Then write the config:
```python
from neurodoc.scan_engine import save_machine_config
save_machine_config({
    "dataset_roots": ["<path_provided>"],
    "eegunity_path": "<path_provided>",
    "model": "<model_or_default>",
    "key": "<key_provided>",
    "ANTHROPIC_BASE_URL": "<url_or_empty>",
    "BASE_URL": "<url_or_empty>",
    "python_env": "python",
    "num_workers": 4,
    "budget": 500,
})
```

Confirm success, then return to the main workflow.

---

## Intent Detection Dialog

After preflight passes, ask:

> "What would you like to do with **[dataset_name]**?
> 1. Generate a new analysis document (first time)
> 2. Update an existing document (re-scan, add task, fix issue)
> 3. Write or fix the kernel
> 4. Validate and fix detected errors
> 5. Something else — describe it"

Route to the matching workflow below.

---

## Workflow 1: Generate New Documentation

**Trigger**: user says "generate", "first time", or no `analysis.md` exists for the dataset.

### Step 1 — Check for reference materials
Look for files in `dataset_document/<dataset>/`:
```bash
ls dataset_document/<dataset>/
```
If empty or missing PDFs/TXTs, ask:
> "Do you have a paper or documentation for this dataset? If so, please put the PDF or
> TXT files in `dataset_document/<dataset>/` and let me know when ready.
> (You can skip this step — the pipeline will still run, but document quality may be lower.)"

### Step 2 — Run the pipeline
```bash
python -m neurodoc.generate --dataset <dataset>
```

Watch for these outcomes and respond accordingly:

| Output pattern | What it means | What to do |
|----------------|--------------|------------|
| `STATUS: done` | Success | Go to Step 3 |
| `STATUS: failed, PHASE: feasibility` | Dataset deemed infeasible | Read `dataset_document/<dataset>/analysis.md` for reason; ask user if they want to override |
| `STATUS: failed, PHASE: kernel_loop` | Kernel generation failed | Go to Workflow 3 |
| `STATUS: paused` | Budget exhausted | Ask user to resume: `--fresh` or just re-run |
| `BudgetExhausted` | Token limit hit | Run `python -m neurodoc.generate --dataset <dataset>` again (resumes from checkpoint) |
| Any Python traceback | Runtime error | Capture error, go to error diagnosis |

### Step 3 — Validate the result
```bash
python -m neurodoc.detect --dataset <dataset>
```

If errors are found, go to **Workflow 4**.
If clean, report:
> "Generation complete! The analysis document is at:
> `dataset_document/<dataset>/analysis.md`
> The kernel is at: `neurodoc/kernels/<dataset>.py`
> No validation errors detected."

---

## Workflow 2: Update Existing Documentation

**Trigger**: user says "update", "re-scan", "add task", "fix issue", or `analysis.md` already exists.

Ask:
> "What kind of update do you need?
> a. Re-scan the data with the existing kernel (refresh File Scan Result section)
> b. Apply a `[to_agent: ...]` directive already written in the document
> c. Fix a specific section manually (I'll guide you)
> d. Regenerate the whole document from scratch"

### 2a — Re-scan only
```bash
python -m neurodoc.full_scan --dataset <dataset>
```
This refreshes `File Scan Result` and `Kernel Responsibilities` without touching task definitions.

### 2b — Apply agent directives
Check the document for `[to_agent: ...]` tags:
```bash
grep -n "to_agent" dataset_document/<dataset>/analysis.md
```
If found:
```bash
python -m neurodoc.upgrade --dataset <dataset>
```

### 2c — Manual section fix
Ask the user which section needs updating, then use the appropriate sub-workflow:
- **Tasks section**: Refer to the task schema in `neurodoc/dataset_api/factory.py` and guide the user to edit the YAML block directly.
- **Paradigm section**: Ask what information changed, then update the markdown.
- **Data Quality Notes**: Ask the user to describe the quality issue; draft the note.

### 2d — Full regeneration
Same as Workflow 1, but add `--fresh` to ignore existing progress:
```bash
python -m neurodoc.generate --dataset <dataset> --fresh
```

---

## Workflow 3: Write or Fix a Kernel

**Trigger**: user says "write kernel", "fix kernel", kernel validation fails, or Phase 5 errors.

### Step 1 — Understand what the kernel needs to do
Read the existing kernel if present:
```
neurodoc/kernels/<dataset>.py
```
Read the KERNEL_RULEBOOK for guidance:
```
neurodoc/kernels/KERNEL_RULEBOOK.md
```

### Step 2 — Check available SKILL templates
Templates in `neurodoc/kernels/skills/` cover common patterns:
- `SKILL_channel_rename.md` — renaming generic EEG-N channels
- `SKILL_event_annotation.md` — mapping event codes to semantic labels
- `SKILL_super_meta.md` — defining super_meta labels for ML tasks
- `SKILL_misc_channel.md` — writing MISC channels (e.g., reaction_time)

Ask the user:
> "Does this dataset use any of these patterns?
> 1. Channels named EEG-0, EEG-1, ... (need renaming)
> 2. Numeric event codes that need semantic labels
> 3. Has a label defined per-epoch (MISC channel, e.g., reaction time)
> 4. Multiple paradigms in one dataset
> Select all that apply, or describe the dataset structure."

### Step 3 — Generate or patch the kernel
Based on the user's answers and any reference materials available, write or patch the kernel.

Key kernel contract (must satisfy):
1. Module-level `KERNEL` object with `.apply(udataset, raw, row) -> mne.io.BaseRaw`
2. `self.required_info_fields = [...]` listing fields written to `eegunity_description`
3. `raw.info["description"]` must be valid JSON with `eegunity_description` key
4. Channel names must match standard 10-20 names after `apply()`
5. `raw_meta` dict: event code -> readable label (e.g., `{"1": "left hand MI"}`)
6. `super_meta` dict: event code -> ML task label (must match Tasks section in analysis.md)

### Step 4 — Validate the kernel
Run a quick syntax check:
```bash
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('k', 'neurodoc/kernels/<dataset>.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK:', m.KERNEL)"
```

Then run a full scan to see if it produces events:
```bash
python -m neurodoc.full_scan --dataset <dataset>
```

If event counts are all zero, ask the user to share a sample of the raw annotation descriptions, then adjust the event mapping.

---

## Workflow 4: Validate and Fix Errors

**Trigger**: user says "validate", "detect errors", or `detect.py` reported issues.

### Step 1 — Run validation
```bash
python -m neurodoc.detect --dataset <dataset>
```

### Step 2 — Diagnose each error

| Rule ID | Severity | Meaning | Fix direction |
|---------|----------|---------|---------------|
| `section_order` | error | Sections out of order in analysis.md | Reorder sections: Paradigm → File Scan Result → Tasks → Data Quality Notes → Kernel Responsibilities |
| `super_meta_consistency` | error | `Super Meta Required` in KR blockquote doesn't match actual `Meta Level` values in Tasks | If Tasks have `super`, set KR to `Yes`; if all `raw`, set KR to `No`. For a misclassified task, fix its `Meta Level` directly — do not change `label_route` just to avoid `super` |
| `target_events_exist` | error | Event ID in task not found in scan results | Run `full_scan`, check Event Structure table; fix event code in task or kernel mapping |
| `classification_y_zero_indexed_sequential` | error | y values are not 0, 1, 2, ... | Edit Target Definition table: y must start at 0 with no gaps |
| `task_dataset_dispatchable` | error | Task fails `dataset_api` dry run | Fix `label_route`, `task_type`, or `target_rows` schema to match factory requirements |
| `kernel_sha256_matches` | warning | Kernel changed after document was written | Run `full_scan` to refresh the SHA256 in the document header |
| `classical_task_evidence` | error | Task Evidence field is empty | Add evidence: cite event IDs, scan counts, or paper reference |

### Step 3 — Apply fixes interactively
For each error, explain it in plain language and ask:
> "This error means [plain-language explanation]. Would you like me to fix it automatically,
> or would you prefer to edit it yourself?"

After all fixes are applied, re-run `detect.py` and confirm zero errors.

---

## Quick Reference

When the user asks "what commands are available" or "help":

| Goal | Command |
|------|---------|
| Generate new doc | `python -m neurodoc.generate --dataset <name>` |
| Re-run from scratch | `python -m neurodoc.generate --dataset <name> --fresh` |
| Re-scan only | `python -m neurodoc.full_scan --dataset <name>` |
| Apply agent directives | `python -m neurodoc.upgrade --dataset <name>` |
| Validate document | `python -m neurodoc.detect --dataset <name>` |
| Validate all datasets | `python -m neurodoc.detect --all` |
| List dataset status | `python -c "from neurodoc.scan_engine import list_datasets; [print(d) for d in list_datasets()]"` |
| Migrate doc to v3 | `python -m neurodoc.tools.migrate_to_v3 --dataset <name>` |

---

## Error Recovery

### "BudgetExhausted" during generation
Progress is saved. Just re-run the same command — it will resume from the last checkpoint.
To increase the budget limit, edit `budget` in the machine config JSON.

### "No events found after scan"
1. Check `neurodoc/kernels/<dataset>.py` — does `raw_meta` cover the actual annotation strings?
2. Run: `python -c "import mne; raw = mne.io.read_raw(...); print(set(a['description'] for a in raw.annotations))"`
3. Update the kernel's event mapping to match the actual annotation strings.

### "Kernel file not found"
The pipeline uses a fallback: `neurodoc/kernels/bids.py` or `neurodoc/kernels/openneuro.py`.
To create a dataset-specific kernel, go to **Workflow 3**.

### Pipeline hangs or crashes mid-run
Check `Script/neurodoc_runtime/logs/<dataset>_*.log` for the last error.
Progress is in `Script/neurodoc_runtime/progress/<dataset>.json` — it is safe to inspect.

---

## Conventions to Follow

- Always use forward slashes in paths, even on Windows.
- Dataset names use the format `openneuro_ds<6-digit-number>` (no spaces).
- When writing or editing `analysis.md`, preserve the exact section order.
- Do not call `pipeline/` modules directly — use the CLI entry points or `neurodoc.api`.
- When patching a kernel, add an inline comment:
  `# Annotator: human, <YYYY-MM-DD>` (or `LLM, <date>`) on the relevant mapping dict.
