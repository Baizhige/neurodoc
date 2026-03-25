# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74.0 | **Sampling Rate**: 250.0 Hz

## Paradigm

Participants viewed famous, unfamiliar, and scrambled face images and performed a subjective spatial symmetry judgment task (yes/no button press). The primary scientific question concerns the neural basis of face recognition, with ERP components (N170, N250) distinguishing famous from unfamiliar and scrambled faces. This is an EEGLAB tutorial dataset based on the SPM multimodal dataset (ds000117); events encode face category, presentation order (first vs. second), and latency of second presentation (early vs. late).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002718

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `famous_new` | 18 (files) | short | raw | Famous face - first presentation |
| `unfamiliar_new` | 18 (files) | short | raw | Unfamiliar face - first presentation |
| `scrambled_new` | 18 (files) | short | raw | Scrambled face - first presentation |
| `famous_second_early` | 18 (files) | short | raw | Famous face - second presentation (early lag) |
| `famous_second_late` | 18 (files) | short | raw | Famous face - second presentation (late lag) |
| `unfamiliar_second_early` | 18 (files) | short | raw | Unfamiliar face - second presentation (early lag) |
| `unfamiliar_second_late` | 18 (files) | short | raw | Unfamiliar face - second presentation (late lag) |
| `scrambled_second_early` | 18 (files) | short | raw | Scrambled face - second presentation (early lag) |
| `scrambled_second_late` | 18 (files) | short | raw | Scrambled face - second presentation (late lag) |
| `right_sym` | 10 (files) | short | raw | Right-hand response: face judged symmetric |
| `left_nonsym` | 10 (files) | short | raw | Left-hand response: face judged non-symmetric |
| `left_sym` | 8 (files) | short | raw | Left-hand response: face judged symmetric |
| `right_nonsym` | 8 (files) | short | raw | Right-hand response: face judged non-symmetric |
| `boundary` | 18 (files) | admin | raw | Segment boundary marker - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Face Recognition
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002718 DOI: https://doi.org/10.18112/openneuro.ds002718.v1.1.0


### Normal Task 1: Face Category Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Three-class face categorization targets the primary N170/N250 ERP question. `boundary` is a segment boundary admin marker - excluded. Response events (right_sym, left_sym, etc.) are button-press responses, not stimulus events. Regression target: `response_time`.

 | Event | y | Meaning |
 |-------|---|---------|
 | `famous_new` | 0 | Famous face - first presentation |
 | `unfamiliar_new` | 1 | Unfamiliar face - first presentation |
 | `scrambled_new` | 2 | Scrambled face - first presentation |
## Data Quality Notes

- Count column shows files-with-event (18 subjects), not individual trial counts - actual trial counts per category are much higher.
- `boundary` events are segment/epoch boundary markers - do not epoch on these.
- This is an EEGLAB tutorial dataset with well-documented preprocessing pipeline.
- Verify channel count consistency across subjects before pooling.

## References

- **Paper**: Multimodal Integration of M/EEG and f/MRI Data in SPM12 (DOI/ref: `ds000117`)
