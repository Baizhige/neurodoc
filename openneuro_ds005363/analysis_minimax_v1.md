# Object Recognition in Healthy Aging (ORHA) - EEG

**Dataset**: `openneuro_ds005363` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005363
**Category**: Sensory/Response | **Subjects**: 43 | **Files (Completed)**: 43 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed images across five visual categories (faces, animals, places, objects, and likely one additional) to investigate visual object representations and how they change with healthy aging. S65-S69 encode the five stimulus categories; S99 is a high-frequency event likely marking fixations or trial separators. The study uses representational similarity analysis to track age-related changes in neural object coding.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005363

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 99` | 21460 | short | raw | Fixation/trial separator (high-frequency onset) |
| `Stimulus/S 66` | 4508 | short | raw | Visual category 2 |
| `Stimulus/S 67` | 4463 | short | raw | Visual category 3 |
| `Stimulus/S 65` | 4421 | short | raw | Visual category 1 |
| `Stimulus/S 69` | 4351 | short | raw | Visual category 5 |
| `Stimulus/S 68` | 4285 | short | raw | Visual category 4 |
| `Stimulus/S 4`-`Stimulus/S 57` | ~1377 each | short | raw | Individual exemplar image onsets (60+ items) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 99`, `Stimulus/S 66`, `Stimulus/S 67`, `Stimulus/S 65`, `Stimulus/S 69`, `Stimulus/S 68`, `Stimulus/S 4`, `Stimulus/S 57`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Animate vs Inanimate Visual Object Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.75 s, target_events = [`animate (faces and animals)`, `inanimate (places and objects)`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 65`, `Stimulus/S 66` (faces, animals) | 0 | Animate objects |
  | `Stimulus/S 67`, `Stimulus/S 68`, `Stimulus/S 69` (places, objects) | 1 | Inanimate objects |
- **Evidence**:
  - DOI: 10.1162/imag.a.1033 — Uses openneuro_ds005363 dataset as control to validate generalizability, performing 2-class decoding of EEG responses to animate vs inanimate images with 43 participants and ~88112 trials.
- **Kernel Notes**: Map S65-S66 to animate class (faces, animals) and S67-S69 to inanimate class (places, objects). Use binary cross-entropy loss for training.

### Normal Task 1: Visual Category Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: S99 (21,460 total) is a high-frequency fixation/separator marker - exclude. S4-S57 encode individual exemplar images (60+ codes, ~1377 each); use for RSA analysis.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Stimulus/S 65` | 0 | Visual category 1 |
 | `Stimulus/S 66` | 1 | Visual category 2 |
 | `Stimulus/S 67` | 2 | Visual category 3 |
 | `Stimulus/S 68` | 3 | Visual category 4 |
 | `Stimulus/S 69` | 4 | Visual category 5 |

## Data Quality Notes

- S99 is a very high-frequency marker (21,460 total) - likely fixation onset, exclude from category decoding.
- 60+ exemplar codes (~1377 each) suitable for RSA.

## References

- **Reference**: `Healthy aging delays and dedifferentiates high-level visual representations`
