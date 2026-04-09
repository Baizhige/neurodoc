# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000 Hz
**Manual Review**: Mr.PJ

## Paradigm

Participants performed two alternating visual go/no-go tasks: an animal categorization task and a target-image recognition task. Images were flashed for 20 ms, each run contained about 100 images, and participants responded by releasing a button for target images while withholding response for non-target images. The first recording phase contains 13 runs and the second recording phase contains 12 runs for each subject, for a total of 25 runs per subject.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `animal_target` | 6298 | event | raw | Target stimulus in the animal categorization task |
| `animal_distractor` | 6300 | event | raw | Non-target stimulus in the animal categorization task |
| `easy_target` | 4200 | event | raw | Easy target stimulus in the recognition task |
| `easy_distractor` | 4200 | event | raw | Easy distractor stimulus in the recognition task |
| `difficult_target` | 4198 | event | raw | Difficult target stimulus in the recognition task |
| `difficult_distractor` | 4200 | event | raw | Difficult distractor stimulus in the recognition task |
| `nonanimal_target` | 2800 | event | raw | Non-animal target stimulus in the recognition task |
| `nonanimal_distractor` | 2800 | event | raw | Non-animal distractor stimulus in the recognition task |
| `correct` | 16921 | event | raw | Correct behavioral response event |
| `incorrect` | 745 | event | raw | Incorrect behavioral response event |
| `response_time` | 17666 | event | raw | Native reaction-time value (ms), stored on stimulus rows with responses |

> **Manual Review Note**: Event IDs and counts updated by human reviewer (Mr.PJ) from BIDS events.tsv — replaced placeholder `stimulus`/`response` entries with actual event names. Kernel should verify event names against events.tsv on next scan.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Target-vs-Distractor ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `animal_target` | 1 | Target / go stimulus |
  | `easy_target` | 1 | Target / go stimulus |
  | `difficult_target` | 1 | Target / go stimulus |
  | `nonanimal_target` | 1 | Target / go stimulus |
  | `animal_distractor` | 0 | Distractor / no-go stimulus |
  | `easy_distractor` | 0 | Distractor / no-go stimulus |
  | `difficult_distractor` | 0 | Distractor / no-go stimulus |
  | `nonanimal_distractor` | 0 | Distractor / no-go stimulus |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Uses this dataset's animal go/no-go condition to compare correct targets and correct distractors with 1 s epochs from -0.3 to 0.7 s, explicitly framing the contrast as go responses on animals versus no-go responses on non-animal images.
- **Kernel Notes**: Binary label collapses all *_target events to 1 and all *_distractor events to 0. Target identity is already encoded in the raw event value — no response-pairing inference needed.

### Classical Task 2: Stimulus-Class ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `animal_target` | 0 | Animal categorization target |
  | `animal_distractor` | 1 | Animal categorization distractor |
  | `easy_target` | 2 | Easy recognition target |
  | `easy_distractor` | 3 | Easy recognition distractor |
  | `difficult_target` | 4 | Difficult recognition target |
  | `difficult_distractor` | 5 | Difficult recognition distractor |
  | `nonanimal_target` | 6 | Non-animal recognition target |
  | `nonanimal_distractor` | 7 | Non-animal recognition distractor |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Reports the full 8-stimulus-class structure used in the paradigm.
- **Kernel Notes**: Preserves the full task structure. The 8-way classification is a downstream decoding formulation rather than the primary contrast in cited papers.

### Classical Task 3: Stimulus-Locked Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `response_time` | continuous | Native reaction time (ms) from BIDS event table |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Reaction time data is natively present in the BIDS event table for 17,666 stimulus rows.
- **Kernel Notes**: Use the native `response_time` column on stimulus rows. RT is present for most target trials and some distractor false-alarm trials. Filter by correct/incorrect status before model construction.

### Classical Task 4: Response Correctness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `correct` | 1 | Correct response |
  | `incorrect` | 0 | Incorrect response |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Response correctness events are explicit in the event table.
- **Kernel Notes**: Response events are explicit and can be analyzed separately from stimulus-locked epochs for response-locked decoding.

## Data Quality Notes

- Large dataset: 350 runs; verify subject/session structure from BIDS metadata.
- ~50% go rate per run based on stimulus (100) vs response (52) counts.
- 1000 Hz sampling rate; consider downsampling to 250 Hz for efficiency.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review