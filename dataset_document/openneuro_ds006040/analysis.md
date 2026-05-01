# Sustained Attention Task (gradCPT) Dataset using simultaneous EEG-fMRI and DTI

**Dataset**: `openneuro_ds006040` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006040
**Category**: High-level Mental | **Subjects**: 28 | **Files (Completed)**: 1064 | **Channels**: 64 | **Sampling Rate**: 5000 Hz | **Manual Review**: Pending

## Paradigm

The dataset uses the Gradual Continuous Performance Task (gradCPT) to measure sustained attention via simultaneous EEG and fMRI recording. Participants detect rare city scenes (targets, S245) within a stream of common mountain scenes (standards, S155). Additional tasks include resting state, visual checkerboard stimulation, and mental imagery. MRI synchronization pulses (TR, Sync On) and cardiac (qrs) signals are also recorded.

## File Scan Result

> **Kernel SHA256**: `c366a0baea6143a577a42e690cd48c882a632f54dfdcf84b5eecf48aba27ec43`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S155` | 201922 | event | raw | Standard stimulus (mountain scene, frequent) |
| `S245` | 201110 | event | raw | Target stimulus (city scene, rare) |
| `S254` | 813 | event | raw | Response/button press |
| `Sync On` | 195242 | admin | raw | MRI sync pulse onset |
| `T  1` | 52960 | admin | raw | Timing marker |
| `TR` | 106494 | admin | raw | MRI TR repetition marker |
| `[]` | 15 | admin | raw | Empty/null event |
| `boundary` | 1064 | admin | raw | Segment boundary |
| `qrs` | 170358 | admin | raw | Cardiac QRS complex |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: gradCPT Trial Correctness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`, `S254`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `correct_trial` | 0 | Correct commission (S245+press) or correct omission (S155+no press) |
  | `incorrect_trial` | 1 | Commission error (S155+press) or omission error (S245+no press) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Classifies correct vs incorrect trials (commission/omission errors) in sustained attention using gradCPT stimuli (S155=mountain/standard, S245=city/target) and button press responses (S254).
- **Kernel Notes**: Epoch around each S155/S245 stimulus. Within each epoch, check for presence/absence of S254 to derive trial outcome. S254 count (813) is low relative to stimuli (400k+), indicating mostly correct withhold responses. Downsample from 5000 Hz before processing.

### Classical Task 2: gradCPT Attention State Classification (In-Zone vs Out-of-Zone)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `in_zone` | 0 | Low RT variability (sustained attention maintained) |
  | `out_zone` | 1 | High RT variability (attention lapses) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Classifies in-the-zone vs out-of-the-zone attention states based on RT variability during correct trials in gradCPT.
- **Kernel Notes**: Must compute reaction time from S254 events and derive rolling RT variability (e.g., coefficient of variation over 5-10 trial rolling window). Low variability → in_zone (y=0), high variability → out_zone (y=1). Downsample from 5000 Hz before processing.

### Classical Task 3: gradCPT Stimulus Classification (Mountain vs City)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`, `S245`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `S155` | 0 | Standard stimulus (mountain scene, withhold response) |
  | `S245` | 1 | Target stimulus (city scene, press button) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Uses gradCPT paradigm with mountain (S155) as frequent standard and city (S245) as rare target stimuli.
- **Kernel Notes**: Basic stimulus-locked epoching for S155 vs S245 classification. S155 is more frequent (201922 vs 201110 events). Downsample from 5000 Hz before processing.

### Potential Task 1: gradCPT Sustained Attention Timecourse Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -30.0 s, tmax = 30.0 s, segment_length = 60.0 s, target_events = [`S155`, `S245`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `in_zone` | 0 | Sustained attention maintained (low RT variability over segment) |
  | `out_zone` | 1 | Attention lapses (high RT variability over segment) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Supports sustained attention analysis using rolling variability metrics across consecutive correct trials.
- **Kernel Notes**: Use longer segments (60s) to capture attentional fluctuations over time. Compute rolling RT variability across correct trials within segment window. Requires RT extraction from S254 timing relative to preceding stimulus. Downsample from 5000 Hz before processing.

### Potential Task 2: gradCPT Reaction Time Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S245`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `S245` + S254 | RT in ms | Reaction time for correct target responses |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — GradCPT measures sustained attention via RT variability; RT extraction from S254 events is documented.
- **Kernel Notes**: Only for target trials (S245) where S254 occurred within window. Extract RT = time(S254) - time(S245). Exclude omission errors (S245 without S254). Downsample from 5000 Hz before processing.

### Normal Task 1: gradCPT Commission Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S155`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `S155` + no S254 | 0 | Correct withhold (standard trial, no response) |
  | `S155` + S254 | 1 | Commission error (responded to non-target) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Commission error framework described: responding to standard stimuli (S155) as if they were targets.
- **Kernel Notes**: Focus specifically on S155 (standard) trials to detect commission errors. Check for S254 presence within 2s window. Downsample from 5000 Hz before processing.

### Normal Task 2: gradCPT Omission Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`S245`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `S245` + S254 | 0 | Correct detection (target trial, responded) |
  | `S245` + no S254 | 1 | Omission error (failed to detect target) |
- **Evidence**:
  - DOI: 10.1038/s41597-026-06616-6 — Omission error framework described: failure to respond to target stimuli (S245).
- **Kernel Notes**: Focus specifically on S245 (target) trials to detect omission errors. Check for S254 absence within 2s window. Downsample from 5000 Hz before processing.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
