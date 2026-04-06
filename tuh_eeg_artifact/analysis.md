# TUH EEG Artifact Corpus

**Dataset**: `tuh_eeg_artifact` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_artifact/v3.0.1/
**Category**: Others | **Subjects**: ~310 | **Files (Completed)**: 310 | **Channels**: 27-128 | **Sampling Rate**: 250-1000 Hz

## Paradigm

The TUH EEG Artifact Corpus (v3.0.1) provides time-stamped, channel-level artifact annotations on 310 clinical EEG recordings selected from the TUH EEG Corpus. Expert annotators labeled artifact segments with type and temporal boundaries, stored in companion CSV sidecar files. Each annotation includes: channel name, start time, stop time, label, and confidence score. Multiple artifact types may co-occur within a recording.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `eyem` | varies | event | raw | Eye movement artifact |
| `musc` | varies | event | raw | Muscle (EMG) artifact |
| `elec` | varies | event | raw | Electrode artifact (pop, movement) |
| `chew` | varies | event | raw | Chewing artifact |
| `shiv` | varies | event | raw | Shivering artifact |
| `elpp` | varies | event | raw | Electrode pop |
| `null` | varies | admin | raw | No artifact (clean segment) |

>
> Artifact annotations are channel-level and time-stamped. Multiple artifact types may appear in a single recording; combined labels (e.g., `musc_elec`, `eyem_musc`) are also present.


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Artifact Type Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.5, target_events = [`eyem`, `musc`, `elec`, `chew`, `shiv`, `elpp`, `null`, `eyem_musc`, `other_combined`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `null` | 0 | Clean EEG (no artifact) |
  | `eyem` | 1 | Eye movement artifact |
  | `musc` | 2 | Muscle (EMG) artifact |
  | `elec` | 3 | Electrode artifact |
  | `chew` | 4 | Chewing artifact |
  | `shiv` | 5 | Shivering artifact |
  | `elpp` | 6 | Electrode pop |
  | `eyem_musc` | 7 | Combined eye movement + muscle artifact |
  | `other_combined` | 8 | Other combined artifact types |
- **Evidence**:
  - DOI: `10.1038/s41598-024-52551-0` — Uses TUH EEG Artifact Corpus (TUAR) at 250 Hz with gradient boosted tree classifiers for artifact detection; achieves 93.95% accuracy with Binary Classification (BC), Multilabel Classification (MC), and Multiclass-Multioutput Classification (MMC) approaches on 1-second windows
  - DOI: `10.1109/embc48229.2022.9871413` — Uses TUAR with three classification approaches (binary, multi-label, multi-output) on 1-second windows with FFT and DWT features
- **Kernel Notes**: Segment raw EEG into 1-second windows with 50% overlap. Extract artifact label for each segment from CSV sidecar annotations (channel-level annotations aggregated to segment level). Handle combined labels (e.g., `eyem_musc`) by assigning to combined class or primary artifact type. Exclude combined artifacts if only single-label classification needed. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Binary Artifact Detection (Artifact vs. Clean)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.5, target_events = [`eyem`, `musc`, `elec`, `chew`, `shiv`, `elpp`, `null`, `combined_artifacts`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `null` | 0 | Clean EEG segment |
  | `eyem` | 1 | Any artifact present |
  | `musc` | 1 | Any artifact present |
  | `elec` | 1 | Any artifact present |
  | `chew` | 1 | Any artifact present |
  | `shiv` | 1 | Any artifact present |
  | `elpp` | 1 | Any artifact present |
  | `combined_artifacts` | 1 | Any combined artifact |
- **Evidence**:
  - DOI: `10.1038/s41598-024-52551-0` — Achieves 93.95% accuracy for Binary Classification (BC) where artifact→1 and null→0
  - DOI: `10.1109/embc48229.2022.9871413` — Achieves 93.95% accuracy for binary classification on 4 temporal channels using 1-second windows
- **Kernel Notes**: Segment raw EEG into 1-second windows with 50% overlap. For each segment, check if any artifact annotation exists (from CSV sidecar). Collapse all artifact types to y=1, null to y=0. Handle multi-channel recordings by aggregating per-segment (e.g., any-channel-has-artifact or majority-vote).

### Potential Task 1: Artifact Type Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `null` segments. Combined labels (e.g., `musc_elec`) require a decision: either assign to the primary artifact type or treat as a separate class. CSV sidecars must be present alongside EDF files.

| Event | y | Meaning |
|-------|---|---------|
| `eyem` | 0 | Eye movement |
| `musc` | 1 | Muscle (EMG) |
| `elec` | 2 | Electrode artifact |
| `chew` | 3 | Chewing |
| `shiv` | 4 | Shivering |
| `elpp` | 5 | Electrode pop |


### Potential Task 2: Artifact vs. Clean EEG Detection (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `null` | 0 | Clean EEG segment |
| `eyem` | 1 | Any artifact |
| `musc` | 1 | Any artifact |
| `elec` | 1 | Any artifact |
| `chew` | 1 | Any artifact |

## Data Quality Notes

- Annotations are at the channel level; aggregate to recording level or use channel-specific labels depending on the task.
- Combined label types (e.g., `eyem_musc`) create label ambiguity; standardize before training.
- Variable channel count and sampling rate; normalize before cross-recording analysis.
- Sex is not reliably available.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review