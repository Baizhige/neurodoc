# Sustained Attention Task (gradCPT) Dataset using simultaneous EEG-fMRI and DTI

**Dataset**: `openneuro_ds006040` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006040
**Category**: High-level Mental | **Subjects**: 28 | **Files (Completed)**: 1064 | **Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

The dataset uses the Gradual Continuous Performance Task (gradCPT) to measure sustained attention via simultaneous EEG and fMRI recording. Participants detect rare city scenes (targets, S245) within a stream of common mountain scenes (standards, S155). Additional tasks include resting state, visual checkerboard stimulation, and mental imagery. MRI synchronization pulses (TR, Sync On) and cardiac (qrs) signals are also recorded.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006040

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S155` | 201922 | short | raw | Standard stimulus (mountain scene, frequent) |
| `S245` | 201110 | short | raw | Target stimulus (city scene, rare) |
| `Sync On` | 195242 | admin | raw | MRI sync pulse onset |
| `qrs` | 170358 | admin | raw | Cardiac QRS complex |
| `TR` | 106494 | admin | raw | MRI TR repetition marker |
| `T 1` | 52960 | admin | raw | Timing marker |
| `S254` | 813 | short | raw | Response / button press |
| `[]` | 15 | admin | raw | Empty/null event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S155`, `S245`, `S254`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: gradCPT Correct vs Incorrect Trial Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.5 s *, target_events = [`S155`, `S245`, `S254`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `correct_trial` | 0 | Correct response: correct commission (S245+press) or correct omission (S155+no press) |
  | `incorrect_trial` | 1 | Error: commission error (S155+press) or omission error (S245+no press) |
- **Super Meta Notes**: Labels derived by combining stimulus events (S155/S245) with response events (S254). A trial is 'correct' if participant correctly withheld for S155 (no press) or correctly responded to S245 (press). A trial is 'incorrect' if participant erroneously pressed for S155 (commission) or failed to press for S245 (omission).
- **Evidence**:
  - DOI: 10.1038/s41597.026.06616-6 — Classifies correct vs incorrect trials (attention lapses) based on pre-target brain activity in DMN, visual, and dorsal attention networks.
- **Kernel Notes**: Kernel must join stimulus events (S155/S245) with response events (S254) within a trial window to determine correctness. Use reaction time from S254 to validate response timing.

### Primary Task 2: gradCPT Attention State Classification (In-the-Zone vs Out-of-the-Zone)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.5 s *, target_events = [`S155`, `S245`, `S254`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `in_the_zone` | 0 | Stable attention state: low RT variability across recent correct trials |
  | `out_of_the_zone` | 1 | Lapsing attention: high RT variability across recent correct trials |
- **Super Meta Notes**: Attention state derived from reaction time (RT) variability during correct trials. 'In-the-zone' = low RT variability (consistent performance); 'Out-of-the-zone' = high RT variability (attentional lapses).
- **Evidence**:
  - DOI: 10.1038/s41597.026.06616-6 — Classifies in-the-zone vs out-of-the-zone attentional states based on RT variability during sustained attention.
- **Kernel Notes**: Kernel must compute rolling RT statistics from S254 events during correct trials. Threshold for 'zone' classification should be derived from median RT variability within each session/block.

### Normal Task 1: gradCPT Sustained Attention (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Primary scientific contrast is S155 (standard) vs S245 (target) for gradCPT attention decoding. `Sync On`, `TR`, `qrs` are MRI/cardiac markers. Very high sampling rate (5000 Hz); downsample before processing.

 | Event | y | Meaning |
 |-------|---|-|
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

## References

- **Reference**: `Sustained Attention Task (gradCPT) Dataset using simultaneous EEG-fMRI and DTI`
