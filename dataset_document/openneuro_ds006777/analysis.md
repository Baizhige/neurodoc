# SFARI AVSRT EEG

**Dataset**: `openneuro_ds006777` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006777
**Category**: Sensory/Response | **Subjects**: 132 | **Files (Completed)**: 132 | **Channels**: 73 | **Sampling Rate**: 512 Hz | **Manual Review**: Pending

## Paradigm

An audiovisual simple reaction-time task (AVSRT) in which participants press a button as quickly as possible upon detecting auditory, visual, or simultaneous audiovisual stimuli. The paradigm measures unimodal vs. multimodal stimulus processing and associated reaction times. The dataset is from the SFARI (Simons Foundation Autism Research Initiative) collection, likely including participants with autism spectrum disorder and neurotypical controls.

## File Scan Result

> **Kernel SHA256**: `6ef3d79d2cd164466ef2d325b9b71b720b3aa054f8c6c3ab69f941a8178ae637`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 46308 | event | raw | Participant button-press response |
| `event_201` | 4 | admin | raw | System artifact (exclude) |
| `event_3` | 16129 | event | raw | Simultaneous audiovisual stimulus onset |
| `event_4` | 15995 | event | raw | Auditory-only stimulus onset |
| `event_5` | 16250 | event | raw | Visual-only stimulus onset |
| `event_50` | 3 | admin | raw | System artifact (exclude) |
| `event_65536` | 355 | admin | raw | System artifact (exclude) |
| `event_65537` | 45 | admin | raw | System artifact (exclude) |
| `event_65539` | 1 | admin | raw | System artifact (exclude) |
| `event_65737` | 483 | admin | raw | System artifact (exclude) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus Modality Classification (Auditory / Visual / Audiovisual)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| `event_3` | 1 | Simultaneous audiovisual stimulus |
| `event_4` | 2 | Auditory-only stimulus |
| `event_5` | 3 | Visual-only stimulus |
- **Evidence** (DOI): https://doi.org/10.18112/openneuro.ds006777.v1.0.0
- **Kernel Notes**: Three conditions are well-balanced (~16 000 trials each). Exclude system artifacts (event_201, event_50, event_65536–event_65737) from epoching. Apply 0.5–40 Hz bandpass and baseline correction (−0.2 to 0 s) before decoding. event_1 (Response_button) is a motor response marker; exclude from stimulus classification.

---

### Potential Task 2: Reaction-Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| MISC Channel Name | Y Mapping Notes |
|---|---|
| `reaction_time` | RT (seconds) = Response_button (event_1) onset − stimulus onset; derived via stim–response pairing. Needs verification: channel name not confirmed in MISC Label Summary (no MISC channels present in scan). |
- **Evidence** (DOI): https://doi.org/10.18112/openneuro.ds006777.v1.0.0
- **Kernel Notes**: RT target is stored in misc/reaction_time channel (derived, not native raw event). Stimulus modality (event_3/4/5) can be included as a covariate. Guard against missed responses (no following Response_button) and catch trials with multiple responses per stimulus. Store derivation source, unit (seconds), and version metadata per Type 2 kernel mode.

---

### Potential Task 3: Response-Locked Motor Epoch (Lateralized Readiness Potential / Motor ERP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| `event_1` | 1 | Button-press response |
- **Evidence** (DOI): https://doi.org/10.18112/openneuro.ds006777.v1.0.0
- **Kernel Notes**: Epochs locked to event_1 (Response_button) isolate motor preparation (LRP) and execution components. A 600 ms pre-response window captures motor preparation; 400 ms post-response covers post-movement rebound. Baseline correction: −0.6 to −0.4 s relative to response. Analyze separately from stimulus-locked epochs to avoid conflation of sensory and motor activity.

---

### Potential Task 1: Group Membership Prediction (ASD vs. Neurotypical)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| MISC Channel Name | Y Mapping Notes |
|---|---|
| `group_label` | ASD vs. NT group membership from participant metadata. Needs verification: no MISC channels present in scan; consider `info` route using `sex` or `age` fields, or derive from external participant metadata. |
- **Evidence** (DOI): https://doi.org/10.18112/openneuro.ds006777.v1.0.0
- **Kernel Notes**: SFARI cohort includes ASD and neurotypical participants. Group membership is a subject-level covariate, not an event label; route via misc with source (participant metadata) and version metadata. May be combined with stimulus-locked epochs for group-difference decoding.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
