# RS_TMSEEG_Data

**Dataset**: `openneuro_ds001849` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds001849
**Category**: Biological State | **Subjects**: 15 | **Files (Completed)**: 120 | **Channels**: 30 | **Sampling Rate**: 5000 Hz
**Manual Review**:

## Paradigm

Resting-state EEG data recorded in conjunction with Transcranial Magnetic Stimulation (TMS). Subjects were at rest with no active task while single-pulse TMS was delivered to three stimulation sites (DLPFC, M1, PPC) in both active and sham conditions. The R128 marker serves as the TMS pulse trigger for epoching; all condition labels must be derived from BIDS acquisition entities in filenames rather than event markers.

## File Scan Result

> **Kernel SHA256**: `2431a8f0a63df523216e52313865a716bfe9114d0b950d95fdba5d32db2fc9ba`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `R128` | 11961 | event | raw | TMS pulse trigger marker |
| `boundary` | 135 | admin | raw | Data segment boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: TMS-evoked potential classification: active vs sham
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`R128`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `R128` (active conditions: dlpfcactive, m1active, ppcactive) | 0 | Active TMS stimulation |
  | `R128` (sham conditions: dlpfcsham, m1sham, ppcsham) | 1 | Sham TMS stimulation |
- **Evidence**:
  - 10.1371/journal.pone.0216185 — The reference paper explicitly uses this dataset to classify TMS-evoked EEG potentials as site-specific neural responses versus artifacts, comparing active vs sham TMS conditions across three stimulation sites (DLPFC, M1, PPC). Classification is 2-class (active vs sham) with analysis focused on post-stimulus time windows, particularly components before ~80ms considered site-specific.
- **Notes**: The condition label (active vs sham) must be derived from the BIDS acquisition filename (e.g., `acq-dlpfcactive` vs `acq-dlpfcsham`) since no explicit condition labels exist in the events data. All `R128` events within a given file share the same condition label. The three active conditions (DLPFC, M1, PPC) are merged to y=0 and three sham conditions are merged to y=1, as the core classification is active vs sham TMS effect rather than site-specific classification.

### Classical Task 2: TMS-evoked potential classification: 6-class site x condition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`R128`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `dlpfcactive` | 0 | DLPFC active stimulation |
  | `dlpfcsham` | 1 | DLPFC sham stimulation |
  | `m1active` | 2 | M1 active stimulation |
  | `m1sham` | 3 | M1 sham stimulation |
  | `ppcactive` | 4 | PPC active stimulation |
  | `ppcsham` | 5 | PPC sham stimulation |
- **Evidence**:
  - 10.1371/journal.pone.0216185 — Freedberg et al. (2020) analyzes three stimulation sites (DLPFC, M1, PPC) each with active and sham conditions, yielding 6 distinct acquisition conditions. The paper's cosine similarity analysis compares across all site-condition combinations.
- **Notes**: Labels are derived from the BIDS `acq-` entity in filenames (e.g., `acq-dlpfcactive`), not from event markers. The `R128` event serves as the pulse trigger for epoching; the 6-class structure represents the full factorial design of site (DLPFC/M1/PPC) × condition (active/sham). This task requires the kernel to map each `R128` epoch to its corresponding acquisition condition based on the source file's BIDS entities. The 2-class active-vs-sham version is Task 1; this 6-class version captures the full experimental design as analyzed in the paper's cosine similarity comparisons.

## Data Quality Notes

- Very high sampling rate of 5000 Hz may require downsampling for efficient processing.
- Subject age, sex, and device metadata are completely missing from the dataset.
- Condition labels (active/sham and stimulation site) are not present in event data and must be parsed from BIDS filename entities.
- All `R128` events within a single file share the same condition, requiring file-level label assignment rather than event-level labeling.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
