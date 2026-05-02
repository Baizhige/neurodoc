# NeuroDoc Agent Skill System

`neurodoc/skills/` contains dialog-driven agent skill definitions for processing EEG
datasets with NeuroDoc. Install once, then talk to your AI assistant naturally — no
commands to memorize.

---

## Quick Install

```bash
# From the project root
python -m neurodoc.skills.install
```

This creates (or updates) `CLAUDE.md` and `AGENTS.md` at the project root, which are
read automatically by Claude Code and Codex at session start.

---

## What it does

After installation, open a new AI session and say something like:

> "I want to process dataset openneuro_ds001784"

The agent will:
1. Check your machine config (LLM key, dataset path, EEGUnity path)
2. Ask what you want to do — generate, update, fix kernel, or validate
3. Run the right pipeline commands for you
4. Explain any errors in plain language
5. Guide you to a working `analysis.md` and `kernel.py`

You never need to remember which `python -m neurodoc.*` command to run.

---

## Supported Workflows

| Workflow | What triggers it |
|----------|-----------------|
| **Generate new document** | "generate", "first time", no analysis.md yet |
| **Update existing document** | "update", "re-scan", "add task" |
| **Write or fix a kernel** | "fix kernel", kernel phase failure |
| **Validate and fix errors** | "validate", "detect", after any change |

---

## File Overview

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Skill definition for Claude Code (loaded via `@neurodoc/skills/CLAUDE.md`) |
| `AGENTS.md` | Skill definition for Codex / OpenAI Agents (inlined into root `AGENTS.md`) |
| `install.py` | One-command installer that wires these files into the project root |
| `README.md` | This file |

---

## Manual Installation

If you prefer not to use the installer:

**Claude Code**: Add this line to your project's `CLAUDE.md`:
```
@neurodoc/skills/CLAUDE.md
```

**Codex / OpenAI Agents**: Copy the contents of `AGENTS.md` into your root `AGENTS.md`.

---

## Updating the Skill

After a NeuroDoc upgrade, re-run the installer:
```bash
python -m neurodoc.skills.install
```

The installer is idempotent — it will not add duplicate entries.

---

## Requirements

- Python 3.8+
- A configured machine config (the skill will guide you through setup if missing)
- EEGUnity installed and pointed to by `eegunity_path` in the machine config
- An Anthropic or OpenAI-compatible API key
