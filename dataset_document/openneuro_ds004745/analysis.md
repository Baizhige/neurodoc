# 8-Channel SSVEP EEG Dataset with Artifact Trials

**Dataset**: `openneuro_ds004745` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004745
**Category**: Sensory/Response | **Subjects**: 6 | **Files (Completed)**: 6 | **Channels**: 8 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants performed Steady-State Visual Evoked Potential (SSVEP) tasks at stimulation frequencies of 2 Hz, 4 Hz, and 8 Hz, under both static artifact-free and voluntary movement artifact conditions. The dataset was created to test artifact removal algorithms for SSVEP-based BCIs under realistic conditions with deliberate motion contamination. Recordings were collected using an 8-channel BioWolf dry electrode system at 1000 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `8ec4540117314d5c94bcdba63475778b4971a7f0fdaef0fb2bd508b0cac49327`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 36 | event | raw | Unresolved |
| `10` | 44 | event | raw | Artifact/rest condition |
| `2` | 36 | event | raw | 2 Hz SSVEP condition |
| `3` | 36 | event | raw | Unresolved |
| `4` | 38 | event | raw | 4 Hz SSVEP condition |
| `5` | 36 | event | raw | Unresolved |
| `6` | 36 | event | raw | Unresolved |
| `7` | 36 | event | raw | Unresolved |
| `8` | 36 | event | raw | 8 Hz SSVEP condition |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: SSVEP Frequency Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--|--------|
  | `2` | 0 | 2 Hz SSVEP condition |
  | `4` | 1 | 4 Hz SSVEP condition |
  | `8` | 2 | 8 Hz SSVEP condition |
  | `10` | 3 | Artifact/rest condition |
- **Evidence**:
  - DOI: 10.1109/EMBC46164.2021.9629771 — "Efficient Artifact Removal from Low-Density Wearable EEG using Artifacts Subspace Reconstruction" — Six young adults performed SSVEP tasks at 2/4/8 Hz stimulation frequencies under both artifact-free and artifact conditions using BioWolf 8 dry electrodes at 1000 Hz sampling. Paper evaluates ASR-cleaned SSVEP responses with Frequency-Tagged Response (FTR) as the classification measure. This is the originating publication for this dataset.
- **Kernel Notes**: Kernel extracts sliding 10 s windows with 50% overlap from raw continuous data, assigns labels based on which SSVEP condition (2/4/8 Hz or artifact/rest) was active during that window. Requires events.tsv to determine condition timing for label assignment. SSVEP harmonics at multiples of stimulation frequency are key features. Bandpass filter 0.15–40 Hz recommended as preprocessing.

### Potential Task 1: SSVEP Event-Locked Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--|--------|
  | `2` | 0 | 2 Hz SSVEP condition onset |
  | `4` | 1 | 4 Hz SSVEP condition onset |
  | `8` | 2 | 8 Hz SSVEP condition onset |
  | `10` | 3 | Artifact/rest condition onset |
- **Evidence**:
  - Paradigm-aligned: SSVEP condition onsets marked by trigger codes allow event-locked epoching around condition transitions. The 1.2 s window captures transient response dynamics following condition switches while maintaining a baseline period for drift correction.
- **Kernel Notes**: Event-locked epoching around condition onset markers (events 2/4/8 for frequency conditions, event 10 for artifact/rest). Shorter window suitable for capturing transient responses to condition changes. Note: only 6 subjects limits statistical power; this approach is plausible but not directly validated by the reference paper which used sliding window segmentation.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
