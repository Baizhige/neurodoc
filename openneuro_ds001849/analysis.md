# RS_TMSEEG_Data

**Dataset**: `openneuro_ds001849` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds001849
**Category**: Biological State | **Subjects**: N/A | **Files (Completed)**: 120 | **Channels**: 30.0 | **Sampling Rate**: 5000.0 Hz

## Paradigm

Resting-state EEG data recorded in conjunction with Transcranial Magnetic Stimulation (TMS). Subjects were at rest (no active task) while TMS pulses were delivered; the R128 marker in BrainVision format marks a system/response trigger present in all files but does not indicate a meaningful task event. The primary scientific interest is resting-state oscillatory dynamics and TMS-evoked potentials.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `R128` | 120 (files) | admin | raw | BrainVision system/response trigger present in every file - not a task event |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null (no task events; R128 is admin))
- **Notes**: R128 appears in all 120 files and is a BrainVision recording artifact marker. High sampling rate (5000 Hz); consider downsampling. TMS artifact rejection may be needed if TMS pulses are captured in recording.

## Data Quality Notes

- R128 is a BrainVision system marker present in every file - it is not a stimulus or response event.
- High sampling rate (5000 Hz); significant downsampling required before most analyses.
- TMS artifacts may contaminate EEG within the first ~50 ms post-pulse; apply TMS artifact rejection if analyzing TMS-evoked potentials.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review