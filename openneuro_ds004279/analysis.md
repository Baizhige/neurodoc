# Large Spanish EEG

**Dataset**: `openneuro_ds004279` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004279
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 60
**Channels**: 69 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed speech perception and silent speech production tasks involving 30 daily Spanish sentences. Each sentence trial followed a fixed structure: a rest period, a preparation cue, a perception phase (hearing the sentence), and a production phase (silently producing the sentence). The study investigated EEG correlates of perceived and silently produced speech.

## File Scan Result

> **Kernel SHA256**: `435f347255c93943812ca902e96ec9ee133dc1f5c4b7bc758f0b7a36f7992679`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 370 | event | raw | Perception phase for sentence 1 |
| `10` | 370 | event | raw | Perception phase for sentence 10 |
| `11` | 370 | event | raw | Perception phase for sentence 11 |
| `12` | 370 | event | raw | Perception phase for sentence 12 |
| `13` | 370 | event | raw | Perception phase for sentence 13 |
| `14` | 370 | event | raw | Perception phase for sentence 14 |
| `15` | 370 | event | raw | Perception phase for sentence 15 |
| `16` | 370 | event | raw | Perception phase for sentence 16 |
| `17` | 370 | event | raw | Perception phase for sentence 17 |
| `18` | 370 | event | raw | Perception phase for sentence 18 |
| `19` | 370 | event | raw | Perception phase for sentence 19 |
| `2` | 370 | event | raw | Perception phase for sentence 2 |
| `20` | 370 | event | raw | Perception phase for sentence 20 |
| `21` | 371 | event | raw | Perception phase for sentence 21 |
| `22` | 370 | event | raw | Perception phase for sentence 22 |
| `23` | 370 | event | raw | Perception phase for sentence 23 |
| `24` | 370 | event | raw | Perception phase for sentence 24 |
| `25` | 370 | event | raw | Perception phase for sentence 25 |
| `26` | 365 | event | raw | Perception phase for sentence 26 |
| `27` | 65 | event | raw | Perception phase for sentence 27 |
| `28` | 60 | event | raw | Perception phase for sentence 28 |
| `29` | 60 | event | raw | Perception phase for sentence 29 |
| `3` | 370 | event | raw | Perception phase for sentence 3 |
| `30` | 10921 | event | raw | Perception phase for sentence 30 |
| `31` | 11100 | event | raw | Production phase for sentence 1 |
| `32` | 11100 | event | raw | Production phase for sentence 2 |
| `33` | 544 | event | raw | Preparation cue for sentence 1 |
| `34` | 10926 | event | raw | Preparation cue for sentence 2 |
| `35` | 298 | event | raw | Rest period for sentence 1 |
| `36` | 366 | event | raw | Rest period for sentence 2 |
| `37` | 370 | event | raw | Rest period for sentence 3 |
| `38` | 370 | event | raw | Rest period for sentence 4 |
| `39` | 125 | event | raw | Admin marker (variable) |
| `4` | 370 | event | raw | Perception phase for sentence 4 |
| `40` | 2 | event | raw | Admin marker (variable) |
| `5` | 370 | event | raw | Perception phase for sentence 5 |
| `6` | 370 | event | raw | Perception phase for sentence 6 |
| `7` | 370 | event | raw | Perception phase for sentence 7 |
| `8` | 370 | event | raw | Perception phase for sentence 8 |
| `9` | 370 | event | raw | Perception phase for sentence 9 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 30-Class Sentence Identity Classification from Perceived Speech
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`perception_1`, `perception_2`, `perception_3`, `perception_4`, `perception_5`, `perception_6`, `perception_7`, `perception_8`, `perception_9`, `perception_10`, `perception_11`, `perception_12`, `perception_13`, `perception_14`, `perception_15`, `perception_16`, `perception_17`, `perception_18`, `perception_19`, `perception_20`, `perception_21`, `perception_22`, `perception_23`, `perception_24`, `perception_25`, `perception_26`, `perception_27`, `perception_28`, `perception_29`, `perception_30`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `perception_1` | 0 | Sentence 1 perception phase |
  | `perception_2` | 1 | Sentence 2 perception phase |
  | `perception_3` | 2 | Sentence 3 perception phase |
  | `perception_4` | 3 | Sentence 4 perception phase |
  | `perception_5` | 4 | Sentence 5 perception phase |
  | `perception_6` | 5 | Sentence 6 perception phase |
  | `perception_7` | 6 | Sentence 7 perception phase |
  | `perception_8` | 7 | Sentence 8 perception phase |
  | `perception_9` | 8 | Sentence 9 perception phase |
  | `perception_10` | 9 | Sentence 10 perception phase |
  | `perception_11` | 10 | Sentence 11 perception phase |
  | `perception_12` | 11 | Sentence 12 perception phase |
  | `perception_13` | 12 | Sentence 13 perception phase |
  | `perception_14` | 13 | Sentence 14 perception phase |
  | `perception_15` | 14 | Sentence 15 perception phase |
  | `perception_16` | 15 | Sentence 16 perception phase |
  | `perception_17` | 16 | Sentence 17 perception phase |
  | `perception_18` | 17 | Sentence 18 perception phase |
  | `perception_19` | 18 | Sentence 19 perception phase |
  | `perception_20` | 19 | Sentence 20 perception phase |
  | `perception_21` | 20 | Sentence 21 perception phase |
  | `perception_22` | 21 | Sentence 22 perception phase |
  | `perception_23` | 22 | Sentence 23 perception phase |
  | `perception_24` | 23 | Sentence 24 perception phase |
  | `perception_25` | 24 | Sentence 25 perception phase |
  | `perception_26` | 25 | Sentence 26 perception phase |
  | `perception_27` | 26 | Sentence 27 perception phase |
  | `perception_28` | 27 | Sentence 28 perception phase |
  | `perception_29` | 28 | Sentence 29 perception phase |
  | `perception_30` | 29 | Sentence 30 perception phase |
- **Kernel Notes**: Verify event ID mapping from events.tsv — event IDs 1-30 correspond to sentences 1-30 perception phases. Downsample data to 250 Hz before epoching. Trim trials to exactly 3 s (750 data points) per paper specifications. Events 27-29 show lower counts (60-65 vs ~370) suggesting incomplete data for those sentences; consider excluding or flagging these. Exclude admin markers (bad_artifact, Impedance_test, bad_before/after_experiment) from epoching.
- **Evidence**: DOI: 10.1088/1741-2552/ad88a3 — 56 participants, 64 EEG channels, 30-class Spanish sentence identity classification from perceived speech using deep neural networks (EEGNet, DeepConvNet, ShallowConvNet) with 3-second windows aligned to perception onset.

### Normal Task 1: Perception vs Production Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = [`perception_1`, `perception_2`, ..., `perception_30`, `production_1`, `production_2`, ..., `production_30`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `perception_1` | 0 | Sentence 1 perception phase |
  | `perception_2` | 0 | Sentence 2 perception phase |
  | ... | 0 | ... |
  | `perception_30` | 0 | Sentence 30 perception phase |
  | `production_1` | 1 | Sentence 1 silent production phase |
  | `production_2` | 1 | Sentence 2 silent production phase |
  | ... | 1 | ... |
  | `production_30` | 1 | Sentence 30 silent production phase |
- **Kernel Notes**: Group all 30 perception_N events as class 0 and all 30 production_N events as class 1. Event IDs 31-32 likely encode production phases (counts ~11100 matching 60 files × ~185 per file). Use 0.5 s overlap for sliding window analysis to capture neural signature differences between listening and silent speaking. Exclude admin events from epoching.
- **Evidence**: DOI: 10.1088/1741-2552/ad88a3 — Same dataset includes both speech perception and silent speech production phases; binary classification between these conditions is a natural extension supported by the paradigm structure.

### Potential Task 1: Preparation Cue Classification (Perception vs Preparation Phase)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = [`perception_1`, `perception_2`, ..., `perception_30`, `preparation_1`, `preparation_2`, ..., `preparation_30`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `preparation_1` | 0 | Sentence 1 preparation cue |
  | `preparation_2` | 0 | Sentence 2 preparation cue |
  | ... | 0 | ... |
  | `preparation_30` | 0 | Sentence 30 preparation cue |
  | `perception_1` | 1 | Sentence 1 perception phase |
  | `perception_2` | 1 | Sentence 2 perception phase |
  | ... | 1 | ... |
  | `perception_30` | 1 | Sentence 30 perception phase |
- **Kernel Notes**: Classify neural activity during preparation cues vs. speech perception to investigate pre-speech motor planning signatures. Preparation phases precede each perception-production sequence and may show distinct EEG signatures related to speech planning. Exclude admin events.
- **Evidence**: No direct reference; plausible from paradigm structure where each trial includes a preparation cue phase preceding perception and production.

### Potential Task 2: Rest Period Activity Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = [`rest_1`, `rest_2`, ..., `rest_30`, `perception_1`, `perception_2`, ..., `perception_30`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `rest_1` | 0 | Sentence 1 rest period |
  | `rest_2` | 0 | Sentence 2 rest period |
  | ... | 0 | ... |
  | `rest_30` | 0 | Sentence 30 rest period |
  | `perception_1` | 1 | Sentence 1 perception phase |
  | `perception_2` | 1 | Sentence 2 perception phase |
  | ... | 1 | ... |
  | `perception_30` | 1 | Sentence 30 perception phase |
- **Kernel Notes**: Compare neural activity during rest periods vs. active speech perception to identify state-dependent EEG changes (e.g., alpha modulation, auditory processing signatures). Exclude bad_* admin events.
- **Evidence**: No direct reference; rest periods are integral to the trial structure and can serve as baseline comparison for speech perception analysis.