# A dataset recorded during development of an affective brain-computer music interface: testing session

**Dataset**: `openneuro_ds002723` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002723
**Category**: Complex Applied | **Subjects**: 8 | **Files (Completed)**: 44 | **Channels**: 37.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants interacted with a real-time affective brain-computer music interface (BCMI) that modified music on-the-fly based on detected emotional states, aiming to induce specific target affective trajectories. This is the testing session of the BCI system (see also ds002722 calibration and ds002724 training sessions). Codes 1-9 encode the target or detected affective music conditions.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2` | 44 (files) | event | raw | Affective music condition 2 |
| `6` | 44 (files) | event | raw | Affective music condition 6 |
| `9` | 42 (files) | event | raw | Affective music condition 9 |
| `4` | 42 (files) | event | raw | Affective music condition 4 |
| `5` | 39 (files) | event | raw | Affective music condition 5 |
| `7` | 38 (files) | event | raw | Affective music condition 7 |
| `1` | 29 (files) | event | raw | Affective music condition 1 |
| `3` | 28 (files) | event | raw | Affective music condition 3 |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Affective Music Condition Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `2` | 0 | Music condition 2 |
  | `6` | 1 | Music condition 6 |
  | `9` | 2 | Music condition 9 |
  | `4` | 3 | Music condition 4 |
  | `5` | 4 | Music condition 5 |
  | `7` | 5 | Music condition 7 |
  | `1` | 6 | Music condition 1 |
  | `3` | 7 | Music condition 3 |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — The paper describes the BCMI testing dataset (ds002723) containing EEG recordings from 8 participants during evaluation of the Brain-Computer Music Interface system, where music conditions 1-9 were used as affective state markers (excluding condition 8).
- **Kernel Notes**: Events are long-type markers (>=2s) representing sustained 60-second trials with 20s target affective state, 20s identify state, and 20s alter state phases. Use epoch_by_long_event_hdf5 to extract the full 60s window for each music condition. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Small dataset: 8 subjects, 44 files.
- 37-channel array includes physiological channels; verify EEG-only channel selection.
- Decode code-to-condition mapping from Daly et al. 2018 (Scientific Data).
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review