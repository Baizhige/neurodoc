# EEG Meditation Study

**Dataset**: `openneuro_ds001787` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz
**Manual Review**:

## Paradigm

Twenty-four meditators (12 expert with ≥10 years daily practice, 12 novices) engaged in sustained meditation sessions continuously recorded at 256 Hz. Approximately every two minutes, a brief probe interrupted the session to assess concentration level or mind-wandering, with subjects providing button-press responses. The study examines neural correlates of sustained attention, including infraslow activity coupled with autonomic markers like galvanic skin response.

## File Scan Result

> **Kernel SHA256**: `c2f5e3496c7fe9b280a9e19cb8b15b2644d16929c032a559162b6fd52167787f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_128` | 983 | event | raw | Stimulus onset |
| `event_16` | 2 | event | raw | Involuntary response onset |
| `event_2` | 1131 | event | raw | Response 1 onset |
| `event_254` | 4 | event | raw | Unmapped marker |
| `event_4` | 754 | event | raw | Response 2 onset |
| `event_8` | 258 | event | raw | Response 3 onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: ISA-GSR Phase-Amplitude Coupling Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0, target_events = [`event_128`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | event_128 | 0 | Low ISA-GSR coupling (below-subject median) |
  | event_128 | 1 | High ISA-GSR coupling (above-subject median) |
- **Evidence**:
  - 10.3389/fnins.2022.765585 — Paper explicitly cites openneuro ds001787; uses 12 expert and 12 novice meditators; computes Hilbert-transformed ISA phase (0.01–0.1 Hz) correlated with GSR amplitude during first 30s of each meditation trial (event_128); uses d-prime to measure discriminability of phase-amplitude coupling; thresholds at median to create binary high/low coupling labels per subject (2 classes).
- **Notes**: Labels are assigned per subject by thresholding the computed ISA-GSR coupling d-prime at the cross-subject median. All event_128 epochs from a given subject share the same binary label. Kernel must derive the isa_gsr_coupling_dprime channel (ISA phase via Hilbert on EEG 0.01–0.1 Hz bandpass + GSR amplitude envelope) and then apply median thresholding to generate per-subject binary labels.

### Potential Task 1: Meditator Expertise Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = 0 s *, tmax = 30 s *, overlap = 0 *, target_events = [`event_128`]
- **Label Route**: info
- **Label Field**: group
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|--------|
  | group | expert | 0 | Expert meditator (≥10 years daily practice) |
  | group | novice | 1 | Novice meditator |
- **Evidence**:
  - participants.tsv — group column is complete across all 24 subjects; 12 expert, 12 novice (balanced)
  - Dataset README — confirms "12 subjects were expert meditators with at least 10 years of daily practice and 12 subjects were novice meditators"
- **Notes**: Groups are biologically grounded and documented in the published protocol; event_128 serves as the meditation trial onset anchor (stimulus = onset of first question per events.json); the 30 s epoch captures sustained meditative state periods between question prompts; overlap=0 per standard long-event segmentation.

### Potential Task 2: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 30 s *, overlap = 0.0, target_events = ['event_128']`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 29–78 (years) | 23/24 subjects have age data; predicts subject age from meditation EEG epochs |
- **Evidence**:
  - (none) — Evidence summary: Age ranges from 29–78 years across 23/24 subjects (complete). Continuous age value available for regression predicting subject age from meditation EEG epochs. Use event_128 as epoch anchor for sustained meditation state analysis.
- **Notes**: B3 archetype: Label Field `age` is a native participants.tsv column (raw meta level). Epochs are anchored at event_128 (Stimulus onset) which marks meditation interruption points approximately every 2 minutes per README. Long event epochs (30s) capture sustained meditation EEG between interruptions.

### Potential Task 3: Subject Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0.0 s *, tmax = 30.0 s *, overlap = 0.0, target_events = ["event_128"]`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|--------|
  | gender | M | 0 | male subject |
  | gender | F | 1 | female subject |
- **Evidence**:
  - participants.tsv confirms equal gender split: 12 male, 12 female subjects (sex={'M': 12, 'F': 12})
  - event_128 (Stimulus onset) serves as epoch anchor capturing sustained meditation state between question prompts
  - README confirms ~2 minute intervals between stimuli; 30 s epoch captures sufficient meditation context
- **Notes**: Binary classification of EEG patterns by biological sex during meditation. Gender is a subject-level variable from participants.tsv (complete, no missing values). The task trains on EEG epochs during meditation sessions, labeled by subject sex. Kernel uses event_128 as epoch anchor to define long meditation segments.

### Potential Task 4: Continuous Meditation State Segmentation by Expertise
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 30 s *, overlap = 0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  | group | expert | 1 | Expert meditator |
  | group | novice | 0 | Novice meditator |
- **Evidence**:
  - README (openneuro_ds001787) — 24 subjects: 12 expert meditators, 12 novices; continuous EEG ~45 min per session; subjects interrupted ~every 2 min for concentration/mind-wandering reports
  - participants.tsv — group column complete for all 24 subjects with expert/novice labels
  - eeg.json — RecordingType=continuous, RecordingDuration~2721s, SamplingFrequency=256 Hz
- **Notes**: Segmentation approach labels entire continuous recording with subject-level expertise. Segment length 30s inferred from SKILL default for sustained biological state; overlaps the ~2-min meditation intervals between questioning events.

### Potential Task 5: Continuous Meditation State Segmentation by Age
- **Task Type**: regression
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: segment_length = 30 s, overlap = 0 s, target_events = []
- **Label Route**: info
- **Label Field**: age
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (years) | Notes |
  |------------|---------------|-------|
  | age        | 29–78         | Partial: 23/24 subjects |
- **Evidence**:
  - participants.tsv — Age available for 23/24 subjects (29-78 years)
  - README — Meditation recording interrupted ~every 2 minutes for responses
- **Notes**: Regression targets participant age from participants.tsv for each 30-second segment of continuous meditation recording. Kernel does not need to derive any misc channels; Info Field (age) is native from participants.tsv. Metadata extraction uses raw participant-level information rather than derived measures.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
