# EEG during Near-Threshold Visual Detection Tasks (No-Cue, 50%-Cue, 100%-Cue)

**Dataset**: `openneuro_ds006171` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006171
**Category**: Sensory/Response | **Subjects**: 26 | **Files (Completed)**: 104 | **Channels**: 144 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed near-threshold visual detection tasks across three cueing conditions: no-cue (0% validity), noninformative cue (50% validity), and informative cue (100% validity). The study examines how spatial attention modulates near-threshold detection performance and associated EEG signatures. Stimuli were brief visual Gabor patches presented at or near detection threshold, and participants reported detection via button press. Behavioral columns (gabor_contrast, subjective_r, objective_r, response_time) stored in events.tsv enable regression analyses.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `128` | 69653 | admin | raw | BioSemi status boundary marker |
| `125` | 23250 | short | raw | 100% validity cue - correct rejection (100pct_CR) |
| `124` | 18239 | short | raw | 100% validity cue - false alarm (100pct_FA) |
| `2` | 13793 | short | raw | Response (detection report) |
| `1` | 13790 | short | raw | Trial start |
| `22` | 6299 | short | raw | 50%-validity cue condition, stimulus B |
| `21` | 6299 | short | raw | 50%-validity cue condition, stimulus A |
| `11` | 6297 | short | raw | No-cue condition, stimulus A |
| `12` | 6295 | short | raw | No-cue condition, stimulus B |
| `122` | 2753 | short | raw | 50% validity cue - miss (50pct_miss) |
| `121` | 2650 | short | raw | 50% validity cue - hit (50pct_hit) |
| `103` | 1530 | short | raw | No-cue - false alarm (nocue_FA) |
| `101` | 1530 | short | raw | No-cue - hit (nocue_hit) |
| `111` | 1529 | short | raw | 50% validity cue - hit (50pct_hit) |
| `104` | 1529 | short | raw | No-cue - correct rejection (nocue_CR) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

[Placeholder: File scan details not provided]

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Near threshold visual detection task
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006171 DOI: https://doi.org/10.18112/openneuro.ds006171.v1.0.0


### Normal Task 1: Near-Threshold Detection Outcome (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Specific kernel maps numeric BioSemi codes to semantic labels. `regression_target`: response_time. `continuous_cols`: response_time, gabor_contrast, subjective_r, objective_r. Code `128` is a BioSemi boundary marker (admin; exclude). Key contrast: hit vs miss across cueing conditions.

 | Event | y | Meaning |
 |-------|---|---------|
 | `catch_trial` | 0 | Catch trial (no stimulus) |
 | `catch_response` | 1 | Response during catch trial |
 | `nocue_hit` | 2 | No-cue condition - hit |
 | `nocue_miss` | 3 | No-cue condition - miss |
 | `nocue_FA` | 4 | No-cue condition - false alarm |
 | `nocue_CR` | 5 | No-cue condition - correct rejection |
 | `50pct_hit` | 6 | 50%-validity cue - hit |
 | `50pct_miss` | 7 | 50%-validity cue - miss |
 | `50pct_FA` | 8 | 50%-validity cue - false alarm |
 | `50pct_CR` | 9 | 50%-validity cue - correct rejection |
 | `100pct_hit` | 10 | 100%-validity cue - hit |
 | `100pct_miss` | 11 | 100%-validity cue - miss |
 | `100pct_FA` | 12 | 100%-validity cue - false alarm |
 | `100pct_CR` | 13 | 100%-validity cue - correct rejection |

## Data Quality Notes

- BioSemi 128/256-channel system; code `128` is a hardware boundary marker, not a stimulus.
- Continuous behavioral columns (gabor_contrast, subjective_r, objective_r, response_time) available for regression.
- Apply bandpass filter (0.1-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006171