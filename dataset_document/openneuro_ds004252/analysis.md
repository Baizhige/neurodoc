# Rotation-tolerant representations elucidate the time course of high-level object processing

**Dataset**: `openneuro_ds004252` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004252
**Category**: Sensory/Response | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 127 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

A single participant viewed visual stimuli of objects at various rotations to investigate the neural time course of rotation-tolerant, high-level object representations. A rapid serial visual presentation (RSVP) design was used with three event types encoding distinct stimulus categories or conditions. The study is a single-subject pilot or proof-of-concept recording.

## File Scan Result

> **Kernel SHA256**: `c0200cb48ca31e874959b55a50d30557995155cbe2781ec4aadc544a9d340928`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E  1` | 14400 | event | raw | Stimulus condition 1 (object/rotation category A) |
| `Event/E  2` | 14400 | event | raw | Stimulus condition 2 (object/rotation category B) |
| `Event/E  3` | 120 | event | raw | Stimulus condition 3 (object/rotation category C) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 60-way object category classification (rotation-tolerant decoding)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0–59 | Object/rotation condition 1 subset (12 categories × 5 exemplars × 8 rotations) |
  | `Event/E  2` | 0–59 | Object/rotation condition 2 subset |
  | `Event/E  3` | 0–59 | Object/rotation condition 3 subset |
- **Evidence**: DOI: 10.31234/osf.io/wp73u — "This study used EEG data from OpenNeuro ds004252 to decode 60-way object classification using multivariate pattern analysis, comparing fixed-rotation decoding with rotation-tolerant decoding, with epochs from -100ms to 800ms relative to stimulus onset."
- **Kernel Notes**: Raw events E1-E3 group stimuli into 3 coarse conditions; however, the paper supports 60-way classification (12 categories × 5 exemplars across 8 rotations). Verify if finer-grained 60-way labels can be reconstructed from stimulus metadata files. If not, fall back to 3-class coarse mapping. Severe class imbalance present (E1/E2: 14400 trials each vs. E3: 120 trials) may require subsampling or class weighting. Single-subject design limits cross-subject generalization.

---

### Potential Task 1: 3-way coarse object category classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0 | Object/rotation condition 1 (coarse category group) |
  | `Event/E  2` | 1 | Object/rotation condition 2 (coarse category group) |
  | `Event/E  3` | 2 | Object/rotation condition 3 (coarse category group) |
- **Evidence**: No direct classification-relevant reference; plausible from paradigm alone (RSVP object recognition with 3 stimulus conditions). Extended epoch window (-200ms to 1000ms) captures N100 and N400 components.
- **Kernel Notes**: Fallback task if 60-way finer labels cannot be reconstructed from metadata. Warning: severe class imbalance (14400:14400:120 ratio) requires subsampling or class weighting. Single-subject design; extended window may improve signal-to-noise for coarse classification.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
