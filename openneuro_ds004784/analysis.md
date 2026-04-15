# Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts

**Dataset**: `openneuro_ds004784` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004784
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 10 | **Channels**: 264 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Technical validation study using an electrically conductive head phantom to simulate brain activity under various artifact conditions (motion, muscle, eye movements) for testing EEG cleaning algorithms. The phantom dataset contains 264-channel EEG recordings with 30 total event markers across 10 files, representing different artifact conditions for algorithm validation.

## File Scan Result

> **Kernel SHA256**: `6f8ebcf042830fcf241a98aca30b700a9b6d73c959e1418bed26675675a9e943`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65343` | 10 | event | raw | Artifact condition marker B (artifact-off/clean baseline) |
| `65471` | 20 | event | raw | Artifact condition marker A (artifact-on/with artifacts) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

(No tasks could be synthesized.)