"""Temporary script: same as Script/Report/build_openneuro_summary_pdf.py,
but prefers analysis_minimax_v2.md over analysis.md per dataset folder.
Output: summary_minimax_temp.pdf in the repo root.
"""
import argparse
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, NavigableString, Tag
import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

try:
    from ftfy import fix_text
except Exception:
    fix_text = None


FONT_CANDIDATES = [
    Path(r"C:\\Windows\\Fonts\\msyh.ttc"),
    Path(r"C:\\Windows\\Fonts\\simhei.ttf"),
    Path(r"C:\\Windows\\Fonts\\msyh.ttf"),
    Path(r"C:\\Windows\\Fonts\\simsun.ttc"),
    Path(r"C:\\Windows\\Fonts\\segoeui.ttf"),
    Path(r"C:\\Windows\\Fonts\\arial.ttf"),
]

MONO_FONT_CANDIDATES = [
    Path(r"C:\\Windows\\Fonts\\consola.ttf"),
    Path(r"C:\\Windows\\Fonts\\cour.ttf"),
    Path(r"C:\\Windows\\Fonts\\msyh.ttc"),
]

SYMBOL_REPLACEMENTS = str.maketrans(
    {
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "≥": ">=",
        "≤": "<=",
        "×": "x",
        "–": "-",
        "—": "-",
        "−": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "…": "...",
        "\u00A0": " ",
    }
)

CATEGORY_ORDER = [
    "Complex Applied",
    "High-level Mental",
    "Action/Output",
    "Sensory/Response",
    "Biological State",
    "Others",
]

CATEGORY_DESCRIPTIONS = {
    "Complex Applied": "Real-world simulation, ecological environment, or multi-dimensional task.",
    "High-level Mental": "Deep internal cognitive/psychological processing tasks.",
    "Action/Output": "Motor intention/execution and BCI-output focused tasks.",
    "Sensory/Response": "Basic stimulus-response, ERP/SSVEP/RSVP, or simple attention tasks.",
    "Biological State": "Task-free or state-monitoring data (rest/sleep/clinical monitoring).",
    "Others": "Does not clearly fit the above categories.",
}

CATEGORY_ALIAS_MAP = {
    "Motor Imagery": "Action/Output",
    "Motor/Movement": "Action/Output",
    "P300 BCI": "Action/Output",
    "Auditory/Language": "High-level Mental",
    "Emotion Recognition": "High-level Mental",
    "Cognitive Task": "High-level Mental",
    "Sleep Staging": "Biological State",
    "Seizure Detection": "Biological State",
    "Artifact/Signal Quality": "Others",
    "Artifact Classification": "Others",
    "SSVEP": "Sensory/Response",
}


def choose_font(font_name: str, candidates: List[Path], fallback: str) -> str:
    for font_path in candidates:
        if not font_path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            return font_name
        except Exception:
            continue
    return fallback


class TechnicalReportDoc(BaseDocTemplate):
    def __init__(self, filename: str, report_title: str, header_font: str, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.report_title = report_title
        self.header_font = header_font
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main")
        template = PageTemplate(id="content", frames=[frame], onPage=self._draw_header_footer)
        self.addPageTemplates([template])

    def _draw_header_footer(self, canv, doc) -> None:
        page_num = canv.getPageNumber()
        if page_num == 1:
            return

        canv.saveState()
        page_w, page_h = doc.pagesize

        line_y = page_h - doc.topMargin + 5
        canv.setStrokeColor(colors.HexColor("#D5DCE5"))
        canv.setLineWidth(0.5)
        canv.line(doc.leftMargin, line_y, page_w - doc.rightMargin, line_y)

        canv.setFont(self.header_font, 8)
        canv.setFillColor(colors.HexColor("#5B6777"))
        canv.drawString(doc.leftMargin, page_h - doc.topMargin + 12, self.report_title)

        footer_y = doc.bottomMargin - 14
        canv.drawRightString(page_w - doc.rightMargin, footer_y, f"Page {page_num}")
        canv.restoreState()

    def afterFlowable(self, flowable) -> None:
        level = getattr(flowable, "_toc_level", None)
        bookmark = getattr(flowable, "_bookmark_name", None)
        if level is None or bookmark is None:
            return

        text = flowable.getPlainText()
        self.canv.bookmarkPage(bookmark)
        self.notify("TOCEntry", (level, text, self.page, bookmark))

        if level <= 1:
            self.canv.addOutlineEntry(text, bookmark, level=level, closed=False)


def clean_text_for_pdf(text: str) -> str:
    cleaned = []
    for ch in text:
        if ch in "\n\r\t":
            cleaned.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat in {"Cc", "Cs", "Co", "Cn"}:
            continue
        cleaned.append(ch)

    text = "".join(cleaned)
    text = text.translate(SYMBOL_REPLACEMENTS)
    return text


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    if fix_text is not None:
        text = fix_text(text)
    return clean_text_for_pdf(text)


def read_text_with_fallback(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return normalize_text(path.read_text(encoding=enc))
        except UnicodeDecodeError:
            continue
    return normalize_text(path.read_text(errors="replace"))


# ---------------------------------------------------------------------------
# KEY CHANGE: prefer analysis_minimax_v2.md; fall back to analysis.md
# ---------------------------------------------------------------------------
def discover_analysis_files(root: Path) -> List[Tuple[str, Path]]:
    pairs: List[Tuple[str, Path]] = []
    for ds_dir in sorted(root.iterdir(), key=lambda p: p.name):
        if not ds_dir.is_dir():
            continue
        if ds_dir.name.startswith("__") or ds_dir.name.startswith("."):
            continue
        minimax_path = ds_dir / "analysis_minimax_v2.md"
        fallback_path = ds_dir / "analysis.md"
        if minimax_path.exists():
            pairs.append((ds_dir.name, minimax_path))
        elif fallback_path.exists():
            pairs.append((ds_dir.name, fallback_path))
    return pairs


def extract_first_h1(md_text: str) -> Optional[str]:
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped:
            break
    return None


def strip_first_h1(md_text: str) -> str:
    return re.sub(r"^\s*#\s+.+?\n", "", md_text, count=1)


def extract_category(md_text: str) -> str:
    match = re.search(r"\*\*Category\*\*:\s*([^|\n]+)", md_text)
    if not match:
        return "Others"
    return clean_text_for_pdf(match.group(1).strip())


def infer_category_from_text(md_text: str) -> str:
    text = md_text.lower()

    complex_applied_kw = [
        "driving", "virtual reality", "mixed reality", "augmented reality",
        "gaming", "moba", "navigation", "naturalistic walking", "gait", "ecological",
    ]
    high_level_kw = [
        "emotion", "language", "speech", "working memory", "n-back",
        "decision", "math", "reinforcement learning", "semantic",
    ]
    action_output_kw = [
        "motor imagery", "bci", "sensorimotor", "movement-related", "motor intent",
    ]
    sensory_response_kw = [
        "oddball", "p300", "mmn", "ssvep", "rsvp", "flanker",
        "go-no-go", "gonogo", "stimulus onset",
    ]
    biological_state_kw = [
        "resting-state", "resting state", "eyes open", "eyes closed",
        "sleep", "psg", "clinical monitoring", "seizure", "epilepsy",
    ]

    if any(k in text for k in complex_applied_kw):
        return "Complex Applied"
    if any(k in text for k in high_level_kw):
        return "High-level Mental"
    if any(k in text for k in action_output_kw):
        return "Action/Output"
    if any(k in text for k in sensory_response_kw):
        return "Sensory/Response"
    if any(k in text for k in biological_state_kw):
        return "Biological State"
    return "Others"


def normalize_category(raw_category: str, md_text: str) -> str:
    category = clean_text_for_pdf((raw_category or "").strip())
    if category in CATEGORY_ORDER:
        return category
    if category in CATEGORY_ALIAS_MAP:
        return CATEGORY_ALIAS_MAP[category]
    return infer_category_from_text(md_text)


def escape_attr(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def render_inline(node) -> str:
    if isinstance(node, NavigableString):
        return escape(str(node))
    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()
    if name in {"strong", "b"}:
        return f"<b>{''.join(render_inline(c) for c in node.children)}</b>"
    if name in {"em", "i"}:
        return f"<i>{''.join(render_inline(c) for c in node.children)}</i>"
    if name == "code":
        txt = escape(node.get_text("", strip=False))
        return f"<font name='Courier'>{txt}</font>"
    if name == "a":
        href = node.get("href", "").strip()
        inner = "".join(render_inline(c) for c in node.children) or escape(href)
        if href:
            return f"<a href='{escape_attr(href)}'>{inner}</a>"
        return inner
    if name == "br":
        return "<br/>"
    if name == "img":
        alt = node.get("alt", "image")
        return f"[Image: {escape(alt)}]"
    return "".join(render_inline(c) for c in node.children)


def li_inline_text(li_tag: Tag) -> str:
    parts: List[str] = []
    for child in li_tag.children:
        if isinstance(child, Tag) and child.name.lower() in {"ul", "ol"}:
            continue
        parts.append(render_inline(child))
    text = "".join(parts).strip()
    if not text:
        text = escape(li_tag.get_text(" ", strip=True))
    return text


def build_list_paragraphs(
    tag: Tag,
    styles: StyleSheet1,
    level: int = 0,
    quote_mode: bool = False,
) -> List:
    ordered = tag.name.lower() == "ol"
    flowables: List = []

    base_style = styles["Quote"] if quote_mode else styles["ListBody"]
    indent = base_style.leftIndent + level * 12
    item_style = ParagraphStyle(
        name=f"ListLevel_{'Q' if quote_mode else 'N'}_{level}",
        parent=base_style,
        leftIndent=indent,
        firstLineIndent=0,
        spaceBefore=1,
        spaceAfter=1,
    )

    for index, li in enumerate(tag.find_all("li", recursive=False), 1):
        prefix = f"{index}. " if ordered else "- "
        content = li_inline_text(li)
        flowables.append(Paragraph(f"{prefix}{content}", item_style))
        for nested in li.find_all(["ul", "ol"], recursive=False):
            flowables.extend(build_list_paragraphs(nested, styles, level + 1, quote_mode=quote_mode))

    return flowables


def build_table(tag: Tag, styles: StyleSheet1, content_width: float) -> Optional[Table]:
    rows: List[List[Paragraph]] = []
    tr_tags = tag.find_all("tr")
    if not tr_tags:
        return None

    for tr in tr_tags:
        raw_cells = tr.find_all(["th", "td"], recursive=False)
        if not raw_cells:
            raw_cells = tr.find_all(["th", "td"])
        row: List[Paragraph] = []
        for cell in raw_cells:
            markup = "".join(render_inline(c) for c in cell.children).strip()
            if not markup:
                markup = " "
            style = styles["TableHeader"] if cell.name.lower() == "th" else styles["TableCell"]
            row.append(Paragraph(markup, style))
        if row:
            rows.append(row)

    if not rows:
        return None

    col_count = max(len(r) for r in rows)
    for r in rows:
        if len(r) < col_count:
            r.extend([Paragraph(" ", styles["TableCell"]) for _ in range(col_count - len(r))])

    col_width = content_width / max(col_count, 1)
    t = Table(rows, colWidths=[col_width] * col_count, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C4A64")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C8D0DA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FBFD")]),
            ]
        )
    )
    return t


def markdown_to_flowables(md_text: str, styles: StyleSheet1, content_width: float) -> List:
    html = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "nl2br"],
        output_format="html5",
    )
    soup = BeautifulSoup(html, "html.parser")
    flowables: List = []

    for node in soup.contents:
        if isinstance(node, NavigableString):
            text = str(node).strip()
            if text:
                flowables.append(Paragraph(escape(text), styles["Body"]))
            continue

        if not isinstance(node, Tag):
            continue

        name = node.name.lower()

        if name in {"h1", "h2"}:
            flowables.append(Paragraph("".join(render_inline(c) for c in node.children), styles["H2"]))
        elif name in {"h3", "h4", "h5", "h6"}:
            flowables.append(Paragraph("".join(render_inline(c) for c in node.children), styles["H3"]))
        elif name == "p":
            markup = "".join(render_inline(c) for c in node.children).strip()
            if markup:
                flowables.append(Paragraph(markup, styles["Body"]))
        elif name in {"ul", "ol"}:
            flowables.extend(build_list_paragraphs(node, styles))
        elif name == "pre":
            code = node.get_text("\n", strip=False).strip("\n")
            if code:
                flowables.append(Preformatted(code, styles["CodeBlock"]))
        elif name == "blockquote":
            for child in node.children:
                if isinstance(child, NavigableString):
                    txt = str(child).strip()
                    if txt:
                        flowables.append(Paragraph(escape(txt), styles["Quote"]))
                    continue
                if not isinstance(child, Tag):
                    continue
                child_name = child.name.lower()
                if child_name == "p":
                    markup = "".join(render_inline(c) for c in child.children).strip()
                    if markup:
                        flowables.append(Paragraph(markup, styles["Quote"]))
                elif child_name in {"ul", "ol"}:
                    flowables.extend(build_list_paragraphs(child, styles, quote_mode=True))
                elif child_name == "pre":
                    code = child.get_text("\n", strip=False).strip("\n")
                    if code:
                        flowables.append(Preformatted(code, styles["CodeBlock"]))
                else:
                    fallback = child.get_text(" ", strip=True)
                    if fallback:
                        flowables.append(Paragraph(escape(fallback), styles["Quote"]))
        elif name == "table":
            tbl = build_table(node, styles, content_width)
            if tbl is not None:
                flowables.append(tbl)
            flowables.append(Spacer(1, 4))
        elif name == "hr":
            flowables.append(Spacer(1, 8))
        else:
            fallback = node.get_text(" ", strip=True)
            if fallback:
                flowables.append(Paragraph(escape(fallback), styles["Body"]))

    return flowables


def heading(flowable: Paragraph, level: int, key: str) -> Paragraph:
    flowable._toc_level = level
    flowable._bookmark_name = key
    return flowable


def make_styles(body_font: str, mono_font: str) -> StyleSheet1:
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName=body_font,
                               fontSize=28, leading=34, textColor=colors.HexColor("#183B66"), spaceAfter=10))
    styles.add(ParagraphStyle(name="CoverSubtitle", parent=styles["Normal"], fontName=body_font,
                               fontSize=13, leading=18, textColor=colors.HexColor("#34495E"), spaceAfter=6))
    styles.add(ParagraphStyle(name="Meta", parent=styles["Normal"], fontName=body_font,
                               fontSize=10, leading=14, textColor=colors.HexColor("#5D6D7E"), spaceAfter=4))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading1"], fontName=body_font,
                               fontSize=18, leading=23, textColor=colors.HexColor("#1A3C5A"),
                               spaceBefore=8, spaceAfter=12))
    styles.add(ParagraphStyle(name="DatasetTitle", parent=styles["Heading1"], fontName=body_font,
                               fontSize=17, leading=22, textColor=colors.HexColor("#12395B"),
                               spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontName=body_font,
                               fontSize=13, leading=17, textColor=colors.HexColor("#1B5E7A"),
                               spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], fontName=body_font,
                               fontSize=11, leading=14, textColor=colors.HexColor("#2A6F8F"),
                               spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontName=body_font,
                               fontSize=9.6, leading=14, textColor=colors.HexColor("#111827"), spaceAfter=4))
    styles.add(ParagraphStyle(name="ListBody", parent=styles["Body"], leftIndent=0, spaceAfter=1))
    styles.add(ParagraphStyle(name="Quote", parent=styles["Body"], leftIndent=8 * mm, rightIndent=4 * mm,
                               textColor=colors.HexColor("#334155"), backColor=colors.HexColor("#F8FAFC"),
                               borderPadding=4, spaceBefore=2, spaceAfter=5))
    styles.add(ParagraphStyle(name="CodeBlock", parent=styles["Body"], fontName=body_font,
                               fontSize=8.3, leading=10.5, backColor=colors.HexColor("#F3F4F6"),
                               borderPadding=4, leftIndent=2 * mm, rightIndent=2 * mm,
                               spaceBefore=2, spaceAfter=6))
    styles.add(ParagraphStyle(name="TableCell", parent=styles["Body"], fontSize=8.7, leading=11, spaceAfter=0))
    styles.add(ParagraphStyle(name="TableHeader", parent=styles["TableCell"],
                               textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle(name="TOCHeading", parent=styles["Heading1"], fontName=body_font,
                               fontSize=18, leading=22, textColor=colors.HexColor("#183B66"), spaceAfter=10))
    return styles


def build_report(root: Path, output: Path) -> None:
    datasets = discover_analysis_files(root)
    if not datasets:
        raise RuntimeError("No analysis_minimax_v2.md or analysis.md files found.")

    body_font = choose_font("ReportBody", FONT_CANDIDATES, "Helvetica")
    mono_font = choose_font("ReportMono", MONO_FONT_CANDIDATES, "Courier")
    styles = make_styles(body_font, mono_font)

    report_title = "EEGDataset Benchmark Technical Report (Minimax v2)"
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    dataset_records: List[Dict[str, str]] = []
    category_counts: Counter = Counter()
    chapter_groups: Dict[str, List[Dict[str, str]]] = {k: [] for k in CATEGORY_ORDER}

    for dataset_id, md_path in datasets:
        md_text = read_text_with_fallback(md_path)
        first_h1 = extract_first_h1(md_text)
        body_md = strip_first_h1(md_text) if first_h1 else md_text
        raw_category = extract_category(md_text)
        std_category = normalize_category(raw_category, md_text)

        rec = {
            "dataset_id": dataset_id,
            "md_text": md_text,
            "body_md": body_md,
            "first_h1": first_h1 or "",
            "category": std_category,
            "source_file": md_path.name,
        }
        dataset_records.append(rec)
        chapter_groups[std_category].append(rec)
        category_counts[std_category] += 1

    for category in CATEGORY_ORDER:
        chapter_groups[category].sort(key=lambda x: x["dataset_id"])

    doc = TechnicalReportDoc(
        str(output),
        report_title=report_title,
        header_font=body_font,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=report_title,
        author="BIDS_description",
        subject="EEGDataset Benchmark technical report (minimax v2)",
    )

    story: List = []

    # Cover
    story.append(Spacer(1, 50))
    story.append(Paragraph(report_title, styles["CoverTitle"]))
    story.append(Paragraph("Unified EEG Dataset Documentation", styles["CoverSubtitle"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Datasets included: <b>{len(dataset_records)}</b>", styles["Meta"]))
    story.append(Paragraph(f"Generated at: <b>{generated}</b>", styles["Meta"]))
    story.append(PageBreak())

    # Preface
    preface = heading(Paragraph("Preface", styles["SectionTitle"]), 0, "preface")
    story.append(preface)
    story.append(
        Paragraph(
            f"This report summarizes <b>{len(dataset_records)}</b> EEG datasets. "
            "Each dataset uses <b>analysis_minimax_v2.md</b> when available, "
            "otherwise falls back to <b>analysis.md</b>.",
            styles["Body"],
        )
    )
    for category in CATEGORY_ORDER:
        count = category_counts.get(category, 0)
        desc = CATEGORY_DESCRIPTIONS.get(category, "")
        story.append(
            Paragraph(
                f"- <b>{escape(category)}</b> ({count}): {escape(desc)}",
                styles["ListBody"],
            )
        )
    story.append(PageBreak())

    # TOC
    toc_title = heading(Paragraph("Table of Contents", styles["TOCHeading"]), 0, "toc")
    story.append(toc_title)
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOCLevel0", fontName=styles["Body"].fontName,
                       fontSize=9.8, leading=13, firstLineIndent=-15, leftIndent=20,
                       rightIndent=20, spaceBefore=2, textColor=colors.HexColor("#1F2937")),
        ParagraphStyle(name="TOCLevel1", fontName=styles["Body"].fontName,
                       fontSize=8.7, leading=11, firstLineIndent=-12, leftIndent=34,
                       rightIndent=20, spaceBefore=1, textColor=colors.HexColor("#4B5563")),
    ]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(PageBreak())

    # Chapters
    dataset_index = 1
    for cat_idx, category in enumerate(CATEGORY_ORDER, 1):
        if cat_idx > 1:
            story.append(PageBreak())

        category_key = category.lower().replace("/", "_").replace(" ", "_")
        category_heading = heading(
            Paragraph(f"Chapter {cat_idx}. {category}", styles["SectionTitle"]),
            0,
            f"category_{category_key}",
        )
        story.append(category_heading)
        story.append(
            Paragraph(
                f"Datasets in this chapter: <b>{category_counts.get(category, 0)}</b>. "
                f"{escape(CATEGORY_DESCRIPTIONS.get(category, ''))}",
                styles["Meta"],
            )
        )

        recs = chapter_groups.get(category, [])
        if not recs:
            story.append(Paragraph("No datasets assigned to this category.", styles["Body"]))
            continue

        for local_idx, rec in enumerate(recs):
            if local_idx > 0:
                story.append(PageBreak())

            dataset_id = rec["dataset_id"]
            body_md = rec["body_md"]
            first_h1 = rec["first_h1"]
            source_file = rec["source_file"]

            section_title = f"{dataset_index:03d}. {dataset_id}"
            if first_h1:
                section_title += f" - {escape(first_h1)}"

            dataset_heading = heading(
                Paragraph(section_title, styles["DatasetTitle"]),
                1,
                f"dataset_{dataset_id}",
            )
            story.append(dataset_heading)
            story.append(Paragraph(f"Source: <i>{escape(source_file)}</i>", styles["Meta"]))
            story.append(Spacer(1, 3))

            flowables = markdown_to_flowables(body_md, styles, doc.width)
            story.extend(flowables if flowables else [Paragraph("(No content)", styles["Body"])])

            dataset_index += 1

    doc.multiBuild(story)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Temporary: build summary PDF preferring analysis_minimax_v2.md over analysis.md."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("summary_minimax_temp.pdf"))
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else (root / args.output)

    build_report(root, output)
    print(f"PDF generated: {output}")


if __name__ == "__main__":
    main()
