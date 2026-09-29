# TUH EEG Artifact Corpus

**Dataset**: `tuh_eeg_artifact` | **Year**: 2020 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/html/tuh_eeg_artifact/
**Category**: Others | **Subjects**: 5000+ | **Files (Completed)**: 5000+ | **Channels**: 21-31 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

The TUH EEG Artifact Corpus is a large-scale collection of clinical EEG recordings from the Temple University Hospital (TUH) EEG database that has been annotated for common EEG artifacts. The dataset contains continuous scalp EEG recordings acquired during routine clinical evaluations of patients with suspected neurological disorders. Expert annotators labeled segments containing eye movements (eyem), muscle activity (musc), electrode artifacts (elec), electrode pops (elpp), and various combinations thereof, alongside background (bckg) periods free of these targeted artifacts. Recordings were obtained using standard 10-20 electrode placement with 21 to 31 channels at 250 Hz sampling rate using Nicolet or Xltek clinical amplifiers.

## File Scan Result

> **Kernel SHA256**: `cc3bb89e5bd9abac7e263b2261823dedca7480d3cb7b281fc7f12a11b151b144`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Classical Task 1: Binary Artifact vs Background Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | bckg | 0 | Background/non-seizure period |
  | eyem | 1 | Eye movement artifact |
  | musc | 1 | Muscle artifact |
  | elec | 1 | Electrode artifact |
  | elpp | 1 | Electrode pop artifact |
  | eyem_musc | 1 | Combined eye movement and muscle artifact |
  | musc_elec | 1 | Combined muscle and electrode artifact |
  | eyem_elec | 1 | Combined eye movement and electrode artifact |
- **Evidence**:
  - 10.1038/s41598-024-52551-0 — Binary classification of artifact present versus background using gradient-boosted trees achieving 93.95% accuracy; maps 11 event IDs into 2 classes (bckg=0, all artifact types=1)
- **Notes**: All artifact event IDs (eyem, musc, elec, elpp, eyem_musc, musc_elec, eyem_elec) are merged into a single positive class y=1, with bckg as the negative class y=0. The epoch parameters use 2-second windows with 50% overlap based on common artifact detection literature practices; these are inferred values as the reference does not specify exact windowing parameters.

### Classical Task 2: 13-class artifact type detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | bckg | 0 | Background/non-seizure period |
  | eyem | 1 | Eye movement artifact |
  | musc | 2 | Muscle artifact |
  | elec | 3 | Electrode artifact |
  | elpp | 4 | Electrode pop artifact |
  | eyem_musc | 5 | Combined eye movement and muscle artifact |
  | musc_elec | 6 | Combined muscle and electrode artifact |
  | eyem_elec | 7 | Combined eye movement and electrode artifact |
- **Evidence**:
  - 10.1109/EMBC48229.2022.9871413 — 13-class artifact classification with 5 individual artifacts, 7 combinations, and background; achieves 93.95% accuracy with 0.838 F1 using AutoML/TPOT on 4 temporal channels. Note: reference uses CHEW and SHIV which map to elpp in this dataset's locked meanings; combination labels differ (eyem_musc, musc_elec, eyem_elec match). Only 8 of 13 classes are available in this dataset's event IDs.
- **Notes**: The reference describes 13 classes but this dataset contains only 8 distinct artifact-related event IDs (bckg, eyem, musc, elec, elpp, eyem_musc, musc_elec, eyem_elec). The remaining 5 classes from the paper (CHEW, SHIV, and 4 additional combinations) are not present in the locked event meanings. The task is formulated as an 8-class classification using available labels. Segment length and overlap are inferred from standard artifact detection practice as exact values were not specified in the reference.



## Data Quality Notes

- All demographic and equipment metadata fields (age, amplifier, cap, handedness, sex) are completely missing from the scanned files, limiting subject-level analyses and reproducibility of recording conditions.
- The Event Structure table is empty in the file scan result, suggesting event annotations may be stored in external files (e.g., .lbl or .tse files) rather than embedded in the raw EEG headers, which is consistent with TUH database conventions.
- The 13-class task reference describes more artifact classes than are actually present in this dataset (8 vs. 13), indicating the dataset may represent a subset or earlier version of the full artifact corpus.
- Channel counts vary between 21-31 channels across recordings, reflecting different clinical montages used during acquisition; analyses should account for variable channel coverage.
- The dataset is derived from clinical recordings with heterogeneous patient populations and recording conditions, which may introduce confounding variables unrelated to the target artifacts.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
