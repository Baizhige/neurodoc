# Poetry EEG Study

**Dataset**: `openneuro_ds006647` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006647
**Category**: High-level Mental | **Subjects**: 51 | **Files (Completed)**: 4 | **Channels**: 70 | **Sampling Rate**: 512 Hz

## Paradigm

Participants read and evaluated 210 short poetic (Haiku, Senryu) and non-poetic control texts on five subjective dimensions: Aesthetic Appeal, Vivid Imagery, Being Moved, Originality, and Creativity. EEG was recorded during reading using a 64-channel BioSemi system. The study investigates neural correlates of aesthetic and creative cognition during poetry processing. BioSemi EDF trigger codes (65280-65288) encode stimulus onset and condition types.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65284` | 852 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65281` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65282` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65283` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65280` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65285` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65286` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65287` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `65288` | 848 | short | raw | BioSemi trigger - stimulus/condition onset |
| `boundary` | 5 | admin | raw | Segment boundary marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

Placeholder for additional file scan metadata as needed.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Readpoetry
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006647 DOI: https://doi.org/10.18112/openneuro.ds006647.v1.0.1


### Normal Task 1: Poetry Condition Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: BioSemi trigger codes 65280-65288; decode from events.tsv to determine poetry vs. control mapping. `boundary` is an admin segment marker (exclude). Only 4 files present despite 51 subjects reported - dataset may be a subset or pilot.

 | Event | y | Meaning |
 |-------|---|---------|
 | `65284` | 0 | BioSemi condition code 65284 |
 | `65281` | 1 | BioSemi condition code 65281 |
 | `65282` | 2 | BioSemi condition code 65282 |
 | `65283` | 3 | BioSemi condition code 65283 |
 | `65280` | 4 | BioSemi condition code 65280 |
 | `65285` | 5 | BioSemi condition code 65285 |
 | `65286` | 6 | BioSemi condition code 65286 |
 | `65287` | 7 | BioSemi condition code 65287 |
 | `65288` | 8 | BioSemi condition code 65288 |
## Data Quality Notes

- Only 4 completed files despite 51 subjects reported; this appears to be a partial dataset.
- `boundary` is a segment boundary marker and must be excluded from analysis.
- BioSemi EDF trigger codes 65280-65288 need decoding from events.tsv.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006647