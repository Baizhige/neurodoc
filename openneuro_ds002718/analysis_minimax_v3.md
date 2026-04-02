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

### Primary Task 1: Face Category Classification (famous vs unfamiliar vs scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `famous_new` | 0 | Famous face - first presentation |
  | `unfamiliar_new` | 1 | Unfamiliar face - first presentation |
  | `scrambled_new` | 2 | Scrambled face - first presentation |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — Three-class face category classification (famous/unfamiliar/scrambled) using ERP analysis (N170/N250 components) with epochs from -0.5s to +1.2s around stimulus onset
- **Kernel Notes**: Normal Task 1 from original analysis.md is subsumed by this Primary Task. Response time regression is available via misc label route but not part of this primary classification task. The paper reports mean RT ~955ms for regression targets.

### Primary Task 2: Repetition Effect Classification (first vs second presentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.2 s *, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `famous_new` | 0 | Famous face - first presentation |
  | `famous_second_early` | 1 | Famous face - second presentation (early lag) |
  | `famous_second_late` | 2 | Famous face - second presentation (late lag) |
  | `unfamiliar_new` | 3 | Unfamiliar face - first presentation |
  | `unfamiliar_second_early` | 4 | Unfamiliar face - second presentation (early lag) |
  | `unfamiliar_second_late` | 5 | Unfamiliar face - second presentation (late lag) |
  | `scrambled_new` | 6 | Scrambled face - first presentation |
  | `scrambled_second_early` | 7 | Scrambled face - second presentation (early lag) |
  | `scrambled_second_late` | 8 | Scrambled face - second presentation (late lag) |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — The original dataset analysis includes repetition effects (initial vs repeat presentations) with detailed timing for early vs late lag conditions
- **Kernel Notes**: This 9-class task captures both face category and presentation order/repetition timing. For simpler binary repetition analysis, collapse first presentations (y=0,3,6) vs second presentations (any second_* event). (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Symmetry Judgment Classification (response-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`right_sym`, `left_nonsym`, `left_sym`, `right_nonsym`]
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `right_sym` | 0 | Right-hand response: face judged symmetric |
  | `left_nonsym` | 1 | Left-hand response: face judged non-symmetric |
  | `left_sym` | 2 | Left-hand response: face judged symmetric |
  | `right_nonsym` | 3 | Right-hand response: face judged non-symmetric |
- **Notes**: Four-class response classification. Could be simplified to 2-class (symmetric vs non-symmetric) or 2-class (left-hand vs right-hand response). The `boundary` events should be excluded.

### Normal Task 2: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`]
- **Label Route**: `misc`
- **Target Definition**: Continuous response_time values from behavioral data (mean ~955ms reported in original study)
- **Notes**: Regression target: predict reaction time from EEG epochs. Requires alignment of behavioral response data with stimulus events. Kernel must extract RT from behavioral file and map to corresponding stimulus epochs.

## Data Quality Notes

- Count column shows files-with-event (18 subjects), not individual trial counts - actual trial counts per category are much higher.
- `boundary` events are segment/epoch boundary markers - do not epoch on these.
- This is an EEGLAB tutorial dataset with well-documented preprocessing pipeline.
- Verify channel count consistency across subjects before pooling.

