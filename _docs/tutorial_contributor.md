# Kernel & Dataset Contributor Guide

This guide is for contributors who want to **add a new dataset**, **fix or improve an existing kernel**, or **re-run the full generation pipeline** — using the **NeuroDoc** CLI.

You will need access to the raw EEG data files and an LLM API key.

---

## Prerequisites

- Git and a GitHub account
- Python 3.9+
- Raw EEG data available locally (for scanning)
- An Anthropic API key (`sk-ant-...`) or an OpenAI-compatible endpoint

---

## Step 1 — Fork & Clone

1. Go to the anonymous review repository on your Git hosting platform
2. Click **Fork** and fork to your personal account
3. Clone your fork:

```bash
git clone https://github.com/<your-username>/<anonymous-repo>.git
cd <anonymous-repo>
```

4. Create a feature branch:

```bash
git checkout -b contrib/<dataset-name>
```

---

## Step 2 — Install NeuroDoc

```bash
pip install -r neurodoc/requirements.txt   # if present
# or install EEGUnity separately:
pip install -e /path/to/eegunity
```

> [!NOTE]
> NeuroDoc requires `EEGUnity` for all scan operations. Make sure it is installed from your local source checkout or package distribution, and that the path is set in your machine config (Step 3).

---

## Step 3 — Configure Your Machine

NeuroDoc uses a per-machine JSON config stored in `Script/neurodoc_runtime/machine_config/`.

Run the interactive setup (first time only):

```python
python -c "
from neurodoc.scan_engine import save_machine_config
save_machine_config({
    'dataset_roots': ['/path/to/your/eeg_data'],
    'eegunity_path': '/path/to/eegunity',
    'model': 'claude-opus-4-7',
    'key': 'sk-ant-...',
    'ANTHROPIC_BASE_URL': '',
    'BASE_URL': '',
    'python_env': 'python',
    'num_workers': 4,
    'budget': 500,
})
"
```

Verify the config loaded correctly:

```bash
python -m neurodoc.scan_engine --check-config
```

---

## Step 4 — Prepare Reference Materials (recommended)

Place any papers, README exports, or official documentation in:

```
dataset_document/<dataset-name>/
```

Supported formats: PDF, TXT. These are used by the pipeline's **Phase 1 (Build Context from academic sources)** step to improve documentation quality. You can skip this step, but quality may be lower.

---

## Step 5 — Run the Generation Pipeline

```bash
python -m neurodoc.generate --dataset <dataset-name>
```

The pipeline runs three phases automatically:

| Phase | What happens |
|---|---|
| **Phase 1: Build Context** | Loads local evidence, scans event IDs, reads your reference PDFs |
| **Phase 2: Task Synthesis** | Judges feasibility, proposes ML task candidates, derives kernel requirements |
| **Phase 3: Kernel Coding** | Generates `kernel.py` in a sandbox, validates it, reconciles tasks with scan results |

Progress is saved after each phase. If interrupted, re-run the same command to resume:

```bash
python -m neurodoc.generate --dataset <dataset-name>          # resume
python -m neurodoc.generate --dataset <dataset-name> --fresh  # start over
```

> [!TIP]
> Watch the terminal output. If Phase 3 reports `STATUS: failed, PHASE: kernel_loop`, the kernel needs manual attention — see the "Fixing a Kernel" section below.

---

## Step 6 — Validate the Output

```bash
python -m neurodoc.detect --dataset <dataset-name>
```

All **errors** must be resolved before submitting a PR. Warnings are acceptable if they have a known explanation noted in **Data Quality Notes**.

Common errors and fixes:

| Error | Fix |
|---|---|
| `target_events_exist` | Event ID in Tasks not found in scan — fix the task or re-run `full_scan` |
| `super_meta_consistency` | Tasks have `Meta Level: super` but KR block says `No` — run `full_scan` to refresh |
| `classical_task_has_evidence` | Add an Evidence line to the task referencing event IDs or a paper |
| `kernel_sha256_matches` | Kernel was edited after the scan — re-run `full_scan` to update the hash |

---

## Step 7 — Re-scan Only (when kernel already exists)

If you only changed the kernel and want to refresh the `File Scan Result` without re-running the full pipeline:

```bash
python -m neurodoc.full_scan --dataset <dataset-name>
```

---

## Step 8 — Commit & Submit PR

Stage only the files relevant to your dataset:

```bash
git add dataset_document/<dataset-name>/analysis.md
git add neurodoc/kernels/<dataset-name>.py
git commit -m "contrib(<dataset-name>): add kernel and initial analysis.md"
git push origin contrib/<dataset-name>
```

Then open a Pull Request on GitHub:
- **Base repository**: `<anonymous-org>/<anonymous-repo>`
- **Base branch**: `dev`
- **Compare branch**: `contrib/<dataset-name>` on your fork

In the PR description, include:
- Dataset name, source URL, and paradigm summary
- `detect.py` output (paste the summary line, e.g., `0 errors, 1 warning`)
- Any known limitations noted in Data Quality Notes

---

## Fixing an Existing Kernel

If a kernel is failing or producing zero events:

```bash
# Check what events are actually in the raw files
python -c "
import mne
raw = mne.io.read_raw('/path/to/file', preload=False)
print(set(a['description'] for a in raw.annotations))
"
```

Then edit `neurodoc/kernels/<dataset>.py` and update the `raw_meta` mapping to match the actual annotation strings. After editing:

```bash
python -m neurodoc.full_scan --dataset <dataset-name>
python -m neurodoc.detect --dataset <dataset-name>
```

See [`neurodoc/kernels/KERNEL_RULEBOOK.md`](../neurodoc/kernels/KERNEL_RULEBOOK.md) for the full kernel specification.

---

## Tips

- Budget is tracked per dataset. If you hit `BudgetExhausted`, just re-run — progress is saved.
- Use `--workers 4` to run multiple datasets in parallel:  `python -m neurodoc.generate --dataset ds1 ds2 ds3 --workers 4`
- The `upgrade.py` CLI applies `[to_agent: ...]` directives written inside `analysis.md` — useful for incremental fixes without a full re-run.

