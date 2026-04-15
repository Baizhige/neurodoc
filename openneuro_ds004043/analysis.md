# The time-course of feature-based attention effects dissociated from temporal expectation and target-related processes

**Dataset**: `openneuro_ds004043` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004043
**Category**: Sensory/Response | **Subjects**: 20 | **Files (Completed)**: 40 | **Channels**: 63 | **Sampling Rate**: 250 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed rapid sequences of overlaid oriented grating pairs (presented at ~10 Hz) and detected a target orientation while attention was cued to different feature dimensions (orientation or color). The study dissociates the time-course of feature-based attention effects from temporal expectation and target-detection processes using EEG frequency-tagging and ERP methods.

## File Scan Result

> **Kernel SHA256**: `9c6350948ce4f7fc03b5de643ba7c01183b6cc6ee58e993b611ad7f32d362fb8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 174080 | event | raw | Grating stimulus onset - condition 1 (attended feature dimension) |
| `E  2` | 174080 | event | raw | Grating stimulus onset - condition 2 (non-attended feature dimension) |
| `E  3` | 1280 | event | raw | Grating stimulus onset - condition 3 (target/distractor trials) |
| `Event/E  1` | 174080 | event | raw | Duplicated event marker (EEGLAB-style prefix variant) |
| `Event/E  2` | 174080 | event | raw | Duplicated event marker (EEGLAB-style prefix variant) |
| `Event/E  3` | 1280 | event | raw | Duplicated event marker (EEGLAB-style prefix variant) |
| `boundary` | 20 | event | raw | Recording segment boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Cued vs Uncued Orientation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, baseline = (None, 0), target_events = [`E 1`, `E 2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `E 1` | 0 | Cued/attended orientation (target feature dimension) |
  | `E 2` | 1 | Uncued/ignored orientation (non-attended feature dimension) |
- **Evidence**:
  - DOI: 10.1038/s41598-022-10687-x — MVPA with LDA classifiers decoded cued vs uncued orientation from EEG epochs (-100 to 800ms) in non-target trials; attention effect emerged ~230ms after stimulus onset
  - DOI: 10.1101/2021.05.24.445376 — Multivariate pattern analysis decoded cued vs uncued orientation coding over time from -100ms to 800ms post-stimulus; controlled for temporal expectation as independent variable
- **Kernel Notes**: Filter epochs to include only non-target trials (exclude `E 3` marker trials which are targets/foils occurring ~100x less frequently). The analysis focuses on non-target stimuli to isolate pure attention effects from target-detection confounds. Verify event ID mapping from events.tsv — E 1 and E 2 must be confirmed as cued and uncued condition markers respectively. High event counts (~174K per condition per file) result in large epoch sets; consider compute-efficient MVPA pipelines.

### Potential Task 1: Multiclass Attention Condition Decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, baseline = (None, 0), target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `E 1` | 0 | Attention condition 1 (grating stimulus onset) |
  | `E 2` | 1 | Attention condition 2 (grating stimulus onset) |
  | `E 3` | 2 | Target/distractor stimulus onset |
- **Evidence**:
  - DOI: 10.1038/s41598-022-10687-x (partial) — The study design included three stimulus conditions presented in a rapid 10Hz stream; multiclass decoding of all conditions is theoretically feasible but not explicitly reported in the published MVPA analysis which focused on binary cued vs uncued comparison
- **Kernel Notes**: Standard epoching will yield highly imbalanced class sizes (E 3 ~1.3K vs E 1/E 2 ~174K each). Stratified sampling or class weighting required. Confirm event-to-condition mapping from events.tsv — E 1/E 2/E 3 semantics may vary across subjects or sessions. Boundary events (n=20) likely mark recording segment breaks; handle appropriately during epoching.
