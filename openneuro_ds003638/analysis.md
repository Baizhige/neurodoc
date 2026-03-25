# EEG: Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms

**Dataset**: `openneuro_ds003638` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003638
**Category**: High-level Mental | **Subjects**: 57 | **Files (Completed)**: 57
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

This study employs three cross-species behavioral paradigms (5-Choice Continuous Performance Task [5CCPT], Probabilistic Reward/Punishment task [PRBP], and Pavlovian-to-Instrumental Transfer [PST]) to identify electrophysiological biomarkers associated with various behavioral dimensions including attention, impulsivity, and reward sensitivity. All 57 subjects completed all three paradigms in a single session. Event markers are encoded as numeric codes with paradigm suffix (e.g., "N 5CCPT", "N PRBP", "N PST").

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003638

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1 5CCPT`-`80 5CCPT` | 57 each | short | raw | 5-Choice CPT numeric trigger codes |
| `116 PRBP`, `117 PRBP` | 57 each | short | raw | Probabilistic reward/punishment task trigger codes |
| `31 PST`, `32 PST`, `39 PST` | 56-57 each | short | raw | Pavlovian-to-Instrumental Transfer task trigger codes |
| `STATUS` | 57 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: 5CCPTPSTPRBP
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003638 DOI: https://doi.org/10.1038/nrn3241


### Normal Task 1: 5CCPT stimulus classification (need to decode event meaning)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric trigger codes require decoding from events.tsv or dataset README. Events with suffix `5CCPT` correspond to the 5-Choice CPT; `PRBP` to reward/punishment; `PST` to Pavlovian transfer. Exact meaning of each numeric code must be verified from dataset documentation.

| Event | y | Meaning |
 |-------|---|------|
| `41 5CCPT` | 0 | 5CCPT correct response (need to confirm from events.tsv) |
| `43 5CCPT` | 1 | 5CCPT commission error (need to confirm from events.tsv) |
## Data Quality Notes

- 30+ distinct numeric trigger types; decode from events.tsv before epoching.
- All three paradigms recorded in a single 57-file session; paradigm blocks need to be separated by trigger suffix.
- `STATUS` is a single admin marker per file; exclude from epoching.

## References

- **Reference**: `Electrophysiological biomarkers of behavioral dimensions from cross-species paradigms. OpenNeuro ds003638.`
