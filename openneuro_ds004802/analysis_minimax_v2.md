# Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot)

**Dataset**: `openneuro_ds004802` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004802
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 79
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

A pilot EEG study investigating the neural underpinnings of loneliness by contrasting social hypersensitivity (amplified neural responses to social stimuli) and hyperalertness (heightened attention to potential social threats). Participants viewed social and non-social stimuli while EEG was recorded. Trigger codes encode stimulus type, valence, and response conditions. Code 20 dominates the event structure (49,726 total) and may represent a high-frequency refresh or fixation signal.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004802

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `20` | 49726 | short | raw | Dominant trigger (likely fixation/refresh signal) |
| `111` | 4144 | short | raw | Trigger code 111 |
| `25` | 2823 | short | raw | Trigger code 25 |
| `24` | 2817 | short | raw | Trigger code 24 |
| `21` | 2747 | short | raw | Trigger code 21 |
| `23` | 2667 | short | raw | Trigger code 23 |
| `22` | 2666 | short | raw | Trigger code 22 |
| `42` | 2319 | short | raw | Trigger code 42 |
| `44` | 2316 | short | raw | Trigger code 44 |
| `43` | 2246 | short | raw | Trigger code 43 |
| `61` | 2221 | short | raw | Trigger code 61 |
| `62` | 2185 | short | raw | Trigger code 62 |
| `65` | 2182 | short | raw | Trigger code 65 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [Needs verification - see Kernel Notes]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | (unconfirmed) | 0 | Target stimulus * |
  | (unconfirmed) | 1 | Non-target stimulus * |
- **Kernel Notes**: Verify event ID mapping from events.tsv. This dataset uses codes for stimulus type, valence, and response conditions; confirm which codes correspond to target vs non-target for P300/oddball paradigm. Code 20 (n=49,726) appears to be fixation/refresh, not stimulus-related.
- **Evidence**: DOI: https://doi.org/10.18112/openneuro.ds004802.v1.0.0 — "Loneliness in the Brain" pilot EEG study; paradigm involves social vs non-social stimuli, but exact target/non-target split not explicitly described in metadata.

### Normal Task 1: Stimulus classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30+ distinct trigger codes; full decode from events.tsv required. Code 20 dominates (49,726 total) - likely a fixation/refresh signal rather than stimulus.

| Event | y | Meaning |
|-------|---|------|
| `20` | 0 | Primary stimulus trigger |
| `111` | 1 | Trigger code 111 |
| `25` | 2 | Trigger code 25 |
| `24` | 3 | Trigger code 24 |
| `21` | 4 | Trigger code 21 |
| `23` | 5 | Trigger code 23 |
| `22` | 6 | Trigger code 22 |
| `42` | 7 | Trigger code 42 |
| `44` | 8 | Trigger code 44 |
| `43` | 9 | Trigger code 43 |
| `61` | 10 | Trigger code 61 |
| `62` | 11 | Trigger code 62 |
| `65` | 12 | Trigger code 65 |


## Data Quality Notes

- 30+ distinct trigger codes - check events.tsv decode table.
- Code 20 (49,726 total) is anomalously high - may be a fixation/refresh signal rather than stimulus.

## References

- **Reference**: `Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness`
