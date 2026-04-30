# EEG: 3-Stim Auditory Oddball and Rest in Parkinson's

**Dataset**: `openneuro_ds003490` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003490
**Category**: Sensory/Response | **Subjects**: 50 | **Files (Completed)**: 75 | **Channels**: 67 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A three-stimulus auditory oddball task (standard tones, target tones requiring button-press response, and novel distractor tones) combined with resting-state (eyes open and eyes closed) EEG recordings in Parkinson's disease patients and age-matched healthy controls. The study aims to identify auditory P300 and mismatch negativity differences between PD patients and controls. BioSemi STATUS markers (S 85, S255) are system admin events to be excluded.

## File Scan Result

> **Kernel SHA256**: `7eed99c23187737b1771b37bd447699725593af250d425a9cb95c01999b5a4d4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 2280 | event | raw | Unknown - not observed in available BIDS files; likely oddball task stimulus |
| `S  2` | 2280 | event | raw | Unknown - not observed in available BIDS files; likely oddball task stimulus |
| `S  3` | 2252 | event | raw | Trial phase onset: Eyes Closed (1Hz trigger marker for eyes-closed resting state) |
| `S  4` | 2254 | event | raw | Trial phase onset: Eyes Closed (1Hz trigger marker for eyes-closed resting state, alternating with S  3) |
| `S 85` | 1 | event | raw | Unknown - not observed in available BIDS files; likely oddball task marker |
| `S200` | 2230 | event | raw | Unknown - not observed in available BIDS files; likely oddball task stimulus |
| `S201` | 10166 | event | raw | Unknown - not observed in available BIDS files; likely oddball task stimulus |
| `S202` | 2229 | event | raw | Unknown - not observed in available BIDS files; likely oddball task stimulus |
| `S255` | 1 | event | raw | Unknown - not observed in available BIDS files; likely oddball task marker |
| `boundary` | 75 | admin | raw | Data segment boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: PD vs Control classification (3-stim oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 2.0 s, target_events = [`S200`, `S201`, `S202`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S200 | 0 | Standard stimulus (frequent non-target) |
  | S201 | 1 | Target stimulus (requires button-press response) |
  | S202 | 2 | Novel distractor stimulus (rare non-target) |
- **Evidence**:
  - 10.1016/j.clinph.2017.11.023 — Original publication (PMID:29294412) describing 3-stimulus auditory oddball paradigm with S200/S201/S202 event structure and ±2s epochs for P300/MMN analysis.
  - 10.21528/cbic2023.027 — CBIC 2023 replication confirming same paradigm parameters and event coding.
- **Notes**: Events S200/S201/S202 are present in the EEG file headers and pre-scan counts but do not appear in the available BIDS events.tsv files for task-Rest sessions. The dataset_description.json and README confirm the full study includes '3-Stim Auditory Oddball' alongside Rest, but only task-Rest files were converted to BIDS format in this release. The high pre-scan counts and header annotations confirm these events belong to the oddball task data. For task execution, the kernel must access these events from the raw EEG file annotations (e.g., .set file annotations) rather than BIDS events.tsv.

### Potential Task 1: PD vs Control from resting EEG (Group classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | PD | 0 | Parkinson's disease |
  | Group | CTL | 1 | Control (healthy) |
- **Evidence**:
- **Notes**: Resting-state EEG segmentation task for subject-level group classification. Continuous 2-second windows with 50% overlap are extracted from the eyes-closed resting state data (marked by S 3/S 4 alternating triggers at 1Hz). Each window inherits the participant's Group label from participants.tsv (PD vs CTL). This is a B3 archetype using native info field with no kernel derivation required. The epoch parameters are inferred from standard resting-state biomarker segmentation practices since the dataset provides continuous resting recordings without trial structure.

### Potential Task 2: PD Medication ON vs OFF Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sess1_Med`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sess1_Med | ON | 0 | PD patient on dopaminergic medication |
  | sess1_Med | OFF | 1 | PD patient off dopaminergic medication |
- **Evidence**:
  - 10.1016/j.clinph.2017.11.023 — Original paper reports ON vs OFF medication comparison within PD group; participants counterbalanced with ~1 week separation between sessions
- **Notes**: This task uses session-level medication state from participants.tsv. The sess1_Med column encodes ON/OFF for PD patients (CTL subjects have 'n/a'). For classification, only PD subjects with valid ON/OFF labels are included. The counterbalanced design (sess1=ON/sess2=OFF or sess1=OFF/sess2=ON) enables within-subject medication state classification. Segmentation with 2s windows and 50% overlap is standard for continuous resting-state EEG biomarker extraction. The epoch parameters are inferred from typical biomarker analysis pipelines for Parkinson's disease EEG.

### Potential Task 3: Age regression from resting EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 48–84 (years) | Continuous age from participants.tsv; complete for all 50 subjects (25 PD, 25 CTL) |
- **Evidence**:
  - participants.tsv — age column complete (N=50, range 48–84 years), numeric dtype suitable for regression
  - README — confirms 25 Parkinson patients and 25 matched controls with age-matched design
  - dataset_description.json — confirms resting EEG task ("EEG: 3-Stim Auditory Oddball and Rest in Parkinson's")
- **Notes**: Standard segmentation approach for age prediction from continuous resting-state EEG. 2-second windows with 50% overlap generate sufficient samples from ~588s recordings while preserving stationarity. Age is a native participants.tsv column requiring no kernel derivation.

### Potential Task 4: Sex classification from resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | Male | 0 | Male participant |
  | sex | Female | 1 | Female participant |
- **Evidence**:
  - participants.tsv — Complete categorical column with 32 Male and 18 Female entries across 50 subjects
  - dataset_description.json — Confirms dataset is "EEG: 3-Stim Auditory Oddball and Rest in Parkinson's" with resting-state data
- **Notes**: Binary sex classification from continuous resting-state EEG using 2-second non-overlapping segments with 50% overlap. The task uses the native `sex` column from participants.tsv (archetype B3), requiring no kernel derivation. Standard approach for EEG-based demographic prediction benchmarks.

## Data Quality Notes

- The dataset contains a discrepancy between the BIDS events.tsv files and the raw EEG file annotations: the oddball task events (S200, S201, S202) are present in EEG headers but missing from available BIDS events.tsv files, which only cover task-Rest sessions.
- Only resting-state EEG files were converted to BIDS format in this release; the 3-stimulus auditory oddball task data exists in raw EEG files but was not BIDS-converted.
- The `device` field is completely missing from info metadata, limiting hardware-specific quality assessments.
- The `sess1_Med` field is only partial (25/50 subjects), which may affect the medication ON/OFF classification task sample size.
- S 3 and S 4 event meanings are inferred from context as eyes-closed resting state 1Hz trigger markers; their exact alternation pattern should be verified during manual review.
- Boundary markers (75 total) indicate data segment boundaries that must be excluded from continuous analysis to avoid edge artifacts.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
