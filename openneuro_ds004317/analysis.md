# Mood Manipulation and PST, Experiment 2

**Dataset**: `openneuro_ds004317` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004317
**Category**: High-level Mental | **Subjects**: 50 | **Files (Completed)**: 50
**Channels**: 66 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A reinforcement learning task (Probabilistic Selection Task) performed by participants following sad or happy mood manipulations. The paradigm mirrors Experiment 1 but compares sad and happy mood conditions rather than sad versus neutral. EEG was recorded to examine mood-dependent differences in reinforcement learning neural signatures.

## File Scan Result

> **Kernel SHA256**: `no_kernel`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 2073 | event | raw | Mood induction phase marker |
| `S  2` | 2084 | event | raw | Mood assessment/validation marker |
| `S  3` | 837 | event | raw | Practice phase stimulus marker |
| `S  4` | 840 | event | raw | Practice phase feedback marker |
| `S  5` | 49 | event | raw | Rest or fixation marker |
| `S  7` | 61 | event | raw | Inter-trial interval marker |
| `S  8` | 7126 | event | raw | Testing phase trial marker |
| `S  9` | 4813 | event | raw | Training phase trial marker |
| `S 12` | 196 | event | raw | Stimulus pair A/B presentation marker |
| `S 13` | 197 | event | raw | Stimulus pair A/C presentation marker |
| `S 14` | 196 | event | raw | Stimulus pair B/C presentation marker |
| `S 15` | 197 | event | raw | Response marker for pair A/B trials |
| `S 16` | 196 | event | raw | Response marker for pair A/C trials |
| `S 21` | 196 | event | raw | Feedback marker for pair A/B (80% correct) |
| `S 23` | 196 | event | raw | Feedback marker for pair A/C (80% correct) |
| `S 24` | 196 | event | raw | Feedback marker for pair B/C (80% correct) |
| `S 25` | 196 | event | raw | Feedback marker for pair A/B (70% correct) |
| `S 26` | 196 | event | raw | Feedback marker for pair A/C (70% correct) |
| `S 31` | 197 | event | raw | Feedback marker for pair B/C (70% correct) |
| `S 32` | 196 | event | raw | Response marker for pair B/C trials |
| `S 34` | 196 | event | raw | Correct feedback marker (pair A/B) |
| `S 35` | 196 | event | raw | Correct feedback marker (pair A/C) |
| `S 36` | 196 | event | raw | Correct feedback marker (pair B/C) |
| `S 41` | 196 | event | raw | Incorrect feedback marker (pair A/B) |
| `S 42` | 196 | event | raw | Incorrect feedback marker (pair A/C) |
| `S 43` | 196 | event | raw | Incorrect feedback marker (pair B/C) |
| `S 45` | 196 | event | raw | Outcome marker for pair A/B |
| `S 46` | 196 | event | raw | Outcome marker for pair A/C |
| `S 51` | 196 | event | raw | Outcome marker for pair B/C |
| `S 52` | 196 | event | raw | Stimulus category marker |
| `S 53` | 196 | event | raw | Stimulus category marker |
| `S 54` | 196 | event | raw | Stimulus category marker |
| `S 56` | 196 | event | raw | Response outcome category marker |
| `S 61` | 196 | event | raw | Outcome category marker |
| `S 62` | 196 | event | raw | Outcome category marker |
| `S 63` | 197 | event | raw | Outcome category marker |
| `S 64` | 196 | event | raw | Outcome category marker |
| `S 65` | 196 | event | raw | Outcome category marker |
| `S 85` | 1 | event | raw | System status marker (admin) |
| `S101` | 4290 | event | raw | Stimulus onset marker (stimulus pair presented) |
| `S102` | 4374 | event | raw | Stimulus onset marker (stimulus pair presented) |
| `S103` | 1600 | event | raw | Stimulus onset marker |
| `S104` | 1675 | event | raw | Stimulus onset marker |
| `S105` | 61 | event | raw | Stimulus marker (practice/pilot) |
| `S116` | 2000 | event | raw | Feedback onset for stimulus pair 1 (reward condition) |
| `S125` | 2000 | event | raw | Feedback onset for stimulus pair 2 (reward condition) |
| `S134` | 2000 | event | raw | Feedback onset for stimulus pair 3 (reward condition) |
| `S143` | 2000 | event | raw | Feedback onset for stimulus pair 1 (punishment condition) |
| `S152` | 2000 | event | raw | Feedback onset for stimulus pair 2 (punishment condition) |
| `S161` | 2000 | event | raw | Feedback onset for stimulus pair 3 (punishment condition) |
| `S191` | 1 | event | raw | System status marker (admin) |
| `S201` | 25 | event | raw | Response marker (button press) |
| `S202` | 25 | event | raw | Response marker (button press) |
| `S203` | 25 | event | raw | Response marker (button press) |
| `S204` | 25 | event | raw | Response marker (button press) |
| `S205` | 201 | event | raw | Response marker (button press) |
| `S211` | 25 | event | raw | Response marker (button press) |
| `S212` | 25 | event | raw | Response marker (button press) |
| `S213` | 25 | event | raw | Response marker (button press) |
| `S214` | 25 | event | raw | Response marker (button press) |
| `S255` | 2 | event | raw | Calibration or system marker |
| `boundary` | 51 | event | raw | Recording discontinuity marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Feedback Outcome Classification (Reward vs Punishment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 6.0 s, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` (trial_type=correct) | 0 | Reward feedback (positive outcome) |
  | `FB` (trial_type=incorrect) | 1 | Punishment feedback (negative outcome) |
- **Evidence**:
  - DOI: 10.1111/psyp.14276 — Uses OpenNeuro dataset ds004317 (Experiment 2, N=50) to examine how mood induction affects Reward Positivity (RewP) and reward learning during a probabilistic selection task, epoching EEG data from -2000 to 6000 ms around feedback onset and classifying correct vs incorrect feedback trials.
- **Kernel Notes**: Raw trigger codes S116/S125/S134/S143/S152/S161 (2000 each) map to FB events across stimulus pairs. The trial_type column in events.tsv provides Correct/Incorrect sub-label distinction for binary classification. Baseline correction from -200 to 0 ms before feedback onset. Build version-controlled trigger decoding table before epoching. STATUS events (S85, S191) are administrative markers—exclude from analysis.

### Potential Task 1: Stimulus-Response Locking Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`STIM`, `RESP`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `STIM` | 0 | Stimulus onset (stimulus pair presented) |
  | `RESP` | 1 | Participant button-press response |
- **Evidence**: No direct DOI reference; task supported by paradigm plausibility. Epoch alignment recommendations suggest mood-dependent differences in perceptual processing and motor preparation are examinable via stimulus and response locking.
- **Kernel Notes**: S101-S105 (stimulus markers) and S201-S214 (response markers, 25 each) map to STIM and RESP events respectively. Optional secondary analysis to complement the primary RewP/feedback-locked analysis. Could support mood classification (sad vs happy) as exploratory extension.

### Potential Task 2: Mood State Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s (relative to mood-relevant events), target_events = [`STIM`, `FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `STIM` | 0 | Sad mood condition trials |
  | `FB` | 1 | Happy mood condition trials |
- **Evidence**: No direct DOI reference; supported by partial evidence from DOI 10.1111/psyp.14276 which contrasts happy vs sad mood conditions during the reinforcement learning task.
- **Kernel Notes**: Paradigm explicitly compares sad vs happy mood states following mood induction. Mood state may modulate neural responses across multiple temporal windows (stimulus processing, response preparation, feedback evaluation). Requires events.tsv metadata for condition labeling.

### Normal Task 1: Feedback Timing Analysis
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` (S116) | 0 | Feedback from stimulus pair A |
  | `FB` (S125) | 1 | Feedback from stimulus pair B |
  | `FB` (S134) | 2 | Feedback from stimulus pair C |
- **Evidence**: Indirect evidence only; supported by paradigm structure where participants learn stimulus-outcome associations across multiple pairs.
- **Kernel Notes**: S116-S161 events likely encode different stimulus pairs with varying reinforcement probabilities. Examining neural responses by pair could reveal differential learning rates. TESTING events (S  8, 7126 total) may contain additional sub-label information in events.tsv trial_type column.