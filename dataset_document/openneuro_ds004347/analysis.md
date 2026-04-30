# Symmetry perception and affective responses: a combined EEG/EMG study

**Dataset**: `openneuro_ds004347` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004347
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24 | **Channels**: 73 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants performed a visual perception task identifying whether stimuli were regular (symmetric/reflectional) or random (asymmetric) patterns to investigate symmetry perception and affective responses. EEG and EMG were simultaneously recorded to capture both neural and facial muscle activity. The dataset contains trial-level event markers aligned to stimulus onset for epoch-based analysis.

## File Scan Result

> **Kernel SHA256**: `a60563dd79622904c3d1cc7955e44f868f37d925b51d097be2cb64bb2b805f9b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 1920 | event | raw | Regular condition onset |
| `event_3` | 1919 | event | raw | Random condition onset |
| `event_65536` | 5 | admin | raw | Unknown system marker (not observed in sampled events.tsv files) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Symmetry vs Random pattern classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_1`, `event_3`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_3` | 0 | Random condition onset (asymmetric pattern) |
  | `event_1` | 1 | Regular condition onset (symmetric/reflectional pattern) |
- **Evidence**:
  - 10.1016/j.neuropsychologia.2012.10.003 — Two-class classification of Regular (symmetric/reflectional) vs Random (asymmetric) visual patterns. 3839 total trials across 24 participants (~160 trials/condition/subject). ERP components N1/P1 and SPN (sustained posterior negativity) are established markers for symmetry perception in this paradigm.
- **Notes**: Event mappings confirmed by multiple subjects' events.json files (sub-001, sub-002, sub-010, sub-020, sub-023): TriggerValue levels define x1='Regular' and x3='Random', corresponding to value=1 and value=3 in events.tsv. Stimulus-locked epochs from -0.2s to 1.0s capture baseline correction window (-0.2, 0.0) and ERP components (N1/P1 at ~100-150ms, SPN at ~200-1000ms) known to differentiate symmetry perception.

## Data Quality Notes

- Multiple metadata fields are missing: `subject_age`, `subject_sex`, `device`, `species`, and `handedness`.
- `subject_sex` was marked as complete in the prior draft but is now missing; this discrepancy should be noted for manual review.
- The `event_65536` system marker is listed in the event structure but was not observed in sampled events.tsv files, suggesting possible file-level variability or rare occurrence.
- EMG/EOG channels are included in the 73-channel montage and should be excluded from EEG-only analyses.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
