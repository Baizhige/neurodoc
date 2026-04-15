# EEG: Probabilistic Learning with Affective Feedback: Exp #2

**Dataset**: `openneuro_ds003753` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003753
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 66 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A reinforcement learning task involving probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to affective stimulus properties. Participants made binary choices (left/right button) between cue stimuli (CUE) associated with positive or negative affective feedback images. Following each choice, an affective feedback image (FB) was presented. The study examines whether the RewP tracks reward value beyond mere monetary reward, responding to affective liking of feedback stimuli.

## File Scan Result

> **Kernel SHA256**: `e2608572e88c00dfd06594a0831242ad9e85ecf84b694cdf76063c550c4ec82b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 1000 | event | raw | Cue stimulus requiring binary choice |
| `S  2` | 999 | event | raw | Affective feedback stimulus (subtype 1) |
| `S  3` | 999 | event | raw | Affective feedback stimulus (subtype 2) |
| `S  4` | 999 | event | raw | Affective feedback stimulus (subtype 3) |
| `S 10` | 1933 | event | raw | Feedback or choice event subtype |
| `S 20` | 2064 | event | raw | Feedback or choice event subtype |
| `S101` | 1339 | event | raw | Cue stimulus subtype (positive valence) |
| `S102` | 660 | event | raw | Cue stimulus subtype (negative valence) |
| `S103` | 1385 | event | raw | Cue stimulus subtype |
| `S104` | 613 | event | raw | Cue stimulus subtype |
| `S110` | 573 | event | raw | Left button press response |
| `S111` | 517 | event | raw | Right button press response |
| `S120` | 594 | event | raw | Response subtype |
| `boundary` | 25 | event | raw | Data segment boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Affective Feedback Classification (Liked vs Disliked)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`S  2`, `S  3`, `S  4`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|---------|
  | `S  2`/`S  3`/`S  4` (liked) | 1 | Liked affective feedback (puppy images, positive valence) |
  | `S  2`/`S  3`/`S  4` (disliked) | 0 | Disliked affective feedback (chair/negative images, negative valence) |
- **Super Meta Notes**: Feedback event IDs (S  2, S  3, S  4 with ~999 events each) represent different affective feedback categories. Binary labels derived by decoding `trial_type` column in events.tsv metadata: puppies = liked (y=1), chair/negative images = disliked (y=0). RewP ERP measured 200-350ms post-feedback at Cz/FCz. Baseline correction: -200 to 0ms.
- **Evidence**:
  - DOI: 10.3758/s13415-021-00950-5 — Binary classification of feedback valence (liked/rewarding vs disliked/non-rewarding affective images) in probabilistic reinforcement learning task with EEG epochs time-locked to FB onset. N=25 subjects, 500Hz recording.
- **Kernel Notes**: Epoch alignment to feedback onset captures RewP component. Map raw event codes S  2/3/4 to FB semantic labels using events.tsv metadata cross-reference. Exclude boundary events (25 total) during continuous data processing. Verify liked/disliked mapping per event ID subtype.

### Normal Task 1: Probabilistic Selection Task (BIDS Publisher-defined)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`S  1`, `S101`-`S104`] (requires verification)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|---------|
  | `S  1` | TBD | Cue stimulus (binary choice left/right) |
  | `S101`-`S104` | TBD | Cue stimulus subtypes (requires events.tsv mapping) |
- **Super Meta Notes**: Publisher-defined BIDS task for probabilistic selection. CUE events likely map to S  1 (1000 events across 25 subjects ≈ 40 per subject) or S101-S104 cue subtypes. FB events map to S  2/3/4 (~999 each). Task parameters need verification from dataset README and events.tsv metadata mapping.
- **Evidence**:
  - DOI: 10.18112/openneuro.ds003753.v1.1.0 — OpenNeuro dataset version metadata.
  - DOI: 10.3758/s13415-021-00950-5 — Source publication describing probabilistic reinforcement learning paradigm.
- **Kernel Notes**: Map raw event codes to semantic labels: S  1 = CUE, S  2/3/4 = FB subtypes, S101-S104 = cue subtypes, S110/S111/S120 = response/feedback subtypes. Verify exact mapping via events.tsv. Reject STATUS events from epoching. Baseline: -200 to 0ms recommended for all epochs.

### Potential Task 1: Response-Related Potential Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S110`, `S111`, `S120`] (requires verification)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|---------|
  | `S110` | TBD | Left button press response |
  | `S111` | TBD | Right button press response |
  | `S120` | TBD | Response subtype (requires events.tsv mapping) |
- **Evidence**: Plausible from paradigm alone — documented Left/Right Button events in dataset description map to S110/S111/S120 codes. DOI required for definitive classification support.
- **Kernel Notes**: Response-locked epochs capture choice-related ERPs. Verify button mapping from events.tsv metadata. Exclude boundary events.

### Potential Task 2: Cue-Evoked Classification (Positive vs Negative Affective Cues)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`S  1`, `S101`-`S104`] (requires verification)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|----|---------|
  | `S  1`/`S101`-`S104` (positive cue) | TBD | Cue associated with positive feedback outcome |
  | `S  1`/`S101`-`S104` (negative cue) | TBD | Cue associated with negative feedback outcome |
- **Evidence**: Plausible from paradigm — probabilistic reinforcement learning task involves cues predicting feedback valence. DOI required for definitive cue classification evidence.
- **Kernel Notes**: Cue-locked epochs capture anticipatory ERP components (e.g., N200, P3a). Verify cue valence mapping from events.tsv trial_type column.