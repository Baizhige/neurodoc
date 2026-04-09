# EEG During Mental Arithmetic Task

**Dataset**: `physionet_eegmat` | **Year**: 2018 | **URL**: https://physionet.org/content/eegmat/1.0.0/
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 23 | **Sampling Rate**: 500 Hz
**Manual Review**: Liu Peng

## Paradigm

Thirty-six healthy subjects (Subject00-Subject35, ages 16-26, predominantly female) completed a mental arithmetic task while EEG was recorded monopolarly using a Neurocom 23-channel system with Ag/AgCl electrodes (Zyma et al., 2019). Each subject contributed two files: a background resting-state recording (suffix _1.edf) and a mental arithmetic task recording (suffix _2.edf). During the mental arithmetic task, subjects performed serial subtraction (e.g., 3141 minus 42) while EEG was recorded. A separate `Count quality` field in `subject-info.csv` rates the subject's arithmetic performance as Good or Bad, providing a behavioral quality label.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Background EEG;Count Quality: Good` | 24 | event | raw | Resting-state (background) EEG recording, EEG quality was Good |
| `Background EEG;Count Quality: Bad` | 12 | event | raw | Resting-state (background) EEG recording, EEG quality was Bad |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 24 | event | raw | Mental arithmetic task EEG recording, task/EEG quality was Good |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 12 | event | raw | Mental arithmetic task EEG recording, task/EEG quality was Bad |


> 1. Event ID truncation: The Event IDs for background EEG and mental arithmetic task EEG are truncated in the scan (e.g., "Background EEG;Count Qua..."). The full Event IDs are inferred as "Background EEG;Count Quality" and "Mental Arithmetic Task EEG;Count Quality" based on the meaning description.
> 2. Meta Level verification: All events are currently marked as "raw" (native labels in raw data). Please verify if these Good/Bad quality labels are directly present in raw data or derived from raw recordings (if derived, Meta Level should be "super").
> 3. Count consistency check: The total counts (24/12 for Good/Bad) are read-only. Please verify if these counts match the actual number of recordings/subjects in the dataset.
> 4. Missing trial-level events: The current Event Structure only includes block-level resting-state/task EEG events. If the raw data contains trial-level stimulus/response events (e.g., arithmetic problem onset, subject's response), these events were missed in the scan and should be added if possible.
> 5. Quality definition clarification: The "Good/Bad" quality labels refer to EEG recording quality for resting-state, and task performance/EEG quality for mental arithmetic task, per the dataset's experimental design.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Age range: 16–26 years, mean age: approximately 18.33 years |
| `subject_sex` | missing | Males (M): 8, females (F): 28, predominantly female |
| `device` | missing | EEG was recorded using a 23-channel Neurocom monopolar system (XAI-MEDICA, Ukraine) with silver/silver chloride electrodes placed per the international 10–20 system, linked ear reference, 500 Hz sampling rate, 0.5–45 Hz bandpass filtering, 50 Hz notch filtering, and electrode impedance kept below 5 kΩ. |


## Tasks

### Classical Task 1: Mental Arithmetic Task vs Resting State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 0.5, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Background EEG;Count Quality: Bad` | 0 | Resting-state EEG |
  | `Background EEG;Count Quality: Good` | 0 | Resting-state EEG |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Mental arithmetic task |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | Mental arithmetic task |
- **Evidence**:
  
  - DOI: 10.13026/C2JQ1P — "The EEGMAT database contains 36 subjects with two 60-second EEG recordings each: background resting-state (_1.edf) and mental arithmetic task (_2.edf), with annotations encoding both condition type and count quality."
- **Kernel Notes**: 

  1. Epoch Parameter Rationale: 0-5s epoch window with 50% overlap (overlap=0.5) is a standard configuration for long-duration EEG segmentation, balancing temporal resolution and sample size, suitable for extracting features from 60-second resting-state and mental arithmetic task recordings.
  2. Label Mapping Rationale: Resting-state EEG events (both Good/Bad quality) are merged to class 0, mental arithmetic task EEG events (both Good/Bad quality) to class 1, as this task only distinguishes between recording conditions, not count quality.
  3. Evidence Rationale: DOI 10.13026/C2JQ1P is the official reference for the EEGMAT dataset, which directly validates this binary classification task.
  4. Quality Control: Exclude artifact-contaminated segments and verify subject count consistency (36 total subjects) before model training.
### Classical Task 2: Arithmetic Performance Quality Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 0.5, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor arithmetic performance |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good arithmetic performance |
- **Evidence**:
  
  - DOI: 10.13026/C2JQ1P — "EEGMAT dataset with annotations encoding condition type (resting-state/mental arithmetic) and count quality (Good/Bad), supporting arithmetic performance quality classification."
- **Kernel Notes**: 

  1. Epoch Parameter Rationale: 0-5s epoch window with 50% overlap (overlap=0.5) is a standard configuration for long-duration EEG segmentation, balancing temporal resolution and sample size, suitable for extracting features from 60-second mental arithmetic task recordings.
  2. Label Mapping Rationale: Only mental arithmetic task EEG events are used for this binary classification task: Bad quality events are mapped to class 0 (Poor arithmetic performance), Good quality events to class 1 (Good arithmetic performance), excluding all resting-state EEG events.
  3. Evidence Rationale: DOI 10.13026/C2JQ1P is the official reference for the EEGMAT dataset, which provides the count quality annotations for this task. The reference 10.1038/s41598 was removed as it does not explicitly use the EEGMAT dataset.
  4. Quality Control: Exclude artifact-contaminated segments, verify subject count consistency (36 total subjects), and ensure count quality labels are consistent across all subjects before model training.
### Potential Task 1: Mental Stress Classification During Arithmetic Task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0, target_events = [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 0 | Low-stress (good performers, derived from count quality: Good) |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | High-stress (poor performers, derived from count quality: Bad) |
- **Evidence**:
  
  - DOI: 10.1109/wccest66994.2025.11389948 — "classify mental stress levels (High-stress vs Low-stress) by segmenting EEG into 5-second epochs, applying k-means clustering on frequency band powers"
- **Kernel Notes**: 

  1. Task Rationale: Potential task for binary classification of mental stress during mental arithmetic task, derived from count quality annotations (Good=Low-stress, Bad=High-stress). No native raw stress labels exist in the EEGMAT dataset, so this task is marked as Potential.
  2. Epoch Parameter Rationale: 5-second segment length with 0% overlap (overlap=0.0) is selected to prevent data leakage, suitable for extracting frequency-domain features for stress classification, consistent with related research.
  3. Label Derivation Rationale: Stress labels are super meta labels derived from raw count quality annotations in mental arithmetic task events, not native raw stress labels.
  4. Quality Control: Exclude all resting-state EEG events and artifact-contaminated segments before analysis; verify subject count consistency (36 total subjects).
## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.
- EEG recordings contain potential ocular/muscular artifacts; apply artifact rejection (e.g., ICA) and standard preprocessing (filtering, re-referencing) before analysis.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
