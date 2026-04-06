# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 280 | **Files (Completed)**: 280
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a sensorimotor rhythm-based brain-computer interface task using high-density scalp EEG. This is the fourth BMI-HDEEG dataset with a two-class (binary) motor imagery design (left hand vs. right hand). Only one event code is present in the data, suggesting the class label is encoded differently.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 280
- **Age Completeness**: 280/280 (100.0%)
- **Sex Completeness**: 280/280 (100.0%)
- **Observed Age Examples**: `23`, `22`, `24`, `21`, `33`, `50`, `20`, `58`
- **Observed Sex Examples**: `Male`, `Female`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004448.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `1cacae7b7d9e09450b37729be1cd9086290782e0083f4dcfba47afc4fe1abe26`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left_hand_MI` | 3635 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## STIM Label Summary

<!-- AUTO-KERNEL-STIM:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Label / Source / Meta Level` are kernel-derived facts.

| Label / Field | Source | Meta Level | Meaning |
|---------------|--------|------------|---------|
| `Status` | raw:stim_channel | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-STIM:END -->

- **Route**: `stim`
- **Role**: Kernel-derived label summary for the current route only.

## Tasks

### Classical Task 1: Right hand motor imagery vs relaxation binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 6-9 s * (imagery period), overlap = 0.0, target_events = [`1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `motor_imagery` | 1 | Right hand motor imagery period |
  | `relaxation` | 0 | Relaxation/-rest period |
- **Super Meta Notes**: (NOT APPLICABLE - meta_level is raw)
- **Evidence**:
  - DOI: `10.1038/s41597-023-02260-6` — Paper describes BMI-HDEEG dataset 4 (OpenNeuro ds004448) with high-density EEG during SMR-based BCI neurofeedback training where participants performed right-hand motor imagery vs relaxation, validated with binary classification of spectral power features to decode resting vs imagery periods.
- **Kernel Notes**: Kernel must parse events.tsv to identify imagery vs relaxation periods based on timing. Raw event ID `1` appears to mark motor imagery class. Verify event ID mapping from events.tsv. The actual binary labels (motor imagery vs relaxation) are derived from experimental timing/annotation metadata, not the single raw event code alone. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Motor Imagery Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one numerical code (1) visible in locator_meta; actual binary class label likely encoded in events.tsv metadata columns or file-level metadata. Specific kernel required.

| Event | y | Meaning |
 |-------|---|------|
 | `left_hand_MI` | 0 | Left hand motor imagery |
 | `right_hand_MI` | 1 | Right hand motor imagery |

## Data Quality Notes

- Only one event code in metadata; class label may be in events.tsv columns rather than trial_type
- 130-channel high-density EEG with extended epochs
- 280 files; binary MI design

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update