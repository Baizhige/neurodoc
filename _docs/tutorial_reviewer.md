# Reviewer & Document Contributor Guide

This guide is for contributors who want to **review existing dataset documents**, improve task definitions, fix wording, or add quality notes — using the **NeuroAudit** web UI.

No Python ML background required. You work entirely through a browser-based interface.

---

## Prerequisites

- Git and a GitHub account
- Python 3.9+
- ~5 minutes to set up

---

## Step 1 — Fork & Clone

1. Go to [github.com/EEG-BenchmarkSkill/EEGBenchmarkSKILL](https://github.com/EEG-BenchmarkSkill/EEGBenchmarkSKILL)
2. Click **Fork** (top-right) and fork to your personal account
3. Clone your fork:

```bash
git clone https://github.com/<your-username>/EEGBenchmarkSKILL.git
cd EEGBenchmarkSKILL
```

4. Create a feature branch:

```bash
git checkout -b review/<dataset-name>
```

---

## Step 2 — Install NeuroAudit

```bash
pip install -r neuroaudit/requirements.txt
```

> [!TIP]
> Using a virtual environment (`python -m venv .venv && source .venv/bin/activate`) is recommended to avoid dependency conflicts.

---

## Step 3 — Configure LLM Access (optional)

NeuroAudit's AI-assisted features (task regeneration, chat help) require a local `config.json`.

Create `neuroaudit/config.json`:

```json
{
  "model": "claude-opus-4-7",
  "key": "sk-ant-...",
  "ANTHROPIC_BASE_URL": ""
}
```

> [!NOTE]
> If you skip this step, all manual review, editing, and save features still work — only LLM-powered actions will be unavailable.

---

## Step 4 — Start NeuroAudit

```bash
python -m neuroaudit
```

Open your browser at **http://127.0.0.1:5000**.

---

## Step 5 — Review a Dataset

The left sidebar lists all datasets. Click one to open its review panel.

### 5.1 Check the Header Metadata

Verify the top-line fields are correct:

| Field | What to check |
|---|---|
| `Category` | One of 6 valid values (Action/Output, Sensory/Response, …) |
| `Subjects` | Matches the paper or dataset description |
| `Channels` | Consistent with File Scan Result |
| `Sampling Rate` | Consistent with File Scan Result |

### 5.2 Review the Paradigm Section

Read the paradigm description. Check for:
- Accurate description of the experimental task
- Correct subject count and equipment
- No fabricated event details not present in the data

### 5.3 Review the Tasks Section

Each task block specifies an ML task. Key fields to verify:

| Field | What to check |
|---|---|
| `Task Type` | `classification` or `regression` — matches the paradigm |
| `Label Route` | `event`, `misc`, or `info` — consistent with File Scan Result |
| `Target Events` | Event IDs that actually appear in the Event Structure table |
| `Evidence` | Non-empty; cites event IDs or paper reference |
| `Meta Level` | `raw` or `super` — should match Kernel Responsibilities |

> [!WARNING]
> Do not add tasks for event IDs that do not appear in the **File Scan Result → Event Structure** table. The scan result is ground truth.

### 5.4 Add or Edit Data Quality Notes

Use bullet points (`- `) to note any known issues:
- Missing channels or subjects
- Ambiguous event codes
- Known artifacts or imbalanced classes

### 5.5 Validate

Click the **Validate** button in the UI. All rules must pass before submission. Common warnings:

| Rule | Fix |
|---|---|
| `classical_task_has_evidence` | Add an Evidence line referencing event IDs or the paper |
| `super_meta_consistency` | If any task has `Meta Level: super`, ensure Kernel Responsibilities shows `Super Meta Required: Yes` |
| `target_events_exist` | Remove or correct event IDs not found in the Event Structure table |

### 5.6 Save

Click **Save** to write the updated `analysis.md` to disk.

---

## Step 6 — Commit & Submit PR

```bash
git add dataset_document/<dataset-name>/analysis.md
git commit -m "review(<dataset-name>): fix task definitions and quality notes"
git push origin review/<dataset-name>
```

Then open a Pull Request on GitHub:
- **Base repository**: `EEG-BenchmarkSkill/EEGBenchmarkSKILL`
- **Base branch**: `dev`
- **Compare branch**: `review/<dataset-name>` on your fork

In the PR description, briefly note:
- Which sections you changed and why
- Whether any validation warnings remain (and why they are acceptable)

---

## Tips

- You can review multiple datasets in one branch; just name it `review/batch-<date>` instead.
- The **rulebook** tab inside NeuroAudit shows the full set of reviewer-facing rules.
- If you are unsure about a field, leave a `[to_agent: please check X]` comment in the document — the pipeline will process it in the next generation run.
