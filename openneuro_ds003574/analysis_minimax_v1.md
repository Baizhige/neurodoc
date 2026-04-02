# Reward Biases Spontaneous Neural Reactivation During Sleep

**Dataset**: `openneuro_ds003574` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003574
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 17
**Channels**: 69 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played two rewarded and non-rewarded video games (FACE and MAZE) followed by a nap sleep session recorded with simultaneous EEG-fMRI. The study examines whether reward enhances spontaneous neural reactivation of game-related memory traces during sleep. Brain patterns from waking gameplay are decoded and compared to sleep activity to identify replay events. EEG event structure consists of BrainVision numeric S-code triggers from the game paradigm with limited per-file occurrence.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003574

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1`-`S 27` | 1 each | short | raw | BrainVision stimulus triggers (game/task events) |
| `R128` | 1 | short | raw | BrainVision response trigger |
| `Sync On` | 1 | short | raw | MRI/EEG synchronization marker |
| `R` | 1 | admin | raw | Generic response marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 1`, `S 27`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Brain State Classification (Wake Game vs Rest)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `face_game` | 0 | Face game playing (60 s blocks) |
  | `maze_game` | 1 | Maze game playing (60 s blocks) |
  | `rest` | 2 | Rest periods (90 s blocks) |
  | `pre_face` | 3 | 3 s before face game onset |
  | `pre_maze` | 4 | 3 s before maze game onset |
- **Super Meta Notes**: Labels are derived from a Conditional Random Fields (CRF) classifier trained on fMRI data during wake game sessions. The classifier decodes brain states (face_game, maze_game, rest) from EEG power features (4s epochs, 2s overlap). For sleep reactivation analysis, these state labels are mapped to reward (won game) vs. no-reward (lost game) based on experimental manipulation.
- **Evidence**:
  - DOI: 10.1038/s41467-021-24357-5 — This study used simultaneous EEG-fMRI to record participants playing face and maze games, then applied a Conditional Random Fields classifier trained on fMRI data to decode brain states during subsequent sleep, showing privileged reactivation of reward-associated game patterns during N3 sleep.
- **Kernel Notes**: Extract EEG power features using 4s Hann windows with 2s overlap. Apply pre-trained CRF decoder to obtain brain state probabilities for each epoch. Map game states to reward/no-reward labels for sleep reactivation analysis.

### Primary Task 2: Sleep Brain State Reactivation Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 20.0 s *, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `reward_reactivation` | 0 | Brain state matching rewarded game (face or maze) |
  | `no_reward_reactivation` | 1 | Brain state matching non-rewarded game |
  | `rest_state` | 2 | Baseline sleep state |
- **Super Meta Notes**: During sleep, the same CRF classifier is applied to fMRI (and EEG) data to decode brain states. The decoded states are then analyzed for privileged reactivation of reward-associated game patterns (won games) vs. non-reward patterns (lost games).
- **Evidence**:
  - DOI: 10.1038/s41467-021-24357-5 — This study used simultaneous EEG-fMRI to record participants playing face and maze games, then applied a Conditional Random Fields classifier trained on fMRI data to decode brain states during subsequent sleep, showing privileged reactivation of reward-associated game patterns during N3 sleep.
- **Kernel Notes**: Apply CRF decoder to sleep EEG epochs (20s windows for sleep staging). Compute reactivation strength for reward vs. no-reward conditions. Compare N2/N3 sleep stages for significant differences.

### Normal Task 1: Continuous sleep EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no label, suitable for unsupervised analysis))
- **Notes**: Only 1 occurrence per event type per file - insufficient for epoch-based classification. Dataset is primarily suited for EEG-fMRI sleep replay analysis using pattern decoding, not standard ERP epoching. The 17 completed files (of 18 subjects) are sleep EEG recordings.

## Data Quality Notes

- Very sparse event structure; each trigger type appears only once per recording.
- EEG-fMRI simultaneous recording; gradient artifact and MRI-related noise present.
- Primary analysis requires decoding waking neural patterns and cross-correlating with sleep activity.

## References

- **Reference**: `Reward biases spontaneous neural reactivation during sleep. Nature Communications, 2021.`
