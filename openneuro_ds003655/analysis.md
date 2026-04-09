# VerbalWorkingMemory

**Dataset**: `openneuro_ds003655` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003655
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 156
**Channels**: 21 | **Sampling Rate**: 500 Hz

## Paradigm

A modified Sternberg working memory task requiring either simple retention or mental manipulation (alphabetization) of letter sequences at three load levels (5, 6, or 7 letters). Participants encoded a letter sequence, maintained it across a delay period, then responded to a probe letter. The mental manipulation condition (alphabetization) places additional executive demands on working memory compared to simple retention. EEG measures during encoding, delay, and probe phases capture load-dependent neural activity.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `encoding` | 936 | event | raw | Letter sequence encoding phase onset |
| `delay period` | 936 | event | raw | Working memory retention/manipulation delay period |
| `probe` | 936 | event | raw | Probe letter presentation |
| `start of the baseline period` | 936 | event | raw | Baseline period onset (pre-trial) |
| `start of the trial` | 156 | event | raw | Trial start marker |
| `presentation of the task instruction` | 156 | event | raw | Task instruction display onset |
| `Response` | 1807 | event | raw | Participant button-press response |
| `STATUS` | 156 | admin | raw | System status marker |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Verbal Working Memory - Retention vs Manipulation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -14.2 s, tmax = 2.2 s, target_events = [`probe`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-------|
  | `probe` (condition: R) | 0 | Retention (simple maintenance) condition |
  | `probe` (condition: M) | 1 | Manipulation (alphabetization) condition |
- **Super Meta Notes**: Derived from raw event `probe` by extracting condition subtype from trial metadata (R=Retention, M=Manipulation). Kernel step: Parse trial condition from events.tsv trial_type column, extract 'R' or 'M' suffix to produce binary label.
- **Evidence**:
  - DOI: 10.1111/ejn.15457 — Shows oscillatory theta/alpha/beta differences between retention and manipulation conditions during encoding and delay phases of verbal working memory with 5/6/7 letter load
- **Kernel Notes**: Epochs extracted relative to probe onset (-14.2 to 2.2 s). Baseline period is -11.5 to -10.5 s. Load level (5/6/7) available as additional factor in trial_type column for ordinal regression if needed. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Delay Period Working Memory State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 6.0 s, overlap = 0.5, target_events = [`delay period`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-------|
  | `delay period` (R condition) | 0 | Retention condition during delay |
  | `delay period` (M condition) | 1 | Manipulation condition during delay |
- **Super Meta Notes**: Derived from raw event `delay period` by extracting condition subtype. Kernel step: Parse trial_type column to identify 'R' (retention) vs 'M' (manipulation) suffix.
- **Evidence**:
  - DOI: 10.1111/ejn.15457 — Examines oscillatory activity differences during delay period (Delay1: -6000 to -3000 ms; Delay2: -3000 to 0 ms) between retention and manipulation
- **Kernel Notes**: Delay period typically >=6s at load levels 5/6/7. Use sliding window (0.5 overlap) to capture sustained activity. Load level can be extracted as additional covariate.

### Potential Task 1: Detect stimulus ERP (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Probe events are short (<1 s); suitable for ERP epoching. Match/non-match accuracy from Response events can be used as trial-level correctness labels.

| Event | y | Meaning |
|-------|---|-------|
| `probe: 5R` / `6R` / `7R` | 0 | Keep condition detection |
| `probe: 5M` / `6M` / `7M` | 1 | Operating condition detection |

### Potential Task 2: Encoding Phase ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`encoding`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-------|
  | `encoding` (R condition) | 0 | Encoding phase for retention |
  | `encoding` (M condition) | 1 | Encoding phase for manipulation |
- **Notes**: Epochs around encoding onset capture initial letter sequence processing. Condition labels derived from trial_type metadata.
- **Evidence**:
  - DOI: 10.1111/ejn.15457 — Examines oscillatory differences between conditions during encoding phase

## Data Quality Notes

- 21-channel EEG; limited spatial resolution but sufficient for frontal working memory analyses.
- Event subtypes encoded in trial_type column (e.g., "delay period: 5M"); parse carefully.
- Multiple sessions per subject (156 files / ~26 subjects ~ 6 files each).


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review