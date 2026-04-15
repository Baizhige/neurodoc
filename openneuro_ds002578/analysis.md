# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2004/2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz
**Manual Review**: Pending

## Paradigm

A continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. Five empty squares were presented continuously on screen, with participants instructed to attend to one designated location and press a mouse button whenever a white disk appeared at that attended location. Event codes encode both the attended position and the cued (stimulus) position, allowing separation of target oddballs (attended location = stimulus location) from non-target distractors. The dataset contains only 2 completed files and represents a very limited subset of the original study data.

## File Scan Result

> **Kernel SHA256**: `1996116d4444f599a313139a66b19f7536e32a71aca4d8a634430c9a9d92bf17`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Picture` | 5939 | event | raw | Generic stimulus presentation marker |
| `Response` | 1202 | event | raw | Participant button press response |
| `admin: marker-203` | 1 | admin | raw | Rare administrative marker; inspect manually if used |
| `admin: marker-217` | 2 | admin | raw | Rare administrative marker; inspect manually if used |
| `admin: marker-237` | 1 | admin | raw | Rare administrative marker; inspect manually if used |
| `boundary` | 58 | event | raw | Data segment boundary marker |
| `distractor: attend-3 cue-1` | 240 | event | raw | Non-target: attend position 3, stimulus at position 1 |
| `distractor: attend-3 cue-4` | 239 | event | raw | Non-target: attend position 3, stimulus at position 4 |
| `distractor: attend-3 cue-5` | 240 | event | raw | Non-target: attend position 3, stimulus at position 5 |
| `distractor: attend-4 cue-1` | 238 | event | raw | Non-target: attend position 4, stimulus at position 1 |
| `distractor: attend-4 cue-2` | 239 | event | raw | Non-target: attend position 4, stimulus at position 2 |
| `distractor: attend-4 cue-3` | 240 | event | raw | Non-target: attend position 4, stimulus at position 3 |
| `distractor: attend-4 cue-5` | 239 | event | raw | Non-target: attend position 4, stimulus at position 5 |
| `target: attend-3 cue-3` | 240 | event | raw | Target oddball: attend position 3, stimulus at position 3 |
| `target: attend-4 cue-4` | 239 | event | raw | Target oddball: attend position 4, stimulus at position 4 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | Not available in dataset metadata |
| `subject_sex` | complete | Not available in dataset metadata |
| `device` | missing | Not available in dataset metadata |

## Tasks

### Normal Task 1: Visual Oddball Target Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`target: attend-3 cue-3`, `target: attend-4 cue-4`, `distractor: attend-3 cue-1`, `distractor: attend-3 cue-4`, `distractor: attend-3 cue-5`, `distractor: attend-4 cue-1`, `distractor: attend-4 cue-2`, `distractor: attend-4 cue-3`, `distractor: attend-4 cue-5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `target: attend-3 cue-3` | 1 | Target oddball (attended position matches cue position 3) |
  | `target: attend-4 cue-4` | 1 | Target oddball (attended position matches cue position 4) |
  | `distractor: attend-3 cue-1` | 0 | Non-target distractor |
  | `distractor: attend-3 cue-4` | 0 | Non-target distractor |
  | `distractor: attend-3 cue-5` | 0 | Non-target distractor |
  | `distractor: attend-4 cue-1` | 0 | Non-target distractor |
  | `distractor: attend-4 cue-2` | 0 | Non-target distractor |
  | `distractor: attend-4 cue-3` | 0 | Non-target distractor |
  | `distractor: attend-4 cue-5` | 0 | Non-target distractor |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477-07.2007 — Partially supports visual oddball paradigm with target/non-target classification structure; establishes epoch parameters and P300/N200 ERP components typical for this task.
- **Kernel Notes**: Only 2 completed EEG files available (extremely limited sample size). Target events indicate attended location matches stimulus location; non-target events encode attend/cue mismatches. Apply baseline correction from -0.2 to 0 s for optimal P300 detection.

### Potential Task 2: Target Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`target: attend-3 cue-3`, `target: attend-4 cue-4`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `target: attend-3 cue-3` | continuous | Reaction time in seconds derived from target event to subsequent Response marker |
  | `target: attend-4 cue-4` | continuous | Reaction time in seconds derived from target event to subsequent Response marker |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477-07.2007 — Supports regression approach via single-trial theta power correlation with reaction time; paradigm includes button press responses to targets.
- **Kernel Notes**: Derive RT by pairing target events with subsequent Response marker. Verify Response marker timing falls within 0.1–1.5 s window per typical RT ranges. Filter false alarm responses (1202 Response markers vs 479 targets suggests ~2.5 responses per target on average; may include anticipatory or incorrect responses requiring filtering).

### Potential Task 3: Response False Alarm Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.3 s, target_events = [`Response`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Response` | derived | Correct response (y=1) if preceded by target event within 0.1–1.5 s; False alarm response (y=0) otherwise |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477-07.2007 — Selective attention paradigms typically include false alarm monitoring; response-locked analysis plausible for error detection.
- **Kernel Notes**: Requires pairing Response markers with preceding stimulus events to classify as correct (post-target) or false alarm (no preceding target or post-distractor). 1202 Response markers suggests multiple button presses per trial; may reflect anticipatory responses or multiple response attempts requiring careful filtering. Response-locked epoching at 256 Hz provides adequate temporal resolution for error-related negativity (ERN) components if present.