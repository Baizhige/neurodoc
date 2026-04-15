# A dataset recorded during development of an affective brain-computer music interface: calibration session

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 94 | **Channels**: 37 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) as a calibration session for an affective brain-computer music interface (BCMI). EEG and physiological signals were recorded to build a mapping from neural/physiological features to targeted emotional states. Codes 1-9 are primary music condition labels; 100-200 range codes encode specific music clip identifiers.

## File Scan Result

> **Kernel SHA256**: `7a06edeb5c3973a647191dafb67dc052c48de334ddb6d6d730109caca0b04194`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Affective Music Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 40.0 s, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|--------------------------|
  | `1` | 0 | Music condition 1 (affective state A) |
  | `2` | 1 | Music condition 2 (affective state B) |
  | `3` | 2 | Music condition 3 (affective state C) |
  | `4` | 3 | Music condition 4 (affective state D) |
  | `5` | 4 | Music condition 5 (affective state E) |
  | `6` | 5 | Music condition 6 (affective state F) |
  | `7` | 6 | Music condition 7 (affective state G) |
  | `8` | 7 | Music condition 8 (affective state H) |
  | `9` | 8 | Music condition 9 (affective state I) |
- **Evidence**:
  - DOI: `10.1038/s41597-020-0507-6` — The paper is the official data descriptor for openneuro_ds002722, describing EEG and physiological recordings from 19 participants listening to 40-second synthetic music clips with 9 different affective conditions (codes 1-9), presented during 5 runs of 18 trials each as a BCMI calibration session.
  - DOI: `10.1038/s41598-022-27361-x` — Demonstrates neural decoding of music from EEG using a similar synthetic music paradigm by the same research group.
- **Kernel Notes**: Epochs align to the onset of each 40-second music clip. Verify EEG-only channels among the 37-channel setup before pooling across subjects. Codes 100-200 (specific clip identifiers) should be filtered; use only codes 1-9 for condition labels.