# Assessment of the visual stimuli properties in P300 paradigm

**Dataset**: `openneuro_ds003190` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003190
**Category**: Sensory/Response | **Subjects**: 19 | **Files (Completed)**: 384 | **Manual Review**: Pending
**Channels**: 9 | **Sampling Rate**: 256 Hz

## Paradigm

A P300 ERP experiment evaluating the effects of stimulus count and visual presentation styles (standard flash vs. cartoon face) on EEG brain activity. The experiment used a P300-based BCI paradigm with target and non-target stimulus flashes. Codes 1-9 represent different non-target stimulus conditions (standard flash); codes 101-109 encode target flash conditions (cartoon face). Codes 200-203 serve as session/block configuration markers. The dataset comprises 19 subjects across multiple runs, totaling 384 BDF files.

## File Scan Result

> **Kernel SHA256**: `b39efab60211591cb32356eb1c56e892a569f70e6752c09d171e14fa6d5b2df1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger/1` | 110333 | event | raw | Non-target stimulus condition 1 (standard flash) |
| `trigger/101` | 570 | event | raw | Target flash condition 101 (cartoon face) |
| `trigger/102` | 537 | event | raw | Target flash condition 102 (cartoon face) |
| `trigger/103` | 548 | event | raw | Target flash condition 103 (cartoon face) |
| `trigger/104` | 576 | event | raw | Target flash condition 104 (cartoon face) |
| `trigger/105` | 466 | event | raw | Target flash condition 105 (cartoon face) |
| `trigger/106` | 322 | event | raw | Target flash condition 106 (cartoon face) |
| `trigger/107` | 251 | event | raw | Target flash condition 107 (cartoon face) |
| `trigger/108` | 169 | event | raw | Target flash condition 108 (cartoon face) |
| `trigger/109` | 75 | event | raw | Target flash condition 109 (cartoon face) |
| `trigger/2` | 110319 | event | raw | Non-target stimulus condition 2 (standard flash) |
| `trigger/200` | 3515 | event | raw | Session configuration marker 200 |
| `trigger/201` | 3515 | event | raw | Session configuration marker 201 |
| `trigger/202` | 3515 | event | raw | Session configuration marker 202 |
| `trigger/203` | 3515 | event | raw | Session configuration marker 203 |
| `trigger/3` | 110306 | event | raw | Non-target stimulus condition 3 (standard flash) |
| `trigger/4` | 110361 | event | raw | Non-target stimulus condition 4 (standard flash) |
| `trigger/5` | 93649 | event | raw | Non-target stimulus condition 5 (standard flash) |
| `trigger/6` | 65330 | event | raw | Non-target stimulus condition 6 (standard flash) |
| `trigger/7` | 48875 | event | raw | Non-target stimulus condition 7 (standard flash) |
| `trigger/8` | 32765 | event | raw | Non-target stimulus condition 8 (standard flash) |
| `trigger/9` | 16072 | event | raw | Non-target stimulus condition 9 (standard flash) |


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
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, baseline = (-0.2, 0.0) s, target_events = [`101`, `102`, `103`, `104`, `105`, `106`, `107`, `108`, `109`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `101` | 0 | Target flash condition 101 (cartoon face) |
  | `102` | 0 | Target flash condition 102 (cartoon face) |
  | `103` | 0 | Target flash condition 103 (cartoon face) |
  | `104` | 0 | Target flash condition 104 (cartoon face) |
  | `105` | 0 | Target flash condition 105 (cartoon face) |
  | `106` | 0 | Target flash condition 106 (cartoon face) |
  | `107` | 0 | Target flash condition 107 (cartoon face) |
  | `108` | 0 | Target flash condition 108 (cartoon face) |
  | `109` | 0 | Target flash condition 109 (cartoon face) |
  | `1` | 1 | Non-target stimulus condition 1 (standard flash) |
  | `2` | 1 | Non-target stimulus condition 2 (standard flash) |
  | `3` | 1 | Non-target stimulus condition 3 (standard flash) |
  | `4` | 1 | Non-target stimulus condition 4 (standard flash) |
  | `5` | 1 | Non-target stimulus condition 5 (standard flash) |
  | `6` | 1 | Non-target stimulus condition 6 (standard flash) |
  | `7` | 1 | Non-target stimulus condition 7 (standard flash) |
  | `8` | 1 | Non-target stimulus condition 8 (standard flash) |
  | `9` | 1 | Non-target stimulus condition 9 (standard flash) |
- **Evidence**:
  - DOI: 10.3390/s20247198 — "Single-Option P300-BCI Performance Is Affected by Visual Stimulation Conditions"; explicit dataset match (19 subjects, 3 sessions, ds003190); binary classification between target codes (101-109) and non-target codes (1-9) using CCA spatial filtering with LDA classifier; reports ~82% accuracy with cartoon face stimuli; paradigm confirms P300 oddball with standard flash vs cartoon face conditions.
- **Kernel Notes**: Group all target flash codes (101-109) as class 0 (target) and all non-target stimulus codes (1-9) as class 1 (non-target). The extreme class imbalance (~2,524 target vs ~584,169 non-target events across dataset) requires stratified sampling or class weighting. Configuration codes 200-203 (~3,515 each) are session/block markers and should NOT be included in epoching. Use -0.2 to 0 s for baseline correction to capture pre-stimulus activity.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
