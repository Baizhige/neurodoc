# Delayed Auditory Feedback EEG/EGG

**Dataset**: `openneuro_ds005403` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005403
**Category**: High-level Mental | **Subjects**: 66 | **Files (Completed)**: 66 | **Channels**: 66 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a speech production task while receiving delayed auditory feedback (DAF) to study neural processing of self-generated speech and auditory-motor monitoring. Three DAF conditions were used: an adaptation condition (fixed delay) and two random delay conditions (random1, random2), compared against a baseline (no delay). EEG was recorded alongside electroglottography (EGG) to capture vocal fold activity simultaneously. The event markers label continuous speech production blocks.

## File Scan Result

> **Kernel SHA256**: `3d5a9d709f331dee8f33df5cdfa388ee03cf9ae11db1a0faf30384b477712d1f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `adaption` | 2560 | event | raw | Adaptation DAF condition (fixed delay) |
| `baseline` | 640 | event | raw | Baseline (no delay) speech production |
| `random1` | 1600 | event | raw | Random delay condition 1 |
| `random2` | 1600 | event | raw | Random delay condition 2 |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `audio`, `audio_envelope`, `audio_onsets`, `egg`, `egg_envelope`, `egg_onsets`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: EEG Encoding/Decoding of Glottal and Audio Features During DAF
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = null, overlap = null, target_events = [`baseline`, `adaption`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|----------|
  | `baseline` | continuous | Baseline (no delay) speech production block |
  | `adaption` | continuous | Adaptation DAF condition block |
- **Evidence**:
  - DOI: 10.1523/jneurosci.2294.24.2025 — Encoding models predict EEG from glottal/audio features; decoding models predict glottal event onsets from EEG during speech production with delayed auditory feedback
- **Kernel Notes**: 
    1. Extract raw EEG epochs aligned to baseline/adaption blocks using epoch_by_long_event_hdf5
    2. Derive audio envelope from raw audio channels through signal processing (gammatone filter bank, envelope computation)
    3. Derive EGG envelope from EGG channel (verify channel type labels)
    4. Compute onset times from audio envelope and EGG envelope
    5. Compute time-lagged features (e.g., -0.5s to +0.5s around each EEG time point)
    6. Train encoding model: predict EEG from audio/EGG features using ridge regression
    7. Train decoding model: predict glottal event onsets from EEG using regression

### Potential Task 1: DAF Condition Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = [`baseline`, `adaption`, `random1`, `random2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|----------|
  | `baseline` | 0 | Baseline (no delay) speech production |
  | `adaption` | 1 | Adaptation DAF condition |
  | `random1` | 2 | Random delay condition 1 |
  | `random2` | 3 | Random delay condition 2 |
- **Evidence**:
  - No DOI available; task is plausible from paradigm description — the three DAF conditions (adaption, random1, random2) and baseline differ in delay timing and predictability, which should produce distinguishable neural signatures during speech production monitoring
- **Kernel Notes**:
    1. Apply bandpass filter (1-40 Hz) and artifact rejection before epoching
    2. Verify EGG channel type labels alongside EEG channels
    3. Baseline has ~3-4x fewer events per subject (640 total vs ~1600-2560 per other condition); use class weighting or balanced sampling for classification