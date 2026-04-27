# EEG: Depression rest

**Dataset**: `openneuro_ds003478` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003478
**Category**: Biological State | **Subjects**: 122 | **Files (Completed)**: 243 | **Channels**: 66 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG recording featuring alternating one-minute intervals of eyes-open and eyes-closed conditions in participants with varying scores on the Beck Depression Inventory (BDI). The study aims to identify EEG biomarkers of depression severity. Each session includes multiple alternating eyes-open and eyes-closed blocks, with admin markers indicating session boundaries. BioSemi system was used for data acquisition with 66 channels at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `a4805a785718ebe14178100eda6a1fb7cab2ce6a8163913ac1f7aca39ac64ba6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 29265 | event | raw | Eyes-open resting state block |
| `11` | 7196 | event | raw | Additional eyes-open block |
| `12` | 7141 | event | raw | Additional eyes-closed block |
| `13` | 3715 | event | raw | Block marker (eyes-open variant) |
| `14` | 3682 | event | raw | Block marker (eyes-closed variant) |
| `15` | 3624 | event | raw | Block marker (eyes-open variant) |
| `16` | 3574 | event | raw | Block marker (eyes-closed variant) |
| `17` | 472 | event | raw | Shorter transition or partial block |
| `175` | 1 | event | raw | Single occurrence marker |
| `2` | 29045 | event | raw | Eyes-closed resting state block |
| `240` | 4 | event | raw | Rare system marker |
| `255` | 20 | event | raw | System status or calibration marker |
| `3` | 15119 | event | raw | Secondary eyes-open block (alternate series) |
| `4` | 14964 | event | raw | Secondary eyes-closed block (alternate series) |
| `5` | 14738 | event | raw | Tertiary eyes-open block (alternate series) |
| `6` | 14530 | event | raw | Tertiary eyes-closed block (alternate series) |
| `boundary` | 109 | event | raw | Continuous data boundary marker |
| `keyboard0` | 1885 | admin | raw | Keyboard response marker - exclude |
| `keypad1` | 5 | admin | raw | Keypad response marker - exclude |
| `keypad2` | 5 | admin | raw | Keypad response marker - exclude |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Depression Status Binary Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`], remove_first_last_s = 10
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Control | 0 | BDI≤7 (no/minimal depression symptoms) |
  | Depressive | 1 | BDI≥13 (clinical depression) |
- **Super Meta Notes**: Labels derived from BDI scores in participants.tsv by threshold mapping. Kernel step: (1) Read BDI scores for each subject from participant metadata. (2) Apply threshold: BDI≤7 → Control (y=0), BDI≥13 → Depressive (y=1). (3) Extract 4-second segments from `Eyes Open` and `Eyes Closed` blocks, excluding first/last 10s per block. (4) Merge segment labels with subject-level BDI-derived depression labels.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Multi-class classification of depression status (cMDD vs pMDD vs None vs Control) using spatial correlations of EEG amplitude fluctuations during eyes-open and eyes-closed rest with BDI-derived group labels.
- **Kernel Notes**: Raw event IDs map to annotated labels: `1` → `Eyes Open`, `2` → `Eyes Closed` (verify via metadata). Remove first/last 10s of each eyes-open/eyes-closed block as artifact rejection. Each ~60s block yields ~10 usable 4-second segments after exclusion. Apply subject-level BDI thresholding consistently across all segments from same subject.

### Classical Task 2: Depression Subtype Multi-Class Classification (cMDD/pMDD/None/Control)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`], remove_first_last_s = 10
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Control | 0 | BDI≤7, no MDD history |
  | None | 1 | BDI≥13, depressive symptoms but no MDD history |
  | pMDD | 2 | BDI≥13, past MDD diagnosis |
  | cMDD | 3 | BDI≥13, current MDD diagnosis |
- **Super Meta Notes**: Labels derived from BDI scores and clinical interview data in participants.tsv. Kernel step: (1) Read BDI scores and clinical MDD status from participant metadata. (2) Apply mapping: BDI≤7 → Control (y=0); BDI≥13 + clinical interview → None (y=1, symptoms without MDD history), pMDD (y=2, past MDD), cMDD (y=3, current MDD). (3) Extract 4-second segments from `Eyes Open` and `Eyes Closed` blocks. (4) Merge segment labels with subject-level multi-class depression subtype labels.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Multi-class classification of depression status (cMDD vs pMDD vs None vs Control) using spatial correlations of EEG amplitude fluctuations during eyes-open and eyes-closed rest with BDI-derived group labels.
- **Kernel Notes**: Raw event IDs map to annotated labels: `1` → `Eyes Open`, `2` → `Eyes Closed`. Remove first/last 10s of each eyes-open/eyes-closed block as artifact rejection. Each ~60s block yields ~10 usable 4-second segments. Class imbalance expected: Control and cMDD may be overrepresented compared to None/pMDD subtypes. Apply subject-level multi-class mapping consistently across all segments.

### Normal Task 1: Eyes-Open vs Eyes-Closed State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`], remove_first_last_s = 10
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Eyes Open | 0 | Eyes-open resting state block |
  | Eyes Closed | 1 | Eyes-closed resting state block |
- **Evidence**: Plausible from paradigm; resting-state eyes-open/eyes-closed contrast is well-established in EEG literature. No specific DOI for this dataset yet.
- **Kernel Notes**: Raw event IDs map to annotated labels: `1` → `Eyes Open`, `2` → `Eyes Closed`. Standard binary contrast task for verifying preprocessing pipeline.

### Potential Task 1: Depression Severity Continuous Prediction (BDI Score Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`], remove_first_last_s = 10
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | BDI continuous | 0–63 | Beck Depression Inventory score per subject |
- **Super Meta Notes**: Kernel step: (1) Read BDI scores from participant metadata. (2) Assign continuous BDI score (0–63 scale) as regression target for all segments from same subject. (3) Train regression model to predict BDI from EEG features.
- **Evidence**: Supported by DOI 10.3389/fpsyt.2023.1132996 (BDI used for group assignment), extended to continuous prediction rather than categorical thresholding.
- **Kernel Notes**: BDI ranges 0–63; consider log-transform or normalization for regression target. Report Pearson correlation between predicted and actual BDI as primary metric.