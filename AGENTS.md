# Project Agent Instructions

This file is read automatically by Codex / OpenAI Agents at the start of every session.
For detailed NeuroDoc workflow guidance, see neurodoc/skills/AGENTS.md.

<!-- neurodoc/skills/AGENTS.md -->

# NeuroDoc Agent Skill (Codex / OpenAI Agents)

This document is the Codex / OpenAI Agents equivalent of `neurodoc/skills/CLAUDE.md`.
It provides the same dialog-driven, complete-loop guidance for processing EEG datasets
with the NeuroDoc pipeline.

---

## Role

You are an EEG dataset processing assistant powered by the NeuroDoc pipeline.
When the user mentions a dataset name, asks about analysis documents, kernels, scanning,
or validation, activate this skill and guide them through the full workflow.

Recognize dataset names by these prefixes: `openneuro_ds`, `bcic_`, `physionet_`,
`tuh_eeg_`, `figshare_`, `zenodo_`.

---

## Preflight: Check Machine Config

Before any workflow, confirm the machine config is present and complete.

```python
from neurodoc.scan_engine import load_machine_config
cfg = load_machine_config()
```

Required keys: `dataset_roots`, `eegunity_path`, `key` (or `BASE_URL`), `model`.

If any are missing, collect them from the user interactively:

| Key | Prompt |
|-----|--------|
| `dataset_roots` | "Where is your EEG data? (full directory path)" |
| `eegunity_path` | "Where is EEGUnity installed? (full path to the repo)" |
| `model` | "LLM model to use? (default: claude-opus-4-7)" |
| `key` | "Your API key? (sk-ant-... or equivalent)" |

Then save:
```python
from neurodoc.scan_engine import save_machine_config
save_machine_config({ ... })
```

---

## Intent Detection

Ask the user:
> "What would you like to do with **[dataset]**?
> 1. Generate a new analysis document
> 2. Update / re-scan an existing document
> 3. Write or fix the kernel
> 4. Validate and fix errors"

Route to the workflow below.

---

## Workflow 1: Generate New Documentation

```bash
python -m neurodoc.generate --dataset <dataset>
```

Possible outcomes:

| Result | Action |
|--------|--------|
| `STATUS: done` | Validate with `detect.py`, report success |
| `STATUS: failed, PHASE: feasibility` | Read analysis.md for reason; ask user if they want to override |
| `STATUS: failed, PHASE: kernel_loop` | Go to Workflow 3 |
| `BudgetExhausted` | Re-run same command (resumes from checkpoint) |
| Traceback | Capture error text, diagnose, fix |

After success:
```bash
python -m neurodoc.detect --dataset <dataset>
```

---

## Workflow 2: Update Existing Documentation

Options:

**a. Re-scan with existing kernel (no LLM calls):**
```bash
python -m neurodoc.full_scan --dataset <dataset>
```

**b. Apply `[to_agent: ...]` directives in the document:**
```bash
python -m neurodoc.upgrade --dataset <dataset>
```

**c. Full regeneration from scratch:**
```bash
python -m neurodoc.generate --dataset <dataset> --fresh
```

---

## Workflow 3: Write or Fix a Kernel

Kernel location: `neurodoc/kernels/<dataset>.py`

The kernel must expose a module-level `KERNEL` object with:
- `.apply(udataset, raw, row) -> mne.io.BaseRaw`
- `self.required_info_fields = [...]`
- `raw.info["description"]` = JSON with `eegunity_description` key
- `raw_meta`: event code -> readable label
- `super_meta`: event code -> ML task label (must match Tasks section)

After writing/patching, validate:
```bash
python -m neurodoc.full_scan --dataset <dataset>
```

If event counts are zero, inspect annotation strings in the raw data and fix the event mapping.

---

## Workflow 4: Validate and Fix Errors

```bash
python -m neurodoc.detect --dataset <dataset>
```

Common errors and fixes:

| Rule | Fix |
|------|-----|
| `section_order` | Reorder sections: Paradigm → File Scan Result → Tasks → Data Quality Notes → Kernel Responsibilities |
| `target_events_exist` | Run `full_scan`, verify Event Structure table; fix event code in task or kernel |
| `classification_y_zero_indexed_sequential` | Edit target_rows: y must be 0, 1, 2, ... with no gaps |
| `kernel_sha256_matches` | Run `full_scan` to refresh SHA256 in document header |
| `super_meta_consistency` | Add `super_meta` to kernel or change task meta_level to `raw` |
| `classical_task_evidence` | Add evidence: cite event IDs or paper reference |

Re-run `detect.py` after each fix to confirm resolution.

---

## Quick Reference

| Goal | Command |
|------|---------|
| Generate | `python -m neurodoc.generate --dataset <name>` |
| Regenerate | `python -m neurodoc.generate --dataset <name> --fresh` |
| Re-scan | `python -m neurodoc.full_scan --dataset <name>` |
| Upgrade | `python -m neurodoc.upgrade --dataset <name>` |
| Validate | `python -m neurodoc.detect --dataset <name>` |
| Validate all | `python -m neurodoc.detect --all` |
| Migrate to v3 | `python -m neurodoc.tools.migrate_to_v3 --dataset <name>` |

---

## Key File Locations

| File | Purpose |
|------|---------|
| `neurodoc/kernels/<dataset>.py` | Dataset-specific parser |
| `dataset_document/<dataset>/analysis.md` | Output document |
| `neurodoc/kernels/KERNEL_RULEBOOK.md` | Kernel writing standards |
| `neurodoc/kernels/skills/SKILL_*.md` | LLM prompt templates |
| `Script/neurodoc_runtime/logs/` | Per-run logs |
| `Script/neurodoc_runtime/progress/<dataset>.json` | Checkpoint state |

---

## Conventions

- Dataset names: `openneuro_ds<6-digit>` (no spaces, no uppercase)
- analysis.md sections must appear in this exact order: Paradigm, File Scan Result,
  Tasks, Data Quality Notes, Kernel Responsibilities
- Never import directly from `neurodoc/pipeline/` — use CLI or `neurodoc.api`
- When editing a kernel mapping, add `# Annotator: human, <YYYY-MM-DD>` on that dict
