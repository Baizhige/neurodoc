# EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants

**Dataset**: `openneuro_ds004515` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004515
**Category**: High-level Mental | **Subjects**: 54 | **Files (Completed)**: 54 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants (light and heavy drinkers) performed a reinforcement learning task involving alcohol-related and neutral imagery cues. On each trial, participants chose between left and right buttons in response to cues, with feedback indicating correct/incorrect responses. The study investigates how reward learning interacts with alcohol cue reactivity across drinking groups, with difficulty (easy/hard) and stimulus type (puppy/alcohol) as manipulated factors.

## File Scan Result

> **Kernel SHA256**: `181607f103ff9acae9f17f4264a3c7c7c0e7e5bde25fcaccd0f5b919e3313de1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | 33945 | event | raw | Trial phase onset: cue/fixation period |
| `Response` | 1373 | event | raw | Participant response (button press) |
| `S 10` | 498 | event | raw | Left button press response |
| `S 11` | 240 | event | raw | Trial phase onset: stimulus presentation (condition 1) |
| `S 12` | 240 | event | raw | Trial phase onset: stimulus presentation (condition 2) |
| `S 13` | 240 | event | raw | Trial phase onset: stimulus presentation (condition 3) |
| `S 14` | 240 | event | raw | Trial phase onset: stimulus presentation (condition 4) |
| `S 20` | 462 | event | raw | Right button press response |
| `S101` | 318 | event | raw | Feedback onset: reward, easy puppy condition |
| `S102` | 162 | event | raw | Feedback onset: punishment, easy puppy condition |
| `S103` | 312 | event | raw | Feedback onset: reward, easy alcohol condition |
| `S104` | 168 | event | raw | Feedback onset: punishment, easy alcohol condition |
| `S110` | 136 | event | raw | Feedback onset: reward, hard puppy condition |
| `S111` | 126 | event | raw | Trial phase onset: fixation/stimulus period (general status marker) |
| `S120` | 147 | event | raw | Feedback onset: punishment, hard puppy condition |
| `S200` | 480 | event | raw | Feedback onset: reward, hard alcohol condition |
| `S201` | 480 | event | raw | Feedback onset: punishment, hard alcohol condition |
| `boundary` | 54 | admin | raw | Recording boundary / data segment marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Reward vs Punishment Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S101`, `S102`, `S103`, `S104`, `S110`, `S120`, `S200`, `S201`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S101 | 1 | reward, easy puppy condition |
  | S102 | 0 | punishment, easy puppy condition |
  | S103 | 1 | reward, easy alcohol condition |
  | S104 | 0 | punishment, easy alcohol condition |
  | S110 | 1 | reward, hard puppy condition |
  | S120 | 0 | punishment, hard puppy condition |
  | S200 | 1 | reward, hard alcohol condition |
  | S201 | 0 | punishment, hard alcohol condition |
- **Evidence**:
  - 10.1016/j.pscychresns.2023.111685 — Primary paper defines 2-class reward vs punishment classification using RewP component; corrected event mapping from locked meanings uses S101/S103/S110/S200 for reward and S102/S104/S120/S201 for punishment across all easy/hard × puppy/alcohol feedback conditions
- **Notes**: The original reference paper used incorrect event codes (S 10/S 12 vs S 11/S 13). The locked ground truth from events.tsv and task code reveals the actual feedback markers are S101-S104, S110, S120, S200-S201, which encode 8 conditions of reward/punishment × easy/hard × puppy/alcohol. Reward conditions (S101, S103, S110, S200) are merged to y=1; punishment conditions (S102, S104, S120, S201) are merged to y=0 for binary classification of feedback valence.

### Classical Task 2: reward vs punishment feedback classification (easy conditions only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s, tmax = 1.0 s, target_events = [`S101`, `S102`, `S103`, `S104`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S101 | 0 | reward, easy puppy condition |
  | S102 | 1 | punishment, easy puppy condition |
  | S103 | 0 | reward, easy alcohol condition |
  | S104 | 1 | punishment, easy alcohol condition |
- **Evidence**:
  - 10.1016/j.pscychresns.2023.111685 — Primary reference describing the 4-condition structure (Rew Pup, Pun Pup, Rew Alc, Pun Alc) for easy difficulty; N=630 reward trials (S101+S103) and N=330 punishment trials (S102+S104)
- **Notes**: Reward conditions (S101, S103) merged to y=0 and punishment conditions (S102, S104) merged to y=1 to create a binary reward vs punishment classification on easy difficulty trials only. This collapses across stimulus category (puppy/alcohol) while preserving the valence dimension of feedback.

### Classical Task 3: reward vs punishment feedback classification (hard conditions only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s, tmax = 1.0 s, target_events = [`S110`, `S120`, `S200`, `S201`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S110 | 0 | reward, hard puppy condition |
  | S200 | 0 | reward, hard alcohol condition |
  | S120 | 1 | punishment, hard puppy condition |
  | S201 | 1 | punishment, hard alcohol condition |
- **Evidence**:
  - 10.1016/j.pscychresns.2023.111685 — reward vs punishment feedback classification restricted to hard difficulty trials; S110/S200 (reward) and S120/S201 (punishment) with balanced classes for hard conditions only
- **Notes**: Merges two reward events (S110 hard puppy, S200 hard alcohol) into y=0 and two punishment events (S120 hard puppy, S201 hard alcohol) into y=1, collapsing across stimulus domain (puppy/alcohol) to focus on valence classification at hard difficulty only. This contrasts with the full feedback classification that includes easy conditions (S101-S104).

### Potential Task 1: Left vs Right Button Press Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`S 10`, `S 20`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 10` | 0 | Left button press response |
  | `S 20` | 1 | Right button press response |
- **Evidence**:
  - events.tsv (sub-001, sub-002, sub-003, sub-015) — `S 10` confirmed as Left Button response
  - events.tsv (sub-010, sub-020) — `S 20` confirmed as Right Button response
  - events.json — trigger code definitions with value field containing event markers
  - README — describes ProbabilisticSelection reinforcement learning task with button press responses
- **Notes**: Motor response ERP classification using confirmed left/right button press markers. Epoch window centered on response onset (-500ms to +500ms) is standard for capturing lateralized readiness potential and motor-related EEG asymmetries. Classes are approximately balanced (S 10: N=498, S 20: N=462).

### Potential Task 2: Stimulus Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 1 s *, target_events = [`S 11`, `S 12`, `S 13`, `S 14`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 11` | 0 | easy puppy |
  | `S 12` | 1 | hard puppy |
  | `S 13` | 2 | easy alcohol |
  | `S 14` | 3 | hard alcohol |
- **Evidence**:
- **Notes**: 4-class classification of stimulus presentation conditions. Event IDs S 11-S 14 correspond to the four experimental conditions based on task code (TrnBlock.m) showing stim values 1-4 sent via io64, with feedback markers (S101-S104, S110, S120, S200-S201) confirming the 2×2×2 structure (easy/hard × puppy/alcohol × reward/punishment). N=240 trials per condition yields perfectly balanced classes. Epoch window 0-1s covers initial visual processing and early emotional response to imagery cues.

### Potential Task 3: alcohol vs neutral stimulus classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 1 s *, target_events = [`S 11`, `S 12`, `S 13`, `S 14`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 11` | 0 | neutral stimulus (puppy, easy condition) |
  | `S 12` | 0 | neutral stimulus (puppy, hard condition) |
  | `S 13` | 1 | alcohol stimulus (easy condition) |
  | `S 14` | 1 | alcohol stimulus (hard condition) |
- **Evidence**:
- **Notes**: Two-class simplification merging difficulty levels: S 11/S 12 (conditions 1/2, puppy/neutral cues) → y=0, S 13/S 14 (conditions 3/4, alcohol cues) → y=1. Tests core alcohol cue reactivity effect. Epoch window 0-1s locked to stimulus onset; parameters inferred from 4-class version with same paradigm structure.

### Potential Task 4: sex classification from resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | subject_sex | F → 0 (female); M → 1 (male) |
- **Evidence**:
  - participants.tsv — N=54 subjects with sex field (F=32, M=22), complete coverage
- **Notes**: Segmentation-based classification using 2-second non-overlapping windows from continuous EEG. The sex label is drawn from participants.tsv (native info column), making this a B3 archetype with raw meta level. No kernel derivation needed.

### Potential Task 5: drinking group × feedback interaction: reward sensitivity
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s, tmax = 1.0 s, target_events = [`S101`, `S102`, `S103`, `S104`, `S110`, `S120`, `S200`, `S201`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S101 | 0 | Feedback onset: reward, easy puppy condition |
  | S102 | 1 | Feedback onset: punishment, easy puppy condition |
  | S103 | 0 | Feedback onset: reward, easy alcohol condition |
  | S104 | 1 | Feedback onset: punishment, easy alcohol condition |
  | S110 | 0 | Feedback onset: reward, hard puppy condition |
  | S120 | 1 | Feedback onset: punishment, hard puppy condition |
  | S200 | 0 | Feedback onset: reward, hard alcohol condition |
  | S201 | 1 | Feedback onset: punishment, hard alcohol condition |
- **Evidence**:
  - events.tsv samples across subjects (sub-001, sub-002, sub-003, sub-010, sub-013, sub-015, sub-020, sub-025) — confirms S101-S104, S110, S120, S200-S201 as feedback onset markers with systematic reward/punishment × easy/hard × puppy/alcohol structure
  - sub-001_task-ProbabilisticSelection_eeg.set header annotations — S101, S102, S103, S104, S110, S120, S200, S201 appear as actual trigger codes in EEG data
  - README and dataset_description.json — confirms study design comparing hazardous drinkers (ALC) vs controls (CTL) with reward positivity (RewP) as primary neural measure
- **Notes**: This task collapses all reward conditions (S101/S103/S110/S200 → y=0) versus all punishment conditions (S102/S104/S120/S201 → y=1) to enable group-level comparison of reward sensitivity. The GROUP variable from participants.tsv (CTL vs ALC) would serve as stratification or covariate in downstream analysis, reflecting the dataset's primary theoretical focus on how reward positivity differs between hazardous drinkers and controls. The epoch window (-0.5 to 1.0 s) captures the feedback-locked ERP including the reward positivity component peaking ~250-350 ms post-feedback.

## Data Quality Notes

- Subject count discrepancy: Existing draft reports 42 subjects but File Scan Result shows 54 subjects (N=54 confirmed in participants.tsv with complete GROUP, BDI, AUDIT, EDUCATION fields).
- Event meaning corrections: The File Scan Result reveals substantially different event meanings than the original draft (e.g., `S 10`/`S 20` are left/right button presses, not reward/punishment feedback; `S 11`-`S 14` are stimulus presentation conditions, not feedback variants).
- Feedback markers reidentified: True feedback markers are S101-S104, S110, S120, S200-S201 (not S 10/S 11/S 12/S 13 as in original draft), encoding 8 conditions of reward/punishment × easy/hard × puppy/alcohol.
- High CUE event count (33,945) suggests this marker may indicate trial phase onset at a finer granularity (e.g., fixation/cue period) rather than individual trials; verify against actual trial count.
- `device` field is missing in info completeness table.
- `boundary` events (N=54) match subject count, suggesting one segmentation boundary per subject; verify if these indicate concatenated runs or preprocessing artifacts.
- Event count imbalance: Some feedback conditions have unequal trials (e.g., S101=318 vs S102=162 for easy puppy; S110=136 vs S200=480 for hard conditions), which may affect classification performance.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
