# ArEEG: Arabic Inner Speech EEG Dataset

**Dataset**: `openneuro_ds005262` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005262
**Category**: High-level Mental | **Subjects**: 12 | **Files (Completed)**: 186 | **Channels**: 8 | **Sampling Rate**: 250 Hz

## Paradigm

EEG recordings of 12 subjects performing imagined (inner) speech tasks based on visual cues presented in Modern Standard Arabic. Subjects silently imagined saying directional words (Up, Down, Left, Right), a Select command, or remained at Rest. The study aims to develop Arabic-language BCI systems using inner speech decoding without overt vocalization.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005262

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Wait` | 8949 | short | raw | Wait period (inter-trial interval) |
| `Comment/Rest` | 4590 | rest | raw | Rest condition |
| `Comment/Up` | 918 | short | raw | Inner speech - "Up" command |
| `Comment/Select` | 918 | short | raw | Inner speech - "Select" command |
| `Comment/Right` | 918 | short | raw | Inner speech - "Right" command |
| `Comment/Left` | 917 | short | raw | Inner speech - "Left" command |
| `Comment/Down` | 916 | short | raw | Inner speech - "Down" command |
| `Comment/WarmUp` | 174 | admin | raw | Warm-up period (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Arabic inner speech command classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Comment/Up`, `Comment/Down`, `Comment/Left`, `Comment/Right`, `Comment/Select`, `Comment/Rest`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Comment/Rest` | 0 | Rest condition (baseline) |
  | `Comment/Up` | 1 | Inner speech of "Up" command |
  | `Comment/Down` | 2 | Inner speech of "Down" command |
  | `Comment/Left` | 3 | Inner speech of "Left" command |
  | `Comment/Right` | 4 | Inner speech of "Right" command |
  | `Comment/Select` | 5 | Inner speech of "Select" command |
- **Evidence**:
  - DOI: https://doi.org/10.18112/openneuro.ds005262.v1.0.1 — Dataset description confirms six-class inner speech task (Up, Down, Left, Right, Select, Rest) with Arabic visual cues
- **Kernel Notes**: Epochs extracted around each cue event. Exclude `Comment/Wait` (inter-trial interval) and `Comment/WarmUp` (admin). Bandpass filter 1-50 Hz recommended. Use CSP or shallow classifiers (LDA, SVM) given only 8 channels.

### Normal Task 1: Inner Speech Command Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Comment/Wait is a high-frequency inter-trial marker - exclude from classification. Comment/WarmUp is admin - exclude. Only 8 EEG channels.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/Rest` | 0 | Rest condition |
 | `Comment/Up` | 1 | Inner speech "Up" |
 | `Comment/Down` | 2 | Inner speech "Down" |
 | `Comment/Left` | 3 | Inner speech "Left" |
 | `Comment/Right` | 4 | Inner speech "Right" |
 | `Comment/Select` | 5 | Inner speech "Select" |


## Data Quality Notes

- Only 8 EEG channels - limited spatial resolution.
- Comment/Wait (8,949 total) is inter-trial interval - exclude from classification.
- Comment/WarmUp is admin - exclude.

## References

- **Reference**: `ArEEG: Arabic Inner Speech EEG dataset`
