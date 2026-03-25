# Poetry Assessment EEG Dataset 1

**Dataset**: `openneuro_ds006648` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006648
**Category**: High-level Mental | **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 70 | **Sampling Rate**: 512 Hz

## Paradigm

Participants read and evaluated 210 short English-language texts including Haikus and Senryus on five subjective dimensions related to aesthetic and creative cognition: Aesthetic Appeal, Vivid Imagery, Being Moved, Originality, and Creativity. EEG was recorded during reading using a 64-channel BioSemi system (70 channels total including references). This is the first of two poetry datasets (companion to ds006647) with full N=47 subject coverage.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006648

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65284` | 9993 | short | raw | BioSemi trigger - stimulus/condition D onset |
| `65281` | 9964 | short | raw | BioSemi trigger - stimulus/condition A onset |
| `65282` | 9964 | short | raw | BioSemi trigger - stimulus/condition B onset |
| `65283` | 9964 | short | raw | BioSemi trigger - stimulus/condition C onset |
| `65286` | 47 | short | raw | BioSemi trigger - stimulus/condition F onset |
| `65287` | 47 | short | raw | BioSemi trigger - stimulus/condition G onset |
| `65288` | 47 | short | raw | BioSemi trigger - stimulus/condition H onset |
| `65285` | 46 | short | raw | BioSemi trigger - stimulus/condition E onset |
| `65280` | 18 | short | raw | BioSemi trigger - rare/practice condition |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Readpoetry
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006648 DOI: https://doi.org/10.18112/openneuro.ds006648.v1.0.0


### Normal Task 1: Poetry Aesthetic Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: BioSemi EDF trigger codes 65280-65288; decode from events.tsv for exact poetry/non-poetry mapping. Codes 65281-65284 are highly frequent (~9964-9993 each); codes 65285-65288 appear rarely (~46-47 total). Code 65280 appears in only 18 files.

 | Event | y | Meaning |
 |-------|---|---------|
 | `65284` | 0 | BioSemi condition code 65284 |
 | `65281` | 1 | BioSemi condition code 65281 |
 | `65282` | 2 | BioSemi condition code 65282 |
 | `65283` | 3 | BioSemi condition code 65283 |
 | `65286` | 4 | BioSemi condition code 65286 |
 | `65287` | 5 | BioSemi condition code 65287 |
 | `65288` | 6 | BioSemi condition code 65288 |
 | `65285` | 7 | BioSemi condition code 65285 |
 | `65280` | 8 | BioSemi condition code 65280 |
## Data Quality Notes

- Codes 65285-65288 and 65280 are rare events; consider excluding from classification due to imbalance.
- BioSemi trigger codes need decoding from events.tsv to determine poetry/non-poetry mapping.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `Poetry Assessment EEG Dataset 1`
