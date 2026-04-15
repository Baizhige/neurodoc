# RS_TMSEEG_Data

**Dataset**: `openneuro_ds001849` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds001849
**Category**: Biological State | **Subjects**: 15 | **Files (Completed)**: 120 | **Channels**: 30 | **Sampling Rate**: 5000 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG data recorded in conjunction with Transcranial Magnetic Stimulation (TMS). Subjects were at rest (no active task) while TMS pulses were delivered; the R128 marker in BrainVision format marks a system/response trigger present in all files but does not indicate a meaningful task event. The primary scientific interest is resting-state oscillatory dynamics and TMS-evoked potentials.

## File Scan Result

> **Kernel SHA256**: `7b81a6091c86b9f1d9e9de67e1b15d497deb4a8b30611562665b6abc79aebad3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: R128` | 11961 | event | raw |  |
| `admin: boundary` | 135 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: TMS-Evoked Potential Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.05, tmax = 0.25, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| R128 | active | TMS pulse with active stimulation |
| R128 | sham | TMS pulse with sham stimulation |

- **Evidence**: DOI: 10.1371/journal.pone.0216185
- **Kernel Notes**: R128 is classified as a BrainVision administrative marker in this dataset's event structure. However, TMS pulses were delivered during recording (per paradigm description), and the cited reference confirms this dataset was used for site-specific TMS-EEG analysis (DLPFC, M1, PPC) with active vs. sham conditions. Verify that R128 aligns with TMS delivery timing; if not, TMS pulse timestamps may need extraction from separate metadata files. High sampling rate (5000 Hz) requires downsampling before analysis. TMS artifact rejection may be needed for the ~50 ms post-pulse window.

### Normal Task 1: Resting-State Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null — no task events; R128 is admin)
- **Meta Level**: `raw`
- **Evidence**: DOI: 10.1371/journal.pone.0216185 (resting-state oscillatory dynamics mentioned in context of TMS-EEG analysis)
- **Kernel Notes**: R128 appears in all 120 files (~100 occurrences per file) and is a BrainVision recording artifact marker — not a stimulus or response event. Since no genuine task events exist, epochs should be created by segmenting the continuous resting-state recording. High sampling rate (5000 Hz) may require downsampling for computational efficiency. Verify 30-channel consistency across subjects before pooling.