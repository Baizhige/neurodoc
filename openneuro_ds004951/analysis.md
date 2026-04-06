# Braille Letters EEG

**Dataset**: `openneuro_ds004951` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004951
**Category**: Sensory/Response | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants identified Braille letters presented via tactile stimulation to left or right index fingers while EEG was recorded. The study investigates cortical plasticity by comparing sighted controls and congenitally blind individuals in processing Braille letter information. Stimulus codes S1-S16 mark individual Braille letter presentations (3,316-3,319 each); S101 and S222 (63,609/63,607) dominate and likely mark response-correct/response-incorrect feedback or block boundaries; S200 (10,535) is a block marker; S253 (9,211) and S254/S255 are admin/system markers.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S101` | 63609 | event | raw | Response feedback / block marker A |
| `Stimulus/S222` | 63607 | event | raw | Response feedback / block marker B |
| `Stimulus/S200` | 10535 | event | raw | Block boundary / condition marker |
| `Stimulus/S253` | 9211 | admin | raw | Admin / response marker (exclude) |
| `Stimulus/S 16` | 3319 | event | raw | Braille letter 16 onset |
| `Stimulus/S 6` | 3319 | event | raw | Braille letter 6 onset |
| `Stimulus/S 15` | 3319 | event | raw | Braille letter 15 onset |
| `Stimulus/S 11` | 3318 | event | raw | Braille letter 11 onset |
| `Stimulus/S 3` | 3318 | event | raw | Braille letter 3 onset |
| `Stimulus/S 10` | 3317 | event | raw | Braille letter 10 onset |
| `Stimulus/S 1`-`S 16` | ~3316-3319 each | event | raw | Individual Braille letter onsets (16 letters) |
| `Stimulus/S255` | ~437 | admin | raw | BrainVision admin sync marker (exclude) |
| `New Segment/` | rare | admin | raw | BrainVision segment boundary (exclude) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S101`, `Stimulus/S222`, `Stimulus/S200`, `Stimulus/S253`, `Stimulus/S 16`, `Stimulus/S 6`, `Stimulus/S 15`, `Stimulus/S 11`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Braille Letter Identity Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.999 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 1` * | 0 | Braille letter B (verify mapping) |
  | `Stimulus/S 2` * | 1 | Braille letter C (verify mapping) |
  | `Stimulus/S 3` * | 2 | Braille letter D (verify mapping) |
  | `Stimulus/S 4` * | 3 | Braille letter L (verify mapping) |
  | `Stimulus/S 5` * | 4 | Braille letter M (verify mapping) |
  | `Stimulus/S 6` * | 5 | Braille letter N (verify mapping) |
  | `Stimulus/S 7` * | 6 | Braille letter V (verify mapping) |
  | `Stimulus/S 8` * | 7 | Braille letter Z (verify mapping) |
- **Super Meta Notes**: N/A - using raw event IDs directly
- **Evidence**:
  - DOI: 10.7554/eLife.98148 — EEG classification of 8 Braille letters (B, C, D, L, M, N, V, Z) from blind participants using SVM with epochs -100ms to 999ms relative to stimulus onset
  - DOI: 10.7554/eLife.98148.2 — Multivariate classification decoding Braille letter identity from EEG patterns
  - DOI: 10.7554/eLife.98148 — Time-resolved SVM pairwise classification of Braille letter identity
- **Kernel Notes**: Mapping between paper letter labels (B, C, D, L, M, N, V, Z) and raw event IDs (S1-S16) must be verified from dataset documentation; current mapping assumes S1-S8 correspond to the 8 letters but this requires confirmation. Baseline correction: -100ms to 0ms. Sampling rate: 1000Hz. Exclude catch trials (E, O) if present in data.

### Potential Task 1: Braille Letter Identification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `New Segment/`, `Stimulus/S253`, `Stimulus/S254`, `Stimulus/S255` are admin - exclude. S101/S222 (63k each) are very high-frequency feedback/block markers - exclude from classification. S200 is a block boundary - exclude.

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

## Data Quality Notes

- `Stimulus/S101` and `Stimulus/S222` are very high-frequency (63k each) - likely feedback or block markers, exclude from classification.
- `New Segment/`, `Stimulus/S253`, `Stimulus/S254`, `Stimulus/S255` are admin/system - exclude.
- Dataset includes sighted controls and congenitally blind participants; group label in participants.tsv.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review