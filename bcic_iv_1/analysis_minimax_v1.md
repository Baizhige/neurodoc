# BCI Competition IV Dataset 1 (Motor Imagery, Uncued Classifier Application)

**Dataset**: `bcic_iv_1` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_1.html
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 14 | **Channels**: 59 | **Sampling Rate**: 1000 Hz

## Paradigm

Seven subjects performed two-class motor imagery without feedback in an asynchronous (self-paced) BCI paradigm (BCI Competition IV, 2008). The two movement classes differed per subject, selected from: left hand, right hand, or foot imagery. A calibration phase used visual arrow cues with 4-second imagery intervals. The evaluation phase used acoustic cues (spoken words) with variable-duration imagery (1.5-8 s) and rest periods (1.5-8 s), simulating a realistic asynchronous BCI scenario. Both calibration and evaluation `.mat` files are provided per subject; the kernel reads class names and event positions directly from the `.mat` structure.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iv/desc_1.html

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left` | ~100/subject | short | raw | Cue onset for left-hand motor imagery |
| `right` | ~100/subject | short | raw | Cue onset for right-hand motor imagery (subjects assigned right class) |
| `foot` | ~100/subject | short | raw | Cue onset for foot motor imagery (subjects assigned foot class) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Class labels vary per subject: some subjects have `left` + `right`, others have `left` + `foot`. Event names are loaded dynamically from `nfo.className` in the `.mat` file. Counts shown are approximate per calibration file.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left`, `right` or `foot`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left` | 0 | Left-hand motor imagery |
  | `right` | 1 | Right-hand motor imagery (subjects assigned right class) |
  | `foot` | 1 | Foot motor imagery (subjects assigned foot class) |
- **Evidence**:
  - DOI: https://doi.org/10.1016/j.neuroimage.2007.01.051 — BCI Competition IV Dataset 1 description confirming motor imagery paradigm with 4-second imagery intervals during calibration
- **Kernel Notes**: Class labels vary per subject (some have left+right, others left+foot). Kernel must read class names from the `.mat` file's `nfo.className` field and create annotations accordingly. Evaluation phase has variable-length trials (1.5-8s); use cue positions as epoch anchors.

### Normal Task 1: Two-Class Motor Imagery Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Class names are subject-specific; the kernel reads them from the `.mat` file and creates annotations accordingly. Evaluation files have continuous recordings with variable-length trials and idle periods; only annotated cue positions should be used as epoch anchors. High sampling rate (1000 Hz); consider downsampling to <=250 Hz.

| Event | y | Meaning |
|-------|---|---------|
| `left` | 0 | Left-hand motor imagery |
| `right` or `foot` | 1 | Second motor imagery class (subject-specific) |
## Data Quality Notes

- Two-class labels vary per subject (left+right vs. left+foot); verify class names per file from the `eegunity_description` field or the `.mat` `nfo.className` field.
- No age or sex information is available in the public release.
- Evaluation phase has variable trial durations and idle periods; the idle state is unlabeled and should be identified by absence of annotations.
- High sampling rate (1000 Hz); memory-intensive; downsampling recommended.

## References

- **Reference**: BCI Competition IV (2008), Dataset 1 - Motor Imagery, Uncued Classifier Application. https://www.bbci.de/competition/iv/desc_1.html

## Data Quality Notes

- Two-class labels vary per subject (left+right vs. left+foot); verify class names per file from the `eegunity_description` field or the `.mat` `nfo.className` field.
- No age or sex information is available in the public release.
- Evaluation phase has variable trial durations and idle periods; the idle state is unlabeled and should be identified by absence of annotations.
- High sampling rate (1000 Hz); memory-intensive; downsampling recommended.

## References

- **Reference**: BCI Competition IV (2008), Dataset 1 - Motor Imagery, Uncued Classifier Application. https://www.bbci.de/competition/iv/desc_1.html
