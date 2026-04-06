# EEG: Depression rest

**Dataset**: `openneuro_ds003478` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003478
**Category**: Biological State | **Subjects**: 122 | **Files (Completed)**: 243
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recording featuring alternating one-minute intervals of eyes-open and eyes-closed conditions in participants with varying scores on the Beck Depression Inventory (BDI). The study aims to identify EEG biomarkers of depression severity. Each session includes multiple alternating eyes-open and eyes-closed blocks, with `Start and Finish` markers indicating session boundaries. STATUS is a BioSemi admin marker.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Eyes Open` | 368 (files) | event | raw | Eyes-open resting state block (~1 min) |
| `Eyes Closed` | 368 (files) | event | raw | Eyes-closed resting state block (~1 min) |
| `STATUS` | 243 (files) | admin | raw | BioSemi system status marker - exclude |
| `Start and Finish` | 184 (files) | admin | raw | Session start/end boundary marker - exclude |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Depression Status Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Control | 0 | BDI≤7 (no depression) |
  | Depressive | 1 | BDI≥13 (clinical depression) |
- **Super Meta Notes**: Derived from BDI scores in participants.tsv by threshold mapping (BDI≤7→Control, BDI≥13→Depressive). Kernel step: Read BDI scores from participant metadata, apply threshold, map each subject to binary label, merge with EEG segment labels.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Multi-class classification of depression status (cMDD vs pMDD vs None vs Control) using spatial correlations of EEG amplitude fluctuations during eyes-open and eyes-closed rest, with BDI-derived group labels.
- **Kernel Notes**: Extract 4-second segments from `Eyes Open` and `Eyes Closed` annotations. Remove initial/final 10s as artifact rejection (per paper methodology). Merge segment labels with BDI-derived depression labels from participants.tsv. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Depression Subtype Classification (cMDD/pMDD/None/Control)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Control | 0 | BDI≤7, no MDD history |
  | None | 1 | BDI≥13, depressive symptoms but no MDD history |
  | pMDD | 2 | BDI≥13, past MDD diagnosis |
  | cMDD | 3 | BDI≥13, current MDD diagnosis |
- **Super Meta Notes**: Derived from BDI scores and clinical interview data in participants.tsv. BDI≤7=Control; BDI≥13 with clinical interview subdivides into cMDD (current major depressive episode), pMDD (past MDD), None (depressive symptoms without MDD history). Kernel step: Read BDI scores and clinical status from participant metadata, apply multi-class mapping, assign labels to all segments.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Multi-class classification of depression status (cMDD vs pMDD vs None vs Control) using spatial correlations of EEG amplitude fluctuations during eyes-open and eyes-closed rest, with BDI-derived group labels.
- **Kernel Notes**: Extract 4-second segments from `Eyes Open` and `Eyes Closed` annotations. Remove initial/final 10s as artifact rejection. Merge segment labels with multi-class depression subtype labels derived from BDI scores and clinical interview data in participants.tsv.

## Data Quality Notes

- `STATUS` is BioSemi hardware marker - exclude.
- `Start and Finish` marks session boundaries - admin marker, exclude.
- Large dataset: 122 subjects, 243 files; subject-level BDI scores available for depression prediction.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review