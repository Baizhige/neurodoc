# Animal Categorization and Detection EEG Dataset

**Dataset**: `openneuro_ds002680` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 56 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Fourteen healthy participants (7 female, 7 male) performed a go/nogo animal categorization task and three single-target image detection tasks (easy animal, difficult animal, non-animal) while EEG was recorded with a 64-channel Neuroscan Synamps 1 system at 500 Hz. Stimuli were 20 ms flashes of natural scene images presented with ~2000 ms SOA; participants lifted their finger for target images (go trials) and withheld response for distractor images (no-go trials) within a 1000 ms response window. The experiment consisted of two sessions per participant, with multiple runs per session containing intermixed trials from the different task conditions. Animal targets and distractors were equally probable, and response times were recorded for all go trials.

## File Scan Result

> **Kernel SHA256**: `5f6bf341a3eff95779da53fed4af7a3fae0901ecc6d8482e2c165887d3f9a830`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `animal_distractor` | 6300 | event | raw | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task |
| `animal_target` | 6298 | event | raw | Stimulus onset: image containing an animal, target in go-nogo animal categorization task |
| `correct` | 16921 | event | raw | Response: correct response |
| `difficult_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
| `difficult_target` | 4198 | event | raw | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
| `easy_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
| `easy_target` | 4200 | event | raw | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
| `incorrect` | 745 | event | raw | Response: incorrect response |
| `nonanimal_distractor` | 2800 | event | raw | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
| `nonanimal_target` | 2800 | event | raw | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time_binned` | native (raw misc in EEG file) | raw | Native raw misc channel; likely contains binned response time data derived from behavioral responses |
| `response_time_misc` | native (raw misc in EEG file) | raw | Native raw misc channel; likely contains continuous response time data from go/nogo button release responses |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing | Neuroscan Synamps 1 (model 5083) |
| `cap` | missing |  |
| `gender` | missing | Available in participants.tsv (F/M values present for sub-002 through sub-008) |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Potential Task 1: 4-class stimulus difficulty detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`easy_target`, `difficult_target`, `nonanimal_target`, `easy_distractor`, `difficult_distractor`, `nonanimal_distractor`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `easy_target` | 0 | Easy-to-detect animal target in single-target detection task |
  | `difficult_target` | 1 | Hard-to-detect animal target in single-target detection task |
  | `nonanimal_target` | 2 | Non-animal target in single-target detection task |
  | `easy_distractor` | 3 | Distractor in easy animal detection task |
  | `difficult_distractor` | 3 | Distractor in difficult animal detection task |
  | `nonanimal_distractor` | 3 | Distractor in non-animal detection task |
- **Evidence**:
- **Notes**: All six event IDs are grounded in the dataset's events.json sidecar (sub-002_ses-01_task-gonogo_run-10_events.json, confirmed identical across sessions). The four target/distractor pairs correspond to three detection sub-tasks (easy, difficult, nonanimal) with targets merged into three classes and all distractor types merged into a single fourth class (y=3) as they share the same functional role (non-target stimuli requiring no-go response). Epoch window (-0.2 to 0.8 s) is inferred from the 20 ms stimulus flash duration and ~2000 ms SOA described in the README, capturing the early visual ERP response. The animal_categorization events (animal_target, animal_distractor) are excluded from this task as they belong to a separate go/nogo paradigm, not the single-target detection tasks.

### Potential Task 2: 2-class easy vs difficult target detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`easy_target`, `difficult_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `easy_target` | 0 | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
  | `difficult_target` | 1 | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
- **Evidence**:
  - `sub-002_ses-02_task-gonogo_run-1_events.json` — Defines `easy_target` as "An image containing an animal (easy to detect) that is a target in a single target image detection task" and `difficult_target` as "An image containing an animal (hard to detect) that is a target in a single target image detection task"
  - `sub-002_ses-01_task-gonogo_run-11_eeg.set` annotations — Contains `difficult_target` and `difficult_distractor` events, confirming these event IDs are present in the EEG recordings
  - `sub-002_ses-01_task-gonogo_run-10_eeg.set` annotations — Contains `animal_target` events from the same task structure, confirming event-anchored epochs are feasible
- **Notes**: Both classes are animal-containing targets from the single-target detection sub-task, differing only in detection difficulty. Distractor trials (easy_distractor, difficult_distractor) and other sub-task events (animal_*, nonanimal_*) are excluded. The 20 ms stimulus presentation with 1000 ms response window motivates a [-0.2, 0.8] s ERP epoch capturing visual evoked responses and early decision-related activity.

### Potential Task 3: 2-class target vs distractor all conditions
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`animal_target`, `easy_target`, `difficult_target`, `nonanimal_target`, `animal_distractor`, `easy_distractor`, `difficult_distractor`, `nonanimal_distractor`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `animal_target` | 0 | Target stimulus (animal image, go-nogo categorization) |
  | `easy_target` | 0 | Target stimulus (easy-to-detect animal image, detection task) |
  | `difficult_target` | 0 | Target stimulus (hard-to-detect animal image, detection task) |
  | `nonanimal_target` | 0 | Target stimulus (non-animal image, detection task) |
  | `animal_distractor` | 1 | Distractor stimulus (non-animal image, go-nogo categorization) |
  | `easy_distractor` | 1 | Distractor stimulus (non-animal image, easy detection task) |
  | `difficult_distractor` | 1 | Distractor stimulus (non-animal image, difficult detection task) |
  | `nonanimal_distractor` | 1 | Distractor stimulus (non-animal image, nonanimal detection task) |
- **Evidence**:
  - `sub-002_ses-01_task-gonogo_run-10_events.json` — events.json defines all 8 stimulus event types with their target/distractor roles across four sub-tasks (animal categorization, easy/difficult/nonanimal detection)
  - `sub-002_ses-01_task-gonogo_run-10_events.tsv` — actual events.tsv samples confirm `animal_target`/`animal_distractor` events with stimulus/response structure
  - `README` — describes go/nogo paradigm with 20 ms stimulus presentation, 2000 ms SOA, target and non-target images equally likely across categorization and recognition tasks
- **Notes**: Collapses across all four sub-task conditions (animal categorization, easy detection, difficult detection, nonanimal detection) to create a generic binary target vs distractor classification. All four target event types map to y=0; all four distractor event types map to y=1. The 20 ms flash presentation and ~2 s SOA are consistent across conditions, supporting a uniform epoch window.

### Potential Task 4: 2-class correct vs incorrect response
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `correct` | 0 | Correct response |
  | `incorrect` | 1 | Incorrect response |
- **Evidence**:
- **Notes**: Response-locked binary classification of behavioral outcome. Epochs are centered on the response event (correct/incorrect) rather than stimulus onset, capturing pre-response readiness potential (e.g., lateralized readiness potential) and post-response feedback-related activity. The -500ms to +500ms window is inferred from standard response-locked ERP literature. Both event types are explicitly defined in events.json with confirmed trigger values (correct=16921, incorrect=745) and appear consistently across all runs in both sessions.

### Potential Task 5: Go-NoGo Animal Categorization (Target vs Distractor)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`animal_target`, `animal_distractor`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `animal_target` | 0 | Stimulus onset: image containing an animal, target in go-nogo animal categorization task (go trial) |
  | `animal_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task (no-go trial) |
- **Evidence**:
  - events.json (sub-002_ses-02_task-gonogo_run-1_events.json) — Defines `animal_target` as "An image containing an animal that is a target in a go-nogo animal categorization task" and `animal_distractor` as "An image not containing an animal that is a distractor in a go-nogo animal categorization task"
  - events.tsv (sub-002_ses-01_task-gonogo_run-10_events.tsv) — Confirmed occurrence of both `animal_target` and `animal_distractor` events with trial_type='stimulus' and response_time values for targets
  - README — Describes go/nogo paradigm: "Participants gave their responses following a go/nogo paradigm" with 1000 ms response window; targets require finger lift (go), distractors require no response (no-go)
- **Notes**: The candidate originally proposed using trial_type column values 'go'/'nogo', but the actual events.tsv shows trial_type='stimulus'/'response' with the go/nogo semantic information encoded in the `value` column (animal_target vs animal_distractor). The events.json trial_type Levels define 'go' and 'nogo' but these do not appear in the actual data samples. The task is reformulated to use the event IDs directly, which unambiguously code the go (animal_target) vs no-go (animal_distractor) distinction in the animal categorization sub-task. The epoch window [-0.2, 0.8] s captures the pre-stimulus baseline and the early ERP components (P1, N1, P2, N2) known to differentiate go and no-go trials in go/no-go paradigms.

### Potential Task 6: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`animal_target`, `easy_target`, `difficult_target`, `nonanimal_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | response_time_misc | Per-trial response time in milliseconds (continuous scalar, from events.tsv:response_time). Trials with missing response_time (nogo/no-response trials) are excluded. |
- **Evidence**:
- **Notes**: The kernel must derive a misc channel `response_time_misc` from events.tsv:response_time. For each stimulus event row with non-null response_time, the scalar RT value is broadcast as a constant misc channel segment for the epoch duration (or stored as trial-level label array). The target_events list includes all four stimulus target types across the task variants. Epoch window [-0.2, 1.0] s is stimulus-locked and covers the full RT range (references note median RT ~440ms, with 1000ms response deadline). Derived misc channel makes this a super-level task.

### Potential Task 7: Response Time Binned Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`animal_target`, `easy_target`, `difficult_target`, `nonanimal_target`]`
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|---------------|
  | `response_time_binned` | 0 = fast response (RT < per-subject median), 1 = slow response (RT >= per-subject median); derived from `events.tsv:response_time` (Units=millisecond). Trials with missing response_time excluded. |
- **Evidence**:
- **Notes**: Kernel derivation step: Extract `response_time` values from stimulus rows in events.tsv (confirmed present in all target event types: animal_target, easy_target, difficult_target, nonanimal_target). Compute per-subject median split on valid response times. Create binary label `response_time_binned`: 0=fast (below median), 1=slow (above median). The derived misc channel is broadcast as a per-trial label array aligned to stimulus onset epochs. Reference notes median RT ~440ms from dataset literature. Response time column is catalog-grounded (found_in=sub-002_ses-01_task-gonogo_run-10_events.tsv, Units=millisecond).

### Potential Task 8: Gender Classification from Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | `gender` | `F` → y=0 (female), `M` → y=1 (male); balanced 7F/7M |
- **Evidence**:
- **Notes**: Subject-level trait prediction via continuous EEG segmentation. No event structure required; 2-second segments with 50% overlap extracted from continuous recordings. Gender labels drawn from participants.tsv native column. Binary classification with perfectly balanced classes (7 female, 7 male participants).

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
