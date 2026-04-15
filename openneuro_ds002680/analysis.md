# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000 Hz
**Manual Review**: Mr.PJ

## Paradigm

Participants performed two alternating visual go/no-go tasks: an animal categorization task and a target-image recognition task. Images were flashed for 20 ms, each run contained about 100 images, and participants responded by releasing a button for target images while withholding response for non-target images. The first recording phase contains 13 runs and the second recording phase contains 12 runs for each subject, for a total of 25 runs per subject.

## File Scan Result

> **Kernel SHA256**: `e808d4e1376c7b72e30bf2c6b3a5bd6084b4f2329ec9b0b857c77d75209d1376`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `animal_distractor` | 6300 | event | raw | Non-target stimulus in the animal categorization task (withhold response) |
| `animal_target` | 6298 | event | raw | Target stimulus in the animal categorization task (release button) |
| `correct` | 16921 | event | raw | Correct behavioral response |
| `difficult_distractor` | 4200 | event | raw | Difficult distractor stimulus in the recognition task (withhold response) |
| `difficult_target` | 4198 | event | raw | Difficult target stimulus in the recognition task (release button) |
| `easy_distractor` | 4200 | event | raw | Easy distractor stimulus in the recognition task (withhold response) |
| `easy_target` | 4200 | event | raw | Easy target stimulus in the recognition task (release button) |
| `incorrect` | 745 | event | raw | Incorrect behavioral response |
| `nonanimal_distractor` | 2800 | event | raw | Non-animal distractor stimulus in the recognition task (withhold response) |
| `nonanimal_target` | 2800 | event | raw | Non-animal target stimulus in the recognition task (release button) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
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
  |-------|---|-|
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
  - DOI: 10.1016/j.cogbrainres.2003.11.010 — Original publication of the dataset paradigm with same 14 subjects, 20ms stimuli, go/no-go response; 50% targets/50% distractors with button release for targets.
  - DOI: 10.1016/S0925-2312(02)00415-0 — Rapid go/no-go visual categorization task, 20ms stimuli, natural photographs, reports 94% accuracy using ICA/source dynamics on single-trial epochs.
- **Kernel Notes**: Binary label collapses all *_target events to 1 and all *_distractor events to 0. Target identity is already encoded in the raw event value — no response-pairing inference needed.

### Classical Task 2: Animal Categorization vs Recognition Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `animal_target` | 0 | Animal categorization task |
  | `animal_distractor` | 0 | Animal categorization task |
  | `easy_target` | 1 | Easy recognition task |
  | `easy_distractor` | 1 | Easy recognition task |
  | `difficult_target` | 2 | Difficult recognition task |
  | `difficult_distractor` | 2 | Difficult recognition task |
  | `nonanimal_target` | 3 | Non-animal recognition task |
  | `nonanimal_distractor` | 3 | Non-animal recognition task |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Reports the two-task paradigm structure used in the dataset.
  - DOI: 10.1016/j.cogbrainres.2003.11.010 — Original publication describing animal categorization and single-photograph recognition tasks.
- **Kernel Notes**: Collapses animal events to class 0 and recognition events (easy/difficult/nonanimal) to classes 1-3, preserving the two major task types for paradigm-level classification.

### Normal Task 1: Response Accuracy Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.3 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `correct` | 1 | Correct behavioral response |
  | `incorrect` | 0 | Incorrect behavioral response |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Uses response accuracy (correct vs incorrect) to filter trials for the go/no-go analysis.
- **Kernel Notes**: Response-locked epochs aligned to behavioral feedback events. The MISC labels (`reaction_time`, `response_time`) can enable precise response alignment and RT-normalized epoching.

### Potential Task 1: Response-Locked Motor Preparation Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.3 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `correct` | 1 | Correct response |
  | `incorrect` | 0 | Error response |
- **Evidence**:
  - Paradigm: Go/no-go tasks are well-suited for response-locked analysis to isolate motor preparation (LRP) and error monitoring (ERN) components.
- **Kernel Notes**: The MISC route contains `reaction_time` and `response_time` labels enabling precise response alignment. Behavioral events exist but are not paired to specific stimuli in the event structure — careful trial matching required.

### Potential Task 2: Recognition Difficulty Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `easy_target` | 0 | Easy difficulty |
  | `easy_distractor` | 0 | Easy difficulty |
  | `difficult_target` | 1 | Difficult difficulty |
  | `difficult_distractor` | 1 | Difficult difficulty |
- **Evidence**:
  - Paradigm: The dataset includes explicit difficulty levels (easy/difficult) designed to modulate recognition performance, making difficulty classification a plausible task.
- **Kernel Notes**: Binary difficulty label within the recognition task only. Collapses target/distractor within each difficulty level.

### Potential Task 3: Target Identity Multi-Class Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.7 s, target_events = [`animal_target`, `easy_target`, `difficult_target`, `nonanimal_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `animal_target` | 0 | Animal category |
  | `easy_target` | 1 | Easy recognition category |
  | `difficult_target` | 2 | Difficult recognition category |
  | `nonanimal_target` | 3 | Non-animal recognition category |
- **Evidence**:
  - Paradigm: Natural scenes with distinct semantic categories (animals, non-animals, easy/difficult photographs) are processed differently in visual cortex.
- **Kernel Notes**: 4-class classification using only target events (go responses). Distractor events omitted to focus on target-specific processing patterns.