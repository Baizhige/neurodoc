# Meditation Expertise and Mind Wandering

**Dataset**: `openneuro_ds001787` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 24 | **Channels**: 64 | **Sampling Rate**: 2048 Hz | **Manual Review**:

## Paradigm

Twenty-four subjects (12 meditation experts, 12 novices) participated in a continuous meditation task while 64-channel EEG was recorded using a BIOSEMI ActiveTwo amplifier. During meditation, subjects were interrupted approximately every 2 minutes by probe questions to self-report their level of concentration and mind-wandering using a 3-response scale. The paradigm combines sustained attention/meditation states with intermittent self-report probes, enabling analysis of both meditation-related neural activity and metacognitive awareness of attentional states.

## File Scan Result

> **Kernel SHA256**: `400231ef4729d465a3cd37073c29c02ea3e4a1774941918a88f1ddae4582756c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `128` | 983 | event | raw |  |
| `16` | 2 | event | raw |  |
| `2` | 1131 | event | raw |  |
| `254` | 5 | event | raw |  |
| `4` | 754 | event | raw |  |
| `8` | 258 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Available in participants.tsv; sample values: 32, 35, 41, 29, 34 |
| `amplifier` | missing | BIOSEMI ActiveTwo |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing | Available in participants.tsv as 'gender' column; values: M, F |

## Tasks

### Potential Task 1: 3-class meditation response
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`2`, `4`, `8`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `2` | 0 | Response 1 (subject response to probe question) |
  | `4` | 1 | Response 2 (subject response to probe question) |
  | `8` | 2 | Response 3 (subject response to probe question) |
- **Evidence**:
  - task-meditation_events.json — defines values 2, 4, 8 as Response 1, Response 2, Response 3 to probe questions about concentration and mind-wandering levels
  - events.tsv samples (sub-001, ses-01) — values 2, 4, 8 consistently appear with trial_type='response'
  - README — subjects interrupted every ~2 minutes during meditation to indicate concentration and mind-wandering levels
- **Notes**: Response-locked epochs for meditation probe responses. The three response options represent subject self-reports of concentration/mind-wandering states. Event 128 (stimulus/question onset) is excluded as it is the probe interruption, not the response. Events 16 (involuntary response, n=2 globally) and 254 (undefined admin marker, n=4 globally) are excluded due to rarity and non-experimental status.

### Potential Task 2: Meditation State vs Probe Interruption
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1 s *, tmax = 3 s *, target_events = [`128`, `2`, `4`, `8`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `128` | 0 | Probe interruption onset (first question) — meditation interruption event |
  | `2` | 1 | Response 1 (to probe question) — post-interruption response state |
  | `4` | 1 | Response 2 (to probe question) — post-interruption response state |
  | `8` | 1 | Response 3 (to probe question) — post-interruption response state |
- **Evidence**:
  - task-meditation_events.json — Value 128 defined as "First question onset (most important marker)" with trial_type "stimulus"; values 2, 4, 8 defined as responses with trial_type "response"
  - sub-001_ses-01_task-meditation_events.tsv — Confirmed pattern: 128 events alternate with 2/4/8 response events every ~2 minutes during continuous recording
  - README — "Subjects were meditating and were interrupted about every 2 minutes to indicate their level of concentration and mind wandering"
- **Notes**: This task contrasts the probe interruption state (y=0, event 128) against response states following interruption (y=1, events 2/4/8 merged). True "ongoing meditation" epochs without interruption markers are not directly available as event-locked targets; the continuous meditation state between probes would require segmentation (not implemented here). The merged y=1 class captures the post-probe cognitive engagement period rather than pure uninterrupted meditation. Event 16 (involuntary response, n=2 globally) and event 254 (undefined admin marker, n=4) are excluded due to extreme rarity. All epoch parameters are inferred from the ~2 minute inter-probe interval and typical ERP analysis windows for stimulus-locked responses.

### Potential Task 3: Expert vs Novice Meditator Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | group | 0=expert, 1=novice (binary classification from participants.tsv 'group' column) |
- **Evidence**:
- **Notes**: Continuous meditation EEG segmented into 30-second windows. No trial structure exists for the expertise contrast; the 'group' column in participants.tsv provides subject-level binary labels (expert/novice, N=12 each). Segment length and overlap inferred from Category SKILL defaults for naturalistic continuous paradigms.

### Potential Task 4: Age Regression from Meditation EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 30 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Numeric age in years (29–78). One subject (sub-024) missing age data; must be excluded. Values used directly as regression target. |
- **Evidence**:
  - participants.tsv — Contains 'age' column with numeric values ranging 29-78; completeness 23/24 subjects (sub-001 through sub-023)
  - eeg.json — RecordingType=continuous, TaskName=meditation, supports segmentation approach for continuous meditation recordings
  - README — Describes continuous meditation paradigm with ~2-minute probe interruptions; EEG recorded during sustained meditation
- **Notes**: Segmentation-based epoching appropriate for continuous meditation EEG without trial-boundary events. 30-second segments with no overlap chosen as default for continuous resting-state-like paradigms. Age prediction from EEG is a well-established neurodevelopmental/neuroaging benchmark; the meditation context provides a controlled cognitive state. One subject with missing age must be excluded at the kernel level.

### Potential Task 5: Gender Classification from Meditation EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | gender | 0 = 'F' (female), 1 = 'M' (male); binary classification from participants.tsv |
- **Evidence**:
  - participants.tsv — 'gender' column with complete data: 12 'M' and 12 'F' across 24 subjects
- **Notes**: Segmentation-based epoching used for continuous meditation EEG; 30-second non-overlapping segments with label assigned per-subject from participants.tsv gender field. Task treats subject-level demographic as classification target from resting-state-like continuous neural activity.

### Potential Task 6: Meditation Segmentation with Group Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | group | `expert` → y=0, `novice` → y=1 |
- **Evidence**:
- **Notes**: Segmentation-based task for continuous naturalistic meditation recording. The entire continuous EEG is divided into 30-second non-overlapping segments. Each segment inherits the subject-level group label from participants.tsv (expert/novice), creating a subject-stratified classification problem. No trial structure is used for epoching since the paradigm is continuous with only intermittent probe interruptions (~2 min) that do not define meaningful task epochs.

## Data Quality Notes

- Event counts are highly imbalanced across response types: event 2 (n=1131) vs event 8 (n=258), which may bias classification toward the dominant response class.
- Event 16 appears only twice globally across all subjects, suggesting possible recording artifact or exceptional involuntary response; excluded from all tasks.
- Event 254 (admin marker, n=5 globally) is undefined in task documentation and excluded from analysis.
- Age data is missing for one subject (sub-024), requiring explicit exclusion for age regression tasks.
- Metadata fields (age, sex, amplifier, cap, handedness) are not embedded in raw EEG headers and must be retrieved from participants.tsv and sidecar files.
- High sampling rate (2048 Hz) will require downsampling for efficient processing; original recordings are continuous with no explicit trial boundaries.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
