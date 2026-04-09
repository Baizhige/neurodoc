# Longitudinal EEG Test-Retest Reliability in Healthy Individuals

**Dataset**: `openneuro_ds007176` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007176
**Category**: Biological State | **Subjects**: 43 | **Files (Completed)**: 300 | **Channels**: 60 | **Sampling Rate**: 1000 Hz

## Paradigm

Longitudinal resting-state EEG recordings collected over four sessions spanning two years to evaluate test-retest reliability of quantitative EEG measures. Recordings are continuous resting-state without structured task events. The dataset enables assessment of EEG biomarker stability across sessions and time points.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds007176.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `06e729f9bd42c4aeb04aabd29647827a0f31ed963ca3833e3643b32258decd48`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 2 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: N/A (no trial events; target_events: null)
- **Notes**: Only event code `0` present (2 total); this is a null trigger with no experimental meaning. Resting-state data; use segmentation across full recording. Session/time-point labels available from participants.tsv for longitudinal analysis.

## Data Quality Notes

- No meaningful event markers; purely continuous resting-state EEG.
- 43 subjects x ~7 sessions/subject = 300 files; multi-session longitudinal design.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update