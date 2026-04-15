# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: 14 | **Files (Completed)**: 350 | **Channels**: 31 | **Sampling Rate**: 1000 Hz
**Manual Review**: Mr.PJ

## Paradigm

Participants seated in a dimly lit room at 110 cm from a computer screen piloted from a PC computer. Two tasks alternated: a categorization task and a recognition task. In both tasks, target images and non-target images were equally likely presented. Participants were tested in two recording phases. The first day was composed of 13 series, the second day of 12 series, with 100 images per series (see details of the series below). To start a series, subjects had to press a touch-sensitive button. A small fixation point (smaller than 0.1 degree of visual angle) was drawn in the middle of a black screen. Then, an 8 bit color vertical photograph (256 pixels wide by 384 pixels high which roughly correspond to 4.5 degree of visual angle in width and 6.5 degree in height) was flashed for 20 ms (2 frames of a 100 Hz SVGA screen) using a programmable graphic board (VSG 2.1, Cambridge Research Systems). This short presentation time avoid that subjects use exploratory eye movement to respond. Participants gave their responses following a go/nogo paradigm. For each target, they had to lift their finger from the button as quickly and accurately as possible (releasing the button restored a focused light beam between an optic fiber led and its receiver; the response latency of this apparatus was under 1 ms). Participants were given 1000 ms to respond, after what any response was considered as a nogo response. The stimulus onset asynchrony (SOA) was 2000 ms plus or minus a random delay of 200 ms. For each distractor, participants had to keep pressing the button during at least 1000 ms (nogo response).

More specifically, in the animal categorization task, participants had to respond whenever there was an animal in the picture. In the recognition task, the session started with a learning phase. A probe image was flashed 15 times during 20 ms intermixed with two presentations of 1000 ms after the fifth and the tenth flashes, allowing an ocular exploration of the image; with an inter-stimulus of 1000 ms. Participants were instructed to carefully examine and learn the probe image in order to recognize it in the following series. The test phase started immediately after the learning phase. The probe image constituted the unique target of the series. Both tasks were organized in series of 100 images; 50 targets images were mixed with 50 non-targets in the animal categorization task; 50 copies of an unique photographs were mixed at random with 50 non-targets in the recognition task.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
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
| `subject_sex` | missing | need |
| `device` | missing | need |


## Tasks

### Classical Task 1: Target-vs-Distractor ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: , target_events = [`animal_target`, `easy_target`, `difficult_target`, `nonanimal_target`, `animal_distractor`, `easy_distractor`, `difficult_distractor`, `nonanimal_distractor`]
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
  - DOI: 10.1038/s41598 — 023-27528-0 — Uses this dataset's animal go/no-go condition to compare correct targets and correct distractors with 1 s epochs from -0.3 to 0.7 s, explicitly framing the contrast as go responses on animals versus no-go responses on non-animal images.
- **Kernel Notes**: 

### Classical Task 2: Stimulus-Class ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: , target_events = [`animal_target`, `animal_distractor`, `easy_target`, `easy_distractor`, `difficult_target`, `difficult_distractor`, `nonanimal_target`, `nonanimal_distractor`]
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
  - DOI: 10.1038/s41598 — 023-27528-0 — Reports the full 8-stimulus-class structure used in the paradigm.
- **Kernel Notes**: 

### Potential Task 1: Response Correctness Classification
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
  - DOI: DOI: — Response events are explicit in the event table and can be analyzed separately from stimulus-locked epochs if response-locked decoding is desired.
- **Kernel Notes**: 

## Data Quality Notes

- Large dataset: 350 runs; verify subject/session structure from BIDS metadata.
- ~50% go rate per run based on stimulus (100) vs response (52) counts.
- 1000 Hz sampling rate; consider downsampling to 250 Hz for efficiency.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
