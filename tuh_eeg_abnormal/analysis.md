# TUH EEG Abnormal Corpus

**Dataset**: `tuh_eeg_abnormal` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_abnormal/v3.0.1/
**Category**: Biological State | **Subjects**: ~2983 | **Files (Completed)**: 2983 | **Channels**: 27-36 | **Sampling Rate**: 250-512 Hz

## Paradigm

The TUH EEG Abnormal Corpus (v3.0.1) is a clinically annotated subset of the TUH EEG Corpus where each recording has been classified as **normal** or **abnormal** by board-certified neurologists (Lopez et al., 2015). Recordings are routine clinical EEG sessions acquired in an outpatient setting at Temple University Hospital. The normal/abnormal label reflects the overall clinical impression of the EEG recording, not individual event annotations. The label is encoded in the directory path (`normal/` or `abnormal/`) and extracted by the kernel to create a single whole-recording annotation.

## File Scan Result

> **Kernel SHA256**: `644d71b532db95d6bc8a1e80722382dbac84ca6c834951df359825f61b56f3d3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `abnormal` | 1466 | event | raw |  |
| `normal` | 1517 | event | raw |  |


### Info
Placeholder: File scan results to be documented.

## Tasks

### Primary Task 1: Normal vs abnormal EEG recording classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `Annotation`
- **Target Definition**: Recording-level normal/abnormal diagnostic label.
- **Evidence**: TUH Abnormal Corpus is explicitly curated for normal-versus-abnormal EEG classification. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.3389/fnins.2016.00196

### Normal Task 1: Normal vs. Abnormal EEG Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: The annotation spans the entire recording; use `epoch_by_long_event_hdf5` with sliding windows. Parse the label prefix before the colon (`:`) to extract the class name. Near-balanced classes: 1517 normal vs. 1466 abnormal.

| Event | y | Meaning |
|-------|-------|--------|
| `normal:1` | 0 | Normal EEG |
| `abnormal:1` | 1 | Abnormal EEG |

## Data Quality Notes

- Sex is not reliably available in this subset.
- Variable channel count (27-36) and sampling rate (250-512 Hz) across recordings; normalize before cross-recording analysis.
- Whole-recording global labels; local event patterns within recordings are not annotated.
- Train/dev split is encoded in directory path; respect the split for proper evaluation.

## Kernel Responsibilities

*Placeholder: Kernel responsibilities to be documented.*