# 8-Channel SSVEP EEG Dataset with Artifact Trials

**Dataset**: `openneuro_ds004745` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004745
**Category**: Sensory/Response | **Subjects**: 6 | **Files (Completed)**: 6
**Channels**: 8 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed Steady-State Visual Evoked Potential (SSVEP) tasks at stimulation frequencies of 2 Hz, 4 Hz, and 8 Hz, under both static artifact-free and voluntary movement artifact conditions. The dataset was created to test artifact removal algorithms for SSVEP-based BCIs under realistic conditions with deliberate motion contamination. Multiple trigger codes mark different frequency and artifact conditions.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004745.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `6d6559969a2b89a29867759855196676c5eadee55145eabd8ac6475fee0ebb17`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `10` | 44 | event | raw | Unresolved from current kernel facts |
| `4` | 38 | event | raw | Unresolved from current kernel facts |
| `1` | 36 | event | raw | Unresolved from current kernel facts |
| `2` | 36 | event | raw | Unresolved from current kernel facts |
| `3` | 36 | event | raw | Unresolved from current kernel facts |
| `5` | 36 | event | raw | Unresolved from current kernel facts |
| `6` | 36 | event | raw | Unresolved from current kernel facts |
| `7` | 36 | event | raw | Unresolved from current kernel facts |
| `8` | 36 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: SSVEP frequency condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 0 | 2 Hz SSVEP condition |
  | `4` | 1 | 4 Hz SSVEP condition |
  | `8` | 2 | 8 Hz SSVEP condition |
  | `10` | 3 | Artifact/rest condition |
- **Evidence**:
  - DOI: 10.1109/embc46164.2021.9629771 — "This paper evaluates ASR artifact removal on 8-channel SSVEP EEG data from 6 subjects performing tasks at 2Hz, 4Hz, and 8Hz stimulation frequencies under both artifact-free and artifact conditions, computing Frequency-Tagged Response (FTR) as the SSVEP measure."
- **Kernel Notes**: Kernel extracts sliding windows of 10 s with 50-75% overlap from raw signal, then assigns label based on which SSVEP condition (2/4/8 Hz or artifact/rest) was active during that window. Requires events.tsv to determine condition timing for label assignment. Bandpass filter 0.15-40Hz applied as preprocessing. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: SSVEP frequency condition classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 6 subjects - very small dataset. Full trigger decode needed from events.tsv. Deliberate motion artifacts present in some trials.

| Event | y | Meaning |
|-------|--|--------|
| `2` | 0 | 2 Hz SSVEP condition |
| `4` | 1 | 4 Hz SSVEP condition |
| `8` | 2 | 8 Hz SSVEP condition |
| `10` | 3 | Artifact/rest condition |

## Data Quality Notes

- Only 6 subjects and 8 channels - limited for generalization.
- Deliberate motion artifacts present in some trials; note artifact condition labels.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update