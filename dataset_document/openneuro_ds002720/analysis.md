# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2018 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 18 | **Files (Completed)**: 165 | **Channels**: 19 | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants used EEG self-regulation to control the tempo of music in a tempo-based brain-computer music interface (BCMI). One condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. Each labeled event spans a full 20-second music clip interval. The dataset contains multiple runs per participant.

## File Scan Result

> **Kernel SHA256**: `59196c175ac3d8d41fdc5ed8d3a687afd6a5cc92ebd61dca68083721485beae3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1` | 1275 | event | raw | Lower alpha condition: participants are instructed to lower their alpha levels to modulate the tempo of music |
| `2` | 1250 | event | raw | Raise alpha condition: participants are instructed to increase their alpha levels to modulate the tempo of music |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 2-class alpha-state BCMI classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `1` | 0 | Lower alpha condition |
  | `2` | 1 | Raise alpha condition |
- **Evidence**:
  - sub-01_task-run2_events.json — defines event `1` as `Lower alpha` and event `2` as `Raise alpha`
  - README — states that the dataset contains EEG from a music-based BCI in which participants intentionally modulated music tempo, and that each music clip is 20 s long
  - events.tsv scan — confirms 2525 total labeled events across the dataset, with 1275 instances of `1` and 1250 instances of `2`
- **Notes**: This is the most direct task supported by the released BIDS event metadata. All non-empty events have duration exactly 20 s, so long-event decoding over the full labeled interval is the most natural formulation. This task should take precedence over demographic segmentation tasks because it reflects the actual experimental manipulation.

### Potential Task 1: sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — sex field complete for all 18 subjects with class imbalance (M=14, F=4)
- **Notes**: Continuous EEG segmentation (4s windows, 50% overlap) applied across all BCMI runs per subject. Binary classification of subject sex from resting/task-continuous EEG. Class imbalance present (M=14, F=4 out of 18 subjects). The segment_length and overlap values are standard defaults for continuous EEG segmentation with no task-specific reference guidance. This is a weak subject-trait task compared with the explicit alpha-state labels available in the event tables.

### Potential Task 2: Binned-Age Classification from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — age column complete for N=18, range 18–28, sample values [23, 24, 28, 20, 19, 26, 20]
- **Notes**: The kernel must derive binary binned labels from the native age field using a median split at approximately 22–23 years (median of 18–28 range ≈ 23). This is a derived classification variant of the continuous age regression task; the kernel discretizes the continuous age into two balanced classes for segment-level classification. Segmentation produces fixed-length windows with 50% overlap; no event alignment is used. This remains an auxiliary demographic task, not the core BCMI task.

## Data Quality Notes

- Twenty-two event files are empty (no events recorded), leaving 143 files with usable event data.
- Non-empty event files do contain valid event labels: trial_type `1` (Lower alpha) and `2` (Raise alpha), with 2525 total labeled events across the dataset.
- Device metadata is completely missing from the dataset; equipment information must be inferred from other sources.
- There is a discrepancy in subject count between the metadata (18 subjects) and dataset_description.json which mentions 19 healthy participants.
- Class imbalance is present in sex classification (14 male, 4 female), which may affect model training and evaluation.
- All non-empty events have duration exactly 20 s, matching the README description that each music clip lasts 20 s.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
