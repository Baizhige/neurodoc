# CHB-MIT Scalp EEG Database

**Dataset**: `physionet_chbmit` | **Year**: 2010 | **URL**: https://physionet.org/content/chbmit/1.0.0/
**Category**: Biological State | **Subjects**: 23 | **Files (Completed)**: 686 | **Channels**: 23 | **Sampling Rate**: 256 Hz
**Manual Review**: Zhida Shang

## Paradigm

Twenty-three pediatric subjects (22 original cases plus chb24 added later; 5 males aged 3-22, 17 females aged 1.5-19, with chb24 age/sex unknown) with intractable seizures were monitored at Children's Hospital Boston following withdrawal of anti-seizure medication to evaluate surgical candidacy (Shoeb & Guttag, 2010). Note: case chb21 was recorded 1.5 years after chb01 from the same female subject. Long-term continuous EEG was recorded from 23 scalp channels (bipolar montage following the 10-20 system) at 256 Hz with 16-bit resolution. The dataset contains 686 EEG files, of which 129 contain one or more seizures, for a total of 198 annotated seizures. Seizure onset and offset times are documented in per-subject summary text files (`chbNN-summary.txt`); the kernel parses these to create `seizure` annotations spanning each ictal period.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `seizure` | 198 | event | raw | Seizure period (onset to offset, variable duration) |


> Files without seizures have no annotations; these ictal-free recordings serve as the negative (interictal) class.
> **Manual Review Note**: Seizure count corrected from 182 to 198 by human reviewer (Zhida Shang); subjects corrected from 22 to 23 (chb24 adds one subject). Kernel should re-verify total seizure count and subject list on next scan.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Binary seizure detection (ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: , target_events = [`seizure`, `(no annotation)`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seizure` | 1 | Ictal (seizure period) |
  | `(no annotation)` | 0 | Interictal + Post-intal + Preictal (seizure-free) |
- **Evidence**:
  - DOI: 10.1016/j.bspc.2024.107379 — Uses 2-second epochs for ictal vs non-seizure classification on CHB-MIT
  - DOI: 10.1038/s41598 — 025-18479-9 — Binary seizure detection (ictal vs non-seizure) on CHB-MIT
  - DOI: 10.1038/s41598 — 025-98389-y — 5-second windows for binary seizure vs no-seizure classification
- **Kernel Notes**: 

### Classical Task 2: Seizure prediction (preictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: , target_events = [`preictal`, `interictal`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `preictal` | 1 | Period 30 min before seizure onset |
  | `interictal` | 0 | Seizure-free period >=4 hours before/after seizure |
- **Evidence**:
  - DOI: 10.1088/1741 — 2552/ada0e5 — Uses 10 s intervals with 90% overlap for preictal vs interictal classification; preictal = 30 min before seizure, interictal >=4 hours away
  - DOI: 10.1109/access.2020.2976866 — Seizure prediction with preictal (30-90 min before seizure) vs interictal using 30-second STFT windows
- **Kernel Notes**: 

### Classical Task 3: Three-class seizure state classification (preictal vs ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: , target_events = [`ictal`, `preictal`, `interictal`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ictal` | 1 | Seizure period (annotated seizure interval) |
  | `preictal` | 0 | 20 min before seizure onset * |
  | `interictal` | 2 | Remaining seizure-free periods |
- **Evidence**:
  - DOI: 10.54525/bbmd.1526069 — Three-class classification (pre-seizure/ictal/non-seizure) using 4-second EEG spectrogram windows with 3-second overlap on CHB-MIT
- **Kernel Notes**: 

## Data Quality Notes

- Severe class imbalance: the majority of recordings are seizure-free; balance by undersampling interictal or using cost-sensitive learning.
- Channel count varies: most files have 23 channels; some cases include 24 or 26 channels (extra ECG or vagal nerve stimulus channels); exclude non-EEG channels.
- Patient-specific model training is recommended; cross-patient generalization is difficult.
- Subject chb24 has unknown age and sex.
- Age range: 1.5-22 years (pediatric); EEG morphology differs significantly from adult norms.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
