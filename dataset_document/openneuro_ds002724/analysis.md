# A dataset recorded during development of an affective brain-computer music interface: training sessions

**Dataset**: `openneuro_ds002724` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002724
**Category**: High-level Mental | **Subjects**: 17 | **Files (Completed)**: 96 | **Channels**: 37 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) during the training phase of an affective brain-computer music interface. This is the training session companion to ds002722 (calibration) and ds002723 (testing). Codes 1-9 encode the nine target affective music conditions.

## File Scan Result

> **Kernel SHA256**: `8b42381113152290faf76763c1eaa743ccbfd986f4b73c621fbc098d77ebd1c3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Affective Music Condition Classification (Short-epoch)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music condition onset), overlap = null, target_events = [1, 2, 3, 4, 5, 6, 7, 8, 9]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| `1` | 0 | Music condition 1 (affective state A1) |
| `2` | 1 | Music condition 2 (affective state A2) |
| `3` | 2 | Music condition 3 (affective state A3) |
| `4` | 3 | Music condition 4 (affective state A4) |
| `5` | 4 | Music condition 5 (affective state A5) |
| `6` | 5 | Music condition 6 (affective state A6) |
| `7` | 6 | Music condition 7 (affective state A7) |
| `8` | 7 | Music condition 8 (affective state A8) |
| `9` | 8 | Music condition 9 (affective state A9) |
- **Evidence**: Daly et al. (2020). Neural and physiological data from participants listening to affective music. Scientific Data. DOI: https://doi.org/10.1038/s41597-020-0507-6
- **Kernel Notes**: Short epochs (-0.2 to 1.0s) capture initial neural response to affective state induction. Verify event channel naming in raw data (may differ from standard). 9-class balanced design across ~95-96 files per condition. Decode valence/arousal mapping from Daly et al. 2018.

---

### Classical Task 2: Affective Music Condition Classification (Sustained-segment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 40.0 s (full stimulus duration), overlap = null, target_events = [1, 2, 3, 4, 5, 6, 7, 8, 9]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| `1` | 0 | Music condition 1 (sustained affective state) |
| `2` | 1 | Music condition 2 (sustained affective state) |
| `3` | 2 | Music condition 3 (sustained affective state) |
| `4` | 3 | Music condition 4 (sustained affective state) |
| `5` | 4 | Music condition 5 (sustained affective state) |
| `6` | 5 | Music condition 6 (sustained affective state) |
| `7` | 6 | Music condition 7 (sustained affective state) |
| `8` | 7 | Music condition 8 (sustained affective state) |
| `9` | 8 | Music condition 9 (sustained affective state) |
- **Evidence**: Daly et al. (2020). Neural and physiological data from participants listening to affective music. Scientific Data. DOI: https://doi.org/10.1038/s41597-020-0507-6
- **Kernel Notes**: 40-second continuous music clips induce sustained affective states. Long event epoching captures entire stimulus period for decoding valence/arousal patterns. Cue duration (40s) is critical parameter. Physiological channels (ECG, GSR) present alongside EEG.

---

### Potential Task 1: Publisher-defined BIDS Task (Run)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| Needs verification | Needs verification | Needs verification |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002724
- **Kernel Notes**: Verify raw event extraction pipeline—triggers may use non-standard channel naming. Event detection reported 'no events detected' despite metadata confirming well-balanced distribution. Verify event channel name in raw data.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
