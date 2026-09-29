#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


DEFAULT_DATASET_DIR = Path(r"E:\github_projects\BIDS_description\dataset_document")
DEFAULT_OUTPUT_DIR = Path("pull_data_script") / "docment_figures"

_EXPORT_EPS: bool = False

TASK_HEADING_RE = re.compile(
    r"^###\s+(?P<kind>Classical|Potential|Normal)\s+Task\s+(?P<idx>\d+)\s*:\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)
INLINE_FIELD_RE = re.compile(r"\*\*(?P<key>[^*]+?)\*\*:\s*(?P<value>[^|\n]+)")

CATEGORY_ORDER = [
    "High-level Mental",
    "Complex Applied",
    "Sensory/Response",
    "Biological State",
    "Action/Output",
    "Others",
]
STATUS_ORDER = [
    "completed",
    "wait_manual_review",
    "wait_kernel_update",
    "hallucinate",
    "failed",
    "missing",
]
TASK_KIND_ORDER = ["classical", "potential", "normal", "unknown"]
TASK_TYPE_ORDER = [
    "classification",
    "regression",
    "segmentation",
    "detection",
    "clustering",
    "rsa",
    "feature_extraction",
    "reliability_analysis",
    "exploratory",
    "other",
    "missing",
]
TASK_TYPE_MAJOR_ORDER = ["classification", "regression", "other", "missing"]
EPOCH_METHOD_ORDER = [
    "event_locked",
    "continuous_segmentation",
    "long_event_locked",
    "multiple",
    "other",
    "missing",
]
LABEL_ROUTE_ORDER = ["event", "info", "misc", "event+misc", "other", "missing"]
META_LEVEL_ORDER = ["raw", "super", "mixed", "missing"]
PAPER_TASK_KIND_ORDER = ["classical", "potential", "normal"]
PAPER_TASK_KIND_FILTERED_ORDER = ["classical", "potential"]
PAPER_SUPER_META_ORDER = ["no", "yes"]
PAPER_LABEL_ROUTE_ORDER = ["event", "info", "misc"]
PAPER_META_LEVEL_ORDER = ["raw", "super"]
PAPER_EPOCH_METHOD_ORDER = ["event_locked", "long_event_locked", "continuous_segmentation"]
PAPER_HEATMAP_TASK_TYPES = ["classification", "regression"]

PAPER_COLOR = {
    "navy": "#264653",
    "green": "#2A9D8F",
    "gold": "#E9C46A",
    "orange": "#F4A261",
    "red": "#E76F51",
    "gray": "#7A7A7A",
    "light": "#F1F5F4",
}
STACK_COLORS = {
    "classical": PAPER_COLOR["navy"],
    "potential": PAPER_COLOR["orange"],
    "normal": PAPER_COLOR["green"],
    "unknown": PAPER_COLOR["gray"],
    "High-level Mental": PAPER_COLOR["navy"],
    "Complex Applied": PAPER_COLOR["orange"],
    "Sensory/Response": PAPER_COLOR["green"],
    "Biological State": PAPER_COLOR["gold"],
    "Action/Output": PAPER_COLOR["red"],
    "Others": PAPER_COLOR["gray"],
    "completed": PAPER_COLOR["green"],
    "wait_manual_review": PAPER_COLOR["orange"],
    "wait_kernel_update": PAPER_COLOR["gold"],
    "hallucinate": PAPER_COLOR["red"],
    "failed": "#B22222",
    "missing": PAPER_COLOR["gray"],
}
PAPER_DISPLAY_LABELS = {
    "classical": "Classical",
    "potential": "Potential",
    "normal": "Normal",
    "no": "No",
    "yes": "Yes",
    "event": "Event",
    "info": "Info",
    "misc": "Misc",
    "raw": "Raw",
    "super": "Super",
    "event_locked": "Event-locked\nwindow",
    "long_event_locked": "Long-event-\nlocked window",
    "continuous_segmentation": "Continuous\nwindow",
    "classification": "Classification",
    "regression": "Regression",
}


@dataclass
class DocumentRecord:
    dataset_name: str
    raw_category: str
    category_group: str
    status: str
    super_meta_required: str
    year_raw: str
    year_start: int | None
    year_end: int | None
    subjects_raw: str
    subjects_count: int | None
    files_completed_raw: str
    files_completed_count: int | None
    channels_raw: str
    sampling_rate_raw: str
    manual_review: str
    task_count: int
    classical_task_count: int
    potential_task_count: int
    normal_task_count: int
    analysis_path: str


@dataclass
class TaskRecord:
    dataset_name: str
    category_group: str
    document_status: str
    super_meta_required: str
    task_index: int
    task_title: str
    task_kind: str
    task_type: str
    epoch_method: str
    label_route: str
    meta_level: str
    raw_task_type: str
    raw_epoch_method: str
    raw_label_route: str
    raw_meta_level: str
    analysis_path: str


def clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def slugify(value: str) -> str:
    text = clean_text(value).lower()
    text = text.replace("/", "_").replace("+", "_plus_")
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_") or "missing"


def parse_inline_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in INLINE_FIELD_RE.finditer(text):
        key = clean_text(match.group("key"))
        value = clean_text(match.group("value"))
        if key and key not in fields:
            fields[key] = value
    return fields


def extract_blockquote_field(text: str, field_name: str) -> str:
    pattern = r"^>\s+\*\*" + re.escape(field_name) + r"\*\*:\s*(.+?)\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    return clean_text(match.group(1)) if match else ""


def extract_field(block: str, field_name: str) -> str:
    pattern = r"^\-\s+\*\*" + re.escape(field_name) + r"\*\*:\s*(.+?)\s*$"
    match = re.search(pattern, block, flags=re.MULTILINE)
    return clean_text(match.group(1)) if match else ""


def normalize_status(value: str) -> str:
    text = slugify(value)
    mapping = {
        "completed": "completed",
        "wait_manual_review": "wait_manual_review",
        "wait_kernel_update": "wait_kernel_update",
        "hallucination": "hallucinate",
        "hallucinate": "hallucinate",
        "failed": "failed",
    }
    return mapping.get(text, text or "missing")


def normalize_category_group(value: str) -> str:
    text = clean_text(value).lower()
    if "high-level mental" in text or "high level mental" in text:
        return "High-level Mental"
    if "complex applied" in text:
        return "Complex Applied"
    if "sensory" in text or "response" in text:
        return "Sensory/Response"
    if "biological state" in text:
        return "Biological State"
    if "action" in text or "output" in text:
        return "Action/Output"
    if not text or text == "missing":
        return "Others"
    return "Others"


def normalize_yes_no(value: str) -> str:
    text = clean_text(value).strip("`").lower()
    if text in {"yes", "no"}:
        return text
    return "missing"


def normalize_task_kind(value: str) -> str:
    text = clean_text(value).lower()
    if text in {"classical", "potential", "normal"}:
        return text
    return "unknown"


def normalize_task_type(value: str) -> str:
    text = clean_text(value).strip("`").lower()
    if not text:
        return "missing"
    if "classification" in text:
        return "classification"
    if "regression" in text:
        return "regression"
    if "segmentation" in text:
        return "segmentation"
    if "detection" in text:
        return "detection"
    if "clustering" in text:
        return "clustering"
    if "encoding/rsa" in text or text == "encoding_rsa":
        return "rsa"
    if text == "rsa":
        return "rsa"
    if "feature" in text:
        return "feature_extraction"
    if "reliability" in text:
        return "reliability_analysis"
    if "exploratory" in text:
        return "exploratory"
    return "other"


def collapse_task_type_major(value: str) -> str:
    if value in {"classification", "regression", "missing"}:
        return value
    return "other"


def normalize_label_route(value: str) -> str:
    text = clean_text(value).strip("`").lower()
    if not text:
        return "missing"

    has_event = "event" in text or "annotation" in text or "stim" in text
    has_info = "info" in text
    has_misc = "misc" in text

    if has_event and has_misc:
        return "event+misc"
    if has_event:
        return "event"
    if has_info:
        return "info"
    if has_misc:
        return "misc"
    return "other"


def normalize_epoch_method(value: str) -> str:
    text = clean_text(value).strip("`").lower()
    if not text:
        return "missing"

    has_event = "epoch_by_event_hdf5" in text or "event-locked" in text or "epoch_by_event" in text
    has_long_event = "epoch_by_long_event_hdf5" in text or "long-event" in text or "long_event" in text
    has_segmentation = "segmentation" in text or "continuous" in text
    method_count = sum((has_event, has_long_event, has_segmentation))

    if method_count >= 2:
        return "multiple"
    if has_event:
        return "event_locked"
    if has_long_event:
        return "long_event_locked"
    if has_segmentation:
        return "continuous_segmentation"
    return "other"


def normalize_meta_level(value: str) -> str:
    text = clean_text(value).strip("`").lower()
    if not text:
        return "missing"
    if "raw" in text and "super" in text:
        return "mixed"
    if text == "raw":
        return "raw"
    if text == "super":
        return "super"
    return "missing"


def parse_first_int(value: str) -> int | None:
    match = re.search(r"\d+", clean_text(value))
    return int(match.group(0)) if match else None


def parse_year_range(value: str) -> tuple[int | None, int | None]:
    years = [int(item) for item in re.findall(r"(?:19|20)\d{2}", clean_text(value))]
    if not years:
        return None, None
    return min(years), max(years)


def split_task_blocks(text: str) -> list[tuple[str, int, str, str]]:
    matches = list(TASK_HEADING_RE.finditer(text))
    blocks: list[tuple[str, int, str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(
            (
                match.group("kind"),
                int(match.group("idx")),
                clean_text(match.group("title")),
                text[start:end].strip(),
            )
        )
    return blocks


def iter_analysis_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.glob("*/analysis.md")):
        yield path


def parse_document(path: Path) -> tuple[DocumentRecord, list[TaskRecord]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    inline_fields = parse_inline_fields(text)

    raw_category = inline_fields.get("Category", "missing")
    category_group = normalize_category_group(raw_category)
    status = normalize_status(extract_blockquote_field(text, "Status"))
    super_meta_required = normalize_yes_no(extract_blockquote_field(text, "Super Meta Required"))
    year_raw = inline_fields.get("Year", "")
    year_start, year_end = parse_year_range(year_raw)

    task_records: list[TaskRecord] = []
    for _, task_index, task_title, block in split_task_blocks(text):
        raw_task_type = extract_field(block, "Task Type")
        raw_epoch_method = extract_field(block, "Epoch Method")
        raw_label_route = extract_field(block, "Label Route") or extract_field(block, "Route")
        raw_meta_level = extract_field(block, "Meta Level")

        task_records.append(
            TaskRecord(
                dataset_name=path.parent.name,
                category_group=category_group,
                document_status=status,
                super_meta_required=super_meta_required,
                task_index=task_index,
                task_title=task_title,
                task_kind=normalize_task_kind(extract_task_kind_from_title_block(block)),
                task_type=normalize_task_type(raw_task_type),
                epoch_method=normalize_epoch_method(raw_epoch_method),
                label_route=normalize_label_route(raw_label_route),
                meta_level=normalize_meta_level(raw_meta_level),
                raw_task_type=clean_text(raw_task_type),
                raw_epoch_method=clean_text(raw_epoch_method),
                raw_label_route=clean_text(raw_label_route),
                raw_meta_level=clean_text(raw_meta_level),
                analysis_path=str(path),
            )
        )

    kind_counter = Counter(task.task_kind for task in task_records)
    document_record = DocumentRecord(
        dataset_name=path.parent.name,
        raw_category=clean_text(raw_category) or "missing",
        category_group=category_group,
        status=status,
        super_meta_required=super_meta_required,
        year_raw=clean_text(year_raw),
        year_start=year_start,
        year_end=year_end,
        subjects_raw=clean_text(inline_fields.get("Subjects", "")),
        subjects_count=parse_first_int(inline_fields.get("Subjects", "")),
        files_completed_raw=clean_text(inline_fields.get("Files (Completed)", "")),
        files_completed_count=parse_first_int(inline_fields.get("Files (Completed)", "")),
        channels_raw=clean_text(inline_fields.get("Channels", "")),
        sampling_rate_raw=clean_text(inline_fields.get("Sampling Rate", "")),
        manual_review=clean_text(inline_fields.get("Manual Review", "")),
        task_count=len(task_records),
        classical_task_count=kind_counter.get("classical", 0),
        potential_task_count=kind_counter.get("potential", 0),
        normal_task_count=kind_counter.get("normal", 0),
        analysis_path=str(path),
    )
    return document_record, task_records


def extract_task_kind_from_title_block(block: str) -> str:
    heading_match = TASK_HEADING_RE.search(block)
    return heading_match.group("kind") if heading_match else ""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: Sequence[dict[str, object]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_counter_csv(path: Path, label_name: str, counter: Counter[str], preferred_order: Sequence[str] | None = None) -> None:
    order_map = {key: index for index, key in enumerate(preferred_order or [])}
    items = sorted(counter.items(), key=lambda item: (order_map.get(item[0], len(order_map)), -item[1], item[0]))
    rows = [{label_name: key, "count": value} for key, value in items]
    write_csv(path, rows, [label_name, "count"])


def write_matrix_csv(path: Path, row_name: str, col_name: str, matrix: dict[str, Counter[str]], row_order: Sequence[str], col_order: Sequence[str]) -> None:
    rows: list[dict[str, object]] = []
    for row_key in row_order:
        row = {row_name: row_key}
        row_counter = matrix.get(row_key, Counter())
        total = 0
        for col_key in col_order:
            value = row_counter.get(col_key, 0)
            row[col_key] = value
            total += value
        row["total"] = total
        rows.append(row)
    write_csv(path, rows, [row_name] + list(col_order) + ["total"])


def build_counter(values: Iterable[str], preferred_order: Sequence[str] | None = None) -> Counter[str]:
    counter = Counter(values)
    if preferred_order:
        for key in preferred_order:
            counter.setdefault(key, 0)
    return counter


def build_nested_counter(rows: Iterable[tuple[str, str]]) -> dict[str, Counter[str]]:
    nested: dict[str, Counter[str]] = defaultdict(Counter)
    for left, right in rows:
        nested[left][right] += 1
    return nested


def configure_matplotlib(font_size: int) -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "Arial",
            "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
            "font.size": font_size,
            "axes.titlesize": font_size + 1,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "axes.edgecolor": "#444444",
            "axes.linewidth": 0.8,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "grid.color": "#D6D6D6",
            "grid.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, output_base: Path) -> None:
    fig.tight_layout()
    save_figure_file(fig, output_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    save_figure_file(fig, output_base.with_suffix(".pdf"), bbox_inches="tight")
    if _EXPORT_EPS:
        save_figure_file(fig, output_base.with_suffix(".eps"), bbox_inches="tight")
    plt.close(fig)


def save_figure_file(fig: plt.Figure, path: Path, **kwargs: object) -> Path:
    try:
        fig.savefig(str(path), **kwargs)
        return path
    except PermissionError:
        fallback_path = path.with_name(path.stem + "_updated" + path.suffix)
        fig.savefig(str(fallback_path), **kwargs)
        print("warning: file busy, wrote fallback: {0}".format(fallback_path))
        return fallback_path


def ordered_items(counter: Counter[str], preferred_order: Sequence[str] | None = None, drop_zero: bool = True) -> list[tuple[str, int]]:
    order_map = {key: index for index, key in enumerate(preferred_order or [])}
    items = [(key, value) for key, value in counter.items() if (not drop_zero or value > 0)]
    return sorted(items, key=lambda item: (order_map.get(item[0], len(order_map)), -item[1], item[0]))


def prettify_token(value: str) -> str:
    mapping = {
        "completed": "Completed",
        "wait_manual_review": "Wait manual review",
        "wait_kernel_update": "Wait kernel update",
        "hallucinate": "Hallucinate",
        "failed": "Failed",
        "missing": "Missing",
        "yes": "Yes",
        "no": "No",
        "classical": "Classical",
        "potential": "Potential",
        "normal": "Normal",
        "unknown": "Unknown",
        "classification": "Classification",
        "regression": "Regression",
        "segmentation": "Segmentation",
        "detection": "Detection",
        "clustering": "Clustering",
        "rsa": "RSA",
        "feature_extraction": "Feature extraction",
        "reliability_analysis": "Reliability analysis",
        "exploratory": "Exploratory",
        "event_locked": "Event-locked",
        "long_event_locked": "Long-event locked",
        "continuous_segmentation": "Continuous segmentation",
        "multiple": "Multiple methods",
        "event": "Event",
        "info": "Info",
        "misc": "Misc",
        "event+misc": "Event + misc",
        "raw": "Raw",
        "super": "Super",
        "mixed": "Mixed",
        "other": "Other",
    }
    return mapping.get(value, value)


def filter_counter(counter: Counter[str], keep_keys: Sequence[str]) -> Counter[str]:
    return Counter({key: counter.get(key, 0) for key in keep_keys})


def style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def label_for(value: str, label_map: dict[str, str] | None = None) -> str:
    if label_map and value in label_map:
        return label_map[value]
    return prettify_token(value)


def draw_barh_panel(
    ax: plt.Axes,
    counter: Counter[str],
    title: str,
    xlabel: str,
    preferred_order: Sequence[str],
    color: str,
    label_map: dict[str, str] | None = None,
) -> None:
    items = ordered_items(counter, preferred_order=preferred_order)
    labels = [label_for(key, label_map) for key, _ in items]
    values = [value for _, value in items]

    ax.barh(range(len(items)), values, color=color, edgecolor="white")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    style_axes(ax)

    offset = max(values) * 0.018 if values else 0.1
    for index, value in enumerate(values):
        ax.text(value + offset, index, str(value), va="center", ha="left", fontsize=8)


def draw_bar_panel(
    ax: plt.Axes,
    counter: Counter[str],
    title: str,
    ylabel: str,
    preferred_order: Sequence[str],
    color: str,
    label_map: dict[str, str] | None = None,
) -> None:
    items = ordered_items(counter, preferred_order=preferred_order)
    labels = [label_for(key, label_map) for key, _ in items]
    values = [value for _, value in items]
    positions = list(range(len(items)))

    ax.bar(positions, values, color=color, edgecolor="white", width=0.72)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    style_axes(ax)

    offset = max(values) * 0.03 if values else 0.1
    for index, value in enumerate(values):
        ax.text(index, value + offset, str(value), va="bottom", ha="center", fontsize=8)


def draw_histogram_panel(
    ax: plt.Axes,
    values: Sequence[int],
    title: str,
    xlabel: str,
    ylabel: str,
    color: str,
) -> None:
    max_value = max(values) if values else 0
    bins = list(range(0, max_value + 2))

    ax.hist(values, bins=bins, color=color, edgecolor="white", align="left", rwidth=0.9)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(list(range(0, max_value + 1)))
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    style_axes(ax)

    if values:
        mean_value = sum(values) / float(len(values))
        median_value = statistics.median(values)
        ax.axvline(mean_value, color=PAPER_COLOR["red"], linestyle="--", linewidth=1.1, label="Mean")
        ax.axvline(median_value, color=PAPER_COLOR["navy"], linestyle="-.", linewidth=1.1, label="Median")
        ax.legend(frameon=False, fontsize=8, loc="upper right")


def draw_stacked_barh_panel(
    ax: plt.Axes,
    matrix: dict[str, Counter[str]],
    row_order: Sequence[str],
    col_order: Sequence[str],
    title: str,
    xlabel: str,
    label_map: dict[str, str] | None = None,
) -> None:
    active_rows = [
        row
        for row in row_order
        if sum(matrix.get(row, Counter()).get(column, 0) for column in col_order) > 0
    ]
    left = [0.0] * len(active_rows)

    for column in col_order:
        values = [matrix.get(row, Counter()).get(column, 0) for row in active_rows]
        if not any(values):
            continue
        ax.barh(
            range(len(active_rows)),
            values,
            left=left,
            color=STACK_COLORS.get(column, PAPER_COLOR["gray"]),
            edgecolor="white",
            label=label_for(column, label_map),
        )
        left = [current + value for current, value in zip(left, values)]

    ax.set_yticks(range(len(active_rows)))
    ax.set_yticklabels([label_for(row, label_map) for row in active_rows])
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    style_axes(ax)

    totals = [
        sum(matrix.get(row, Counter()).get(column, 0) for column in col_order)
        for row in active_rows
    ]
    offset = max(totals) * 0.015 if totals else 0.1
    for index, total in enumerate(totals):
        ax.text(total + offset, index, str(total), va="center", ha="left", fontsize=8)


def draw_heatmap_panel(
    ax: plt.Axes,
    matrix: dict[str, Counter[str]],
    row_order: Sequence[str],
    col_order: Sequence[str],
    title: str,
    label_map: dict[str, str] | None = None,
) -> None:
    data = [[matrix.get(row, Counter()).get(col, 0) for col in col_order] for row in row_order]
    vmax = max(max(row) for row in data) if data else 1

    cmap = LinearSegmentedColormap.from_list(
        "paper_heat",
        [PAPER_COLOR["light"], PAPER_COLOR["gold"], PAPER_COLOR["orange"], PAPER_COLOR["red"]],
    )
    image = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=vmax)
    ax.set_xticks(range(len(col_order)))
    ax.set_xticklabels([label_for(col, label_map) for col in col_order])
    ax.set_yticks(range(len(row_order)))
    ax.set_yticklabels([label_for(row, label_map) for row in row_order])
    ax.set_title(title, loc="left", fontweight="bold")
    style_axes(ax)

    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            if value <= 0:
                continue
            text_color = "white" if value > vmax * 0.45 else "#222222"
            ax.text(col_index, row_index, str(value), ha="center", va="center", color=text_color, fontsize=9)

    return image


def draw_meta_type_dual_axis_panel(
    ax: plt.Axes,
    document_super_meta_counter: Counter[str],
    task_meta_level_counter: Counter[str],
    title: str,
) -> None:
    categories = ["raw", "super"]
    document_values = [
        document_super_meta_counter.get("no", 0),
        document_super_meta_counter.get("yes", 0),
    ]
    task_values = [
        task_meta_level_counter.get("raw", 0),
        task_meta_level_counter.get("super", 0),
    ]
    positions = [0, 1]
    width = 0.32

    bars_left = ax.bar(
        [position - width / 2.0 for position in positions],
        document_values,
        width=width,
        color=PAPER_COLOR["green"],
        edgecolor="white",
        label="Documents",
    )
    ax.set_xticks(positions)
    ax.set_xticklabels([PAPER_DISPLAY_LABELS[item] for item in categories])
    ax.set_ylabel("Documents")
    ax.yaxis.label.set_color(PAPER_COLOR["green"])
    ax.tick_params(axis="y", colors=PAPER_COLOR["green"])
    ax.set_title(title, loc="left", fontweight="bold", pad=8)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    style_axes(ax)

    ax_right = ax.twinx()
    bars_right = ax_right.bar(
        [position + width / 2.0 for position in positions],
        task_values,
        width=width,
        color=PAPER_COLOR["navy"],
        edgecolor="white",
        alpha=0.9,
        label="Tasks",
    )
    ax_right.set_ylabel("Tasks")
    ax_right.yaxis.label.set_color(PAPER_COLOR["navy"])
    ax_right.tick_params(axis="y", colors=PAPER_COLOR["navy"])
    ax_right.spines["top"].set_visible(False)

    left_offset = max(document_values) * 0.03 if document_values else 0.1
    for bar, value in zip(bars_left, document_values):
        ax.text(bar.get_x() + bar.get_width() / 2.0, value + left_offset, str(value), ha="center", va="bottom", fontsize=8)

    right_offset = max(task_values) * 0.03 if task_values else 0.1
    for bar, value in zip(bars_right, task_values):
        ax_right.text(
            bar.get_x() + bar.get_width() / 2.0,
            value + right_offset,
            str(value),
            ha="center",
            va="bottom",
            fontsize=8,
        )



def plot_barh_counts(
    counter: Counter[str],
    output_base: Path,
    title: str,
    xlabel: str,
    preferred_order: Sequence[str] | None = None,
    color: str = PAPER_COLOR["navy"],
) -> None:
    items = ordered_items(counter, preferred_order=preferred_order)
    fig_height = max(3.0, 0.45 * len(items) + 1.3)
    fig, ax = plt.subplots(figsize=(7.0, fig_height))
    draw_barh_panel(ax, counter, title, xlabel, preferred_order or [], color)
    save_figure(fig, output_base)


def plot_histogram(
    values: Sequence[int],
    output_base: Path,
    title: str,
    xlabel: str,
    ylabel: str,
    color: str = PAPER_COLOR["green"],
) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    draw_histogram_panel(ax, values, title, xlabel, ylabel, color)
    save_figure(fig, output_base)


def plot_stacked_barh(
    matrix: dict[str, Counter[str]],
    row_order: Sequence[str],
    col_order: Sequence[str],
    output_base: Path,
    title: str,
    xlabel: str,
) -> None:
    active_rows = [row for row in row_order if sum(matrix.get(row, Counter()).values()) > 0]
    if not active_rows:
        return

    fig_height = max(3.5, 0.6 * len(active_rows) + 1.2)
    fig, ax = plt.subplots(figsize=(7.4, fig_height))
    draw_stacked_barh_panel(ax, matrix, row_order, col_order, title, xlabel)
    ax.legend(frameon=False, ncol=min(4, len(col_order)), loc="upper center", bbox_to_anchor=(0.5, -0.12))
    save_figure(fig, output_base)


def plot_heatmap(
    matrix: dict[str, Counter[str]],
    row_order: Sequence[str],
    col_order: Sequence[str],
    output_base: Path,
    title: str,
    value_label: str,
) -> None:
    active_rows = [row for row in row_order if sum(matrix.get(row, Counter()).values()) > 0]
    active_cols = [col for col in col_order if any(matrix.get(row, Counter()).get(col, 0) > 0 for row in row_order)]
    if not active_rows or not active_cols:
        return

    data = [[matrix.get(row, Counter()).get(col, 0) for col in active_cols] for row in active_rows]
    vmax = max(max(row) for row in data) if data else 1

    fig_width = max(6.5, 1.0 * len(active_cols) + 2.5)
    fig_height = max(3.2, 0.6 * len(active_rows) + 1.6)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    image = draw_heatmap_panel(ax, matrix, active_rows, active_cols, title)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.04)
    colorbar.set_label(value_label)
    save_figure(fig, output_base)


def write_summary_markdown(path: Path, documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord]) -> None:
    document_status = build_counter((doc.status for doc in documents), STATUS_ORDER)
    document_category = build_counter((doc.category_group for doc in documents), CATEGORY_ORDER)
    task_kind = build_counter((task.task_kind for task in tasks), TASK_KIND_ORDER)
    task_type = build_counter((task.task_type for task in tasks), TASK_TYPE_ORDER)
    epoch_method = build_counter((task.epoch_method for task in tasks), EPOCH_METHOD_ORDER)

    task_counts = [doc.task_count for doc in documents]
    mean_task_count = sum(task_counts) / float(len(task_counts)) if task_counts else 0.0
    median_task_count = statistics.median(task_counts) if task_counts else 0

    lines = [
        "# Document Resource Summary",
        "",
        "## Key counts",
        "",
        "- Documents: {0}".format(len(documents)),
        "- Tasks: {0}".format(len(tasks)),
        "- Mean tasks per dataset: {0:.3f}".format(mean_task_count),
        "- Median tasks per dataset: {0}".format(median_task_count),
        "- Max tasks in a single dataset: {0}".format(max(task_counts) if task_counts else 0),
        "",
        "## Document status",
        "",
    ]
    lines.extend("- {0}: {1}".format(prettify_token(key), value) for key, value in ordered_items(document_status, STATUS_ORDER))
    lines.extend(
        [
            "",
            "## Category coverage",
            "",
        ]
    )
    lines.extend("- {0}: {1}".format(prettify_token(key), value) for key, value in ordered_items(document_category, CATEGORY_ORDER))
    lines.extend(
        [
            "",
            "## Task kinds",
            "",
        ]
    )
    lines.extend("- {0}: {1}".format(prettify_token(key), value) for key, value in ordered_items(task_kind, TASK_KIND_ORDER))
    lines.extend(
        [
            "",
            "## Task types",
            "",
        ]
    )
    lines.extend("- {0}: {1}".format(prettify_token(key), value) for key, value in ordered_items(task_type, TASK_TYPE_ORDER))
    lines.extend(
        [
            "",
            "## Epoch methods",
            "",
        ]
    )
    lines.extend("- {0}: {1}".format(prettify_token(key), value) for key, value in ordered_items(epoch_method, EPOCH_METHOD_ORDER))

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_tables(documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord], table_dir: Path) -> None:
    ensure_dir(table_dir)

    document_rows = [asdict(document) for document in documents]
    task_rows = [asdict(task) for task in tasks]
    if document_rows:
        write_csv(table_dir / "documents.csv", document_rows, list(document_rows[0].keys()))
    if task_rows:
        write_csv(table_dir / "tasks.csv", task_rows, list(task_rows[0].keys()))

    write_counter_csv(
        table_dir / "summary_documents_by_status.csv",
        "status",
        build_counter((document.status for document in documents), STATUS_ORDER),
        STATUS_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_documents_by_category.csv",
        "category_group",
        build_counter((document.category_group for document in documents), CATEGORY_ORDER),
        CATEGORY_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_documents_by_super_meta_required.csv",
        "super_meta_required",
        build_counter((document.super_meta_required for document in documents), ["no", "yes", "missing"]),
        ["no", "yes", "missing"],
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_kind.csv",
        "task_kind",
        build_counter((task.task_kind for task in tasks), TASK_KIND_ORDER),
        TASK_KIND_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_type.csv",
        "task_type",
        build_counter((task.task_type for task in tasks), TASK_TYPE_ORDER),
        TASK_TYPE_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_type_major.csv",
        "task_type_major",
        build_counter((collapse_task_type_major(task.task_type) for task in tasks), TASK_TYPE_MAJOR_ORDER),
        TASK_TYPE_MAJOR_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_epoch_method.csv",
        "epoch_method",
        build_counter((task.epoch_method for task in tasks), EPOCH_METHOD_ORDER),
        EPOCH_METHOD_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_label_route.csv",
        "label_route",
        build_counter((task.label_route for task in tasks), LABEL_ROUTE_ORDER),
        LABEL_ROUTE_ORDER,
    )
    write_counter_csv(
        table_dir / "summary_tasks_by_meta_level.csv",
        "meta_level",
        build_counter((task.meta_level for task in tasks), META_LEVEL_ORDER),
        META_LEVEL_ORDER,
    )

    category_taskkind = build_nested_counter((task.category_group, task.task_kind) for task in tasks)
    write_matrix_csv(
        table_dir / "summary_tasks_by_category_and_kind.csv",
        "category_group",
        "task_kind",
        category_taskkind,
        CATEGORY_ORDER,
        TASK_KIND_ORDER,
    )
    status_category = build_nested_counter((document.status, document.category_group) for document in documents)
    write_matrix_csv(
        table_dir / "summary_documents_by_status_and_category.csv",
        "status",
        "category_group",
        status_category,
        STATUS_ORDER,
        CATEGORY_ORDER,
    )
    tasktype_epoch = build_nested_counter((task.task_type, task.epoch_method) for task in tasks)
    write_matrix_csv(
        table_dir / "summary_tasks_by_type_and_epoch_method.csv",
        "task_type",
        "epoch_method",
        tasktype_epoch,
        TASK_TYPE_ORDER,
        EPOCH_METHOD_ORDER,
    )
    tasktype_epoch_major = build_nested_counter(
        (collapse_task_type_major(task.task_type), task.epoch_method) for task in tasks
    )
    write_matrix_csv(
        table_dir / "summary_tasks_by_type_major_and_epoch_method.csv",
        "task_type_major",
        "epoch_method",
        tasktype_epoch_major,
        TASK_TYPE_MAJOR_ORDER,
        EPOCH_METHOD_ORDER,
    )
    tasktype_label = build_nested_counter((task.task_type, task.label_route) for task in tasks)
    write_matrix_csv(
        table_dir / "summary_tasks_by_type_and_label_route.csv",
        "task_type",
        "label_route",
        tasktype_label,
        TASK_TYPE_ORDER,
        LABEL_ROUTE_ORDER,
    )
    tasktype_label_major = build_nested_counter(
        (collapse_task_type_major(task.task_type), task.label_route) for task in tasks
    )
    write_matrix_csv(
        table_dir / "summary_tasks_by_type_major_and_label_route.csv",
        "task_type_major",
        "label_route",
        tasktype_label_major,
        TASK_TYPE_MAJOR_ORDER,
        LABEL_ROUTE_ORDER,
    )

    top_datasets = sorted(
        (
            {
                "dataset_name": document.dataset_name,
                "task_count": document.task_count,
                "category_group": document.category_group,
                "status": document.status,
            }
            for document in documents
        ),
        key=lambda row: (-int(row["task_count"]), row["dataset_name"]),
    )
    write_csv(
        table_dir / "top_datasets_by_task_count.csv",
        top_datasets,
        ["dataset_name", "task_count", "category_group", "status"],
    )


def export_figures(documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord], figure_dir: Path) -> None:
    ensure_dir(figure_dir)

    document_status = build_counter((document.status for document in documents), STATUS_ORDER)
    document_category = build_counter((document.category_group for document in documents), CATEGORY_ORDER)
    document_super_meta = build_counter((document.super_meta_required for document in documents), ["no", "yes", "missing"])
    task_kind = build_counter((task.task_kind for task in tasks), TASK_KIND_ORDER)
    task_type = build_counter((task.task_type for task in tasks), TASK_TYPE_ORDER)
    task_type_major = build_counter((collapse_task_type_major(task.task_type) for task in tasks), TASK_TYPE_MAJOR_ORDER)
    epoch_method = build_counter((task.epoch_method for task in tasks), EPOCH_METHOD_ORDER)
    label_route = build_counter((task.label_route for task in tasks), LABEL_ROUTE_ORDER)
    meta_level = build_counter((task.meta_level for task in tasks), META_LEVEL_ORDER)

    plot_barh_counts(
        document_category,
        figure_dir / "fig_documents_by_category",
        "Benchmark documents by category",
        "Number of documents",
        CATEGORY_ORDER,
        color=PAPER_COLOR["navy"],
    )
    plot_barh_counts(
        document_status,
        figure_dir / "fig_documents_by_status",
        "Benchmark documents by status",
        "Number of documents",
        STATUS_ORDER,
        color=PAPER_COLOR["orange"],
    )
    plot_barh_counts(
        document_super_meta,
        figure_dir / "fig_documents_by_super_meta_required",
        "Datasets requiring super-level metadata",
        "Number of documents",
        ["no", "yes", "missing"],
        color=PAPER_COLOR["green"],
    )
    plot_histogram(
        [document.task_count for document in documents],
        figure_dir / "fig_tasks_per_dataset_histogram",
        "Tasks per dataset document",
        "Tasks defined in a document",
        "Number of documents",
        color=PAPER_COLOR["green"],
    )
    plot_barh_counts(
        task_kind,
        figure_dir / "fig_tasks_by_kind",
        "Task definitions by task kind",
        "Number of tasks",
        TASK_KIND_ORDER,
        color=PAPER_COLOR["orange"],
    )
    plot_barh_counts(
        task_type,
        figure_dir / "fig_tasks_by_type",
        "Task definitions by task type",
        "Number of tasks",
        TASK_TYPE_ORDER,
        color=PAPER_COLOR["red"],
    )
    plot_barh_counts(
        task_type_major,
        figure_dir / "fig_tasks_by_type_major",
        "Task definitions by task type (major groups)",
        "Number of tasks",
        TASK_TYPE_MAJOR_ORDER,
        color=PAPER_COLOR["red"],
    )
    plot_barh_counts(
        epoch_method,
        figure_dir / "fig_tasks_by_epoch_method",
        "Task definitions by epoch method",
        "Number of tasks",
        EPOCH_METHOD_ORDER,
        color=PAPER_COLOR["navy"],
    )
    plot_barh_counts(
        label_route,
        figure_dir / "fig_tasks_by_label_route",
        "Task definitions by label route",
        "Number of tasks",
        LABEL_ROUTE_ORDER,
        color=PAPER_COLOR["gold"],
    )
    plot_barh_counts(
        meta_level,
        figure_dir / "fig_tasks_by_meta_level",
        "Task definitions by meta level",
        "Number of tasks",
        META_LEVEL_ORDER,
        color=PAPER_COLOR["green"],
    )

    category_taskkind = build_nested_counter((task.category_group, task.task_kind) for task in tasks)
    plot_stacked_barh(
        category_taskkind,
        CATEGORY_ORDER,
        TASK_KIND_ORDER,
        figure_dir / "fig_category_taskkind_stacked",
        "Task-kind composition within each category",
        "Number of tasks",
    )

    status_category = build_nested_counter((document.status, document.category_group) for document in documents)
    plot_stacked_barh(
        status_category,
        STATUS_ORDER,
        CATEGORY_ORDER,
        figure_dir / "fig_status_category_stacked",
        "Category mix across document statuses",
        "Number of documents",
    )

    tasktype_epoch = build_nested_counter((task.task_type, task.epoch_method) for task in tasks)
    plot_heatmap(
        tasktype_epoch,
        TASK_TYPE_ORDER,
        EPOCH_METHOD_ORDER,
        figure_dir / "fig_tasktype_epochmethod_heatmap",
        "Task type vs. epoch method",
        "Task count",
    )
    tasktype_epoch_major = build_nested_counter(
        (collapse_task_type_major(task.task_type), task.epoch_method) for task in tasks
    )
    plot_heatmap(
        tasktype_epoch_major,
        TASK_TYPE_MAJOR_ORDER,
        EPOCH_METHOD_ORDER,
        figure_dir / "fig_tasktype_epochmethod_heatmap_major",
        "Task type vs. epoch method (major groups)",
        "Task count",
    )

    tasktype_label = build_nested_counter((task.task_type, task.label_route) for task in tasks)
    plot_heatmap(
        tasktype_label,
        TASK_TYPE_ORDER,
        LABEL_ROUTE_ORDER,
        figure_dir / "fig_tasktype_labelroute_heatmap",
        "Task type vs. label route",
        "Task count",
    )
    tasktype_label_major = build_nested_counter(
        (collapse_task_type_major(task.task_type), task.label_route) for task in tasks
    )
    plot_heatmap(
        tasktype_label_major,
        TASK_TYPE_MAJOR_ORDER,
        LABEL_ROUTE_ORDER,
        figure_dir / "fig_tasktype_labelroute_heatmap_major",
        "Task type vs. label route (major groups)",
        "Task count",
    )

    top_documents = sorted(documents, key=lambda item: (-item.task_count, item.dataset_name))[:20]
    top_counter = Counter({document.dataset_name: document.task_count for document in top_documents})
    plot_barh_counts(
        top_counter,
        figure_dir / "fig_top20_datasets_by_task_count",
        "Top 20 datasets by number of defined tasks",
        "Number of tasks",
        [document.dataset_name for document in top_documents],
        color=PAPER_COLOR["navy"],
    )


def write_overview_json(path: Path, documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord]) -> None:
    overview = {
        "document_count": len(documents),
        "task_count": len(tasks),
        "tasks_per_dataset": {
            "mean": round(sum(document.task_count for document in documents) / float(len(documents)), 3)
            if documents
            else 0.0,
            "median": statistics.median([document.task_count for document in documents]) if documents else 0,
            "min": min((document.task_count for document in documents), default=0),
            "max": max((document.task_count for document in documents), default=0),
        },
        "documents_by_status": dict(build_counter((document.status for document in documents), STATUS_ORDER)),
        "documents_by_category": dict(build_counter((document.category_group for document in documents), CATEGORY_ORDER)),
        "tasks_by_kind": dict(build_counter((task.task_kind for task in tasks), TASK_KIND_ORDER)),
        "tasks_by_type": dict(build_counter((task.task_type for task in tasks), TASK_TYPE_ORDER)),
        "tasks_by_epoch_method": dict(build_counter((task.epoch_method for task in tasks), EPOCH_METHOD_ORDER)),
        "tasks_by_label_route": dict(build_counter((task.label_route for task in tasks), LABEL_ROUTE_ORDER)),
        "tasks_by_meta_level": dict(build_counter((task.meta_level for task in tasks), META_LEVEL_ORDER)),
    }
    path.write_text(json.dumps(overview, indent=2, ensure_ascii=False), encoding="utf-8")


def export_paper_panels(documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord], figure_dir: Path) -> None:
    document_super_meta = filter_counter(
        build_counter((document.super_meta_required for document in documents), PAPER_SUPER_META_ORDER),
        PAPER_SUPER_META_ORDER,
    )
    task_kind_filtered = filter_counter(
        build_counter((task.task_kind for task in tasks), PAPER_TASK_KIND_FILTERED_ORDER),
        PAPER_TASK_KIND_FILTERED_ORDER,
    )
    label_route = filter_counter(
        build_counter((task.label_route for task in tasks), PAPER_LABEL_ROUTE_ORDER),
        PAPER_LABEL_ROUTE_ORDER,
    )
    meta_level = filter_counter(
        build_counter((task.meta_level for task in tasks), PAPER_META_LEVEL_ORDER),
        PAPER_META_LEVEL_ORDER,
    )
    category_taskkind = build_nested_counter((task.category_group, task.task_kind) for task in tasks)
    tasktype_epoch = build_nested_counter(
        (
            collapse_task_type_major(task.task_type),
            task.epoch_method,
        )
        for task in tasks
        if collapse_task_type_major(task.task_type) in PAPER_HEATMAP_TASK_TYPES and task.epoch_method in PAPER_EPOCH_METHOD_ORDER
    )

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    draw_stacked_barh_panel(
        ax,
        category_taskkind,
        CATEGORY_ORDER,
        PAPER_TASK_KIND_FILTERED_ORDER,
        "Task-kind composition across EEG categories",
        "Number of tasks",
        PAPER_DISPLAY_LABELS,
    )
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    save_figure(fig, figure_dir / "fig_category_taskkind_stacked_paper")

    fig, ax = plt.subplots(figsize=(3.2, 3.0))
    draw_meta_type_dual_axis_panel(
        ax,
        document_super_meta,
        meta_level,
        "Meta Type",
    )
    save_figure(fig, figure_dir / "fig_meta_type_dualaxis_paper")

    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_bar_panel(
        ax,
        task_kind_filtered,
        "Task Type",
        "Number of tasks",
        PAPER_TASK_KIND_FILTERED_ORDER,
        PAPER_COLOR["orange"],
        PAPER_DISPLAY_LABELS,
    )
    save_figure(fig, figure_dir / "fig_task_type_filtered_paper")

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    draw_bar_panel(
        ax,
        filter_counter(
            build_counter((task.epoch_method for task in tasks), PAPER_EPOCH_METHOD_ORDER),
            PAPER_EPOCH_METHOD_ORDER,
        ),
        "Task definitions by epoch method",
        "Number of tasks",
        PAPER_EPOCH_METHOD_ORDER,
        PAPER_COLOR["navy"],
        PAPER_DISPLAY_LABELS,
    )
    save_figure(fig, figure_dir / "fig_tasks_by_epoch_method_paper")

    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_bar_panel(
        ax,
        label_route,
        "Task targets by label route",
        "Number of tasks",
        PAPER_LABEL_ROUTE_ORDER,
        PAPER_COLOR["gold"],
        PAPER_DISPLAY_LABELS,
    )
    save_figure(fig, figure_dir / "fig_tasks_by_label_route_paper")

    fig, ax = plt.subplots(figsize=(3.2, 3.0))
    draw_bar_panel(
        ax,
        meta_level,
        "Task targets by meta level",
        "Number of tasks",
        PAPER_META_LEVEL_ORDER,
        PAPER_COLOR["green"],
        PAPER_DISPLAY_LABELS,
    )
    save_figure(fig, figure_dir / "fig_tasks_by_meta_level_paper")

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    draw_histogram_panel(
        ax,
        [document.task_count for document in documents],
        "Tasks per dataset document",
        "Tasks per dataset",
        "Number of documents",
        PAPER_COLOR["green"],
    )
    save_figure(fig, figure_dir / "fig_tasks_per_dataset_histogram_paper")

    fig, ax = plt.subplots(figsize=(5.0, 2.8))
    image = draw_heatmap_panel(
        ax,
        tasktype_epoch,
        PAPER_HEATMAP_TASK_TYPES,
        PAPER_EPOCH_METHOD_ORDER,
        "Task type vs. epoch method",
        PAPER_DISPLAY_LABELS,
    )
    colorbar = fig.colorbar(image, ax=ax, fraction=0.06, pad=0.04)
    colorbar.set_label("Task count")
    save_figure(fig, figure_dir / "fig_tasktype_epochmethod_heatmap_paper")


def export_resource_overview(documents: Sequence[DocumentRecord], tasks: Sequence[TaskRecord], output_base: Path) -> None:
    task_counts = [document.task_count for document in documents]
    document_super_meta = filter_counter(
        build_counter((document.super_meta_required for document in documents), PAPER_SUPER_META_ORDER),
        PAPER_SUPER_META_ORDER,
    )
    task_kind_filtered = filter_counter(
        build_counter((task.task_kind for task in tasks), PAPER_TASK_KIND_FILTERED_ORDER),
        PAPER_TASK_KIND_FILTERED_ORDER,
    )
    label_route = filter_counter(
        build_counter((task.label_route for task in tasks), PAPER_LABEL_ROUTE_ORDER),
        PAPER_LABEL_ROUTE_ORDER,
    )
    meta_level = filter_counter(
        build_counter((task.meta_level for task in tasks), PAPER_META_LEVEL_ORDER),
        PAPER_META_LEVEL_ORDER,
    )
    category_taskkind = build_nested_counter((task.category_group, task.task_kind) for task in tasks)
    tasktype_epoch = build_nested_counter(
        (
            collapse_task_type_major(task.task_type),
            task.epoch_method,
        )
        for task in tasks
        if collapse_task_type_major(task.task_type) in PAPER_HEATMAP_TASK_TYPES and task.epoch_method in PAPER_EPOCH_METHOD_ORDER
    )

    fig = plt.figure(figsize=(8.4, 10.9))
    grid = fig.add_gridspec(
        nrows=4,
        ncols=3,
        height_ratios=[0.72, 2.2, 1.7, 1.95],
        hspace=0.78,
        wspace=0.44,
    )

    ax_summary = fig.add_subplot(grid[0, :])
    ax_summary.axis("off")
    ax_summary.text(0.0, 0.93, "Documented EEG benchmark resource overview", fontsize=15, fontweight="bold", ha="left", va="top")
    summary_items = [
        (str(len(documents)), "Dataset documents"),
        (str(len(tasks)), "Task definitions"),
        ("0.00" if not documents else "{0:.2f}".format(sum(task_counts) / float(len(task_counts))), "Mean tasks / dataset"),
    ]
    x_positions = [0.06, 0.39, 0.72]
    for (value, label), x_pos in zip(summary_items, x_positions):
        ax_summary.text(x_pos, 0.35, value, fontsize=20, fontweight="bold", ha="center", va="center", color=PAPER_COLOR["navy"])
        ax_summary.text(x_pos, 0.05, label, fontsize=10, ha="center", va="center", color="#444444")

    ax_a = fig.add_subplot(grid[1, :])
    draw_stacked_barh_panel(
        ax_a,
        category_taskkind,
        CATEGORY_ORDER,
        PAPER_TASK_KIND_FILTERED_ORDER,
        "(A) Category coverage and task-kind composition",
        "",
        PAPER_DISPLAY_LABELS,
    )
    ax_a.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.12))

    row_two = grid[2, :].subgridspec(1, 3, width_ratios=[1.08, 1.16, 0.82], wspace=0.45)

    ax_b = fig.add_subplot(row_two[0, 0])
    draw_histogram_panel(
        ax_b,
        task_counts,
        "(B) Tasks per dataset",
        "Tasks / dataset",
        "Documents",
        PAPER_COLOR["green"],
    )

    ax_c = fig.add_subplot(row_two[0, 1])
    draw_meta_type_dual_axis_panel(
        ax_c,
        document_super_meta,
        meta_level,
        "(C) Meta Type",
    )

    ax_d = fig.add_subplot(row_two[0, 2])
    draw_bar_panel(
        ax_d,
        task_kind_filtered,
        "(D) Task Type",
        "Tasks",
        PAPER_TASK_KIND_FILTERED_ORDER,
        PAPER_COLOR["orange"],
        PAPER_DISPLAY_LABELS,
    )
    ax_d.set_ylabel("Tasks", labelpad=2)

    row_three = grid[3, :].subgridspec(1, 3, width_ratios=[0.92, 1.04, 1.04], wspace=0.42)

    ax_e = fig.add_subplot(row_three[0, 0])
    draw_bar_panel(
        ax_e,
        label_route,
        "(E) Label route",
        "Tasks",
        PAPER_LABEL_ROUTE_ORDER,
        PAPER_COLOR["gold"],
        PAPER_DISPLAY_LABELS,
    )

    ax_f = fig.add_subplot(row_three[0, 1:])
    image = draw_heatmap_panel(
        ax_f,
        tasktype_epoch,
        PAPER_HEATMAP_TASK_TYPES,
        PAPER_EPOCH_METHOD_ORDER,
        "(F) Task type vs. epoch method",
        PAPER_DISPLAY_LABELS,
    )
    colorbar = fig.colorbar(image, ax=ax_f, fraction=0.04, pad=0.02)
    colorbar.set_label("Task count")

    save_figure_file(fig, output_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    save_figure_file(fig, output_base.with_suffix(".pdf"), bbox_inches="tight")
    if _EXPORT_EPS:
        save_figure_file(fig, output_base.with_suffix(".eps"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse BIDS benchmark analysis.md documents and export paper-ready figures and tables."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help="Path to dataset_document root (default: {0})".format(DEFAULT_DATASET_DIR),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for figures/tables (default: {0})".format(DEFAULT_OUTPUT_DIR),
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=10,
        help="Base font size for generated figures.",
    )
    parser.add_argument(
        "--only_completed",
        action="store_true",
        help="Only include documents (and their tasks) whose status is 'completed'.",
    )
    parser.add_argument(
        "--eps",
        action="store_true",
        help="Additionally export all figures in EPS format.",
    )
    args = parser.parse_args()

    global _EXPORT_EPS
    _EXPORT_EPS = args.eps

    dataset_root = args.dataset_root
    if not dataset_root.exists():
        raise SystemExit("dataset root does not exist: {0}".format(dataset_root))

    configure_matplotlib(args.font_size)

    documents: list[DocumentRecord] = []
    tasks: list[TaskRecord] = []
    for analysis_path in iter_analysis_files(dataset_root):
        document_record, task_records = parse_document(analysis_path)
        documents.append(document_record)
        tasks.extend(task_records)

    if args.only_completed:
        documents = [doc for doc in documents if doc.status == "completed"]
        tasks = [task for task in tasks if task.document_status == "completed"]

    output_dir = args.output_dir
    figure_dir = output_dir / "figures"
    table_dir = output_dir / "tables"
    ensure_dir(output_dir)
    ensure_dir(figure_dir)
    ensure_dir(table_dir)

    export_tables(documents, tasks, table_dir)
    export_figures(documents, tasks, figure_dir)
    export_paper_panels(documents, tasks, figure_dir)
    export_resource_overview(documents, tasks, output_dir / "doc_resource_overview")
    write_overview_json(output_dir / "summary_overview.json", documents, tasks)
    write_summary_markdown(output_dir / "summary_overview.md", documents, tasks)

    completed_documents = [doc for doc in documents if doc.status == "completed"]
    completed_tasks = [task for task in tasks if task.document_status == "completed"]
    export_resource_overview(completed_documents, completed_tasks, output_dir / "doc_resource_overview_completed_only")

    print("dataset_root: {0}".format(dataset_root))
    print("documents: {0}".format(len(documents)))
    print("tasks: {0}".format(len(tasks)))
    print("output_dir: {0}".format(output_dir))
    print("figure_dir: {0}".format(figure_dir))
    print("table_dir: {0}".format(table_dir))


if __name__ == "__main__":
    main()
