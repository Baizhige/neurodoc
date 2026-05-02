"""
neurodoc/skills/install.py

One-command installer for the NeuroDoc agent skill.

Usage:
    python -m neurodoc.skills.install

What it does:
    1. Finds (or creates) a CLAUDE.md at the project root.
    2. Appends an @-import directive so Claude Code loads the skill automatically.
    3. Creates an AGENTS.md at the project root for Codex / OpenAI Agents.
    4. Prints a confirmation with next steps.
"""

from __future__ import annotations

import os
import sys
import textwrap

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILLS_DIR = _THIS_DIR                         # neurodoc/skills/
_REPO_ROOT = os.path.dirname(os.path.dirname(_SKILLS_DIR))  # project root


def _rel(path: str) -> str:
    """Return a forward-slash path relative to repo root."""
    return os.path.relpath(path, _REPO_ROOT).replace(os.sep, "/")


# ---------------------------------------------------------------------------
# CLAUDE.md management
# ---------------------------------------------------------------------------

CLAUDE_IMPORT_LINE = "@neurodoc/skills/CLAUDE.md"

CLAUDE_HEADER = textwrap.dedent("""\
    # Project Instructions

    This file is read automatically by Claude Code at the start of every session.

""")


def _install_claude_md() -> None:
    claude_path = os.path.join(_REPO_ROOT, "CLAUDE.md")

    if os.path.exists(claude_path):
        with open(claude_path, "r", encoding="utf-8") as f:
            content = f.read()
        if CLAUDE_IMPORT_LINE in content:
            print(f"[skip]  CLAUDE.md already contains '{CLAUDE_IMPORT_LINE}'")
            return
        # Append the import at the end
        with open(claude_path, "a", encoding="utf-8") as f:
            f.write(f"\n{CLAUDE_IMPORT_LINE}\n")
        print(f"[ok]    Appended '{CLAUDE_IMPORT_LINE}' to existing CLAUDE.md")
    else:
        # Create a minimal CLAUDE.md
        with open(claude_path, "w", encoding="utf-8") as f:
            f.write(CLAUDE_HEADER)
            f.write(f"{CLAUDE_IMPORT_LINE}\n")
        print(f"[ok]    Created CLAUDE.md with '{CLAUDE_IMPORT_LINE}'")


# ---------------------------------------------------------------------------
# AGENTS.md management (Codex / OpenAI Agents)
# ---------------------------------------------------------------------------

AGENTS_IMPORT_LINE = "# @neurodoc/skills/AGENTS.md"

AGENTS_PREAMBLE = textwrap.dedent("""\
    # Project Agent Instructions

    This file is read automatically by Codex / OpenAI Agents at the start of every session.
    For detailed NeuroDoc workflow guidance, see neurodoc/skills/AGENTS.md.

""")

_SKILLS_AGENTS_PATH = os.path.join(_SKILLS_DIR, "AGENTS.md")


def _install_agents_md() -> None:
    agents_path = os.path.join(_REPO_ROOT, "AGENTS.md")

    if not os.path.exists(_SKILLS_AGENTS_PATH):
        print("[warn]  neurodoc/skills/AGENTS.md not found — skipping AGENTS.md install")
        return

    # Read the skills AGENTS.md content
    with open(_SKILLS_AGENTS_PATH, "r", encoding="utf-8") as f:
        skills_content = f.read()

    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "neurodoc/skills/AGENTS.md" in existing:
            print("[skip]  AGENTS.md already references neurodoc/skills/AGENTS.md")
            return
        # Append the skills content
        with open(agents_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n<!-- neurodoc/skills/AGENTS.md -->\n\n")
            f.write(skills_content)
        print("[ok]    Appended NeuroDoc skill content to existing AGENTS.md")
    else:
        # Create a new AGENTS.md that embeds the skills content
        with open(agents_path, "w", encoding="utf-8") as f:
            f.write(AGENTS_PREAMBLE)
            f.write(f"<!-- neurodoc/skills/AGENTS.md -->\n\n")
            f.write(skills_content)
        print("[ok]    Created AGENTS.md with embedded NeuroDoc skill content")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("NeuroDoc skill installer")
    print(f"  Repo root : {_REPO_ROOT}")
    print(f"  Skills dir: {_rel(_SKILLS_DIR)}")
    print()

    _install_claude_md()
    _install_agents_md()

    print()
    print("Done. Next steps:")
    print("  1. Open a new Claude Code session in this repo.")
    print("     The skill will load automatically from CLAUDE.md.")
    print("  2. Say: 'I want to process dataset openneuro_ds001784'")
    print("     The agent will guide you through the full workflow.")
    print()
    print("  To update the skill after a NeuroDoc upgrade, re-run this installer.")


if __name__ == "__main__":
    main()
