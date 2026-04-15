# EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task

**Dataset**: `openneuro_ds003838` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003838/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 86 | **Files (Completed)**: 296 | **Channels**: 2 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a classic digit span working memory task involving serial recall of digit sequences of 5, 9, or 13 digits, along with a separate eyes-closed resting state condition. Each digit in a sequence was marked with an event indicating the digit position, sequence length, and whether it was later correctly recalled or forgotten. The dataset also includes ECG/PPG physiological signals recorded simultaneously with EEG.

## File Scan Result

> **Kernel SHA256**: `8760ef8f59d8096d402af858f6761db44f0c40a100ac54cfb32e524b4136db46`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `[98]` | 8 | event | raw | Experimental event marker |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `PPG`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Correct vs Error Memory Encoding (binary classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`memory X/05 correct`, `memory X/09 correct`, `memory X/13 correct`, `memory X/05 error`, `memory X/09 error`, `memory X/13 error`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `memory X/05 correct` | 0 | Digit correctly recalled later (5-item sequence) |
  | `memory X/09 correct` | 0 | Digit correctly recalled later (9-item sequence) |
  | `memory X/13 correct` | 0 | Digit correctly recalled later (13-item sequence) |
  | `memory X/05 error` | 1 | Digit forgotten later (5-item sequence) |
  | `memory X/09 error` | 1 | Digit forgotten later (9-item sequence) |
  | `memory X/13 error` | 1 | Digit forgotten later (13-item sequence) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01414-2 — Data descriptor for this dataset explicitly defines event codes marking each digit with sequence length and recall outcome (partial support: correlational analysis, not ML classification).
  - DOI: 10.1111/psyp.14275 — Analyzes EEG/pupillometric correlates of correct vs error recall across load levels; epoched data from −1500 to 3500 ms (partial support: correlational analysis).
- **Kernel Notes**: Aggregate all correct events (regardless of digit position X) as class 0, all error events as class 1. Exclude `STATUS` (admin marker). Event IDs contain placeholder 'X' for digit position; kernel should match patterns `memory .*/correct` and `memory .*/error` to capture all positions and sequence lengths.

### Potential Task 2: Working Memory Load Classification (multi-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.5 s, target_events = [`memory X/05 correct`, `memory X/09 correct`, `memory X/13 correct`, `memory X/05 error`, `memory X/09 error`, `memory X/13 error`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `memory X/05 correct` | 0 | Low load (5 digits) correctly recalled |
  | `memory X/05 error` | 0 | Low load (5 digits) forgotten |
  | `memory X/09 correct` | 1 | Medium load (9 digits) correctly recalled |
  | `memory X/09 error` | 1 | Medium load (9 digits) forgotten |
  | `memory X/13 correct` | 2 | High load (13 digits) correctly recalled |
  | `memory X/13 error` | 2 | High load (13 digits) forgotten |
- **Evidence**:
  - DOI: 10.1111/psyp.14275 — Examines working memory overload effects by analyzing EEG/pupillometric responses across digit sequences of 5, 9, and 13 items (partial support: correlational analysis of load effects, not ML classification).
  - DOI: 10.1038/s41598-023-48917-5 — Analyzes task-evoked pupillary responses as correlates of cognitive load across sequence lengths (partial support: correlational analysis).
- **Kernel Notes**: Class labels represent cognitive load level (5=class 0, 9=class 1, 13=class 2), ignoring recall outcome for load classification. The longer epoch window (-1.5 to 3.5s) aligns with published methodology examining the full cognitive processing window. Event IDs use placeholder 'X' for digit position; kernel should match patterns to capture all positions within each sequence length.