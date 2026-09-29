from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from neurodoc.api import call_llm_text, check_analysis_text, load_rules
from neurodoc.paths import DATASET_DOCUMENT_DIR

_DETECT_RULES = load_rules()

_TASK_BLOCKING_RULES = {
    "classification_task_has_multiple_classes",
    "classification_y_zero_indexed_sequential",
    "derived_misc_requires_super_meta",
    "epoch_parameters_complete",
    "label_route_no_deprecated",
    "no_mi_on_phase_markers",
    "segmentation_requires_empty_target_events",
    "segmentation_requires_nonevent_route",
    "single_target_per_task",
    "target_def_schema_matches_route",
    "target_events_exist",
    "target_events_in_event_structure",
    "task_numbering_from_one",
    "task_order_classical_first",
    "task_type_no_normal",
}

_TD_HEADERS: dict[tuple[str, str], list[str]] = {
    ("event", "classification"): ["Event ID", "y", "Meaning"],
    ("event", "regression"): ["Event ID", "Value", "Meaning"],
    ("misc", "classification"): ["MISC Channel Name", "Y Mapping Notes"],
    ("misc", "regression"): ["MISC Channel Name", "Y Mapping Notes"],
    ("info", "classification"): ["Info Field", "Y Mapping Notes"],
    ("info", "regression"): ["Info Field", "Y Mapping Notes"],
}

_GEN_SYSTEM = """\
You are an EEG task documentation expert working in NeuroAudit.

You MUST stay inside the current audit document boundary:
- Use ONLY the current analysis.md content and the per-reference extraction results.
- Do NOT assume access to raw dataset files, events.tsv, sidecars, kernels, scans, or hidden context.
- Do NOT invent event IDs, misc channels, info fields, or participant columns that are not explicitly present in the current document grounding lists.

You will receive:
1. analysis.md context excluding the current Tasks section,
2. document-grounded white lists from the current analysis.md:
   - Event IDs from ### Event Structure where Type = event
   - MISC channels from ### MISC Label Summary
   - Info fields from ### Info
3. Phase-1 reference extraction summaries.

Generate a complete replacement ## Tasks section that strictly follows the app + rulebook constraints.

Hard rules:
- Valid Label Route values: event | misc | info
- Never output Annotation, STIM, MISC, Normal Task, or other deprecated labels.
- Do NOT output a `Label Field` bullet. It is deprecated for every route.
- For misc/info routes, the label source is the first and only row of Target Definition.
- Route=misc allows both classification and regression.
- segmentation => target_events = [] and Route must not be event.
- event-route target_events and Event ID rows must come only from the provided event whitelist.
- misc-route Target Definition source must come only from the provided MISC whitelist.
- info-route Target Definition source must come only from the provided Info whitelist.
- One task = one label source. Split multidimensional labels into separate tasks.
- Classification y values must be 0-based sequential integers.
- Event-route classification must have at least 2 distinct classes.
- Target Definition header must exactly match the canonical schema for Route x Task Type.

Canonical Target Definition headers:
- event + classification: | Event ID | y | Meaning |
- event + regression: | Event ID | Value | Meaning |
- misc + classification: | MISC Channel Name | Y Mapping Notes |
- misc + regression: | MISC Channel Name | Y Mapping Notes |
- info + classification: | Info Field | Y Mapping Notes |
- info + regression: | Info Field | Y Mapping Notes |

For misc/info routes:
- Target Definition must have exactly one data row.
- `Y Mapping Notes` must explain value-to-y mapping for classification.
- Use `no mapping` when y directly follows the source field or channel value.

Epoch parameter minimums:
- epoch_by_event_hdf5: tmin, tmax, target_events
- epoch_by_long_event_hdf5: tmin, tmax, overlap, target_events
- epoch_by_segmentation_hdf5: segment_length, overlap, target_events=[]

Grounding policy:
- If a reference suggests a task that cannot be grounded to the current document white lists, DROP it.
- Prefer fewer valid tasks over invented tasks.
- If no valid task can be grounded, return an empty but valid Tasks section.

Formatting requirements for tasks_section:
- Each task heading MUST be exactly `### Classical Task N: <title>` or `### Potential Task N: <title>`.
- Every task field MUST use the exact bullet syntax `- **Field Name**: value`.
- Use these exact field names only:
  - `Task Type`
  - `Epoch Method`
  - `Epoch Parameters`
  - `Label Route`
  - `Meta Level`
  - `Target Definition`
  - `Evidence`
  - `Notes`
- Do NOT use aliases such as `Route`, `Details`, `Description`, or YAML section labels.
- `Epoch Parameters` MUST be one single line of comma-separated `key = value` pairs.
- `Target Definition` MUST be a markdown table placed immediately under `- **Target Definition**:`.
- `Evidence` MUST be a markdown bullet list placed immediately under `- **Evidence**:`.
- Every Evidence bullet MUST use the exact format `- <ref> — <description>` when a
  description exists. Use a literal em dash with one space on each side: ` — `.
- Do NOT use `DOI:` prefixes.
- Do NOT use ` - ` as the separator between ref and description.

Canonical task skeleton:
### Classical Task 1: Example title
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, target_events = [`event_a`, `event_b`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_a` | 0 | class A |
  | `event_b` | 1 | class B |
- **Evidence**:
  - 10.0000/example — concise evidence
- **Notes**: optional notes

Canonical misc/info example:
### Potential Task 1: Example source-level label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5, target_events = []
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `misc:p_factor` | no mapping |
- **Evidence**:
  - none
- **Notes**: optional notes

Output JSON only:
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...",
  "summary": "<one sentence>",
  "dropped_notes": ["<short note>", "..."]
}
"""

_REPAIR_SYSTEM = """\
You are repairing a neuroaudit ## Tasks section using ONLY current-document grounding.

You will receive:
- the current Tasks section,
- the current analysis.md grounding white lists,
- blocking semantic / grounding errors.

Repair rules:
- Stay doc-only: never introduce any Event ID, MISC channel, or Info field outside the provided white lists.
- Fix in place when possible: numbering, y renumbering, Label Route normalization, Target Definition header normalization, target_events cleanup.
- Remove any legacy `Label Field` bullet; for misc/info routes, keep the source only in the first column of Target Definition.
- misc/info Target Definition tables must use the two-column v1.0.0 schema and exactly one row.
- Drop a task only if it cannot be grounded to the current document.
- Keep Classical tasks before Potential tasks.
- Event-route classification y values must be 0-based sequential integers.
- segmentation must use target_events = [] and non-event route.

Output JSON only:
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...",
  "changes_summary": "<short summary>"
}
"""


def _analysis_path(dataset_name: str) -> Path:
    return DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"


def load_analysis_md(dataset_name: str) -> str:
    path = _analysis_path(dataset_name)
    if not path.exists():
        raise FileNotFoundError(f"analysis.md not found for dataset '{dataset_name}'")
    return path.read_text(encoding="utf-8", errors="replace")


def _load_llm_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"LLM config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def _call_llm_factory(llm_config: dict[str, Any]) -> Callable[[list[dict[str, str]], int], str]:
    def _call(messages: list[dict[str, str]], timeout: int = 240) -> str:
        return call_llm_text(llm_config, messages, timeout=timeout)

    return _call


def _parse_llm_json(raw: str) -> tuple[dict[str, Any] | None, str | None]:
    text = re.sub(r"<think>[\s\S]*?</think>", "", str(raw or ""), flags=re.IGNORECASE).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None, "No JSON object found."
    try:
        return json.loads(match.group(0)), None
    except json.JSONDecodeError as exc:
        return None, f"JSON decode error: {exc}"


def _extract_section_block(text: str, title: str, level: int) -> str:
    pattern = rf"(^{'#' * level}\s+{re.escape(title)}\s*$.*?)(?=^\#{{1,{level}}}\s+|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_section_body(text: str, title: str, level: int) -> str:
    block = _extract_section_block(text, title, level)
    if not block:
        return ""
    idx = block.find("\n")
    return block[idx + 1 :].strip() if idx >= 0 else ""


def _remove_tasks_section(analysis_md: str) -> str:
    return re.sub(r"\n##\s*Tasks\s*\n.*?(?=\n## |\Z)", "\n## Tasks\n\n(omitted for regeneration context)\n", analysis_md, flags=re.DOTALL)


def _parse_markdown_table_with_header(body: str) -> tuple[list[str], list[list[str]]]:
    header: list[str] = []
    rows: list[list[str]] = []
    seen_header = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line.startswith("|") or line.count("|") < 2:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells:
            continue
        if not seen_header:
            header = cells
            seen_header = True
            continue
        if all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells):
            continue
        rows.append(cells)
    return header, rows


def _parse_markdown_table(body: str) -> list[list[str]]:
    _, rows = _parse_markdown_table_with_header(body)
    return rows


def _clean_token(value: str) -> str:
    out = (value or "").strip()
    changed = True
    while out and changed:
        changed = False
        if len(out) >= 2 and (
            (out[0] == out[-1] == "`")
            or (out[0] == out[-1] == '"')
            or (out[0] == out[-1] == "'")
        ):
            out = out[1:-1].strip()
            changed = True
    return out.strip()


def _normalize_label_route(value: str) -> str:
    cleaned = _clean_token(value).lower()
    aliases = {
        "annotation": "event",
        "stim": "event",
        "event": "event",
        "misc": "misc",
        "info": "info",
    }
    return aliases.get(cleaned, cleaned)


def _extract_task_field(block: str, field_names: str | list[str]) -> str | None:
    names = field_names if isinstance(field_names, list) else [field_names]
    lines = block.splitlines()
    field_re = re.compile(r"^\s*(?:-\s*)?\*\*[^*]+\*\*:\s*")
    for i, line in enumerate(lines):
        for field in names:
            m = re.match(rf"^\s*(?:-\s*)?\*\*{re.escape(field)}\*\*:\s*(.*)$", line)
            if not m:
                continue
            body: list[str] = []
            if m.group(1).strip():
                body.append(m.group(1).rstrip())
            for j in range(i + 1, len(lines)):
                if field_re.match(lines[j]):
                    break
                if re.match(r"^###\s+", lines[j]):
                    break
                body.append(lines[j])
            return "\n".join(body).strip()
    return None


def _split_task_blocks(tasks_section: str) -> list[str]:
    text = (tasks_section or "").strip()
    if text.startswith("## Tasks"):
        text = re.sub(r"^##\s*Tasks\s*", "", text, count=1).strip()
    return [b.strip() for b in re.split(r"(?=^###\s+)", text, flags=re.MULTILINE) if b.strip()]


def _event_rows_from_analysis(analysis_md: str) -> list[dict[str, str]]:
    body = _extract_section_body(_extract_section_block(analysis_md, "File Scan Result", 2), "Event Structure", 3)
    rows = _parse_markdown_table(body)
    result: list[dict[str, str]] = []
    for cells in rows:
        row = {
            "event_id": _clean_token(cells[0]) if len(cells) > 0 else "",
            "type": cells[2].strip().lower() if len(cells) > 2 else "",
        }
        if row["event_id"]:
            result.append(row)
    return result


def extract_analysis_grounding(analysis_md: str) -> dict[str, list[str]]:
    fsr_block = _extract_section_block(analysis_md, "File Scan Result", 2)
    misc_body = _extract_section_body(fsr_block, "MISC Label Summary", 3)
    info_body = _extract_section_body(fsr_block, "Info", 3)

    event_rows = _event_rows_from_analysis(analysis_md)
    event_ids = [r["event_id"] for r in event_rows if r.get("type") == "event"]
    if not event_ids:
        event_ids = [r["event_id"] for r in event_rows]

    misc_fields = [_clean_token(row[0]) for row in _parse_markdown_table(misc_body) if row and _clean_token(row[0])]
    info_fields = [_clean_token(row[0]) for row in _parse_markdown_table(info_body) if row and _clean_token(row[0])]

    return {
        "analysis_event_ids": list(dict.fromkeys(event_ids)),
        "analysis_misc_fields": list(dict.fromkeys(misc_fields)),
        "analysis_info_fields": list(dict.fromkeys(info_fields)),
    }


def _run_task_semantic_checks(tasks_section: str, dataset_name: str, analysis_md: str) -> list[dict[str, Any]]:
    ts = (tasks_section or "").strip()
    if not ts.startswith("##"):
        ts = "## Tasks\n\n" + ts

    fsr_block = _extract_section_block(analysis_md, "File Scan Result", 2)
    if not fsr_block:
        fsr_block = (
            "## File Scan Result\n\n"
            "### Event Structure\n\n| Event ID | Count | Type | Meta Level | Meaning |\n|---|---|---|---|---|\n\n"
            "### MISC Label Summary\n\n| Channel | Source | Meta | Notes |\n|---|---|---|---|\n\n"
            "### Info\n\n| Field | Completeness | Notes |\n|---|---|---|\n"
        )

    shell = (
        "# Analysis\n\n"
        "## Paradigm\n\n(stub)\n\n"
        f"{fsr_block}\n\n"
        f"{ts}\n\n"
        "## Data Quality Notes\n\n- (stub)\n\n"
        "## Kernel Responsibilities\n\n> **Super Meta Required**: No\n> **Status**: wait_manual_review\n"
    )
    violations = check_analysis_text(shell, dataset_name=dataset_name, rules=_DETECT_RULES)
    return [v for v in violations if v.get("rule_id") in _TASK_BLOCKING_RULES]


def format_semantic_errors(violations: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for v in violations:
        rid = v.get("rule_id", "?")
        sev = v.get("severity", "?")
        desc = v.get("desc", "") or ""
        detail = v.get("detail", "") or ""
        if desc and detail:
            result.append(f"[{sev}] {rid}: {desc} - {detail}")
        elif desc:
            result.append(f"[{sev}] {rid}: {desc}")
        else:
            result.append(f"[{sev}] {rid}: {detail}")
    return result


def _compress_extractions(extractions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keep = (
        "reference_file",
        "ref",
        "classification",
        "supports_task",
        "task_type",
        "n_classes",
        "paradigm",
        "epoch_method_hint",
        "epoch_params",
        "target_events",
        "label_mapping",
        "meta_level",
        "super_meta_note",
        "evidence_desc",
    )
    useful = [e for e in extractions if e.get("classification") in {"relevant", "partial"}]
    return [{k: e.get(k) for k in keep if e.get(k) not in (None, "", [])} for e in useful]


def _build_generation_user_msg(
    dataset_name: str,
    analysis_md: str,
    grounding: dict[str, list[str]],
    extractions: list[dict[str, Any]],
    skill_text: str,
) -> str:
    refs = _compress_extractions(extractions)
    return (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md context (Tasks omitted) ===\n{_remove_tasks_section(analysis_md)}\n\n"
        f"=== Document-grounded Event whitelist ===\n{json.dumps(grounding['analysis_event_ids'], ensure_ascii=False)}\n\n"
        f"=== Document-grounded MISC whitelist ===\n{json.dumps(grounding['analysis_misc_fields'], ensure_ascii=False)}\n\n"
        f"=== Document-grounded Info whitelist ===\n{json.dumps(grounding['analysis_info_fields'], ensure_ascii=False)}\n\n"
        f"=== Category skill hint ===\n{skill_text[:2000]}\n\n"
        f"=== Phase-1 reference extractions ===\n{json.dumps(refs, ensure_ascii=False, indent=2)}\n\n"
        "Write a complete replacement ## Tasks section using only the document-grounded white lists above."
    )


def _build_repair_user_msg(
    dataset_name: str,
    analysis_md: str,
    grounding: dict[str, list[str]],
    tasks_section: str,
    errors: list[str],
) -> str:
    return (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md context (Tasks omitted) ===\n{_remove_tasks_section(analysis_md)}\n\n"
        f"=== Event whitelist ===\n{json.dumps(grounding['analysis_event_ids'], ensure_ascii=False)}\n\n"
        f"=== MISC whitelist ===\n{json.dumps(grounding['analysis_misc_fields'], ensure_ascii=False)}\n\n"
        f"=== Info whitelist ===\n{json.dumps(grounding['analysis_info_fields'], ensure_ascii=False)}\n\n"
        f"=== Current Tasks ===\n{tasks_section}\n\n"
        f"=== Errors to fix ===\n{json.dumps(errors, ensure_ascii=False, indent=2)}\n\n"
        "Repair the Tasks section while staying inside the document white lists."
    )


def _parse_epoch_params_dict(epoch_params_raw: str) -> tuple[dict[str, str], list[str]]:
    raw = (epoch_params_raw or "").strip()
    if not raw:
        return {}, []
    pairs: dict[str, str] = {}
    custom: list[str] = []
    known_keys = {"tmin", "tmax", "overlap", "segment_length", "target_events"}

    def _remember(key: str, value: str) -> None:
        clean_key = _clean_token(key)
        clean_val = value.strip().rstrip(",")
        if not clean_key or not clean_val:
            return
        if clean_key == "target_events":
            if clean_val.startswith("[") and clean_val.endswith("]"):
                clean_val = clean_val[1:-1].strip()
            pairs["target_events"] = clean_val
            return
        pairs[clean_key] = clean_val
        if clean_key not in known_keys:
            entry = f"{clean_key} = {clean_val}"
            if entry not in custom:
                custom.append(entry)

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^-\s*", "", stripped)
        m = re.match(r"^['\"`]?([A-Za-z_][A-Za-z0-9_]*)['\"`]?\s*[:=]\s*(.+)$", stripped)
        if m:
            _remember(m.group(1), m.group(2))

    flat = raw.replace("\n", ", ")
    for m in re.finditer(r"['\"`]?([A-Za-z_][A-Za-z0-9_]*)['\"`]?\s*[:=]\s*(\[[^\]]*\]|[^,\n]+)", flat):
        _remember(m.group(1), m.group(2))
    return pairs, custom


def _parse_target_events(raw: str) -> list[str]:
    text = (raw or "").strip()
    quoted_matches = re.findall(r"`([^`]+)`|\"([^\"]+)\"|'([^']+)'", text)
    if quoted_matches:
        items: list[str] = []
        for groups in quoted_matches:
            token = _clean_token(next((g for g in groups if g), ""))
            if token and token not in items:
                items.append(token)
        return items
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    items: list[str] = []
    for piece in re.split(r"[,;\n]", text):
        token = _clean_token(piece)
        if token and token not in items:
            items.append(token)
    return items


def _parse_evidence_lines(block: str) -> list[str]:
    field = _extract_task_field(block, "Evidence") or ""
    lines: list[str] = []
    for raw in field.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        elif line:
            line = line.lstrip("* ").strip()
        else:
            continue
        normalized = _normalize_evidence_line(line)
        if normalized:
            lines.append(normalized)
    return lines


def _normalize_evidence_line(line: str) -> str:
    text = (line or "").strip()
    if not text:
        return ""
    text = re.sub(r"^DOI:\s*", "", text, flags=re.IGNORECASE).strip()
    if " — " in text:
        ref, desc = text.split(" — ", 1)
        ref = ref.strip()
        desc = desc.strip()
        return f"- {ref} — {desc}" if ref and desc else (f"- {ref}" if ref else "")
    if " - " in text:
        ref, desc = text.split(" - ", 1)
        ref = ref.strip()
        desc = desc.strip()
        return f"- {ref} — {desc}" if ref and desc else (f"- {ref}" if ref else "")
    return f"- {text}"


def _parse_task_block(block: str) -> dict[str, Any]:
    heading = block.splitlines()[0] if block.splitlines() else ""
    hm = re.match(r"^###\s+(Classical|Potential)\s+Task(?:\s+\d+)?\s*:\s*(.+)$", heading)
    kind = hm.group(1) if hm else "Potential"
    title = hm.group(2).strip() if hm else heading.lstrip("# ").strip()
    task_type = _clean_token(_extract_task_field(block, "Task Type") or "classification").lower()
    epoch_method = _clean_token(_extract_task_field(block, "Epoch Method") or "epoch_by_event_hdf5")
    epoch_pairs, epoch_custom = _parse_epoch_params_dict(_extract_task_field(block, "Epoch Parameters") or "")
    label_route = _normalize_label_route(_extract_task_field(block, ["Label Route", "Route"]) or "event")
    label_field = _clean_token(_extract_task_field(block, "Label Field") or "")
    meta_level = _clean_token(_extract_task_field(block, "Meta Level") or "raw").lower() or "raw"
    td_field = _extract_task_field(block, "Target Definition") or ""
    td_header, td_rows = _parse_markdown_table_with_header(td_field)
    notes = _extract_task_field(block, ["Notes", "Details", "Kernel Notes", "Description"]) or ""
    return {
        "kind": kind,
        "title": title,
        "task_type": task_type,
        "epoch_method": epoch_method,
        "epoch_pairs": epoch_pairs,
        "epoch_custom": epoch_custom,
        "label_route": label_route,
        "label_field": label_field,
        "meta_level": meta_level,
        "td_header": td_header,
        "td_rows": td_rows,
        "evidence": _parse_evidence_lines(block),
        "notes": notes.strip(),
    }


def _canonical_td_rows(task: dict[str, Any]) -> list[list[str]]:
    rows = [[_clean_token(c) for c in row] for row in task.get("td_rows", [])]
    route = task["label_route"]
    task_type = task["task_type"]
    if route == "event":
        out: list[list[str]] = []
        for row in rows:
            label = row[0] if len(row) > 0 else ""
            second = row[1] if len(row) > 1 else ""
            meaning = row[2] if len(row) > 2 else ""
            out.append([label, second, meaning])
        return out
    if route in {"misc", "info"}:
        header = [_clean_token(h).lower() for h in task.get("td_header", [])]
        grouped: dict[str, list[str]] = {}
        order: list[str] = []
        fallback = _clean_token(task.get("label_field", ""))

        for row in rows:
            label = row[0] if len(row) > 0 else fallback
            if not label:
                continue

            note = ""
            if len(row) >= 2:
                if len(row) == 2 or (len(header) >= 2 and header[1] == "y mapping notes"):
                    note = row[1]
                elif len(row) >= 4 and "y" in header:
                    note = f"{row[1]} -> {row[2]}"
                    if row[3]:
                        note += f" ({row[3]})"
                else:
                    note = "; ".join(c for c in row[1:] if c)
            note = note or "no mapping"

            if label not in grouped:
                grouped[label] = []
                order.append(label)
            if note not in grouped[label]:
                grouped[label].append(note)

        return [[label, "; ".join(grouped[label]) or "no mapping"] for label in order]
    return rows


def _repair_classification_y(task: dict[str, Any], rows: list[list[str]]) -> list[list[str]]:
    route = task["label_route"]
    if task["task_type"] != "classification" or route != "event":
        return rows
    key_idx, y_idx = 0, 1
    keys = [(_clean_token(row[key_idx]) if len(row) > key_idx else "") for row in rows]
    uniq: list[str] = []
    for key in keys:
        if key and key not in uniq:
            uniq.append(key)
    if len(uniq) < 2:
        return rows
    mapping = {key: str(i) for i, key in enumerate(uniq)}
    out: list[list[str]] = []
    for row in rows:
        new_row = list(row)
        key = _clean_token(row[key_idx]) if len(row) > key_idx else ""
        while len(new_row) <= y_idx:
            new_row.append("")
        new_row[y_idx] = mapping.get(key, new_row[y_idx])
        out.append(new_row)
    return out


def _normalize_task(task: dict[str, Any], grounding: dict[str, list[str]]) -> dict[str, Any] | None:
    event_ids = set(grounding["analysis_event_ids"])
    misc_fields = set(grounding["analysis_misc_fields"])
    info_fields = set(grounding["analysis_info_fields"])

    task["title"] = task["title"].replace("Normal Task", "").strip() or "Unnamed task"
    task["label_route"] = _normalize_label_route(task["label_route"])
    if task["task_type"] not in {"classification", "regression"}:
        return None

    rows = _canonical_td_rows(task)
    label_field = _clean_token(task["label_field"])
    if task["label_route"] in {"misc", "info"} and rows:
        label_field = _clean_token(rows[0][0])
    task["label_field"] = label_field

    epoch_pairs = {k: v for k, v in task["epoch_pairs"].items()}
    target_events = _parse_target_events(epoch_pairs.get("target_events", ""))
    if task["epoch_method"] == "epoch_by_segmentation_hdf5":
        target_events = []
    else:
        target_events = [e for e in target_events if e in event_ids]
    task["target_events"] = target_events

    if task["label_route"] == "event":
        task["label_field"] = ""
        cleaned_rows = []
        for row in rows:
            label = _clean_token(row[0]) if len(row) > 0 else ""
            if label not in event_ids:
                continue
            cleaned_rows.append([label, row[1] if len(row) > 1 else "", row[2] if len(row) > 2 else ""])
        rows = cleaned_rows
        if task["epoch_method"] != "epoch_by_segmentation_hdf5":
            if target_events:
                rows = [row for row in rows if row[0] in set(target_events)]
            else:
                target_events = [row[0] for row in rows if row[0] in event_ids]
                task["target_events"] = list(dict.fromkeys(target_events))
        if task["epoch_method"] == "epoch_by_segmentation_hdf5":
            return None
    elif task["label_route"] == "misc":
        if label_field not in misc_fields:
            return None
        distinct_sources = {_clean_token(row[0]) for row in rows if row and _clean_token(row[0])}
        if len(distinct_sources) > 1:
            return None
        notes = rows[0][1] if rows and len(rows[0]) > 1 else "no mapping"
        rows = [[label_field, notes or "no mapping"]]
        if task["epoch_method"] == "epoch_by_segmentation_hdf5":
            task["target_events"] = []
    elif task["label_route"] == "info":
        if label_field not in info_fields:
            return None
        distinct_sources = {_clean_token(row[0]) for row in rows if row and _clean_token(row[0])}
        if len(distinct_sources) > 1:
            return None
        notes = rows[0][1] if rows and len(rows[0]) > 1 else "no mapping"
        rows = [[label_field, notes or "no mapping"]]
        if task["epoch_method"] == "epoch_by_segmentation_hdf5":
            task["target_events"] = []
    else:
        return None

    rows = _repair_classification_y(task, rows)
    task["td_rows"] = rows
    notes_lower = (task.get("notes") or "").lower()
    if "placeholder" in notes_lower:
        return None

    if task["task_type"] == "classification":
        if task["label_route"] == "event":
            classes = {_clean_token(row[1]) for row in rows if len(row) > 1 and _clean_token(row[1])}
            if len(classes) < 2:
                return None
        elif task["label_route"] in {"misc", "info"}:
            notes = _clean_token(rows[0][1]) if rows and len(rows[0]) > 1 else ""
            if not notes:
                return None

    required = {
        "epoch_by_event_hdf5": ["tmin", "tmax"],
        "epoch_by_long_event_hdf5": ["tmin", "tmax", "overlap"],
        "epoch_by_segmentation_hdf5": ["segment_length", "overlap"],
    }.get(task["epoch_method"], [])
    for key in required:
        if not _clean_token(epoch_pairs.get(key, "")):
            return None
    if task["epoch_method"] != "epoch_by_segmentation_hdf5" and not task["target_events"] and task["label_route"] == "event":
        return None

    if task["meta_level"] not in {"raw", "super"}:
        task["meta_level"] = "raw"
    if task["label_route"] != "misc" and task["meta_level"] == "super":
        task["meta_level"] = "raw"
    return task


def _serialize_epoch_params(task: dict[str, Any]) -> str:
    pairs = dict(task["epoch_pairs"])
    pairs["target_events"] = ", ".join(f"`{e}`" for e in task["target_events"])
    parts: list[str] = []
    ordered = ["tmin", "tmax", "segment_length", "overlap"]
    for key in ordered:
        val = _clean_token(pairs.get(key, ""))
        if not val:
            continue
        if key in {"tmin", "tmax", "segment_length"} and not re.search(r"\bs\b", val):
            val = f"{val} s"
        parts.append(f"{key} = {val}")
    parts.extend(task.get("epoch_custom", []))
    parts.append(
        "target_events = []"
        if task["epoch_method"] == "epoch_by_segmentation_hdf5"
        else "target_events = [" + pairs["target_events"] + "]"
    )
    return ", ".join(parts)


def _serialize_target_def(task: dict[str, Any]) -> str:
    headers = _TD_HEADERS[(task["label_route"], task["task_type"])]
    lines = [
        f"  | {' | '.join(headers)} |",
        "  |" + "|".join("---" for _ in headers) + "|",
    ]
    for row in task["td_rows"]:
        cells = []
        for i, cell in enumerate(row):
            val = _clean_token(cell)
            if i == 0 and val:
                val = f"`{val}`"
            cells.append(val)
        lines.append(f"  | {' | '.join(cells)} |")
    return "\n".join(lines)


def _serialize_task(task: dict[str, Any], number: int) -> str:
    evidence_lines = task["evidence"] or []
    evidence_block = "\n".join(f"  {line}" if not line.startswith("  ") else line for line in evidence_lines)
    notes = task["notes"] or ""
    notes_line = f"- **Notes**: {notes}" if notes else "- **Notes**:"
    return (
        f"### {task['kind']} Task {number}: {task['title']}\n"
        f"- **Task Type**: {task['task_type']}\n"
        f"- **Epoch Method**: `{task['epoch_method']}`\n"
        f"- **Epoch Parameters**: {_serialize_epoch_params(task)}\n"
        f"- **Label Route**: `{task['label_route']}`\n"
        f"- **Meta Level**: {task['meta_level']}\n"
        f"- **Target Definition**:\n{_serialize_target_def(task)}\n"
        f"- **Evidence**:\n{evidence_block if evidence_block else '  - none'}\n"
        f"{notes_line}"
    )


def normalize_tasks_section(tasks_section: str, grounding: dict[str, list[str]]) -> str:
    tasks = []
    for block in _split_task_blocks(tasks_section):
        parsed = _parse_task_block(block)
        normalized = _normalize_task(parsed, grounding)
        if normalized is not None:
            tasks.append(normalized)
    classical = [t for t in tasks if t["kind"] == "Classical"]
    potential = [t for t in tasks if t["kind"] != "Classical"]
    parts = ["## Tasks\n"]
    for i, task in enumerate(classical, 1):
        parts.append(_serialize_task(task, i))
    for i, task in enumerate(potential, 1):
        parts.append(_serialize_task(task, i))
    if len(parts) == 1:
        parts.append("(No tasks could be grounded from current analysis.md and references.)")
    return "\n\n".join(parts).rstrip() + "\n"


def _parse_task_summaries(tasks_section: str) -> list[dict[str, Any]]:
    out = []
    for block in _split_task_blocks(tasks_section):
        parsed = _parse_task_block(block)
        out.append(
            {
                "title": parsed["title"],
                "route": parsed["label_route"],
                "label_field": parsed["label_field"],
                "epoch_method": parsed["epoch_method"],
                "target_events": _parse_target_events(parsed["epoch_pairs"].get("target_events", "")),
                "target_def_first_col": [_clean_token(row[0]) for row in parsed["td_rows"] if row and _clean_token(row[0])],
            }
        )
    return out


def _grounding_errors(tasks_section: str, grounding: dict[str, list[str]]) -> list[str]:
    event_ids = set(grounding["analysis_event_ids"])
    misc_fields = set(grounding["analysis_misc_fields"])
    info_fields = set(grounding["analysis_info_fields"])
    errors: list[str] = []
    for task in _parse_task_summaries(tasks_section):
        title = task["title"]
        route = task["route"]
        field = _clean_token(task["label_field"])
        target_events = task["target_events"]
        td_first_col = task["target_def_first_col"]
        if route == "event":
            bad_te = [e for e in target_events if e not in event_ids]
            bad_td = [e for e in td_first_col if e not in event_ids]
            if bad_te:
                errors.append(f"{title}: target_events not grounded in current Event Structure: {bad_te}")
            if bad_td:
                errors.append(f"{title}: Target Definition Event IDs not grounded: {bad_td}")
        elif route == "misc":
            source = field or (td_first_col[0] if td_first_col else "")
            if source and source not in misc_fields:
                errors.append(f"{title}: misc source '{source}' is not in current MISC grounding.")
        elif route == "info":
            source = field or (td_first_col[0] if td_first_col else "")
            if source and source not in info_fields:
                errors.append(f"{title}: info source '{source}' is not in current Info grounding.")
    return errors


def _generate_once(
    dataset_name: str,
    analysis_md: str,
    grounding: dict[str, list[str]],
    extractions: list[dict[str, Any]],
    skill_text: str,
    call_llm: Callable[[list[dict[str, str]], int], str],
) -> tuple[str, str]:
    user_msg = _build_generation_user_msg(dataset_name, analysis_md, grounding, extractions, skill_text)
    raw = call_llm(
        [
            {"role": "system", "content": _GEN_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        timeout=300,
    )
    parsed, err = _parse_llm_json(raw)
    if parsed is None:
        raise ValueError(err or "Generation JSON parse failed.")
    tasks_section = str(parsed.get("tasks_section", "")).strip()
    summary = str(parsed.get("summary", "")).strip()
    if not tasks_section.startswith("## Tasks"):
        raise ValueError("Generation returned tasks_section without a top-level ## Tasks heading.")
    return tasks_section, summary


def _repair_once(
    dataset_name: str,
    analysis_md: str,
    grounding: dict[str, list[str]],
    tasks_section: str,
    errors: list[str],
    call_llm: Callable[[list[dict[str, str]], int], str],
) -> str:
    user_msg = _build_repair_user_msg(dataset_name, analysis_md, grounding, tasks_section, errors)
    raw = call_llm(
        [
            {"role": "system", "content": _REPAIR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        timeout=240,
    )
    parsed, err = _parse_llm_json(raw)
    if parsed is None:
        raise ValueError(err or "Repair JSON parse failed.")
    return str(parsed.get("tasks_section", "")).strip()


def generate_tasks_phase2_strict(
    dataset_name: str,
    extractions: list[dict[str, Any]],
    analysis_md: str,
    skill_text: str,
    llm_config_path: Path,
) -> dict[str, Any]:
    grounding = extract_analysis_grounding(analysis_md)
    llm_config = _load_llm_config(llm_config_path)
    call_llm = _call_llm_factory(llm_config)

    if not any(grounding.values()):
        return {
            "ok": False,
            "tasks_section": "",
            "summary": "",
            "semantic_errors": [],
            "hard_fail_reason": "Current analysis.md has no Event Structure / MISC / Info grounding to support task regeneration.",
            "grounding_summary": {
                "event_whitelist": [],
                "misc_whitelist": [],
                "info_whitelist": [],
                "reference_stats": {"input_extractions": len(extractions), "useful_extractions": 0},
            },
            "generation_mode": "doc_only_rulebook_v1_0_strict",
        }

    useful = [e for e in extractions if e.get("classification") in {"relevant", "partial"}]
    tasks_section, summary = _generate_once(
        dataset_name=dataset_name,
        analysis_md=analysis_md,
        grounding=grounding,
        extractions=extractions,
        skill_text=skill_text,
        call_llm=call_llm,
    )
    normalized = normalize_tasks_section(tasks_section, grounding)
    violations = _run_task_semantic_checks(normalized, dataset_name, analysis_md)
    grounding_errors = _grounding_errors(normalized, grounding)
    errors = format_semantic_errors(violations) + grounding_errors

    if errors:
        repaired = _repair_once(
            dataset_name=dataset_name,
            analysis_md=analysis_md,
            grounding=grounding,
            tasks_section=normalized,
            errors=errors,
            call_llm=call_llm,
        )
        normalized = normalize_tasks_section(repaired, grounding)
        violations = _run_task_semantic_checks(normalized, dataset_name, analysis_md)
        grounding_errors = _grounding_errors(normalized, grounding)
        errors = format_semantic_errors(violations) + grounding_errors

    return {
        "ok": not errors,
        "tasks_section": normalized,
        "summary": summary or "Doc-only strict regeneration finished.",
        "semantic_errors": errors,
        "hard_fail_reason": "" if not errors else "Generated tasks failed doc-only strict grounding or rule checks.",
        "grounding_summary": {
            "event_whitelist": grounding["analysis_event_ids"],
            "misc_whitelist": grounding["analysis_misc_fields"],
            "info_whitelist": grounding["analysis_info_fields"],
            "reference_stats": {
                "input_extractions": len(extractions),
                "useful_extractions": len(useful),
            },
        },
        "generation_mode": "doc_only_rulebook_v1_0_strict",
    }
