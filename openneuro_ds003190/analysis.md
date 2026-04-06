# Assessment of the visual stimuli properties in P300 paradigm

**Dataset**: `openneuro_ds003190` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003190
**Category**: Sensory/Response | **Subjects**: 19 | **Files (Completed)**: 384
**Channels**: 9 | **Sampling Rate**: 256 Hz

## Paradigm

A P300 ERP experiment evaluating the effects of stimulus count and visual presentation styles (standard flash vs. cartoon face) on EEG brain activity. The experiment used a P300-based BCI paradigm with target and non-target stimulus flashes. Codes 1-9 represent different stimulus conditions or counts; codes 100-203 range encode specific stimulus configurations. The dataset has 19 subjects with many runs (384 files total).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 382 (files) | event | raw | P300 stimulus condition 1 (non-target flashx) |
| `2` | 382 (files) | event | raw | P300 stimulus condition 2 (non-target flashx) |
| `3` | 382 (files) | event | raw | P300 stimulus condition 3 |
| `4` | 382 (files) | event | raw | P300 stimulus condition 4 |
| `200` | 382 (files) | event | raw | P300 stimulus configuration 200 |
| `201` | 382 (files) | event | raw | P300 stimulus configuration 201 |
| `202` | 382 (files) | event | raw | P300 stimulus configuration 202 |
| `203` | 382 (files) | event | raw | P300 stimulus configuration 203 |
| `101` | 363 (files) | event | raw | P300 target flash condition 101 |
| `102` | 354 (files) | event | raw | P300 target flash condition 102 |
| `103` | 368 (files) | event | raw | P300 target flash condition 103 |
| `104` | 370 (files) | event | raw | P300 target flash condition 104 |
| `5` | 326 (files) | event | raw | P300 stimulus condition 5 |
| `105` | 305 (files) | event | raw | P300 target flash condition 105 |
| `6` | 224 (files) | event | raw | P300 stimulus condition 6 |
| `106` | 212 (files) | event | raw | P300 target flash condition 106 |
| `7` | 169 (files) | event | raw | P300 stimulus condition 7 |
| `107` | 161 (files) | event | raw | P300 target flash condition 107 |
| `8` | 112 (files) | event | raw | P300 stimulus condition 8 |
| `108` | 110 (files) | event | raw | P300 target flash condition 108 |
| `9` | 56 (files) | event | raw | P300 stimulus condition 9 |
| `109` | 47 (files) | event | raw | P300 target flash condition 109 |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: P300 Target vs Non-Target Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`101`, `102`, `103`, `104`, `105`, `106`, `107`, `108`, `109`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `101` | 0 | Target flash condition 101 |
  | `102` | 0 | Target flash condition 102 |
  | `103` | 0 | Target flash condition 103 |
  | `104` | 0 | Target flash condition 104 |
  | `105` | 0 | Target flash condition 105 |
  | `106` | 0 | Target flash condition 106 |
  | `107` | 0 | Target flash condition 107 |
  | `108` | 0 | Target flash condition 108 |
  | `109` | 0 | Target flash condition 109 |
  | `1` | 1 | Non-target stimulus condition 1 |
  | `2` | 1 | Non-target stimulus condition 2 |
  | `3` | 1 | Non-target stimulus condition 3 |
  | `4` | 1 | Non-target stimulus condition 4 |
  | `5` | 1 | Non-target stimulus condition 5 |
  | `6` | 1 | Non-target stimulus condition 6 |
  | `7` | 1 | Non-target stimulus condition 7 |
  | `8` | 1 | Non-target stimulus condition 8 |
  | `9` | 1 | Non-target stimulus condition 9 |
- **Kernel Notes**: Group all target flash codes (101-109) as class 0 (target) and all non-target stimulus codes (1-9) as class 1 (non-target). Kernel applies LDA classifier with CCA spatial filtering on 9-channel EEG. (replaces Potential Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.3390/s20247198 — Single-trial binary classification between target and non-target P300 events from EEG signals recorded using the openneuro ds003190 dataset with 19 subjects across 3 sessions, using CCA spatial filtering and LDA classifier, achieving ~82% accuracy with cartoon face stimuli.

## Data Quality Notes

- Very sparse 9-channel EEG; limited spatial coverage.
- 384 files across 19 subjects = ~20 runs/subject; verify session structure.
- Numeric trigger codes require specific kernel to decode semantic P300 target/non-target labels.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review