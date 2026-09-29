# Motor Imagery of Upper Limb Movements in Parkinson's Disease

**Dataset**: `ds004022` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Seven subjects with Parkinson's disease performed motor imagery tasks involving four right-upper limb movements: reaching, grasping, lifting, and twisting. Each subject completed three runs with 40 trials per run, following a structured trial sequence of 3s fixation cross, 4s visual cue, 3s ready state, and 5s motor imagery execution. EEG was recorded with 64 channels at 1000 Hz sampling rate, concurrently with fNIRS, for BCI decoding applications in a clinical population.

## File Scan Result

> **Kernel SHA256**: `d43095f05fb6439a5255dc17d37791958c5861634f4d131a503054c729c51a1a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `S  1` | 21 | admin | raw | Run/session start marker |
| `S  2` | 840 | event | raw | Trial onset marker |
| `S  3` | 210 | event | raw | Motor imagery task type marker (one of four right-upper limb movements: reaching, grasping, lifting, twisting) |
| `S  4` | 210 | event | raw | Motor imagery task type marker (one of four right-upper limb movements: reaching, grasping, lifting, twisting) |
| `S  5` | 210 | event | raw | Motor imagery task type marker (one of four right-upper limb movements: reaching, grasping, lifting, twisting) |
| `S  6` | 210 | event | raw | Motor imagery task type marker (one of four right-upper limb movements: reaching, grasping, lifting, twisting) |
| `S  7` | 840 | event | raw | Trial phase onset: fixation cross (3s) |
| `S  8` | 840 | event | raw | Trial phase onset: visual cue (4s) |
| `S  9` | 840 | event | raw | Trial phase onset: ready state (3s) |
| `S 10` | 840 | event | raw | Trial phase onset: motor imagery execution (5s) |
| `boundary` | 21 | admin | raw | Data boundary marker between runs |
| `condition 12` | 21 | admin | raw | Run boundary or condition block marker |

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Potential Task 1: 4-class right-upper limb motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, target_events = [`S 10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S  3` | 0 | reaching |
  | `S  4` | 1 | grasping |
  | `S  5` | 2 | lifting |
  | `S  6` | 3 | twisting |
- **Evidence**:
  - eeg.json TaskDescription — describes four right-upper limb MI tasks: reaching, grasping, lifting, and twisting
  - README — trial structure with 40 trials per run, 3s fixation + 4s visual cue + 3s ready state + 5s MI execution; S 10 marks 5s MI execution phase
  - Event count patterns — S 3-6 each appear 210 times (840 total trials / 4 task types), consistent with balanced 4-class design
- **Notes**: Epochs are anchored to S 10 (MI execution onset) with 0-5s window matching the 5-second MI execution phase described in README. The four motor imagery task types (S 3-S 6) serve as class labels. Specific mapping of S 3-S 6 to individual movements (reaching/grasping/lifting/twisting) could not be definitively confirmed due to inability to extract event latencies from binary .set files; y=0..3 assignment follows the numeric order of event codes.

### Potential Task 2: 4-class motor imagery from trial onset
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 15 s *, target_events = [`S  2`, `S  3`, `S  4`, `S  5`, `S  6`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S  3 | 0 | Reaching (right-upper limb motor imagery) |
  | S  4 | 1 | Grasping (right-upper limb motor imagery) |
  | S  5 | 2 | Lifting (right-upper limb motor imagery) |
  | S  6 | 3 | Twisting (right-upper limb motor imagery) |
- **Evidence**:
  - eeg.json — "four right-upper limb movements for MI tasks: reaching, grasping, lifting, and twisting"
  - README — trial structure: 3s fixation + 4s visual cue + 3s ready state + 5s MI execution = 15s total; 40 trials per run with four MI tasks in random order
  - Event count analysis — S 2=840 (trial onsets), S 3-S 6=210 each (840/4 task types), consistent with balanced 4-class design
- **Notes**: Task anchors on S 2 (trial onset marker) with tmin=0, but uses S 3-S 6 as the class labels since these markers appear at trial onset to indicate which of the four MI tasks will be performed. The 15s epoch captures the full trial including preparatory/anticipatory activity (fixation, cue, ready) through MI execution. Specific mapping of S 3-S 6 to reaching/grasping/lifting/twisting is not definitively confirmed due to inability to extract event latencies from binary .set files; the assignment above follows the natural ordering in the task description. S 2 serves as the epoch anchor; the co-occurring S 3-S 6 marker at trial onset provides the class label.

### Potential Task 3: Binary MI Task vs Rest (Fixation Baseline)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, target_events = [`S  7`, `S 10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S  7` | 0 | fixation cross (rest baseline, 3s) |
  | `S 10` | 1 | motor imagery execution (active task, first 3s) |
- **Evidence**:
  - events.json / README — trial structure: 3s fixation (S 7) + 4s cue (S 8) + 3s ready (S 9) + 5s MI execution (S 10); 40 trials × 3 runs × 7 subjects = 840 occurrences each of S 7 and S 10
  - eeg.json — TaskDescription confirms four right-upper limb MI tasks with EEG/fNIRS acquisition for BCI decoding
- **Notes**: Epochs truncated to 3s to match fixation duration with first 3s of MI execution, creating balanced-length rest vs active comparison for ERD/ERS detection in mu/beta bands. Full MI period is 5s but 3s was chosen per epoch_hint to balance classes; alternative would be 5s MI with 3s fixation yielding unequal epoch lengths.

### Potential Task 4: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | age | Continuous numeric age in years (48–83); used directly as regression target |
- **Evidence**:
- **Notes**: Segmentation-based epoching with 2-second windows and 50% overlap applied to continuous EEG recordings. Each subject's age from participants.tsv serves as the regression target for all segments derived from that subject's recordings, enabling brain-age prediction modeling from motor imagery EEG data.

### Potential Task 5: Years Since Diagnosis regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | Years Since Diagnosis | Continuous numeric value in years (range 6–73); directly used as regression target. Higher values indicate longer disease chronicity. |
- **Evidence**:
- **Notes**: B3 archetype — uses native participants.tsv column `Years Since Diagnosis` as continuous regression target. Segmentation epoching (2s windows, 50% overlap) applied to continuous EEG to predict disease duration from neural features during motor imagery. No kernel derivation needed; label is pre-existing in dataset metadata.

### Potential Task 6: Sex Classification from Motor Imagery EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | sex | M → 0 (male, n=3); F → 1 (female, n=4) |
- **Evidence**:
- **Notes**: Subject-level classification task using 2-second non-overlapping segmented windows of continuous EEG recorded during motor imagery. The label (sex) is drawn from participants.tsv, making this a B3 archetype with raw meta level. Near-balanced classes (3 male, 4 female) support binary classification. The kernel must read the `sex` field from participants.tsv and assign it to all epochs belonging to that subject.

### Potential Task 7: Hand Dominance Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | Hand Dominance | `R` → y=0 (right-handed, n=6); `L` → y=1 (left-handed, n=1). Severe class imbalance 6:1. |
- **Evidence**:
  - participants.tsv — Hand Dominance column: 6 subjects right-handed (R), 1 subject left-handed (L)
- **Notes**: Segmented windows (2s, 50% overlap) are used since no trial-locked epoching is appropriate for this subject-level demographic classification. The task predicts handedness from resting/task-continuing EEG patterns. Severe imbalance (6:1) makes this a challenging proof-of-concept task; stratified sampling or class weighting is recommended.

## Data Quality Notes

- Small sample size (n=7) limits generalizability and statistical power for machine learning models.
- All subjects have Parkinson's disease, which may introduce pathological EEG features (e.g., tremor artifacts, altered beta activity) distinct from healthy populations.
- Event code mapping for S 3-S 6 to specific movement types (reaching/grasping/lifting/twisting) is inferred from numeric ordering but not definitively confirmed due to inability to extract event latencies from binary .set files.
- Severe class imbalance in Task 7 (hand dominance: 6 right-handed vs 1 left-handed) makes reliable classification challenging.
- No known data quality issues regarding signal acquisition or file integrity.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
