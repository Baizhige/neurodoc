# Reading Guide for a Single Dataset Description

## Who This Is For
Use this guide when reading one dataset file such as:

- `openneuro_ds005383/analysis.md`

Goal:

- Quickly understand what the dataset contains
- Decide whether it is suitable for your task
- Avoid common misinterpretations

## Suggested Reading Order
Read sections in this order:

1. `Dataset` line (ID, year, URL, subjects, channels, sampling rate)
2. `Paradigm`
3. `Event Structure`
4. `HDF5 Production Guide` (or equivalent epoching guidance)
5. `Task 1/Task 2 ...`
6. `Data Quality Notes`
7. `References`

This order gives context first, then label mechanics, then practical modeling constraints.

## How To Interpret Each Section

## 1) Dataset Snapshot
Focus on:

- Number of subjects/files: impacts sample size and variance
- Channels and sampling rate: affects feature design and filtering strategy
- Category: high-level task family (cognitive, sensory-response, biological state, etc.)

## 2) Paradigm
This section answers:

- What participants did
- What stimuli/conditions exist
- Which cognitive or physiological process is targeted

If paradigm text is broad, cross-check with `Event Structure` for concrete labels.

## 3) Event Structure
Treat this as label inventory.

- `short`: trial-like markers (usually for event-locked epochs)
- `long`: sustained-state markers
- `rest`: resting-state blocks
- `admin`: boundary/system markers; usually excluded from targets

Important:

- Event count may be per file, not per total trial.
- Some numeric codes need decoding via `events.tsv` or dataset docs.

## 4) HDF5 / Epoching Guidance
This section is operational:

- Label source (annotation, participants.tsv, external metadata)
- Kernel type (generic vs dataset-specific)
- Recommended epoch method
- Segment window (`tmin`, `tmax`, overlap)
- Target mapping (`event -> y`)

If target mapping is `null`, the dataset may be:

- segmentation-only
- unsupervised
- requires external labels

## 5) Task Sections
Use task sections to identify direct ML usage:

- classification (`binary`, `multiclass`)
- regression
- long-event segmentation

For each task, verify:

1. Is the label source explicit?
2. Is class balance acceptable?
3. Are epochs compatible with event type?

## 6) Data Quality Notes
Read this before modeling.

Typical blockers:

- sparse target events
- heavy class imbalance
- missing trial markers
- channel inconsistency across subjects
- very high sampling rate (requires downsampling planning)

## Practical Decision Checklist
Before using a dataset, answer:

1. Can I construct labels without manual decoding?
2. Is event density enough for my task?
3. Is the windowing strategy clear and reproducible?
4. Do quality notes introduce major risk?
5. Are references sufficient for ambiguity resolution?

## Common Pitfalls

1. Treating `admin` markers as target labels
2. Ignoring whether counts are per file vs per trial
3. Assuming numeric triggers are self-explanatory
4. Skipping `Data Quality Notes` and over-trusting raw event tables
5. Using dataset-level metadata as trial-level labels without justification

## Fast Workflow (3-Minute Scan)

1. Read metadata line and paradigm
2. Read event table and mark usable target labels
3. Read epoching guidance and task mapping
4. Read quality notes and decide:
   - `usable now`
   - `usable with extra decoding`
   - `not suitable for current objective`
