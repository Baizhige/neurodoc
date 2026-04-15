# Braille Letters EEG

**Dataset**: `openneuro_ds004951` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004951
**Category**: Sensory/Response | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants identified Braille letters presented via tactile stimulation to left or right index fingers while EEG was recorded. The study investigates cortical plasticity by comparing sighted controls and congenitally blind individuals in processing Braille letter information. Stimulus codes S10-S16 mark individual Braille letter presentations (~3298-3301 each).

## File Scan Result

> **Kernel SHA256**: `bca6bdbc5406855bc363bfa0909ecc190a21615b1a5142b0968e57e49e915b61`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 10` | 3299 | event | raw | Braille letter 10 onset |
| `Stimulus/S 11` | 3300 | event | raw | Braille letter 11 onset |
| `Stimulus/S 12` | 3298 | event | raw | Braille letter 12 onset |
| `Stimulus/S 13` | 3298 | event | raw | Braille letter 13 onset |
| `Stimulus/S 14` | 3299 | event | raw | Braille letter 14 onset |
| `Stimulus/S 15` | 3301 | event | raw | Braille letter 15 onset |
| `Stimulus/S 16` | 3301 | event | raw | Braille letter 16 onset |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `HEOG`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Braille Letter Identity Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, baseline = (-0.2, 0.0) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 1` | 0 | Braille letter B |
  | `Stimulus/S 2` | 1 | Braille letter C |
  | `Stimulus/S 3` | 2 | Braille letter D |
  | `Stimulus/S 4` | 3 | Braille letter L |
  | `Stimulus/S 5` | 4 | Braille letter M |
  | `Stimulus/S 6` | 5 | Braille letter N |
  | `Stimulus/S 7` | 6 | Braille letter V |
  | `Stimulus/S 8` | 7 | Braille letter Z |
- **Evidence**:
  - DOI: 10.7554/eLife.98148 — EEG classification of 8 Braille letters (B, C, D, L, M, N, V, Z) from blind participants using SVM with epochs -100ms to 999ms relative to stimulus onset. Multivariate classification decoding Braille letter identity from EEG patterns. Within-hand vs cross-hand transfer learning to distinguish sensory vs perceptual representations.
- **Kernel Notes**: Braille letters E and O are vigilance targets (catch trials) - exclude from classification. S101/S222 events (~63k each) are response feedback markers - exclude. S200 block marker (~10k) - exclude. S253/S255 admin markers - exclude. Label mapping assumes S1-S8 correspond to B, C, D, L, M, N, V, Z per publication methodology - verify from dataset documentation. Sampling rate: 1000Hz. Baseline window: -200ms to 0ms for correction.

### Potential Task 1: Braille Letter Identification (16-class extended)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, baseline = (-0.2, 0.0) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 1` | 0 | Braille letter 1 |
  | `Stimulus/S 2` | 1 | Braille letter 2 |
  | `Stimulus/S 3` | 2 | Braille letter 3 |
  | `Stimulus/S 4` | 3 | Braille letter 4 |
  | `Stimulus/S 5` | 4 | Braille letter 5 |
  | `Stimulus/S 6` | 5 | Braille letter 6 |
  | `Stimulus/S 7` | 6 | Braille letter 7 |
  | `Stimulus/S 8` | 7 | Braille letter 8 |
  | `Stimulus/S 9` | 8 | Braille letter 9 |
  | `Stimulus/S 10` | 9 | Braille letter 10 |
  | `Stimulus/S 11` | 10 | Braille letter 11 |
  | `Stimulus/S 12` | 11 | Braille letter 12 |
  | `Stimulus/S 13` | 12 | Braille letter 13 |
  | `Stimulus/S 14` | 13 | Braille letter 14 |
  | `Stimulus/S 15` | 14 | Braille letter 15 |
  | `Stimulus/S 16` | 15 | Braille letter 16 |
- **Evidence**: N/A - plausible from paradigm alone
- **Kernel Notes**: Full 16-class Braille letter classification using all S1-S16 events (~3300 each). Includes catch trials E and O unlike Classical Task 1. Exclude admin markers (S253, S255, New Segment/), S101/S222 feedback markers, and S200 block boundaries. Verify S9 triggers present in raw data (not confirmed in available events list).

### Potential Task 2: Braille Late Cognitive Processing Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.3 s, tmax = 1.0 s, baseline = (0.3, 0.5) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 1` | 0 | Braille letter B |
  | `Stimulus/S 2` | 1 | Braille letter C |
  | `Stimulus/S 3` | 2 | Braille letter D |
  | `Stimulus/S 4` | 3 | Braille letter L |
  | `Stimulus/S 5` | 4 | Braille letter M |
  | `Stimulus/S 6` | 5 | Braille letter N |
  | `Stimulus/S 7` | 6 | Braille letter V |
  | `Stimulus/S 8` | 7 | Braille letter Z |
- **Evidence**: N/A - plausible from paradigm and alignment recommendations
- **Kernel Notes**: Alternative epoch window focusing on late cognitive processing (300-1000ms) capturing decision/response-related components. Excludes early somatosensory evoked potentials for cleaner classification of higher-order perceptual representations. Based on alignment recommendations for Braille_Late_Response paradigm.