# ArEEG: Arabic Inner Speech EEG Dataset

**Dataset**: `openneuro_ds005262` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005262
**Category**: High-level Mental | **Subjects**: 12 | **Files (Completed)**: 186 | **Channels**: 8 | **Sampling Rate**: 250 Hz
**Manual Review**: Pending

## Paradigm

EEG recordings of 12 subjects performing imagined (inner) speech tasks based on visual cues presented in Modern Standard Arabic. Subjects silently imagined saying directional words (Up, Down, Left, Right), a Select command, or remained at Rest. The study aims to develop Arabic-language BCI systems using inner speech decoding without overt vocalization.

## File Scan Result

> **Kernel SHA256**: `bbbb68a2f8bc904707e779b7f404fda50f268d5c255fddcaa4d755d6859ddda8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Down` | 916 | event | raw | Inner speech of "Down" command |
| `Comment/Left` | 917 | event | raw | Inner speech of "Left" command |
| `Comment/Rest` | 4590 | event | raw | Rest condition (baseline) |
| `Comment/Right` | 918 | event | raw | Inner speech of "Right" command |
| `Comment/Select` | 918 | event | raw | Inner speech of "Select" command |
| `Comment/Up` | 918 | event | raw | Inner speech of "Up" command |
| `Comment/Wait` | 8949 | event | raw | Wait period (inter-trial interval) |
| `Comment/WarmUp` | 174 | admin | raw | Warm-up period (exclude) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Arabic Inner Speech Command Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Comment/Up`, `Comment/Down`, `Comment/Left`, `Comment/Right`, `Comment/Select`, `Comment/Rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `Comment/Rest` | 0 | Rest condition (baseline) |
  | `Comment/Up` | 1 | Inner speech of "Up" command |
  | `Comment/Down` | 2 | Inner speech of "Down" command |
  | `Comment/Left` | 3 | Inner speech of "Left" command |
  | `Comment/Right` | 4 | Inner speech of "Right" command |
  | `Comment/Select` | 5 | Inner speech of "Select" command |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05387-w — "ArEEG: an Open-Access Arabic Inner Speech EEG Dataset" (Scientific Data, 2025) — describes the exact openneuro_ds005262 dataset with 12 subjects, 8-channel EEG, 250 Hz sampling rate, and explicitly defines the 6-class inner speech classification task with Rest=0, Up=1, Down=2, Left=3, Right=4, Select=5 label mapping
- **Kernel Notes**: Extract epochs from -0.2s to 1.0s around each cue event marking visual cue onset. Exclude `Comment/Wait` (inter-trial interval marker, 8949 events) and `Comment/WarmUp` (admin, 174 events). Rest class has ~5x more trials (4590) than command classes (~918 each) — class balancing recommended. Apply 1–50 Hz bandpass filter. Use CSP or shallow classifiers (LDA, SVM) given only 8 channels and limited spatial resolution.