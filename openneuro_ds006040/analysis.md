# Sustained Attention Task (gradCPT) Dataset using simultaneous EEG-fMRI and DTI

**Dataset**: `openneuro_ds006040` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006040
**Category**: High-level Mental | **Subjects**: 28 | **Files (Completed)**: 1064 | **Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

The dataset uses the Gradual Continuous Performance Task (gradCPT) to measure sustained attention via simultaneous EEG and fMRI recording. Participants detect rare city scenes (targets, S245) within a stream of common mountain scenes (standards, S155). Additional tasks include resting state, visual checkerboard stimulation, and mental imagery. MRI synchronization pulses (TR, Sync On) and cardiac (qrs) signals are also recorded.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S155` | 201922 | event | raw | Standard stimulus (mountain scene, frequent) |
| `S245` | 201110 | event | raw | Target stimulus (city scene, rare) |
| `Sync On` | 195242 | admin | raw | MRI sync pulse onset |
| `qrs` | 170358 | admin | raw | Cardiac QRS complex |
| `TR` | 106494 | admin | raw | MRI TR repetition marker |
| `T 1` | 52960 | admin | raw | Timing marker |
| `S254` | 813 | event | raw | Response / button press |
| `[]` | 15 | admin | raw | Empty/null event |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S155`, `S245`, `S254`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: gradCPT Trial Correctness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`, `S254`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | correct_trial | 0 | Correct commission (S245+press) or correct omission (S155+no press) |
  | incorrect_trial | 1 | Commission error (S155+press) or omission error (S245+no press) |
- **Super Meta Notes**: Derived from raw events [`S155`, `S245`, `S254`]. For each stimulus event (S155 or S245), kernel must check whether S254 occurred within the trial window (0-2s) to determine if response was correct. Labels: correct commission = S245 + S254 within window; correct omission = S155 + no S254; commission error = S155 + S254 within window; omission error = S245 + no S254. Combine correct commission + correct omission into y=0, commission error + omission error into y=1.
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Classifies correct vs incorrect trials (commission/omission errors) in sustained attention using gradCPT stimuli (S155=mountain/standard, S245=city/target) and button press responses (S254).
- **Kernel Notes**: Epoch around each S155/S245 stimulus. Within each epoch, check for presence/absence of S254 to derive trial outcome. Downsample from 5000 Hz before processing.

### Classical Task 2: gradCPT Attention State Classification (In-Zone vs Out-of-Zone)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | in_zone | 0 | Low RT variability (sustained attention maintained) |
  | out_zone | 1 | High RT variability (attention lapses) |
- **Super Meta Notes**: Derived from raw events [`S155`, `S245`]. Kernel must compute RT variability across consecutive correct trials within a rolling window. If variability < threshold → in_zone (y=0), if > threshold → out_zone (y=1). Requires reaction time extraction from S254 events.
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Classifies in-the-zone vs out-of-the-zone attention states based on RT variability during correct trials in gradCPT.
- **Kernel Notes**: Must compute reaction time from S254 events and derive rolling RT variability. Downsample from 5000 Hz before processing.

### Classical Task 3: gradCPT Stimulus Classification (Mountain vs City)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S155` | 0 | Standard stimulus (mountain scene, withhold response) |
  | `S245` | 1 | Target stimulus (city scene, press button) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Uses gradCPT paradigm with mountain (S155) as frequent standard and city (S245) as rare target stimuli.
- **Kernel Notes**: Basic stimulus-locked epoching for S155 vs S245 classification. Downsample from 5000 Hz before processing.

### Potential Task 1: gradCPT Sustained Attention (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Primary scientific contrast is S155 (standard) vs S245 (target) for gradCPT attention decoding. `Sync On`, `TR`, `qrs`, `T 1` are MRI/cardiac markers. Very high sampling rate (5000 Hz); downsample before processing.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Sync On` | 0 | MRI sync pulse |
 | `S155` | 1 | Standard (mountain) |
 | `TR` | 2 | MRI TR marker |
 | `S245` | 3 | Target (city) |
 | `qrs` | 4 | Cardiac QRS |
 | `T 1` | 5 | Timing marker |
 | `S254` | 6 | Button press/response |
 | `[]` | 7 | Null event |

## Data Quality Notes

- Very high sampling rate (5000 Hz); downsample to <=1000 Hz for most analyses.
- `Sync On`, `TR`, `qrs` are MRI/cardiac markers and should be excluded from stimulus-locked analysis.
- Simultaneous EEG-fMRI data requires MRI artifact correction (template subtraction or similar).


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review