# Inner Speech BCI Dataset

**Dataset**: `openneuro_ds003626` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003626
**Category**: High-level Mental | **Subjects**: 10 | **Files (Completed)**: 30
**Channels**: 137 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Participants performed inner speech (imagined speech), pronounced speech, and visualization tasks involving four directional commands (Up, Down, Right, Left) and eight word stimuli (social words: child, daughter, father, wife; numerical words: four, three, ten, six) to explore the neural correlates of the 'inner voice' phenomenon for potential BCI applications. High-density EEG (137 channels) was recorded during all three modalities of speech production/imagery. No discrete event markers were captured in the EEG trigger channel; paradigm timing is encoded externally in events.tsv and behavioral log files.

## File Scan Result

> **Kernel SHA256**: `c3863c6607ab7b9e7b768f8ac27a70815d37b89e84c98398e6fc5eca3b04b6f3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_11` | 30 | event | raw | Word stimulus onset (social category - session blocks) |
| `event_12` | 30 | event | raw | Word stimulus onset (social category - session blocks) |
| `event_13` | 30 | event | raw | Word stimulus onset (social category - session blocks) |
| `event_14` | 30 | event | raw | Word stimulus onset (social category - session blocks) |
| `event_15` | 150 | event | raw | Word stimulus trial events (social words) |
| `event_16` | 150 | event | raw | Word stimulus trial events (numerical words) |
| `event_17` | 379 | event | raw | Inter-trial interval or response-related events |
| `event_21` | 30 | event | raw | Session or block start marker (modality 1) |
| `event_22` | 61 | event | raw | Block or trial segment marker (modality 2) |
| `event_23` | 59 | event | raw | Block or trial segment marker (modality 3) |
| `event_31` | 1409 | event | raw | Continuous recording segment marker |
| `event_32` | 1410 | event | raw | Continuous recording segment marker |
| `event_33` | 1409 | event | raw | Continuous recording segment marker |
| `event_34` | 1407 | event | raw | Continuous recording segment marker |
| `event_42` | 5634 | event | raw | Continuous EEG data block |
| `event_44` | 5632 | event | raw | Continuous EEG data block |
| `event_45` | 5636 | event | raw | Continuous EEG data block |
| `event_46` | 5631 | event | raw | Continuous EEG data block |
| `event_51` | 120 | event | raw | Rest period or fixation cross events |
| `event_61` | 81 | event | raw | Directional command event (Up/visualization) |
| `event_62` | 93 | event | raw | Directional command event (Down/visualization) |
| `event_63` | 88 | event | raw | Directional command event (Left/visualization) |
| `event_64` | 116 | event | raw | Directional command event (Right/visualization) |
| `event_65536` | 1 | admin | raw | Recording initialization or metadata marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Inner speech word classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = ["child", "daughter", "father", "wife", "four", "three", "ten", "six"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `child` | 0 | Social word - child |
  | `daughter` | 1 | Social word - daughter |
  | `father` | 2 | Social word - father |
  | `wife` | 3 | Social word - wife |
  | `four` | 4 | Numerical word - four |
  | `three` | 5 | Numerical word - three |
  | `ten` | 6 | Numerical word - ten |
  | `six` | 7 | Numerical word - six |
- **Evidence**:
  - DOI: 10.3389/fnhum.2025.1668935 — Uses OpenNeuro ds003626 to classify 8 imagined words (social and numerical categories) from EEG using EEGNet and Transformer models with LOSO cross-validation
- **Kernel Notes**: ⚠️ **Event ID Mapping Verification Required**: The target_events listed are semantic labels. Actual event IDs in the dataset are numeric (event_11-event_17). Kernel must verify mapping between semantic word labels and numeric event IDs from events.tsv. Available event IDs with 30 counts (event_11, event_12, event_13, event_14) are candidates for the 4 social word categories; verify correspondence. Bandpass 0.1-50Hz FIR filtering and artifact rejection ±300μV recommended per literature.

### Potential Task 2: Directional command decoding (inner speech, pronounced speech, visualization)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s, tmin = null, tmax = null, target_events = ["Up", "Down", "Left", "Right"]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Up` | 0 | Upward directional command |
  | `Down` | 1 | Downward directional command |
  | `Left` | 2 | Left directional command |
  | `Right` | 3 | Right directional command |
- **Super Meta Notes**: Three modalities captured: inner speech, pronounced speech, and visualization. No EEG trigger markers present in raw data. Trial onsets and modality labels must be reconstructed from events.tsv or behavioral logs. Modality and directional command labels are embedded in external timing files, requiring super-meta extraction.
- **Evidence**:
  - DOI: 10.1038/s41597-022-01147-2 — Dataset descriptor paper for OpenNeuro ds003626; provides acquisition protocol but does not define specific ML classification task for directional commands
  - Partial Support: Paradigm description indicates 4 directional commands (Up/Down/Left/Right) across 3 modalities, but no reference provides validated epoch parameters or event mapping for this specific classification task
- **Kernel Notes**: ⚠️ **Validation Needed**: (1) Directional command event IDs not found in available event IDs — must verify mapping from events.tsv. (2) Three modalities require modality label extraction as part of super-meta. (3) Epoch parameters tmin/tmax undefined — reconstruction from external timing required. (4) High-density 137-channel EEG at 1024Hz; segmentation with 0.5s overlap enables continuous BCI decoding approach. Small sample size (n=10) limits generalization.
