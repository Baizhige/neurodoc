# Anticipatory differences between Attention and Expectation

**Dataset**: `openneuro_ds004502` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004502
**Category**: Sensory/Response | **Subjects**: 38 | **Files (Completed)**: 38
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

An experimental task investigating neural mechanisms of anticipation by comparing stimulus-driven attention and predictive expectation. Participants attended to auditory or visual stimuli with varying validity cues to disentangle attention (stimulus-driven) from expectation (predictive) effects on neural anticipatory activity.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004502

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 17` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 18` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 19` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 20` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 21` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 22` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 23` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 24` | 38xx | short | raw | BrainVision trigger - decode from events.tsv |
| `S 33`...`S 57` | 38xx | short | raw | BrainVision trigger codes (22 codes) - decode from events.tsv |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 17`, `S 18`, `S 19`, `S 20`, `S 21`, `S 22`, `S 23`, `S 24`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Attexp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004502 DOI: https://doi.org/10.18112/openneuro.ds004502.v1.0.1


### Normal Task 1: Attention vs Expectation Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30 distinct BrainVision trigger codes (S 17-S 57 range) require semantic decoding from events.tsv. Grouping into attention vs. expectation conditions requires understanding the trigger code mapping.

| Event | y | Meaning |
 |-------|---|------|
 | `S 17`...`S 24` | 0 | Attention condition trials (S1x range) |
 | `S 33`...`S 57` | 1 | Expectation condition trials (S3x-S5x range) |
## Data Quality Notes

- 30 distinct trigger codes require semantic decoding from events.tsv metadata
- All 30 codes appear in all 38 files with consistent counts
- 63 channels at 1000 Hz (BrainVision system)

## References

- **Reference**: `Anticipatory differences between Attention and Expectation`
