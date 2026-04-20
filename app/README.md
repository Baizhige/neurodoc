# EEG Audit Tool

Local HTML audit UI for reviewing EEG dataset documentation.

## Setup

```bash
cd /path/to/BIDS_description/app
pip install flask
python server.py
```

Then open http://127.0.0.1:5000 in your browser.

## Usage

1. Select a dataset from the left sidebar (filter by Category if needed)
2. Review each of the 6 steps in order:
   - **Meta** — dataset header fields, category, manual review notes
   - **Paradigm** — experimental paradigm description (edit + preview)
   - **File Scan Result** — Event Structure table, MISC summary, Info completeness
   - **Tasks** — Classical/Potential task definitions (with target_events validation)
   - **DQN** — Data Quality Notes
   - **Kernel** — Super Meta Required toggle + Status dropdown
3. Click **Save File** to write changes back to `analysis.md`

## LLM Integration

Open **Settings** (top right) and configure:
- **BASE_URL** — any OpenAI-compatible endpoint (e.g. `https://api.openai.com/v1`)
- **ANTHROPIC_BASE_URL** — any Anthropic-compatible endpoint (e.g. `https://api.kimi.com/coding/`)
- **API Key** — your API key
- **Model** — model name (e.g. `gpt-4o`)

Only one of `BASE_URL` or `ANTHROPIC_BASE_URL` may be configured at a time.

Then use the **LLM Chat** tab in the right panel to ask questions about the current dataset and step.

## Files

- `server.py` — Flask backend
- `index.html` — SPA frontend
- `rulebook.md` — documentation rulebook (shown in right panel)
- `config.json` — LLM config (auto-created on first save)
