# analysis.md Template & Principles (EEGDataset Benchmark)

## Purpose
This guide defines a unified `analysis.md` standard for EEG datasets so that:

1. kernels can be generated directly from documentation;
2. HDF5 export pipelines can be configured directly from documentation;
3. raw-meta and super-meta logic is explicit and reproducible.

---

## Core Concepts

### Raw Meta
Direct labels or markers that already exist in source data, for example:

- `events.tsv` annotation labels
- trigger/stim channel markers
- admin/system markers (`boundary`, `9999`, etc.)

### Super Meta
Derived labels that are not directly present as raw event IDs and must be created by kernel logic, for example:

- `response_time`
- `confidence`
- subject-level factors (`p_factor`, `externalizing_factor`)
- merged clinical/behavioral outcomes

---

## Kernel Responsibilities (Three Types)

Every dataset must explicitly choose one or more responsibility types:

1. **Type 1: Raw-meta extraction only**
   - Kernel extracts and normalizes raw labels.
   - Dataset scientific intent is consistent with raw labels.

2. **Type 2: Raw + Super meta integration**
   - Kernel extracts raw labels and derives/joins super-meta targets.
   - Dataset scientific intent is not fully represented by raw labels alone.

3. **Type 3: Label-route orchestration**
   - Kernel maps final labels into EEGUnity routes:
     - `Annotation`
     - `stim`
     - `misc`
   - Kernel ensures export-time consistency and provenance.

---

## Required Section Order

Every `analysis.md` should follow this order:

1. `# <Dataset Title>`
2. Metadata header lines:
   - `**Dataset**`, `**Year**`, `**URL`
   - `**Category**`, `**Subjects**`, `**Files (Completed)**`
   - `**Channels**`, `**Sampling Rate**`
3. `## Paradigm`
4. `## Kernel Responsibilities`
5. `## Event Structure`
6. `## MISC Label Summary` (optional)
7. `## STIM Label Summary` (optional)
8. `## Tasks`
9. `## Data Quality Notes`
10. `## References`

`## HDF5 Production Guide` is deprecated in this version. Use `## Tasks` only.

---

## Event Structure Requirements

`Event Structure` must include a `Meta Level` column:

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `...`    | ...           | ...  | raw/super  | ...     |

Rules:

- Raw event markers should be labeled `raw`.
- If an event-like label is derived by kernel, mark as `super`.
- Admin markers must remain explicit and should not be default learning targets.

---

## MISC / STIM Optional Sections

Add these sections when relevant.

### `## MISC Label Summary` (optional)
Use this section when labels are in `misc` route.

Should include:

- label names (for example `response_time`, `p_factor`)
- derivation source (tables/files)
- unit/transform (if applicable)

### `## STIM Label Summary` (optional)
Use this section when labels are derived from trigger/stim channels.

Should include:

- trigger source
- decoding/mapping rule
- whether labels are raw or transformed

---

## Task Writing Rules

Only task descriptions should define export behavior.

Do not include a `Primary Task Summary` subsection in `analysis.md`. Status tracking belongs in audit CSV files only.

Use task headings in either form:

- `### Primary Task N: ...`
- `### Normal Task N: ...`

For each task, include fields in this order:

- **Task type**: classification / regression / segmentation
- **Epoch Method**:
  - `epoch_by_event_hdf5`
  - `epoch_by_long_event_hdf5`
  - `epoch_by_segmentation_hdf5`
- **Epoch Parameters**:
  - for `epoch_by_event_hdf5`: `tmin`, `tmax`, `target_events`
  - for `epoch_by_long_event_hdf5`: `tmin`, `tmax`, `overlap`, `target_events`
  - for `epoch_by_segmentation_hdf5`: `segment_length`, `overlap`
- **Label Route**: `Annotation`, `stim`, or `misc`
- **Target Definition**:
  - classification: event-to-label mapping (for example `left_hand -> 0`, `right_hand -> 1`)
  - regression: target variable name, source, and where it is stored (`misc`/`stim`/`Annotation`)
- **Evidence**:
  - required for `Primary Task`
  - must include at least one external source URL/DOI (paper DOI, dataset page, or competition page)
- **Kernel notes**: what must be implemented to reproduce targets

Primary vs Normal policy:

- **Primary Task**: only when task intent is confirmed by external evidence.
- **Normal Task**: derived/recommended task from raw/super meta when external confirmation is unavailable.

If a dataset has canonical benchmark tasks, include them explicitly as `Primary Task`.

---

## Category Taxonomy (Priority Order)

Assign exactly one category using highest-priority match:

1. `Complex Applied`
2. `High-level Mental`
3. `Action/Output`
4. `Sensory/Response`
5. `Biological State`
6. `Others`

---

## Quality Checklist

Before finalizing an `analysis.md`:

1. Does `Kernel Responsibilities` clearly state Type 1/2/3?
2. Does `Event Structure` include `Meta Level`?
3. Are optional `MISC/STIM` sections included when needed?
4. Is `HDF5 Production Guide` removed?
5. Are tasks sufficient for direct EEGUnity implementation?
6. Are admin markers explicitly handled?
7. Are all uncertain facts marked as `Needs verification`?

---

## Minimal Skeleton

```md
# <Dataset Title>

**Dataset**: `<dataset_id>` | **Year**: `<year>` | **URL**: `<url>`
**Category**: `<one of 6 categories>` | **Subjects**: `<n>` | **Files (Completed)**: `<n>`
**Channels**: `<n>` | **Sampling Rate**: `<hz>`

## Paradigm
<summary>

## Kernel Responsibilities
- **Type 1**: ...
- **Type 2**: ...
- **Type 3**: ...
> **Selected mode**: Type X
> **Why**: ...

## Event Structure
| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `...` | ... | ... | raw/super | ... |

## MISC Label Summary
- ...

## STIM Label Summary
- ...

## Tasks
### Primary Task 1: ...
- **Task Type**: ...
- **Epoch Method**: ...
- **Epoch Parameters**: ...
- **Label Route**: Annotation/stim/misc
- **Target Definition**: ...
- **Evidence**: ...
- **Kernel Notes**: ...

### Normal Task 1: ...
- **Task Type**: ...
- **Epoch Method**: ...
- **Epoch Parameters**: ...
- **Label Route**: Annotation/stim/misc
- **Target Definition**: ...
- **Kernel Notes**: ...

## Data Quality Notes
- ...

## References
- ...
```

---

## AI Prompt Template

```txt
Generate analysis.md for this EEG dataset.

Hard requirements:
1. Follow ANALYSIS_TEMPLATE_GUIDE.md section order exactly.
2. Add "Kernel Responsibilities" before "Event Structure".
3. Use the 3 responsibility types and select mode(s) explicitly.
4. In Event Structure, include "Meta Level" (raw/super).
5. Add optional MISC/STIM sections when needed.
6. Do not use "HDF5 Production Guide" section.
7. Use only "Tasks" section for export-ready ML configuration.
8. Do not add "Primary Task Summary" in markdown.
9. For each task, include task type, epoch method, epoch parameters, label route, target definition, and kernel notes.
10. Primary tasks must include external URL/DOI evidence; otherwise write as Normal Task.
11. If uncertain, write "Needs verification" instead of guessing.

Output:
- Markdown only.
```
