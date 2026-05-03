# YOTO (You Only Think Once): An EEG Dataset for Tracking Spontaneous Cognitive Transitions and Multimodal Stimuli Responses in Resting-State and Task Phases

**Dataset**: `openneuro_ds005815` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005815
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 205 | **Channels**: 30 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

Participants engaged in resting-state (eyes open/closed) and task phases involving unimodal and multimodal stimuli (visual and auditory) and mental imagery, providing self-reported vividness ratings. The YOTO paradigm investigates spontaneous cognitive transitions and mental imagery across stimulus modalities with numeric condition codes and named state markers.

## File Scan Result

> **Kernel SHA256**: `41a3e353a99393b29ea4bc2f0b429b3ad50c888fc2b50a54ba0fa8e734ac709e`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `6`-`9` | 6720 each | event | raw | Stimulus condition codes (decode from events.tsv) |
| `TrialProc` | 6528 | event | raw | Trial procedure marker |
| `23` | 840 | event | raw | Stimulus/response code 23 |
| `22` | 420 | event | raw | Stimulus/response code 22 |
| `21` | 420 | event | raw | Stimulus/response code 21 |
| `StartInstruction` | 66 | event | raw | Instruction block onset |
| `Eyeclosed` | 66 | event | raw | Eyes-closed resting onset |
| `FixationBreak` | 66 | event | raw | Fixation break event |
| `EyeOpen` | 66 | event | raw | Eyes-open resting onset |
| `EndInstruction` | 66 | event | raw | Instruction block offset |
| `88` | 64 | event | raw | Response/trigger code 88 |
| `30`-`35` | 280 each | event | raw | Imagery/rating condition codes |
| `99` | 101 | admin | raw | Admin/session marker |
| `1` | 81 | event | raw | Condition code 1 |
| `2`-`5` | 68 each | event | raw | Condition codes 2-5 |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Multi-class Mental Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.0 s, target_events = [`1`, `2`, `3`, `6`, `7`, `8`, `21`, `22`, `23`, `30`] *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 1 | Visual stimuli condition code * |
  | `6` | 1 | Visual stimuli condition code * |
  | `21` | 1 | Visual stimuli condition code * |
  | `2` | 2 | Auditory stimuli condition code * |
  | `7` | 2 | Auditory stimuli condition code * |
  | `22` | 2 | Auditory stimuli condition code * |
  | `3` | 3 | Multimodal stimuli condition code * |
  | `8` | 3 | Multimodal stimuli condition code * |
  | `23` | 3 | Multimodal stimuli condition code * |
- **Super Meta Notes**: (empty - Meta Level is raw)
- **Evidence**:
  - DOI: `10.1038/s41597-025-05881-1` — YOTO dataset validation paper showing visual/auditory/multimodal mental imagery classification with 3-class label mapping (visual=1, auditory=2, multimodal=3)
- **Kernel Notes**: Extract 4s epochs from imagery phase (post-stimulus onset). Verify event ID to modality mapping from events.tsv — current mapping uses numeric codes as best inference from available raw events; paper describes `visual_square`, `auditory_vowel_a` style labels which may be derived BIDS names.

---

### Classical Task 2: Publisher-defined BIDS task: Rest1
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = see Target Definition | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `EyeOpen` | 1 | Eyes-open resting state |
  | `Eyeclosed` | 2 | Eyes-closed resting state |
  | `StartInstruction` | Needs verification | Instruction onset — verify if used as epoch marker |
  | `EndInstruction` | Needs verification | Instruction offset — verify if used as epoch marker |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005815 DOI: 10.18112/openneuro.ds005815.v2.0.1

---

### Classical Task 3: Publisher-defined BIDS task: Rest2
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = see Target Definition | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `EyeOpen` | 1 | Eyes-open resting state |
  | `Eyeclosed` | 2 | Eyes-closed resting state |
  | `StartInstruction` | Needs verification | Instruction onset — verify if used as epoch marker |
  | `EndInstruction` | Needs verification | Instruction offset — verify if used as epoch marker |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005815 DOI: 10.18112/openneuro.ds005815.v2.0.1

---

### Potential Task 1: Multi-task Cognitive (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `99` | 0 | Admin/session marker |
  | `1` | 1 | Condition code 1 |
  | `2` | 2 | Condition code 2 |
  | `3` | 3 | Condition code 3 |
  | `5` | 4 | Condition code 5 |
  | `StartInstruction` | 5 | Instruction onset |
  | `Eyeclosed` | 6 | Eyes-closed onset |
  | `FixationBreak` | 7 | Fixation break |
  | `EyeOpen` | 8 | Eyes-open onset |
  | `EndInstruction` | 9 | Instruction offset |
  | `88` | 10 | Response code 88 |
  | `6`-`9` | 11 | Condition code range 6-9 (needs verification) |
  | `21` | 12 | Code 21 |
  | `22` | 13 | Code 22 |
  | `23` | 14 | Code 23 |
  | `30`-`35` | 15 | Imagery code range 30-35 (needs verification) |

- **Notes**: Numerical codes require decoding from events.tsv. Eyes-open/closed markers (`EyeOpen`, `Eyeclosed`) can be used for resting-state analysis.

 | Event | y | Meaning |
 |-------|---|---------|
 | `99` | 0 | Admin/session marker |
 | `1` | 1 | Condition code 1 |
 | `2` | 2 | Condition code 2 |
 | `3` | 3 | Condition code 3 |
 | `5` | 4 | Condition code 5 |
 | `StartInstruction` | 5 | Instruction onset |
 | `Eyeclosed` | 6 | Eyes-closed onset |
 | `FixationBreak` | 7 | Fixation break |
 | `EyeOpen` | 8 | Eyes-open onset |
 | `EndInstruction` | 9 | Instruction offset |
 | `88` | 10 | Response code 88 |
 | `6` | 11 | Condition code 6 |
 | `7` | 12 | Condition code 7 |
 | `8` | 13 | Condition code 8 |
 | `9` | 14 | Condition code 9 |
 | `23` | 15 | Code 23 |
 | `22` | 16 | Code 22 |
 | `21` | 17 | Code 21 |
 | `30` | 18 | Imagery code 30 |
 | `35` | 19 | Imagery code 35 |
 | `25` | 20 | Imagery code 25 |
 | `32` | 21 | Imagery code 32 |
 | `31` | 22 | Imagery code 31 |
 | `27` | 23 | Imagery code 27 |
 | `28` | 24 | Imagery code 28 |
 | `24` | 25 | Imagery code 24 |
 | `33` | 26 | Imagery code 33 |
 | `26` | 27 | Imagery code 26 |
 | `29` | 28 | Imagery code 29 |
 | `34` | 29 | Imagery code 34 |

## Data Quality Notes

- Numerical event codes require mapping from dataset events.tsv or README.
- Small dataset (20 subjects); low statistical power for rare conditions.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
