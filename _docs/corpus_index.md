# EEG Corpus — Complete Documentation
> **53 completed datasets** · generated 2026-05-07
> Regenerate: completed-only index generated from `dataset_document/*/analysis.md`

---
## Table of Contents

### 🤜 Action/Output
- [A dataset recorded during development of a tempo-based brain-computer music interface](#a-dataset-recorded-during-development-of-a-tempo-based-brain-computer-music-interface)
- [A Large EEG Motor Imagery Dataset for EEG-BCI](#a-large-eeg-motor-imagery-dataset-for-eeg-bci)
- [BCI Competition IV Dataset 1 (Motor Imagery, Uncued Classifier Application)](#bci-competition-iv-dataset-1-motor-imagery-uncued-classifier-application)
- [BCI Competition IV Dataset 2a (4-Class Motor Imagery)](#bci-competition-iv-dataset-2a-4-class-motor-imagery)
- [BCI Competition IV Dataset 2b (Left/Right Hand Motor Imagery)](#bci-competition-iv-dataset-2b-leftright-hand-motor-imagery)
- [BCI Competition IV Dataset 4 (ECoG Finger Flexion Prediction)](#bci-competition-iv-dataset-4-ecog-finger-flexion-prediction)
- [EEG Dataset for Cursor BCI (Meng 2019)](#eeg-dataset-for-cursor-bci-meng-2019)
- [EEG Datasets of Stroke Patients (Motor Imagery)](#eeg-datasets-of-stroke-patients-motor-imagery)
- [EEG Motor Movement/Imagery Database](#eeg-motor-movementimagery-database)
- [ERP-Based Brain-Computer Interface Recordings](#erp-based-brain-computer-interface-recordings)
- [High-Gamma EEG Motor Imagery Dataset](#high-gamma-eeg-motor-imagery-dataset)
- [Kaggle BCI Challenge (INRIA) Dataset](#kaggle-bci-challenge-inria-dataset)
- [Motor Imagery vs Rest - Low-Cost EEG System](#motor-imagery-vs-rest-low-cost-eeg-system)
- [Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment](#multimodal-eeg-and-fnirs-biosignal-acquisition-during-motor-imagery-tasks-in-patients-with-orthopedic-impairment)
- [OpenBMI Motor Imagery EEG Dataset](#openbmi-motor-imagery-eeg-dataset)
- [Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task](#real-time-eeg-feedback-on-alpha-power-lateralization-leads-to-behavioral-improvements-in-a-covert-attention-task)
- [SHU Motor Imagery EEG Dataset](#shu-motor-imagery-eeg-dataset)
- [The BMI-HDEEG dataset 3](#the-bmi-hdeeg-dataset-3)
- [The BMI-HDEEG dataset 4](#the-bmi-hdeeg-dataset-4)

### 👁️ Sensory/Response
- [Go-nogo categorization and detection task](#go-nogo-categorization-and-detection-task)
- [Visual Oddball Task (256 channels)](#visual-oddball-task-256-channels)

### 🧠 High-level Mental
- [A dataset recorded during development of an affective brain-computer music interface: calibration session](#a-dataset-recorded-during-development-of-an-affective-brain-computer-music-interface-calibration-session)
- [Auditory evoked potential EEG-Biometric dataset](#auditory-evoked-potential-eeg-biometric-dataset)
- [Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging](#disentangling-the-origins-of-confidence-in-speeded-perceptual-judgments-through-multimodal-imaging)
- [EEG During Mental Arithmetic Task](#eeg-during-mental-arithmetic-task)
- [Face processing EEG dataset for EEGLAB](#face-processing-eeg-dataset-for-eeglab)

### 🔀 Complex Applied
- [Healthy Brain Network (HBN) EEG - Release 1](#healthy-brain-network-hbn-eeg-release-1)
- [Healthy Brain Network (HBN) EEG - Release 10](#healthy-brain-network-hbn-eeg-release-10)
- [Healthy Brain Network (HBN) EEG - Release 11](#healthy-brain-network-hbn-eeg-release-11)
- [Healthy Brain Network (HBN) EEG - Release 2](#healthy-brain-network-hbn-eeg-release-2)
- [Healthy Brain Network (HBN) EEG - Release 3](#healthy-brain-network-hbn-eeg-release-3)
- [Healthy Brain Network (HBN) EEG - Release 4](#healthy-brain-network-hbn-eeg-release-4)
- [Healthy Brain Network (HBN) EEG - Release 5](#healthy-brain-network-hbn-eeg-release-5)
- [Healthy Brain Network (HBN) EEG - Release 6](#healthy-brain-network-hbn-eeg-release-6)
- [Healthy Brain Network (HBN) EEG - Release 7](#healthy-brain-network-hbn-eeg-release-7)
- [Healthy Brain Network (HBN) EEG - Release 8](#healthy-brain-network-hbn-eeg-release-8)
- [Healthy Brain Network (HBN) EEG - Release 9](#healthy-brain-network-hbn-eeg-release-9)

### 🩺 Biological State
- [CAP Sleep Database](#cap-sleep-database)
- [CHB-MIT Scalp EEG Database](#chb-mit-scalp-eeg-database)
- [Ear-EEG Sleep Monitoring 2019 (EESM19)](#ear-eeg-sleep-monitoring-2019-eesm19)
- [Ear-EEG Sleep Monitoring 2023 (EESM23)](#ear-eeg-sleep-monitoring-2023-eesm23)
- [EEG Meditation Study](#eeg-meditation-study)
- [HMC Sleep Staging Database](#hmc-sleep-staging-database)
- [sleepdata_shhs](#sleepdata_shhs)
- [Sleep-EDF Database Expanded](#sleep-edf-database-expanded)
- [TUH EEG Abnormal Corpus](#tuh-eeg-abnormal-corpus)
- [TUH EEG Corpus (Base)](#tuh-eeg-corpus-base)
- [TUH EEG Events Corpus](#tuh-eeg-events-corpus)
- [TUH EEG Seizure Corpus](#tuh-eeg-seizure-corpus)
- [TUH EEG Slowing Corpus](#tuh-eeg-slowing-corpus)
- [UCD Sleep Apnea Database](#ucd-sleep-apnea-database)
- [Ultra High-Density EEG - Interictal Migraine and Controls](#ultra-high-density-eeg-interictal-migraine-and-controls)

### 📦 Others
- [TUH EEG Artifact Corpus](#tuh-eeg-artifact-corpus)

---

# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2018 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 18 | **Files (Completed)**: 165 | **Channels**: 19 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants used EEG self-regulation to control the tempo of music in a tempo-based brain-computer music interface (BCMI). One condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. Each labeled event spans a full 20-second music clip interval. The dataset contains multiple runs per participant.

## File Scan Result

> **Kernel SHA256**: `59196c175ac3d8d41fdc5ed8d3a687afd6a5cc92ebd61dca68083721485beae3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1` | 1275 | event | raw | Lower alpha condition: participants are instructed to lower their alpha levels to modulate the tempo of music |
| `2` | 1250 | event | raw | Raise alpha condition: participants are instructed to increase their alpha levels to modulate the tempo of music |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 2-class alpha-state BCMI classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `1` | 0 | Lower alpha condition |
  | `2` | 1 | Raise alpha condition |
- **Evidence**:
  - sub-01_task-run2_events.json — defines event `1` as `Lower alpha` and event `2` as `Raise alpha`
  - README — states that the dataset contains EEG from a music-based BCI in which participants intentionally modulated music tempo, and that each music clip is 20 s long
  - events.tsv scan — confirms 2525 total labeled events across the dataset, with 1275 instances of `1` and 1250 instances of `2`
- **Notes**: This is the most direct task supported by the released BIDS event metadata. All non-empty events have duration exactly 20 s, so long-event decoding over the full labeled interval is the most natural formulation. This task should take precedence over demographic segmentation tasks because it reflects the actual experimental manipulation.

### Potential Task 1: sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — sex field complete for all 18 subjects with class imbalance (M=14, F=4)
- **Notes**: Continuous EEG segmentation (4s windows, 50% overlap) applied across all BCMI runs per subject. Binary classification of subject sex from resting/task-continuous EEG. Class imbalance present (M=14, F=4 out of 18 subjects). The segment_length and overlap values are standard defaults for continuous EEG segmentation with no task-specific reference guidance. This is a weak subject-trait task compared with the explicit alpha-state labels available in the event tables.

### Potential Task 2: Binned-Age Classification from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — age column complete for N=18, range 18–28, sample values [23, 24, 28, 20, 19, 26, 20]
- **Notes**: The kernel must derive binary binned labels from the native age field using a median split at approximately 22–23 years (median of 18–28 range ≈ 23). This is a derived classification variant of the continuous age regression task; the kernel discretizes the continuous age into two balanced classes for segment-level classification. Segmentation produces fixed-length windows with 50% overlap; no event alignment is used. This remains an auxiliary demographic task, not the core BCMI task.

## Data Quality Notes

- Twenty-two event files are empty (no events recorded), leaving 143 files with usable event data.
- Non-empty event files do contain valid event labels: trial_type `1` (Lower alpha) and `2` (Raise alpha), with 2525 total labeled events across the dataset.
- Device metadata is completely missing from the dataset; equipment information must be inferred from other sources.
- There is a discrepancy in subject count between the metadata (18 subjects) and dataset_description.json which mentions 19 healthy participants.
- Class imbalance is present in sex classification (14 male, 4 female), which may affect model training and evaluation.
- All non-empty events have duration exactly 20 s, matching the README description that each music clip lasts 20 s.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# A Large EEG Motor Imagery Dataset for EEG-BCI

**Dataset**: `figshare_largemi` | **Year**: 2018 | **URL**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698
**Category**: Action/Output | **Subjects**: 13 | **Files (Completed)**: 73 | **Channels**: 22 | **Sampling Rate**: 200/1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Thirteen subjects (A–M) participated in multiple EEG recording sessions in this large EEG-BCI dataset. The published dataset includes 60 hours of EEG from 13 participants across 75 sessions. EEG was recorded with 22 channels total: 19 standard 10/20 EEG leads, 2 ground leads (A1, A2), and 1 synchronization channel (X3). The main BCI dataset contains over 60,000 motor imagery examples collected in four interaction paradigms, while an additional NoMT paradigm was recorded as a baseline / consistency-check condition.

The paradigms are:

CLA: 3-state synchronous MI — left hand, right hand, and a passive state.
HaLT: 6-state synchronous MI — left hand, right hand, left leg, right leg, tongue, and a passive state.
5F: 5-state finger MI — imagery of individual finger movements on one hand.
FreeForm: self-paced voluntary left- and right-hand key presses, designed to study EEG activity preceding voluntary motor execution rather than standard cue-based imagery.
NoMT: visual-stimulus-only, no-motor-response baseline sessions. These sessions were similar to HaLT in visual presentation, but participants were explicitly instructed not to respond to the visual signals and instead passively watched the screen throughout. No mental imagery states were present (0St).

For the synchronous paradigms, each recording session began with an initial relaxation period and then contained three 15-minute interaction segments separated by breaks. In the cue-based trials, a visual action signal was presented for 1 s, followed by a 1.5–2.5 s pause, for an average trial length of about 3 s. In CLA, HaLT, and 5F, subjects performed the instructed imagery once during the 1-second cue interval. In contrast, FreeForm was self-paced rather than cue-triggered: participants voluntarily pressed left- or right-hand keys at arbitrary times while EEG was recorded.

## File Scan Result

> **Kernel SHA256**: `a8832789924f840bc44bd3b38edc6fc29bb5dfedf3c46c596f9f27524bc69c51`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `5F: index finger MI` | 3308 | event | raw | Index finger motor imagery cue (5F paradigm) |
| `5F: middle finger MI` | 3716 | event | raw | Middle finger motor imagery cue (5F paradigm) |
| `5F: pinkie MI` | 3561 | event | raw | Pinky finger motor imagery cue (5F paradigm) |
| `5F: ring finger MI` | 3578 | event | raw | Ring finger motor imagery cue (5F paradigm) |
| `5F: thumb MI` | 3908 | event | raw | Thumb motor imagery cue (5F paradigm) |
| `CLA: left hand MI` | 4624 | event | raw | Left-hand motor imagery cue (CLA paradigm) |
| `CLA: passive state` | 4178 | event | raw | Passive state instruction (CLA paradigm) |
| `CLA: right hand MI` | 4624 | event | raw | Right-hand motor imagery cue (CLA paradigm) |
| `FREEFORM: left hand MI` | 1066 | event | raw | Left-hand motor imagery onset (FreeForm paradigm) |
| `FREEFORM: right hand MI` | 1061 | event | raw | Right-hand motor imagery onset (FreeForm paradigm) |
| `HaLT: left hand MI` | 4631 | event | raw | Left-hand motor imagery cue (HaLT paradigm) |
| `HaLT: left leg MI` | 4564 | event | raw | Left leg motor imagery cue (HaLT paradigm) |
| `HaLT: passive state` | 4560 | event | raw | Passive state instruction (HaLT paradigm) |
| `HaLT: right hand MI` | 4593 | event | raw | Right-hand motor imagery cue (HaLT paradigm) |
| `HaLT: right leg MI` | 4446 | event | raw | Right leg motor imagery cue (HaLT paradigm) |
| `HaLT: tongue MI` | 4847 | event | raw | Tongue motor imagery cue (HaLT paradigm) |
| `NoMT: left hand cue` | 1114 | event | raw | Visual cue for left hand (NoMT baseline) |
| `NoMT: left leg cue` | 1113 | event | raw | Visual cue for left leg (NoMT baseline) |
| `NoMT: passive cue` | 1103 | event | raw | Visual cue for passive state (NoMT baseline) |
| `NoMT: right hand cue` | 1114 | event | raw | Visual cue for right hand (NoMT baseline) |
| `NoMT: right leg cue` | 1076 | event | raw | Visual cue for right leg (NoMT baseline) |
| `NoMT: tongue cue` | 1178 | event | raw | Visual cue for tongue (NoMT baseline) |
| `admin: marker-91` | 63 | admin | raw | unkown |
| `admin: marker-92` | 31 | admin | raw | unkown |
| `admin: marker-99` | 172 | admin | raw | unkown |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: CLA-Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`CLA: left hand MI`, `CLA: right hand MI`, `CLA: passive state`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `CLA: left hand MI` | 0 | Left-hand motor imagery (CLA paradigm, marker 1) |
  | `CLA: right hand MI` | 1 | Right-hand motor imagery (CLA paradigm, marker 2) |
  | `CLA: passive state` | 2 | Passive/idle state (CLA paradigm, marker 3) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 2: Halt-Paradigm Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`HaLT: left hand MI`, `HaLT: right hand MI`, `HaLT: passive state`, `HaLT: left leg MI`, `HaLT: right leg MI`, `HaLT: tongue MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `HaLT: left hand MI` | 0 | Left-hand motor imagery (HaLT paradigm, marker 1) |
  | `HaLT: right hand MI` | 1 | Right-hand motor imagery (HaLT paradigm, marker 2) |
  | `HaLT: passive state` | 2 | Passive/idle state (HaLT paradigm, marker 3) |
  | `HaLT: left leg MI` | 3 | Left-leg motor imagery (HaLT paradigm, marker 4) |
  | `HaLT: right leg MI` | 4 | Right-leg motor imagery (HaLT paradigm, marker 6) |
  | `HaLT: tongue MI` | 5 | Tongue motor imagery (HaLT paradigm, marker 5) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 3: 5F-Paradigm Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`5F: thumb MI`, `5F: index finger MI`, `5F: middle finger MI`, `5F: ring finger MI`, `5F: pinkie MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `5F: thumb MI` | 0 | Thumb finger imagery (5F paradigm, marker 1) |
  | `5F: index finger MI` | 1 | Index finger imagery (5F paradigm, marker 2) |
  | `5F: middle finger MI` | 2 | Middle finger imagery (5F paradigm, marker 3) |
  | `5F: ring finger MI` | 3 | Ring finger imagery (5F paradigm, marker 4) |
  | `5F: pinkie MI` | 4 | Pinkie finger imagery (5F paradigm, marker 5) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 4: Binary Left vs. Right Hand Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`FREEFORM: left hand MI`, `FREEFORM: right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `FREEFORM: left hand MI` | 0 | Left-hand motor imagery (FREEFORM paradigm) |
  | `FREEFORM: right hand MI` | 1 | Right-hand motor imagery (FREEFORM paradigm) |
- **Evidence**:
  - 10.1109/tnsre.2022.3186442 — Binary classification of left vs right hand motor imagery from the figshare_largemi dataset (the paper not claim specific paradigm, this task is for FREEFORM)
- **Notes**: 

## Data Quality Notes

- Multiple paradigms in one dataset; **always filter by protocol type before analysis** (use file path to identify protocol: `CLA`, `HaLT`, `FREEFORM`, `5F`, `NoMT`).
- Sampling rates differ: 200 Hz (5F protocol), 1000 Hz (CLA/HaLT/FREEFORM); process separately or resample to a common rate.
- Subject demographics: 13 subjects (A-M), 9 female / 4 male, age ranges 20-35.
- NoMT sessions have `none` annotations; exclude from MI analysis or use as rest class.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# BCI Competition IV Dataset 1 (Motor Imagery, Uncued Classifier Application)

**Dataset**: `bcic_iv_1` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_1.html
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 14 | **Channels**: 59 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Seven subject datasets are provided for two-class motor imagery without feedback in an asynchronous (self-paced) BCI paradigm (BCI Competition IV, 2008). The two movement classes differed per subject, selected from left hand, right hand, or foot imagery. A calibration phase used visual arrow cues with 4-second imagery intervals. The evaluation phase used acoustic cues (spoken words) with variable-duration imagery (1.5-8 s) and rest periods (1.5-8 s), simulating a realistic asynchronous BCI scenario. Both calibration and evaluation `.mat` files are provided per subject; class names are available in the `.mat` structure, whereas event positions are provided in the calibration files (`mrk.pos`) but not in the evaluation files. Later competition materials noted that three datasets (`c`, `d`, and `e`) were artificially generated.

## File Scan Result

> **Kernel SHA256**: `be708ccaca35d8c1b12185468ac158b74a29c36fa810b3dc09073853c425cde5`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `foot` | 200 | event | raw | Cue onset for foot motor imagery (subjects assigned foot class) |
| `left` | 500 | event | raw | Cue onset for left-hand motor imagery |
| `right` | 300 | event | raw | Cue onset for right-hand motor imagery (subjects assigned right class) |


> Class labels vary per subject: some subjects have `left` + `right`, others have `left` + `foot`. Event names are loaded dynamically from `nfo.className` in the `.mat` file. Counts shown are approximate per calibration file.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | BrainAmp MR plus amplifiers; Ag/AgCl electrode cap |


## Tasks

### Classical Task 1: Three-Class Motor Imagery Classification (Standard Calibration)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, target_events = [`foot`, `left`, `right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left` | 0 | Left hand motor imagery (subject-specific class 1) |
  | `right` | 1 | Right hand motor imagery (subject-specific class 2, when paired with left) |
  | `foot` | 2 | Foot motor imagery (subject-specific class 2, when paired with left) |
- **Evidence**:
  - 10.1016/j.neuroimage.2010.03.022 — - tmin=0s tmax=4s relative to cue onset for 4-second imagery intervals during calibration
  - 10.3389/fnins.2010.00198 — - calibration phase used visual arrow cues with 4-second imagery intervals
- **Notes**: Two-class labels are subject-specific (left+right vs. left+foot); verify class names per file from `nfo.classes`. Only calibration data with fixed 4-second cue/imagery trials should be used. The primary cue-locked imagery window is 0-4 s after cue onset. A baseline-inclusive variant may use -0.5-4.0 s to include 0.5 s of pre-cue fixation baseline for offline baseline correction; this is a preprocessing/windowing variant of the same calibration task, not a separate task definition. y values encode all three possible event IDs for documentation, but actual binary classification should use the subject-specific class pair in each file.

## Data Quality Notes

- Two-class labels vary per subject (left+right vs. left+foot); verify class names per file from the `eegunity_description` field or the `.mat` `nfo.className` field.
- No age or sex information is available in the public release.
- Evaluation phase has variable trial durations and idle periods; the idle state is unlabeled and should be identified by absence of annotations.
- High sampling rate (1000 Hz); memory-intensive; downsampling recommended.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# BCI Competition IV Dataset 2a (4-Class Motor Imagery)

**Dataset**: `bcic_iv_2a` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2a.pdf
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 18 | **Channels**: 25 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

Nine subjects (A01-A09) performed four-class cued motor imagery (BCI Competition IV, 2008): left hand, right hand, feet, and tongue. Each session contained 6 runs of 48 trials each (288 trials per session), balanced across 4 classes (72 trials per class). A fixation cross preceded each trial, followed by a visual arrow cue indicating the imagery class, and a 4-second imagery period. Short resting intervals separated trials. Each subject was recorded in two sessions: a training session (suffix `T.gdf`) with event labels, and an evaluation session (suffix `E.gdf`) with initially unknown labels replaced by kernel-loaded `.mat` companion files. EEG was recorded from 22 channels (standard 10-20, sensorimotor focus) plus 3 bipolar EOG channels (filtered 0.5-100 Hz, notch at 50 Hz).

## File Scan Result

> **Kernel SHA256**: `489182843c6974d9f77d2a7ccd1f1bad91a5f3eb1d01dfc7e15b3321e4eb8803`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Cue onset foot (class 3)` | 1375 | event | raw | Feet motor imagery cue |
| `Cue onset left (class 1)` | 1224 | event | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | 1224 | event | raw | Right-hand motor imagery cue |
| `Cue onset tongue (class 4)` | 1656 | event | raw | Tongue motor imagery cue |
| `Eye movements` | 18 | admin | raw | Artifactual eye movement event |
| `Idling EEG (eyes closed)` | 17 | admin | raw | Resting state with eyes closed |
| `Idling EEG (eyes open)` | 17 | admin | raw | Resting state with eyes open |
| `Rejected trial` | 488 | admin | raw | Trial rejected by experimenter |
| `Start of a new run` | 153 | admin | raw | Run boundary marker |
| `Start of a trial` | 4896 | admin | raw | Trial-onset fixation cross (pre-cue marker) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`, `Cue onset foot (class 3)`, `Cue onset tongue (class 4)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
  | `Cue onset foot (class 3)` | 2 | Feet motor imagery |
  | `Cue onset tongue (class 4)` | 3 | Tongue motor imagery |
- **Evidence**:
  - DOI: official website — Official BCI Competition IV Dataset 2a description defines four-class MI (left hand, right hand, feet, tongue) as benchmark task with 4s imagery window from cue onset.
  - DOI: 10.1109/tnnls.2018.2789927 — CNN trained on 0.5-2.5s MI period after cue onset.
  - DOI: 10.1109/tnsre.2022.3156076 — SincNet hybrid achieves 74.26% accuracy.
- **Notes**: 

### Potential Task 1: Binary Motor Imagery - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

- Rejected trials (variable per subject/session) should be excluded from analysis.
- EOG channels present; apply artifact rejection or regression before motor imagery classification.
- Evaluation files initially contain `Cue unknown (class 783)` entries that the kernel replaces with proper class labels from `.mat` companion files; verify companion file presence.
- Class balance is enforced by design (72 trials per class per session); minor imbalance may arise from rejected trials.
- Subject age range: 17-26 years; 7 female, 2 male subjects.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# BCI Competition IV Dataset 2b (Left/Right Hand Motor Imagery)

**Dataset**: `bcic_iv_2b` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2b.pdf
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 46 | **Channels**: 6 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

Nine subjects (B01-B09) performed two-class cued motor imagery of the left and right hand (BCI Competition IV, 2008). Only 3 bipolar EEG channels over the sensorimotor cortex (C3, Cz, C4) and 3 EOG channels were recorded (0.5-100 Hz, notch at 50 Hz). Each subject underwent 5 sessions over two days: sessions 1-2 without feedback, sessions 3-5 with BCI feedback. Each session contained multiple runs of ~60-80 trials per class. A fixation cross preceded each trial, followed by a visual left/right arrow cue for 1.25 s, then a 4-second (begin at 3 s after cue) imagery period with optional BCI cursor feedback. Evaluation sessions (suffix `E.gdf`) have unknown cue labels that the kernel resolves from companion `.mat` files.

## File Scan Result

> **Kernel SHA256**: `f8318b338ce28894e9eb4e28cfcd174ed8fe180a3c6730d7756c660f2518fadc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `BCI feedback (continuous)` | 1440 | admin | raw | BCI feedback period (sessions 3-5 only) |
| `Cue onset left (class 1)` | 4460 | event | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | 4460 | event | raw | Right-hand motor imagery cue |
| `Eye blinks` | 263 | admin | raw | Eye artifact marker |
| `Eye rotation` | 263 | admin | raw | Eye artifact marker |
| `Horizontal eye movement` | 53 | admin | raw | Eye artifact marker |
| `Idling EEG (eyes closed)` | 43 | admin | raw | Resting state with eyes closed |
| `Idling EEG (eyes open)` | 43 | admin | raw | Resting state with eyes open |
| `Rejected trial` | 1253 | admin | raw | Experimenter-rejected trial |
| `Start of a new run` | 252 | admin | raw | Run boundary marker |
| `Start of a trial` | 6240 | admin | raw | Trial-onset fixation cross (pre-cue) |
| `Vertical eye movement` | 323 | admin | raw | Eye artifact marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | a device with Ag/AgCl electrode |

## Tasks

### Classical Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1109/tnsre.2022.3156076 — Segmented BCI IV-2b data into four overlapping 2-second time windows for MI classification (−0.5s to 1.5s  , 0s to 2s, 0.5 sto 2.5s , and 1 to 3s)
  - DOI: 10.1109/tnsre.2023.3241846 — Used epoched data from 3rd to 7th second relative to cue onset for left vs right hand MI (3s to  7s, start from ”Start of a trial“ event)
  - DOI: 10.3389/fnins.2020.00918 — Trained CNN classifiers on sessions 1-3 for inter-subject continuous decoding of left vs right hand MI (0.8s ~ 2.8 s, from "Cue onset")
- **Notes**: 

## Data Quality Notes

- Only 3 EEG channels (C3, Cz, C4): very limited spatial resolution; spatial filtering (CSP) is critical.
- EOG channels present; apply artifact regression before MI classification.
- Feedback sessions (3-5) may show learning effects; sessions 1-2 provide cleaner baseline.
- Evaluation files use `Cue unknown (class 783)` initially; companion `.mat` files are required by the kernel to resolve labels.
- Subject demographics: B01-B09, ages 20-32, mixed sex.
- 46 files total across 9 subjects x 5 sessions; some sessions may have extra evaluation runs.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# BCI Competition IV Dataset 4 (ECoG Finger Flexion Prediction)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.pdf
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 53/67/69 (48/62/64 ECoG + 5 misc) | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

BCI Competition IV Dataset 4 is an ECoG finger flexion prediction dataset, not a motor imagery dataset. Three epilepsy patients performed actual visually cued finger movements with ECoG recorded from 48-64 subdural electrodes over sensorimotor cortex. Visual cues named one of five fingers, and subjects repeatedly flexed the cued finger during a 2 s cue period while finger-position amplitudes were recorded with a data glove as five continuous target signals. The public release contains one MATLAB file per subject with `train_data` containing 400 s of labeled ECoG, `train_dg` containing the five training finger-position traces, and `test_data` containing 200 s of ECoG with labels withheld. Cue timing and per-cue labels are not included, so `train_segment` and `test_segment_onset` are administrative markers rather than movement-class events.

## File Scan Result

> **Kernel SHA256**: `a70a20c716fdf52ce64804f37490c4b4369921ba52a7542cb2c262c233299254`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `test_segment_onset` | 3 | event | raw | Onset of the 200 s public test segment; finger-position labels are withheld in the release, so `finger1`-`finger5` are NaN in this segment. |
| `train_segment` | 3 | event | raw | Start of the 400 s labeled training segment containing valid continuous finger-position traces in `finger1`-`finger5`. |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `finger1` | native (raw misc in EEG file) | raw | Continuous thumb flexion trace from `train_dg` column 1; valid in `train_segment`, NaN in the public test segment. |
| `finger2` | native (raw misc in EEG file) | raw | Continuous index-finger flexion trace from `train_dg` column 2; valid in `train_segment`, NaN in the public test segment. |
| `finger3` | native (raw misc in EEG file) | raw | Continuous middle-finger flexion trace from `train_dg` column 3; valid in `train_segment`, NaN in the public test segment. |
| `finger4` | native (raw misc in EEG file) | raw | Continuous ring-finger flexion trace from `train_dg` column 4; valid in `train_segment`, NaN in the public test segment. |
| `finger5` | native (raw misc in EEG file) | raw | Continuous little-finger flexion trace from `train_dg` column 5; valid in `train_segment`, NaN in the public test segment. |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Not provided in the public competition release. |
| `amplifier` | complete | Acquisition amplifier reported by the official dataset description. |
| `bandpass_hz` | complete | Acquisition band-pass range reported in the competition description. |
| `cap` | complete | Subdural clinical ECoG grid/array rather than a scalp EEG cap. |
| `data_glove_lag_sec` | complete | Approximate glove-to-amplifier lag reported by the official description. |
| `data_glove_native_rate_hz` | complete | Native sampling rate of the original finger-position glove measurements. |
| `data_glove_release_rate_hz` | complete | Sampling rate of the released ECoG and supersampled glove traces. |
| `dataset` | complete | Dataset identifier written by the kernel. |
| `device` | complete | Acquisition stack summarized from the public competition description. |
| `ecog_channel_count` | complete | Number of neural ECoG channels before the five finger misc channels are appended. |
| `finger_label_channels` | complete | Names of the five continuous glove-label channels materialized by the kernel. |
| `finger_label_names` | complete | Finger-name order corresponding to `finger1` through `finger5`. |
| `finger_label_valid_segment` | complete | Segment in which the glove labels are valid and non-NaN. |
| `handedness` | missing | Not provided in the public competition release. |
| `recording_type` | complete | Invasive ECoG recording, not scalp EEG. |
| `reference` | complete | Reference/ground scheme described for the original acquisition before rereferencing. |
| `sampling_rate_hz` | complete | Final sample rate of the released ECoG recordings. |
| `sex` | missing | Not provided in the public competition release. |
| `source_file` | complete | Original public MATLAB container file for the subject. |
| `subject_id` | complete | Subject identifier inferred from the MATLAB filename. |
| `test_duration_sec` | complete | Duration of the unlabeled public test segment. |
| `test_label_policy` | complete | Explains why the finger misc channels are NaN during the public test segment. |
| `train_duration_sec` | complete | Duration of the labeled training segment. |


## Tasks

### Classical Task 1: Continuous Finger Flexion Regression — Thumb
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger1` | continuous thumb flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger1` corresponds to the thumb trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; thumb prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a thumb-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger1` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 2: Continuous Finger Flexion Regression — Index Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger2` | continuous index-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger2` corresponds to the index-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; index-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as an index-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger2` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 3: Continuous Finger Flexion Regression — Middle Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger3` | continuous middle-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger3` corresponds to the middle-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; middle-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a middle-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger3` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 4: Continuous Finger Flexion Regression — Ring Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger4` | continuous ring-finger flexion trace (a.u.; present in labels/submission format, excluded from official final scoring) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger4` corresponds to the ring-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation page notes that the ring finger was excluded from the final averaged score, although the trace remains part of the five-column data-glove target format.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. The ring-finger trace exists in the released label structure and prediction format, but it was excluded from the official final average score. It should not be treated as a ring-vs-other-fingers classification task.

### Classical Task 5: Continuous Finger Flexion Regression — Little Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger5` | continuous little-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger5` corresponds to the little-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; little-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a little-finger-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger5` data-glove trace over the labeled 400 s `train_segment`.

## Data Quality Notes

- The public competition `.mat` files contain no cue-onset markers and no per-cue finger-class event stream, even though the experimental protocol used visual finger cues.
- `train_segment` and `test_segment_onset` are administrative segmentation markers only; they must not be treated as motor imagery labels or movement-class labels.
- This is ECoG from subdural clinical grids, not scalp EEG. No standard 10-20 montage applies, and the official description notes that channel order was scrambled.
- Actual ECoG channel counts are sub1 = 62, sub2 = 48, sub3 = 64. With the five kernel-created finger misc channels, the MNE raws have 67, 53, and 69 channels.
- Test-segment finger labels are withheld in the original public `.mat` competition release; the kernel uses NaN for `finger1`-`finger5` in the 200 s test segment so supervised loaders ignore those samples. Official true labels were later made available on the competition results page for offline evaluation.
- Data-glove measurements were sampled at 25 Hz and super-sampled to 1000 Hz in the released `train_dg`; the official description reports an approximately 37 ms glove/amplifier lag.
- The five target traces are thumb, index, middle, ring, and little finger flexion. The ring finger trace is present in the data and prediction format, but was excluded from the official final average score.
- Age, sex, handedness, anatomical electrode names, and subject-specific electrode locations are not available in the released files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# EEG Dataset for Cursor BCI (Meng 2019)

**Dataset**: `figshare_meng2019` | **Year**: 2019 | **URL**: https://doi.org/10.6084/m9.figshare.7959572
**Category**: Action/Output | **Subjects**: 42 | **Files (Completed)**: 126 | **Channels**: 62/64 | **Sampling Rate**: 100/128 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed a one-dimensional cursor BCI task using mental imagery in three experiments (Meng et al., 2019). EEG was recorded from 62/64 channels. Subjects imagined motor or other mental activities to move a cursor toward a target positioned Left or Right Side. The dataset covers three experiments (Exp1, Exp2, Exp3); Exp1 and Exp2 used a Neuroscan SynAmps RT amplifier, while Exp3 used a Biosemi Active Two system. The paradigm recorded both target intent events (what the subject was trying to do) and result events (what the BCI decoded), enabling analysis of mental imagery decoding accuracy.

## File Scan Result


> **Kernel SHA256**: `611ecb0061d5421f7b3f18f42bbe84280cb89edb888a676dde2ba49e90154dd2`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Sampled (3/126 files)
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `result cursor minus` | ~166 | event | raw | BCI decoded - direction (feedback signal) |
| `result cursor plus` | ~168 | event | raw | BCI decoded + direction (feedback signal) |
| `target cursor minus` | ~183 | event | raw | Target positioned below center; subject imagines left movement |
| `target cursor plus` | ~182 | event | raw | Target positioned above center; subject imagines right movement |
| `target rest` | ~365 | event | raw | Target at center; subject imagines neutral/rest state |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | missing | N/A |
| `device` | missing | Exp1 and Exp2 used a Neuroscan SynAmps RT amplifier, while Exp3 used a Biosemi Active Two system. |

## Tasks

### Potential Task 1: Two-class motor imagery cursor direction decoding (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 1.5 s, tmax = 4.5 s, target_events = [`target cursor plus`, `target cursor minus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `target cursor plus` | 1 | Left-hand motor imagery (cursor moves up/+) |
  | `target cursor minus` | 0 | Right-hand motor imagery (cursor moves down/-) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2019.00128 — This paper analyzes the same figshare dataset from 42 subjects performing left/right hand motor imagery to control a cursor BCI, evaluating behavioral performance and ERD/ERS patterns.
- **Notes**: 

## Data Quality Notes

- Sex information is not available in the dataset metadata.
- Three experiments (Exp1, Exp2, Exp3) use different amplifier systems; process per-experiment or normalize across systems.
- Subject count is not explicitly stated; estimate from unique subject folders in file paths.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# EEG Datasets of Stroke Patients (Motor Imagery)

**Dataset**: `figshare_stroke` | **Year**: 2022 | **URL**: https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5
**Category**: Action/Output | **Subjects**: 50 | **Files (Completed)**: 50 | **Channels**: 33 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

Fifty stroke patients (sub-01 to sub-50) performed a cued left/right hand motor imagery task (ZhenTec NT1 amplifier, Ag/AgCl cap). EEG was recorded from 29 scalp channels plus 2 EOG channels (HEOL, VEOR). Each recording session contained 20 trials per hand class (20 left + 20 right = 40 trials total). Each trial comprised three phases: an instruction period (visual cue indicating the target hand), a motor imagery period (subject imagines the indicated hand movement), and a break period (rest). The dataset is designed to study MI-based BCI performance in stroke rehabilitation. Subject ages range from 31 to 77 years (median 57.5), with predominantly right-handed subjects (48/50) and a male-majority cohort (39M/11F).

## File Scan Result

> **Kernel SHA256**: `11759583348321d136db5d087841f6b3abe68cf483378b87d118cc3a59ca49b8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Break beginning - Left hand` | 1000 | admin | raw | Rest/break period following a left-hand trial |
| `Break beginning - Right hand` | 1000 | admin | raw | Rest/break period following a right-hand trial |
| `Instruction beginning - Left hand` | 1000 | admin | raw | Instruction cue onset for left-hand trial |
| `Instruction beginning - Right hand` | 1000 | admin | raw | Instruction cue onset for right-hand trial |
| `Motor imagery beginning - Left hand` | 1000 | event | raw | Left-hand motor imagery period onset |
| `Motor imagery beginning - Right hand` | 1000 | event | raw | Right-hand motor imagery period onset |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | also showed in task-motor-imagery_eeg.json |


## Tasks

### Classical Task 1: Motor Imagery Classification (Left vs. Right Hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Motor imagery beginning - Left hand`, `Motor imagery beginning - Right hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Motor imagery beginning - Left hand` | 0 | Left-hand motor imagery |
  | `Motor imagery beginning - Right hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - 10.1016/j.compbiomed.2025.111285 — Uses figshare stroke dataset (50 subjects) for left/right hand motor imagery classification, segmenting EEG trials from 1 to 4 seconds post-cue with multi-domain features and SCSO-optimized BLS classifier achieving 96.41% accuracy. Deviation: tmin=1.0s used to avoid residual VEPs (kernel default tmin=0.0s).
  - 10.48084/etasr.15300 — Uses figshare stroke motor imagery dataset (50 patients, 40 trials each) to classify left-hand vs right-hand motor imagery EEG signals using CNN, LSTM, and hybrid CNN-LSTM models.
- **Notes**: tmin=0.0s marks MI onset precisely per event markers. Paper DOI: 10.1016/j.compbiomed.2025.111285 uses tmin=1.0s to exclude early VEP components from the preceding instruction cue — mark deviation. Standard paradigm window is 0–4 s per the dataset design (instruction → motor imagery → break).

## Data Quality Notes

- Stroke patient population: highly variable EEG quality due to neurological deficits and movement impairments.
- Very small per-subject trial count (20 per class); cross-subject aggregation is essential.
- EOG channels present (HEOL, VEOR); apply artifact rejection or EOG regression before MI classification.
- Two left-handed subjects (sub-06, sub-15); consider excluding or annotating for lateralization analyses.
- Age range 31-77 years (median 57.5); age-related EEG changes may confound MI classification.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# EEG Motor Movement/Imagery Database

**Dataset**: `physionet_eegmmidb` | **Year**: 2009 | **URL**: https://physionet.org/content/eegmmidb/1.0.0/
**Category**: Action/Output | **Subjects**: 109 | **Files (Completed)**: 1526 | **Channels**: 64 | **Sampling Rate**: 160 Hz | **Manual Review**: anonymous for review

## Paradigm

One hundred and nine volunteers performed a series of motor movement and motor imagery tasks, recorded with 64 EEG electrodes (international 10-10 system) at 160 Hz using the BCI2000 system (Schalk et al., 2004). Each subject completed 14 runs (R01-R14): two baseline runs (eyes open and eyes closed), and twelve task runs organized in three repeating cycles of four run types. Task runs alternate between real movements and mental imagery of the same movements. Two movement classes are used: left/right fist, and both fists/both feet. Events T0 (rest), T1, and T2 are annotated within each run; T1/T2 meanings differ by run number.

## File Scan Result

> **Kernel SHA256**: `bd1ed7ea5b310949f1bb2ce29057964e4e25db94ffb6a393129b948b562b88b8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Baseline, eyes closed` | 109 | event | raw | Eyes closed resting state baseline recording |
| `Baseline, eyes open` | 109 | event | raw | Eyes open resting state baseline recording |
| `Imagine Opening Both Fists Movement` | 2465 | event | raw | Motor imagery cue: open both fists |
| `Imagine Opening Feet Movement` | 2455 | event | raw | Motor imagery cue: open/move both feet |
| `Imagine Opening Left Fist Movement` | 2480 | event | raw | Motor imagery cue: open left fist |
| `Imagine Opening Right Fist Movement` | 2438 | event | raw | Motor imagery cue: open right fist |
| `Open Both Feet Movement` | 2469 | event | raw | Real movement cue: open both feet |
| `Open Both Fists Movement` | 2440 | event | raw | Real movement cue: open both fists |
| `Open Left Fist Movement` | 2471 | event | raw | Real movement cue: open left fist |
| `Open Right Fist Movement` | 2456 | event | raw | Real movement cue: open right fist |
| `Rest` | 19675 | event | raw | Rest period / trial baseline marker |
| `T1` | 2 | admin | raw | Task cue type 1 (meaning varies by run) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 4-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Imagine Opening Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery |
  | `Imagine Opening Both Fists Movement` | 2 | Both-fists motor imagery |
  | `Imagine Opening Feet Movement` | 3 | Both-feet motor imagery |
- **Evidence**:
  - DOI: 10.1109/TNSRE.2022.3186442 — 4-class motor imagery classification (left/right fist, both fists, both feet) using the PhysioNet EEG Motor Imagery Database with tmin=0.0s and tmax=3.0s
- **Notes**: 

### Potential Task 1: 4-Class Motor Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Open Left Fist Movement`, `Open Right Fist Movement`, `Open Both Fists Movement`, `Open Both Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Open Left Fist Movement` | 0 | Left-fist movement |
  | `Open Right Fist Movement` | 1 | Right-fist movement |
  | `Open Both Fists Movement` | 2 | Both-fists movement |
  | `Open Both Feet Movement` | 3 | Both-feet movement |
- **Evidence**:

- **Notes**: 

### Potential Task 2: 4-Class Motor Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Open Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Open Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Open Both Fists Movement`, `Imagine Opening Feet Movement`, `Open Both Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery (R04/08/12) |
  | `Open Left Fist Movement` | 0 | Left-fist real movement (R03/07/11) |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery (R04/08/12) |
  | `Open Right Fist Movement` | 1 | Right-fist real movement (R03/07/11) |
  | `Imagine Opening Both Fists Movement` | 2 | Both-fists motor imagery (R06/10/14) |
  | `Open Both Fists Movement` | 2 | Both-fists real movement (R05/09/13) |
  | `Imagine Opening Feet Movement` | 3 | Both-feet motor imagery (R06/10/14) |
  | `Open Both Feet Movement` | 3 | Both-feet real movement (R05/09/13) |
- **Evidence**:

- **Notes**: 

### Potential Task 3: Binary Left vs. Right Fist Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery |
- **Evidence**:

- **Notes**: 

### Potential Task 4: Both Fists vs. Both Feet Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Both Fists Movement`, `Imagine Opening Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Both Fists Movement` | 0 | Both-fists motor imagery (R06/10/14) |
  | `Imagine Opening Feet Movement` | 1 | Both-feet motor imagery (R06/10/14) |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

- Age and sex information are not available in the public metadata.
- Known data quality issues: several subjects have noisy recordings; EEG.physionet.org community notes suggest subjects S088, S089, S092, S100, S104 may have unusual recordings.
- T1/T2 event meaning **changes by run number**; always filter by run before assigning class labels.
- `Baseline` (T0) events in task runs are rest periods and should be excluded from MI classification targets.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# ERP-Based Brain-Computer Interface Recordings

**Dataset**: `physionet_erpbci` | **Year**: 2014 | **URL**: https://physionet.org/content/erpbci/1.0.0/
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 245 | **Channels**: 70 | **Sampling Rate**: 2048 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants spelled characters using a standard 6x6 matrix speller while EEG was recorded with a BioSemi ActiveTwo system (64 EEG + 2 earlobe reference + 4 EOG channels) at 2048 Hz (Riccio et al., 2013). Each row and column of the 6x6 character matrix was randomly intensified for 100 ms with a 50 ms gap (150 ms SOA). Each row/column flashed approximately 20 times per trial, and participants mentally counted target character flashes to sustain attention. The kernel processes raw row/column flash events and classifies each as `seen` (target - the row or column containing the attended character flashed) or `unseen` (non-target) for both rows and columns separately.

## File Scan Result

> **Kernel SHA256**: `e0a11f6326ce932b8d655a71963420e1b77d7b011e8ab2e0e3a96f36b3fac752`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `seen (column)` | 2391 | event | raw | Target column flash (attended character's column lit up) |
| `seen (row)` | 2005 | event | raw | Target row flash (attended character's row lit up) |
| `unseen (column)` | 11819 | event | raw | Non-target column flash |
| `unseen (row)` | 9614 | event | raw | Non-target row flash |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | No subject age demographic information is publicly available in this dataset. |
| `sex` | missing | No subject sex demographic information is publicly available in this dataset. |
| `device` | missing | Recordings collected via BioSemi ActiveTwo EEG system (2048 Hz sampling rate), with 64 EEG channels, 2 earlobe references, and 4 EOG channels; software re-referencing required for full CMRR. |


## Tasks

### Classical Task 1: P300 Target vs. Non-Target Classification in Matrix Speller
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (column)`, `seen (row)`, `unseen (column)`, `unseen (row)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seen (row)` | 1 | Target row flash (attended character's row intensified) |
  | `seen (column)` | 1 | Target column flash (attended character's column intensified) |
  | `unseen (row)` | 0 | Non-target row flash |
  | `unseen (column)` | 0 | Non-target column flash |
- **Evidence**:
  - 10.13026/C2101S — Dataset page describes ERP-based BCI recordings from a P300 matrix speller paradigm where participants spell characters by focusing on target flashes; row/column intensifications can be classified as target (attended) or non-target.
- **Notes**: Verify event ID mapping from events.tsv. Extract epochs centered on each row/column intensification event (±0.1/0.8s window). Combine `seen (row)` and `seen (column)` as positive class (y=1), `unseen (row)` and `unseen (column)` as negative class (y=0). EOG channels should be excluded from features. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Row vs. Column P300 Speller Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (column)`, `seen (row)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seen (row)` | 0 | Target flash occurred in a row |
  | `seen (column)` | 1 | Target flash occurred in a column |
- **Evidence**:

- **Notes**: Use intersection of identified target row and target column to determine spelled character.

## Data Quality Notes

- Very high sampling rate (2048 Hz); consider downsampling to 256 or 512 Hz for computational efficiency.
- Class imbalance: 2 target flashes vs. 10 non-target flashes per sequence (1:5 ratio); balance with oversampling or cost-sensitive learning.
- EOG channels present (4 channels); apply artifact rejection before P300 classification.
- Age and sex information are not available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# High-Gamma EEG Motor Imagery Dataset

**Dataset**: `other_highgammadataset` | **Year**: 2017 | **URL**: https://gin.g-node.org/robintibor/high-gamma-dataset/src/master/data
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 28 | **Channels**: 133 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The High-Gamma Dataset contains EEG recordings from 14 healthy participants performing four cued motor execution conditions: left-hand finger tapping, right-hand finger tapping, bilateral toe clenching, and rest. EEG was recorded in a high-frequency-optimized laboratory using a 128-electrode WaveGuard Original cap and a NeurOne amplifier at 5 kHz. For the analyses reported in Schirrmeister et al. (2017), the data were resampled to 250 Hz and restricted to 44 electrodes over the motor cortex. Each participant completed about 13 runs, yielding roughly 963 trials on average, with the first 11 runs used for training and the last 2 runs used for testing. A key feature of this dataset is its suitability for studying movement-related activity in the high-gamma range, which makes it particularly valuable for evaluating EEG decoding methods based on deep neural networks.

## File Scan Result

> **Kernel SHA256**: `aaa8004eb70a2a4a6a4911a2a6e522e48652708968ab483419634579fb3402f5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `feet` | 1405 | event | raw | Bilateral toe clenching motor execution cue |
| `left_hand` | 1404 | event | raw | Left-hand finger tapping motor execution cue |
| `rest` | 1404 | event | raw | Rest period cue (no movement) |
| `right_hand` | 1404 | event | raw | Right-hand finger tapping motor execution cue |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left_hand`, `right_hand`, `feet`, `rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_hand` | 0 | Left-hand motor imagery |
  | `right_hand` | 1 | Right-hand motor imagery |
  | `feet` | 2 | Feet motor imagery |
  | `rest` | 3 | Rest but same cue |
- **Evidence**:
  - DOI: 10.1002/hbm.23730 — Uses the High-Gamma Dataset (HGD) with 14 subjects performing four-class motor imagery (left hand, right hand, feet, rest) across two sessions per subject, evaluating deep ConvNets against FBCSP baseline for EEG decoding.
- **Notes**: 

### Classical Task 2: Left vs. Right Hand Motor Imagery Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left_hand`, `right_hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_hand` | 0 | Left-hand motor imagery |
  | `right_hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1002/hbm.23730 — Deep learning evaluation on HGD includes left/right hand motor imagery decoding as key binary classification subtask.
- **Notes**: 

## Data Quality Notes

- No exact age or sex information available in the public release.
- Two sessions per subject (train/test): separate by filename suffix for proper evaluation if needed.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Kaggle BCI Challenge (INRIA) Dataset

**Dataset**: `kaggle_inria` | **Year**: 2015 | **URL**: https://www.kaggle.com/c/inria-bci-challenge
**Category**: Action/Output | **Subjects**: 26 | **Files (Completed)**: 130 | **Channels**: 58 | **Sampling Rate**: 200 Hz | **Manual Review**: anonymous for review

## Paradigm

Twenty-six subjects (ages 20-37) performed a P300-based BCI feedback task using a 56-channel Ag/AgCl EEG cap at 200 Hz (plus 1 EOG channel and 1 FeedBackEvent channel, total 58). The task was a P300 matrix speller in which subjects attended to a target character while row/column flashes elicited P300 responses. Feedback was provided after each trial: subjects received either a correct ("good") or incorrect ("wrong") response to the P300 classifier output. Each session file (CSV format) contains one session for one subject; each subject has 5 sessions. Feedback event times are encoded in the dedicated `FeedBackEvent` channel; labels ("good" or "wrong") are sourced from a companion `TrainLabels.csv` file. Test sessions have unknown labels.

## File Scan Result

> **Kernel SHA256**: `b7b6d30d084aef11930444b66f20db1a72b9b071faa81dd4d08634281a8d276f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `good feedback to P300` | 3850 | event | raw | Feedback event: BCI output was correct |
| `unknown feedback to P300` | 3400 | event | raw | Feedback event: label unknown (test sessions) |
| `wrong feedback to P300` | 1590 | event | raw | Feedback event: BCI output was incorrect |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (130/133) | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Feedback Error Detection (Good vs Wrong)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.3 s, target_events = [`good feedback to P300`, `wrong feedback to P300`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `good feedback to P300` | 0 | Correct BCI feedback (classifier output matched user intent) |
  | `wrong feedback to P300` | 1 | Incorrect BCI feedback (classifier output differed from user intent) |
- **Evidence**:
  - 10.1109/TBCAS.2022.3215962 — Validates EEGNet accelerator on ERN dataset with epochs [0, 1.3]s post feedback for binary classification of correct vs. incorrect BCI feedback.
  - 10.1016/j.inffus.2024.102316 — Uses ERN dataset from Kaggle BCI Challenge for adversarial filtering evaluation with epochs [0, 1.3]s post feedback onset.
  - 10.1109/ACCESS.2024.3467154 — Evaluates DCAE defense on ERN dataset with tmin=0s, tmax=1.3s, bandpass [1,40]Hz.
  - 10.1088/1741-2552/aace8c — Evaluates EEGNet on ERN paradigm with epochs [0, 1.25]s post feedback.
- **Notes**: FeedBackEvent channel (column 57) encodes feedback onset times; match labels from TrainLabels.csv by feedback ID (e.g., S01_Sess01_FB001). Exclude sessions with `unknown feedback to P300` (test set). Bandpass filter 1-40Hz recommended per paper preprocessing. (replaces Potential Task 1 from original analysis.md)


## Data Quality Notes

- Data stored as CSV files (not standard EEG format); MNE loader produces unsupported-file-type warnings that are non-fatal.
- 58 channels include 56 EEG + 1 EOG + 1 FeedBackEvent auxiliary channel; remove FeedBackEvent and EOG before training.
- Many sessions have only unknown labels (test set); only sessions with known labels in TrainLabels.csv can be used for supervised learning.
- Age range 20-37 available from dataset metadata; no sex information.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50 | **Channels**: 15 | **Sampling Rate**: 125 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants without prior BCI experience performed a motor imagery vs rest protocol during EEG recording with a low-cost consumer-grade EEG system. The protocol included one familiarization run (RUN0), with actual dominant-hand grasping movements and rest trials, followed by four formal MI vs rest runs (RUN1-RUN4) whose protocol design specified 20 trials per condition per run. OpenViBE/OVTK annotations mark trial phases, condition cues, baseline periods, and session boundaries; markers named as feedback should be interpreted as protocol phase markers because no real feedback was presented to participants. The study evaluates offline motor-imagery detection and demonstrates the feasibility of affordable EEG hardware for MI-BCI research.

## File Scan Result

> **Kernel SHA256**: `28da8b02b8c556ef27d3c8fd26e82bcaa29756b38d38475b254a7c9394307bb0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `OVTK_GDF_Correct` | 697 | admin | raw | OpenViBE protocol tag; often co-occurs with `OVTK_GDF_Incorrect` and is not usable as a correct-feedback label |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Trial preparation phase onset: fixation cross |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session boundary: end of session |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial end marker |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | OpenViBE trial sub-stage marker after the task period; no actual feedback was presented in this experiment |
| `OVTK_GDF_Incorrect` | 697 | admin | raw | OpenViBE protocol tag; often co-occurs with `OVTK_GDF_Correct` and is not usable as an error-feedback label |
| `OVTK_GDF_Right` | 845 | event | raw | Condition cue: motor imagery of dominant-hand grasping in RUN1-RUN4; actual grasping cue in RUN0 |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial onset marker |
| `OVTK_GDF_Tongue` | 845 | event | raw | Condition cue: rest/idle condition; this OpenViBE/GDF label does not indicate tongue imagery in this dataset |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Run-level baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Run-level baseline period stop |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Auditory cue marker |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Session boundary: experiment start |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Session boundary: experiment stop |
| `OVTK_StimulationId_Train` | 48 | admin | raw | System marker: training/calibration |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Derived from the `age` column of `participants.tsv`; range 20-30 years |
| `sex` | complete | Derived from the `gender` column of `participants.tsv`; `M` = 6, `F` = 4 |
| `device` | complete | Data in Brief reports EEG acquisition with Electro-Cap System II connected to OpenBCI Cyton + Daisy; this device information is not repeated in each per-run `eeg.json` |
| `participant_id` | complete | Native `participants.tsv` column; 10 participants: `sub-02` to `sub-12`, excluding `sub-01` and `sub-11` |
| `gender` | complete | Native `participants.tsv` column; values are `M` and `F` |
| `age` | complete | Native `participants.tsv` column; unit is years, range 20-30 |
| `dominant hand` | complete | Native `participants.tsv` column; all participants are `R` |


## Tasks

### Classical Task 1: 2-class motor imagery vs rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Right` | 0 | Motor imagery of dominant-hand grasping |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle condition |
- **Evidence**:
  - 10.1016/j.dib.2022.108225 - The Data in Brief paper explicitly states that RUN1-RUN4 are MI vs rest runs, with 20 trials per condition per formal run, and that the event markers for motor imagery and rest are `OVTK_GDF_Right` and `OVTK_GDF_Tongue`, respectively.
  - 10.1016/j.heliyon.2020.e03425 - The original Heliyon paper describes dominant-hand grasping motor imagery vs rest/idle and uses EEG segments from 0.5 to 2.5 s after the cue in the single-time-window analysis.
  - `task-MIvsRest_events.json` - The BIDS sidecar defines value levels `770 = MI` and `772 = Rest`, confirming the two-condition paradigm structure.
  - README - States that RUN1-RUN4 consist of MI vs Rest conditions and that RUN0 involves real grasping movement for familiarization.
- **Notes**: Use RUN1-RUN4 for the formal MI vs rest task. RUN0 is a familiarization run in which `OVTK_GDF_Right` marks actual grasping rather than motor imagery, so RUN0 should be excluded or explicitly filtered at the file/run level. `OVTK_GDF_Tongue` is an OpenViBE/GDF naming reuse; in this dataset it represents rest/idle, not tongue motor imagery.

### Potential Task 1: Motor imagery vs rest with pre-cue context
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.0 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Right` | 0 | Motor imagery of dominant-hand grasping |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle condition |
- **Evidence**:
  - `task-MIvsRest_events.json` - The value column defines `770 = MI` and `772 = Rest` as condition codes.
  - README - RUN1-RUN4 consist of MI vs Rest conditions with kinesthetic imagination of dominant-hand grasping vs rest/idle.
  - Per-run `eeg.json` files - Formal runs are named with task labels such as `MIvsRestRUN1`.
  - EDF annotation audit - `OVTK_GDF_Right` and `OVTK_GDF_Tongue` are present as raw condition cues in formal MI runs.
- **Notes**: This is an alternative epoching strategy using the same condition events as the classical task but a wider window. `tmin = -0.5 s` captures short pre-cue context rather than the full fixation period; the full fixation cross starts earlier in the trial. This task is a candidate extension and should not replace the classical 0.5-2.5 s window supported by the Heliyon analysis.

### Potential Task 2: Fixation cross vs trial end marker classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`OVTK_GDF_Cross_On_Screen`, `OVTK_GDF_End_Of_Trial`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Cross_On_Screen` | 0 | Fixation / trial preparation phase onset |
  | `OVTK_GDF_End_Of_Trial` | 1 | Trial end marker |
- **Evidence**:
  - EDF annotation audit - Both markers are directly present in EDF annotations; `OVTK_GDF_Cross_On_Screen` appears 1691 times and `OVTK_GDF_End_Of_Trial` appears 1689 times.
  - 10.1016/j.heliyon.2020.e03425 - The protocol describes fixation before the task cue and a post-task trial/break structure.
- **Notes**: `OVTK_GDF_Feedback_Continuous` is excluded because it is largely co-timed with `OVTK_GDF_End_Of_Trial` in the EDF annotations and this experiment did not provide actual feedback. Treating `Feedback_Continuous` and `End_Of_Trial` as separate classes would risk duplicate windows with conflicting labels.

### Potential Task 3: Baseline vs motor-imagery task state
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`OVTK_GDF_Right`, `OVTK_StimulationId_BaselineStart`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_StimulationId_BaselineStart` | 0 | Run-level baseline period onset |
  | `OVTK_GDF_Right` | 1 | Motor imagery cue onset in formal MI runs |
- **Evidence**:
  - README - RUN1-RUN4 consist of MI vs Rest conditions, while baseline periods are marked by `OVTK_StimulationId_BaselineStart` and `OVTK_StimulationId_BaselineStop`.
  - 10.1016/j.heliyon.2020.e03425 - The protocol includes baseline EEG before the stimulation protocol and task cues during trials.
  - EDF annotation audit - `OVTK_StimulationId_BaselineStart` and `OVTK_GDF_Right` are both directly present in EDF annotations.
- **Notes**: This candidate task contrasts run-level baseline onset with active motor-imagery cue onset. The class counts are naturally imbalanced because baseline start appears once per run, whereas `OVTK_GDF_Right` is a trial-level cue. Implementations should restrict `OVTK_GDF_Right` to RUN1-RUN4 to avoid mixing RUN0 actual grasping with formal motor imagery.

### Potential Task 4: Age regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - `participants.tsv` - `age` is a native column with values for all 10 participants.
  - `participants.json` - Defines `age` as participant age with units in years.
- **Notes**: This is a subject-level metadata regression candidate. Labels come directly from the native `participants.tsv` column, so `Label Route = info` and `Meta Level = raw`. Because N = 10 and the age range is narrow, this task should be treated only as a low-sample-size candidate analysis, not as a core benchmark.

### Potential Task 5: Sex/gender classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | Male -> 0; Female -> 1 |
- **Evidence**:
  - `participants.tsv` - `gender` is a native column with values for all 10 participants.
  - `participants.json` - Defines `gender` as participant sex and maps `M` to male and `F` to female.
- **Notes**: This is a subject-level metadata classification candidate. The class distribution is `M` = 6 and `F` = 4. Segmentation creates multiple windows but does not increase the number of independent participants, so segment counts should not be interpreted as independent subject counts.

## Data Quality Notes

- `OVTK_GDF_Tongue` is repurposed from standard GDF nomenclature to indicate the rest/idle condition in this dataset; it should not be interpreted as tongue motor imagery.
- RUN0 is a familiarization run in which `OVTK_GDF_Right` marks actual dominant-hand grasping. Formal MI vs rest tasks should use RUN1-RUN4 or explicitly filter RUN0.
- Data in Brief and Heliyon both state that no actual feedback was presented. `OVTK_GDF_Feedback_Continuous` is therefore a protocol phase marker, and `OVTK_GDF_Correct` / `OVTK_GDF_Incorrect` should not be used as feedback correctness labels.
- `OVTK_GDF_Correct` and `OVTK_GDF_Incorrect` often co-occur at the same annotation onset, which further prevents their use as a correct-vs-incorrect feedback classification target.
- `OVTK_GDF_Feedback_Continuous` is largely co-timed with `OVTK_GDF_End_Of_Trial`; using them as separate target classes may create duplicate windows with conflicting labels.
- The dataset is small: 10 participants and 50 EEG EDF files. Age and sex/gender tasks are subject-level metadata candidates and have limited statistical power.
- Event counts show a slight imbalance between `OVTK_GDF_Start_Of_Trial` / `OVTK_GDF_Cross_On_Screen` and `OVTK_GDF_End_Of_Trial` / `OVTK_GDF_Feedback_Continuous`, indicating minor annotation boundary irregularities.
- The numeric code mapping in `task-MIvsRest_events.json` records `770 = MI` and `772 = Rest`; the EDF annotations expose OVTK description strings, and the `OVTK_GDF_Right` / `OVTK_GDF_Tongue` MI-rest mapping is confirmed by the Data in Brief paper.
- The EEG device model is documented in the Data in Brief paper but is not repeated in each per-run `eeg.json`.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21 | **Channels**: 18 | **Sampling Rate**: 500 | **Manual Review**: anonymous for review
## Paradigm

Seven participants with orthopedic impairment performed four right-upper-limb motor imagery tasks (reaching, grasping, lifting, and twisting) while 18-channel EEG and fNIRS were recorded simultaneously. Each participant completed three sessions; each session contained 40 trials with the four MI tasks presented in random order. Each trial consisted of 3 s fixation, a 4 s visual cue indicating the movement task, a 3 s ready/gray-screen period to reduce afterimage effects, and a 5 s instructed motor imagery period. Event markers `S 7`-`S 10` label the four MI task types, but their exact mapping to reaching/grasping/lifting/twisting is not recoverable from the available metadata.

## File Scan Result

> **Kernel SHA256**: `f159e25f8de105c2cebaeb73c9854d33dff9482b7372c2ad586ca9542c5eedde`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `S 1` | 21 | admin | raw | Run/session start marker |
| `S 10` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 2` | 840 | event | raw | Trial phase onset or sub-event marker |
| `S 3` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 4` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 5` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 6` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 7` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 8` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 9` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `boundary` | 21 | admin | raw | Run boundary marker |
| `condition 12` | 21 | admin | raw | Condition label marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | BrainVision ActiCHamp |


## Tasks

### Classical Task 1: Four-Class Right-Upper-Limb Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 7.0 s, tmax = 14.5 s, target_events = [`S 3`, `S 4`, `S 5`, `S 6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `S 3` | 0 | Motor imagery condition 1: one of reaching, grasping, lifting, twisting |
  | `S 4` | 1 | Motor imagery condition 2: one of reaching, grasping, lifting, twisting |
  | `S 5` | 2 | Motor imagery condition 3: one of reaching, grasping, lifting, twisting |
  | `S 6` | 3 | Motor imagery condition 4: one of reaching, grasping, lifting, twisting |
- **Evidence**:
  - 10.18112/openneuro.ds004022.v1.0.0 — Official README
  - 10.3389/fnhum.2025.1583342 — Table 3: confirms 18 channels, 7 participants, 3 sessions/participant, 40 trials/session, 4 MI tasks, and trial structure `3s fixation, 4s cue, 3s ready, 5s MI`.
- **Notes**: `S 3-S 6` are confirmed as the four mutually exclusive MI condition markers by raw event counts and event order. The exact semantic mapping to reaching/grasping/lifting/twisting is not documented, so do not assign `S 3 = Reach` etc. `S 7-S 10` should not be used as class labels because all four occur once in every trial. The epoch window is cue-marker relative and chosen to cover the later MI period; if the kernel supports context labels, a cleaner implementation is to epoch `S 8` to `S 10` and label each epoch by the preceding `S 3-S 6` marker.

## Data Quality Notes

- No run-level `events.tsv` files are present; event annotations are embedded in EEGLAB `.set` headers, so event semantics must be inferred from raw event order and counts.
- The exact mapping from `S 3`, `S 4`, `S 5`, and `S 6` to reaching, grasping, lifting, and twisting is not documented in the README, BIDS sidecars, or reference papers.
- `S 7-S 10` occur once in every trial and are trial phase markers, not four-class MI labels; they should not be used directly as target classes.
- The likely MI execution window is later than the `S 3-S 6` condition marker; epoch timing should account for the trial sequence `S 2 -> S 3/S 4/S 5/S 6 -> S 7 -> S 8 -> S 9 -> S 10`.
- The dataset is small: 7 participants and 21 EEG runs, so subject leakage and weak cross-subject generalization are major evaluation risks.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# OpenBMI Motor Imagery EEG Dataset

**Dataset**: `other_openbmi` | **Year**: 2019 | **URL**: https://gigadb.org/dataset/100542
**Category**: Action/Output | **Subjects**: 54 | **Files (Completed)**: 108 | **Channels**: 62 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Fifty-four healthy subjects (24–35 years old; 25 females) participated in the OpenBMI experiments, which were recorded across two sessions on different days. For the motor imagery (MI) paradigm, EEG was acquired at 1000 Hz using a BrainAmp amplifier (Brain Products, Munich, Germany) with 62 Ag/AgCl EEG electrodes. The binary MI task comprised left- and right-hand imagery. In each trial, subjects first fixated on a central cross for 3 s and then performed the cued imagery task for 4 s according to a left or right arrow. Each MI session consisted of two phases, an offline training phase and an online test phase, and each phase contained 100 trials with balanced left- and right-hand imagery tasks. In the validation procedure reported in the paper, MI decoding was performed using 20 electrodes over the motor cortex, and EEG epochs were extracted from 1000 to 3500 ms relative to stimulus onset.

## File Scan Result

> **Kernel SHA256**: `42c2c71dbd5b0012e7422b9f830de227d3074d8ef424a3100e8bc4fb58103d75`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `left hand MI` | 5400 | event | raw | Left-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |
| `right hand MI` | 5400 | event | raw | Right-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (108/436) | N/A |
| `sex` | partial (108/436) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Motor imagery decoding - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`left hand MI`, `right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left hand MI` | 0 | Left-hand motor imagery |
  | `right hand MI` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1093/gigascience/giz002 — OpenBMI dataset with 54 subjects performing binary motor imagery (left vs right hand) across two sessions, using EEG epochs for CSP+LDA classification
  - DOI: 10.1016/j.neunet.2020.12.013 — Uses OpenBMI dataset for deep CNN-based transfer learning achieving 84.19% average accuracy
- **Notes**: 

## Data Quality Notes

- no record

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2019/2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. Subjects attended to left or right hemifields based on visual cue presentations (half-circle cues for left/right, full circle for center), with continuous alpha-band lateralization index computed from posterior electrodes and fed back in real-time. The paradigm included both offline calibration runs and online neurofeedback runs with trial structures comprising fixation, cue, target, and response phases.

## File Scan Result

> **Kernel SHA256**: `037acc48f2069aa8913ea20691642e0dde801f9e2a83f0e81feb91538fe9c21d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 16179 | event | raw | Trial phase onset: cue left |
| `event_11` | 3013 | event | raw | Trial phase onset: target left |
| `event_12` | 2248 | event | raw | Trial phase onset: target right |
| `event_13` | 1129 | event | raw | Trial phase onset: target center |
| `event_15` | 938 | event | raw | Button press correct |
| `event_2` | 5020 | event | raw | Trial phase onset: cue right |
| `event_4` | 5020 | admin | raw | Run start |
| `event_5` | 9333 | admin | raw | Run end |
| `event_6` | 6720 | event | raw | Trial phase onset: trial start |
| `event_8` | 1711 | event | raw | Trial phase onset: trial start |
| `event_9` | 4995 | event | raw | Trial phase onset: fixation on |


> For details of the complete protocol, experimental design, feedback logic and recording parameters, please refer to the main text of the paper, Figures 1a–d, Supplementary Table S1 and the Methods section. Maybe we set super meta long, which belongs to epoch_by_long_event_hdf5, and rest for epoch_by_segmentation_hdf5.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Range from 21-27 y, Mean age = 23 y |
| `sex` | complete | 7 female, 7 male (sex distribution fully reported in the manuscript) |
| `device` | missing | EEG recording: g.tec HIamp 64-channel active EEG amplifier (512 Hz sampling rate, linked ears reference, 10-10 international electrode system, ground at FCz); Eye tracking: SR Research EyeLink 1000 optical eye tracker (500 Hz sampling rate); Stimulus display: 24" LCD monitor (50 cm fixed viewing distance) |


## Tasks

### Classical Task 1: 2-class covert visuospatial attention (left vs right target)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`event_11`, `event_12`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_11` | 0 | target left |
  | `event_12` | 1 | target right |
- **Evidence**:
  - 10.1007/s10548-019-00725-9 — Primary paper explicitly describes 2-class CVSA classification using target onset events. Left target (event_11) vs right target (event_12) with tmin=-0.5s, tmax=2.0s. 3013 left targets and 2248 right targets available. BCI decoder calibration was performed on these events as part of the neurofeedback paradigm.
- **Notes**: Event meanings confirmed by events.json sidecar: x11='target left', x12='target right'. The task uses target onset events (not cue events) to classify covert visuospatial attention direction based on lateralized alpha power modulations during the sustained attention period.

### Potential Task 1: 3-class covert visuospatial attention (left vs right vs center)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`event_11`, `event_12`, `event_13`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_11` | 0 | target left (covert attention to left hemifield) |
  | `event_12` | 1 | target right (covert attention to right hemifield) |
  | `event_13` | 2 | target center (no covert attention shift, control condition) |
- **Evidence**:
  - events.json — "x11": "target left", "x12": "target right", "x13": "target center" (hardware trigger value levels confirmed across all sessions)
  - events.tsv samples — event_value 11/12/13 consistently paired with event_name "target_left"/"target_right"/"target_center" in sub-01 ses-01, ses-02 (offlinecatch, onlinesham)
  - README — "a full circle around the fixation point indicated a central fixation trial (no covert attention shift)"
- **Notes**: Target events (11/12/13) mark the onset of the sustained attention phase where subjects maintain covert visuospatial attention to the cued location. Center trials serve as an explicit control condition with no lateralized attention demand, enabling 3-way classification of attention state. Epoch window [-0.5, 2.0] s captures pre-target baseline and early sustained attention period; values inferred from analogous 2-class CVSA task structure.

### Potential Task 2: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:

- **Notes**: Small-sample subject-level regression (N=14). Segmentation-based epoching with 4s non-overlapping windows extracts features from continuous sustained-attention EEG to predict age as a continuous biomarker. The narrow age range (21-27 years) limits predictive utility but demonstrates feasibility of age regression from EEG features.

### Potential Task 3: Sex Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — N=14 subjects with complete sex data: 7 female (F), 7 male (M)
  - README — "Fourteen healthy subjects (seven female, seven male), age 23±1.52 years"
- **Notes**: Segmentation-based approach for subject-level biomarker classification. The 4-second segment length is a standard default for continuous EEG analysis when no specific temporal structure is required; overlap=0.0 ensures independent segments. Binary classification with perfectly balanced classes (7 vs 7). Very small sample size (N=14) limits generalizability but the task is technically feasible. All segments from a given subject receive the same label from participants.tsv.

## Data Quality Notes

- `device` field is missing from all files, limiting hardware provenance tracking.
- Event counts show substantial imbalance between cue events (event_1: 16179, event_2: 5020) suggesting possible data quality issue or multiple event definitions for left cues (event_1 may conflate multiple conditions).
- Multiple trial start event IDs (event_6, event_8, event_9) with overlapping meanings may indicate inconsistent event coding across runs or sessions.
- Run end events (9333) exceed run start events (5020) by factor of ~1.86, suggesting possible duplicate or spurious run end markers.
- Small sample size (N=14) limits statistical power for subject-level biomarker tasks (age regression, sex classification).
- Age range is extremely narrow (21-27 years), severely limiting generalizability of age regression model.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# SHU Motor Imagery EEG Dataset

**Dataset**: `figshare_shudb` | **Year**: 2022 | **URL**: https://figshare.com/articles/software/shu_dataset/19228725/1
**Category**: Action/Output | **Subjects**: 25 | **Files (Completed)**: 232 | **Channels**: 32 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

The MI experiment was divided into three stages. In the first stage, 0-2s was the rest preparation period, during which subjects can rest, have small body movements, and blink. The second stage, 2-4s, was the prompt stage. In this stage, the left-hand or right-hand movement animation will appear on the monitor to remind subjects of the hand task next. The third stage, 4-8s, was the process of MI. During this period, subjects perform MI tasks of hand movement in the corresponding direction according to the arrow prompt in the monitor. The EEG equipment collected and stored signals at this stage. 100 trials were obtained after completing a session. In the experiment, we carried out five independent sessions with 2 to 3 days interval on each subject so that each subject had 500 trials in 5 sessions eventually.

## File Scan Result

> **Kernel SHA256**: `55ceca75ed985c7f3ad8cd934d1a755e59dc281e37852d9f37b420ea0e3f1035`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left` | 11146 | event | raw | Left-hand motor imagery cue onset |
| `right` | 11174 | event | raw | Right-hand motor imagery cue onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 3.5 s, target_events = [`left`, `right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left` | 0 | Left-hand motor imagery |
  | `right` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1016/j.heliyon.2024.e37343 — Validates multi-session left vs right hand motor imagery classification using CNN-based feature extraction with 3s MI window (offset is 0.5)
  - DOI: 10.1016/j.jneumeth.2025.110483 — Validates on SHU dataset achieving 87.2% within-session and 67.2% cross-session accuracy for left/right hand MI
  - DOI: 10.1109/jbhi.2024.3467090 — Evaluates binary motor imagery classification on SHU dataset achieving 69.3% accuracy
- **Notes**: 

## Data Quality Notes

- Conflict exist on event label but dataset can be classified

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 22 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based motor task with a 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The experimental design includes both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) paradigm sessions, with thirty subjects participating and handedness information available in the participants metadata.

## File Scan Result

> **Kernel SHA256**: `a622f3c18fda073fcab4904a246197ba85ac15a30fabf10670a0af99d88be864`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1-rest` | 4180 | event | raw | Rest/relaxation instruction onset; trigger value 1, instruction `rest`, present in both 2-phase and 4-phase blocks. |
| `event_2-ready` | 910 | event | raw | Ready/preparation instruction onset in 4-phase blocks; trigger value 2, instruction `ready`, typically preceding the motor imagery task period. |
| `event_2-task` | 3270 | event | raw | Task/motor imagery instruction onset in 2-phase blocks; trigger value 2, instruction `task`, corresponding to right-finger kinesthetic motor imagery/SMR-ERD control. |
| `event_3-task` | 910 | event | raw | Task/motor imagery instruction onset in 4-phase blocks; trigger value 3, instruction `task`, corresponding to right-finger kinesthetic motor imagery/SMR-ERD control. |
| `event_4-interval` | 910 | event | raw | Interval/blank instruction onset in 4-phase blocks; trigger value 4, instruction `interval`, used as the post-task blank/break phase. |


> Event IDs are emitted as `event_<value>-<instruction>` because raw trigger value 2 is reused with different meanings (`ready` in 4-phase blocks and `task` in 2-phase blocks). Onsets are converted from the events.tsv millisecond unit to MNE seconds by the kernel.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | complete | EEG sidecar reports Manufacturer = Magstim EGI, ManufacturersModelName = GES400, SamplingFrequency = 1000, and EEGChannelCount = 129. |
| `amplifier` | complete | e.g. GES400 |
| `cap` | complete | e.g. Magstim EGI Hydrocel Geodesic Sensor Net |
| `dataset` | complete | e.g. openneuro_ds004447 |
| `eeg_channel_count` | complete | e.g. 129, 128 |
| `eeg_ground` | complete | e.g. CPz, placed on FCz |
| `eeg_placement_scheme` | complete | e.g. 10-20 system, 10 percent system |
| `eeg_reference` | complete | e.g. Cz |
| `event_description_format` | complete | e.g. event_<value>-<instruction> |
| `event_onset_units` | complete | e.g. ms converted to seconds |
| `handedness` | complete | e.g. left, right |
| `manufacturer` | complete | e.g. Magstim EGI |
| `paradigm_schema` | complete | e.g. 4phase, 2phase |
| `sampling_rate_hz` | complete | e.g. 1000 |
| `session` | complete | e.g. ses-01, ses-02, ses-03 |
| `source_file` | complete | e.g. sub-001_ses-01_task-smrbmi_eeg.edf, sub-001_ses-02_task-smrbmi_eeg.edf, sub-001_ses-03_task-smrbmi_eeg.edf |
| `stim_channel` | complete | e.g. Status |
| `subject_id` | complete | e.g. sub-001, sub-002, sub-003 |
| `task` | complete | e.g. smrbmi |


## Tasks

### Classical Task 1: Rest vs right-hand motor imagery state classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_1-rest`, `event_2-task`, `event_3-task`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_1-rest` | 0 | rest / relaxation phase |
  | `event_2-task` | 1 | right-hand motor imagery task phase in 2-phase training sessions |
  | `event_3-task` | 1 | right-hand motor imagery task phase in 4-phase assessment sessions |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — The data descriptor describes Dataset 3 as a sensorimotor rhythm-based BCI dataset using right-hand motor imagery and SMR-ERD control.
  - OpenNeuro ds004447 `events.tsv` — Public event files contain `rest` and `task` instructions; trigger value 2 is schema-dependent and must be disambiguated by instruction.
  - https://github.com/Junichi-Ushiba-Laboratory/pj-hd-smrbmi/blob/main/helper_analysis_EEG.m — Sample analysis code labels Dataset 3 windows as rest/task.
- **Notes**: This is the most defensible classical task because it matches the dataset's core SMR-ERD BCI contrast: rest versus right-hand motor imagery. It replaces the unsupported "motor preparation vs execution" formulation. `tmax = 2 s` is a conservative implementation window and is not claimed as a verbatim paper parameter.

### Potential Task 1: Ready vs task state classification in 4-phase assessment sessions
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_2-ready`, `event_3-task`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_2-ready` | 0 | ready / preparation instruction in 4-phase assessment sessions |
  | `event_3-task` | 1 | right-hand motor imagery task instruction in 4-phase assessment sessions |
- **Evidence**:
  - OpenNeuro ds004447 `events.tsv` — 4-phase sessions contain value 2 with instruction `ready` and value 3 with instruction `task`.
- **Notes**: This is data-supported but should remain a Potential Task. Current evidence confirms the event structure, but does not support treating ready-vs-task as the primary published benchmark.

### Potential Task 2: Four-state instruction classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_1-rest`, `event_2-ready`, `event_2-task`, `event_3-task`, `event_4-interval`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_1-rest` | 0 | rest / relaxation instruction |
  | `event_2-ready` | 1 | ready / preparation instruction in 4-phase assessment sessions |
  | `event_2-task` | 2 | right-hand motor imagery task instruction in 2-phase training sessions |
  | `event_3-task` | 2 | right-hand motor imagery task instruction in 4-phase assessment sessions |
  | `event_4-interval` | 3 | interval / blank instruction in 4-phase assessment sessions |
- **Evidence**:
  - OpenNeuro ds004447 `events.tsv` — Public event files expose `rest`, `ready`, `task`, and `interval` instructions.
- **Notes**: This task classifies instruction/phase state rather than motor-imagery class. Because `ready` and `interval` occur only in 4-phase sessions, downstream use should report schema imbalance.

### Potential Task 3: Age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping; numeric age in years, range 19-27 for the 22 publicly available EEG subjects |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Age metadata is available; only `sub-001` to `sub-022` have public EEG data directories.
- **Notes**: Subject-level metadata task. It is technically implementable but not the core BCI benchmark.

### Potential Task 4: Sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | female -> 0; male -> 1 |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Sex metadata is available; among the 22 publicly available EEG subjects the distribution is 3 female / 19 male.
- **Notes**: Technically valid binary metadata task, but strongly imbalanced and not central to the BCI paradigm.

### Potential Task 5: Handedness classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `handedness` | left -> 0; right -> 1 |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Handedness metadata is available; among the 22 publicly available EEG subjects the distribution is 1 left / 21 right.
- **Notes**: Satisfies the two-class requirement but is extremely imbalanced; treat as an edge-case metadata task.

## Data Quality Notes

- Event meanings differ across session schemas (Schema A vs Schema B), requiring careful session-aware task construction.
- Schema A (assessment sessions: ses-01, ses-07, ses-13, ses-19) uses 4-phase structure with event_1=rest, event_6=ready, event_4=task, event_5=interval.
- Schema B (training sessions: ses-02-06, ses-08-12, ses-14-18) uses 2-phase structure with event_2=task, event_3=rest.
- Severe class imbalance in Schema A: event_6 (ready) has only 91 events versus ~1237 for task/interval.
- Device metadata is missing from the dataset scan results.
- Gender distribution is highly imbalanced (5 female, 25 male).
- Handedness is extremely imbalanced (1 left-handed, 29 right-handed).
- Age range is narrow (18-27 years), potentially limiting regression task viability.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 56 | **Files (Completed)**: 280 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

This is the fourth BMI-HDEEG sensorimotor rhythm-based BCI dataset. Scientific Data 2023 describes Dataset 4 as a bivariate BCI using alpha-band and beta-band activity. Participants performed kinesthetic motor imagery of right finger movement during the imagery period and active relaxation of the right finger during the relaxation period. The public OpenNeuro ds004448 v1.0.2 file tree contains EEG data for 56 subjects and 280 EEG EDF files. Public BIDS events.tsv files contain only Trial start annotations and do not directly expose left/right, rest/imagery, feedback group, verum/placebo, alpha/beta, or phase labels. Therefore this document does not define left-vs-right or rest-vs-imagery event-route tasks from the current public BIDS event labels.

## File Scan Result

> **Kernel SHA256**: `d72f26fbb472eccd2b3469776dfe7698494f2e80185fb7afd92c7a5e7ba46828`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 277 | event | raw | Trial phase onset: Trial start |
| `event_2` | 1723 | event | raw | Unknown event code not present in BIDS events.tsv annotations |
| `event_3` | 1875 | event | raw | Unknown event code not present in BIDS events.tsv annotations |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | EEG sidecar reports `Manufacturer = Magstim EGI`, `ManufacturersModelName = GES400`, `SamplingFrequency = 1000`, and `EEGChannelCount = 129`. |


## Tasks

### Potential Task 1: Age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping; numeric age in years, range 19-58 |
- **Evidence**:
  - OpenNeuro ds004448 `participants.tsv` — `age` is complete for all 56 public participants.
- **Notes**: Subject-level metadata task using fixed EEG segmentation. This is technically implementable but is not the core BCI benchmark described by the data descriptor.

### Potential Task 2: Gender classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | female -> 0; male -> 1 |
- **Evidence**:
  - OpenNeuro ds004448 `participants.tsv` — `gender` is complete; distribution is 7 female / 49 male.
- **Notes**: Technically valid binary metadata task, but highly imbalanced and not central to the BCI paradigm.

## Data Quality Notes

- Event codes `event_2` (n=1723) and `event_3` (n=1875) are present in the raw data but have no corresponding annotations in BIDS events.tsv files, limiting interpretability of trial structure.
- File count (280) exceeds subject count (56), indicating multiple files per subject (likely multiple runs/sessions); users should verify within-subject consistency before pooling.
- Gender classification task has severe class imbalance (~87.5% male vs ~12.5% female) which may bias model training without mitigation strategies.
- `handedness` is available in `participants.tsv`, but it is not defined as a task label because the distribution is extremely imbalanced (1 left / 55 right) and it is not part of the core BCI paradigm.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed two alternating visual go/no-go tasks: an animal categorization task and a target-image recognition task. Images were flashed for 20 ms, each run contained about 100 images, and participants responded by releasing a button for target images while withholding response for non-target images. The first recording phase contains 13 runs and the second recording phase contains 12 runs for each subject, for a total of 25 runs per subject.

## File Scan Result

> **Kernel SHA256**: `ff0ca244b877ee53f921cd182aadc7b0a3c9a2d53a7bf101424de81b7a3af3ff`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `animal_distractor` | 6300 | event | raw | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task |
| `animal_target` | 6298 | event | raw | Stimulus onset: image containing an animal, target in go-nogo animal categorization task |
| `correct` | 16921 | event | raw | Response: correct behavioral response |
| `difficult_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
| `difficult_target` | 4198 | event | raw | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
| `easy_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
| `easy_target` | 4200 | event | raw | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
| `incorrect` | 745 | event | raw | Response: incorrect behavioral response |
| `nonanimal_distractor` | 2800 | event | raw | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
| `nonanimal_target` | 2800 | event | raw | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 2-class animal categorization target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_distractor` | 0 | Image containing an animal, target in go-nogo animal categorization task |
  | `animal_target` | 1 | Image not containing an animal, distractor in go-nogo animal categorization task |
- **Evidence**:
  - doi:10.1016/j.cogbrainres.2003.11.010 — Classical 2-class go/no-go animal categorization with 14 subjects, 20 ms flashes, 25 runs; matches dataset parameters exactly
  - 10.1038/s41598-023-27528-0 — Describes epochs from -1 to 2 s with effect window 350-450 ms for similar paradigm; ~6300 balanced trials per class
- **Notes**: Conservative epoch window (-0.3 to 0.7 s) chosen to capture typical visual ERP components (P1, N1, P300) for 20 ms flash paradigm while avoiding post-response contamination. Both target_events are stimulus onset markers from the go-nogo animal categorization task specifically, excluding easy/difficult/nonanimal variants which belong to a different recognition task condition.

### Potential Task 1: 8-class stimulus type discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`, `difficult_distractor`, `difficult_target`, `easy_distractor`, `easy_target`, `nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_target` | 0 | Stimulus onset: image containing an animal, target in go-nogo animal categorization task |
  | `animal_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task |
  | `easy_target` | 2 | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
  | `easy_distractor` | 3 | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
  | `difficult_target` | 4 | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
  | `difficult_distractor` | 5 | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
  | `nonanimal_target` | 6 | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |
  | `nonanimal_distractor` | 7 | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — BIDS sidecar defining all 8 stimulus event types with their meanings (animal_target/distractor, easy_target/distractor, difficult_target/distractor, nonanimal_target/distractor)
  - sub-002_ses-01_task-gonogo_run-10_events.tsv — Direct observation of event values in data: animal_target, animal_distractor, correct, etc.
  - README — Task description: two alternated tasks (categorization and recognition), target and non-target images equally likely, go/nogo paradigm with 20 ms stimulus presentation
- **Notes**: Most granular event-based task possible with this dataset. Combines 4 task conditions (animal go-nogo categorization, easy/difficult/nonanimal single-target detection) × 2 target/distractor levels = 8 classes. Highly imbalanced across classes: animal (~6300 each), easy/difficult (~4200 each), nonanimal (~2800 each).

### Potential Task 2: 2-class easy detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`easy_distractor`, `easy_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `easy_target` | 0 | Stimulus onset: image containing an animal (easy to detect), target in single target easy animal image detection task |
  | `easy_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — Defines `easy_target` as "An image containing an animal (easy to detect) that is a target in a single target image detection task" and `easy_distractor` as "An image not containing an animal that is a distractor in a single target easy animal image detection task"
  - events.tsv sample (sub-002_ses-01_task-gonogo_run-10) — Shows `easy_target` and `easy_distractor` events with stimulus trial_type and response_time values
  - README — Describes go/nogo paradigm with 20 ms flash presentation, 2000 ms SOA, and 1000 ms response window; same paradigm structure as other detection tasks in dataset
- **Notes**: Inferred epoch window (-0.3 to 0.7 s) based on 20 ms flash paradigm shared with animal categorization task; post-stimulus window covers typical visual ERP components (P1, N1, P2, N2) and early motor preparation for go responses. ~4200 trials per class estimated from event counts. No direct classical reference for this specific easy detection contrast, but structurally identical to established visual detection paradigms.

### Potential Task 3: 2-class difficult detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`difficult_distractor`, `difficult_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `difficult_target` | 0 | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
  | `difficult_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
- **Evidence**:
  - events.json sidecar (sub-002_ses-01_task-gonogo_run-10_events.json, sub-002_ses-01_task-gonogo_run-11_events.json) — confirms `difficult_target` and `difficult_distractor` as event levels with descriptions matching the difficult detection task condition
  - events.tsv samples (sub-002_ses-01_task-gonogo_run-11_events.tsv) — direct observation of `difficult_target` and `difficult_distractor` events in actual data
  - README — describes the recognition/detection task with target and non-target images equally likely, 20 ms flash presentation, go/nogo response paradigm
- **Notes**: ~4200 trials each of difficult_target and difficult_distractor, balanced classes. Epoch window inferred from classical task defaults for the same 20 ms flash paradigm (tmin=-0.3s, tmax=0.7s). This is the more challenging discrimination condition compared to easy_target/easy_distractor due to hard-to-detect animal images.

### Potential Task 4: 2-class nonanimal detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `nonanimal_target` | 0 | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |
  | `nonanimal_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — events.json sidecar defines `nonanimal_target` as "An image not containing an animal that is a target in a single target image detection task" and `nonanimal_distractor` as "An image not containing an animal that is a distractor in a single target non-animal image detection task"
  - sub-002_ses-01_task-gonogo_run-10_events.tsv — direct observation of stimulus events with values `nonanimal_target` and `nonanimal_distractor` in actual data
  - README — describes go/nogo paradigm with 20 ms stimulus presentation, 1000 ms response window, 2000 ms ± 200 ms SOA; epoch window inferred from classical task defaults for this flash paradigm
- **Notes**: ~2800 trials each of nonanimal_target and nonanimal_distractor, balanced. Control condition without animal content in the single-target non-animal detection variant of the gonogo task.

### Potential Task 5: 2-class response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `correct` | 0 | Correct behavioral response |
  | `incorrect` | 1 | Incorrect behavioral response |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — `correct` defined as "Correct response", `incorrect` defined as "Incorrect response" in value column Levels
  - events.tsv samples — Response events with trial_type='response' and values 'correct'/'incorrect' observed across all runs
- **Notes**: Response-locked epochs for error-related negativity (ERN) and correct-response positivity analysis. Highly imbalanced classes (~16921 correct vs ~745 incorrect). Epoch window -0.3 to 0.7 s centered on response onset to capture ERN (~0-100 ms) and Pe (~200-400 ms) components. Values marked with * inferred from standard ERN/Pe ERP literature.

### Potential Task 6: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — Include the gender of the subjects
- **Notes**: Segmentation-based biometric classification using 2-second overlapping EEG segments (50% overlap) from continuous recordings. Subject gender labels are drawn from participants.tsv, with balanced classes (7F, 7M across 14 subjects). No event structure required; segments are extracted uniformly across the continuous recording. Epoch parameters inferred from standard segmentation defaults for subject-level biometric tasks.

### Potential Task 7: Go vs No-Go Trial Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`, `difficult_distractor`, `difficult_target`, `easy_distractor`, `easy_target`, `nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_target` | 0 | Go trial (target stimulus requiring button release) |
  | `easy_target` | 0 | Go trial (target stimulus requiring button release) |
  | `difficult_target` | 0 | Go trial (target stimulus requiring button release) |
  | `nonanimal_target` | 0 | Go trial (target stimulus requiring button release) |
  | `animal_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `easy_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `difficult_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `nonanimal_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
- **Evidence**:
  - events.json sidecar files (sub-002_ses-01_task-gonogo_run-10_events.json, sub-002_ses-01_task-gonogo_run-11_events.json) — Defines all 8 stimulus event types with explicit target/distractor meanings for go-nogo and single-target detection variants
  - events.tsv samples (sub-002_ses-01_task-gonogo_run-10_events.tsv) — Confirms event occurrence with trial_type='stimulus' and value column containing target/distractor events
  - README — Describes go/nogo paradigm: "Participants gave their responses following a go/nogo paradigm. For each target, they had to lift their finger from the button"
  - dataset_description.json — "Go-nogo categorization and detection task" confirms paradigm
- **Notes**: Many-to-one mapping of 8 distinct stimulus events to 2 classes (y=0 for all target/go trials, y=1 for all distractor/no-go trials) based on required behavioral response. The four target types (animal, easy, difficult, nonanimal) and four distractor types are collapsed across task variants (categorization vs. detection) since all share the same go/no-go response requirement. Epoch window inferred from related tasks in same dataset.

## Data Quality Notes

- *_eeg.json sidecars report EEGChannelCount: 0, while all *_channels.tsv files contain 31 channel rows; channel metadata should therefore be taken from the channel files rather than the sidecar field.
- The event JSON describes trial_type levels such as go, nogo, and responses, but the released TSV files actually use stimulus and response; downstream parsing should follow the TSV contents.
- The response_time column is available and populated for many stimulus rows, including some distractor trials with false-alarm responses, so RT-based analyses should explicitly filter by target/distractor and correctness criteria.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2004/2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz | **Manual Review**: anonymous for review

## Paradigm

A continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. Five empty squares were presented continuously on screen, with participants instructed to attend to one designated location and press a mouse button whenever a white disk appeared at that attended location. Event codes encode both the attended position and the cued (stimulus) position, allowing separation of target oddballs (attended location = stimulus location) from non-target distractors. The dataset contains only 2 completed files and represents a very limited subset of the original study data.

## File Scan Result

> **Kernel SHA256**: `3c221cbb992edef968d255c442ebb1899989076165e8a307a10b84832e041755`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `203` | 1 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `217` | 2 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `237` | 1 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `31` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 1 (distractor, expected) |
| `33` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 3 (target, unexpected oddball) |
| `34` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 4 (distractor, expected) |
| `35` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 5 (distractor, expected) |
| `41` | 238 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 1 (distractor, expected) |
| `42` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 2 (distractor, expected) |
| `43` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 3 (distractor, expected) |
| `44` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 4 (target, unexpected oddball) |
| `45` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 5 (distractor, expected) |
| `Picture` | 5939 | event | raw | Experimental stimulus onset: drawing of five rectangular boxes with highlighted cue box and disc |
| `Response` | 1202 | event | raw | Participant response: keyboard key press |
| `boundary` | 58 | admin | raw | Trial phase onset: pause/discontinuous segment boundary |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: visual oddball target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`31`, `33`, `34`, `35`, `41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `33` | 1 | target: attend-3 cue-3, disc in cued box (unexpected oddball) |
  | `44` | 1 | target: attend-4 cue-4, disc in cued box (unexpected oddball) |
  | `31` | 0 | distractor: attend-3 cue-3, disc in box 1 (expected) |
  | `34` | 0 | distractor: attend-3 cue-3, disc in box 4 (expected) |
  | `35` | 0 | distractor: attend-3 cue-3, disc in box 5 (expected) |
  | `41` | 0 | distractor: attend-4 cue-4, disc in box 1 (expected) |
  | `42` | 0 | distractor: attend-4 cue-4, disc in box 2 (expected) |
  | `43` | 0 | distractor: attend-4 cue-4, disc in box 3 (expected) |
  | `45` | 0 | distractor: attend-4 cue-4, disc in box 5 (expected) |
- **Evidence**:
  - 10.1523/jneurosci.3477.07.2007 — Classical visual oddball task with target (attended=cued location) vs distractor (attended≠cued location). Two target events exist: 33 (attend-3 cue-3) and 44 (attend-4 cue-4). Seven distractor events exist: 31, 34, 35, 41, 42, 43, 45. Total target trials: 479; distractor trials: 1675. Epoch window tmin=-1s to tmax=2s follows the published target-locked analysis window.
- **Notes**: All nine numeric event codes (31-35, 41-45) appear in the exported EEG files as annotations, confirmed by events.tsv counts and events.json definitions. The two target conditions (33, 44) are merged to y=1; all seven distractor conditions (31, 34, 35, 41, 42, 43, 45) are merged to y=0, reflecting the core oddball manipulation of target vs non-target discrimination.

### Potential Task 1: visual oddball 9-class position decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`31`, `33`, `34`, `35`, `41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `31` | 0 | Distractor: box 3 cued, disc in position 1 |
  | `33` | 1 | Target: box 3 cued, disc in position 3 (oddball) |
  | `34` | 2 | Distractor: box 3 cued, disc in position 4 |
  | `35` | 3 | Distractor: box 3 cued, disc in position 5 |
  | `41` | 4 | Distractor: box 4 cued, disc in position 1 |
  | `42` | 5 | Distractor: box 4 cued, disc in position 2 |
  | `43` | 6 | Distractor: box 4 cued, disc in position 3 |
  | `44` | 7 | Target: box 4 cued, disc in position 4 (oddball) |
  | `45` | 8 | Distractor: box 4 cued, disc in position 5 |
- **Evidence**:
  - events.json sidecar (sub-001, sub-002) — HED tags and level descriptions confirm 31-35 and 41-45 encode box×disc position combinations; target positions (33, 44) are oddball conditions where disc appears in cued box
  - README — describes selective attention visual oddball paradigm with five rectangular boxes and target detection task
  - events.tsv counts — confirm event IDs 31, 33, 34, 35, 41, 42, 43, 44, 45 all appear in the released data
- **Notes**: 9-class classification tests spatial decodability beyond binary target/distractor. The 9 conditions are near-balanced (~238-240 trials each). y values assigned by sorting event IDs numerically: 31→0, 33→1, 34→2, 35→3, 41→4, 42→5, 43→6, 44→7, 45→8. Note that position 2 in box 3 (code 32) is absent from actual data exports. Epoch window follows the published oddball target-locked analysis style rather than a parameter explicitly specified in the BIDS metadata.

### Potential Task 2: Visual Oddball Target vs Distractor (Attend-3 Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`31`, `33`, `34`, `35`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `33` | 1 | Target: box 3 highlighted/cued, disc in box 3 (unexpected oddball) |
  | `31` | 0 | Distractor: box 3 highlighted/cued, disc in box 1 (expected) |
  | `34` | 0 | Distractor: box 3 highlighted/cued, disc in box 4 (expected) |
  | `35` | 0 | Distractor: box 3 highlighted/cued, disc in box 5 (expected) |
- **Evidence**:
  - - events.json sidecar — confirms event 33 is the attend-3 target oddball and events 31, 34, 35 are attend-3 distractors
  - - README / EEG sidecar — describe the selective-attention oddball task and target detection rule
- **Notes**: Restricted to attend-3 condition where box 3 is always highlighted/cued. Target (event 33, disc in cued box 3) is contrasted against three distractor types (events 31, 34, 35) where the disc appears in non-cued boxes 1, 4, or 5. All distractor events are merged to y=0 to test within-condition oddball detection (target probability ~25% within attend-3 trials). Epoch window matches classical oddball stimulus-locked analysis; parameters inferred from standard visual oddball ERP literature as no explicit epoch window was specified in dataset documentation.

### Potential Task 3: Visual Oddball Target vs Distractor (Attend-4 Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `44` | 1 | target (attend-4, disc in cued box 4) |
  | `41` | 0 | distractor (attend-4, disc in box 1) |
  | `42` | 0 | distractor (attend-4, disc in box 2) |
  | `43` | 0 | distractor (attend-4, disc in box 3) |
  | `45` | 0 | distractor (attend-4, disc in box 5) |
- **Evidence**:
  - - events.json sidecar — confirms event 44 is the attend-4 target oddball and events 41, 42, 43, 45 are attend-4 distractors
  - - README / EEG sidecar — describe the selective-attention oddball task and target detection rule
- **Notes**: Restricted to attend-4 condition only (cue box 4 highlighted). Target event 44 (disc in cued box 4, unexpected oddball) vs distractor events 41-43,45 (disc in non-cued boxes 1-3,5, expected). Controls for attended location to test within-condition oddball effects. All five event codes confirmed in EEG file annotations and events.json sidecar definitions. Epoch window inferred from classical oddball timing (-1 to +2 s relative to stimulus onset).

### Potential Task 4: Gender Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — N=2 subjects with gender field: 1 female (sub-001), 1 male (sub-002)
- **Notes**: Segment-based approach required since no discriminating event structure exists for this subject-level label. 10-second non-overlapping segments at 256 Hz yield 2560 samples per segment. Only 2 subjects are available, with 1 subject per class; this is an extremely weak proof-of-concept subject-trait decoding task and will likely be filtered out downstream.

### Potential Task 5: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — age column present for both subjects with value 30
- **Notes**: Archetype B3: age is a native participants.tsv field (no kernel derivation needed). Segmentation-based epoching creates 10-second non-overlapping windows from continuous EEG; each segment inherits the subject's age as the regression target. However, both subjects are age 30, so this task has zero label variance and is effectively non-viable.

## Data Quality Notes

- Extremely small sample size: only 2 completed files/subjects available, severely limiting statistical power and generalizability.
- Missing device metadata in Info table; BioSemi 256-channel system inferred from dataset documentation and channel count.
- Age field shows zero variance (both subjects age 30), making age regression task non-viable; downstream pipeline should filter this task out.
- Gender classification task has only 1 sample per class (N=2 total), which is insufficient for meaningful machine learning.
- Event code 32 (distractor: attend-3 cue-2) is documented in paradigm description but absent from actual data exports; this appears to be a planned but unused condition.
- Spurious system markers (203, 217, 237) present in raw data but marked as removed during preprocessing; these should be excluded from analysis.
- High number of `Picture` events (5939) relative to trial-coded events (~2394) suggests screen refresh or frame-level triggers were logged, requiring careful event selection for epoching.
- `boundary` events (58) indicate discontinuous segments or pauses in recording; users should verify whether these affect trial integrity.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# A dataset recorded during development of an affective brain-computer music interface: calibration session

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 94 | **Channels**: 37 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Nineteen healthy adults (age 19–30, 11 female) participated in a calibration session for an affective brain-computer music interface (BCMI). Participants listened to 21-second synthetic music clips designed to induce specific affective states across a 3×3 valence (low/neutral/high) by arousal (low/neutral/high) design. EEG was recorded with 37 channels at 1000 Hz alongside physiological signals including GSR, with each trial marked by paired events indicating both the target affective condition (codes 1–9) and the specific music stimulus played (codes 101–209).

## File Scan Result

> **Kernel SHA256**: `edceca8fb0342cae25894706ac98f4bee2577ea60c03235c17862ab9d5cd2415`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1` | 125 | event | raw | Affect target trial onset: LVLA, low valence and low arousal |
| `101` | 19 | event | raw | musicPlayed marker: stimulus-list item 1 (code - 100) |
| `102` | 18 | event | raw | musicPlayed marker: stimulus-list item 2 (code - 100) |
| `103` | 18 | event | raw | musicPlayed marker: stimulus-list item 3 (code - 100) |
| `104` | 19 | event | raw | musicPlayed marker: stimulus-list item 4 (code - 100) |
| `105` | 19 | event | raw | musicPlayed marker: stimulus-list item 5 (code - 100) |
| `106` | 19 | event | raw | musicPlayed marker: stimulus-list item 6 (code - 100) |
| `107` | 19 | event | raw | musicPlayed marker: stimulus-list item 7 (code - 100) |
| `108` | 19 | event | raw | musicPlayed marker: stimulus-list item 8 (code - 100) |
| `109` | 18 | event | raw | musicPlayed marker: stimulus-list item 9 (code - 100) |
| `110` | 19 | event | raw | musicPlayed marker: stimulus-list item 10 (code - 100) |
| `113` | 19 | event | raw | musicPlayed marker: stimulus-list item 13 (code - 100) |
| `114` | 19 | event | raw | musicPlayed marker: stimulus-list item 14 (code - 100) |
| `115` | 19 | event | raw | musicPlayed marker: stimulus-list item 15 (code - 100) |
| `116` | 18 | event | raw | musicPlayed marker: stimulus-list item 16 (code - 100) |
| `117` | 19 | event | raw | musicPlayed marker: stimulus-list item 17 (code - 100) |
| `118` | 19 | event | raw | musicPlayed marker: stimulus-list item 18 (code - 100) |
| `119` | 18 | event | raw | musicPlayed marker: stimulus-list item 19 (code - 100) |
| `120` | 18 | event | raw | musicPlayed marker: stimulus-list item 20 (code - 100) |
| `121` | 19 | event | raw | musicPlayed marker: stimulus-list item 21 (code - 100) |
| `122` | 18 | event | raw | musicPlayed marker: stimulus-list item 22 (code - 100) |
| `125` | 19 | event | raw | musicPlayed marker: stimulus-list item 25 (code - 100) |
| `126` | 18 | event | raw | musicPlayed marker: stimulus-list item 26 (code - 100) |
| `127` | 18 | event | raw | musicPlayed marker: stimulus-list item 27 (code - 100) |
| `128` | 19 | event | raw | musicPlayed marker: stimulus-list item 28 (code - 100) |
| `129` | 19 | event | raw | musicPlayed marker: stimulus-list item 29 (code - 100) |
| `130` | 18 | event | raw | musicPlayed marker: stimulus-list item 30 (code - 100) |
| `131` | 18 | event | raw | musicPlayed marker: stimulus-list item 31 (code - 100) |
| `132` | 19 | event | raw | musicPlayed marker: stimulus-list item 32 (code - 100) |
| `133` | 19 | event | raw | musicPlayed marker: stimulus-list item 33 (code - 100) |
| `134` | 19 | event | raw | musicPlayed marker: stimulus-list item 34 (code - 100) |
| `137` | 19 | event | raw | musicPlayed marker: stimulus-list item 37 (code - 100) |
| `138` | 19 | event | raw | musicPlayed marker: stimulus-list item 38 (code - 100) |
| `139` | 19 | event | raw | musicPlayed marker: stimulus-list item 39 (code - 100) |
| `140` | 18 | event | raw | musicPlayed marker: stimulus-list item 40 (code - 100) |
| `141` | 18 | event | raw | musicPlayed marker: stimulus-list item 41 (code - 100) |
| `142` | 19 | event | raw | musicPlayed marker: stimulus-list item 42 (code - 100) |
| `143` | 19 | event | raw | musicPlayed marker: stimulus-list item 43 (code - 100) |
| `144` | 19 | event | raw | musicPlayed marker: stimulus-list item 44 (code - 100) |
| `145` | 18 | event | raw | musicPlayed marker: stimulus-list item 45 (code - 100) |
| `146` | 18 | event | raw | musicPlayed marker: stimulus-list item 46 (code - 100) |
| `149` | 19 | event | raw | musicPlayed marker: stimulus-list item 49 (code - 100) |
| `150` | 19 | event | raw | musicPlayed marker: stimulus-list item 50 (code - 100) |
| `151` | 18 | event | raw | musicPlayed marker: stimulus-list item 51 (code - 100) |
| `152` | 19 | event | raw | musicPlayed marker: stimulus-list item 52 (code - 100) |
| `153` | 19 | event | raw | musicPlayed marker: stimulus-list item 53 (code - 100) |
| `154` | 19 | event | raw | musicPlayed marker: stimulus-list item 54 (code - 100) |
| `155` | 19 | event | raw | musicPlayed marker: stimulus-list item 55 (code - 100) |
| `156` | 19 | event | raw | musicPlayed marker: stimulus-list item 56 (code - 100) |
| `157` | 19 | event | raw | musicPlayed marker: stimulus-list item 57 (code - 100) |
| `158` | 19 | event | raw | musicPlayed marker: stimulus-list item 58 (code - 100) |
| `161` | 19 | event | raw | musicPlayed marker: stimulus-list item 61 (code - 100) |
| `162` | 19 | event | raw | musicPlayed marker: stimulus-list item 62 (code - 100) |
| `163` | 18 | event | raw | musicPlayed marker: stimulus-list item 63 (code - 100) |
| `164` | 18 | event | raw | musicPlayed marker: stimulus-list item 64 (code - 100) |
| `165` | 19 | event | raw | musicPlayed marker: stimulus-list item 65 (code - 100) |
| `166` | 19 | event | raw | musicPlayed marker: stimulus-list item 66 (code - 100) |
| `167` | 19 | event | raw | musicPlayed marker: stimulus-list item 67 (code - 100) |
| `168` | 19 | event | raw | musicPlayed marker: stimulus-list item 68 (code - 100) |
| `169` | 19 | event | raw | musicPlayed marker: stimulus-list item 69 (code - 100) |
| `170` | 19 | event | raw | musicPlayed marker: stimulus-list item 70 (code - 100) |
| `173` | 19 | event | raw | musicPlayed marker: stimulus-list item 73 (code - 100) |
| `174` | 18 | event | raw | musicPlayed marker: stimulus-list item 74 (code - 100) |
| `175` | 19 | event | raw | musicPlayed marker: stimulus-list item 75 (code - 100) |
| `176` | 18 | event | raw | musicPlayed marker: stimulus-list item 76 (code - 100) |
| `177` | 18 | event | raw | musicPlayed marker: stimulus-list item 77 (code - 100) |
| `178` | 18 | event | raw | musicPlayed marker: stimulus-list item 78 (code - 100) |
| `179` | 18 | event | raw | musicPlayed marker: stimulus-list item 79 (code - 100) |
| `180` | 19 | event | raw | musicPlayed marker: stimulus-list item 80 (code - 100) |
| `181` | 18 | event | raw | musicPlayed marker: stimulus-list item 81 (code - 100) |
| `182` | 18 | event | raw | musicPlayed marker: stimulus-list item 82 (code - 100) |
| `185` | 18 | event | raw | musicPlayed marker: stimulus-list item 85 (code - 100) |
| `186` | 19 | event | raw | musicPlayed marker: stimulus-list item 86 (code - 100) |
| `187` | 18 | event | raw | musicPlayed marker: stimulus-list item 87 (code - 100) |
| `188` | 18 | event | raw | musicPlayed marker: stimulus-list item 88 (code - 100) |
| `189` | 19 | event | raw | musicPlayed marker: stimulus-list item 89 (code - 100) |
| `190` | 19 | event | raw | musicPlayed marker: stimulus-list item 90 (code - 100) |
| `191` | 19 | event | raw | musicPlayed marker: stimulus-list item 91 (code - 100) |
| `192` | 19 | event | raw | musicPlayed marker: stimulus-list item 92 (code - 100) |
| `193` | 19 | event | raw | musicPlayed marker: stimulus-list item 93 (code - 100) |
| `194` | 19 | event | raw | musicPlayed marker: stimulus-list item 94 (code - 100) |
| `197` | 18 | event | raw | musicPlayed marker: stimulus-list item 97 (code - 100) |
| `198` | 18 | event | raw | musicPlayed marker: stimulus-list item 98 (code - 100) |
| `199` | 18 | event | raw | musicPlayed marker: stimulus-list item 99 (code - 100) |
| `2` | 188 | event | raw | Affect target trial onset: NVLA, neutral valence and low arousal |
| `200` | 18 | event | raw | musicPlayed marker: stimulus-list item 100 (code - 100) |
| `201` | 18 | event | raw | musicPlayed marker: stimulus-list item 101 (code - 100) |
| `202` | 19 | event | raw | musicPlayed marker: stimulus-list item 102 (code - 100) |
| `203` | 18 | event | raw | musicPlayed marker: stimulus-list item 103 (code - 100) |
| `204` | 18 | event | raw | musicPlayed marker: stimulus-list item 104 (code - 100) |
| `205` | 19 | event | raw | musicPlayed marker: stimulus-list item 105 (code - 100) |
| `206` | 18 | event | raw | musicPlayed marker: stimulus-list item 106 (code - 100) |
| `3` | 148 | event | raw | Affect target trial onset: HVLA, high valence and low arousal |
| `4` | 205 | event | raw | Affect target trial onset: LVNA, low valence and neutral arousal |
| `5` | 205 | event | raw | Affect target trial onset: NVNA, neutral valence and neutral arousal |
| `6` | 195 | event | raw | Affect target trial onset: HVNA, high valence and neutral arousal |
| `7` | 258 | event | raw | Affect target trial onset: LVHA, low valence and high arousal |
| `9` | 368 | event | raw | Affect target trial onset: HVHA, high valence and high arousal |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `GSR` | derived (per Task Notes) | super | Native GSR signal listed in channels.tsv with unit microV; sample-aligned with EEG, so no additional derived channel is required |
| `VA1` | native (raw misc in EEG file) | raw | Continuous FEELTRACE valence report on a 0-9 scale; native UserReport channel, sample-aligned with EEG |
| `VA2` | native (raw misc in EEG file) | raw | Continuous FEELTRACE arousal report on a 0-9 scale; native UserReport channel, sample-aligned with EEG |
| `VAtarg` | native (raw misc in EEG file) | raw | Target affect code for the music clip, using the 1-9 valence/arousal grid; native MetaData channel, sample-aligned with EEG |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | complete | N/A |
| `cap` | complete | e.g. 32-channel EEG cap |
| `dataset` | complete | e.g. openneuro_ds002722 |
| `eeg_reference` | complete | e.g. placed on FCz |
| `subject_id` | complete | e.g. sub-01, sub-02, sub-03 |
| `task` | complete | e.g. Run |


## Tasks

### Classical Task 1: 9-Class Affective State Classification (Valence × Arousal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `1` | 0 | LVLA: low valence, low arousal |
  | `2` | 1 | NVLA: neutral valence, low arousal |
  | `3` | 2 | HVLA: high valence, low arousal |
  | `4` | 3 | LVNA: low valence, neutral arousal |
  | `5` | 4 | NVNA: neutral valence, neutral arousal |
  | `6` | 5 | HVNA: high valence, neutral arousal |
  | `7` | 6 | LVHA: low valence, high arousal |
  | `9` | 7 | HVHA: high valence, high arousal |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 - Primary data descriptor for openneuro_ds002722 describing 9-class affective state classification across 3×3 valence-by-arousal design with 21-second music clips
  - 10.1038/s41598-019-45105-2 - Describes calibration session for affective BCMI with 21-second synthetic music clips and event codes 1-9 marking target affective conditions
- **Notes**: Event ID 8 (NVHA: neutral valence, high arousal) is defined in events.json but has zero occurrences, reducing the design from 9 to 8 observed classes. The 21-second epoch duration matches the full music clip length per events.tsv. Classification y values are 0-based sequential integers.

### Classical Task 2: 3-Class Valence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `1` | 0 | low valence |
  | `4` | 1 | low valence |
  | `7` | 2 | low valence |
  | `2` | 3 | neutral valence |
  | `5` | 4 | neutral valence |
  | `3` | 5 | high valence |
  | `6` | 6 | high valence |
  | `9` | 7 | high valence |
- **Evidence**:
  - 10.1038/s41598-019-45105-2 - Reports results for reduced 3-class valence-only classification problem derived from the full 3×3 design
- **Notes**: Collapses the 3×3 valence-arousal grid into three valence levels. Event ID 8 (neutral valence, high arousal) is absent from data. Low valence events: 1 (LVLA), 4 (LVNA), 7 (LVHA). Neutral valence events: 2 (NVLA), 5 (NVNA). High valence events: 3 (HVLA), 6 (HVNA), 9 (HVHA).

### Classical Task 3: 3-Class Arousal Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `1` | 0 | low arousal |
  | `2` | 1 | low arousal |
  | `3` | 2 | low arousal |
  | `4` | 3 | neutral arousal |
  | `5` | 4 | neutral arousal |
  | `6` | 5 | neutral arousal |
  | `7` | 6 | high arousal |
  | `9` | 7 | high arousal |
- **Evidence**:
  - 10.1038/s41598-019-45105-2 - Reports results for reduced 3-class arousal-only classification problem derived from the full 3×3 design
- **Notes**: Collapses the 3×3 valence-arousal grid into three arousal levels. Event ID 8 (neutral valence, high arousal) is absent from data. Low arousal events: 1 (LVLA), 2 (NVLA), 3 (HVLA). Neutral arousal events: 4 (LVNA), 5 (NVNA), 6 (HVNA). High arousal events: 7 (LVHA), 9 (HVHA).

### Potential Task 1: Continuous Valence Regression from FEELTRACE
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `VA1` | 0–9 (a.u.) |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 - Dataset includes continuous FEELTRACE ratings for valence and arousal during music clip listening
  - analysis.md MISC Label Summary - VA1 documented as continuous FEELTRACE valence report on 0-9 scale
- **Notes**: Regression on continuous subjective valence ratings collected during each 21-second trial. VA1 is a native raw MISC channel sample-aligned with EEG. The 0-9 scale matches the FEELTRACE interface used in the paradigm.

### Potential Task 2: Continuous Arousal Regression from FEELTRACE
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `VA2` | 0–9 (a.u.) |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 - Dataset includes continuous FEELTRACE ratings for valence and arousal during music clip listening
  - analysis.md MISC Label Summary - VA2 documented as continuous FEELTRACE arousal report on 0-9 scale
- **Notes**: Regression on continuous subjective arousal ratings collected during each 21-second trial. VA2 is a native raw MISC channel sample-aligned with EEG. The 0-9 scale matches the FEELTRACE interface used in the paradigm.

### Potential Task 3: GSR-Based Arousal Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `GSR` | continuous (μV) |
- **Evidence**:
  - analysis.md MISC Label Summary - GSR listed as derived (per Task Notes) with native signal in channels.tsv
  - analysis.md Data Quality Notes - GSR channel units are unspecified and require verification
- **Notes**: Uses galvanic skin response as a physiological proxy for arousal level. GSR is marked as super meta because the derived channel annotation requires verification. Units are documented as microV in channels.tsv but may be μS; this uncertainty is noted in Data Quality Notes.

### Potential Task 4: Subject Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | female |
- **Evidence**:
  - analysis.md Paradigm - 19 healthy adults (11 female, 8 male) participated
  - analysis.md Info table - subject_sex field marked complete
- **Notes**: Demographic classification task using EEG features to predict participant sex. Epoching uses segmentation due to lack of event-locked structure for this demographic variable. 11 female and 8 male participants provides imbalanced but viable two-class problem.

### Potential Task 5: Music Stimulus Identification (90-Class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 21.0 s, overlap = 0.0, target_events = [`101`, `102`, `103`, `104`, `105`, `106`, `107`, `108`, `109`, `110`, `113`, `114`, `115`, `116`, `117`, `118`, `119`, `120`, `121`, `122`, `125`, `126`, `127`, `128`, `129`, `130`, `131`, `132`, `133`, `134`, `137`, `138`, `139`, `140`, `141`, `142`, `143`, `144`, `145`, `146`, `149`, `150`, `151`, `152`, `153`, `154`, `155`, `156`, `157`, `158`, `161`, `162`, `163`, `164`, `165`, `166`, `167`, `168`, `169`, `170`, `173`, `174`, `175`, `176`, `177`, `178`, `179`, `180`, `181`, `182`, `185`, `186`, `187`, `188`, `189`, `190`, `191`, `192`, `193`, `194`, `197`, `198`, `199`, `200`, `201`, `202`, `203`, `204`, `205`, `206`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `101` | 0 | stimulus item 1 |
  | `102` | 1 | stimulus item 2 |
  | `103` | 2 | stimulus item 3 |
  | `104` | 3 | stimulus item 4 |
  | `105` | 4 | stimulus item 5 |
  | `106` | 5 | stimulus item 6 |
  | `107` | 6 | stimulus item 7 |
  | `108` | 7 | stimulus item 8 |
  | `109` | 8 | stimulus item 9 |
  | `110` | 9 | stimulus item 10 |
  | `113` | 10 | stimulus item 13 |
  | `114` | 11 | stimulus item 14 |
  | `115` | 12 | stimulus item 15 |
  | `116` | 13 | stimulus item 16 |
  | `117` | 14 | stimulus item 17 |
  | `118` | 15 | stimulus item 18 |
  | `119` | 16 | stimulus item 19 |
  | `120` | 17 | stimulus item 20 |
  | `121` | 18 | stimulus item 21 |
  | `122` | 19 | stimulus item 22 |
  | `125` | 20 | stimulus item 25 |
  | `126` | 21 | stimulus item 26 |
  | `127` | 22 | stimulus item 27 |
  | `128` | 23 | stimulus item 28 |
  | `129` | 24 | stimulus item 29 |
  | `130` | 25 | stimulus item 30 |
  | `131` | 26 | stimulus item 31 |
  | `132` | 27 | stimulus item 32 |
  | `133` | 28 | stimulus item 33 |
  | `134` | 29 | stimulus item 34 |
  | `137` | 30 | stimulus item 37 |
  | `138` | 31 | stimulus item 38 |
  | `139` | 32 | stimulus item 39 |
  | `140` | 33 | stimulus item 40 |
  | `141` | 34 | stimulus item 41 |
  | `142` | 35 | stimulus item 42 |
  | `143` | 36 | stimulus item 43 |
  | `144` | 37 | stimulus item 44 |
  | `145` | 38 | stimulus item 45 |
  | `146` | 39 | stimulus item 46 |
  | `149` | 40 | stimulus item 49 |
  | `150` | 41 | stimulus item 50 |
  | `151` | 42 | stimulus item 51 |
  | `152` | 43 | stimulus item 52 |
  | `153` | 44 | stimulus item 53 |
  | `154` | 45 | stimulus item 54 |
  | `155` | 46 | stimulus item 55 |
  | `156` | 47 | stimulus item 56 |
  | `157` | 48 | stimulus item 57 |
  | `158` | 49 | stimulus item 58 |
  | `161` | 50 | stimulus item 61 |
  | `162` | 51 | stimulus item 62 |
  | `163` | 52 | stimulus item 63 |
  | `164` | 53 | stimulus item 64 |
  | `165` | 54 | stimulus item 65 |
  | `166` | 55 | stimulus item 66 |
  | `167` | 56 | stimulus item 67 |
  | `168` | 57 | stimulus item 68 |
  | `169` | 58 | stimulus item 69 |
  | `170` | 59 | stimulus item 70 |
  | `173` | 60 | stimulus item 73 |
  | `174` | 61 | stimulus item 74 |
  | `175` | 62 | stimulus item 75 |
  | `176` | 63 | stimulus item 76 |
  | `177` | 64 | stimulus item 77 |
  | `178` | 65 | stimulus item 78 |
  | `179` | 66 | stimulus item 79 |
  | `180` | 67 | stimulus item 80 |
  | `181` | 68 | stimulus item 81 |
  | `182` | 69 | stimulus item 82 |
  | `185` | 70 | stimulus item 85 |
  | `186` | 71 | stimulus item 86 |
  | `187` | 72 | stimulus item 87 |
  | `188` | 73 | stimulus item 88 |
  | `189` | 74 | stimulus item 89 |
  | `190` | 75 | stimulus item 90 |
  | `191` | 76 | stimulus item 91 |
  | `192` | 77 | stimulus item 92 |
  | `193` | 78 | stimulus item 93 |
  | `194` | 79 | stimulus item 94 |
  | `197` | 80 | stimulus item 97 |
  | `198` | 81 | stimulus item 98 |
  | `199` | 82 | stimulus item 99 |
  | `200` | 83 | stimulus item 100 |
  | `201` | 84 | stimulus item 101 |
  | `202` | 85 | stimulus item 102 |
  | `203` | 86 | stimulus item 103 |
  | `204` | 87 | stimulus item 104 |
  | `205` | 88 | stimulus item 105 |
  | `206` | 89 | stimulus item 106 |
- **Evidence**:
  - analysis.md Event Structure - musicPlayed markers (codes 101-209, minus gaps) indicate specific stimulus items with 18-19 trials each
  - analysis.md Data Quality Notes - explicitly notes this as "Potential Task 8" involving 90 classes with ~18-19 trials each, severely underpowered
- **Notes**: Classification of which specific music stimulus was played based on EEG response. This task is severely underpowered with only ~18-19 trials per class across 90 classes, as noted in Data Quality Notes. Some stimulus codes are missing from the sequence (e.g., 111-112, 123-124, etc.), resulting in non-contiguous numbering. Listed as Potential due to severe class imbalance and underpowered design.

## Data Quality Notes

- Event ID 8 (neutral valence, high arousal) is defined in the events.json sidecar but has zero occurrences across all files, reducing the 3×3 design to 8 observed affective conditions.
- The `device` field is completely missing from Info metadata, limiting hardware traceability.
- GSR channel units are unspecified in available metadata and require verification (μS vs. arbitrary units).
- Event counts show slight imbalance across affective conditions (e.g., 125 for ID 1 vs. 368 for ID 9), which may affect classification performance.
- Music piece identification task (Potential Task 8) involves 90 classes with only ~18-19 trials each, making it severely underpowered.
- The README mentions 40-second music clips while events.tsv shows duration=21s, indicating a discrepancy between documentation and actual trial structure; the 21s value from events.tsv is used for epoching.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Auditory evoked potential EEG-Biometric dataset

**Dataset**: `physionet_auditoryeeg` | **Year**: 2021 | **URL**: https://physionet.org/content/auditory-eeg/1.0.0/
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 205 | **Channels**: 4 | **Sampling Rate**: 200 Hz | **Manual Review**: Shu Peng

## Paradigm

Twenty volunteers (s01-s20) aged 21-31 participated in a multipurpose EEG study involving resting-state and auditory stimulus paradigms, completing all tasks in a single day while seated comfortably. EEG data was recorded at a 200 Hz sampling rate using an OpenBCI Ganglion board with four gold-cup electrodes (T7, F8, Cz, P4) positioned according to the 10/10 international system, alongside ear-placed reference and ground electrodes. The recording conditions consisted of three-minute sessions for resting states (eyes open, eyes closed) and six auditory stimulus tasks. For the auditory stimuli, subjects listened to a native song, a non-native song (Arabic for Italian subjects, and Italian for non-Italian subjects), and neutral instrumental music, which were delivered via both in-ear and bone-conducting headphones.

## File Scan Result

> **Kernel SHA256**: `f2baba5ab9eae9018027474a4a0fd04e526a9b49f98707e5b415b7e04bf76e9a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `auditory_native_song_bone` | 120 | event | raw | Native song via bone-conduction headphones (ex08) |
| `auditory_native_song_in_ear` | 120 | event | raw | Native-language song via in-ear headphones (ex05) |
| `auditory_neutral_music_bone` | 120 | event | raw | Neutral instrumental music via bone-conduction headphones (ex10) |
| `auditory_neutral_music_in_ear` | 120 | event | raw | Neutral instrumental music via in-ear headphones (ex07) |
| `auditory_nonnative_song_bone` | 120 | event | raw | Non-native song via bone-conduction headphones (ex09) |
| `auditory_nonnative_song_in_ear` | 120 | event | raw | Non-native language song via in-ear headphones (ex06) |
| `resting_eyes_closed` | 360 | event | raw | Resting state with eyes closed (ex02) |
| `resting_eyes_open` | 358 | event | raw | Resting state with eyes open (ex01) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (1438/2166) | e.g. 27, 23, 26 |
| `amplifier` | partial (1438/2166) | e.g. OpenBCI Ganglion Board |
| `cap` | partial (1438/2166) | e.g. gold-cup electrodes with Ten20 conductive paste |
| `device` | partial (1438/2166) | e.g. OpenBCI Ganglion Board, a 4-channel EEG acquisition system sampling at 200 Hz, with gold-cup electrodes at T7, F8, Cz, and P4 using Ten20 conductive paste and OpenBCI GUI v5.0.3. |
| `handedness` | missing | N/A |
| `sex` | partial (1438/2166) | e.g. male, female |


## Tasks

### Potential Task 1: Experimental Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_closed`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open |
  | `resting_eyes_closed` | 1 | Resting state eyes closed |
  | `auditory_native_song_in_ear` | 2 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 3 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 4 | Neutral music in-ear |
  | `auditory_native_song_bone` | 5 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 6 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 7 | Neutral music bone-conduction |
- **Evidence**:
  - Event Structure table shows 8 file-supported experimental conditions with event-level annotations spanning entire recordings
  - Paradigm section describes resting-state conditions and six auditory stimulus conditions
- **Notes**: Noise-isolation conditions are excluded because no corresponding scanable records are present in the local `RECORDS`/file inventory. Each annotation spans the full recording file; long-event epoching with 30s windows captures sustained state. Primary dataset purpose is biometric identification, but condition classification is derivable from event labels.

### Potential Task 2: Eyes-Open Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open baseline |
  | `auditory_native_song_in_ear` | 1 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 2 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 3 | Neutral music in-ear |
  | `auditory_native_song_bone` | 4 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 5 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 6 | Neutral music bone-conduction |
- **Evidence**:
  - Event Structure table provides event IDs for eyes-open resting and auditory conditions
  - Paradigm notes eyes-open resting and all auditory conditions use comparable alertness state
- **Notes**: Excludes `resting_eyes_closed` to control for eye-state confound and excludes unavailable noise-isolation records. Useful for comparing auditory delivery methods while holding eye state constant.

### Potential Task 3: Binary Resting vs. Auditory Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_closed`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting (any state) |
  | `resting_eyes_closed` | 0 | Resting (any state) |
  | `auditory_native_song_in_ear` | 1 | Auditory stimulation |
  | `auditory_nonnative_song_in_ear` | 1 | Auditory stimulation |
  | `auditory_neutral_music_in_ear` | 1 | Auditory stimulation |
  | `auditory_native_song_bone` | 1 | Auditory stimulation |
  | `auditory_nonnative_song_bone` | 1 | Auditory stimulation |
  | `auditory_neutral_music_bone` | 1 | Auditory stimulation |
- **Evidence**:
  - Paradigm describes two major condition classes: resting-state and auditory stimulus paradigms
  - Event Structure provides sufficient counts for both super-classes
- **Notes**: Collapses 8 file-supported conditions into 2 superordinate categories. Useful for the simplest baseline task before finer-grained condition classification.

### Potential Task 4: In-Ear vs. Bone-Conduction Headphone Comparison
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `auditory_native_song_in_ear` | 0 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 0 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 0 | Neutral music in-ear |
  | `auditory_native_song_bone` | 1 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 1 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 1 | Neutral music bone-conduction |
- **Evidence**:
  - Paradigm explicitly contrasts in-ear vs. bone-conduction headphone delivery
  - Event Structure contains matched stimulus types across both delivery methods
- **Notes**: Uses all six file-supported auditory events as a binary delivery-method task: in-ear (`y=0`) versus bone-conduction (`y=1`). Compares neural response to matched stimulus categories via different transduction pathways.

## Data Quality Notes

- Only 4 EEG channels (non-standard OpenBCI placement); spatial coverage is limited.
- Primary use case is biometric identification (same person across sessions), not condition classification; adapt label source accordingly.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 119 | **Channels**: 63 | **Sampling Rate**: 5000 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimates were collected using a visual analogue scale (VAS). High sampling rate (5000 Hz) requires downsampling before epoching.

## File Scan Result

> **Kernel SHA256**: `403e1d8a5bd902759e4807d4044828a390140b5e3a2c32f52438f071182964ef`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Response/R128` | 44303 | event | raw | Response trigger |
| `Stimulus/S  7` | 1347 | event | raw | Trial phase onset: stimulus marker 7 |
| `Stimulus/S  8` | 1477 | event | raw | Trial phase onset: stimulus marker 8 |
| `Stimulus/S 11` | 2851 | event | raw | Trial phase onset: stimulus marker 11 |
| `Stimulus/S 12` | 2854 | event | raw | Trial phase onset: stimulus marker 12 |
| `Stimulus/S 17` | 1356 | event | raw | Trial phase onset: stimulus marker 17 |
| `Stimulus/S 18` | 1489 | event | raw | Trial phase onset: stimulus marker 18 |
| `Stimulus/S 27` | 5657 | event | raw | Trial phase onset: stimulus marker 27 |
| `Stimulus/S 37` | 120 | event | raw | Trial phase onset: stimulus marker 37 |
| `Stimulus/S 38` | 109 | event | raw | Trial phase onset: stimulus marker 38 |
| `Stimulus/S 40` | 6175 | event | raw | Trial phase onset: stimulus marker 40 |
| `Stimulus/S 41` | 5703 | event | raw | Trial phase onset: stimulus marker 41 |
| `Stimulus/S 43` | 6583 | event | raw | Trial phase onset: stimulus marker 43 |
| `Stimulus/S 44` | 475 | event | raw | Trial phase onset: stimulus marker 44 |
| `Stimulus/S128` | 474612 | event | raw | Continuous sampling trigger |
| `Stimulus/S140` | 3 | event | raw | Trial phase onset: stimulus marker 140 |
| `Stimulus/S145` | 1 | event | raw | Trial phase onset: stimulus marker 145 |
| `Stimulus/S155` | 2 | event | raw | Trial phase onset: stimulus marker 155 |
| `Stimulus/S165` | 39 | event | raw | Trial phase onset: stimulus marker 165 |
| `Stimulus/S166` | 48 | event | raw | Trial phase onset: stimulus marker 166 |
| `Stimulus/S169` | 1 | event | raw | Trial phase onset: stimulus marker 169 |
| `Stimulus/S171` | 4364 | event | raw | Trial phase onset: stimulus marker 171 |
| `SyncStatus/Sync On` | 30864 | admin | raw | Synchronization trigger onset |


> 1. The experimental paradigm of the paper consists of an active/observation dual-condition design (lines 655–659 of the paper), with trials alternating within blocks (4 blocks per run, alternating between active and observation). The type of all trials is a fixed attribute of the experimental design and is not ‘unknown’;  
> 2.  The key events in the trial sequences described in the paper (start of gaze, start of stimulus, start of response, start of masking, start of confidence scale) are all clearly defined experimental marker events; there are no ‘unknown events’ serving as core epoch anchors or trial markers, and the ‘unknown’ Event ID has no basis in the paper.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Mean age = 24.6 ± 1.43 y |
| `sex` | complete | Twenty-five healthy volunteers (12 females) |
| `device` | missing | EEG Recording: Data acquired via BrainVision system; MR-gradient artifacts removed via sliding window template subtraction. BCG artifacts removed using TP10 electrode (right mastoid) with semi-automatic procedure. Preprocessing included 1-10 Hz Butterworth filter (4th order zero-phase), [-0.2, 0.6] s epoching around response onset, common average reference, and ICA for artifact removal (EEGLAB/MATLAB). fMRI Recording: Structural (T1) and functional MRI data included; preprocessed using fMRIPrep with GLM analysis for BOLD signal estimation. |


## Tasks

### Classical Task 1: Binary Classification of Perceptual Decision Accuracy
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`, `Stimulus/S 27`, `Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stimulus/S 40` | 0 | Correct perceptual decision |
  | `Stimulus/S 41` | 1 | Correct perceptual decision |
  | `Stimulus/S 43` | 2 | Correct perceptual decision |
  | `Stimulus/S 27` | 3 | Correct perceptual decision |
  | `Stimulus/S 11` | 4 | Erroneous perceptual decision |
  | `Stimulus/S 12` | 5 | Erroneous perceptual decision |
  | `Stimulus/S 17` | 6 | Erroneous perceptual decision |
  | `Stimulus/S 18` | 7 | Erroneous perceptual decision |
- **Evidence**:
  - 10.1073/pnas.1918335117 - Binary classification of correct vs. erroneous perceptual decisions with eight stimulus markers mapped to two accuracy classes
  - 10.1038/s41467-021-23540-y - Binary classification of choice accuracy with epochs -0.2s to 1.5s relative to stimulus onset
  - 10.7554/eLife.53900 - Binary classification of first-order choice accuracy using trial-locked EEG epochs with correct (S 40/41/43/27) and erroneous (S 11/12/17/18) decision markers
- **Notes**: The eight stimulus markers are pooled into two classes reflecting speeded perceptual decision outcomes. The 5000 Hz sampling rate requires downsampling before epoching. The `Response/R128` event was excluded from target_events despite appearing in one reference because the primary epoching is stimulus-locked per the majority of sources; response-locked analyses are secondary.

### Classical Task 2: Segmentation-Based Analysis for Resting-State Sessions
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - openneuro_ds002158 — Resting-state sessions lack all event markers (no events.tsv, no .vmrk), enforcing segmentation-based approaches only for those files
- **Notes**: This task serves as a fallback for resting-state sessions that lack event markers entirely. The `sex` field is complete across all participants. Classification is binary with two distinct classes. The `age` field could alternatively be used for regression (Potential Task), but the age range in a sample of 20 participants may be limited. This task is explicitly segmentation-based with empty target_events as required.

## Data Quality Notes

- Extremely high sampling rate (5000 Hz) requires substantial downsampling before practical analysis; native resolution is well above typical EEG analysis needs and will increase computational load and storage requirements significantly.
- Large number of continuous sampling triggers (`Stimulus/S128`, 474612 events) indicates a feedback or rating device sending dense markers during confidence VAS periods; these must be excluded from epoching to avoid contaminating trial-locked analyses.
- fMRI-EEG synchronization pulses (`SyncStatus/Sync On`, 30864 events) present as admin markers; these require filtering during event extraction for pure EEG analyses.
- `device` field is missing from info metadata, limiting hardware documentation for reproducibility.
- Event meanings for stimulus markers are inferred from paper and events.tsv mappings rather than explicit documentation in sidecar files; kernel must validate mappings against actual `events.tsv` trial_type columns.
- Resting-state sessions lack all event markers (no events.tsv, no .vmrk), enforcing segmentation-based approaches only for those files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# EEG During Mental Arithmetic Task

**Dataset**: `physionet_eegmat` | **Year**: 2018 | **URL**: https://physionet.org/content/eegmat/1.0.0/
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 23 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

Thirty-six healthy subjects (Subject00-Subject35, ages 16-26, predominantly female) completed a mental arithmetic task while EEG was recorded monopolarly using a Neurocom 23-channel system with Ag/AgCl electrodes (Zyma et al., 2019). Each subject contributed two files: a background resting-state recording (suffix `_1.edf`) and a mental arithmetic task recording (suffix `_2.edf`). During the mental arithmetic task, subjects performed serial subtraction (e.g., 3141 minus 42) while EEG was recorded. A separate `Count quality` field in `subject-info.csv` rates the subject's arithmetic performance as Good or Bad, providing a behavioral quality label.

## File Scan Result

> **Kernel SHA256**: `2d377403dfb36e0b6ad6454cf2d69b00d8096cf9a7ebb560a8baff950dedaad6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Background EEG;Count Quality: Bad` | 12 | event | raw | Resting-state recording with poor arithmetic performance label |
| `Background EEG;Count Quality: Good` | 24 | event | raw | Resting-state recording with good arithmetic performance label |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 12 | event | raw | Mental arithmetic task recording with poor performance label |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 24 | event | raw | Mental arithmetic task recording with good performance label |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Age range: 16–26 years, mean age: approximately 18.33 years |
| `sex` | complete | Males (M): 8, females (F): 28, predominantly female |
| `device` | missing | EEG was recorded using a 23-channel Neurocom monopolar system (XAI-MEDICA, Ukraine) with silver/silver chloride electrodes placed per the international 10–20 system, linked ear reference, 500 Hz sampling rate, 0.5–45 Hz bandpass filtering, 50 Hz notch filtering, and electrode impedance kept below 5 kΩ. |


## Tasks

### Classical Task 1: Mental Arithmetic vs Rest Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Resting-state, bad quality |
  | `Background EEG;Count Quality: Good` | 1 | Resting-state, good quality |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 2 | Mental arithmetic, bad quality |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 3 | Mental arithmetic, good quality |
- **Evidence**:
  - Paradigm section describes two conditions: background resting-state (`_1.edf`) and mental arithmetic task (`_2.edf`)
  - Event Structure table confirms four event types combining condition and count quality
- **Notes**: Binary classification of cognitive state (rest vs mental arithmetic), collapsing across count quality. Long epochs (60s) assumed to capture full recording duration; adjust if actual durations differ.

### Classical Task 2: Mental Arithmetic Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor arithmetic performance |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good arithmetic performance |
- **Evidence**:
  - Paradigm section states `Count quality` field rates arithmetic performance as Good or Bad
  - Event Structure table shows 10 Bad and 26 Good mental arithmetic recordings
- **Notes**: Classifies arithmetic performance quality during mental arithmetic task only. Excludes background recordings. Imbalanced classes (10 vs 26).

### Classical Task 3: Resting-State Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Poor arithmetic performance (rest) |
  | `Background EEG;Count Quality: Good` | 1 | Good arithmetic performance (rest) |
- **Evidence**:
  - Paradigm section notes count quality is a behavioral label from `subject-info.csv`
  - Event Structure table shows 10 Bad and 26 Good background recordings
- **Notes**: Investigates whether arithmetic quality correlates with resting-state EEG patterns. Same subjects in both conditions, so quality label is subject-level. Imbalanced classes (10 vs 26).

### Classical Task 4: Four-Way Condition-Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Rest, bad quality |
  | `Background EEG;Count Quality: Good` | 1 | Rest, good quality |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 2 | Task, bad quality |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 3 | Task, good quality |
- **Evidence**:
  - Paradigm describes full 2x2 design: condition (rest/task) x quality (good/bad)
  - Event Structure table provides all four combinations
- **Notes**: Multi-class extension exploring interaction between cognitive state and performance quality. Very imbalanced (10/26/10/26). May require stratified sampling or class weighting.

### Potential Task 1: Subject Age Regression from Mental Arithmetic
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - Paradigm section notes ages 16-26
  - Info table confirms `age` is complete
- **Notes**: Predicts subject age from mental arithmetic EEG. Requires pairing event epochs with info metadata by subject ID. Age range is narrow (10 years), limiting regression difficulty.

### Potential Task 2: Subject Sex Classification from Mental Arithmetic
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | no mapping |
- **Evidence**:
  - Paradigm notes predominantly female subjects
  - Info table confirms `sex` is complete
- **Notes**: Binary sex classification from mental arithmetic EEG. Predominantly female sample may cause class imbalance. Requires super meta pairing with subject info.

### Potential Task 3: Continuous Quality Regression (Rest Condition)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Bad quality label |
  | `Background EEG;Count Quality: Good` | 1 | Good quality label |
- **Evidence**:
  - Event Structure provides binary quality labels embedded in event descriptions
  - Paradigm notes count quality is behavioral performance metric
- **Notes**: Treats binary quality as pseudo-continuous regression target (0/1) using sliding windows. Alternative formulation of Task 3. Overlap creates more samples from limited data.

### Potential Task 4: Continuous Quality Regression (Task Condition)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |---|---|---|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Bad quality label |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good quality label |
- **Evidence**:
  - Same evidence as Potential Task 3, applied to mental arithmetic condition
  - Event Structure confirms task condition events with quality labels
- **Notes**: Regression formulation of Task 2. Sliding window approach for more samples. Quality label is subject-level, so all windows from same subject share identical target.

## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2015 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants viewed famous faces, unfamiliar faces, and scrambled faces while making a left/right subjective symmetry judgment. Each image was presented twice, with the second presentation occurring either immediately (early lag) or after a delay (late lag). The EEGLAB repackaging merged the original runs, corrected event latencies, resampled the EEG to 250 Hz, and retained stimulus identity, response side/symmetry, presentation order, and repetition distance information in the event table. This is based on the SPM multimodal face dataset (ds000117).

## File Scan Result

> **Kernel SHA256**: `d59146ae08cacb638e8c260abb81f84cd24c60b8571ab63d8e1787ba6c5614e6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `boundary` | 90 | admin | raw | Run boundary marker indicating boundary between merged runs |
| `famous_new` | 2700 | event | raw | Initial presentation of famous face |
| `famous_second_early` | 1313 | event | raw | Immediate repeated presentation of famous face |
| `famous_second_late` | 1291 | event | raw | Delayed repeated presentation of famous face |
| `left_nonsym` | 3532 | event | raw | Left button press to indicate less symmetric face |
| `left_sym` | 3381 | event | raw | Left button press to indicate more symmetric face |
| `right_nonsym` | 3616 | event | raw | Right button press to indicate less symmetric face |
| `right_sym` | 4900 | event | raw | Right button press to indicate more symmetric face |
| `scrambled_new` | 2700 | event | raw | Initial presentation of scrambled face |
| `scrambled_second_early` | 1271 | event | raw | Immediate repeated presentation of scrambled face |
| `scrambled_second_late` | 1334 | event | raw | Delayed repeated presentation of scrambled face |
| `unfamiliar_new` | 2700 | event | raw | Initial presentation of unfamiliar face |
| `unfamiliar_second_early` | 1304 | event | raw | Immediate repeated presentation of unfamiliar face |
| `unfamiliar_second_late` | 1316 | event | raw | Delayed repeated presentation of unfamiliar face |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | partial (13/18) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 3-class face category classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `scrambled_new`, `unfamiliar_new`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Initial presentation of famous face |
  | `unfamiliar_new` | 1 | Initial presentation of unfamiliar face |
  | `scrambled_new` | 2 | Initial presentation of scrambled face |
- **Evidence**:
  - 10.1038/sdata.2015.1 — Original dataset publication describing face processing paradigm with famous, unfamiliar, and scrambled face conditions
  - 10.3389/fnins.2019.00300 — Reference describing standard ERP analysis and N170/M170 component analysis in face processing
- **Notes**: Three-category classification of initial face presentations only (excluding repeated presentations to avoid priming effects). Famous and unfamiliar faces are both intact faces, while scrambled faces serve as a low-level visual control. The N170/M170 ERP components at ~170ms are the primary neural markers distinguishing these conditions.

### Potential Task 1: 9-class face presentation type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Initial presentation of famous face |
  | `famous_second_early` | 1 | Immediate repeated presentation of famous face |
  | `famous_second_late` | 2 | Delayed repeated presentation of famous face |
  | `scrambled_new` | 3 | Initial presentation of scrambled face |
  | `scrambled_second_early` | 4 | Immediate repeated presentation of scrambled face |
  | `scrambled_second_late` | 5 | Delayed repeated presentation of scrambled face |
  | `unfamiliar_new` | 6 | Initial presentation of unfamiliar face |
  | `unfamiliar_second_early` | 7 | Immediate repeated presentation of unfamiliar face |
  | `unfamiliar_second_late` | 8 | Delayed repeated presentation of unfamiliar face |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines all 9 face presentation trial_type levels with meanings for new, second_early, and second_late presentations across famous, scrambled, and unfamiliar face categories
- **Notes**: 9-way classification distinguishing both face category (famous/scrambled/unfamiliar) and repetition status (new/immediate repeat/delayed repeat). ~2700 new presentations and ~1300 each for early/late repeats per category. Epoch window inferred from standard face ERP paradigms; repetition effects (e.g., N250r) may appear in later time windows but standard -200 to 1000 ms epoching captures the core face-evoked response.

### Potential Task 2: 3-class face repetition status classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | New face presentation (first occurrence) |
  | `unfamiliar_new` | 0 | New face presentation (first occurrence) |
  | `scrambled_new` | 0 | New face presentation (first occurrence) |
  | `famous_second_early` | 1 | Early/immediate repetition |
  | `unfamiliar_second_early` | 1 | Early/immediate repetition |
  | `scrambled_second_early` | 1 | Early/immediate repetition |
  | `famous_second_late` | 2 | Late/delayed repetition |
  | `unfamiliar_second_late` | 2 | Late/delayed repetition |
  | `scrambled_second_late` | 2 | Late/delayed repetition |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: new (famous_new/unfamiliar_new/scrambled_new), early repeat (famous_second_early/unfamiliar_second_early/scrambled_second_early), late repeat (famous_second_late/unfamiliar_second_late/scrambled_second_late) with explicit descriptions of initial, immediate repeated, and delayed repeated presentations
  - events.tsv samples — Confirm event values and face_type columns distinguish face categories; event_type='faces' for all stimulus presentations
- **Notes**: Collapses across all three face categories (famous, unfamiliar, scrambled) to isolate repetition status effects. This tests neural signatures of repetition suppression/priming independent of face familiarity. ~8100 new, ~3900 early, ~3940 late trials across 18 subjects. Epoch window (-0.2, 1.0)s captures baseline and sustained post-stimulus activity where repetition effects are expected.

### Potential Task 3: Famous vs Unfamiliar Face Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Famous face (initial presentation) |
  | `famous_second_early` | 0 | Famous face (immediate repeat) |
  | `famous_second_late` | 0 | Famous face (delayed repeat) |
  | `unfamiliar_new` | 1 | Unfamiliar face (initial presentation) |
  | `unfamiliar_second_early` | 1 | Unfamiliar face (immediate repeat) |
  | `unfamiliar_second_late` | 1 | Unfamiliar face (delayed repeat) |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: famous_new, famous_second_early, famous_second_late as "famous face" presentations; unfamiliar_new, unfamiliar_second_early, unfamiliar_second_late as "unfamiliar face" presentations. All face presentation events have event_type='faces'.
  - events.tsv sample (sub-002) — Confirms event values: famous_new=5, unfamiliar_new=13, with face_type column distinguishing 'famous' vs 'unfamiliar'.
  - eeg.json — TaskDescription confirms famous vs unfamiliar vs scrambled face photographs presented for 800-1000 ms.
- **Notes**: Collapses repetition status (new/second_early/second_late) within each face type to create a binary famous vs unfamiliar classification. The ~5300 presentations per class provide balanced trials. The N250 and later ERP components are known to differentiate familiar from unfamiliar faces.

### Potential Task 4: 4-class symmetry judgment classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | Left button press, more symmetric |
  | `left_nonsym` | 1 | Left button press, less symmetric |
  | `right_sym` | 2 | Right button press, more symmetric |
  | `right_nonsym` | 3 | Right button press, less symmetric |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels with `left_sym`: "Left button press to indicated more symmetric face", `left_nonsym`: "Left button press to indicated less symmetric face", `right_sym`: "Right button press to indicated more symmetric face", `right_nonsym`: "Right button press to indicated less symmetric face"
  - eeg.json TaskDescription — Subjects pressed left or right key based on symmetry judgment (more/less symmetric than average), with key assignment counter-balanced across participants
  - events.tsv sample — Confirms button press events appear with trial_type values `left_sym`, `left_nonsym`, `right_sym`, `right_nonsym` and event_type='button_press'
- **Notes**: This is effectively a 4-class motor response classification task. The left/right mapping to 'more'/'less symmetric' was counterbalanced across subjects, so the semantic symmetry judgment is confounded with motor response. The task classifies the specific button press type (left/right × sym/nonsym). ~15,400 total button presses across 18 subjects. Epoch window includes pre-stimulus baseline (-0.5s) to capture readiness potential and 1.0s post-press for motor execution and post-movement rebound.

### Potential Task 5: 2-class symmetry response classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | more symmetric response |
  | `right_sym` | 0 | more symmetric response |
  | `left_nonsym` | 1 | less symmetric response |
  | `right_nonsym` | 1 | less symmetric response |
- **Evidence**:
  - task-FaceRecognition_events.json — trial_type Levels define left_sym/right_sym as "more symmetric face" and left_nonsym/right_nonsym as "less symmetric face"
  - eeg.json TaskDescription — participants pressed one of two keys based on symmetry judgment ('more' or 'less symmetric' than average), with left/right assignment counter-balanced across participants
  - README — events were renamed taking into account button assigned to each subject, confirming subject-specific counterbalancing
  - sub-002_task-FaceRecognition_events.tsv sample — shows left_nonsym (value=256) and right_sym (value=4096) co-occurring, confirming semantic labels are already remapped per subject in BIDS version
- **Notes**: This task collapses across left/right hand responses to create a binary symmetry judgment classification. The BIDS version of this dataset already has subject-specific remapping applied (per README: "Renaming events taking into account button assigned to each subject"), so left_sym/right_sym consistently mean "more symmetric" and left_nonsym/right_nonsym consistently mean "less symmetric" across all subjects. The epoch window includes a pre-stimulus baseline (-0.5s) to capture decision-related activity that may precede the motor response, with post-response window (1.0s) to capture motor execution and reafferent activity. ~8300 'more symmetric' vs ~7100 'less symmetric' responses total.

### Potential Task 6: 2-class motor response laterality
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | Left hand motor response |
  | `left_nonsym` | 0 | Left hand motor response |
  | `right_sym` | 1 | Right hand motor response |
  | `right_nonsym` | 1 | Right hand motor response |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines `left_sym` and `left_nonsym` as left button presses, `right_sym` and `right_nonsym` as right button presses; all button presses use values 256 (left) and 4096 (right) with counterbalanced semantic labels across subjects.
  - events.tsv sample (sub-002) — Confirms `left_nonsym` and `right_sym` events present with value 256 and 4096 respectively, event_type='button_press'.
  - README — Describes task requiring left or right index finger key-press based on symmetry judgment, with assignment counter-balanced across participants.
- **Notes**: Motor lateralization task collapsing across the semantic judgment (symmetric vs non-symmetric). All left button presses (regardless of meaning) map to y=0, all right button presses map to y=1. This yields a pure motor response laterality classification (~6900 left vs ~8500 right responses).

### Potential Task 7: face vs scrambled classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | intact face (famous, first presentation) |
  | `famous_second_early` | 0 | intact face (famous, immediate repeat) |
  | `famous_second_late` | 0 | intact face (famous, delayed repeat) |
  | `unfamiliar_new` | 0 | intact face (unfamiliar, first presentation) |
  | `unfamiliar_second_early` | 0 | intact face (unfamiliar, immediate repeat) |
  | `unfamiliar_second_late` | 0 | intact face (unfamiliar, delayed repeat) |
  | `scrambled_new` | 1 | scrambled face (first presentation) |
  | `scrambled_second_early` | 1 | scrambled face (immediate repeat) |
  | `scrambled_second_late` | 1 | scrambled face (delayed repeat) |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: famous_new/unfamiliar_new as intact faces, scrambled_new as scrambled faces; all second_early/second_late variants are repetition conditions of same face types
  - eeg.json — TaskDescription confirms stimuli were "photographs of either a famous face or a scrambled face"
- **Notes**: All famous and unfamiliar face events (new and both repeat types) merged to y=0 (intact faces); all scrambled face events (new and both repeat types) merged to y=1 (scrambled faces). Tests configural/holistic face processing via N170 sensitivity to face vs scrambled distinction. ~10,600 intact face vs ~5,300 scrambled face presentations total across 18 subjects.

### Potential Task 8: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — age column with values 23–31 years, partial completeness (13/18 subjects)
- **Notes**: Segmentation-based subject-level trait prediction. Non-overlapping 2-second windows from continuous EEG are used to predict subject age. No event alignment needed; the full continuous recording is segmented. Age is a native participants.tsv column (B3 archetype, raw meta level). Subjects with missing age data will be excluded by the kernel.

### Potential Task 9: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:

- **Notes**: Subject-level binary classification using 2-second non-overlapping windows of continuous EEG. Gender is a native participants.tsv column with partial coverage (13/18 subjects: 7 M, 6 F). The kernel does not need to derive any new channels; labels are read directly from the BIDS participants sidecar.

## Data Quality Notes

- `sex` is only partially complete (13/18 subjects), with 5 subjects missing gender/sex information.
- `device` field is completely missing from dataset metadata, limiting hardware reproducibility.
- Event counts for `famous_second_early` (1313) and `famous_second_late` (1291) do not sum exactly to `famous_new` (2700), indicating minor data loss or exclusion during preprocessing (similar pattern for other categories).
- The `boundary` events (90 total, 5 per subject) indicate merged runs from the original acquisition; users should verify no edge artifacts at boundaries.
- Button press event counts are unbalanced (`right_sym` = 4900 vs `left_nonsym` = 3532), reflecting response bias or task design asymmetry rather than data quality issue.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2017/2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale developmental EEG battery collected from children and adolescents. This release includes six paradigms: naturalistic movie watching, resting state with alternating eyes-open and eyes-closed periods, contrast change detection, surround suppression, sequence learning, and symbol search. For the current benchmark draft, we keep only the tasks that have strong grounding in the release documentation and can be implemented directly from native events or narrowly defined kernel derivations.

## File Scan Result

> **Kernel SHA256**: `d2a20370c75e70aa962603af5a1b27b44532d88150c49839b32b4d27ebabb160`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1136 | admin | raw | Administrative recording/session marker |
| `boundary` | 728 | admin | raw | EEGLAB/BIDS boundary or discontinuity marker, not a stimulus class |
| `break cnt` | 1488 | admin | raw | Administrative break counter marker, often at recording onset |
| `contrastChangeB1_start` | 102 | event | raw | Start of contrast change detection block/run 1 |
| `contrastChangeB2_start` | 117 | event | raw | Start of contrast change detection block/run 2 |
| `contrastChangeB3_start` | 143 | event | raw | Start of contrast change detection block/run 3 |
| `contrastTrial_start` | 8884 | event | raw | Start of a single contrast change detection trial |
| `contrast_response_correct` | 6588 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 731 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 600 | event | raw | Dot position 1 offset in sequence learning |
| `dot_no1_ON` | 600 | event | raw | Dot position 1 onset in sequence learning |
| `dot_no2_OFF` | 1202 | event | raw | Dot position 2 offset in sequence learning |
| `dot_no2_ON` | 1234 | event | raw | Dot position 2 onset in sequence learning |
| `dot_no3_OFF` | 600 | event | raw | Dot position 3 offset in sequence learning |
| `dot_no3_ON` | 624 | event | raw | Dot position 3 onset in sequence learning |
| `dot_no4_OFF` | 600 | event | raw | Dot position 4 offset in sequence learning |
| `dot_no4_ON` | 600 | event | raw | Dot position 4 onset in sequence learning |
| `dot_no5_OFF` | 600 | event | raw | Dot position 5 offset in sequence learning |
| `dot_no5_ON` | 600 | event | raw | Dot position 5 onset in sequence learning |
| `dot_no6_OFF` | 600 | event | raw | Dot position 6 offset in sequence learning |
| `dot_no6_ON` | 600 | event | raw | Dot position 6 onset in sequence learning |
| `dot_no7_OFF` | 793 | event | raw | Dot position 7 offset in sequence learning |
| `dot_no7_ON` | 792 | event | raw | Dot position 7 onset in sequence learning |
| `dot_no8_OFF` | 396 | event | raw | Dot position 8 offset in sequence learning |
| `dot_no8_ON` | 396 | event | raw | Dot position 8 onset in sequence learning |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset in the surround suppression task |
| `instructed_toCloseEyes` | 680 | event | raw | Auditory instruction to close eyes during resting state |
| `instructed_toOpenEyes` | 816 | event | raw | Auditory instruction to open eyes during resting state |
| `learningBlock_1` | 122 | event | raw | Start of sequence learning block 1 |
| `learningBlock_2` | 121 | event | raw | Start of sequence learning block 2 |
| `learningBlock_3` | 120 | event | raw | Start of sequence learning block 3 |
| `learningBlock_4` | 119 | event | raw | Start of sequence learning block 4 |
| `learningBlock_5` | 118 | event | raw | Start of sequence learning block 5 |
| `left_buttonPress` | 5095 | event | raw | Left mouse button press response in contrast change detection |
| `left_target` | 4243 | event | raw | Left-tilted contrast target presentation |
| `newPage` | 194 | event | raw | New symbol search page or query set presented |
| `resting_start` | 139 | event | raw | Start of resting-state recording |
| `right_buttonPress` | 4634 | event | raw | Right mouse button press response in contrast change detection |
| `right_target` | 4251 | event | raw | Right-tilted contrast target presentation |
| `seqLearning_start` | 122 | event | raw | Sequence learning task start |
| `seqLearning_stop` | 118 | event | raw | Sequence learning task stop |
| `stim_ON` | 13278 | event | raw | Surround suppression visual stimulus onset |
| `surroundSuppB1_start` | 108 | event | raw | Start of surround suppression block/run 1 |
| `surroundSuppB2_start` | 99 | event | raw | Start of surround suppression block/run 2 |
| `symbolSearch_start` | 76 | event | raw | Symbol search task start |
| `trialResponse` | 1247 | event | raw | Participant response in the symbol search task |
| `video_start` | 761 | event | raw | Movie stimulus presentation start |
| `video_stop` | 723 | event | raw | Movie stimulus presentation stop |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Seconds from contrast target onset to the first valid button press within the same trial; filled from target onset through the matched response and NaN elsewhere |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | Availability flag for the Despicable Me movie watching recording |
| `DiaryOfAWimpyKid` | complete | Availability flag for the Diary of a Wimpy Kid movie watching recording |
| `FunwithFractals` | complete | Availability flag for the Fun with Fractals movie watching recording |
| `RestingState` | complete | Availability flag for the resting-state recording |
| `ThePresent` | complete | Availability flag for The Present movie watching recording |
| `age` | complete | Participant age in years |
| `attention` | partial (1304/1342) | CBCL-derived attention dimension score |
| `commercial_use` | complete | Participant consent flag for commercial use |
| `contrastChangeDetection_1` | complete | Availability/QC flag for contrast change detection run 1 |
| `contrastChangeDetection_2` | complete | Availability/QC flag for contrast change detection run 2 |
| `contrastChangeDetection_3` | complete | Availability/QC flag for contrast change detection run 3 |
| `dataset` | complete | Kernel-added dataset identifier |
| `dataset_root` | complete | Kernel-added absolute raw dataset root used for the scan |
| `device` | complete | Hardware label combined from EEG sidecar manufacturer and model fields |
| `eeg_reference` | complete | EEG reference from the EEG sidecar |
| `ehq_total` | partial (1325/1342) | Edinburgh Handedness Questionnaire total score; positive is more right-handed and negative is more left-handed |
| `externalizing` | partial (1304/1342) | CBCL-derived externalizing symptom dimension score |
| `full_pheno` | complete | Flag indicating whether a full phenotypic file is available |
| `internalizing` | partial (1304/1342) | CBCL-derived internalizing symptom dimension score |
| `manufacturer` | complete | EEG sidecar manufacturer field |
| `manufacturers_model_name` | complete | EEG sidecar amplifier/cap model field |
| `p_factor` | partial (1304/1342) | Participant-level general psychopathology factor score |
| `power_line_frequency` | complete | Power-line frequency in Hz from the EEG sidecar |
| `recording_type` | complete | BIDS recording type from the EEG sidecar |
| `release_number` | complete | HBN EEG release identifier |
| `run` | partial (500/1342) | BIDS run entity; blank for tasks without an explicit run index |
| `sampling_frequency` | complete | EEG sampling frequency in Hz from the EEG sidecar |
| `seqLearning6target` | complete | Availability flag for the 6-target sequence learning variant |
| `seqLearning8target` | complete | Availability flag for the 8-target sequence learning variant |
| `sex` | complete | Participant sex code from participants.tsv |
| `subject_id` | complete | BIDS participant identifier |
| `surroundSupp_1` | complete | Availability/QC flag for surround suppression run 1 |
| `surroundSupp_2` | complete | Availability/QC flag for surround suppression run 2 |
| `symbolSearch` | complete | Availability/QC flag for the symbol search recording |
| `task` | complete | BIDS task entity parsed from the file name |


## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 10

**Dataset**: `openneuro_ds005515` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005515
**Category**: Complex Applied | **Subjects**: 533 | **Files (Completed)**: 2515 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 10 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `b07fb98eb91956901f6040d0f4d6cd21c85c456c0b68c06c05a57e5198d5737f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 2105 | event | raw |  |
| `IBEG` | 4 | event | raw |  |
| `IEND` | 12 | event | raw |  |
| `boundary` | 1385 | event | raw |  |
| `break cnt` | 1451 | event | raw |  |
| `contrastChangeB1_start` | 75 | event | raw |  |
| `contrastChangeB2_start` | 132 | event | raw |  |
| `contrastChangeB3_start` | 91 | event | raw |  |
| `contrastTrial_start` | 5858 | event | raw |  |
| `contrast_response_correct` | 3731 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 493 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 24 | event | raw |  |
| `dot_no1_ON` | 24 | event | raw |  |
| `dot_no2_OFF` | 48 | event | raw |  |
| `dot_no2_ON` | 521 | event | raw |  |
| `dot_no3_OFF` | 24 | event | raw |  |
| `dot_no3_ON` | 474 | event | raw |  |
| `dot_no4_OFF` | 24 | event | raw |  |
| `dot_no4_ON` | 24 | event | raw |  |
| `dot_no5_OFF` | 24 | event | raw |  |
| `dot_no5_ON` | 24 | event | raw |  |
| `dot_no6_OFF` | 24 | event | raw |  |
| `dot_no6_ON` | 24 | event | raw |  |
| `dot_no7_OFF` | 26 | event | raw |  |
| `dot_no7_ON` | 24 | event | raw |  |
| `dot_no8_OFF` | 12 | event | raw |  |
| `dot_no8_ON` | 12 | event | raw |  |
| `fixpoint_ON` | 10562 | event | raw |  |
| `instructed_toCloseEyes` | 2365 | event | raw |  |
| `instructed_toOpenEyes` | 2862 | event | raw |  |
| `learningBlock_1` | 17 | event | raw |  |
| `learningBlock_2` | 4 | event | raw |  |
| `learningBlock_3` | 2 | event | raw |  |
| `learningBlock_4` | 1 | event | raw |  |
| `left_buttonPress` | 3689 | event | raw |  |
| `left_target` | 2545 | event | raw |  |
| `net` | 2 | event | raw |  |
| `newPage` | 188 | event | raw |  |
| `resting_start` | 516 | event | raw |  |
| `right_buttonPress` | 3034 | event | raw |  |
| `right_target` | 2812 | event | raw |  |
| `seqLearning_start` | 18 | event | raw |  |
| `seqLearning_stop` | 9 | event | raw |  |
| `stim_ON` | 10818 | event | raw |  |
| `surroundSuppB1_start` | 98 | event | raw |  |
| `surroundSuppB2_start` | 67 | event | raw |  |
| `symbolSearch_start` | 70 | event | raw |  |
| `trialResponse` | 1211 | event | raw |  |
| `video_start` | 1627 | event | raw |  |
| `video_stop` | 1610 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, caution, unavailable |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, caution, unavailable |
| `ThePresent` | complete | e.g. unavailable, available, caution |
| `age` | complete | e.g. 7.0599, 13.6389, 7.0018 |
| `attention` | complete | e.g. -0.363, -0.866, -0.434 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. unavailable, caution, available |
| `contrastChangeDetection_2` | complete | e.g. unavailable, caution, available |
| `contrastChangeDetection_3` | complete | e.g. caution, unavailable, available |
| `dataset` | complete | e.g. openneuro_ds005515 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005515 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 55.63, 100.05, -86.71 |
| `externalizing` | complete | e.g. -0.05, -0.348, -0.235 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | complete | e.g. -0.042, -0.373, -1.491 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. -0.636, -1.681, -0.268 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R10 |
| `run` | partial (377/2515) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable |
| `seqLearning8target` | complete | e.g. unavailable |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAA396TWZ, sub-NDARAA773LUW, sub-NDARAB674LNB |
| `surroundSupp_1` | complete | e.g. caution, unavailable, available |
| `surroundSupp_2` | complete | e.g. unavailable, caution, available |
| `symbolSearch` | complete | e.g. caution, unavailable, available |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 11

**Dataset**: `openneuro_ds005516` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005516
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 3396 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 11 is a large-scale, multi-task developmental battery collected from children and adolescents aged 5-22 years. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, serial dot, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recording.

## File Scan Result

> **Kernel SHA256**: `318b9070bc5ce6136bb575dc11faf76a0b7a1d99209b7a79558a3cec69661626`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 3038 | event | raw |  |
| `IBEG` | 19 | event | raw |  |
| `IEND` | 22 | event | raw |  |
| `SPIK` | 2 | event | raw |  |
| `boundary` | 1462 | event | raw |  |
| `break cnt` | 3196 | event | raw |  |
| `contrastChangeB1_start` | 398 | event | raw |  |
| `contrastChangeB2_start` | 283 | event | raw |  |
| `contrastChangeB3_start` | 234 | event | raw |  |
| `contrastTrial_start` | 19366 | event | raw |  |
| `contrast_response_correct` | 14289 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1858 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 19 | event | raw |  |
| `dot_no1_ON` | 19 | event | raw |  |
| `dot_no2_OFF` | 48 | event | raw |  |
| `dot_no2_ON` | 107 | event | raw |  |
| `dot_no3_OFF` | 19 | event | raw |  |
| `dot_no3_ON` | 72 | event | raw |  |
| `dot_no4_OFF` | 19 | event | raw |  |
| `dot_no4_ON` | 22 | event | raw |  |
| `dot_no5_OFF` | 19 | event | raw |  |
| `dot_no5_ON` | 19 | event | raw |  |
| `dot_no6_OFF` | 19 | event | raw |  |
| `dot_no6_ON` | 19 | event | raw |  |
| `dot_no7_OFF` | 10 | event | raw |  |
| `dot_no7_ON` | 6 | event | raw |  |
| `dot_no8_OFF` | 3 | event | raw |  |
| `dot_no8_ON` | 3 | event | raw |  |
| `fixpoint_ON` | 37760 | event | raw |  |
| `instructed_toCloseEyes` | 1370 | event | raw |  |
| `instructed_toOpenEyes` | 1644 | event | raw |  |
| `learningBlock_1` | 8 | event | raw |  |
| `learningBlock_2` | 3 | event | raw |  |
| `learningBlock_3` | 3 | event | raw |  |
| `learningBlock_4` | 3 | event | raw |  |
| `learningBlock_5` | 2 | event | raw |  |
| `left_buttonPress` | 14777 | event | raw |  |
| `left_target` | 9226 | event | raw |  |
| `net` | 4 | event | raw |  |
| `newPage` | 601 | event | raw |  |
| `resting_start` | 372 | event | raw |  |
| `right_buttonPress` | 13758 | event | raw |  |
| `right_target` | 9311 | event | raw |  |
| `seqLearning_start` | 8 | event | raw |  |
| `seqLearning_stop` | 1 | event | raw |  |
| `stim_ON` | 37825 | event | raw |  |
| `surroundSuppB1_start` | 327 | event | raw |  |
| `surroundSuppB2_start` | 262 | event | raw |  |
| `symbolSearch_start` | 222 | event | raw |  |
| `trialResponse` | 4056 | event | raw |  |
| `video_start` | 1666 | event | raw |  |
| `video_stop` | 1541 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, caution, unavailable |
| `DiaryOfAWimpyKid` | complete | e.g. available, caution, unavailable |
| `FunwithFractals` | complete | e.g. available, caution, unavailable |
| `RestingState` | complete | e.g. available, unavailable, caution |
| `ThePresent` | complete | e.g. available, caution, unavailable |
| `age` | complete | e.g. 20.1817, 7.2728, 22.0002 |
| `attention` | complete | e.g. 0.032, 0.118, -1.159 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, caution, unavailable |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005516 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005516 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 100, 33.35, 80.04 |
| `externalizing` | complete | e.g. -0.825, -0.45, -0.668 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | complete | e.g. 0.101, -0.648, 0.098 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. 0.887, -1.487, 0.015 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R11 |
| `run` | partial (1355/3396) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable |
| `seqLearning8target` | complete | e.g. unavailable |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAB678VYW, sub-NDARAB683CYD, sub-NDARAC296UCB |
| `surroundSupp_1` | complete | e.g. available, caution, unavailable |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. available, caution, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 2

**Dataset**: `openneuro_ds005506` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005506
**Category**: Complex Applied | **Subjects**: 152 | **Files (Completed)**: 1405 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 2 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `643f1e413ec8ef573301a37c7ab1be072b89c31a045b40e52ab197269de18a89`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1150 | event | raw |  |
| `boundary` | 799 | event | raw |  |
| `break cnt` | 1577 | event | raw |  |
| `contrastChangeB1_start` | 107 | event | raw |  |
| `contrastChangeB2_start` | 120 | event | raw |  |
| `contrastChangeB3_start` | 154 | event | raw |  |
| `contrastTrial_start` | 9310 | event | raw |  |
| `contrast_response_correct` | 6633 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 933 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 640 | event | raw |  |
| `dot_no1_ON` | 640 | event | raw |  |
| `dot_no2_OFF` | 1284 | event | raw |  |
| `dot_no2_ON` | 1326 | event | raw |  |
| `dot_no3_OFF` | 640 | event | raw |  |
| `dot_no3_ON` | 679 | event | raw |  |
| `dot_no4_OFF` | 640 | event | raw |  |
| `dot_no4_ON` | 640 | event | raw |  |
| `dot_no5_OFF` | 640 | event | raw |  |
| `dot_no5_ON` | 640 | event | raw |  |
| `dot_no6_OFF` | 640 | event | raw |  |
| `dot_no6_ON` | 640 | event | raw |  |
| `dot_no7_OFF` | 756 | event | raw |  |
| `dot_no7_ON` | 756 | event | raw |  |
| `dot_no8_OFF` | 378 | event | raw |  |
| `dot_no8_ON` | 378 | event | raw |  |
| `fixpoint_ON` | 14081 | event | raw |  |
| `instructed_toCloseEyes` | 736 | event | raw |  |
| `instructed_toOpenEyes` | 883 | event | raw |  |
| `learningBlock_1` | 131 | event | raw |  |
| `learningBlock_2` | 129 | event | raw |  |
| `learningBlock_3` | 128 | event | raw |  |
| `learningBlock_4` | 126 | event | raw |  |
| `learningBlock_5` | 126 | event | raw |  |
| `left_buttonPress` | 5762 | event | raw |  |
| `left_target` | 4439 | event | raw |  |
| `newPage` | 215 | event | raw |  |
| `resting_start` | 156 | event | raw |  |
| `right_buttonPress` | 4970 | event | raw |  |
| `right_target` | 4463 | event | raw |  |
| `seqLearning_start` | 131 | event | raw |  |
| `seqLearning_stop` | 126 | event | raw |  |
| `stim_ON` | 14116 | event | raw |  |
| `surroundSuppB1_start` | 117 | event | raw |  |
| `surroundSuppB2_start` | 103 | event | raw |  |
| `symbolSearch_start` | 84 | event | raw |  |
| `trialResponse` | 1372 | event | raw |  |
| `video_start` | 797 | event | raw |  |
| `video_stop` | 765 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable |
| `RestingState` | complete | e.g. available, caution |
| `ThePresent` | complete | e.g. available, unavailable |
| `age` | complete | e.g. 13.4391, 11.5822, 5.5485 |
| `attention` | partial (1370/1405) | e.g. -0.6509999999999999, -1.0659999999999998, -1.025 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005506 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005506 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | partial (1364/1405) | e.g. -83.38, 55.63, 53.36 |
| `externalizing` | partial (1370/1405) | e.g. 0.62, 0.001, -0.099 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | partial (1370/1405) | e.g. -0.229, 0.903, 0.253 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (1370/1405) | e.g. 0.37, 1.035, -1.125 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R2 |
| `run` | partial (521/1405) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. available, unavailable |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAB793GL3, sub-NDARAH948UF0, sub-NDARAM675UR8 |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable |
| `symbolSearch` | complete | e.g. available, unavailable, caution |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 3

**Dataset**: `openneuro_ds005507` | **Year**: 2017/2025 | **URL**: https://openneuro.org/datasets/ds005507
**Category**: Complex Applied | **Subjects**: 183 | **Files (Completed)**: 1812 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 3 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `38bada9129dfa26bd00e3ccdd98a0327b4465006cbbf82bef2ae2847699b50f8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1446 | event | raw |  |
| `boundary` | 1074 | event | raw |  |
| `break cnt` | 1973 | event | raw |  |
| `contrastChangeB1_start` | 140 | event | raw |  |
| `contrastChangeB2_start` | 151 | event | raw |  |
| `contrastChangeB3_start` | 208 | event | raw |  |
| `contrastTrial_start` | 12072 | event | raw |  |
| `contrast_response_correct` | 8346 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1249 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 823 | event | raw |  |
| `dot_no1_ON` | 823 | event | raw |  |
| `dot_no2_OFF` | 1648 | event | raw |  |
| `dot_no2_ON` | 1694 | event | raw |  |
| `dot_no3_OFF` | 823 | event | raw |  |
| `dot_no3_ON` | 858 | event | raw |  |
| `dot_no4_OFF` | 823 | event | raw |  |
| `dot_no4_ON` | 832 | event | raw |  |
| `dot_no5_OFF` | 823 | event | raw |  |
| `dot_no5_ON` | 823 | event | raw |  |
| `dot_no6_OFF` | 823 | event | raw |  |
| `dot_no6_ON` | 823 | event | raw |  |
| `dot_no7_OFF` | 962 | event | raw |  |
| `dot_no7_ON` | 962 | event | raw |  |
| `dot_no8_OFF` | 481 | event | raw |  |
| `dot_no8_ON` | 481 | event | raw |  |
| `fixpoint_ON` | 18564 | event | raw |  |
| `instructed_toCloseEyes` | 915 | event | raw |  |
| `instructed_toOpenEyes` | 1101 | event | raw |  |
| `learningBlock_1` | 171 | event | raw |  |
| `learningBlock_2` | 165 | event | raw |  |
| `learningBlock_3` | 163 | event | raw |  |
| `learningBlock_4` | 162 | event | raw |  |
| `learningBlock_5` | 162 | event | raw |  |
| `left_buttonPress` | 6995 | event | raw |  |
| `left_target` | 5753 | event | raw |  |
| `newPage` | 274 | event | raw |  |
| `resting_start` | 194 | event | raw |  |
| `right_buttonPress` | 6266 | event | raw |  |
| `right_target` | 5800 | event | raw |  |
| `seqLearning_start` | 171 | event | raw |  |
| `seqLearning_stop` | 160 | event | raw |  |
| `stim_ON` | 18602 | event | raw |  |
| `surroundSuppB1_start` | 154 | event | raw |  |
| `surroundSuppB2_start` | 137 | event | raw |  |
| `symbolSearch_start` | 107 | event | raw |  |
| `trialResponse` | 1757 | event | raw |  |
| `video_start` | 1041 | event | raw |  |
| `video_stop` | 1013 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, caution |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 7.9827, 10.2275, 11.93 |
| `attention` | partial (1765/1812) | e.g. -0.235, -1.106, 0.381 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, caution, unavailable |
| `contrastChangeDetection_2` | complete | e.g. available, caution, unavailable |
| `contrastChangeDetection_3` | complete | e.g. available, caution, unavailable |
| `dataset` | complete | e.g. openneuro_ds005507 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005507 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | partial (1760/1812) | e.g. 90.05, 83.38, 93.38 |
| `externalizing` | partial (1765/1812) | e.g. -0.387, 0.453, -0.6509999999999999 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | partial (1765/1812) | e.g. 0.034, 0.001, 0.55 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (1765/1812) | e.g. -0.018000000000000002, 1.506, 1.735 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R3 |
| `run` | partial (679/1812) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. available, unavailable |
| `seqLearning8target` | complete | e.g. unavailable, available, caution |
| `sex` | complete | e.g. F, M |
| `subject_id` | complete | e.g. sub-NDARAA948VFH, sub-NDARAC853DTE, sub-NDARAD774HAZ |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. available, caution, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 4

**Dataset**: `openneuro_ds005508` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005508
**Category**: Complex Applied | **Subjects**: 324 | **Files (Completed)**: 3342 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 4 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `ad37bdbc2b8969b577002b5f92f1a231d92eef61a02cfd596a1bcbee917d052b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 2502 | event | raw |  |
| `boundary` | 1871 | event | raw |  |
| `break cnt` | 3452 | event | raw |  |
| `contrastChangeB1_start` | 258 | event | raw |  |
| `contrastChangeB2_start` | 279 | event | raw |  |
| `contrastChangeB3_start` | 304 | event | raw |  |
| `contrastTrial_start` | 20646 | event | raw |  |
| `contrast_response_correct` | 14455 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 2155 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 1468 | event | raw |  |
| `dot_no1_ON` | 1468 | event | raw |  |
| `dot_no2_OFF` | 2938 | event | raw |  |
| `dot_no2_ON` | 3055 | event | raw |  |
| `dot_no3_OFF` | 1468 | event | raw |  |
| `dot_no3_ON` | 1570 | event | raw |  |
| `dot_no4_OFF` | 1468 | event | raw |  |
| `dot_no4_ON` | 1468 | event | raw |  |
| `dot_no5_OFF` | 1468 | event | raw |  |
| `dot_no5_ON` | 1468 | event | raw |  |
| `dot_no6_OFF` | 1468 | event | raw |  |
| `dot_no6_ON` | 1468 | event | raw |  |
| `dot_no7_OFF` | 1734 | event | raw |  |
| `dot_no7_ON` | 1734 | event | raw |  |
| `dot_no8_OFF` | 867 | event | raw |  |
| `dot_no8_ON` | 867 | event | raw |  |
| `fixpoint_ON` | 35072 | event | raw |  |
| `instructed_toCloseEyes` | 1608 | event | raw |  |
| `instructed_toOpenEyes` | 1929 | event | raw |  |
| `learningBlock_1` | 296 | event | raw |  |
| `learningBlock_2` | 295 | event | raw |  |
| `learningBlock_3` | 293 | event | raw |  |
| `learningBlock_4` | 293 | event | raw |  |
| `learningBlock_5` | 291 | event | raw |  |
| `left_buttonPress` | 11751 | event | raw |  |
| `left_target` | 9806 | event | raw |  |
| `newPage` | 509 | event | raw |  |
| `resting_start` | 326 | event | raw |  |
| `right_buttonPress` | 10656 | event | raw |  |
| `right_target` | 9909 | event | raw |  |
| `seqLearning_start` | 296 | event | raw |  |
| `seqLearning_stop` | 291 | event | raw |  |
| `stim_ON` | 35171 | event | raw |  |
| `surroundSuppB1_start` | 278 | event | raw |  |
| `surroundSuppB2_start` | 270 | event | raw |  |
| `symbolSearch_start` | 195 | event | raw |  |
| `trialResponse` | 3286 | event | raw |  |
| `video_start` | 1368 | event | raw |  |
| `video_stop` | 1342 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable |
| `RestingState` | complete | e.g. available, unavailable |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 10.0518, 12.9211, 12.943 |
| `attention` | partial (3279/3342) | e.g. 0.907, -1.506, 0.18100000000000002 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005508 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005508 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 86.71, 66.77, 80.04 |
| `externalizing` | partial (3279/3342) | e.g. 0.297, 0.34700000000000003, 0.8 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | partial (3279/3342) | e.g. 0.32, 0.271, 0.84 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (3279/3342) | e.g. 1.181, 1.137, 1.128 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R4 |
| `run` | partial (1304/3342) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. available, unavailable |
| `sex` | complete | e.g. F, M |
| `subject_id` | complete | e.g. sub-NDARAC349YUC, sub-NDARAC350BZ0, sub-NDARAD232HVV |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. caution, available, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 5

**Dataset**: `openneuro_ds005509` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005509
**Category**: Complex Applied | **Subjects**: 330 | **Files (Completed)**: 3326 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 5 is a large-scale, multi-task developmental battery collected from children and adolescents aged 5-21 years. Participants completed six paradigms including naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `f5aea7e69f37918dfd21038c10ebabcaab581ae2881ce3c777f402c67b94692a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `./sub-NDARFR095UJK/eeg/sub-NDARFR095UJK_task-seqLearning6target_events.tsv` | 1 | event | raw |  |
| `9999` | 2339 | event | raw |  |
| `boundary` | 1839 | event | raw |  |
| `break cnt` | 3296 | event | raw |  |
| `contrastChangeB1_start` | 233 | event | raw |  |
| `contrastChangeB2_start` | 282 | event | raw |  |
| `contrastChangeB3_start` | 260 | event | raw |  |
| `contrastTrial_start` | 18682 | event | raw |  |
| `contrast_response_correct` | 13181 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1971 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 1553 | event | raw |  |
| `dot_no1_ON` | 1553 | event | raw |  |
| `dot_no2_OFF` | 3106 | event | raw |  |
| `dot_no2_ON` | 3119 | event | raw |  |
| `dot_no3_OFF` | 1553 | event | raw |  |
| `dot_no3_ON` | 1565 | event | raw |  |
| `dot_no4_OFF` | 1553 | event | raw |  |
| `dot_no4_ON` | 1558 | event | raw |  |
| `dot_no5_OFF` | 1553 | event | raw |  |
| `dot_no5_ON` | 1553 | event | raw |  |
| `dot_no6_OFF` | 1553 | event | raw |  |
| `dot_no6_ON` | 1553 | event | raw |  |
| `dot_no7_OFF` | 2100 | event | raw |  |
| `dot_no7_ON` | 2100 | event | raw |  |
| `dot_no8_OFF` | 1050 | event | raw |  |
| `dot_no8_ON` | 1050 | event | raw |  |
| `fixpoint_ON` | 35136 | event | raw |  |
| `instructed_toCloseEyes` | 1639 | event | raw |  |
| `instructed_toOpenEyes` | 1969 | event | raw |  |
| `learningBlock_1` | 319 | event | raw |  |
| `learningBlock_2` | 310 | event | raw |  |
| `learningBlock_3` | 310 | event | raw |  |
| `learningBlock_4` | 307 | event | raw |  |
| `learningBlock_5` | 307 | event | raw |  |
| `left_buttonPress` | 10192 | event | raw |  |
| `left_target` | 8947 | event | raw |  |
| `newPage` | 522 | event | raw |  |
| `resting_start` | 336 | event | raw |  |
| `right_buttonPress` | 9498 | event | raw |  |
| `right_target` | 8977 | event | raw |  |
| `seqLearning_start` | 319 | event | raw |  |
| `seqLearning_stop` | 307 | event | raw |  |
| `stim_ON` | 35156 | event | raw |  |
| `surroundSuppB1_start` | 286 | event | raw |  |
| `surroundSuppB2_start` | 263 | event | raw |  |
| `symbolSearch_start` | 202 | event | raw |  |
| `trialResponse` | 3367 | event | raw |  |
| `video_start` | 1205 | event | raw |  |
| `video_stop` | 1190 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, unavailable |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 8.212, 6.975, 11.2867 |
| `attention` | partial (3257/3326) | e.g. -0.966, 0.033, 0.163 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005509 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005509 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 46.69, 53.36, 96.72 |
| `externalizing` | partial (3257/3326) | e.g. -0.364, 0.9990000000000001, -0.87 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | partial (3257/3326) | e.g. -0.636, 0.003, -0.079 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (3257/3326) | e.g. 1.004, 0.8029999999999999, -0.853 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R5 |
| `run` | partial (1294/3326) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. available, unavailable |
| `seqLearning8target` | complete | e.g. unavailable, available, caution |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAC350XUM, sub-NDARAC857HDB, sub-NDARAH304ED7 |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. caution, available, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 6

**Dataset**: `openneuro_ds005510` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005510
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 1227 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 6 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching (Despicable Me, The Present, Diary of a Wimpy Kid, Fun with Fractals), eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population with phenotypic assessments including IQ, behavioral problems, ADHD, anxiety, and socioeconomic status.

## File Scan Result

> **Kernel SHA256**: `76bcfd2a5d00f8f8435e8a5c5ed7e31cdc02b81f26900043ce08196d30f9a41e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 866 | event | raw |  |
| `boundary` | 666 | event | raw |  |
| `break cnt` | 1242 | event | raw |  |
| `contrastChangeB1_start` | 44 | event | raw |  |
| `contrastChangeB2_start` | 111 | event | raw |  |
| `contrastChangeB3_start` | 94 | event | raw |  |
| `contrastTrial_start` | 5817 | event | raw |  |
| `contrast_response_correct` | 4110 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 566 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 634 | event | raw |  |
| `dot_no1_ON` | 634 | event | raw |  |
| `dot_no2_OFF` | 1270 | event | raw |  |
| `dot_no2_ON` | 1268 | event | raw |  |
| `dot_no3_OFF` | 634 | event | raw |  |
| `dot_no3_ON` | 634 | event | raw |  |
| `dot_no4_OFF` | 634 | event | raw |  |
| `dot_no4_ON` | 648 | event | raw |  |
| `dot_no5_OFF` | 634 | event | raw |  |
| `dot_no5_ON` | 634 | event | raw |  |
| `dot_no6_OFF` | 634 | event | raw |  |
| `dot_no6_ON` | 634 | event | raw |  |
| `dot_no7_OFF` | 853 | event | raw |  |
| `dot_no7_ON` | 852 | event | raw |  |
| `dot_no8_OFF` | 426 | event | raw |  |
| `dot_no8_ON` | 426 | event | raw |  |
| `fixpoint_ON` | 13696 | event | raw |  |
| `instructed_toCloseEyes` | 676 | event | raw |  |
| `instructed_toOpenEyes` | 810 | event | raw |  |
| `learningBlock_1` | 129 | event | raw |  |
| `learningBlock_2` | 127 | event | raw |  |
| `learningBlock_3` | 126 | event | raw |  |
| `learningBlock_4` | 126 | event | raw |  |
| `learningBlock_5` | 126 | event | raw |  |
| `left_buttonPress` | 3743 | event | raw |  |
| `left_target` | 2793 | event | raw |  |
| `newPage` | 224 | event | raw |  |
| `resting_start` | 138 | event | raw |  |
| `right_buttonPress` | 3249 | event | raw |  |
| `right_target` | 2796 | event | raw |  |
| `seqLearning_start` | 129 | event | raw |  |
| `seqLearning_stop` | 126 | event | raw |  |
| `stim_ON` | 13706 | event | raw |  |
| `surroundSuppB1_start` | 118 | event | raw |  |
| `surroundSuppB2_start` | 96 | event | raw |  |
| `symbolSearch_start` | 86 | event | raw |  |
| `trialResponse` | 1483 | event | raw |  |
| `video_start` | 441 | event | raw |  |
| `video_stop` | 435 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable |
| `FunwithFractals` | complete | e.g. available, unavailable |
| `RestingState` | complete | e.g. available, caution |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 10.7939, 5.8054, 12.8362 |
| `attention` | partial (1194/1227) | e.g. 1.0290000000000001, -0.601, 0.309 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005510 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005510 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 60.03, 80.04, 33.35 |
| `externalizing` | partial (1194/1227) | e.g. 0.14400000000000002, 1.5630000000000002, 0.242 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | partial (1194/1227) | e.g. -0.461, -0.523, 0.004 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (1194/1227) | e.g. 0.366, 0.8540000000000001, -0.5920000000000001 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R6 |
| `run` | partial (446/1227) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. available, unavailable |
| `sex` | complete | e.g. F, M |
| `subject_id` | complete | e.g. sub-NDARAB055BPR, sub-NDARAB348EWR, sub-NDARAB458VK9 |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable |
| `symbolSearch` | complete | e.g. caution, available, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 7

**Dataset**: `openneuro_ds005511` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005511
**Category**: Complex Applied | **Subjects**: 381 | **Files (Completed)**: 3100 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 7 is a large-scale, multi-task developmental battery collected from children and adolescents ages 5–21. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks across multiple recording sessions. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using standardized clinical assessments and high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `7cdc6ec382ae96046df3a8e1894ba74e92c34c89cb6ccf314c9b506c32533f36`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 2143 | event | raw |  |
| `boundary` | 1728 | event | raw |  |
| `break cnt` | 3092 | event | raw |  |
| `contrastChangeB1_start` | 118 | event | raw |  |
| `contrastChangeB2_start` | 232 | event | raw |  |
| `contrastChangeB3_start` | 206 | event | raw |  |
| `contrastTrial_start` | 13272 | event | raw |  |
| `contrast_response_correct` | 9675 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1250 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 1668 | event | raw |  |
| `dot_no1_ON` | 1668 | event | raw |  |
| `dot_no2_OFF` | 3343 | event | raw |  |
| `dot_no2_ON` | 3345 | event | raw |  |
| `dot_no3_OFF` | 1668 | event | raw |  |
| `dot_no3_ON` | 1675 | event | raw |  |
| `dot_no4_OFF` | 1668 | event | raw |  |
| `dot_no4_ON` | 1668 | event | raw |  |
| `dot_no5_OFF` | 1668 | event | raw |  |
| `dot_no5_ON` | 1668 | event | raw |  |
| `dot_no6_OFF` | 1668 | event | raw |  |
| `dot_no6_ON` | 1668 | event | raw |  |
| `dot_no7_OFF` | 2234 | event | raw |  |
| `dot_no7_ON` | 2232 | event | raw |  |
| `dot_no8_OFF` | 1116 | event | raw |  |
| `dot_no8_ON` | 1116 | event | raw |  |
| `fixpoint_ON` | 34688 | event | raw |  |
| `instructed_toCloseEyes` | 1825 | event | raw |  |
| `instructed_toOpenEyes` | 2193 | event | raw |  |
| `learningBlock_1` | 338 | event | raw |  |
| `learningBlock_2` | 333 | event | raw |  |
| `learningBlock_3` | 333 | event | raw |  |
| `learningBlock_4` | 332 | event | raw |  |
| `learningBlock_5` | 332 | event | raw |  |
| `left_buttonPress` | 7530 | event | raw |  |
| `left_target` | 6361 | event | raw |  |
| `newPage` | 603 | event | raw |  |
| `resting_start` | 377 | event | raw |  |
| `right_buttonPress` | 6992 | event | raw |  |
| `right_target` | 6384 | event | raw |  |
| `seqLearning_start` | 338 | event | raw |  |
| `seqLearning_stop` | 332 | event | raw |  |
| `stim_ON` | 34708 | event | raw |  |
| `surroundSuppB1_start` | 314 | event | raw |  |
| `surroundSuppB2_start` | 228 | event | raw |  |
| `symbolSearch_start` | 228 | event | raw |  |
| `trialResponse` | 4059 | event | raw |  |
| `video_start` | 1115 | event | raw |  |
| `video_stop` | 1097 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, unavailable |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 7.9574, 11.6294, 7.2536 |
| `attention` | complete | e.g. -0.914, -0.001, -0.321 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005511 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005511 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz, common |
| `ehq_total` | complete | e.g. 100.05, -20.01, -71.17 |
| `externalizing` | complete | e.g. 0.312, 0.02, 0.517 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | complete | e.g. -1.867, -0.995, 0.561 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. 2.43, -0.943, 0.376 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R7 |
| `run` | partial (1070/3100) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. unavailable, available |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAC462DZH, sub-NDARAE866UVF, sub-NDARAF440XWG |
| `surroundSupp_1` | complete | e.g. available, unavailable, caution |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. unavailable, available, caution |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 8

**Dataset**: `openneuro_ds005512` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005512
**Category**: Complex Applied | **Subjects**: 257 | **Files (Completed)**: 2320 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 8 is a large-scale, multi-task developmental battery collected from children and adolescents across the New York City area. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population, enabling multi-label classification of DSM-V diagnoses.

## File Scan Result

> **Kernel SHA256**: `6cb274b2d83ba7364d80e8e1df2572c85b8e4cfafdf32db9170cca3cd91d3842`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1751 | event | raw |  |
| `boundary` | 1237 | event | raw |  |
| `break cnt` | 2258 | event | raw |  |
| `contrastChangeB1_start` | 182 | event | raw |  |
| `contrastChangeB2_start` | 194 | event | raw |  |
| `contrastChangeB3_start` | 170 | event | raw |  |
| `contrastTrial_start` | 12963 | event | raw |  |
| `contrast_response_correct` | 9040 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1237 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 968 | event | raw |  |
| `dot_no1_ON` | 968 | event | raw |  |
| `dot_no2_OFF` | 1940 | event | raw |  |
| `dot_no2_ON` | 1992 | event | raw |  |
| `dot_no3_OFF` | 968 | event | raw |  |
| `dot_no3_ON` | 1017 | event | raw |  |
| `dot_no4_OFF` | 968 | event | raw |  |
| `dot_no4_ON` | 984 | event | raw |  |
| `dot_no5_OFF` | 968 | event | raw |  |
| `dot_no5_ON` | 968 | event | raw |  |
| `dot_no6_OFF` | 968 | event | raw |  |
| `dot_no6_ON` | 968 | event | raw |  |
| `dot_no7_OFF` | 1075 | event | raw |  |
| `dot_no7_ON` | 1072 | event | raw |  |
| `dot_no8_OFF` | 536 | event | raw |  |
| `dot_no8_ON` | 536 | event | raw |  |
| `fixpoint_ON` | 22913 | event | raw |  |
| `instructed_toCloseEyes` | 1104 | event | raw |  |
| `instructed_toOpenEyes` | 1326 | event | raw |  |
| `learningBlock_1` | 200 | event | raw |  |
| `learningBlock_2` | 195 | event | raw |  |
| `learningBlock_3` | 191 | event | raw |  |
| `learningBlock_4` | 191 | event | raw |  |
| `learningBlock_5` | 191 | event | raw |  |
| `left_buttonPress` | 6946 | event | raw |  |
| `left_target` | 6151 | event | raw |  |
| `newPage` | 366 | event | raw |  |
| `resting_start` | 229 | event | raw |  |
| `right_buttonPress` | 6875 | event | raw |  |
| `right_target` | 6231 | event | raw |  |
| `seqLearning_start` | 202 | event | raw |  |
| `seqLearning_stop` | 191 | event | raw |  |
| `stim_ON` | 22981 | event | raw |  |
| `surroundSuppB1_start` | 182 | event | raw |  |
| `surroundSuppB2_start` | 176 | event | raw |  |
| `symbolSearch_start` | 144 | event | raw |  |
| `trialResponse` | 2318 | event | raw |  |
| `video_start` | 950 | event | raw |  |
| `video_stop` | 877 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. unavailable, available |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 21.2167, 9.1653, 13.6279 |
| `attention` | complete | e.g. -0.647, -0.342, 0.978 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005512 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005512 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 6.67, 73.34, 80.04 |
| `externalizing` | complete | e.g. -1.051, 0.442, -0.516 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | complete | e.g. 1.24, 0.643, 0.315 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. 0.987, -0.392, 1.561 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R8 |
| `run` | partial (870/2320) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. unavailable, available |
| `sex` | complete | e.g. F, M |
| `subject_id` | complete | e.g. sub-NDARAA306NT2, sub-NDARAA504CRN, sub-NDARAA947ZG5 |
| `surroundSupp_1` | complete | e.g. unavailable, caution, available |
| `surroundSupp_2` | complete | e.g. available, unavailable, caution |
| `symbolSearch` | complete | e.g. unavailable, available, caution |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Healthy Brain Network (HBN) EEG - Release 9

**Dataset**: `openneuro_ds005514` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005514
**Category**: Complex Applied | **Subjects**: 295 | **Files (Completed)**: 2885 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

The Healthy Brain Network (HBN) EEG Release 9 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5-21). Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection with contrast change blocks, surrounding suppression, sequence learning with five progressive blocks, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population with multi-modal phenotypic assessment.

## File Scan Result

> **Kernel SHA256**: `7d4d4d4240243f45df77b516b7c87913a857054faad71886bdf6ad94cb062e8f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 2155 | event | raw |  |
| `boundary` | 1554 | event | raw |  |
| `break cnt` | 2807 | event | raw |  |
| `contrastChangeB1_start` | 226 | event | raw |  |
| `contrastChangeB2_start` | 253 | event | raw |  |
| `contrastChangeB3_start` | 217 | event | raw |  |
| `contrastTrial_start` | 16449 | event | raw |  |
| `contrast_response_correct` | 12040 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 1616 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 1204 | event | raw |  |
| `dot_no1_ON` | 1204 | event | raw |  |
| `dot_no2_OFF` | 2413 | event | raw |  |
| `dot_no2_ON` | 2487 | event | raw |  |
| `dot_no3_OFF` | 1204 | event | raw |  |
| `dot_no3_ON` | 1226 | event | raw |  |
| `dot_no4_OFF` | 1204 | event | raw |  |
| `dot_no4_ON` | 1225 | event | raw |  |
| `dot_no5_OFF` | 1204 | event | raw |  |
| `dot_no5_ON` | 1204 | event | raw |  |
| `dot_no6_OFF` | 1204 | event | raw |  |
| `dot_no6_ON` | 1204 | event | raw |  |
| `dot_no7_OFF` | 1536 | event | raw |  |
| `dot_no7_ON` | 1532 | event | raw |  |
| `dot_no8_OFF` | 766 | event | raw |  |
| `dot_no8_ON` | 766 | event | raw |  |
| `fixpoint_ON` | 30018 | event | raw |  |
| `instructed_toCloseEyes` | 1325 | event | raw |  |
| `instructed_toOpenEyes` | 1591 | event | raw |  |
| `learningBlock_1` | 244 | event | raw |  |
| `learningBlock_2` | 241 | event | raw |  |
| `learningBlock_3` | 240 | event | raw |  |
| `learningBlock_4` | 240 | event | raw |  |
| `learningBlock_5` | 239 | event | raw |  |
| `left_buttonPress` | 10593 | event | raw |  |
| `left_target` | 7857 | event | raw |  |
| `newPage` | 409 | event | raw |  |
| `resting_start` | 273 | event | raw |  |
| `right_buttonPress` | 10002 | event | raw |  |
| `right_target` | 7910 | event | raw |  |
| `seqLearning_start` | 244 | event | raw |  |
| `seqLearning_stop` | 239 | event | raw |  |
| `stim_ON` | 30059 | event | raw |  |
| `surroundSuppB1_start` | 234 | event | raw |  |
| `surroundSuppB2_start` | 235 | event | raw |  |
| `symbolSearch_start` | 161 | event | raw |  |
| `trialResponse` | 2569 | event | raw |  |
| `video_start` | 1157 | event | raw |  |
| `video_stop` | 1085 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable, caution |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, unavailable |
| `ThePresent` | complete | e.g. available, unavailable, caution |
| `age` | complete | e.g. 14.5916, 9.1899, 9.986 |
| `attention` | complete | e.g. -0.38299999999999995, 0.183, -0.882 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, caution, unavailable |
| `contrastChangeDetection_2` | complete | e.g. available, caution, unavailable |
| `contrastChangeDetection_3` | complete | e.g. available, caution, unavailable |
| `dataset` | complete | e.g. openneuro_ds005514 |
| `dataset_root` | complete | e.g. /home/public/eeg_dataset/openneuro_raw/ds005514 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 93.38, -66.67, 96.67 |
| `externalizing` | complete | e.g. -0.078, -0.235, -0.031 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | complete | e.g. -1.2990000000000002, -1.518, -0.583 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. -0.684, 0.43700000000000006, 1.239 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R9 |
| `run` | partial (1124/2885) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. available, unavailable, caution |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAC589YMB, sub-NDARAC853CR6, sub-NDARAE710YWG |
| `surroundSupp_1` | complete | e.g. available, caution, unavailable |
| `surroundSupp_2` | complete | e.g. available, caution, unavailable |
| `symbolSearch` | complete | e.g. available, caution, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# CAP Sleep Database

**Dataset**: `physionet_capslpdb` | **Year**: 2012 | **URL**: https://physionet.org/content/capslpdb/1.0.0/
**Category**: Biological State | **Subjects**: 108 | **Files (Completed)**: 108 | **Channels**: 5-36 | **Sampling Rate**: 100-512 Hz | **Manual Review**: anonymous for review

## Paradigm

The CAP Sleep Database comprises 108 overnight polysomnographic (PSG) recordings collected at the Sleep Disorders Center of the Ospedale Maggiore of Parma, Italy. The cohort includes 16 healthy controls and 92 patients with sleep disorders, including nocturnal frontal lobe epilepsy (NFLE, n=40), REM sleep behavior disorder (RBD, n=22), periodic leg movements (PLM, n=10), insomnia (n=9), narcolepsy (n=5), sleep-disordered breathing (SDB, n=4), and bruxism (n=2). Expert neurologists annotated both sleep macrostructure according to Rechtschaffen & Kales rules and CAP events according to Terzano’s atlas. CAP phase A events are further divided into subtypes A1, A2, and A3, corresponding respectively to predominantly synchronized EEG patterns with low autonomic/somatomotor impact, mixed synchronized–desynchronized patterns with intermediate impact, and predominantly desynchronized patterns with stronger autonomic/somatomotor effects. The recordings include at least three EEG channels, along with EOG, submental EMG, bilateral anterior tibial EMG, respiratory signals, and EKG; some recordings also contain additional bipolar EEG traces.

## File Scan Result

> **Kernel SHA256**: `75b8e91f0ee85940a6f1b23fc7c5369f4c8f497d330ce43caa933221925b80ab`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `A1` | 26788 | event | raw | CAP phase A1: high-amplitude synchronized EEG |
| `A2` | 10519 | event | raw | CAP phase A2: mixed synchronization EEG |
| `A3` | 14324 | event | raw | CAP phase A3: desynchronized EEG |
| `B` | 51737 | event | raw | Non-CAP EEG period (baseline interval) |
| `SLEEP-MT` | 11 | admin | raw | Movement time boundary marker |
| `SLEEP-REM` | 18935 | event | raw | REM sleep stage epoch marker |
| `SLEEP-S0` | 19495 | event | raw | Wakefulness stage epoch marker |
| `SLEEP-S1` | 4642 | event | raw | NREM Sleep stage 1 epoch marker |
| `SLEEP-S2` | 39192 | event | raw | NREM Sleep stage 2 epoch marker |
| `SLEEP-S3` | 11953 | event | raw | NREM Sleep stage 3 epoch marker |
| `SLEEP-S4` | 13780 | event | raw | NREM Sleep stage 4 epoch marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 1, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `SLEEP-S0` | 0 | Wake (S0) |
  | `SLEEP-S1` | 1 | NREM Stage 1 |
  | `SLEEP-S2` | 2 | NREM Stage 2 |
  | `SLEEP-S3` | 3 | NREM Stage 3 |
  | `SLEEP-S4` | 4 | NREM Stage 4 |
  | `SLEEP-REM` | 5 | REM sleep |
- **Evidence**:
  - 10.13026/C2VC79 — Dataset documentation confirming PSG/EEG sleep scoring with R&K stages
  - 10.1109/tnsre.2019.2934828 — The classification is typically performed on thirty-seconds windows of the electroencephalography (EEG) recording.
- **Notes**: 

### Classical Task 2: CAP A-phase detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 14 s, overlap = 1, target_events = [`A1`, `A2`, `A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `A1` | 0 | CAP A-phase (subtype A1) |
  | `A2` | 1 | CAP A-phase (subtype A2) |
  | `A3` | 2 | CAP A-phase (subtype A3) |
- **Evidence**:
  - 10.1109/tnsre.2019.2934828 — CAP A-phase detection is performed at 1 Hz resolution using feature vectors extracted from short overlapping windows, with an LSTM operating on 14-second temporal contexts centered at each time step.
- **Notes**: 

### Potential Task 1: CAP A-phase subtype classification (4 seconds)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 1, target_events = [`A1`, `A2`, `A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `A1` | 0 | CAP Phase A1 (synchronized EEG) |
  | `A2` | 1 | CAP Phase A2 (mixed pattern) |
  | `A3` | 2 | CAP Phase A3 (desynchronized EEG) |
- **Evidence**:

- **Notes**: 

### Potential Task 2: NREM classification (4-second)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 1.0, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `SLEEP-S0` | 0 | Wake (S0) |
  | `SLEEP-S1` | 1 | NREM Stage 1 |
  | `SLEEP-S2` | 2 | NREM Stage 2 |
  | `SLEEP-S3` | 3 | NREM Stage 3 |
  | `SLEEP-S4` | 4 | NREM Stage 4 |
  | `SLEEP-REM` | 5 | REM sleep |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

- Channel count and sampling rate vary substantially across subjects; normalize before cross-subject analysis.
- Mixed clinical population: NFLE, RBD, PLM, insomnia, narcolepsy, SDB, bruxism, and healthy controls; group labels are encoded in the subject metadata. May be update kernel if more tasks are needed

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# CHB-MIT Scalp EEG Database

**Dataset**: `physionet_chbmit` | **Year**: 2010 | **URL**: https://physionet.org/content/chbmit/1.0.0/
**Category**: Biological State | **Subjects**: 23 | **Files (Completed)**: 686 | **Channels**: 23 | **Sampling Rate**: 256 Hz | **Manual Review**: anonymous for review

## Paradigm

Twenty-three pediatric subjects (22 original cases plus chb24 added later; 5 males aged 3-22, 17 females aged 1.5-19, with chb24 age/sex unknown) with intractable seizures were monitored at Children's Hospital Boston following withdrawal of anti-seizure medication to evaluate surgical candidacy (Shoeb & Guttag, 2010). Note: case chb21 was recorded 1.5 years after chb01 from the same female subject. Long-term continuous EEG was recorded from 23 scalp channels (bipolar montage following the 10-20 system) at 256 Hz with 16-bit resolution. The dataset contains 686 EEG files, of which 129 contain one or more seizures, for a total of 198 annotated seizures. Seizure onset and offset times are documented in per-subject summary text files (`chbNN-summary.txt`); the kernel parses these to create `seizure` annotations spanning each ictal period.

## File Scan Result

> **Kernel SHA256**: `5b18a5f37633b5153a20c7a1573700377f710a8901f40e266ea5f1f3079e57e9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `interictal_complement` | 883 | event | super | Seizure-free complement of the raw seizure intervals within the current recording. |
| `interictal_ge_4h` | 392 | event | super | Seizure-free time at least 4 hours away from any seizure onset or offset. |
| `preictal_20min` | 229 | event | super | Twenty-minute window preceding seizure onset, clipped to non-seizure time. |
| `preictal_30min` | 239 | event | super | Thirty-minute window preceding seizure onset, clipped to non-seizure time. |
| `seizure` | 198 | event | raw | Seizure interval (onset to offset) parsed from the CHB-MIT summary/seizure annotations. |


> Counts in the Event Structure table represent annotation segments written to individual EDF files, not the number of logical seizure episodes. Super-meta events such as preictal_20min and preictal_30min are derived from seizure onset times and then clipped to file boundaries. Therefore, a single seizure may yield more than one preictal annotation segment when its preictal window spans multiple consecutive EDF files. As a result, the total counts for preictal_20min and preictal_30min can be greater than the total count for seizure.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (664/686) | e.g. 11, 14, 22 |
| `amplifier` | missing | N/A |
| `cap` | missing | N/A |
| `handedness` | missing | N/A |
| `sex` | partial (664/686) | e.g. Female, Male |


## Tasks

### Classical Task 1: Binary seizure detection (ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0, target_events = [`interictal_complement`, `seizure`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seizure` | 1 | Ictal (seizure period) |
  | `interictal_complement` | 0 | Interictal (seizure-free) |
- **Evidence**:
  - 10.1016/j.bspc.2024.107379 — CHB-MIT seizure intervals are taken from the dataset summary files, non-seizure data are taken from the remaining recording time, and each subject is represented with 2 s samples for seizure vs non-seizure classification.
  - 10.1038/s41598-025-18479-9 — CHB-MIT is used for binary epileptic seizure detection based on ictal and interictal EEG phases.
  - 10.1038/s41598-025-98389-y — Public EEG datasets including CHB-MIT are divided into 5 s fragments labeled as seizure or no seizure for binary classification, providing an alternative windowing protocol.
- **Notes**: 

### Classical Task 2: Seizure prediction (preictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s, overlap = 0.9, target_events = [`interictal_ge_4h`, `preictal_30min`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `preictal_30min` | 1 | Thirty-minute window preceding seizure onset, clipped to non-seizure time |
  | `interictal_ge_4h` | 0 | Seizure-free time at least 4 hours away from any seizure onset or offset |
- **Evidence**:
  - 10.1088/1741-2552/ada0e5 — CHB-MIT preictal data are defined as the 30 min before seizure onset, interictal data are at least 4 hours before seizure onset and 4 hours after seizure end, and EEG is segmented into 10 s intervals with 90% overlap.
  - 10.1109/access.2020.2976866 — CHB-MIT seizure prediction is formulated as preictal vs interictal classification, with the preictal state described as the 30 min before seizure onset.
  - 10.3390/app12094158 — CHB-MIT preictal/interictal seizure prediction uses a seizure-distance rule for interictal data and evaluates fixed-window EEG representations.
- **Notes**: Use generated super events directly. Extract 10-second windows with 90% overlap only inside `preictal_30min` and `interictal_ge_4h`; this makes `overlap = 9.0 s`. Exclude raw `seizure` intervals, postictal transition time, and any unlabeled seizure-free periods that do not satisfy the >=4-hour interictal rule.

### Potential Task 1: Three-class seizure state classification (preictal vs ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.75, target_events = [`interictal_ge_4h`, `preictal_20min`, `seizure`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `preictal_20min` | 0 | Twenty-minute window preceding seizure onset, clipped to non-seizure time |
  | `seizure` | 1 | Ictal period from annotated seizure onset to offset |
  | `interictal_ge_4h` | 2 | Seizure-free time at least 4 hours away from any seizure onset or offset |
- **Evidence**:
  - 10.54525/bbmd.1526069 — CHB-MIT EEG is organized as a three-class problem with pre-seizure, seizure, and non-seizure labels; the pre-seizure interval is the 20 min before seizure, and spectrogram windows are 4 s long with a 1 s shift.
- **Notes**: 

## Data Quality Notes

- Severe class imbalance: the majority of recordings are seizure-free; balance by undersampling interictal or using cost-sensitive learning.
- Channel count varies: most files have 23 channels; some cases include 24 or 26 channels (extra ECG or vagal nerve stimulus channels); exclude non-EEG channels.
- Patient-specific model training is recommended; cross-patient generalization is difficult.
- Patient-specific seizure detection/prediction should be treated as evaluation protocol variants of Classical Tasks 1-2 rather than separate label tasks; avoid subject leakage, especially between chb01 and chb21.
- Subject chb24 has unknown age and sex.
- Age range: 1.5-22 years (pediatric); EEG morphology differs significantly from adult norms.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2018-2020/2019/2024/2025 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 516 | **Channels**: 25 | **Sampling Rate**: 256/500 Hz | **Manual Review**: anonymous for review

## Paradigm

This dataset records home-based ear-EEG sleep monitoring from 20 healthy participants and is split into two parts. The official README states that data collection took place between 2018 and 2020 and that the first publication was in 2019. Part a contains 20 subjects with four nights each of simultaneous partial PSG, ear-EEG, and wrist-worn actigraphy in the home. Part b contains 10 of those subjects with an additional 12 nights using ear-EEG, actigraphy, and a single EOG electrode. PSG nights are sessions 1-4 and each PSG night has official scoring acquisition event files. The event structure also contains Danish diary/protocol annotations, synchronization and trigger markers, electrode-test/biocalibration annotations, and ASSR-related raw event codes.

## File Scan Result

> **Kernel SHA256**: `babb43ee6f8ce05ae72cbf3c197d37f6e1a36aed5e13e2c9c9ad39b2c1d766f4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Biocalibrations` | 79 | event | raw |  |
| `Biocalibrations start` | 11 | event | raw |  |
| `ElektrodeTest` | 1 | event | raw |  |
| `Gik i seng` | 80 | event | raw |  |
| `Højre prop ud/ind` | 1 | event | raw |  |
| `Højre prop ude i 5 min.` | 1 | event | raw |  |
| `Kort højre prop ude` | 1 | event | raw |  |
| `Lights Out` | 94 | event | raw |  |
| `Sov uroligt` | 1 | event | raw |  |
| `Stadig vågen` | 1 | event | raw |  |
| `Start af måling` | 75 | event | raw |  |
| `Stod op` | 70 | event | raw |  |
| `Stoppede måling` | 2 | event | raw |  |
| `Sync` | 77 | event | raw |  |
| `Tog propper ud` | 1 | event | raw |  |
| `Tog propperne ud` | 1 | event | raw |  |
| `Toietl` | 1 | event | raw |  |
| `Vågen` | 7 | event | raw |  |
| `Vågen i nat` | 1 | event | raw |  |
| `Vågen længe` | 1 | event | raw |  |
| `Vågen-gik i seng` | 1 | event | raw |  |
| `Vågen-stod op` | 1 | event | raw |  |
| `elektrodetest 2` | 1 | event | raw |  |
| `højre prop ude igen` | 2 | event | raw |  |
| `højre øreprop i igen` | 2 | event | raw |  |
| `højre øreprop ude` | 2 | event | raw |  |
| `i seng igen` | 2 | event | raw |  |
| `meget vågen i ca. 2 timer` | 1 | event | raw |  |
| `opvågning` | 1 | event | raw |  |
| `på toilet` | 2 | event | raw |  |
| `satte propperne i` | 2 | event | raw |  |
| `sluk mobita` | 1 | event | raw |  |
| `slukkede mobita` | 1 | event | raw |  |
| `tog propper ud` | 1 | event | raw |  |
| `tog propperne ud` | 1 | event | raw |  |
| `tog venstre prop ud` | 1 | event | raw |  |
| `vågen` | 6 | event | raw |  |
| `vågen i lidt tid` | 2 | event | raw |  |
| `vågnede` | 1 | event | raw |  |
| `Electrodetest` | 198 | event | raw |  |
| `Forsøg på at sove` | 1 | event | raw |  |
| `Got up` | 126 | event | raw |  |
| `Højre prop ud/ind` | 1 | event | raw |  |
| `Højre prop ude i 5 min.` | 1 | event | raw |  |
| `Kort højre prop ude` | 1 | event | raw |  |
| `Lights Out` | 199 | event | raw |  |
| `Løs elektrode` | 1 | event | raw |  |
| `Mega vågen` | 1 | event | raw |  |
| `Opvågnen` | 1 | event | raw |  |
| `Opvågning` | 1 | event | raw |  |
| `Sov uroligt` | 1 | event | raw |  |
| `Stadig vågen` | 1 | event | raw |  |
| `Start of recording` | 200 | event | raw |  |
| `Stod op for at slukke lys` | 1 | event | raw |  |
| `Stoppede måling` | 2 | event | raw |  |
| `Stoppede målingen` | 1 | event | raw |  |
| `Sync` | 197 | event | raw |  |
| `Tog propper ud` | 1 | event | raw |  |
| `Tog propperne ud` | 2 | event | raw |  |
| `Tog venstre prop ud` | 1 | event | raw |  |
| `Toietl` | 1 | event | raw |  |
| `Vågen` | 15 | event | raw |  |
| `Vågen i nat` | 1 | event | raw |  |
| `Vågen længe` | 1 | event | raw |  |
| `Vågen-gik i seng` | 1 | event | raw |  |
| `Vågen-stod op` | 1 | event | raw |  |
| `Went to bed` | 199 | event | raw |  |
| `elektrodetest 2` | 1 | event | raw |  |
| `event_1` | 25 | event | raw |  |
| `event_131071` | 8 | event | raw |  |
| `event_2` | 88 | event | raw |  |
| `event_3` | 16 | event | raw |  |
| `event_4` | 19 | event | raw |  |
| `event_5` | 51 | event | raw |  |
| `event_6` | 34 | event | raw |  |
| `event_7` | 20 | event | raw |  |
| `event_8` | 6 | event | raw |  |
| `event_9` | 2 | event | raw |  |
| `genereret af lyde` | 1 | event | raw |  |
| `højre prop ude igen` | 1 | event | raw |  |
| `højre øreprop i igen` | 1 | event | raw |  |
| `højre øreprop ude` | 1 | event | raw |  |
| `i seng igen` | 1 | event | raw |  |
| `meget vågen i ca. 2 timer` | 1 | event | raw |  |
| `opvågning` | 1 | event | raw |  |
| `på toilet` | 1 | event | raw |  |
| `rettede på prop` | 1 | event | raw |  |
| `rettede øreprop til` | 1 | event | raw |  |
| `scoring1_1-W` | 11408 | event | raw | Manual sleep scoring by scorer 1: Wake |
| `scoring1_2-REM` | 13675 | event | raw | Manual sleep scoring by scorer 1: REM sleep |
| `scoring1_3-N1` | 5510 | event | raw | Manual sleep scoring by scorer 1: N1 sleep |
| `scoring1_4-N2` | 32478 | event | raw | Manual sleep scoring by scorer 1: N2 sleep |
| `scoring1_5-N3` | 12836 | event | raw | Manual sleep scoring by scorer 1: N3 sleep |
| `scoring1_7-Artefact` | 2871 | event | raw | Manual sleep scoring by scorer 1: Artefact; exclude from sleep-stage targets |
| `scoring2_1-W` | 12464 | event | raw | Manual sleep scoring by scorer 2: Wake |
| `scoring2_2-REM` | 14263 | event | raw | Manual sleep scoring by scorer 2: REM sleep |
| `scoring2_3-N1` | 3713 | event | raw | Manual sleep scoring by scorer 2: N1 sleep |
| `scoring2_4-N2` | 31305 | event | raw | Manual sleep scoring by scorer 2: N2 sleep |
| `scoring2_5-N3` | 16167 | event | raw | Manual sleep scoring by scorer 2: N3 sleep |
| `scoring2_7-Artefact` | 886 | event | raw | Manual sleep scoring by scorer 2: Artefact; exclude from sleep-stage targets |
| `tog højre øreprop ud` | 1 | event | raw |  |
| `tog propper ud` | 1 | event | raw |  |
| `tog venstre prop ud` | 1 | event | raw |  |
| `trigger` | 30726 | event | raw |  |
| `vågen` | 8 | event | raw |  |
| `vågen i lidt tid` | 1 | event | raw |  |
| `vågnede uden prop` | 1 | event | raw |  |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Mapped from `participants.tsv` column `age`; age in 2019, range 22-36 years. |
| `sex` | complete | Mapped from `participants.tsv` column `sex`; values `f` = 13, `m` = 7. |
| `device` | complete | README identifies the EEG recorder as TMSi Mobita; amplifier/cap details are also captured in scan-derived fields. |
| `acq` | partial (356/516) | e.g. PSG, earEEG |
| `amplifier` | complete | e.g. TMSi Mobita |
| `cap` | complete | e.g. custom ear-EEG earpieces, custom ear-EEG earpieces with partial PSG electrodes, custom self-applied ear-EEG earpieces with single EOG electrode |
| `dataset` | complete | e.g. openneuro_ds005185 |
| `eeg_channel_count` | complete | e.g. 20, 22, 18 |
| `eeg_reference` | complete | e.g. average, common |
| `emg_channel_count` | complete | e.g. 0, 3 |
| `eog_channel_count` | complete | e.g. 0, 2, 1 |
| `misc_channel_count` | complete | e.g. 0 |
| `power_line_frequency_hz` | complete | e.g. 50 |
| `recording_type` | complete | e.g. EEG |
| `sampling_rate_hz` | complete | e.g. 256.0, 500.0 |
| `session` | complete | e.g. ses-001, ses-002, ses-003 |
| `sleep_diary_available` | complete | e.g. False, True |
| `sleep_scoring1_available` | complete | e.g. False, True |
| `sleep_scoring2_available` | complete | e.g. False, True |
| `sleep_stage_event_format` | complete | e.g. scoring<scorer>_<code>-<stage> |
| `source_file` | complete | e.g. edf_used_to_score1.edf, edf_used_to_score2.edf, sub-001_ses-001_task-ASSR_acq-PSG_eeg.set |
| `subject_id` | complete | e.g. sub-001, sub-002, sub-003 |
| `task` | partial (356/516) | e.g. ASSR, sleep, electrodeTestLab |
| `task_description` | partial (156/516) | e.g. Auditory Steady State Response: 40 Hz amplitude modulated noise, with accompanying trigger signal, was played to the subject. By focusing on the 40 Hz SNR in the recorded data, an objective signal quality could be determined., Subject watched a short video clip with various instructions (jaw clenching, eyes open/closed, eyes moving left & right), to be able to compare those results to the ASSR results. |


## Tasks

### Classical Task 1: Scorer 1 5-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`scoring1_1-W`, `scoring1_2-REM`, `scoring1_3-N1`, `scoring1_4-N2`, `scoring1_5-N3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `scoring1_1-W` | 0 | Wake, scorer 1 |
  | `scoring1_3-N1` | 1 | N1 sleep, scorer 1 |
  | `scoring1_4-N2` | 2 | N2 sleep, scorer 1 |
  | `scoring1_5-N3` | 3 | N3 sleep, scorer 1 |
  | `scoring1_2-REM` | 4 | REM sleep, scorer 1 |
- **Evidence**:
  - OpenNeuro ds005185 README — PSG nights are sessions 1-4 and each PSG night has an additional scoring acquisition event file.
  - OpenNeuro `task-sleep_events.json` — `Scoring1` defines manual sleep scoring by scorer 1 with Wake, REM, N1, N2, N3, Artefact, and Unscored levels.
  - Full official S3 audit — 80 scorer-1 scoring files; all scoring rows have `duration = 30`.
  - 10.1038/s41597-025-04579-8 — Data descriptor states EESM19 manual scorings are included as `.tsv` event files and PSG recordings were scored twice by different technicians.
  - 10.1038/s41598-019-53115-3 — First EESM19 publication supports whole-night ear-EEG sleep-stage analysis.
- **Notes**: `scoring1_7-Artefact` is excluded from target events. Scorer 1 is kept separate from scorer 2; no scorer merging or adjudication is assumed.

### Classical Task 2: Scorer 2 5-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`scoring2_1-W`, `scoring2_2-REM`, `scoring2_3-N1`, `scoring2_4-N2`, `scoring2_5-N3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `scoring2_1-W` | 0 | Wake, scorer 2 |
  | `scoring2_3-N1` | 1 | N1 sleep, scorer 2 |
  | `scoring2_4-N2` | 2 | N2 sleep, scorer 2 |
  | `scoring2_5-N3` | 3 | N3 sleep, scorer 2 |
  | `scoring2_2-REM` | 4 | REM sleep, scorer 2 |
- **Evidence**:
  - OpenNeuro ds005185 README — PSG nights are sessions 1-4 and each PSG night has an additional scoring acquisition event file.
  - OpenNeuro `task-sleep_events.json` — `Scoring2` defines manual sleep scoring by scorer 2 with Wake, REM, N1, N2, N3, Artefact, and Unscored levels.
  - Full official S3 audit — 80 scorer-2 scoring files; all scoring rows have `duration = 30`.
  - 10.1038/s41597-025-04579-8 — Data descriptor states EESM19 PSG recordings were manually scored twice and scorings are included as `.tsv` event files.
  - 10.1038/s41598-019-53115-3 — First EESM19 publication supports whole-night ear-EEG sleep-stage analysis.
- **Notes**: `scoring2_7-Artefact` is excluded from target events. Scorer 2 is kept separate from scorer 1; no scorer merging or adjudication is assumed.

### Potential Task 1: Age regression from sleep EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping; numeric age in years, range 22-36 |
- **Evidence**:
  - OpenNeuro ds005185 `participants.tsv` and `participants.json` — age is available for all 20 participants and is defined as age in 2019.
- **Notes**: Subject-level metadata task, not a core published sleep-staging benchmark. Segmenting EEG does not increase the number of independent subject-level age labels.

### Potential Task 2: Sex classification from sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | f -> 0; m -> 1 |
- **Evidence**:
  - OpenNeuro ds005185 `participants.tsv` and `participants.json` — sex is complete for all 20 participants; distribution is 13 f / 7 m.
- **Notes**: Subject-level metadata task, not a core published sleep-staging benchmark.

## Data Quality Notes

- Sleep stage labels (W/N1/N2/N3/REM) are not present in raw EEG event markers and must be extracted from PSG annotation sidecar files.
- Danish-language event annotations dominate the event structure, which may require translation for broader usability; multiple spelling variants exist (e.g., `Vågen` vs `vågen`, `Tog propper ud` vs `tog propper ud`).
- ASSR task events (event_4 through event_9) appear in the scan with low counts but their provenance cannot be verified from events.tsv files, creating uncertainty for task construction.
- The extremely high count of `trigger` events (30,726) relative to all other events suggests dense synchronization pulses that may need downsampling or exclusion during epoching.
- Multiple event ID systems are in use: string descriptions with Danish text, numeric event codes (event_1 through event_131071), and a generic `trigger` marker, which may complicate event parsing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2020-2022/2023/2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 4/13 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. Subjects manually sent trigger events to mark boundaries between video sequences and sleep sequences during the recording sessions.

## File Scan Result

> **Kernel SHA256**: `bc63a68f9ba26c0981ba24bc421dde0b1f1f07f31c18c348a3eacd3f53b7c533`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Artefact` | 1032 | admin | raw | Manual scoring artefact / unusable signal epoch |
| `Sleep stage N1` | 2662 | event | raw | N1 sleep epoch |
| `Sleep stage N2` | 15122 | event | raw | N2 sleep epoch |
| `Sleep stage N3` | 5161 | event | raw | N3 sleep epoch |
| `Sleep stage R` | 6259 | event | raw | REM sleep epoch |
| `Sleep stage W` | 2879 | event | raw | Wake epoch |
| `error -10` | 12535 | admin | raw |  |
| `error -100` | 118 | admin | raw |  |
| `event_2` | 72 | admin | raw |  |
| `oLED` | 6 | admin | raw |  |
| `trigger` | 243 | admin | raw |  |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `amplifier` | missing | N/A |
| `cap` | missing | N/A |
| `handedness` | missing | N/A |
| `sex` | missing | N/A |


## Tasks

### Classical Task 1: Five-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | wake epoch |
  | `Sleep stage N1` | 1 | N1 sleep epoch |
  | `Sleep stage N2` | 2 | N2 sleep epoch |
  | `Sleep stage N3` | 3 | N3 sleep epoch |
  | `Sleep stage R` | 4 | REM sleep epoch |
- **Evidence**:
  - OpenNeuro ds005178 `task-sleep_acq-scoring_events.json` defines manual sleep scoring levels Wake, REM, N1, N2, N3, and Artefact.
  - OpenNeuro ds005178 README describes at-home sleep recordings from 10 healthy participants with PSG plus ear-EEG for the first two recordings.
  - 10.1038/s41597-025-04579-8 describes EESM23 as an OpenNeuro ear-EEG sleep monitoring dataset with manual scoring stored as event files.
- **Notes**: Use only manually scored sleep-stage annotations. Exclude `Artefact`, trigger markers, and ear-EEG recording-failure markers from the target classes. Manual scoring files are available for the PSG sleep recordings, not for every ear-EEG-only session.

## Data Quality Notes

- Manual sleep scoring is available through `acq-scoring_events.tsv` files for the PSG sleep recordings; later ear-EEG-only sessions do not all have manual sleep-stage labels.
- `Artefact` is a manual scoring label for unusable signal epochs and should be excluded from the five-class sleep-stage target.
- `trigger` and `event_2` are boundary/marker events, not sleep-stage labels; `event_2` lacks sufficient public semantic documentation for task use.
- `error -10`, `error -100`, and `oLED` are ear-EEG recording-failure markers documented in `task-sleep_acq-earEEGRecordingFailures_events.json`.
- The public BIDS files do not include `participants.tsv`; subject age, sex, and handedness are unavailable.
- Channel configuration varies by acquisition: ear-EEG files have 4 EEG channels plus trigger, while PSG files have 13 physiological channels plus trigger.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# EEG Meditation Study

**Dataset**: `openneuro_ds001787` | **Year**: 2018/2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz | **Manual Review**: anonymous for review

## Paradigm

Twenty-four meditators (12 expert with ≥10 years daily practice, 12 novices) engaged in sustained meditation sessions. The released BDF files contain 80 channels (64 EEG, 15 auxiliary/misc physiological channels, and one BioSemi Status channel) sampled at 256 Hz after downsampling from the original 2048 Hz recordings. Approximately every two minutes, a brief probe interrupted the session to assess concentration level or mind-wandering, with subjects providing button-press responses. The study examines neural correlates of sustained attention, including infraslow activity coupled with autonomic markers like galvanic skin response.

## File Scan Result

> **Kernel SHA256**: `377803ea82e8e3e2c7cbb78f82abd7bb1a5a1723dac9b49a67ff799a39eb1fc4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `128` | 983 | event | raw | First question onset during the meditation probe |
| `16` | 2 | event | raw | Involuntary response marker |
| `2` | 1131 | event | raw | Response 1 to one of the probe questions |
| `254` | 5 | event | raw | BioSemi STATUS marker; administrative trigger not tied to a probe response |
| `4` | 754 | event | raw | Response 2 to one of the probe questions |
| `8` | 258 | event | raw | Response 3 to one of the probe questions |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `EXG1` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG2` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG3` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG4` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG5` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG6` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG7` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG8` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Erg1` | native (raw misc in EEG file) | raw | Native BioSemi auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Erg2` | native (raw misc in EEG file) | raw | Native BioSemi auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `GSR1` | native (raw misc in EEG file) | raw | Native galvanic skin response channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `GSR2` | native (raw misc in EEG file) | raw | Native galvanic skin response channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Plet` | native (raw misc in EEG file) | raw | Native plethysmography/PPG channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Resp` | native (raw misc in EEG file) | raw | Native respiration channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Temp` | native (raw misc in EEG file) | raw | Native temperature channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (38/40) | N/A |
| `sex` | complete | N/A |
| `device` | complete | N/A |
| `amplifier` | complete | e.g. BIOSEMI ActiveTwo |
| `cap` | complete | e.g. BioSemi 64-channel cap |
| `group` | complete | e.g. expert, novice |


## Tasks

### Potential Task 1: GSR amplitude regression from meditation EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `GSR1` | no mapping |
- **Evidence**:
  - 10.3389/fnins.2022.765585 — Reference paper explicitly analyzes ISA-GSR coupling during meditation; GSR1 and GSR2 are continuous native misc channels on the raw object (BioSemi ActiveTwo with 15 misc channels)
- **Notes**: B1 archetype (native misc channel regression). GSR1 selected as primary GSR channel; GSR2 also available as redundant backup. Segment length of 10s inferred from paper's analysis of sustained meditation states (first 30s period after meditation onset), with non-overlapping windows for independent samples.

### Potential Task 2: Respiration-EEG Coupling Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `Resp` | no mapping |
- **Evidence**:

- **Notes**: Native misc channel "Resp" is present in the BioSemi ActiveTwo channel set (confirmed in eeg.json: MiscChannelCount=15, and Resp appears in native misc channel catalog). The task uses 10-second non-overlapping windows to capture multiple respiratory cycles at typical resting rates (~12-20 breaths/min ≈ 3-5 s/cycle). The regression target is the continuous respiration signal amplitude, enabling investigation of EEG-respiration coupling during meditation practice.

### Potential Task 3: Temperature-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `Temp` | no mapping |
- **Evidence**:
  - `eeg.json` — BioSemi ActiveTwo recording with MiscChannelCount=15, confirming auxiliary channels including Temp
  - `README` — Meditation study with continuous recording; temperature as autonomic correlate of meditative state
- **Notes**: Native misc channel `Temp` is a continuous non-EEG signal already present in the raw BDF files. No kernel derivation needed; the regression target is read directly from the `Temp` channel. The 10-second segmentation window is chosen because temperature changes slowly relative to EEG dynamics, providing sufficient samples per epoch for stable regression targets.

### Potential Task 4: Plethysmography-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `Plet` | no mapping |
- **Evidence**:
  - [eeg.json, README] — Dataset includes native MISC channel `Plet` (plethysmography) among 15 misc channels; continuous recording during meditation task with ~2-minute interruption intervals for self-report.
- **Notes**: Archetype B1: native misc channel `Plet` is directly available on the raw data as a continuous peripheral physiological recording. No kernel derivation needed. The 10-second segmentation windows are chosen to capture multiple cardiac cycles for stable cardiovascular-EEG coupling estimation.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# HMC Sleep Staging Database

**Dataset**: `physionet_hmcsleepstaging` | **Year**: 2021-2022 | **URL**: https://physionet.org/content/hmc-sleep-staging/1.1/
**Category**: Biological State | **Subjects**: 151 | **Files (Completed)**: 151 | **Channels**: 8 | **Sampling Rate**: 256 Hz | **Manual Review**: anonymous for review

## Paradigm

One hundred and fifty-one (151) overnight polysomnographic recordings from the Haaglanden Medisch Centrum (HMC) Sleep Center, Netherlands, were collected and annotated using the AASM (American Academy of Sleep Medicine) scoring rules. EEG was recorded from 4 bipolar derivations (F4-M1, C4-M1, O2-M1, C3-M2), supplemented by chin EMG, two EOG channels (E1-M2, E2-M2), and ECG, all at 256 Hz. Expert sleep technicians scored each 30-second epoch as Wake, N1, N2, N3, or REM. Light-on and light-off events mark the intended sleep period boundaries.

## File Scan Result

> **Kernel SHA256**: `c64f05a92bbd474b29e1b669b21059d23994732634081f3cf43a6f989b7ff3a3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Sleep stage N1` | 8103 | event | raw | AASM NREM Stage N1 sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage N2` | 24969 | event | raw | AASM NREM Stage N2 sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage N3` | 13243 | event | raw | AASM NREM Stage N3 / slow-wave sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage R` | 10974 | event | raw | AASM REM sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage W` | 12217 | event | raw | Wake, scored as a 30-second sleep-stage annotation |


> The source scoring files also include `Lights off` and `Lights on` markers, but they are not listed in the current scanned Event Structure. Sleep-stage annotations use 30-second epochs according to AASM scoring.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | [To Agent: Dataset-level aggregate age is 53.9 ± 15.4 years.] |
| `sex` | missing | [To Agent: Dataset-level aggregate sex distribution is 85 M / 66 F.] |
| `device` | missing | [To Agent: Dataset documentation states recordings used SOMNOscreen PSG, PSG+, and EEG 10-20 recorders from SOMNOmedics, Germany, with AgAgCl electrodes.] |


## Tasks

### Classical Task 1: 5-Class Sleep Stage Classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | NREM Stage 1 |
  | `Sleep stage N2` | 2 | NREM Stage 2 |
  | `Sleep stage N3` | 3 | NREM Stage 3 / Slow-wave sleep |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.1109/embc58623.2025.11252818 — 5-class sleep stage classification (W/N1/N2/N3/R) using C4/M1 EEG channel with non-overlapping 30-second epochs, tmin=0s, tmax=30s; explicitly uses HMC dataset
  - 10.3390/s23052458 — 5-class sleep staging (Wake/N1/N2/N3/REM) using ECG from HMC database with 30-s epochs; confirms dataset and 5-class structure (uses 22.5-s overlap for ECG-specific augmentation)
  - 10.1371/journal.pone.0256111 — CNN and CNN-LSTM models for 5-class sleep stage classification (Wake/N1/N2/N3/REM) using 30-second PSG epochs from HMC dataset
- **Notes**: Primary AASM sleep staging task. Exclude 'Lights off' and 'Lights on' admin events from target_events. Implement annotation string cleaning to strip trailing commas before event matching. Consider optional interval restriction to lights-off-lights-on bounds to exclude wake periods far from sleep onset. Class imbalance expected (N1 rare). ECG channel present but should be excluded from EEG feature extraction.

### Classical Task 2: Wake vs. Sleep Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | Sleep (any stage) |
  | `Sleep stage N2` | 1 | Sleep (any stage) |
  | `Sleep stage N3` | 1 | Sleep (any stage) |
  | `Sleep stage R` | 1 | Sleep (any stage) |
- **Evidence**:
  - 10.1109/embc58623.2025.11252818 — Binary collapse of 5-class task is standard derived analysis; same epoch parameters apply
  - 10.1371/journal.pone.0256111 — Binary sleep/wake discrimination is common simplification of the same 5-class HMC staging paradigm
- **Notes**: Binary remapping of Classical Task 1. Same epoching parameters; labels collapsed W→0, all sleep stages→1. Same preprocessing considerations apply (exclude admin events, comma cleaning, lights-off/on interval restriction).

### Potential Task 1: Sliding-Window Sleep Staging with Overlap (ECG-based Augmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 22.5, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | NREM Stage 1 |
  | `Sleep stage N2` | 2 | NREM Stage 2 |
  | `Sleep stage N3` | 3 | NREM Stage 3 / Slow-wave sleep |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.3390/s23052458 — ECG-based sleep staging with 75% overlap (22.5s) for data augmentation; deviates from standard AASM non-overlapping protocol. ECG-specific, not EEG-primary.
- **Notes**: Secondary augmentation configuration derived from one paper. 22.5-s overlap creates 4× epoch count increase. Originally developed for ECG signal analysis; applicability to pure EEG staging is experimental. Not standard clinical practice. Same target_events and label mapping as Classical Task 1.

## Data Quality Notes

- AASM scoring (N1/N2/N3/REM/W) as opposed to R&K (S1/S2/S3/S4/REM/W) used in older datasets; not directly comparable.
- ECG channel present; exclude from EEG features.
- Aggregated demographics: 85 Male / 66 Female, Mean Age 53.9 ± 15.4. Individual subject-to-demographic mapping is not in public metadata due to strict EDF de-identification (Header: 'X X X').
- N1 is relatively rare; class imbalance between stages is expected.
- Five annotations carry a trailing comma (`Sleep stage W,`); strip commas from annotation strings before processing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-2003 | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: ~5804 | **Files (Completed)**: 8444 | **Channels**: 14 | **Sampling Rate**: 1-256 Hz | **Manual Review**: anonymous for review

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort investigating cardiovascular and other outcomes of sleep-disordered breathing. Participants aged 40+ underwent unattended overnight home polysomnography (PSG), collected by certified technicians. SHHS-1 enrolled 6,441 participants from major epidemiological cohorts, and 3,295 participants completed a second PSG approximately 5 years later (SHHS-2). The dataset includes full-night EEG, EOG, EMG, ECG, respiratory, and oximetry signals with expert sleep-stage annotation in 30-second epochs.

## File Scan Result

> **Kernel SHA256**: `9b2c11591e4e2ca376b0ad5925385f0cbbe420994b5669e33c9116041ac1d96e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `ASDA arousal&#124;Arousal (ASDA)` | 3429 | event | raw | ASDA-scored arousal annotation |
| `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)` | 980 | event | raw | Chin-EMG-related arousal annotation |
| `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)` | 1 | event | raw | Chin-EMG-related arousal annotation; spelling variant |
| `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)` | 111 | event | raw | Respiratory-effort-related arousal annotation |
| `Arousal&#124;Arousal ()` | 1072561 | event | raw | Generic arousal annotation |
| `Arousal&#124;Arousal (STANDARD)` | 12345 | event | raw | Standard arousal annotation |
| `Arousal&#124;Arousal (Standard)` | 1103 | event | raw | Standard arousal annotation; spelling variant |
| `Central apnea&#124;Central Apnea` | 38217 | event | raw | Central apnea respiratory event |
| `External arousal&#124;Arousal (External Arousal)` | 120 | event | raw | Arousal attributed to external disturbance |
| `Hypopnea&#124;Hypopnea` | 1588062 | event | raw | Hypopnea respiratory event |
| `Mixed apnea&#124;Mixed Apnea` | 530 | event | raw | Mixed apnea respiratory event |
| `Movement&#124;6` | 2 | admin | raw | Movement-time / non-scorable sleep-stage marker |
| `Obstructive apnea&#124;Obstructive Apnea` | 238656 | event | raw | Obstructive apnea respiratory event |
| `Periodic breathing&#124;Periodic Breathing` | 1 | event | raw | Periodic breathing interval |
| `REM sleep&#124;5` | 77963 | event | raw | REM sleep stage |
| `Recording Start Time` | 8444 | admin | raw | Recording start boundary marker |
| `Respiratory artifact&#124;Respiratory artifact` | 7 | admin | raw | Respiratory signal artifact marker |
| `SpO2 artifact&#124;SpO2 artifact` | 286898 | admin | raw | Pulse-oximetry artifact marker |
| `SpO2 desaturation&#124;SpO2 desaturation` | 1151606 | event | raw | Oxygen desaturation event |
| `Stage 1 sleep&#124;1` | 159595 | event | raw | NREM/R&K stage 1 sleep |
| `Stage 2 sleep&#124;2` | 391562 | event | raw | NREM/R&K stage 2 sleep |
| `Stage 3 sleep&#124;3` | 229582 | event | raw | NREM/R&K stage 3 sleep |
| `Stage 4 sleep&#124;4` | 22813 | event | raw | NREM/R&K stage 4 sleep |
| `Unscored&#124;9` | 198 | admin | raw | Unscored interval; exclude from sleep-stage labels |
| `Unsure&#124;Unsure` | 1219 | admin | raw | Uncertain annotation; exclude from supervised labels |
| `Wake&#124;0` | 260624 | event | raw | Wakefulness stage |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ABDO RES` | native (raw misc in EEG file) | raw | Abdominal respiratory effort belt signal |
| `AIRFLOW` | native (raw misc in EEG file) | raw | Thermistor airflow signal; SHHS1/SHHS2 alias |
| `H.R.` | native (raw misc in EEG file) | raw | Heart rate derived from ECG/oximetry; SHHS1 label |
| `LIGHT` | native (raw misc in EEG file) | raw | Ambient light on/off sensor |
| `NEW AIR` | native (raw misc in EEG file) | raw | Alternate thermistor airflow channel used in SHHS1 |
| `OX stat` | native (raw misc in EEG file) | raw | Oximetry status channel |
| `POSITION` | native (raw misc in EEG file) | raw | Body position sensor |
| `SaO2` | native (raw misc in EEG file) | raw | Pulse oximetry oxygen saturation |
| `THOR RES` | native (raw misc in EEG file) | raw | Thoracic respiratory effort belt signal |
| `spindle_density` | derived by kernel from EEG | super | Sleep spindle count per minute computed within N2 epochs |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (8444/8571) | Available for 8444/8571 scanned records |
| `sex` | partial (8444/8571) | Available for 8444/8571 scanned records |
| `device` | complete | Compumedics P-Series Sleep Monitoring System; SHHS2 used P-series v3/v4 variants |


## Tasks

### Classical Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`REM sleep&#124;5`, `Stage 1 sleep&#124;1`, `Stage 2 sleep&#124;2`, `Stage 3 sleep&#124;3`, `Stage 4 sleep&#124;4`, `Wake&#124;0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Wake&#124;0` | 0 | Wake |
  | `Stage 1 sleep&#124;1` | 1 | N1 |
  | `Stage 2 sleep&#124;2` | 2 | N2 |
  | `Stage 3 sleep&#124;3` | 3 | N3/SWS |
  | `Stage 4 sleep&#124;4` | 3 | N3/SWS |
  | `REM sleep&#124;5` | 4 | REM |
- **Evidence**:
  - 10.5665/sleep.5774 — National Sleep Research Resource provides SHHS PSG data with expert sleep-stage annotations in 30-second epochs
- **Notes**: Stage 4 is rare; merge Stage 3 and Stage 4 into N3/SWS class for robust modeling. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Sleep Spindle Density Regression in N2 Sleep
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2 sleep&#124;2`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `spindle_density` | derived from N2 EEG epochs; y is spindle count per minute |
- **Evidence**:
  - 10.1038/ncomms15930 — Characterizes sleep spindles in 11,630 individuals from NSRR including SHHS (N=5,793), analyzing spindle density, amplitude, duration and frequency during N2 sleep as heritable quantitative traits
- **Notes**: Derived from raw EEG signal in N2 (`Stage 2 sleep&#124;2`) epochs by wavelet band-pass filtering (FC=8-18 Hz) and spindle detection (0.3-3.0 s duration windows). Kernel step: Apply Morlet wavelet transform centered at 13.5 Hz, detect spindle events via amplitude thresholding, compute density = spindle count / epoch duration in minutes. Requires EEG signal processing; spindle density is primary target, with amplitude, duration, and frequency as optional additional regression targets.

### Potential Task 1: Sleep vs Wake Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`REM sleep&#124;5`, `Stage 1 sleep&#124;1`, `Stage 2 sleep&#124;2`, `Stage 3 sleep&#124;3`, `Stage 4 sleep&#124;4`, `Wake&#124;0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Wake&#124;0` | 0 | Awake |
  | `Stage 1 sleep&#124;1` | 1 | Asleep |
  | `Stage 2 sleep&#124;2` | 1 | Asleep |
  | `Stage 3 sleep&#124;3` | 1 | Asleep |
  | `Stage 4 sleep&#124;4` | 1 | Asleep |
  | `REM sleep&#124;5` | 1 | Asleep |
- **Evidence**:

- **Notes**: Useful baseline task when class granularity is reduced.

### Potential Task 2: Arousal Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 5.0 s, target_events = [`ASDA arousal&#124;Arousal (ASDA)`, `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)`, `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)`, `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)`, `Arousal&#124;Arousal ()`, `Arousal&#124;Arousal (STANDARD)`, `Arousal&#124;Arousal (Standard)`, `External arousal&#124;Arousal (External Arousal)`, `Stage 2 sleep&#124;2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stage 2 sleep&#124;2` | 0 | Non-arousal sleep-stage anchor |
  | `Arousal&#124;Arousal ()` | 1 | Generic cortical arousal |
  | `ASDA arousal&#124;Arousal (ASDA)` | 1 | ASDA-scored arousal |
  | `Arousal&#124;Arousal (STANDARD)` | 1 | Standard arousal |
  | `Arousal&#124;Arousal (Standard)` | 1 | Standard arousal spelling variant |
  | `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)` | 1 | Chin-EMG-related arousal |
  | `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)` | 1 | Chin-EMG-related arousal spelling variant |
  | `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)` | 1 | Respiratory-effort-related arousal |
  | `External arousal&#124;Arousal (External Arousal)` | 1 | External arousal |
- **Evidence**:

- **Notes**: Negative sampling strategy should exclude windows overlapping any arousal annotation to avoid label leakage.

### Potential Task 3: Respiratory Event Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Central apnea&#124;Central Apnea`, `Hypopnea&#124;Hypopnea`, `Mixed apnea&#124;Mixed Apnea`, `Obstructive apnea&#124;Obstructive Apnea`, `Periodic breathing&#124;Periodic Breathing`, `Stage 2 sleep&#124;2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stage 2 sleep&#124;2` | 0 | Non-respiratory-event sleep-stage anchor |
  | `Hypopnea&#124;Hypopnea` | 1 | Hypopnea respiratory event |
  | `Central apnea&#124;Central Apnea` | 1 | Central apnea respiratory event |
  | `Obstructive apnea&#124;Obstructive Apnea` | 1 | Obstructive apnea respiratory event |
  | `Mixed apnea&#124;Mixed Apnea` | 1 | Mixed apnea respiratory event |
  | `Periodic breathing&#124;Periodic Breathing` | 1 | Periodic breathing interval |
- **Evidence**:

- **Notes**: Respiratory subtype definitions should be verified per XML file and NSRR conversion version.

## Data Quality Notes

- EDF channels retain mixed native sampling rates; loaders must inspect per-channel EDF headers rather than assuming a single sampling rate.
- Channel naming may vary across files (`NEW AIR` vs `AIRFLOW`), so channel selection should be robust to aliases.
- Annotation counts can differ between XML-derived event totals and summary CSV fields due to historical software conversion effects.
- Desaturation labels may be missing or partially inconsistent in some files; consider deriving desaturation from raw `SaO2` traces when needed.
- Class imbalance is expected (N2 dominant; Wake/N1 relatively sparse; Stage 4 rare).
- Recordings are unattended home PSG and therefore may have higher motion/environmental artifact than in-lab PSG.
- Hardware/Sampling Shift between cohorts: SHHS-1 (1995-1998) uses EEG/EMG/ECG 125 Hz, EOG 50 Hz, respiratory 10 Hz, and SpO2/HR/position/light 1 Hz; SHHS-2 includes v3/v4 variants with ECG 250/256 Hz, EEG/EMG 125/128 Hz, EOG 50/64 Hz, respiratory 10/8 Hz, and SpO2/HR 1 Hz. DataLoader must check signal headers dynamically rather than hardcoding frequencies.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Sleep-EDF Database Expanded

**Dataset**: `physionet_sleepedfx` | **Year**: 1987-1991/1994 | **URL**: https://physionet.org/content/sleep-edfx/1.0.0/
**Category**: Biological State | **Subjects**: 106 | **Files (Completed)**: 197 | **Channels**: 7 | **Sampling Rate**: 100 Hz | **Manual Review**: anonymous for review

## Paradigm

The sleep-edf database contains 197 whole-night PolySomnoGraphic sleep recordings, containing EEG, EOG, chin EMG, and event markers. Some records also contain respiration and body temperature. Corresponding hypnograms (sleep patterns) were manually scored by well-trained technicians according to the Rechtschaffen and Kales manual, and are also available.

## File Scan Result

> **Kernel SHA256**: `db96b3badc0af51588705980412f7ed0016ef5345e218e37bd3d1fd192911aad`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Movement time` | 196 | event | raw | Subject movement marker; out-of-bed period during recording |
| `Sleep stage 1` | 7292 | event | raw | Sleep stage 1 (light sleep) epoch annotation |
| `Sleep stage 2` | 8171 | event | raw | Sleep stage 2 (light sleep) epoch annotation |
| `Sleep stage 3` | 4820 | event | raw | Sleep stage 3 (slow wave sleep) epoch annotation |
| `Sleep stage 4` | 1462 | event | raw | Sleep stage 4 (deep slow wave sleep) epoch annotation |
| `Sleep stage ?` | 173 | event | raw | Unscored or ambiguous epoch; annotation uncertain |
| `Sleep stage R` | 1953 | event | raw | Sleep stage R (REM sleep) epoch annotation |
| `Sleep stage W` | 4461 | event | raw | Sleep stage W (wakefulness) epoch annotation |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Sleep stage classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage R`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 |
  | `Sleep stage 2` | 2 | NREM Stage 2 |
  | `Sleep stage 3` | 3 | NREM Stage 3 (includes S3+S4 merged per AASM) |
  | `Sleep stage 4` | 3 | NREM Stage 3 (mapped to y=3; S3 and S4 merged) |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.7717/peerjcs.1561_table — 2 — Five-class sleep staging (W, N1, N2, N3, REM) on Sleep-EDF Expanded, 30-second epochs, AASM standard merging S3+S4 into N3
- **Notes**: 

### Potential Task 1: Wake vs. Sleep Binary Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage R`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | Any sleep (stages 1-4 and R) |
  | `Sleep stage 2` | 1 | Any sleep |
  | `Sleep stage 3` | 1 | Any sleep |
  | `Sleep stage 4` | 1 | Any sleep |
  | `Sleep stage R` | 1 | Any sleep |
- **Evidence**:
  - **Notes**:
- **Notes**: **Kernel Notes**:

## Data Quality Notes

- Only PSG files should be processed; Hypnogram files (matched companion files) are used for annotation only and are returned unchanged by the kernel.
- Class imbalance: Stage 2 is the most frequent stage; Wake also contributes large counts from lights-on periods at start/end of recording.
- Two EEG channels only (Fpz-Cz, Pz-Oz); limited spatial resolution.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# TUH EEG Abnormal Corpus

**Dataset**: `tuh_eeg_abnormal` | **Year**: 2016-2017/2024 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 2383 | **Files (Completed)**: 2983 | **Channels**: 27-36 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

The TUH EEG Abnormal Corpus (v3.0.1) is a clinically annotated subset of the TUH EEG Corpus where each recording has been classified as **normal** or **abnormal** by board-certified neurologists. Recordings are routine clinical EEG sessions acquired in an outpatient setting at Temple University Hospital. The normal/abnormal label reflects the overall clinical impression of the EEG recording, not individual event annotations. The label is encoded in the directory path (`normal/` or `abnormal/`) and extracted by the kernel to create a single whole-recording annotation.

## File Scan Result

> **Kernel SHA256**: `644d71b532db95d6bc8a1e80722382dbac84ca6c834951df359825f61b56f3d3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `abnormal` | 1466 | event | raw | Whole-recording label: clinically abnormal EEG finding |
| `normal` | 1517 | event | raw | Whole-recording label: clinically normal EEG finding |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Normal vs Abnormal EEG Recording Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 10 s, overlap = 0.0, target_events = [`abnormal`, `normal`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `normal` | 0 | Normal EEG recording |
  | `abnormal` | 1 | Abnormal EEG recording |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119521 — Uses 10-second non-overlapping epochs on TUAB dataset (resting-state EEG recordings with normal/abnormal labels) with 10-fold cross-validation, establishing standard epoching parameters for this dataset.
- **Notes**: 

## Data Quality Notes

- Variable channel count (27-36) across recordings; normalize before cross-recording analysis if needed.
- Train/dev split is encoded in directory path; respect the split for proper evaluation.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# TUH EEG Corpus (Base)

**Dataset**: `tuh_eeg` | **Year**: 2002-2017 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 10874 | **Files (Completed)**: 69652 | **Channels**: 17-128 | **Sampling Rate**: 250-1000 Hz | **Manual Review**: anonymous for review

## Paradigm

The Temple University Hospital EEG Corpus (v2.0.1) is the largest publicly available clinical EEG archive, containing approximately 69,652 EDF recordings from 10874 de-identified patients. Recordings span routine clinical EEG sessions performed for neurological evaluation (epilepsy monitoring, encephalopathy, post-operative assessment, etc.). Three standard TCP (Temporal Central Parasagittal) referential montages are used: `01_tcp_ar` (average reference), `02_tcp_le` (linked ears), and `03_tcp_ar_a` (alternating average reference). Channel counts vary (17-128) and multiple sampling rates are present (250, 256, 400, 512, 1000 Hz). No structured experiment events exist; EDF annotations are clinical technician notes in free text.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

> No structured classification annotations. The base corpus is not labeled for any specific ML task, so it generaly use for pre-training; use specialized TUH subsets (tuh_eeg_abnormal, tuh_eeg_seizure, etc.) for supervised learning.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | using NicoletOne(Natus) |


## Tasks


## Data Quality Notes

- No Record

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# TUH EEG Events Corpus

**Dataset**: `tuh_eeg_events` | **Year**: 2015-2016 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 290 | **Files (Completed)**: 518 | **Channels**: 24-33 | **Sampling Rate**: 250 Hz | **Manual Review**: anonymous for review

## Paradigm

The TUH EEG Event Corpus, a subset of the larger TUH EEG Corpus, contains annotated EEG data crucial for the analysis of various brain events. The dataset includes labeled recordings of events such as spike and slow wave discharges (spsw), generalized periodic epileptiform discharges (gped), periodic lateralized epileptiform discharges (pled), eye movements (eyem), artifacts (artf), and background (bckg) activities. This version of the corpus offers data files in the European Data Format (edf) and various annotation types, including lab and rec files, detailing event onset and duration.

The dataset is divided into two main sets: training and evaluation. The training set contains 359 files, with annotations spanning all event categories. The evaluation set is made up of 159 files, offering a separate set for testing algorithms developed on the training data. Files are stored with a systematic naming convention that references unique patient identifiers and session numbers. Two EEG channel configurations are used: averaged reference (AR) and linked ears reference (LE), aligning with standard 10/20 electrode montages for comprehensive data analysis.

This corpus is primarily used for EEG event classification, which is valuable for advancing research in epilepsy and neurological disorders. The data has been meticulously curated to support research in EEG signal processing and classification techniques.

## File Scan Result

> **Kernel SHA256**: `9c93f64e385e08686b90b12f5de77c778e1be7fb1cc6420c41ee7a4cc817dacd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `artifact` | 13257 | event | raw | Non-specific artifact |
| `background` | 73372 | event | raw | Normal background EEG activity |
| `eye movement` | 1399 | event | raw | Eye movement artifact |
| `generalized periodic epileptiform discharges` | 15931 | event | raw | GPEDs - generalized periodic epileptiform pattern |
| `periodic lateralized epileptiform discharges` | 8182 | event | raw | PLEDs - lateralized epileptiform pattern |
| `spike and sharp wave` | 1212 | event | raw | Spike or sharp wave discharge |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 6-class EEG Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1.0 s, overlap = 0, target_events = [`artifact`, `background`, `eye movement`, `generalized periodic epileptiform discharges`, `periodic lateralized epileptiform discharges`, `spike and sharp wave`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `background` | 0 | Normal background EEG |
  | `spike and sharp wave` | 1 | Epileptiform spike/sharp wave |
  | `generalized periodic epileptiform discharges` | 2 | GPEDs |
  | `periodic lateralized epileptiform discharges` | 3 | PLEDs |
  | `artifact` | 4 | Non-specific artifact |
  | `eye movement` | 5 | Eye movement artifact |
- **Evidence**:
  - 10.1109/spmb.2015.7405421 — Performs 6-way EEG event classification (SPSW, GPED, PLED, ARTF, EYEM, BCKG) using 1-sec epochs with features computed every 0.1 s. Direct mapping to dataset event IDs confirmed.
- **Notes**: epoch_by_long_event_hdf5

### Classical Task 2: Binary Epileptiform vs. Background Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1.0 s, overlap = 0, target_events = [`background`, `generalized periodic epileptiform discharges`, `periodic lateralized epileptiform discharges`, `spike and sharp wave`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `background` | 0 | Normal background EEG |
  | `spike and sharp wave` | 1 | Epileptiform spike/sharp wave |
  | `generalized periodic epileptiform discharges` | 1 | Epileptiform (GPEDs) |
  | `periodic lateralized epileptiform discharges` | 1 | Epileptiform (PLEDs) |
- **Evidence**:
  - 10.1109/spmb.2015.7405421 — Explicitly evaluates a 2-way (epileptiform vs background) classification paradigm collapsing SPSW, GPED, and PLED into one class.
- **Notes**: The background is long event, so here we use “epoch_by_long_event_hdf5" method

## Data Quality Notes

- Background annotations are long events; epileptiform events are short - class length mismatch may cause imbalance.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# TUH EEG Seizure Corpus

**Dataset**: `tuh_eeg_seizure` | **Year**: 2018 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg
**Category**: Biological State | **Subjects**: 675 | **Files (Completed)**: 7361 | **Channels**: 17-128 | **Sampling Rate**: 250/256/400/1000 Hz | **Manual Review**: anonymous for review

## Paradigm

The TUH EEG Seizure Corpus (TUSZ) is a specialized dataset developed to advance seizure detection algorithms through machine learning. A subset of the broader TUH EEG Corpus, this dataset includes sessions specifically featuring seizure events, alongside sessions without seizures for testing false alarm rates. It consists of data from three primary directories: training (train), development (dev), and evaluation (eval), with 7361 files in total, across various seizure and non-seizure events.

The dataset features EEG data in European Data Format (edf), with event-based annotations captured in both multi-class and bi-class formats. Multi-class annotations provide detailed seizure types, while bi-class annotations simplify the dataset into seizure (seiz) and background (bckg) labels. These annotations are recorded per channel, capturing the spread of seizures across multiple electrodes.

EEG recordings are captured using two common reference configurations: averaged reference (AR) and linked ears reference (LE), with the data adhering to the standard 10/20 channel montage for consistency across files. The dataset includes a vast number of seizure events, with specific counts for training, development, and evaluation sets.

The TUSZ corpus plays a vital role in the development and testing of advanced seizure detection systems, supporting both the detection of seizures and the analysis of seizure-free segments

## File Scan Result

> **Kernel SHA256**: `0c90e3ec94547026731787ac95cb32b924b667dc778975c503f0d947daff981f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `absz` | 121 | event | raw | Absence seizure |
| `bckg` | 15454 | event | raw | Background activity |
| `cpsz` | 1520 | event | raw | Complex partial seizure |
| `fnsz` | 4891 | event | raw | Focal non-specific seizure |
| `gnsz` | 2491 | event | raw | Generalized non-specific seizure |
| `mysz` | 3 | event | raw | Myoclonic seizure |
| `seiz` | 146 | event | raw | Seizure event (Common seizure class which can include all types of seizure) |
| `spsz` | 57 | event | raw | Simple partial seizure |
| `tcsz` | 199 | event | raw | Tonic-clonic seizure (At first stiffening and then jerking of body (Grand Mal)) |
| `tnsz` | 126 | event | raw | Tonic seizure (Stiffening of body during seizure, EEG effects disappears) |


> the meaning from dataset file "seizures_types_v02.xlsx"

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Binary Seizure Detection (Seizure vs Background)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`absz`, `bckg`, `cpsz`, `fnsz`, `gnsz`, `mysz`, `seiz`, `spsz`, `tcsz`, `tnsz`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Background / non-seizure |
  | `gnsz` | 1 | Generalized non-specific seizure |
  | `fnsz` | 1 | Focal non-specific seizure |
  | `cpsz` | 1 | Complex partial seizure |
  | `absz` | 1 | Absence seizure |
  | `tnsz` | 1 | Tonic seizure |
  | `spsz` | 1 | Simple Partial Seizure |
  | `mysz` | 1 | Myoclonic Seizure |
  | `tcsz` | 1 | Tonic Clonic Seizure |
- **Evidence**:
  - 10.1088/1741-2552/ac7d0d — Uses TUH EEG with 1-second windows (50% overlap) for binary seizure vs non-seizure classification; leave-one-out cross-subject evaluation
  - 10.1109/tii.2023.3274913 — Uses TUH EEG with 4-second non-overlapping epochs for binary seizure detection; CNN classifier achieved 98.48% average accuracy with leave-one-patient-out cross-validation
- **Notes**: 

### Potential Task 1: Multi-class Seizure Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`absz`, `cpsz`, `fnsz`, `gnsz`, `mysz`, `spsz`, `tcsz`, `tnsz`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `gnsz` | 0 | Generalized non-specific seizure |
  | `fnsz` | 1 | Focal non-specific seizure |
  | `cpsz` | 2 | Complex partial seizure |
  | `absz` | 3 | Absence seizure |
  | `tnsz` | 4 | Tonic seizure |
  | `spsz` | 5 | Simple Partial Seizure |
  | `tcsz` | 6 | Tonic Clonic Seizure |
  | `mysz` | 7 | Myoclonic Seizure |
- **Evidence**:

- **Notes**: classify further specific seizure, more challenge.

## Data Quality Notes

- ## Kernel Responsibilities

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# TUH EEG Slowing Corpus

**Dataset**: `tuh_eeg_slowing` | **Year**: 2017 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg
**Category**: Biological State | **Subjects**: 38 | **Files (Completed)**: 112 | **Channels**: 27-41 | **Sampling Rate**: 250/256/400/512 Hz | **Manual Review**: anonymous for review

## Paradigm

The TUH EEG Slowing Corpus is a subset of the TUH EEG Corpus, designed to aid in the development of algorithms that can differentiate between seizure and slowing events in EEG data. The dataset includes sessions with seizure events, slowing events, and complex background events. It contains 300 files, divided into 3 main categories: complex background, seizure, and slowing.

The corpus features EEG data in the European Data Format (EDF), along with annotated files in both term-based and event-based formats. Term-based annotations provide labels for 10-second segments, making them useful for machine learning tasks that focus on overall classification rather than individual channels. Event-based annotations include detailed timings and channel indices, representing the onset and duration of events across different channels.

Clinical EEGs in the dataset utilize two common reference configurations: averaged reference (AR) and linked ears reference (LE), in line with the 10/20 electrode system. A total of 38 patients contributed to the dataset across 75 sessions.

## File Scan Result

> **Kernel SHA256**: `25d3dd7c66e5c06b63d712490f8a5a2603faeb1a5d721ffa93853ebf56e412ab`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `bckg` | 2150 | event | raw | Background - normal EEG |
| `seiz` | 2143 | event | raw | Seizure activity |
| `slow` | 2119 | event | raw | EEG slowing (pathological slow-wave activity) |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: EEG Slowing Detection (2-Class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`slow`, `bckg`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Normal background EEG |
  | `slow` | 1 | EEG slowing (pathological slow-wave activity) |
- **Evidence**:

- **Notes**: 

### Potential Task 2: 3-Class EEG State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`seiz`, `slow`, `bckg`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Normal background EEG |
  | `slow` | 1 | EEG slowing |
  | `seiz` | 2 | Seizure activity |
- **Evidence**:

- **Notes**: 

## Data Quality Notes
- No subject-level demographics are available in the released metadata.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2007 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 | **Channels**: 14/16 | **Sampling Rate**: 8/64/128 | **Manual Review**: anonymous for review

## Paradigm

Twenty-five adult subjects suspected of sleep-disordered breathing underwent full overnight polysomnographic (PSG) monitoring at St. Vincent's University Hospital Sleep Disorders Clinic, Dublin, in the St. Vincent's University Hospital / University College Dublin Sleep Apnea Database. The PSG recordings are stored as EDF-format files with a `.rec` suffix and contain multiple physiological signals, including EEG (C3-A2, C4-A1), EOG, submental EMG, ECG, airflow, respiratory movement, oxygen saturation, snoring/body position, and pulse-related channels. Sleep stages were scored by an experienced sleep technologist according to Rechtschaffen and Kales rules and stored in companion `_stage.txt` files as 30-second epoch labels: 0 = Wake, 1 = REM, 2 = Stage 1, 3 = Stage 2, 4 = Stage 3, 5 = Stage 4, 6 = Artifact, and 7 = Indeterminate.

Companion `_lifecard.edf` files contain simultaneous three-channel Holter ECG recordings from a Reynolds Lifecard CF system and should not be treated as EEG/PSG sleep-staging recordings. For EEG benchmark processing, these Lifecard ECG files should be skipped or handled separately from the PSG `.rec` files.

## File Scan Result

> **Kernel SHA256**: `be40fcba92ce9917ba252fe3ec53369fedab8990c4fb6c78793c3654d5f32efe`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Sleep stage 1` | 3016 | event | raw | NREM Stage 1 (R&K scoring) |
| `Sleep stage 2` | 3403 | event | raw | NREM Stage 2 (R&K scoring) |
| `Sleep stage 3` | 6985 | event | raw | NREM Stage 3 / slow-wave sleep (R&K scoring) |
| `Sleep stage 4` | 673 | event | raw | NREM Stage 4 / deep slow-wave sleep (R&K scoring) |
| `Sleep stage 8` | 15 | event | raw | Undefined or artifact epoch; exclude from standard sleep-stage classification |
| `Sleep stage REM` | 1990 | event | raw | Rapid eye movement sleep |
| `Sleep stage W` | 4707 | event | raw | Wake |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `apnea_label` | native (raw misc in EEG file) | raw | Binary 0/1 derived from companion `_respevt.txt`: 1 when an `APNEA-*` or `HYP-*` event overlaps the current sample/window, otherwise 0. |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Available per subject in `SubjectDetails.xls` as `Age`, but not present in EDF headers. |
| `amplifier` | missing | PSG `.rec` files were acquired on a Jaeger-Toennies PSG system; companion `_lifecard.edf` files come from a Reynolds Lifecard CF Holter recorder. |
| `cap` | missing | Electrode cap/hardware model is not explicitly documented in the dataset release. |
| `handedness` | missing | Handedness is not reported in the public dataset metadata. |
| `sex` | missing | Available per subject in `SubjectDetails.xls` as `Gender`, but not present in EDF headers. |


## Tasks

### Classical Task 1: Sleep Stage Classification (5-class AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage REM`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 (N1) |
  | `Sleep stage 2` | 2 | NREM Stage 2 (N2) |
  | `Sleep stage 3` | 3 | NREM Stage 3 (AASM N3; merged with stage 4) |
  | `Sleep stage 4` | 3 | NREM Stage 4 (merged into AASM N3) |
  | `Sleep stage REM` | 4 | REM sleep |
- **Evidence**:
  - 10.1371/journal.pone.0256111 — 5-class sleep stage classification (W/N1/N2/N3/REM) using UCD Sleep Apnea Database; explicitly maps R&K stages 3 and 4 to single AASM N3 class; uses 30s epochs (tmin=0s, tmax=30s, no overlap); excludes undefined/artifact epochs.
- **Notes**: --

### Classical Task 2: Sleep Apnea Detection
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 5.0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `apnea_label` | Binary 0/1: 0 = no apnea/hypopnea event overlaps the 10 s window; 1 = at least one apnea/hypopnea event overlaps the 10 s window. Derived from `_respevt.txt` files (not a native signal channel). Needs verification: channel not present in MISC Label Summary. |
- **Evidence**:
  - 10.1109/TENSYMP49402.2020.9230848 — Binary apnea/non-apnea classification using 10-second EEG frames with 50% overlap from the UCD sleep apnea database; positive class includes obstructive, central, and mixed apnea/hypopnea events.
- **Notes**: --

### Potential Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30.0 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | Continuous value in years, per-subject. Available for all 25 subjects in `SubjectDetails.csv` / `SubjectDetails.xls`. Same value assigned to all epochs from a given subject. |
- **Evidence**:

- **Notes**: `age` is not present in the standard scanned info fields but can be injected from the companion SubjectDetails metadata. This is a Potential task because the dataset is small for age regression and no dataset-specific age-regression benchmark was identified. Use subject-level train/test splits to prevent leakage across 30 s segments from the same subject.

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Comprehensive clinical demographics in `SubjectDetails.xls` for all 25 subjects: Age, Gender, BMI, and PSG AHI (Apnea-Hypopnea Index).
- Sleep stages in `_stage.txt` are encoded as pure integers (0,1,2,3,4,5,8) representing 30s epochs — kernel must implement numeric-to-stage mapping.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 35 | **Files (Completed)**: 117 | **Channels**: 128 | **Sampling Rate**: 512 Hz | **Manual Review**: anonymous for review

## Paradigm

The dataset contains high-density EEG recordings from interictal migraine patients and healthy controls during three conditions: (1) **SSVEP** - steady-state visual evoked potentials elicited by visual stimuli flickering at 4 Hz and 6 Hz; (2) **SSAEP** - steady-state auditory evoked potentials elicited by amplitude-modulated tones at 4 Hz and 6 Hz; and (3) **resting state**. EEG was recorded using a BioSemi ActiveTwo system with a customized 128-channel high-density EEG montage, sampled at 512 Hz (Chamanzar et al., 2020).

According to the dataset documentation, the main study reports 17 interictal migraine patients and 18 age- and gender-matched healthy controls. The demographic table lists migraine participants M1-M18, but M13 lacks the SSAEP recording and was excluded from the main study dataset; M2, M6, and M18 were also excluded from some analyses because of medication. The matched control group consists of 18 controls, while C2, C6, and C12 are additional healthy control subjects available in the dataset rather than missing-data subjects.

The dataset enables comparison of sensory processing and resting-state EEG activity between migraine patients in the interictal period and healthy controls.

## File Scan Result

> **Kernel SHA256**: `04696b9de008be8dc5f92ddbac8703374e60d9fbe7d14a0898fb627163677e2f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `4Hz auditory feedback end for Health` | 221 | event | raw | 4 Hz auditory steady-state stimulus end (healthy controls) |
| `4Hz auditory feedback end for migraine` | 181 | event | raw | 4 Hz auditory steady-state stimulus end (migraine patients) |
| `4Hz auditory stimulation start for Health` | 2100 | event | raw | 4 Hz auditory steady-state stimulus onset (healthy controls) |
| `4Hz auditory stimulation start for migraine` | 1706 | event | raw | 4 Hz auditory steady-state stimulus onset (migraine patients) |
| `4Hz vision feedback end for Health` | 226 | event | raw | 4 Hz visual steady-state stimulus end (healthy controls) |
| `4Hz vision feedback end for migraine` | 200 | event | raw | 4 Hz visual steady-state stimulus end (migraine patients) |
| `4Hz vision stimulation start for Health` | 2016 | event | raw | 4 Hz visual steady-state stimulus onset (healthy controls) |
| `4Hz vision stimulation start for migraine` | 1787 | event | raw | 4 Hz visual steady-state stimulus onset (migraine patients) |
| `6Hz auditory feedback end for Health` | 176 | event | raw | 6 Hz auditory steady-state stimulus end (healthy controls) |
| `6Hz auditory feedback end for migraine` | 137 | event | raw | 6 Hz auditory steady-state stimulus end (migraine patients) |
| `6Hz auditory stimulation start for Health` | 2099 | event | raw | 6 Hz auditory steady-state stimulus onset (healthy controls) |
| `6Hz auditory stimulation start for migraine` | 1705 | event | raw | 6 Hz auditory steady-state stimulus onset (migraine patients) |
| `6Hz vision feedback end for Health` | 165 | event | raw | 6 Hz visual steady-state stimulus end (healthy controls) |
| `6Hz vision feedback end for migraine` | 150 | event | raw | 6 Hz visual steady-state stimulus end (migraine patients) |
| `6Hz vision stimulation start for Health` | 2016 | event | raw | 6 Hz visual steady-state stimulus onset (healthy controls) |
| `6Hz vision stimulation start for migraine` | 1779 | event | raw | 6 Hz visual steady-state stimulus onset (migraine patients) |
| `resting Health` | 21 | event | raw | Resting-state EEG recording (healthy controls) |
| `resting migraine` | 18 | event | raw | Resting-state EEG recording (migraine patients) |


> The task events are encoded as numeric trigger values in the BioSemi Status channel. For sensory tasks, the main epoch labels described in the protocol are 1 and 2 for the onset of 4 Hz and 6 Hz stimulation, respectively, and 11 and 22 for response/feedback-related markers following 4 Hz and 6 Hz trials. The stimulus-onset markers correspond to the start of the 2 s visual or auditory stimulation. The 11/22 markers are not generic trial-end markers; they are emitted only for feedback/response trials in which a response was detected. In addition to these epoch labels, the stimulus scripts also send task-level markers such as 30 near the start of the task and 20 near the end.
> 
> For resting state, the protocol defines label 1 as the start of a resting block and label 2 as the end of a resting block. The available BDF files do contain such 1/2 resting-state block markers, although the markers visible in the current subset may not fully cover all six 2 min blocks described in the protocol.
> 
> Any scanned event names that include group suffixes such as healthy/control or migraine should be treated as interpreted labels rather than raw trigger codes. These group labels should be removed or normalized before constructing modality- or frequency-classification tasks to avoid label leakage.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (108/117) | N/A |
| `sex` | partial (108/117) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Migraine Patient vs Healthy Control Classification (SSVEP/SSAEP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz auditory stimulation start for Health`, `4Hz auditory stimulation start for migraine`, `4Hz vision stimulation start for Health`, `4Hz vision stimulation start for migraine`, `6Hz auditory stimulation start for Health`, `6Hz auditory stimulation start for migraine`, `6Hz vision stimulation start for Health`, `6Hz vision stimulation start for migraine`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `4Hz vision stimulation start for Health` | 0 | Healthy control |
  | `6Hz vision stimulation start for Health` | 0 | Healthy control |
  | `4Hz auditory stimulation start for Health` | 0 | Healthy control |
  | `6Hz auditory stimulation start for Health` | 0 | Healthy control |
  | `4Hz vision stimulation start for migraine` | 1 | Interictal migraine patient |
  | `6Hz vision stimulation start for migraine` | 1 | Interictal migraine patient |
  | `4Hz auditory stimulation start for migraine` | 1 | Interictal migraine patient |
  | `6Hz auditory stimulation start for migraine` | 1 | Interictal migraine patient |
- **Evidence**:
  - Protocol: sensory-task labels `1` and `2` mark the onset of 4 Hz and 6 Hz stimulation, respectively; each visual or auditory stimulus lasts 2 s. Labels `11` and `22` are response/feedback-related markers and should not be treated as generic trial-end markers.
  - 10.1093/braincomms/fcab061 — Chamanzar et al. compare high-density EEG responses between interictal migraine participants and healthy controls during 4 Hz / 6 Hz visual and auditory stimulation and resting state.
- **Notes**: Uses Event Structure labels that encode group membership (`for Health` vs `for migraine`). M13 lacks SSAEP/auditory data and should be excluded from SSAEP-specific analyses. C2, C6, and C12 are additional available healthy controls rather than missing-data controls. Use subject-level train/test splitting to avoid leakage across epochs from the same participant.

### Potential Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz vision stimulation start for Health`, `4Hz vision stimulation start for migraine`, `6Hz vision stimulation start for Health`, `6Hz vision stimulation start for migraine`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `4Hz vision stimulation start for Health` | 0 | 4 Hz visual flicker stimulus |
  | `4Hz vision stimulation start for migraine` | 0 | 4 Hz visual flicker stimulus |
  | `6Hz vision stimulation start for Health` | 1 | 6 Hz visual flicker stimulus |
  | `6Hz vision stimulation start for migraine` | 1 | 6 Hz visual flicker stimulus |
- **Evidence**:
  - Protocol: SSVEP trials used Gaussian-filtered vertical sine-wave gratings alternating contrast sinusoidally at 4 Hz or 6 Hz for 2 s. Labels `1` and `2` indicate 4 Hz and 6 Hz stimulus onset, respectively.
  - 10.1093/braincomms/fcab061 — The visual stimulation condition includes 4 Hz and 6 Hz steady-state visual stimulation, enabling frequency-specific SSVEP analysis.
- **Notes**: Restrict this task to SSVEP/visual recordings. The group suffixes are included only because they are part of the available Event Structure IDs; the classification target should be frequency, not subject group.

## Data Quality Notes

- Group labels are subject-level metadata derived from the subject ID prefix (`M` = migraine, `C` = control), not native task labels. Raw scanned event names may also contain group-specific suffixes and should be normalized before task construction to avoid label leakage.
- Subject age/sex metadata are available for the 36 matched-analysis participants in `Migraine_Control_Demographics.csv`, but not for the extra released controls (`C2`, `C6`, `C12`).
- Subject `M13` lacks the SSAEP recording, so auditory-task availability differs from the nominal participant count.
- The released dataset and the publication analysis subset are not identical: `M2`, `M6`, and `M18` were excluded from the main paper analysis because of medication, and `C2`, `C6`, `C12` are extra released controls not included in the matched-analysis metadata file.
- The protocol defines numeric trigger codes for stimulus onset/feedback and six 2 min resting blocks, whereas the scanned event table contains interpreted text labels; event semantics should be checked carefully before epoching.
- `feedback end` markers correspond to the end of the post-stimulus feedback/response interval and are not generic trial-end markers; they occur only in feedback trials.
- Recordings use a 128-channel high-density montage, which increases spatial detail but also makes channel handling and interpolation choices more consequential.
- The associated publication analyzed both sensory and resting EEG in 2 s windows; resting-state analyses used non-overlapping 2 s intervals.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed

---

# TUH EEG Artifact Corpus

**Dataset**: `tuh_eeg_artifact` | **Year**: 2021-2020/2024 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Others | **Subjects**: 213 | **Files (Completed)**: 310 | **Channels**: 27-41 | **Sampling Rate**: 250/256/400/512 Hz | **Manual Review**: anonymous for review

## Paradigm

The TUH EEG Artifact Corpus (TUAR) is a comprehensive dataset designed for the identification and evaluation of various artifacts in electroencephalogram (EEG) signals. This dataset includes EEG recordings annotated for multiple types of artifacts such as eye movements, muscle artifacts, and electrode issues, among others. The corpus has been developed to assist in the training and evaluation of artifact detection models, with its latest release (v3.0.1) offering detailed annotations for all relevant events across different channel configurations. The data is divided into files containing EEG signals, with annotations provided in CSV format to mark the start and stop times of specific artifact events. It consists of over 160,000 events from 310 EEG files, covering 213 patients and a total of nearly 100 hours of data. This dataset is particularly useful for research involving artifact detection and seizure classification in clinical EEG data. Notably, it includes specific seizure annotations alongside standard artifact labels, facilitating the analysis of co-occurring events. Researchers are encouraged to cite the corresponding publications for more details on the dataset's creation and annotation methodology.

## File Scan Result

> **Kernel SHA256**: `a76e25dadae339282ebf9cccfcc2d5d2081b8e73ccf097ad905d7e92cc8fb67e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `chew` | 6482 | event | raw | Chewing artifact period in EEG signal |
| `chew_elec` | 152 | event | raw | Concurrent chewing and electrode artifact in EEG |
| `chew_musc` | 243 | event | raw | Concurrent chewing and muscle artifact in EEG |
| `elec` | 33130 | event | raw | Electrode artifact period in EEG signal |
| `elpp` | 172 | event | raw | Electrode/potential artifact period in EEG signal |
| `eyem` | 38569 | event | raw | Eye movement artifact period in EEG signal |
| `eyem_chew` | 864 | event | raw | Concurrent eye movement and chewing artifact in EEG |
| `eyem_elec` | 2422 | event | raw | Concurrent eye movement and electrode artifact in EEG |
| `eyem_musc` | 18677 | event | raw | Concurrent eye movement and muscle artifact in EEG |
| `eyem_shiv` | 45 | event | raw | Concurrent eye movement and shivering artifact in EEG |
| `musc` | 51052 | event | raw | Muscle artifact period in EEG signal |
| `musc_elec` | 7651 | event | raw | Concurrent muscle and electrode artifact in EEG |
| `shiv` | 613 | event | raw | Shivering artifact period in EEG signal |
| `shiv_elec` | 1 | event | raw | Concurrent shivering and electrode artifact in EEG |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Artifact Type Classification (13-class, Event-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, overlap = 0, target_events = [`chew`, `chew_elec`, `chew_musc`, `elec`, `elpp`, `eyem`, `eyem_chew`, `eyem_elec`, `eyem_musc`, `eyem_shiv`, `musc`, `musc_elec`, `shiv`, `shiv_elec`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `eyem` | 0 | Eye movement artifact |
  | `musc` | 1 | Muscle (EMG) artifact |
  | `elec` | 2 | Electrode artifact |
  | `chew` | 3 | Chewing artifact |
  | `shiv` | 4 | Shivering artifact |
  | `elpp` | 5 | Electrode pop |
  | `eyem_musc` | 6 | Combined eye movement + muscle |
  | `eyem_elec` | 7 | Combined eye movement + electrode |
  | `eyem_chew` | 8 | Combined eye movement + chewing |
  | `musc_elec` | 9 | Combined muscle + electrode |
  | `chew_elec` | 10 | Combined chewing + electrode |
  | `chew_musc` | 11 | Combined chewing + muscle |
  | `eyem_shiv` | 12 | Combined eye movement + shivering |
- **Evidence**:
  - 10.1109/EMBC48229.2022.9871413 — Achieves 93.95% accuracy with MMC on 1-second windows from artifact onset; uses FFT and DWT features on 4 temporal channels at 250 Hz
- **Notes**: The source paper reports 13 classes; this release uses a 6-class grouping based on reviewer suggestions.

### Potential Task 1: Pure Artifact Family Classification (6-class, Event-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, overlap = 0, target_events = [`chew`, `elec`, `elpp`, `eyem`, `musc`, `shiv`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `eyem` | 0 | Eye movement artifact |
  | `musc` | 1 | Muscle (EMG) artifact |
  | `elec` | 2 | Electrode artifact |
  | `chew` | 3 | Chewing artifact |
  | `shiv` | 4 | Shivering artifact |
  | `elpp` | 5 | Electrode pop |
- **Evidence**:
  - 10.1109/EMBC48229.2022.9871413 — Achieves 93.95% accuracy with MMC on 1-second windows from artifact onset; uses FFT and DWT features on 4 temporal channels at 250 Hz
- **Notes**: Restrict this potential task to the six pure artifact labels only. Multi-component labels such as `eyem_musc` and `musc_elec` are excluded because the current rulebook expects single integer class assignments rather than multi-label targets.

## Data Quality Notes

- Annotations are at the channel level; aggregate to recording level or use channel-specific labels depending on the task.
- Variable channel count and sampling rate; normalize before cross-recording analysis.
- Sex is not reliably available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed

---

