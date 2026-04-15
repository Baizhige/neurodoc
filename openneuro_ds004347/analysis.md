# Symmetry perception and affective responses: a combined EEG/EMG study

**Dataset**: `openneuro_ds004347` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004347
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24
**Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a visual perception task identifying whether stimuli were regular (symmetric) or random (asymmetric) patterns to investigate symmetry perception and affective responses. EEG and EMG were simultaneously recorded to capture both neural and facial muscle activity. The dataset contains trial-level event markers aligned to stimulus onset for epoch-based analysis.

## File Scan Result

> **Kernel SHA256**: `4153fa480bb54aa5ba354ba98ab968c6fccd2c325794a731b9955bd8a10551b7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 1920 | event | raw | Symmetry condition: reflectional/regular patterns |
| `event_3` | 1919 | event | raw | Asymmetry condition: random patterns |
| `event_65536` | 5 | event | raw | System marker: experiment control event |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Symmetry Perception Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, baseline = (-0.2, 0.0)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `event_1` | 1 | Symmetry condition: reflectional/regular patterns |
  | `event_3` | 0 | Asymmetry condition: random patterns |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2012.10.003` — Original publication for ds004347; combined EEG/EMG recording; participants classified reflection vs random patterns; 80 trials per condition per participant; analyzes ERPs (N1/P1 components) and SPN for symmetry perception
- **Kernel Notes**: The dataset contains 3839 trial events (event_1: 1920, event_3: 1919) corresponding to symmetry vs asymmetry conditions. Apply baseline correction using pre-stimulus window. Exclude EMG/EOG channels (~8-10 of 73 channels) from EEG analyses. Consider separate pipelines for EEG vs EMG data.

### Potential Task 2: Continuous Segmentation (spectral/connectivity analysis)
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**:
  | Segment Condition | y | Meaning |
  |------------------|---|--------|
  | Sliding window across recording | variable | Time-frequency power or connectivity metrics across continuous EEG |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2012.10.003` — Paper supports time-frequency analysis of symmetry perception; dual EEG-EMG recording enables combined sensorimotor and neural analysis
- **Kernel Notes**: Continuous segmentation enables spectral and connectivity analyses complementary to trial-averaged ERPs. Useful for capturing sustained processing (SPN) and oscillatory dynamics across the ~3s stimulus duration. Merge segments with external metadata if condition labels needed per window.
