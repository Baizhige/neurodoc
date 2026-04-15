# Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset

**Dataset**: `openneuro_ds005345` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005345
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 28
**Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants engaged in naturalistic listening to excerpts of "Le Petit Prince" (The Little Prince) under single-talker and multi-talker conditions during simultaneous EEG and 7T fMRI recording. The study investigates neural processing of speech under cocktail-party-style listening conditions. Stimulus/S 11 marks single-talker condition onsets; Stimulus/S 31-S 34 mark multi-talker condition variants. `Comment/actiCAP Data On` is an EEG system administrative marker.

## File Scan Result

> **Kernel SHA256**: `cab1c04904220ae097f0e808a7ac608706ade302bb00249698a7a5dd78475d72`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/actiCAP Data On` | 26 | admin | raw | EEG recording system start marker |
| `Stimulus/S 11` | 20 | event | raw | Single-talker listening block onset |
| `Stimulus/S 31` | 6 | event | raw | Multi-talker condition variant 31 onset |
| `Stimulus/S 32` | 6 | event | raw | Multi-talker condition variant 32 onset |
| `Stimulus/S 33` | 6 | event | raw | Multi-talker condition variant 33 onset |
| `Stimulus/S 34` | 6 | event | raw | Multi-talker condition variant 34 onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Listening Condition Classification (Multitalker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 600 s, overlap = 0.0, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Single-talker listening |
  | `Stimulus/S 31` | 1 | Multi-talker mix_f attended |
  | `Stimulus/S 32` | 2 | Multi-talker mix_m attended |
  | `Stimulus/S 33` | 3 | Multi-talker mix_f unattended |
  | `Stimulus/S 34` | 4 | Multi-talker mix_m unattended |
- **Evidence**:
  - DOI: 10.1101/2025.04.03.646958 — Validates LPP Multi-talkker Dataset with 64-channel EEG from 25 participants listening to single-talker and multi-talker conditions (Stimulus/S 11, S31-S34), epochs segmented from -500ms to 10 minutes after section onset
  - DOI: 10.1038/s41597-025-05158-7 — Describes LPP Multi-talker Dataset (OpenNeuro ds005345) with EEG from 26 participants during naturalistic listening, validated via ISC analysis showing neural differentiation between conditions
- **Kernel Notes**: Verify event ID mapping from events.tsv. Overlap=0.0 for contiguous block analysis. Exclude `Comment/actiCAP Data On` admin marker. Verify tmax alignment with actual block durations if shorter than 600s.

### Potential Task 1: Word-Level ERP Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.5 s, target_events = [verify word-onset markers required]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Single-talker word epoch |
  | `Stimulus/S 31` | 1 | Multi-talker condition 31 word epoch |
  | `Stimulus/S 32` | 2 | Multi-talker condition 32 word epoch |
  | `Stimulus/S 33` | 3 | Multi-talker condition 33 word epoch |
  | `Stimulus/S 34` | 4 | Multi-talker condition 34 word epoch |
- **Evidence**:
  - DOI: 10.1101/2025.04.03.646958 — Mentions word-level epochs extracted from -100ms to 500ms after word offset
- **Kernel Notes**: Requires word-level event markers in events.tsv. Currently only block-level markers (Stimulus/S 11, S31-S34) are available. Check for companion events file with word-onset markers; if absent, this task cannot be executed. Consider verifying with dataset BIDS structure before implementation.