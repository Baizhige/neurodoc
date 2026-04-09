# EEG: Visual Working Memory + Cabergoline Challenge

**Dataset**: `openneuro_ds003519` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003519
**Category**: High-level Mental | **Subjects**: 27 | **Files (Completed)**: 54
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a visuospatial working memory task under a double-blind Cabergoline (dopamine D2/D3 agonist) drug challenge to investigate pharmacological modulation of working memory processing. The task involved memorizing spatial locations of stimuli followed by a probe stimulus requiring a match/non-match judgment. Distractor stimuli were presented during the retention interval. The study examines individual differences in working memory capacity and dopaminergic modulation.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stim Onset` | 162 | event | raw | Study stimulus onset (to-be-remembered) |
| `Question Mark Probe` | 108 | event | raw | Probe stimulus requiring match judgment |
| `Response` | 108 | event | raw | Participant button-press response |
| `STATUS` | 54 | admin | raw | System status marker |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Dopamine (Cabergoline) vs Placebo Session Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60 s *, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Placebo` | 0 | Placebo session control condition |
  | `Cabergoline` | 1 | Drug (Cabergoline) administration session |
- **Super Meta Notes**: Derived from session-level experimental design (drug vs placebo crossover) rather than raw EEG event markers. Kernel step: Read session type from participants.tsv/scans.tsv metadata and assign label 0 for placebo, 1 for drug. Must group epochs by session to avoid data leakage.
- **Evidence**:
  - DOI: 10.20944/preprints202106.0509.v2 — Uses 27 participants from OpenNeuro ds003519 to classify placebo vs drug (Cabergoline) sessions using EEG functional connectivity features
  - DOI: 10.3390/bdcc5030039 — Classifies drug vs placebo conditions using correlation matrix features from trial-based EEG data, achieving 71-93% accuracy
- **Kernel Notes**: Extract connectivity features (e.g., correlation matrices, coherence) from segmented EEG windows. Use session label as target. Apply cross-validation at subject level to avoid within-subject leakage in crossover design.

### Classical Task 2: Visual Working Memory ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Stim Onset`, `Question Mark Probe`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stim Onset` | 0 | Memory stimulus presentation (encoding phase) |
  | `Question Mark Probe` | 1 | Probe stimulus presentation (retrieval/decision phase) |
- **Evidence**:
  - DOI: 10.3758/s13415-018-0584-6 — Reference paper for the Visual Working Memory paradigm used in this dataset
- **Kernel Notes**: Epoch around stimulus onsets to capture ERP components. Stim Onset captures encoding-related activity; Question Mark Probe captures retrieval/decisional activity. Session (drug vs placebo) can be included as covariate.

### Potential Task 1: Stimulus presentation ERP (single class, can be used for feature extraction)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Study stimulus vs probe comparison captures encoding vs retrieval phases. Two sessions per subject (drug vs placebo); treat session as covariate.

| Event | y | Meaning |
|-------|---|---------|
| `Stim Onset` | 0 | Memory stimulus presentation |
| `Question Mark Probe` | 1 | Probe stimulus presentation |

## Data Quality Notes

- 54 files for 27 subjects; two sessions per subject (drug/placebo crossover design).
- Drug condition information should be in participants.tsv or scans.tsv.
- Limited event types; primary utility is ERP characterization of encoding and retrieval phases.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review