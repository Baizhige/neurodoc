# README Template & Authoring Guide

## Purpose
This file defines how to generate a clean, consistent `README.md` for a single dataset folder such as:

- `openneuro_ds005383/analysis.md`

It is intended for both:

- AI assistants
- Human contributors

## Input Files
Use the following as the source of truth:

1. `openneuro_dsXXXXXX/analysis.md` (required)
2. Dataset metadata from the same file (dataset id, URL, year, category, subjects, channels, sampling rate)

Do not invent details that are not explicitly supported by source text.

## Output Target
Create:

- `openneuro_dsXXXXXX/README.md`

## Writing Rules
Use these rules strictly:

1. Write in English only.
2. Keep technical content concise and factual.
3. Preserve dataset-specific event names exactly (for example: `S 4`, `FB: +1`, `OVTK_GDF_Right`).
4. If uncertainty exists, state it explicitly with wording like: `Needs verification from events.tsv/README`.
5. Do not add claims about performance, diagnosis, or outcomes unless present in the source.
6. Prefer short paragraphs, bullet lists, and tables for readability.

## Recommended README Structure
Use this section order:

1. Title
2. Dataset Snapshot
3. Paradigm Summary
4. Event Structure
5. HDF5/Epoching Guidance
6. Suggested Tasks
7. Data Quality Notes
8. References

## README Template
Copy and fill this template:

```md
# <Dataset Title>

## Dataset Snapshot

| Field | Value |
|---|---|
| Dataset ID | `<openneuro_dsXXXXXX>` |
| URL | `<https://openneuro.org/datasets/...>` |
| Year | `<YYYY or N/A>` |
| Category | `<Category>` |
| Subjects | `<N or N/A>` |
| Files (Completed) | `<N or N/A>` |
| Channels | `<N or N/A>` |
| Sampling Rate | `<Hz or N/A>` |

## Paradigm Summary

<2-5 sentences describing what participants did and what was measured.>

## Event Structure

| Event ID | Type | Meaning | Notes |
|---|---|---|---|
| `<event>` | `<short/long/rest/admin>` | `<meaning>` | `<optional>` |

## HDF5 / Epoching Guidance

- Label source: `<Annotation / participants.tsv / none>`
- Kernel: `<Generic BIDS / Specific kernel path>`
- Recommended epoch method: `<epoch_by_event_hdf5 / epoch_by_long_event_hdf5 / epoch_by_segmentation_hdf5>`
- Segment: `<tmin/tmax or segment length + overlap>`
- Target mapping:

| Event | y | Meaning |
|---|---|---|
| `<event>` | `<index>` | `<label meaning>` |

## Suggested Tasks

- Task 1: `<name>` (`<binary/multiclass/regression>`)
- Optional Task 2: `<name>`

## Data Quality Notes

- `<artifact risks / class imbalance / sparse events / marker decode caveat>`
- `<channel/system caveats>`

## References

- `<paper title / DOI / dataset citation>`
```

## AI Prompt Template
Use this prompt when asking an AI to generate a single-dataset README:

```txt
You are generating README.md for one dataset folder in this repository.

Input:
- Source file: openneuro_dsXXXXXX/analysis.md

Requirements:
1. English only.
2. Do not hallucinate. If missing, write "N/A" or "Needs verification".
3. Preserve exact event codes and labels.
4. Use this structure:
   - Title
   - Dataset Snapshot (table)
   - Paradigm Summary
   - Event Structure (table)
   - HDF5 / Epoching Guidance
   - Suggested Tasks
   - Data Quality Notes
   - References
5. Keep style concise and technical.

Output:
- Markdown only, ready to save as openneuro_dsXXXXXX/README.md
```

## Quality Checklist
Before finalizing, check:

1. Any non-English text remaining?
2. Any invented or unsupported claims?
3. Do event labels match source exactly?
4. Is target mapping explicit and reproducible?
5. Are limitations and caveats clearly stated?
