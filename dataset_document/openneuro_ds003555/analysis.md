# Dataset of EEG Recordings of Pediatric Patients with Epilepsy Based on the 10-20 System

**Dataset**: `openneuro_ds003555` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003555
**Category**: Biological State | **Subjects**: 30 | **Files (Completed)**: 257 | **Channels**: 52 | **Sampling Rate**: 2000 Hz | **Manual Review**:

## Paradigm

Continuous sleep EEG recordings from pediatric patients with epilepsy, focused on identifying High-Frequency Oscillations (HFOs) as clinical biomarkers during N3 slow-wave sleep stages. The dataset was recorded using the standard 10-20 electrode system and is intended for automated HFO detection algorithm development and sleep stage analysis. No task-based paradigm was employed; recordings capture spontaneous brain activity during sleep.

## File Scan Result

> **Kernel SHA256**: `f8fd5c3d96162132f8fe7a85f79fe71e06ea4a51520c68f03c79e0cff8aadb72`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: HFO rate vs age regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 300 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Regression target: subject chronological age in years (range 0.7–17.4). All segments from same subject share identical label. |
- **Evidence**:
  - 10.3389/fnins.2022.861480 — Investigates age-related changes in HFOs in pediatric population; HFO rate (ripples per minute) varies with age and is clinically relevant as non-invasive biomarker of epileptogenicity
- **Notes**: Archetype C with native info column (age). Segmentation produces 5-minute segments matching the N3 interval selection described in README. The model must learn HFO-related features from the raw EEG signal to predict subject age. Since age is a subject-level variable, all segments from the same subject receive identical regression targets, encouraging the model to extract stable HFO rate signatures across segments. No derived misc channel is required; the kernel operates on raw EEG and uses native participants.tsv age column.

---

### Potential Task 1: Age Prediction from Sleep EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Regression target: subject-level age in years (range 0.7–17.4). Applied to all segments from that subject; pediatric population with focal or generalized epilepsy. |
- **Evidence**:
  - participants.tsv — age column complete for all 30 subjects (range 0.7–17.4 years)
  - README — "how high-frequency oscillations are impacted by age in the pediatric population" establishes age as key variable of interest
  - eeg.json — TaskDescription confirms study of "age related changes in case of pediatric patients"
- **Notes**: Segmentation-based approach using standard 30-second PSG epochs with 50% overlap to maximize sample count. Age is a subject-level continuous variable from participants.tsv (native info field), requiring no kernel derivation. All segments from a given subject share the same age label, making this a subject-level regression task with multiple samples per subject.

---

### Potential Task 2: Sex Classification from Sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | Classification target: binary encoding from participants.tsv sex field. f → class 0 (female), m → class 1 (male). |
- **Evidence**:
  - participants.tsv — 30 subjects with complete sex information: 16 female (f), 14 male (m)
- **Notes**: Subject-level binary classification from continuous sleep EEG segments. 30-second segments with 50% overlap are standard for sleep EEG analysis. Sex is a per-subject demographic variable applied uniformly to all segments from each subject. The task leverages well-documented sex differences in sleep EEG spectral properties as a valid supervised learning objective, though this was not the primary study goal (HFO detection in epilepsy).

---

### Potential Task 3: Pathology Classification from Sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `pathology`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | pathology | Classification target: 7-class encoding from participants.tsv pathology field. Classes: 0=perinatal_ischemic (bilateral perinatal ischemic lesions with left predominance), 1=genetic_dmn1 (genetic: DMN1 mutation), 2=fcd_radiologic ((radiologic suspicion of) FCD), 3=genetic_other (genetic), 4=perinatal_thalamic (perinatal thalamic bleeding, hippocampal atrophy/sclerosis?), 5=fcd_1a (FCD 1a), 6=mmcd (mMCD). Needs verification: small sample size (~4-5 subjects/class) may require merging into coarser groupings. |
- **Evidence**:
- **Notes**: Subject-level pathology labels from participants.tsv are applied to all 30-second segments. Seven distinct pathologies are encoded as 0-based integers. Given small sample size (N=30 total, ~4-5 subjects per class), downstream may merge into coarser groupings (e.g. structural vs genetic vs FCD). Segment length of 30s is standard for sleep EEG analysis and matches the N3 interval selection described in the dataset. The pathology field is a native participants.tsv column requiring no kernel derivation.

---

### Potential Task 4: Continuous Sleep EEG Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Regression target: subject age in years (range 0.7–17.4) used as proxy continuous variable for unsupervised pre-training compatibility. All segments from same subject share identical age label. |
- **Evidence**:
- **Notes**: This archetype C task uses pure segmentation with no discriminating native label available for unsupervised learning. The kernel uses the native `age` info field as a technically valid regression target to satisfy the framework, though the semantic goal is representation learning on continuous sleep EEG at 2000 Hz. The 2.0s segments (4000 samples) with 50% overlap are appropriate for HFO-scale analysis as noted in the dataset analysis. No native events or misc channels provide usable continuous labels for this paradigm; age serves as a subject-level continuous placeholder enabling training infrastructure compatibility.

## Data Quality Notes

- Very high sampling rate (2000 Hz); high memory requirements for processing.
- Pediatric epilepsy population; inter-individual variability in seizure history and medications.
- HFO detection requires high-frequency filtering (80-500 Hz); standard 0.5-40 Hz bandpass not appropriate for primary analysis goal.
- No event markers detected; continuous sleep EEG recording without trial-level events.
- Device information missing from metadata.
- Small sample size (N=30) with class imbalance for pathology classification (~4-5 subjects per class).

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
