# A multi-subject and multi-session EEG dataset for modelling human visual object recognition

**Dataset**: `openneuro_ds005589` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005589
**Category**: Sensory/Response | **Subjects**: 32 | **Files (Completed)**: 1592 | **Channels**: 133 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants underwent Rapid Serial Visual Presentation (RSVP) at 5 Hz and a low-speed visual presentation task to record brain responses to visual object recognition across multiple image categories. Codes 1-20 correspond to object categories in the low-speed task; codes 21-27 to RSVP categories; code 99 is catch trials; codes 252/254 are feedback. Multiple sessions were recorded per subject.

## File Scan Result

> **Kernel SHA256**: `3b862d82c5ab1d387cde8c3a7ca69199072c3173f11f49286045281157f4c51c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 20-Category Visual Object Recognition Decoding (Low-Speed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.5 s, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `99`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Object category 1 |
  | `2` | 1 | Object category 2 |
  | `3` | 2 | Object category 3 |
  | `4` | 3 | Object category 4 |
  | `5` | 4 | Object category 5 |
  | `6` | 5 | Object category 6 |
  | `7` | 6 | Object category 7 |
  | `8` | 7 | Object category 8 |
  | `9` | 8 | Object category 9 |
  | `10` | 9 | Object category 10 |
  | `11` | 10 | Object category 11 |
  | `12` | 11 | Object category 12 |
  | `13` | 12 | Object category 13 |
  | `14` | 13 | Object category 14 |
  | `15` | 14 | Object category 15 |
  | `16` | 15 | Object category 16 |
  | `17` | 16 | Object category 17 |
  | `18` | 17 | Object category 18 |
  | `19` | 18 | Object category 19 |
  | `20` | 19 | Object category 20 |
  | `99` | 20 | Catch trial (special stimulus) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04843-x — This paper presents the MSS dataset with ~800,000 RSVP trials and ~40,000 low-speed trials for 20-category visual object recognition, validating EEG classification using epochs of 0–500ms post-stimulus with a fully connected neural network achieving above-chance decoding across all 20 categories.
- **Kernel Notes**: Use 500ms epochs from stimulus onset (tmin=0.0s, tmax=0.5s) aligned to event onset. Map event IDs 1–20 to labels 0–19 for 20-category classification. Event ID 99 (catch trials) serves as a 21st class (label 20). Exclude feedback codes 252/254 from stimulus-response epochs to prevent contamination. Apply bandpass filter (1–40 Hz) and baseline correction using pre-stimulus window (e.g., -0.1 to 0 s) if tmin is adjusted. Per-session z-score normalization recommended given the multi-session structure (32 subjects × 1592 files).

### Potential Task 1: RSVP 7-Category Visual Object Recognition Decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.2 s, target_events = [`21`, `22`, `23`, `24`, `25`, `26`, `27`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `21` | 0 | RSVP category 21 |
  | `22` | 1 | RSVP category 22 |
  | `23` | 2 | RSVP category 23 |
  | `24` | 3 | RSVP category 24 |
  | `25` | 4 | RSVP category 25 |
  | `26` | 5 | RSVP category 26 |
  | `27` | 6 | RSVP category 27 |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04843-x — The paradigm description confirms RSVP at 5 Hz with object category codes 21–27, providing the basis for rapid visual object recognition decoding. The dataset contains ~798 trials per RSVP category.
- **Kernel Notes**: Hard-cap epochs at 200ms to avoid bleed from the next RSVP stimulus (5 Hz = 200ms interval). Omit pre-stimulus baseline since the prior stimulus occupies that window; if baseline correction is needed, use a within-epoch window (first 10–20ms). Exclude feedback events (252/254) and catch trials (99) from RSVP classification epochs. Map event IDs 21–27 to labels 0–6 for 7-category classification.
