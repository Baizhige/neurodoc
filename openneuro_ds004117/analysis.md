# Sternberg Working Memory

**Dataset**: `openneuro_ds004117` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004117
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 85
**Channels**: 71 | **Sampling Rate**: 250 Hz

## Paradigm

A modified Sternberg working memory task in which participants selectively memorized sets of 3, 5, or 7 target letters (marked with lowercase 'g' prefix, e.g., gH) while ignoring identical-font distractor letters. After a retention period, a probe letter was presented and participants indicated with auditory feedback whether it was in the memorized set. The study investigates frontal midline EEG dynamics (particularly theta oscillations) during working memory maintenance.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `WM` | 85 files | event | raw | Working memory trial onset / encoding phase |
| `nonWM` | 85 files | event | raw | Non-working-memory (distractor) trial |
| `gA`-`gZ` (prefixed letters) | 85 files | event | raw | Working memory target letter onset (to be memorized) |
| `A`-`Z` (plain letters) | 85 files | event | raw | Distractor letter onset (to be ignored) |
| `255` | 85 files | admin | raw | System trigger (likely BrainVision marker 255 = all bits) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Working Memory Encoding - Memorize vs Ignore Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`WM`, `nonWM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `WM` | 1 | Working memory encoding trial (Memorize letters) |
  | `nonWM` | 0 | Non-working-memory distractor trial (Ignore letters) |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2005.04.014` — Frontal midline theta dynamics analysis during modified Sternberg working memory task, classifying Memorize vs Ignore letter trials with memory load manipulation (3, 5, 7 letters), using 3-s epochs (tmin=-1.0s, tmax=2.0s) relative to letter onset.
- **Kernel Notes**: Extract epochs around WM and nonWM event markers. Exclude event ID `255` (admin/system marker). Optionally analyze memory load (3, 5, 7 letters) as secondary analysis by examining preceding WM trial context. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Memory Load Classification (3, 5, 7 items)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`WM`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `WM` (load=3) | 0 | Working memory encoding with 3 letters |
  | `WM` (load=5) | 1 | Working memory encoding with 5 letters |
  | `WM` (load=7) | 2 | Working memory encoding with 7 letters |
- **Super Meta Notes**: Derived from raw event `WM` by parsing trial metadata or preceding context indicating set size (3, 5, or 7 target letters). Kernel step: Load trial set-size information from events.tsv sidecar or task-related metadata fields to assign load-level labels.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2005.04.014` — Analyzed theta power changes with memory load (3, 5, 7 letters), showing increased frontal midline theta for higher memory loads.
- **Kernel Notes**: Requires access to trial-level metadata specifying the number of items in each WM trial. Verify set-size encoding in events.tsv or dataset documentation.

### Potential Task 1: WM vs Non-WM Letter Encoding (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `WM` | 1 | Working memory encoding trial |
  | `nonWM` | 0 | Non-working-memory (distractor) trial |
- **Notes**: 255 is an admin marker and must be excluded. Individual letter events (A-Z, gA-gZ) mark specific letter presentations and can be used for fine-grained analysis. 23 subjects x ~3.7 sessions on average = 85 files.

## Data Quality Notes

- Trigger 255 (all-bits-high) is a system artifact and must be excluded
- Individual letter events provide fine-grained trial structure for ERP analysis
- 23 subjects x multiple sessions - verify session structure before pooling


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review