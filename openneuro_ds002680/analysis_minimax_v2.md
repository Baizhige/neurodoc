# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants performed two alternating visual go/no-go tasks: an animal categorization task and a target-image recognition task. Images were flashed for 20 ms, each run contained about 100 images, and participants responded by releasing a button for target images while withholding response for non-target images. The first recording phase contains 13 runs and the second recording phase contains 12 runs for each subject, for a total of 25 runs per subject.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: the dataset already contains raw stimulus classes, response correctness markers, and native `response_time`; derived labels are mainly needed for collapsing multiple stimulus classes into broader go/no-go or correctness groupings.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: target, distractor, correct, incorrect, response_time

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `animal_target` | 6298 | short | raw | Target stimulus in the animal categorization task |
| `animal_distractor` | 6300 | short | raw | Non-target stimulus in the animal categorization task |
| `easy_target` | 4200 | short | raw | Easy target stimulus in the recognition task |
| `easy_distractor` | 4200 | short | raw | Easy distractor stimulus in the recognition task |
| `difficult_target` | 4198 | short | raw | Difficult target stimulus in the recognition task |
| `difficult_distractor` | 4200 | short | raw | Difficult distractor stimulus in the recognition task |
| `nonanimal_target` | 2800 | short | raw | Non-animal target stimulus in the recognition task |
| `nonanimal_distractor` | 2800 | short | raw | Non-animal distractor stimulus in the recognition task |
| `correct` | 16921 | short | raw | Correct behavioral response event |
| `incorrect` | 745 | short | raw | Incorrect behavioral response event |
| `response_time` | 17666 | short | raw | Native reaction-time value in milliseconds, stored on stimulus rows with responses |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `short`: all task-relevant events in this dataset are short stimulus or response events
> - `admin`: no dedicated boundary/admin event type was observed in the `_events.tsv` files

## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores continuous or collapsed labels derived from native event-table fields.
- **Candidate Labels**: `response_time`, `is_go`, `is_target`, `is_correct`
- **Kernel Note**: `response_time` is already present in the BIDS event table and does not need to be reconstructed from event pairing.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`
- **Kernel Note**: Prefer the concrete stimulus values over a generic `stimulus` label because the class identity is already present in the raw event table.

## Tasks

### Primary Task 1: Target-vs-Distractor ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | `*_target` stimulus classes | 1 | Target / go stimulus |
  | `*_distractor` stimulus classes | 0 | Distractor / no-go stimulus |
- **Super Meta Notes**: Collapse the eight raw stimulus classes into a binary target-vs-distractor label by mapping all `*_target` values to target/go and all `*_distractor` values to distractor/no-go.
- **Evidence**:
  - DOI: `10.1016/j.cogbrainres.2003.11.010` studied this dataset design directly, with 14 subjects alternating an animal categorization task and a target-image recognition task, and compared ERP differences between correct target and correct distractor trials in both tasks.
  - DOI: `10.1038/s41598-023-27528-0` used this dataset's animal go/no-go condition to compare correct targets and correct distractors with 1 s epochs from -0.3 to 0.7 s, explicitly framing the contrast as go responses on animals versus no-go responses on non-animal images.
- **Kernel Notes**: This primary task is literature-supported because target vs distractor is the comparison used in the published analyses. The binary label does not need to be inferred from response presence because target vs distractor identity is already encoded in the raw stimulus event value.

### Normal Task 1: Stimulus-Class ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | `animal_target` | 1 | Animal categorization target |
  | `animal_distractor` | 2 | Animal categorization distractor |
  | `easy_target` | 3 | Easy recognition target |
  | `easy_distractor` | 4 | Easy recognition distractor |
  | `difficult_target` | 5 | Difficult recognition target |
  | `difficult_distractor` | 6 | Difficult recognition distractor |
  | `nonanimal_target` | 7 | Non-animal recognition target |
  | `nonanimal_distractor` | 8 | Non-animal recognition distractor |
- **Notes**: This formulation preserves the task structure described in the README, but the exact 8-way classification framing is a downstream decoding formulation rather than the primary contrast stated in the cited papers.

### Normal Task 2: Stimulus-Locked Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `misc`
- **Target Definition**: `response_time`
- **Notes**: Use the native `response_time` column on stimulus rows. Reaction time is present for many target trials and a smaller number of distractor trials with false-alarm responses, so filtering by target/distractor and correct/incorrect status is recommended before model construction.

### Normal Task 3: Response Correctness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | `correct` | 1 | Correct response |
  | `incorrect` | 0 | Incorrect response |
- **Notes**: Response events are explicit in the event table and can be analyzed separately from stimulus-locked epochs if response-locked decoding is desired.

## Data Quality Notes

- The dataset contains 14 subjects, each with 2 sessions and 25 runs total, yielding 350 `_events.tsv` files.
- Each run contains about 100 stimulus events and an average of about 50.5 response events.
- The `response_time` column is natively present and non-null for 17,666 stimulus rows.
- `_eeg.json` sidecars report `EEGChannelCount: 0`, but all 350 `*_channels.tsv` files contain 31 channel rows; use the channel files rather than the sidecar field for channel-count reporting.
- One run has metadata but no corresponding EEGLAB file: `sub-002_ses-01_task-gonogo_run-12`.
- The event JSON describes `trial_type` levels as `go`, `nogo`, and `responses`, but the actual TSV files use `stimulus` and `response`; rely on the TSV contents for programmatic labeling.

## References

- **Reference**: `Go-nogo categorization and detection task`
