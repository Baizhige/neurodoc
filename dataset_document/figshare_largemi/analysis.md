# A Large EEG Motor Imagery Dataset for EEG-BCI

**Dataset**: `figshare_largemi` | **Year**: 2018 | **URL**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698
**Category**: Action/Output | **Subjects**: 13 | **Files (Completed)**: 73 | **Channels**: 22 | **Sampling Rate**: 200/1000 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

Thirteen subjects (A–M) participated in multiple EEG recording sessions in this large EEG-BCI dataset. The published dataset includes 60 hours of EEG from 13 participants across 75 sessions. EEG was recorded with 22 channels total: 19 standard 10/20 EEG leads, 2 ground leads (A1, A2), and 1 synchronization channel (X3). The main BCI dataset contains over 60,000 motor imagery examples collected in four interaction paradigms, while an additional NoMT paradigm was recorded as a baseline / consistency-check condition.

The paradigms are:

CLA: 3-state synchronous MI — left hand, right hand, and a passive state.
HaLT: 6-state synchronous MI — left hand, right hand, left leg, right leg, tongue, and a passive state.
5F: 5-state finger MI — imagery of individual finger movements on one hand.
FreeForm: self-paced voluntary left- and right-hand key presses, designed to study EEG activity preceding voluntary motor execution rather than standard cue-based imagery.
NoMT: visual-stimulus-only, no-motor-response baseline sessions. These sessions were similar to HaLT in visual presentation, but participants were explicitly instructed not to respond to the visual signals and instead passively watched the screen throughout. No mental imagery states were present (0St).

For the synchronous paradigms, each recording session began with an initial relaxation period and then contained three 15-minute interaction segments separated by breaks. In the cue-based trials, a visual action signal was presented for 1 s, followed by a 1.5–2.5 s pause, for an average trial length of about 3 s. In CLA, HaLT, and 5F, subjects performed the instructed imagery once during the 1-second cue interval. In contrast, FreeForm was self-paced rather than cue-triggered: participants voluntarily pressed left- or right-hand keys at arbitrary times while EEG was recorded.

## File Scan Result

> **Kernel SHA256**: `a8832789924f840bc44bd3b38edc6fc29bb5dfedf3c46c596f9f27524bc69c51`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `5F: index finger MI` | 3308 | event | raw | Index finger motor imagery cue (5F paradigm) |
| `5F: middle finger MI` | 3716 | event | raw | Middle finger motor imagery cue (5F paradigm) |
| `5F: pinkie MI` | 3561 | event | raw | Pinky finger motor imagery cue (5F paradigm) |
| `5F: ring finger MI` | 3578 | event | raw | Ring finger motor imagery cue (5F paradigm) |
| `5F: thumb MI` | 3908 | event | raw | Thumb motor imagery cue (5F paradigm) |
| `CLA: left hand MI` | 4624 | event | raw | Left-hand motor imagery cue (CLA paradigm) |
| `CLA: passive state` | 4178 | event | raw | Passive state instruction (CLA paradigm) |
| `CLA: right hand MI` | 4624 | event | raw | Right-hand motor imagery cue (CLA paradigm) |
| `FREEFORM: left hand MI` | 1066 | event | raw | Left-hand motor imagery onset (FreeForm paradigm) |
| `FREEFORM: right hand MI` | 1061 | event | raw | Right-hand motor imagery onset (FreeForm paradigm) |
| `HaLT: left hand MI` | 4631 | event | raw | Left-hand motor imagery cue (HaLT paradigm) |
| `HaLT: left leg MI` | 4564 | event | raw | Left leg motor imagery cue (HaLT paradigm) |
| `HaLT: passive state` | 4560 | event | raw | Passive state instruction (HaLT paradigm) |
| `HaLT: right hand MI` | 4593 | event | raw | Right-hand motor imagery cue (HaLT paradigm) |
| `HaLT: right leg MI` | 4446 | event | raw | Right leg motor imagery cue (HaLT paradigm) |
| `HaLT: tongue MI` | 4847 | event | raw | Tongue motor imagery cue (HaLT paradigm) |
| `NoMT: left hand cue` | 1114 | event | raw | Visual cue for left hand (NoMT baseline) |
| `NoMT: left leg cue` | 1113 | event | raw | Visual cue for left leg (NoMT baseline) |
| `NoMT: passive cue` | 1103 | event | raw | Visual cue for passive state (NoMT baseline) |
| `NoMT: right hand cue` | 1114 | event | raw | Visual cue for right hand (NoMT baseline) |
| `NoMT: right leg cue` | 1076 | event | raw | Visual cue for right leg (NoMT baseline) |
| `NoMT: tongue cue` | 1178 | event | raw | Visual cue for tongue (NoMT baseline) |
| `admin: marker-91` | 63 | admin | raw | unkown |
| `admin: marker-92` | 31 | admin | raw | unkown |
| `admin: marker-99` | 172 | admin | raw | unkown |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: CLA-Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`CLA: left hand MI`, `CLA: right hand MI`, `CLA: passive state`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `CLA: left hand MI` | 0 | Left-hand motor imagery (CLA paradigm, marker 1) |
  | `CLA: right hand MI` | 1 | Right-hand motor imagery (CLA paradigm, marker 2) |
  | `CLA: passive state` | 2 | Passive/idle state (CLA paradigm, marker 3) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 2: Halt-Paradigm Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`HaLT: left hand MI`, `HaLT: right hand MI`, `HaLT: passive state`, `HaLT: left leg MI`, `HaLT: right leg MI`, `HaLT: tongue MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `HaLT: left hand MI` | 0 | Left-hand motor imagery (HaLT paradigm, marker 1) |
  | `HaLT: right hand MI` | 1 | Right-hand motor imagery (HaLT paradigm, marker 2) |
  | `HaLT: passive state` | 2 | Passive/idle state (HaLT paradigm, marker 3) |
  | `HaLT: left leg MI` | 3 | Left-leg motor imagery (HaLT paradigm, marker 4) |
  | `HaLT: right leg MI` | 4 | Right-leg motor imagery (HaLT paradigm, marker 6) |
  | `HaLT: tongue MI` | 5 | Tongue motor imagery (HaLT paradigm, marker 5) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 3: 5F-Paradigm Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`5F: thumb MI`, `5F: index finger MI`, `5F: middle finger MI`, `5F: ring finger MI`, `5F: pinkie MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `5F: thumb MI` | 0 | Thumb finger imagery (5F paradigm, marker 1) |
  | `5F: index finger MI` | 1 | Index finger imagery (5F paradigm, marker 2) |
  | `5F: middle finger MI` | 2 | Middle finger imagery (5F paradigm, marker 3) |
  | `5F: ring finger MI` | 3 | Ring finger imagery (5F paradigm, marker 4) |
  | `5F: pinkie MI` | 4 | Pinkie finger imagery (5F paradigm, marker 5) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, demonstrating multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
- **Notes**: 

### Classical Task 4: Binary Left vs. Right Hand Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1 s, target_events = [`FREEFORM: left hand MI`, `FREEFORM: right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `FREEFORM: left hand MI` | 0 | Left-hand motor imagery (FREEFORM paradigm) |
  | `FREEFORM: right hand MI` | 1 | Right-hand motor imagery (FREEFORM paradigm) |
- **Evidence**:
  - 10.1109/tnsre.2022.3186442 — Binary classification of left vs right hand motor imagery from the figshare_largemi dataset (the paper not claim specific paradigm, this task is for FREEFORM)
- **Notes**: 

## Data Quality Notes

- Multiple paradigms in one dataset; **always filter by protocol type before analysis** (use file path to identify protocol: `CLA`, `HaLT`, `FREEFORM`, `5F`, `NoMT`).
- Sampling rates differ: 200 Hz (5F protocol), 1000 Hz (CLA/HaLT/FREEFORM); process separately or resample to a common rate.
- Subject demographics: 13 subjects (A-M), 9 female / 4 male, age ranges 20-35.
- NoMT sessions have `none` annotations; exclude from MI analysis or use as rest class.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
