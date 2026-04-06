# Reward Biases Spontaneous Neural Reactivation During Sleep

**Dataset**: `openneuro_ds003574` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003574
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 17
**Channels**: 69 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played two rewarded and non-rewarded video games (FACE and MAZE) followed by a nap sleep session recorded with simultaneous EEG-fMRI. The study examines whether reward enhances spontaneous neural reactivation of game-related memory traces during sleep. Brain patterns from waking gameplay are decoded and compared to sleep activity to identify replay events. EEG event structure consists of BrainVision numeric S-code triggers from the game paradigm with limited per-file occurrence.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1`-`S 27` | 1 each | event | raw | BrainVision stimulus triggers (game/task events) |
| `R128` | 1 | event | raw | BrainVision response trigger |
| `Sync On` | 1 | event | raw | MRI/EEG synchronization marker |
| `R` | 1 | admin | raw | Generic response marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Sleep Brain State Classification (Reward vs No-Reward Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60.0 s, overlap = 0.0, target_events = [`face_game`, `maze_game`, `rest`, `pre_face`, `pre_maze`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `face_game` | 0 | Face game playing (60s block) - rewarded condition |
  | `maze_game` | 1 | Maze game playing (60s block) - non-rewarded condition |
  | `rest` | 2 | Rest periods (90s block) |
  | `pre_face` | 3 | 3s before face game onset |
  | `pre_maze` | 4 | 3s before maze game onset |
- **Super Meta Notes**: Derived from raw BrainVision trigger events (`S 1`-`S 27`) by CRF classifier trained on fMRI data during wake game session, then applied to sleep fMRI/EEG to obtain brain state likelihoods. Kernel step: Apply pre-trained CRF model to EEG spectral features (4s epochs, 2s overlap) during sleep periods to classify into 5 brain states; map to reward (face game = won) vs no-reward (maze game = lost) labels for replay analysis.
- **Evidence**:
  - DOI: 10.1038/s41467-021-24357-5 — Conditional Random Fields classifier decoded brain states during sleep, showing privileged reactivation of reward-associated game patterns during N3 sleep.
- **Kernel Notes**: Verify event ID mapping from events.tsv. Raw trigger mapping: `S 1`-`S 13` → face_game, `S 14`-`S 27` → maze_game, `R` → rest. Use 4s EEG epochs with 2s overlap for feature extraction (EEG power bands). Requires pre-trained classifier weights from paper for inference on sleep EEG.

### Potential Task 1: Continuous sleep EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null (no label, suitable for unsupervised analysis))
- **Notes**: Only 1 occurrence per event type per file - insufficient for epoch-based classification. Dataset is primarily suited for EEG-fMRI sleep replay analysis using pattern decoding, not standard ERP epoching. The 17 completed files (of 18 subjects) are sleep EEG recordings.

### Potential Task 2: Sleep stage classification (20s windows)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`sleep_stage_n1`, `sleep_stage_n2`, `sleep_stage_n3`, `sleep_stage_rem`, `sleep_stage_wake`] *
- **Label Route**: `event`
- **Target Definition**: Standard 5-class sleep staging from EEG
- **Notes**: Paper mentions 20s windows for sleep staging; requires hypnogram annotation or external sleep stage labels. (replaces Classical Task 1-3 from original analysis.md which had "Needs verification" parameters)

## Data Quality Notes

- Very sparse event structure; each trigger type appears only once per recording.
- EEG-fMRI simultaneous recording; gradient artifact and MRI-related noise present.
- Primary analysis requires decoding waking neural patterns and cross-correlating with sleep activity.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review