# NeuroAudit

NeuroAudit is a local Flask web app for reviewing, editing, validating, and regenerating task definitions for EEG dataset documentation under `dataset_document/`.

The reviewer-facing rule source is [`rulebook.md`](rulebook.md), currently archived as v1.0.0.

## Run

```bash
cd /path/to/BIDS_description
pip install -r neuroaudit/requirements.txt
python -m neuroaudit
```

Open `http://127.0.0.1:5000`.

## Review Workflow

1. Select a dataset from the sidebar. NeuroAudit reads `dataset_document/<dataset>/analysis.md`.
2. Review metadata and paradigm text.
3. Review `File Scan Result`, `Event Structure`, optional `MISC Label Summary`, `Info`, and task definitions.
4. Review `Data Quality Notes` and `Kernel Responsibilities`.
5. Use preview and save controls to write the edited `analysis.md`.

The right panel exposes the step guide, the v1.0.0 rulebook, and chat-style LLM assistance.

## Rulebook Contract

- `rulebook.md` is the canonical English review policy for NeuroAudit.
- v1.0.0 preserves the design logic of the former draft v0.6 and stores legacy version notes inside the same document.
- Future rule changes should create a new rulebook version entry and avoid silently changing field schemas, status values, or task-validity boundaries.

## Project Scope

- `server.py`: Flask backend for dataset browsing, saving, reference parsing, and LLM actions
- `index.html`: single-page review UI
- `template_checker.py` / `template_spec.py`: structural validation for `analysis.md`
- `rulebook.md`: reviewer-facing documentation shown inside the UI
- `skills/`: category-specific prompt fragments used by the task regeneration flow
- `strict_tasks.py`: strict task regeneration and validation helpers

## Architecture

- Dataset documents are read from `dataset_document/<dataset>/analysis.md`.
- Semantic validation and LLM transport are provided by `neurodoc.api`.
- NeuroAudit does not depend on `neurodoc` internal file layout beyond that stable API.
- File-scan content is expected to come from the kernel/neurodoc pipeline; NeuroAudit edits and validates the resulting Markdown.

## Configuration

`config.json` stores local LLM endpoint, model, key, and proxy settings used by UI-triggered LLM calls. Treat it as local runtime configuration and avoid placing production credentials in shared commits.

LLM-assisted features may be unavailable when the endpoint, key, model, proxy, or optional reference-extraction dependencies are missing.

## Validation

NeuroAudit combines two validation layers:

- Structural checks from `template_checker.py` and `template_spec.py`.
- Semantic checks exposed through `neurodoc.api.check_analysis_text`.

The app is designed to surface validation issues for reviewer action; human reviewers remain responsible for final `completed` or `hallucination` status decisions.

## Maintenance Notes

- Keep app-facing documentation, UI hints, prompts, and comments in English.
- Do not change task schema, route semantics, or status rules without updating `rulebook.md` and its version archive.
- `Script/` is intentionally ignored and is not part of the NeuroAudit runtime contract.
