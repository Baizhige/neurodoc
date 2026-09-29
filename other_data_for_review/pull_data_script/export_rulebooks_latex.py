#!/usr/bin/env python
"""
Export NeuroDoc semantic rulebook (YAML) and NeuroAudit rulebook (Markdown)
to LaTeX appendix files.

Usage:
    python pull_data_script/export_rulebooks_latex.py
"""
from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml as _yaml
    def _load_yaml(text: str) -> dict:
        return _yaml.safe_load(text)
except ImportError:
    raise SystemExit("PyYAML is required: pip install pyyaml")

NEURODOC_YAML = Path(r"E:\github_projects\BIDS_description\neurodoc\rulebook\semantic_rules.yaml")
NEUROAUDIT_MD = Path(r"E:\github_projects\BIDS_description\neuroaudit\rulebook.md")
OUTPUT_DIR    = Path("pull_data_script")

# ---------------------------------------------------------------------------
# Shared text helpers
# ---------------------------------------------------------------------------

_LATEX_SPECIALS = [
    # ASCII specials — must come first so inserted LaTeX \ isn't re-escaped
    ("\\", r"\textbackslash{}"),
    ("&",  r"\&"),
    ("%",  r"\%"),
    ("$",  r"\$"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
    # Unicode → LaTeX (after ASCII escaping so the \ in $\beta$ is not touched)
    # Greek lower-case
    ("α", r"$\alpha$"),   ("β", r"$\beta$"),    ("γ", r"$\gamma$"),
    ("δ", r"$\delta$"),   ("ε", r"$\varepsilon$"), ("η", r"$\eta$"),
    ("θ", r"$\theta$"),   ("λ", r"$\lambda$"),  ("μ", r"$\mu$"),
    ("ν", r"$\nu$"),      ("ξ", r"$\xi$"),      ("π", r"$\pi$"),
    ("ρ", r"$\rho$"),     ("σ", r"$\sigma$"),   ("τ", r"$\tau$"),
    ("φ", r"$\varphi$"),  ("χ", r"$\chi$"),     ("ψ", r"$\psi$"),
    ("ω", r"$\omega$"),
    # Greek upper-case (common in EEG)
    ("Δ", r"$\Delta$"),   ("Θ", r"$\Theta$"),   ("Σ", r"$\Sigma$"),
    ("Ω", r"$\Omega$"),   ("Γ", r"$\Gamma$"),   ("Λ", r"$\Lambda$"),
    # Math symbols
    ("≠", r"$\neq$"),     ("≤", r"$\leq$"),     ("≥", r"$\geq$"),
    ("±", r"$\pm$"),      ("×", r"$\times$"),   ("÷", r"$\div$"),
    ("∞", r"$\infty$"),   ("≈", r"$\approx$"),  ("∝", r"$\propto$"),
    ("→", r"$\rightarrow$"), ("←", r"$\leftarrow$"),
    ("↑", r"$\uparrow$"), ("↓", r"$\downarrow$"),
    ("°", r"$^{\circ}$"),
    ("−", r"$-$"),        # U+2212 minus sign
    ("·", r"$\cdot$"),    # U+00B7 middle dot
    # Typography
    ("'", r"'"),   ("'", r"`"),
    (""", r"''"),  (""", r"``"),
    ("–", r"--"),  ("—", r"---"),
    ("…", r"\\ldots{}"),
]


def latex_escape(text: str) -> str:
    for char, rep in _LATEX_SPECIALS:
        text = text.replace(char, rep)
    return text


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def format_rule_id(rule_id: str) -> str:
    """Render a rule_id (underscore-separated) as breakable \texttt{...}."""
    escaped = latex_escape(rule_id)          # _ → \_
    breakable = escaped.replace(r"\_", r"\_\allowbreak{}")
    return r"\texttt{" + breakable + r"}"


def convert_inline(text: str) -> str:
    """Escape text and convert `code` and **bold** spans to LaTeX."""
    parts = re.split(r"(`[^`\n]+`)", text)
    result = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            inner = latex_escape(part[1:-1]).replace("\x00", r"\textbar{}")
            result.append(r"\texttt{" + inner + r"}")
        else:
            s = latex_escape(part).replace("\x00", r"\textbar{}")
            s = re.sub(r"\*\*(.+?)\*\*", lambda m: r"\textbf{" + m.group(1) + r"}", s)
            result.append(s)
    return "".join(result)


# ---------------------------------------------------------------------------
# Markdown table helpers (shared by both renderers)
# ---------------------------------------------------------------------------

def _parse_md_row(line: str) -> list[str]:
    """Split a markdown table row, honouring \\| escaped pipes."""
    line = line.replace(r"\|", "\x00")           # protect escaped pipes
    cells = [c.strip() for c in line.strip("|").split("|")]
    return cells  # \x00 placeholders resolved later by convert_inline


def _is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\|[\s\-|:]+\|$", line.strip()))


def render_md_table(lines_block: list[str]) -> str:
    """Convert a list of markdown table lines to a booktabs LaTeX tabular."""
    rows = [_parse_md_row(ln) for ln in lines_block if not _is_table_sep(ln)]
    if not rows:
        return ""
    headers = rows[0]
    data    = rows[1:]
    n = len(headers)
    # equal-width p columns so cells wrap
    col_w = r"\dimexpr 0.88\linewidth/" + str(n) + r"\relax"
    spec  = ("p{" + col_w + "}") * n
    out = [
        r"\begingroup\footnotesize",
        r"\begin{tabular}{@{}" + spec + r"@{}}",
        r"\toprule",
        " & ".join(r"\textbf{" + convert_inline(h) + r"}" for h in headers) + r" \\",
        r"\midrule",
    ]
    for row in data:
        padded = (row + [""] * n)[:n]
        out.append(" & ".join(convert_inline(c) for c in padded) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\endgroup"]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# YAML rulebook
# ---------------------------------------------------------------------------

def _parse_hc_blocks(yaml_text: str) -> list[tuple[str, str]]:
    """Extract (HC-N, description) from YAML comment header."""
    comment_lines: list[str] = []
    for line in yaml_text.splitlines():
        if line.startswith("#"):
            comment_lines.append(line[1:])
        elif line.strip():
            break
    raw = "\n".join(comment_lines)
    hcs: list[tuple[str, str]] = []
    for m in re.finditer(r"(HC-\d+)\s+(.*?)(?=\n\s*HC-\d+|\Z)", raw, re.DOTALL):
        hc_id = m.group(1)
        desc  = re.sub(r"\s+", " ", m.group(2)).strip()
        desc  = re.sub(r"\s*-{3,}\s*$", "", desc).strip()
        if desc:
            hcs.append((hc_id, desc))
    return hcs


def _get_rule_groups(yaml_text: str) -> list[tuple[str, str, list[str]]]:
    """Return [(group_letter, group_name, [rule_id, ...])] in document order."""
    groups: list[tuple[str, str, list[str]]] = []
    cur_letter = cur_name = ""
    cur_ids: list[str] = []
    for line in yaml_text.splitlines():
        m = re.match(r"\s*#\s*---\s*Group\s+([^:]+):\s*(.+?)\s*---", line)
        if m:
            if cur_ids:
                groups.append((cur_letter, cur_name, cur_ids))
            cur_letter, cur_name, cur_ids = m.group(1).strip(), m.group(2).strip(), []
            continue
        m2 = re.match(r"\s*-\s*id:\s*['\"]?(\w+)['\"]?", line)
        if m2 and cur_letter:
            cur_ids.append(m2.group(1))
    if cur_ids:
        groups.append((cur_letter, cur_name, cur_ids))
    return groups


def render_yaml_rulebook(yaml_path: Path) -> str:
    yaml_text   = yaml_path.read_text(encoding="utf-8")
    data        = _load_yaml(yaml_text)
    rules_by_id = {r["id"]: r for r in data.get("rules", [])}
    hcs         = _parse_hc_blocks(yaml_text)
    groups      = _get_rule_groups(yaml_text)

    out: list[str] = []

    out.append(
        r"\noindent This appendix summarizes a programmatic encoding of machine-checkable provisions "
        r"from the shared entry rulebook, as used by \texttt{detect.py} to check "
        r"\texttt{analysis.md} and kernel files. Check types include "
        r"\texttt{section\_exists}, \texttt{pattern}, \texttt{field\_value}, and "
        r"\texttt{cross\_check}.\par\smallskip"
    )

    # ---- outer wrapper box ----
    out.append(
        r"\begin{tcolorbox}[breakable,enhanced,"
        r"colback=white,colframe=gray!50,"
        r"boxrule=0.8pt,arc=4pt,left=8pt,right=8pt,top=6pt,bottom=6pt,"
        r"title={\normalsize\bfseries NeuroDoc Semantic Rulebook},"
        r"coltitle=black,colbacktitle=gray!15,titlerule=0.5pt]"
    )

    # ---- HC section ----
    if hcs:
        out.append(r"\noindent\rule{\linewidth}{0.4pt}\par\smallskip")
        out.append(r"\noindent{\bfseries\small Hard Constraints (HC)}")
        out.append(r"{\footnotesize\ ---\ enforced in generation pipeline; not detectable by \texttt{detect.py}}\par\smallskip")
        for hc_id, desc in hcs:
            out.append(
                r"\noindent{\footnotesize\textbf{" + latex_escape(hc_id) + r".}~"
                + convert_inline(desc) + r"}\par\smallskip"
            )
        out.append(r"\noindent\rule{\linewidth}{0.4pt}\par\smallskip")

    # ---- rule groups as tabulars ----
    out.append(r"\noindent{\bfseries\small Semantic Check Rules}\par\smallskip")

    for letter, name, rule_ids in groups:
        if not rule_ids:
            continue
        out.append(
            r"\smallskip\noindent{\footnotesize\bfseries Group~"
            + latex_escape(letter) + r":~" + latex_escape(name)
            + r"}\par\smallskip"
        )
        out.append(r"\begingroup\footnotesize")
        out.append(r"\begin{tabular}{@{}p{0.22\linewidth}ll p{0.46\linewidth}@{}}")
        out.append(r"\toprule")
        out.append(r"\textbf{Rule ID} & \textbf{Sev.} & \textbf{Target} & \textbf{Description} \\")
        out.append(r"\midrule")
        for rule_id in rule_ids:
            rule = rules_by_id.get(rule_id)
            if not rule:
                continue
            sev    = rule.get("severity", "")
            target = rule.get("target", "")
            desc   = rule.get("desc", "")
            sev_tex = r"\textbf{[E]}" if sev == "error" else r"\textbf{[W]}"
            out.append(
                format_rule_id(rule_id) + r" & "
                + sev_tex + r" & \texttt{" + latex_escape(target) + r"} & "
                + convert_inline(desc) + r" \\"
            )
            out.append(r"\addlinespace[1pt]")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}")
        out.append(r"\endgroup")

    out.append(r"\end{tcolorbox}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Markdown rulebook
# ---------------------------------------------------------------------------

def _close_list(out: list[str], in_list: str | None) -> None:
    if in_list == "enum":
        out.append(r"\end{enumerate}")
    elif in_list == "bullet":
        out.append(r"\end{itemize}")


def render_md_rulebook(md_path: Path, start_marker: str = "# Part I") -> str:
    text = md_path.read_text(encoding="utf-8", errors="replace")

    # Trim to start_marker
    idx = text.find("\n" + start_marker)
    text = text[idx + 1:] if idx != -1 else text[text.find(start_marker):]

    lines = text.splitlines()
    out: list[str] = []
    in_list: str | None = None
    part_count = 0

    def close_list() -> None:
        nonlocal in_list
        _close_list(out, in_list)
        in_list = None

    # ---- outer wrapper box ----
    out.append(
        r"\begin{tcolorbox}[breakable,enhanced,"
        r"colback=white,colframe=gray!50,"
        r"boxrule=0.8pt,arc=4pt,left=8pt,right=8pt,top=6pt,bottom=6pt,"
        r"title={\normalsize\bfseries NeuroAudit Rulebook v1.0.0},"
        r"coltitle=black,colbacktitle=gray!15,titlerule=0.5pt]"
    )
    out.append(r"\small")

    i = 0
    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        # ---- fenced code block (any indentation) ----
        if re.match(r"^\s*```", line):
            close_list()
            i += 1
            code_lines: list[str] = []
            while i < len(lines):
                if re.match(r"^\s*```", lines[i]):
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            out.append(r"\begin{quote}\ttfamily\footnotesize")
            for cl in code_lines:
                # strip up to 3-space indent (fence indentation) then escape verbatim
                content = re.sub(r"^   ", "", cl)
                out.append(latex_escape(content) + r"\\")
            out.append(r"\end{quote}")
            continue

        # ---- markdown table ----
        if stripped.startswith("|") and stripped.endswith("|"):
            if i + 1 < len(lines) and _is_table_sep(lines[i + 1].strip()):
                close_list()
                tbl: list[str] = [stripped]
                i += 1  # skip separator line
                i += 1
                while i < len(lines) and lines[i].strip().startswith("|"):
                    tbl.append(lines[i].strip())
                    i += 1
                out.append(render_md_table(tbl))
                continue

        # ---- Part heading ----
        if re.match(r"^#\s+Part\s+", line):
            close_list()
            part_text = re.sub(r"^#\s+", "", line).strip()
            out.append(r"\par\bigskip")
            out.append(r"\noindent\rule{\linewidth}{0.8pt}\par\nopagebreak")
            out.append(r"\noindent{\bfseries\normalsize " + convert_inline(part_text) + r"}\par\nopagebreak")
            out.append(r"\noindent\rule{\linewidth}{0.8pt}\par\smallskip")
            part_count += 1
            i += 1
            continue

        # ---- Chapter heading ----
        if re.match(r"^##\s+Chapter\s+", line):
            close_list()
            ch_text = re.sub(r"^##\s+", "", line).strip()
            out.append(r"\medskip\noindent{\bfseries\normalsize " + convert_inline(ch_text) + r"}")
            out.append(r"\par\nopagebreak\noindent\rule{\linewidth}{0.4pt}\par\smallskip")
            i += 1
            continue

        # ---- Article heading ----
        if re.match(r"^###\s+Article\s+", line):
            close_list()
            art_text = re.sub(r"^###\s+", "", line).strip()
            out.append(r"\smallskip\noindent{\bfseries\normalsize " + convert_inline(art_text) + r"}\par\smallskip")
            i += 1
            continue

        # ---- Horizontal rule ----
        if stripped == "---":
            close_list()
            out.append(r"\par\medskip\noindent\rule{\linewidth}{0.3pt}\par\medskip")
            i += 1
            continue

        # ---- Empty line ----
        if not stripped:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and in_list:
                nxt = lines[j].strip()
                if in_list == "enum"   and re.match(r"^\d+\.\s", nxt): i += 1; continue
                if in_list == "bullet" and nxt.startswith("- "):        i += 1; continue
            close_list()
            out.append("")
            i += 1
            continue

        # ---- Numbered list item (not indented) ----
        if re.match(r"^\d+\.\s", stripped) and not line[0].isspace():
            if in_list != "enum":
                close_list()
                out.append(r"\begin{enumerate}[leftmargin=1.5em,noitemsep,topsep=2pt]")
                in_list = "enum"
            item_text = re.sub(r"^\d+\.\s+", "", stripped)

            # Collect indented sub-content (nested bullets, code fences, tables)
            nested_lines: list[str] = []
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                nls = nl.strip()
                if nl and nl[0].isspace() and nls:
                    nested_lines.append(nl)
                    j += 1
                elif not nls:
                    if j + 1 < len(lines) and lines[j + 1] and lines[j + 1][0].isspace():
                        nested_lines.append(nl)
                        j += 1
                        continue
                    break
                else:
                    break

            out.append(r"\item " + convert_inline(item_text))

            if nested_lines:
                # Check what the nested content is
                non_empty = [nl for nl in nested_lines if nl.strip()]
                first = non_empty[0].strip() if non_empty else ""

                if re.match(r"^```", first):
                    # nested code fence
                    k = 0
                    code_inner: list[str] = []
                    in_fence = False
                    for nl in nested_lines:
                        ns = nl.strip()
                        if re.match(r"^```", ns):
                            if not in_fence:
                                in_fence = True
                            else:
                                break
                        elif in_fence:
                            code_inner.append(nl)
                    out.append(r"\begin{quote}\ttfamily\footnotesize")
                    for cl in code_inner:
                        out.append(latex_escape(re.sub(r"^   ", "", cl)) + r"\\")
                    out.append(r"\end{quote}")

                elif first.startswith("|") and len(non_empty) > 1 and _is_table_sep(non_empty[1].strip()):
                    # nested table
                    tbl = [nl.strip() for nl in non_empty]
                    out.append(render_md_table(tbl))

                elif re.match(r"^\d+\.", first) or first.startswith("- "):
                    is_enum_nested = all(
                        re.match(r"^\d+\.", nl.strip()) or not nl.strip()
                        for nl in non_empty
                    )
                    env = "enumerate" if is_enum_nested else "itemize"
                    out.append(r"\begin{" + env + r"}[leftmargin=1.2em,noitemsep,topsep=1pt]")
                    for nl in non_empty:
                        ns = re.sub(r"^(?:\d+\.|-)\s*", "", nl.strip())
                        out.append(r"\item " + convert_inline(ns))
                    out.append(r"\end{" + env + r"}")

                else:
                    # plain continuation text
                    for nl in non_empty:
                        out.append(convert_inline(nl.strip()))

            i = j
            continue

        # ---- Bullet list item (not indented) ----
        if stripped.startswith("- ") and not line[0].isspace():
            if in_list != "bullet":
                close_list()
                out.append(r"\begin{itemize}[leftmargin=1.5em,noitemsep,topsep=2pt]")
                in_list = "bullet"
            out.append(r"\item " + convert_inline(stripped[2:]))
            i += 1
            continue

        # ---- Skip indented continuation lines already consumed ----
        if line and line[0].isspace() and stripped:
            i += 1
            continue

        # ---- Plain paragraph text ----
        if stripped:
            close_list()
            out.append(r"\noindent " + convert_inline(stripped) + r"\par\smallskip")
        i += 1

    close_list()
    out.append(r"\normalsize")
    out.append(r"\end{tcolorbox}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_PREAMBLE_HINT = """\
% Required packages (add to your preamble if not already present):
%   \\usepackage[skins,breakable]{tcolorbox}
%   \\usepackage{enumitem}
%   \\usepackage{booktabs}
%   \\usepackage{xcolor}

"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("processing: semantic_rules.yaml")
    yaml_out = OUTPUT_DIR / "appendix_semantic_rules.tex"
    yaml_out.write_text(_PREAMBLE_HINT + render_yaml_rulebook(NEURODOC_YAML), encoding="utf-8")
    print(f"written: {yaml_out}")

    print("processing: neuroaudit/rulebook.md")
    md_out = OUTPUT_DIR / "appendix_neuroaudit_rulebook.tex"
    md_out.write_text(_PREAMBLE_HINT + render_md_rulebook(NEUROAUDIT_MD, start_marker="# Part I"), encoding="utf-8")
    print(f"written: {md_out}")


if __name__ == "__main__":
    main()
