# Longitudinal EEG Test-Retest Reliability in Healthy Individuals

**Dataset**: `openneuro_ds007176` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007176
**Category**: Biological State | **Subjects**: 43 | **Files (Completed)**: 300 | **Channels**: 60 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Longitudinal resting-state EEG recordings collected over four sessions spanning two years to evaluate test-retest reliability of quantitative EEG measures. Recordings are continuous resting-state without structured task events. The dataset enables assessment of EEG biomarker stability across sessions and time points.

## File Scan Result

> **Kernel SHA256**: `eb67d493b7e4b41c77502f53ddf0a526aded127e8c1bee49194408e030932233`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 2 | event | raw | Null trigger with no experimental meaning; continuous resting-state recording |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Resting-State EEG Reliability Analysis

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5 s, target_events = null
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| N/A | N/A | No discrete trial events; continuous resting-state EEG segmented into fixed-length windows |

- **Notes**: Reliability analysis examines test-retest consistency of quantitative EEG biomarkers (e.g., spectral band power) across longitudinal sessions. Session/time-point labels from participants.tsv required as super meta for reliability modeling (ICC, W-corr, etc.).

- **Evidence (DOI)**: https://doi.org/10.1016/j.bspc.2026.109484

- **Kernel Notes**: Dataset contains purely continuous resting-state EEG with no meaningful experimental events (only null triggers `Stimulus/S 1`, count=2). Use fixed-length segmentation (4 s windows, 0.5 s overlap) to extract representative epochs across full recording duration. Apply bandpass filter (0.5–40 Hz) and artifact rejection (ICA) prior to segmentation. For test-retest reliability analysis, ensure consistent segment extraction strategy across all sessions per subject. Band power estimation via multitaper spectral approach as per referenced methodology.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
