#!/usr/bin/env python
"""
Export analysis.md documents as a LaTeX appendix block.

Usage:
    python pull_data_script/export_doc_latex.py --dataset bcic_iv_2a bcic_iv_2b
    python pull_data_script/export_doc_latex.py --dataset bcic_iv_2a --output pull_data_script/my_appendix.tex
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_DATASET_DIR = Path(r"E:\github_projects\BIDS_description\dataset_document")
DEFAULT_OUTPUT = Path("pull_data_script") / "appendix_documents.tex"

# ---------------------------------------------------------------------------
# Text helpers
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
    ("’", r"'"),   ("‘", r"`"),
    ("”", r"''"),  ("“", r"``"),
    ("–", r"--"),  ("—", r"---"),
    ("…", r"\\ldots{}"),
]


def latex_escape(text: str) -> str:
    for char, rep in _LATEX_SPECIALS:
        text = text.replace(char, rep)
    return text


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def convert_inline(text: str) -> str:
    """Escape text and convert `code` and **bold** to LaTeX."""
    # Split on backtick spans first so we don't escape their content twice
    parts = re.split(r"(`[^`\n]+`)", text)
    result = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            result.append(r"\texttt{" + latex_escape(part[1:-1]) + r"}")
        else:
            s = latex_escape(part)
            # **bold**
            s = re.sub(r"\*\*(.+?)\*\*", lambda m: r"\textbf{" + m.group(1) + r"}", s)
            result.append(s)
    return "".join(result)


# ---------------------------------------------------------------------------
# Markdown parsers
# ---------------------------------------------------------------------------

_INLINE_FIELD_RE = re.compile(r"\*\*(?P<key>[^*]+?)\*\*:\s*(?P<value>[^|\n]+)")
_BQ_FIELD_RE = re.compile(r"^>\s+\*\*(?P<key>[^*]+?)\*\*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
_TASK_HEADING_RE = re.compile(
    r"^###\s+(?P<kind>Classical|Potential|Normal)\s+Task\s+(?P<idx>\d+)\s*:\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)


def parse_inline_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for m in _INLINE_FIELD_RE.finditer(text):
        k, v = clean(m.group("key")), clean(m.group("value"))
        if k and k not in fields:
            fields[k] = v
    return fields


def parse_bq_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for m in _BQ_FIELD_RE.finditer(text):
        k, v = clean(m.group("key")), clean(m.group("value"))
        if k and k not in fields:
            fields[k] = v
    return fields


def extract_h1(text: str) -> str:
    m = re.match(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return clean(m.group(1)) if m else ""


def extract_section(text: str, name: str) -> str:
    """Return content of a ## section, stripped."""
    pat = r"^##\s+" + re.escape(name) + r"\s*$"
    m = re.search(pat, text, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def split_task_blocks(tasks_text: str) -> list[tuple[str, int, str, str]]:
    matches = list(_TASK_HEADING_RE.finditer(tasks_text))
    result = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tasks_text)
        result.append((
            m.group("kind"),
            int(m.group("idx")),
            clean(m.group("title")),
            tasks_text[start:end].strip(),
        ))
    return result


def _field_pattern(name: str) -> str:
    return r"^\-\s+\*\*" + re.escape(name) + r"\*\*"


def extract_simple_field(block: str, name: str) -> str:
    m = re.search(_field_pattern(name) + r":\s*(.+?)\s*$", block, re.MULTILINE)
    return clean(m.group(1)) if m else ""


def extract_multiline_field(block: str, name: str) -> str:
    """Extract a field whose value continues on the following lines (e.g. a table)."""
    # empty-value form:  - **Name**:\n<content>
    m = re.search(_field_pattern(name) + r":\s*\n", block, re.MULTILINE)
    if m:
        start = m.end()
        nxt = re.search(r"^\-\s+\*\*", block[start:], re.MULTILINE)
        end = start + nxt.start() if nxt else len(block)
        return block[start:end].strip()
    # inline form as fallback
    return extract_simple_field(block, name)


def parse_md_table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not re.match(r"^\|[\s\-|:]+\|$", ln.strip())
    ]
    if not lines:
        return [], []

    def split_row(line: str) -> list[str]:
        return [clean(c) for c in line.strip("|").split("|")]

    return split_row(lines[0]), [split_row(ln) for ln in lines[1:]]


def parse_bullet_list(text: str) -> list[str]:
    items = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("- "):
            items.append(s[2:].strip())
    return [i for i in items if i]


def parse_evidence(block: str) -> list[str]:
    m = re.search(_field_pattern("Evidence") + r":\s*\n", block, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    nxt = re.search(r"^\-\s+\*\*", block[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(block)
    return parse_bullet_list(block[start:end])


# ---------------------------------------------------------------------------
# LaTeX rendering
# ---------------------------------------------------------------------------

# Rule thickness above each task heading: Classical is visually heavier
_TASK_RULE_WIDTH: dict[str, str] = {
    "Classical": "0.7pt",
    "Potential": "0.4pt",
    "Normal":    "0.2pt",
}

# ---- Column-width ratios for Target Definition tables — adjust to taste ----
TD_RATIO_3COL: list[int] = [4, 1, 4]   # Event ID | Y | Meaning
TD_RATIO_2COL: list[int] = [1, 4]       # Info Field | Y Mapping Notes
_TD_TABLE_WIDTH: float = 0.88           # total table width as fraction of \linewidth

# Font-size constants — one LaTeX step smaller than original (≈ −1 pt at 10 pt base).
# Adjust here to shift sizes globally; ladder: \normalsize→\small→\footnotesize→\scriptsize.
_SZ_TITLE = r"\small"        # tcolorbox title text    (was \normalsize)
_SZ_BADGE = r"\scriptsize"   # status badge            (was \footnotesize)
_SZ_META  = r"\footnotesize" # meta row, URL line      (was \small)
_SZ_BODY  = r"\footnotesize" # paradigm / notes body   (was \small)
_SZ_HEAD  = r"\footnotesize" # section-label text      (was \small)
_SZ_TASK  = r"\footnotesize" # task heading + fields   (was \small)
_SZ_EVID  = r"\scriptsize"   # evidence bullet items   (was \footnotesize)
_SZ_SCAN  = r"\scriptsize"   # scan tables & BQ meta   (was \footnotesize)
_SZ_TABLE = r"\footnotesize" # Target-Definition table (was \small)


def status_badge(status: str) -> str:
    label = latex_escape(status.replace("_", " ").title())
    return r"\colorbox{gray!20}{" + _SZ_BADGE + r"\sffamily\bfseries " + label + r"}"


def md_table_to_latex(
    headers: list[str],
    rows: list[list[str]],
    col_ratios: list[int] | None = None,
) -> str:
    if not headers or not rows:
        return ""
    n = len(headers)
    if col_ratios and len(col_ratios) == n:
        total = sum(col_ratios)
        spec = "".join(
            f"p{{{r * _TD_TABLE_WIDTH / total:.4f}\\linewidth}}" for r in col_ratios
        )
    else:
        col_w = r"\dimexpr " + f"{_TD_TABLE_WIDTH:.2f}" + r"\linewidth/" + str(n) + r"\relax"
        spec = ("p{" + col_w + "}") * n
    lines = [
        r"\begingroup" + _SZ_TABLE,
        r"\begin{tabular}{@{}" + spec + r"@{}}",
        r"\toprule",
        " & ".join(r"\textbf{" + convert_inline(h) + r"}" for h in headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        padded = (row + [""] * n)[:n]
        lines.append(" & ".join(convert_inline(c) for c in padded) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\endgroup"]
    return "\n".join(lines)


# ---- Scan-result rendering ----

# Total column-width budget as a fraction of \linewidth.
# Inter-column space = (n-1)*2*\tabcolsep; with \tabcolsep=2pt that is at most
# 4*(2*2pt)=16pt overhead for a 5-column table — well within any box width.
_SCAN_TABLE_WIDTH: float = 0.94

# Column-ratio presets — edit these numbers to widen/narrow individual columns.
# Event Structure: [Event ID, Count (total), Type, Meta Level, Meaning]
_SCAN_EVENT_COL_RATIOS: list[int] = [2, 2, 1, 1, 6]
# Info: [Field, Completeness, Notes]
_SCAN_INFO_COL_RATIOS: list[int] = [2, 2, 4]


def _scan_table_col_ratios(headers: list[str]) -> list[int] | None:
    """Return named ratio preset for known scan-result table shapes."""
    n = len(headers)
    last = headers[-1].lower() if headers else ""
    if n == 5 and "meaning" in last:
        return _SCAN_EVENT_COL_RATIOS
    if n == 3:
        return _SCAN_INFO_COL_RATIOS
    if n == 2:
        return [2, 5]
    return None


def _scan_table_to_latex(
    headers: list[str],
    rows: list[list[str]],
    col_ratios: list[int] | None = None,
    breakable_cols: set[int] | None = None,
) -> str:
    if not headers:
        return ""
    n = len(headers)
    if col_ratios and len(col_ratios) == n:
        total = sum(col_ratios)
        spec = "".join(
            f"p{{{r * _SCAN_TABLE_WIDTH / total:.4f}\\linewidth}}" for r in col_ratios
        )
    else:
        col_w = r"\dimexpr " + f"{_SCAN_TABLE_WIDTH:.2f}" + r"\linewidth/" + str(n) + r"\relax"
        spec = ("p{" + col_w + "}") * n
    lines = [
        r"\begingroup" + _SZ_SCAN + r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{@{}" + spec + r"@{}}",
        r"\toprule",
        " & ".join(r"\textbf{" + convert_inline(h) + r"}" for h in headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        padded = (row + [""] * n)[:n]
        cells = []
        for j, c in enumerate(padded):
            cell = convert_inline(c)
            if breakable_cols and j in breakable_cols:
                cell = cell.replace(r"\_", r"\_\allowbreak{}")
            cells.append(cell)
        lines.append(" & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\endgroup"]
    return "\n".join(lines)


def render_scan_result(scan_text: str) -> list[str]:
    """Render the ## File Scan Result section as structured LaTeX."""
    out: list[str] = []
    out.append(r"\noindent\rule{\linewidth}{0.4pt}\par\nopagebreak")
    out.append(r"\noindent{\bfseries" + _SZ_HEAD + r" File Scan Result}\par\smallskip")

    # Blockquote metadata  (> Key: Value  or  > **Key**: Value)
    bq_lines: list[str] = []
    for ln in scan_text.splitlines():
        m = re.match(r"^>\s*(.+?)\s*$", ln)
        if m:
            raw = re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(1))
            bq_lines.append(raw)

    if bq_lines:
        out.append(r"{" + _SZ_SCAN)
        for ln in bq_lines:
            km = re.match(r"^(.+?):\s*(.+)$", ln)
            if km:
                key = latex_escape(km.group(1).strip())
                val = convert_inline(km.group(2).strip())
                out.append(r"\noindent\textbf{" + key + r":}~" + val + r"\par\smallskip")
            else:
                out.append(r"\noindent " + convert_inline(ln) + r"\par\smallskip")
        out.append(r"}")

    # ### sub-sections (Event Structure, Info, …)
    sub_re = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    subsections = list(sub_re.finditer(scan_text))

    for i, m in enumerate(subsections):
        name = clean(m.group(1))
        start = m.end()
        end = subsections[i + 1].start() if i + 1 < len(subsections) else len(scan_text)
        content = scan_text[start:end].strip()

        out.append(
            r"\smallskip\noindent{" + _SZ_HEAD + r"\bfseries " + convert_inline(name) + r"}\par\smallskip"
        )

        tbl_lines = [ln.strip() for ln in content.splitlines() if ln.strip().startswith("|")]
        if tbl_lines:
            headers, rows = parse_md_table("\n".join(tbl_lines))
            if headers:
                is_info  = len(headers) == 3 and headers[0].lower() == "field"
                is_event = len(headers) == 5 and "meaning" in headers[-1].lower()
                breakable_cols: set[int] | None = {0} if (is_info or is_event) else None
                out.append(_scan_table_to_latex(headers, rows, _scan_table_col_ratios(headers), breakable_cols))

        non_tbl_lines = [
            ln for ln in content.splitlines()
            if ln.strip() and not ln.strip().startswith("|")
            and not re.match(r"^\|[\s\-|:]+\|$", ln.strip())
        ]
        if non_tbl_lines:
            items = parse_bullet_list("\n".join(non_tbl_lines))
            if items:
                out.append(r"\begin{itemize}[leftmargin=1.4em,noitemsep,topsep=2pt]")
                for item in items:
                    out.append(r"\item{" + _SZ_BODY + r" " + convert_inline(item) + r"}")
                out.append(r"\end{itemize}")

    # Fallback: no subsections and no blockquotes
    if not subsections and not bq_lines:
        notes = parse_bullet_list(scan_text)
        if notes:
            out.append(r"\begin{itemize}[leftmargin=1.4em,noitemsep,topsep=2pt]")
            for note in notes:
                out.append(r"\item{" + _SZ_BODY + r" " + convert_inline(note) + r"}")
            out.append(r"\end{itemize}")
        else:
            out.append(r"{" + _SZ_BODY + r" " + convert_inline(clean(scan_text)) + r"}")

    return out


def render_task(kind: str, idx: int, title: str, block: str, add_rule: bool = True) -> str:
    """Render a task as inline text (no inner tcolorbox) with a rule separator."""
    task_type    = extract_simple_field(block, "Task Type")
    epoch_method = extract_simple_field(block, "Epoch Method")
    epoch_params = extract_simple_field(block, "Epoch Parameters")
    label_route  = extract_simple_field(block, "Label Route")
    meta_level   = extract_simple_field(block, "Meta Level")
    notes        = extract_simple_field(block, "Notes")

    td_raw = extract_multiline_field(block, "Target Definition")
    td_latex = ""
    if td_raw:
        h, r = parse_md_table(td_raw)
        if len(h) == 3:
            td_latex = md_table_to_latex(h, r, col_ratios=TD_RATIO_3COL)
        elif len(h) == 2:
            td_latex = md_table_to_latex(h, r, col_ratios=TD_RATIO_2COL)
        else:
            td_latex = md_table_to_latex(h, r)

    evidence = parse_evidence(block)
    rule_w = _TASK_RULE_WIDTH.get(kind, "0.4pt")

    lines: list[str] = []

    # Thin rule + task heading (no inner box)
    if add_rule:
        lines.append(r"\noindent\rule{\linewidth}{" + rule_w + r"}\par\nopagebreak")
    lines.append(
        r"\noindent{" + _SZ_TASK + r"\bfseries " + latex_escape(kind)
        + r"~Task~" + str(idx) + r":} "
        + r"{" + _SZ_TASK + r" " + convert_inline(title) + r"}\par\smallskip"
    )

    # Core fields as a compact two-column tabular
    field_rows: list[tuple[str, str]] = []
    if task_type:     field_rows.append(("Type",         convert_inline(task_type)))
    if epoch_method:  field_rows.append(("Epoch Method", convert_inline(epoch_method)))
    if epoch_params:  field_rows.append(("Epoch Params", convert_inline(epoch_params)))
    if label_route:   field_rows.append(("Label Route",  convert_inline(label_route)))
    if meta_level:    field_rows.append(("Meta Level",   convert_inline(meta_level)))

    if field_rows:
        lines.append(r"{" + _SZ_TASK + r"\begin{tabular}{@{}lp{0.62\linewidth}@{}}")
        for label, val in field_rows:
            lines.append(r"\textbf{" + latex_escape(label) + r"} & " + val + r" \\")
        lines.append(r"\end{tabular}}")

    if td_latex:
        lines.append(r"\par\noindent{" + _SZ_TASK + r"\bfseries Target Definition:}\par\smallskip")
        lines.append(td_latex)

    if evidence:
        lines.append(r"\par\noindent{" + _SZ_TASK + r"\itshape Evidence:}\par")
        lines.append(r"\begin{itemize}[leftmargin=1.3em,noitemsep,topsep=1pt]")
        for item in evidence:
            lines.append(r"\item[" + _SZ_EVID + r"$\cdot$] {" + _SZ_EVID + r" " + convert_inline(item) + r"}")
        lines.append(r"\end{itemize}")

    if notes and notes.strip().lower() not in ("", "n/a", "none", "-"):
        lines.append(r"\par\noindent{" + _SZ_TASK + r"\bfseries Notes:} {" + _SZ_TASK + r" " + convert_inline(notes) + r"}")

    return "\n".join(lines)


def render_document(text: str) -> str:
    title = extract_h1(text)
    inline_fields = parse_inline_fields(text)
    bq_fields = parse_bq_fields(text)

    inline_fields["Manual Review"] = "Anonymous"

    status     = clean(bq_fields.get("Status", "missing")).lower()
    super_meta = clean(bq_fields.get("Super Meta Required", ""))

    paradigm_text = extract_section(text, "Paradigm")
    tasks_text    = extract_section(text, "Tasks")
    scan_text     = extract_section(text, "File Scan Result")
    quality_text  = extract_section(text, "Data Quality Notes")

    task_blocks   = split_task_blocks(tasks_text) if tasks_text else []
    quality_notes = parse_bullet_list(quality_text)

    dataset_id = inline_fields.get("Dataset", "").strip("`").strip()
    year       = inline_fields.get("Year", "")
    category   = inline_fields.get("Category", "")
    subjects   = inline_fields.get("Subjects", "")
    channels   = inline_fields.get("Channels", "")
    sr         = inline_fields.get("Sampling Rate", "")
    files_ok   = inline_fields.get("Files (Completed)", "")
    url        = inline_fields.get("URL", "")

    out: list[str] = []

    # Single outer breakable box — all content flows inside without inner boxes
    out.append(
        r"\noindent\begin{tcolorbox}[breakable,enhanced,"
        r"colback=white,colframe=gray!55,"
        r"boxrule=0.9pt,arc=4pt,left=6pt,right=6pt,top=4pt,bottom=4pt,"
        r"title={" + _SZ_TITLE + r"\bfseries " + convert_inline(title)
        + r"\hfill " + status_badge(status) + r"},"
        r"coltitle=black,colbacktitle=gray!12,titlerule=0.5pt]"
    )

    # Meta info row
    meta: list[str] = []
    if dataset_id:
        meta.append(r"\textbf{ID:}~\texttt{" + latex_escape(dataset_id) + r"}")
    if year:
        meta.append(r"\textbf{Year:}~" + latex_escape(year))
    if category:
        meta.append(r"\textbf{Category:}~" + latex_escape(category))
    if subjects:
        meta.append(r"\textbf{Subjects:}~" + latex_escape(subjects))
    if channels:
        meta.append(r"\textbf{Channels:}~" + latex_escape(channels))
    if sr:
        meta.append(r"\textbf{SR:}~" + latex_escape(sr))
    if files_ok:
        meta.append(r"\textbf{Files (completed):}~" + latex_escape(files_ok))
    if super_meta:
        meta.append(r"\textbf{Super Meta:}~" + latex_escape(super_meta))
    meta.append(r"\textbf{Reviewer:}~Anonymous")

    out.append(r"{" + _SZ_META + r" " + r" $\mid$ ".join(meta) + r"}")
    if url:
        out.append(r"\par{" + _SZ_META + r"\textbf{URL:}~\url{" + url + r"}}")
    out.append(r"\tcbline")

    # Paradigm
    if paradigm_text:
        out.append(r"\noindent{\bfseries" + _SZ_HEAD + r" Paradigm}\par\smallskip")
        out.append(r"{" + _SZ_BODY + r" " + convert_inline(clean(paradigm_text)) + r"}")

    # File Scan Result — after Paradigm, before Tasks
    if scan_text:
        out.extend(render_scan_result(scan_text))

    # Tasks — each rendered inline with rule separators, no inner tcolorbox
    if task_blocks:
        out.append(r"\noindent\rule{\linewidth}{0.7pt}\par\nopagebreak")
        out.append(r"\noindent{\bfseries" + _SZ_HEAD + r" Tasks}")
        for i, (kind, idx, ttitle, block) in enumerate(task_blocks):
            out.append(render_task(kind, idx, ttitle, block, add_rule=(i > 0)))
        out.append(r"\par\smallskip")

    # Data Quality Notes
    if quality_notes:
        out.append(r"\noindent\rule{\linewidth}{0.4pt}\par\nopagebreak")
        out.append(r"\noindent{\bfseries" + _SZ_HEAD + r" Data Quality Notes}\par\smallskip")
        out.append(r"\begin{itemize}[leftmargin=1.4em,noitemsep,topsep=2pt]")
        for note in quality_notes:
            out.append(r"\item{" + _SZ_BODY + r" " + convert_inline(note) + r"}")
        out.append(r"\end{itemize}")

    out.append(r"\end{tcolorbox}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_PREAMBLE_HINT = """\
% -----------------------------------------------------------------------
% Required packages (add to your preamble if not already present):
%   \\usepackage[skins,breakable]{tcolorbox}
%   \\usepackage{enumitem}
%   \\usepackage{booktabs}
%   \\usepackage{xcolor}
%   \\usepackage{url}
% -----------------------------------------------------------------------

"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export analysis.md documents to a LaTeX appendix block."
    )
    parser.add_argument(
        "--dataset",
        nargs="+",
        required=True,
        metavar="ID",
        help="Dataset directory names (e.g. bcic_iv_2a bcic_iv_2b).",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        metavar="DIR",
        help="Root directory containing dataset subdirectories.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="FILE",
        help="Output .tex file (default: %(default)s).",
    )
    args = parser.parse_args()

    blocks: list[str] = []
    for ds_id in args.dataset:
        path = args.dataset_root / ds_id / "analysis.md"
        if not path.exists():
            print(f"warning: not found — {path}")
            continue
        print(f"processing: {ds_id}")
        text = path.read_text(encoding="utf-8", errors="replace")
        blocks.append(render_document(text))

    if not blocks:
        print("no documents processed, nothing written.")
        return

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Wrap in a group with tight paragraph spacing to prevent gaps between boxes
    body = (
        r"{\setlength{\parskip}{2pt}\setlength{\parindent}{0pt}" + "\n"
        + "\n\\vspace{3pt}\n".join(blocks)
        + "\n}"
    )
    output_path.write_text(_PREAMBLE_HINT + body, encoding="utf-8")
    print(f"written: {output_path}  ({len(blocks)} document(s))")


if __name__ == "__main__":
    main()
