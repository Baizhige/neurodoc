# Ear-EEG Sleep Monitoring 2017 (EESM17)

**Dataset**: `openneuro_ds004348` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004348
**Category**: Biological State | **Subjects**: 9 | **Files (Completed)**: 36 | **Channels**: 35 | **Sampling Rate**: 200 Hz
**Manual Review**: Pending

## Paradigm

Nightly sleep monitoring and pre-sleep resting recordings using ear-EEG and partial polysomnography in a naturalistic home environment. Nine healthy subjects were recorded simultaneously with PSG and ear-EEG for one night each. Subjects wore ear-mounted EEG devices during sleep, enabling investigation of sleep stage classification using AASM guidelines and comparison between ear-EEG and conventional PSG signals. Manual scoring was performed by trained clinical experts following AASM guidelines.

## File Scan Result

> **Kernel SHA256**: `adde5deb2af08ea52bb7d8003448bf6c7276db5e32bf801abb81d8507f916b40`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `512` | 16 | event | raw | Unknown trigger code |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep Stage Classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | W | 0 | Wake stage |
  | N1 | 1 | Non-REM Stage 1 |
  | N2 | 2 | Non-REM Stage 2 |
  | N3 | 3 | Non-REM Stage 3 (slow wave sleep) |
  | R | 4 | REM stage |
- **Evidence**:
  - DOI: 10.1186/s12938-017-0400-5 — "Automatic sleep staging using ear-EEG." Nine healthy subjects recorded simultaneously with PSG and ear-EEG for one night each. Random forest classifier trained to automatically score sleep stages (W/REM/NREM1/NREM2/NREM3) from ear-EEG data, comparing to manual expert scoring. Cohen's kappa 0.5–0.8, leave-one-out cross-validation specificity 0.94, sensitivity 0.52. Confirms AASM-standard 30-second non-overlapping epochs.
- **Kernel Notes**: Sleep stage labels are in PSG annotation files (Hypnogram/XML), NOT raw event markers. Extract 30-s epochs aligned to AASM standard scoring windows and map to W/N1/N2/N3/R labels. The `Awake` raw event marker serves only as a boundary reference for wake periods. Filter out `Artifact` and `Arousal` annotations from training data. Severe class imbalance expected: N3 and REM are rare relative to N2. Only 9 subjects limits generalization. Include channel selection to exclude non-EEG channels (ECG, respiratory belt) from 35-channel set.

### Normal Task 1: Sleep Quality Metrics
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | TST | continuous | Total Sleep Time (minutes) |
  | SE | continuous | Sleep Efficiency (%) |
  | WASO | continuous | Wake After Sleep Onset (minutes) |
  | SL | continuous | Sleep Latency (minutes to N1) |
- **Evidence**:
  - DOI: 10.1186/s12938-017-0400-5 — Supports derivation of sleep quality metrics from AASM-scored sleep stages. Manual scoring by trained clinical experts following AASM guidelines enables extraction of standard sleep parameters.
- **Kernel Notes**: Derive metrics from sleep stage annotation sequences: TST = sum of all N1+N2+N3+REM epoch durations; WASO = sum of W epochs within sleep period; SE = (TST / Sleep Period Time) × 100; SL = time from Lights Off to first N1 epoch. Use `Lights Off` and `Lights On` events as boundary markers for sleep period. Report per-subject metrics for group-level analysis.

### Potential Task 1: Pre-Sleep Resting State Characterization
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | PreSleep_Resting | 0 | Pre-sleep resting-state EEG segment |
- **Evidence**:
  - Plausible from paradigm: Dataset includes pre-sleep resting recordings between "Beginning of Recording" and "Lights Off" markers. Standard resting-state EEG characterization uses short segments (4–10 s) with moderate overlap for robust spectral estimation.
- **Kernel Notes**: Extract continuous EEG segments from the pre-sleep period only (between `Beginning of Recording` and `Lights Off` events). Exclude artifact-contaminated portions. Use segmentation with 4-second windows and 50% overlap for spectral feature extraction (alpha/mu/beta band power). Apply to ear-EEG channels only. This task enables baseline EEG characterization before sleep onset for comparison with other datasets.