# EEG: 3-Stim Auditory Oddball and Rest in Parkinson's

**Dataset**: `openneuro_ds003490` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003490
**Category**: Sensory/Response | **Subjects**: 50 | **Files (Completed)**: 75 | **Channels**: 67 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A three-stimulus auditory oddball task (standard tones, target tones requiring button-press response, and novel distractor tones) combined with resting-state (eyes open and eyes closed) EEG recordings in Parkinson's disease patients and age-matched healthy controls. The study aims to identify auditory P300 and mismatch negativity differences between PD patients and controls. BioSemi STATUS markers (S 85, S255) are system admin events to be excluded.

## File Scan Result

> **Kernel SHA256**: `a66ae57b2e72950c6a8876202001fd45ad0894ebb4db219fc36faf0c041a5f64`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 2280 | event | raw | Eyes Open resting block |
| `S  2` | 2280 | event | raw | Eyes Closed resting block |
| `S  3` | 2252 | event | raw | Resting block (sub-condition or session) |
| `S  4` | 2254 | event | raw | Resting block (sub-condition or session) |
| `S 85` | 1 | admin | raw | BioSemi STATUS marker - exclude |
| `S200` | 2230 | event | raw | Standard tone (frequent non-target) |
| `S201` | 10166 | event | raw | Target tone (requires button press, P3b) |
| `S202` | 2229 | event | raw | Novel distractor tone (rare, P3a) |
| `S255` | 1 | admin | raw | BioSemi STATUS marker - exclude |
| `boundary` | 75 | event | raw | Recording boundary marker - exclude |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Parkinson's Disease vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 2.0 s, target_events = [`S200`, `S201`, `S202`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--|-------|
  | `S200` | 0 | Standard tone (non-target) |
  | `S201` | 1 | Target tone (requires button press) |
  | `S202` | 2 | Novel distractor tone |
- **Super Meta Notes**: Subject-level classification of PD patients (ON/OFF medication) vs healthy controls using EEG features extracted from tone-evoked epochs (±2s). Aggregate epoch-level complexity features (LZC, SampEn), frequency domain (FFT), or texture features (Haralick, Fractal) per subject, then classify groups using SVM or RF. Group labels derived from participants.tsv (PD_ON, PD_OFF, HC). Verify S200/S201/S202 mapping to Standard/Target/Novel via StimChannel; exclude STATUS markers (S 85, S255) and boundary events.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2017.11.023 — SVM pattern classifiers on EEG novelty responses achieved 82% accuracy classifying PD vs controls; 3-class (PD_ON/PD_OFF/HC) classification supported
  - DOI: 10.21528/cbic2023.027 — Haralick and Fractal texture features from ±2s EEG epochs used to classify PD vs healthy controls; RF achieved 79.49% accuracy
  - DOI: 10.1038/s41598-025-00826-5 — EEG complexity metrics (Lempel-Ziv, sample entropy) during 3-stimulus oddball classify PD patients from healthy controls
- **Kernel Notes**: Load participants.tsv for group mapping. Extract epochs around S200/S201/S202 events per subject, compute features per epoch, aggregate (mean/std) to subject level. Exclude S 85 and S255 (BioSemi STATUS). Do not mix tone epochs with resting-state blocks.

### Potential Task 1: Auditory Tone Type Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`S200`, `S201`, `S202`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--|-------|
  | `S200` | 0 | Standard tone (frequent non-target) |
  | `S201` | 1 | Target tone (infrequent, P3b) |
  | `S202` | 2 | Novel tone (rare distractor, P3a) |
- **Evidence**: DOI: 10.1016/j.clinph.2017.11.023 — Midfrontal EEG responses to novelty discriminate stimulus types; standard oddball paradigm supports tone categorization via P300 components
- **Kernel Notes**: Onset-aligned epoching captures P300 (P3a/P3b) components distinguishing Novel/Target from Standard. Verify event mapping via StimChannel. Exclude S 85, S255, boundary. Rest blocks are separate paradigm—do not combine.

### Potential Task 2: Eyes Open vs Eyes Closed Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, segment_length = 2.0 s, target_events = [`S  1`, `S  2`, `S  3`, `S  4`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--|-------|
  | `S  1` | 0 | Eyes Open resting block |
  | `S  2` | 1 | Eyes Closed resting block |
- **Evidence**: Paradigm documentation indicates eyes open (S 1) and eyes closed (S 2) blocks; S 3/S 4 may represent additional rest conditions or sub-blocks
- **Kernel Notes**: Sustained resting-state blocks require sliding window approach (50% overlap) to capture ongoing dynamics. Exclude STATUS (S 85, S255) and boundary events. Do not mix rest epochs with tone epochs.