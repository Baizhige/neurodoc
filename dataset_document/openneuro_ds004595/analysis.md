# EEG: RL Task (3-Armed Bandit) with Alcohol Cues in Hazardous Drinkers

**Dataset**: `openneuro_ds004595` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004595
**Category**: High-level Mental | **Subjects**: 53 | **Files (Completed)**: 53 | **Channels**: 66 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Participants completed a reinforcement learning task using a 3-armed bandit paradigm incorporating alcohol-related and neutral beverage cues to study decision-making in hazardous drinkers versus controls. On each trial, a cue was presented followed by a three-arm choice display and probabilistic win/loss feedback. The study examines electrophysiological markers of cue-driven exploration and aberrant reinforcement learning in hazardous drinkers compared to healthy controls.

## File Scan Result

> **Kernel SHA256**: `703cddbf0fd78b8779e7559d2973521d743f4af58aad5a42d62103835216eff7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: marker-199` | 533 | event | raw | Admin marker for end-of-session cleanup or synchronization |
| `admin: marker-99` | 533 | event | raw | Admin marker for session initialization or sync |
| `boundary` | 53 | event | raw | BIDS boundary event marking continuous recording segments |
| `break end` | 173 | event | raw | End of inter-trial break period |
| `break start` | 726 | event | raw | Start of inter-trial break period |
| `choice display` | 12464 | event | raw | Three-arm bandit options displayed on screen |
| `cue: alcohol` | 18550 | event | raw | Alcohol beverage cue presentation |
| `cue: neutral` | 5553 | event | raw | Neutral (non-alcohol) beverage cue presentation |
| `feedback: loss` | 9713 | event | raw | Probabilistic loss outcome feedback |
| `feedback: win` | 7254 | event | raw | Probabilistic win outcome feedback |
| `instruction` | 667 | event | raw | Task instruction screen presentation |
| `novel cue: order 1` | 2955 | event | raw | Novel arm-order permutation variant 1 |
| `novel cue: order 2` | 2931 | event | raw | Novel arm-order permutation variant 2 |
| `novel cue: order 3` | 2853 | event | raw | Novel arm-order permutation variant 3 |
| `novel cue: order 4` | 2934 | event | raw | Novel arm-order permutation variant 4 |
| `novel cue: order 5` | 2908 | event | raw | Novel arm-order permutation variant 5 |
| `novel cue: order 6` | 2919 | event | raw | Novel arm-order permutation variant 6 |
| `response: left arm` | 1068 | event | raw | Left arm button press response |
| `response: right arm` | 1050 | event | raw | Right arm button press response |
| `trial: baseline` | 181 | event | raw | Baseline trial without active stimulus |
| `trial: end` | 194 | event | raw | Trial sequence termination marker |
| `trial: start` | 159 | event | raw | Trial sequence initiation marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Alcohol vs Neutral Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`cue: alcohol`, `cue: neutral`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `cue: alcohol` | 0 | Alcohol beverage cue presentation |
  | `cue: neutral` | 1 | Neutral beverage cue presentation |
- **Kernel Notes**: The `cue: alcohol` (18,550 trials) and `cue: neutral` (5,553 trials) events represent the primary substance-specific cue conditions. Longer tmax=2.0s accommodates typical cue duration in beverage paradigms. Aggregate as binary classification to capture differential neural responses (P3a/P3b) to alcohol vs neutral cues in hazardous drinkers.
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "EEG recorded during a three-armed bandit RL task with alcohol and neutral beverage cues; cue-locked epochs analyzed for P3a/P3b components; hazardous drinkers showed aberrant cue-specific exploration compared to controls."

### Classical Task 2: Feedback Valence Classification (Win vs Loss)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`feedback: win`, `feedback: loss`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `feedback: win` | 0 | Monetary/probabilistic win outcome |
  | `feedback: loss` | 1 | Monetary/probabilistic loss outcome |
- **Kernel Notes**: Feedback-locked epochs centered on `feedback: win` vs `feedback: loss` events will capture FRN/ERN components. The tmin=-0.2s allows brief baseline correction while tmax=1.0s captures the full feedback-related processing window. Event counts (win: 7,254; loss: 9,713) support balanced binary classification.
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "Three-armed bandit task with probabilistic win/loss feedback; feedback-locked ERPs analyzed; model-based analysis of reinforcement learning signals."

### Classical Task 3: Novel Cue Explore/Exploit Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`novel cue: order 1`, `novel cue: order 2`, `novel cue: order 3`, `novel cue: order 4`, `novel cue: order 5`, `novel cue: order 6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `novel cue: order 1` | 0 | Novel cue permutation order 1 |
  | `novel cue: order 2` | 1 | Novel cue permutation order 2 |
  | `novel cue: order 3` | 2 | Novel cue permutation order 3 |
  | `novel cue: order 4` | 3 | Novel cue permutation order 4 |
  | `novel cue: order 5` | 4 | Novel cue permutation order 5 |
  | `novel cue: order 6` | 5 | Novel cue permutation order 6 |
- **Kernel Notes**: Aggregate all 6 novel cue orders as a single class for P3a/P3b ERP analysis (following DOI 10.5334/cpsy.96 epoch window -500 to 1000ms), OR treat as 6-class classification for permutation-specific exploration analysis. Verify mapping to alcohol vs neutral cues from events.tsv. These events encode arm-order permutations for the bandit choice display.
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "Novel cues (6 arm-order permutations) presented during explore-exploit decisions; P3a/P3b amplitudes and POMDP model parameters (BONUS, IEV) predicted exploratory vs exploitative choice behavior."

### Normal Task 1: Response Arm Classification (Left vs Right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.5 s, target_events = [`response: left arm`, `response: right arm`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `response: left arm` | 0 | Left arm button press response |
  | `response: right arm` | 1 | Right arm button press response |
- **Kernel Notes**: Response-locked epochs capture motor preparation/execution components (MRP, lateralized readiness potential). Event counts (left: 1,068; right: 1,050) are well-balanced. Consider epoching around `choice display` events (12,464) instead for earlier motor planning markers.
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "3-armed bandit task requires discrete motor responses to left/right arms; motor-related potentials analyzed in context of decision-making."

### Potential Task 1: Choice Display ERP Analysis
- **Task Type**: exploratory
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 1.5 s, target_events = [`choice display`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `choice display` | 0 | Three-arm choice options displayed |
- **Kernel Notes**: The `choice display` events (12,464 trials) represent the moment when bandit arm options appear. This task lacks clear classification labels for supervised learning but supports exploratory ERP analysis (N2pc, stimulus-locked P3) or unsupervised clustering to identify choice-related neural states. Labels could be derived from subsequent `response: left/right arm` events post-hoc.
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "Choice display signals onset of three-armed bandit options; cued decision-making process analyzed via ERP components."

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
