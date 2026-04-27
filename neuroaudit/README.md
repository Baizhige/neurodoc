# NeuroAudit

Web UI for reviewing and editing dataset documentation under `dataset_document/`.

## Run

```bash
cd /path/to/BIDS_description
pip install -r neuroaudit/requirements.txt
python -m neuroaudit
```

Open `http://127.0.0.1:5000`.

## Scope

- `server.py`: Flask backend for dataset browsing, saving, reference parsing, and LLM actions
- `index.html`: single-page review UI
- `template_checker.py` / `template_spec.py`: structural validation for `analysis.md`
- `rulebook.md`: reviewer-facing documentation shown inside the UI
- `skills/`: category-specific prompt fragments used by the task regeneration flow

## Architecture

- Dataset documents are read from `dataset_document/<dataset>/analysis.md`.
- Semantic validation and LLM transport are provided by `neurodoc.api`.
- NeuroAudit does not depend on `neurodoc` internal file layout beyond that stable API.

## Notes

- `config.json` stores local UI-side LLM settings.
- `Script/` is intentionally ignored and is not part of the NeuroAudit runtime contract.
