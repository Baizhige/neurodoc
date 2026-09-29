# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed two alternating visual go/no-go tasks: an animal categorization task and a target-image recognition task. Images were flashed for 20 ms, each run contained about 100 images, and participants responded by releasing a button for target images while withholding response for non-target images. The first recording phase contains 13 runs and the second recording phase contains 12 runs for each subject, for a total of 25 runs per subject.

## File Scan Result

> **Kernel SHA256**: `ff0ca244b877ee53f921cd182aadc7b0a3c9a2d53a7bf101424de81b7a3af3ff`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `animal_distractor` | 6300 | event | raw | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task |
| `animal_target` | 6298 | event | raw | Stimulus onset: image containing an animal, target in go-nogo animal categorization task |
| `correct` | 16921 | event | raw | Response: correct behavioral response |
| `difficult_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
| `difficult_target` | 4198 | event | raw | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
| `easy_distractor` | 4200 | event | raw | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
| `easy_target` | 4200 | event | raw | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
| `incorrect` | 745 | event | raw | Response: incorrect behavioral response |
| `nonanimal_distractor` | 2800 | event | raw | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
| `nonanimal_target` | 2800 | event | raw | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 2-class animal categorization target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_distractor` | 0 | Image containing an animal, target in go-nogo animal categorization task |
  | `animal_target` | 1 | Image not containing an animal, distractor in go-nogo animal categorization task |
- **Evidence**:
  - doi:10.1016/j.cogbrainres.2003.11.010 — Classical 2-class go/no-go animal categorization with 14 subjects, 20 ms flashes, 25 runs; matches dataset parameters exactly
  - 10.1038/s41598-023-27528-0 — Describes epochs from -1 to 2 s with effect window 350-450 ms for similar paradigm; ~6300 balanced trials per class
- **Notes**: Conservative epoch window (-0.3 to 0.7 s) chosen to capture typical visual ERP components (P1, N1, P300) for 20 ms flash paradigm while avoiding post-response contamination. Both target_events are stimulus onset markers from the go-nogo animal categorization task specifically, excluding easy/difficult/nonanimal variants which belong to a different recognition task condition.

### Potential Task 1: 8-class stimulus type discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`, `difficult_distractor`, `difficult_target`, `easy_distractor`, `easy_target`, `nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_target` | 0 | Stimulus onset: image containing an animal, target in go-nogo animal categorization task |
  | `animal_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in go-nogo animal categorization task |
  | `easy_target` | 2 | Stimulus onset: image containing an animal (easy to detect), target in single target image detection task |
  | `easy_distractor` | 3 | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
  | `difficult_target` | 4 | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
  | `difficult_distractor` | 5 | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
  | `nonanimal_target` | 6 | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |
  | `nonanimal_distractor` | 7 | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — BIDS sidecar defining all 8 stimulus event types with their meanings (animal_target/distractor, easy_target/distractor, difficult_target/distractor, nonanimal_target/distractor)
  - sub-002_ses-01_task-gonogo_run-10_events.tsv — Direct observation of event values in data: animal_target, animal_distractor, correct, etc.
  - README — Task description: two alternated tasks (categorization and recognition), target and non-target images equally likely, go/nogo paradigm with 20 ms stimulus presentation
- **Notes**: Most granular event-based task possible with this dataset. Combines 4 task conditions (animal go-nogo categorization, easy/difficult/nonanimal single-target detection) × 2 target/distractor levels = 8 classes. Highly imbalanced across classes: animal (~6300 each), easy/difficult (~4200 each), nonanimal (~2800 each).

### Potential Task 2: 2-class easy detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`easy_distractor`, `easy_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `easy_target` | 0 | Stimulus onset: image containing an animal (easy to detect), target in single target easy animal image detection task |
  | `easy_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target easy animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — Defines `easy_target` as "An image containing an animal (easy to detect) that is a target in a single target image detection task" and `easy_distractor` as "An image not containing an animal that is a distractor in a single target easy animal image detection task"
  - events.tsv sample (sub-002_ses-01_task-gonogo_run-10) — Shows `easy_target` and `easy_distractor` events with stimulus trial_type and response_time values
  - README — Describes go/nogo paradigm with 20 ms flash presentation, 2000 ms SOA, and 1000 ms response window; same paradigm structure as other detection tasks in dataset
- **Notes**: Inferred epoch window (-0.3 to 0.7 s) based on 20 ms flash paradigm shared with animal categorization task; post-stimulus window covers typical visual ERP components (P1, N1, P2, N2) and early motor preparation for go responses. ~4200 trials per class estimated from event counts. No direct classical reference for this specific easy detection contrast, but structurally identical to established visual detection paradigms.

### Potential Task 3: 2-class difficult detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`difficult_distractor`, `difficult_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `difficult_target` | 0 | Stimulus onset: image containing an animal (hard to detect), target in single target image detection task |
  | `difficult_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target difficult animal image detection task |
- **Evidence**:
  - events.json sidecar (sub-002_ses-01_task-gonogo_run-10_events.json, sub-002_ses-01_task-gonogo_run-11_events.json) — confirms `difficult_target` and `difficult_distractor` as event levels with descriptions matching the difficult detection task condition
  - events.tsv samples (sub-002_ses-01_task-gonogo_run-11_events.tsv) — direct observation of `difficult_target` and `difficult_distractor` events in actual data
  - README — describes the recognition/detection task with target and non-target images equally likely, 20 ms flash presentation, go/nogo response paradigm
- **Notes**: ~4200 trials each of difficult_target and difficult_distractor, balanced classes. Epoch window inferred from classical task defaults for the same 20 ms flash paradigm (tmin=-0.3s, tmax=0.7s). This is the more challenging discrimination condition compared to easy_target/easy_distractor due to hard-to-detect animal images.

### Potential Task 4: 2-class nonanimal detection target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `nonanimal_target` | 0 | Stimulus onset: image not containing an animal, target in single target non-animal image detection task |
  | `nonanimal_distractor` | 1 | Stimulus onset: image not containing an animal, distractor in single target non-animal image detection task |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — events.json sidecar defines `nonanimal_target` as "An image not containing an animal that is a target in a single target image detection task" and `nonanimal_distractor` as "An image not containing an animal that is a distractor in a single target non-animal image detection task"
  - sub-002_ses-01_task-gonogo_run-10_events.tsv — direct observation of stimulus events with values `nonanimal_target` and `nonanimal_distractor` in actual data
  - README — describes go/nogo paradigm with 20 ms stimulus presentation, 1000 ms response window, 2000 ms ± 200 ms SOA; epoch window inferred from classical task defaults for this flash paradigm
- **Notes**: ~2800 trials each of nonanimal_target and nonanimal_distractor, balanced. Control condition without animal content in the single-target non-animal detection variant of the gonogo task.

### Potential Task 5: 2-class response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `correct` | 0 | Correct behavioral response |
  | `incorrect` | 1 | Incorrect behavioral response |
- **Evidence**:
  - sub-002_ses-01_task-gonogo_run-10_events.json — `correct` defined as "Correct response", `incorrect` defined as "Incorrect response" in value column Levels
  - events.tsv samples — Response events with trial_type='response' and values 'correct'/'incorrect' observed across all runs
- **Notes**: Response-locked epochs for error-related negativity (ERN) and correct-response positivity analysis. Highly imbalanced classes (~16921 correct vs ~745 incorrect). Epoch window -0.3 to 0.7 s centered on response onset to capture ERN (~0-100 ms) and Pe (~200-400 ms) components. Values marked with * inferred from standard ERN/Pe ERP literature.

### Potential Task 6: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — Include the gender of the subjects
- **Notes**: Segmentation-based biometric classification using 2-second overlapping EEG segments (50% overlap) from continuous recordings. Subject gender labels are drawn from participants.tsv, with balanced classes (7F, 7M across 14 subjects). No event structure required; segments are extracted uniformly across the continuous recording. Epoch parameters inferred from standard segmentation defaults for subject-level biometric tasks.

### Potential Task 7: Go vs No-Go Trial Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_distractor`, `animal_target`, `difficult_distractor`, `difficult_target`, `easy_distractor`, `easy_target`, `nonanimal_distractor`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `animal_target` | 0 | Go trial (target stimulus requiring button release) |
  | `easy_target` | 0 | Go trial (target stimulus requiring button release) |
  | `difficult_target` | 0 | Go trial (target stimulus requiring button release) |
  | `nonanimal_target` | 0 | Go trial (target stimulus requiring button release) |
  | `animal_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `easy_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `difficult_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
  | `nonanimal_distractor` | 1 | No-Go trial (distractor stimulus requiring response withholding) |
- **Evidence**:
  - events.json sidecar files (sub-002_ses-01_task-gonogo_run-10_events.json, sub-002_ses-01_task-gonogo_run-11_events.json) — Defines all 8 stimulus event types with explicit target/distractor meanings for go-nogo and single-target detection variants
  - events.tsv samples (sub-002_ses-01_task-gonogo_run-10_events.tsv) — Confirms event occurrence with trial_type='stimulus' and value column containing target/distractor events
  - README — Describes go/nogo paradigm: "Participants gave their responses following a go/nogo paradigm. For each target, they had to lift their finger from the button"
  - dataset_description.json — "Go-nogo categorization and detection task" confirms paradigm
- **Notes**: Many-to-one mapping of 8 distinct stimulus events to 2 classes (y=0 for all target/go trials, y=1 for all distractor/no-go trials) based on required behavioral response. The four target types (animal, easy, difficult, nonanimal) and four distractor types are collapsed across task variants (categorization vs. detection) since all share the same go/no-go response requirement. Epoch window inferred from related tasks in same dataset.

## Data Quality Notes

- *_eeg.json sidecars report EEGChannelCount: 0, while all *_channels.tsv files contain 31 channel rows; channel metadata should therefore be taken from the channel files rather than the sidecar field.
- The event JSON describes trial_type levels such as go, nogo, and responses, but the released TSV files actually use stimulus and response; downstream parsing should follow the TSV contents.
- The response_time column is available and populated for many stimulus rows, including some distractor trials with false-alarm responses, so RT-based analyses should explicitly filter by target/distractor and correctness criteria.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
