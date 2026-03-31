# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2015 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74 | **Sampling Rate**: 250.0 Hz

## Paradigm

Participants viewed famous faces, unfamiliar faces, and scrambled faces while making a left/right subjective symmetry judgment. Each image was presented twice, with the second presentation occurring either immediately or after a delayed lag. The EEGLAB repackaging merged the original runs, corrected event latencies, resampled the EEG to 250 Hz, and retained stimulus identity, response side/symmetry, presentation order, and repetition distance information in the event table.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: famous, unfamiliar, scrambled, repetition, symmetry judgment

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `famous_new` | 2700 | short | raw | Initial presentation of a famous face |
| `famous_second_early` | 1313 | short | raw | Immediate repeat of a famous face |
| `famous_second_late` | 1291 | short | raw | Delayed repeat of a famous face |
| `unfamiliar_new` | 2700 | short | raw | Initial presentation of an unfamiliar face |
| `unfamiliar_second_early` | 1304 | short | raw | Immediate repeat of an unfamiliar face |
| `unfamiliar_second_late` | 1316 | short | raw | Delayed repeat of an unfamiliar face |
| `scrambled_new` | 2700 | short | raw | Initial presentation of a scrambled face |
| `scrambled_second_early` | 1271 | short | raw | Immediate repeat of a scrambled face |
| `scrambled_second_late` | 1334 | short | raw | Delayed repeat of a scrambled face |
| `right_sym` | 4900 | short | raw | Right-button response indicating more symmetric than average |
| `right_nonsym` | 3616 | short | raw | Right-button response indicating less symmetric than average |
| `left_sym` | 3381 | short | raw | Left-button response indicating more symmetric than average |
| `left_nonsym` | 3532 | short | raw | Left-button response indicating less symmetric than average |
| `boundary` | 90 | admin | raw | Boundary marker introduced when original runs were merged |
| `face_type` | 15929 | short | super meta integration | Collapsed face-category label from raw events: famous vs unfamiliar vs scrambled |
| `repetition_status` | 15929 | short | super meta integration | Collapsed presentation-order label derived from `event_order`: first vs repeated |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `short`: all stimulus and button-press events in this dataset are short events
> - `admin`: `boundary` events should be excluded from epoch targets

## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels from native event-table fields.
- **Candidate Labels**: `face_type`, `repetition_status`, `repetition_lag`, `response_hand`, `symmetry_judgment`
- **Kernel Note**: The `response_time` column exists in the event tables but is empty in this EEGLAB repackaging, so reaction-time regression should not be treated as a supported default task.

## Tasks

### Primary Task 1: Face Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `famous_*` | 0 | Famous / familiar face |
  | `unfamiliar_*` | 1 | Unfamiliar face |
  | `scrambled_*` | 2 | Scrambled face |
- **Evidence**:
  - DOI: `10.1038/sdata.2015.1` describes this dataset and states that, for technical validation, the repetition manipulation is ignored, leaving three trial-types: Familiar (Famous) Faces, Unfamiliar (Nonfamous) Faces, and Scrambled Faces.
- **Kernel Notes**: This is the strongest literature-backed primary task for the repackaged EEG dataset. The raw `trial_type` values must be collapsed by face category rather than restricting analysis to only the `_new` events.

### Normal Task 1: Repetition Effect Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `*_new` | 0 | First presentation |
  | `*_second_early`, `*_second_late` | 1 | Repeated presentation |
- **Notes**: The event table explicitly preserves presentation order through both `trial_type` and `event_order`, so repetition can be analyzed directly even though the 2015 data descriptor chose to ignore this manipulation in its technical validation examples.

### Normal Task 2: Repetition Lag Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [`famous_second_early`, `famous_second_late`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `*_second_early` | 0 | Immediate repeat |
  | `*_second_late` | 1 | Delayed repeat |
- **Notes**: This task uses the explicit early/late repetition labels and is further supported by the native `trial_dist` and `time_dist` columns.

### Normal Task 3: Symmetry Judgment Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`right_sym`, `left_nonsym`, `left_sym`, `right_nonsym`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `right_sym` | 0 | Right-hand response: more symmetric |
  | `left_nonsym` | 1 | Left-hand response: less symmetric |
  | `left_sym` | 2 | Left-hand response: more symmetric |
  | `right_nonsym` | 3 | Right-hand response: less symmetric |
- **Notes**: This response-locked task is supported by explicit button-press events, but the original paper treats symmetry judgment mainly as an attention-maintenance task rather than the main scientific contrast.

## Data Quality Notes

- The dataset contains 18 EEG subjects and 18 EEG event files.
- EEG sidecars report `SamplingFrequency: 250` and `EEGChannelCount: 70`.
- Channel files contain 74 recorded channels in total: 70 EEG channels plus 4 physiological channels (HEOG, VEOG, and 2 ECG/EKG channels).
- The `response_time` column is present in the event tables but completely empty in this repackaged EEGLAB version.
- Total event rows across subjects: 31,448.
- `boundary` events appear because the original runs were merged during EEGLAB repackaging.
- One subject uses `ECG` rather than `EKG` as the channel type label for the two cardiac channels; this is a minor metadata inconsistency.

## References

- **Paper**: Wakeman, D. G. & Henson, R. N. A multi-subject, multi-modal human neuroimaging dataset. Sci Data 2, 150001 (2015). DOI: `10.1038/sdata.2015.1`
