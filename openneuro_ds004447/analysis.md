# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A brain-computer interface (BCI) task based on sensorimotor rhythms (SMR) recorded with high-density scalp EEG. Subjects (N=30, age 18–27, 5 female/25 male) performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. The dataset contains 130-channel high-density EEG (GES400/Hydrocel GSN) with 4-second imagery windows aligned to visual cue onset. Alignment is confirmed as ONSET: "Onset of the first frame of each instruction presented on the screen" (BCI2000-style). Significant class imbalance exists, with event_2 (right hand) having 5090 trials versus event_1 (left hand) with only 327 trials. A feedback marker (event_5) and special session marker (event_6) appear in a subset of recordings.

## File Scan Result

> **Kernel SHA256**: `cdefee25bb451e6878563d1f76f44e328955ab2b55f29c6a2674c8572f8e6abc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 327 | event | raw | Motor imagery cue - class 1 (left hand MI) |
| `event_2` | 5090 | event | raw | Motor imagery cue - class 2 (right hand MI) |
| `event_3` | 3270 | event | raw | Motor imagery cue - class 3 (feet MI) |
| `event_4` | 1237 | event | raw | Motor imagery cue - class 4 (tongue MI) |
| `event_5` | 1237 | event | raw | Feedback cue or feedback onset marker |
| `event_6` | 91 | event | raw | Special session marker (subset of files) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Four-class Motor Imagery Classification

> **[AUTO-REMOVED]** This task was removed by the post-synthesis guard because it assigned motor imagery class labels to event IDs that are confirmed trial phase markers (e.g., rest/ready/task/interval) by the isolated P3b event annotator. The events.tsv ground truth takes precedence over BCI convention and paper content. If the dataset does encode MI class labels, they must appear in a sidecar file explicitly mapping event_ids to MI classes.
