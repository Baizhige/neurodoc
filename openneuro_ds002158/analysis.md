# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 949 | **Channels**: 63 | **Sampling Rate**: 5000 Hz
**Channels**: 63 | **Sampling Rate**: 5000 Hz
**Manual Review**: Liu Peng

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimates were collected using a visual analogue scale (VAS).

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `unknown` | 119 (files) | event | raw | Response onset (epoch anchor) - actual trial type may be in events.tsv `value` column; used as epoch anchor |


> 1. The experimental paradigm of the paper consists of an active/observation dual-condition design (lines 655–659 of the paper), with trials alternating within blocks (4 blocks per run, alternating between active and observation). The type of all trials is a fixed attribute of the experimental design and is not ‘unknown’;
> 2. The key events in the trial sequences described in the paper (start of gaze, start of stimulus, start of response, start of masking, start of confidence scale) are all clearly defined experimental marker events; there are no ‘unknown events’ serving as core epoch anchors or trial markers, and the ‘unknown’ Event ID has no basis in the paper.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Mean age = 24.6 ± 1.43 y |
| `subject_sex` | missing | Twenty-five healthy volunteers (12 females) |
| `device` | missing | EEG Recording: Data acquired via BrainVision system; MR-gradient artifacts removed via sliding window template subtraction. BCG artifacts removed using TP10 electrode (right mastoid) with semi-automatic procedure. Preprocessing included 1-10 Hz Butterworth filter (4th order zero-phase), [-0.2, 0.6] s epoching around response onset, common average reference, and ICA for artifact removal (EEGLAB/MATLAB). fMRI Recording: Structural (T1) and functional MRI data included; preprocessed using fMRIPrep with GLM analysis for BOLD signal estimation. |


## Tasks

### Classical Task 1: Confidence Regression from EEG during Speeded Perceptual Decisions
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `confidence`
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — EEG amplitude time-locked to first-order response onset used to model confidence via linear regression; multivariate EEG decoding derived single-trial confidence predictions.
  - DOI: misc meaning — y = continuous 0-1 confidence rating reported by participants after first-order response (active: button press; observation: virtual hand onset), derived from behavioral data.
- **Kernel Notes**: 
  1. Label Derivation: `confidence` is a super meta continuous scalar label stored in the `misc` route, derived from participants' post-decisional confidence ratings (0-1 continuous scale) collected in both active (committed decision) and observation (observed decision) conditions. It is not a native raw event ID. 
  2. Epoch Parameter Rationale: The [-0.2, 0.6] s epoch window is directly adopted from the dataset's official preprocessing pipeline, time-locked to first-order response onset (button press in active condition, virtual hand onset in observation condition), fully consistent with the reference paper's analysis. 
  3. Task Rationale: This regression task directly replicates the paper's core analysis: modeling single-trial confidence from EEG amplitude time-locked to response onset, using linear regression and multivariate EEG decoding for confidence prediction. 
  4. Exclusion Criteria: Exclude bad trials (defined in behavioral analysis) and active-condition trials with response times >500 ms (per experimental protocol). 
  5. Condition Inclusion: Includes both active and observation conditions, as reported in the manuscript.

## Data Quality Notes

- Event label `unknown` is a placeholder - actual trial type information may be in events.tsv `value` or `trial_type` columns.
- Confidence ratings stored in misc channel `confidence`; reaction times in `response_time`.
- High sampling rate (5000 Hz); significant downsampling required.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
