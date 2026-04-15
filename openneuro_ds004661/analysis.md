# ANDI: Auditory N-back Dual-task EEG

**Dataset**: `openneuro_ds004661` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004661
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 17 | **Channels**: 64 | **Sampling Rate**: 128 Hz
**Manual Review**: Pending

## Paradigm

A dual-task paradigm combining a guided visual search task (tracking a red annulus) with an auditory N-back working memory task to study cognitive interference. Event code `1` marks the dominant condition (non-target/standard trials, 29,820 total) and `2` marks the minority condition (target/match trials, 2,948 total). The large imbalance between codes (~10:1) indicates standard auditory stimuli vs. N-back target matches requiring working memory retrieval.

## File Scan Result

> **Kernel SHA256**: `9cf28f8bf286ba476d27c3c3eacedd92e217950653b5e31bb0314ec3bfe98249`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 29820 | event | raw | Non-target trial (auditory standard) |
| `2` | 2948 | event | raw | N-back target match |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: N-back Target Detection Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [1, 2]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Non-target trial (auditory standard) |
| `2` | 1 | N-back target match |

- **Evidence**: OpenNeuro dataset metadata and README. Source: https://openneuro.org/datasets/ds004661 DOI: https://doi.org/10.18112/openneuro.ds004661.v1.1.0
- **Kernel Notes**: Strong class imbalance (29,820 non-targets vs 2,948 targets, ~10:1 ratio) requires undersampling majority class or weighted loss function during training. Raw event codes are `1` and `2` (not documented codes `10`/`11`); verify mapping against dataset README. Low sampling rate (128 Hz) limits spectral resolution above 40 Hz (Nyquist); apply appropriate anti-aliasing and bandpass filtering during preprocessing.

### Normal Task 1: Cognitive Load ERP Analysis (Target vs Non-target)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [1, 2]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Non-target trial |
| `2` | 1 | N-back target match |

- **Evidence**: Dual-task paradigm combining visual search with auditory N-back; ERP components (e.g., P300, N200) expected for target detection in working memory tasks. Paradigm reference: Ries et al., 2016 (see dataset documentation).
- **Kernel Notes**: Window reduced to tmax=0.8s to focus on early ERP components; longer window (1.0s) may capture later cognitive processing stages. Consider baseline correction using pre-stimulus interval [-0.2, 0] s.

### Potential Task 1: Visual Search Performance During N-back Load
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping for visual search tracking task (red annulus tracking); parameters require verification from dataset README.
- **Evidence**: Paradigm plausibility; dual-task design suggests visual search performance is recorded alongside N-back task.
- **Kernel Notes**: Visual search task details (tracking accuracy, annulus position events) not directly captured in available event structure; verify with dataset supplementary files or README for event code definitions.

### Potential Task 2: Cross-Modal Interference Effects
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [1, 2]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**: Interaction labels between visual search load and N-back target detection derived from combined task conditions.
- **Evidence**: Dual-task paradigm design; cognitive interference between visual and auditory modalities expected.
- **Kernel Notes**: Cross-modal interference labels require super meta derivation combining visual search task performance metadata with N-back event timing; may need companion behavioral data files for subject-level load estimates.