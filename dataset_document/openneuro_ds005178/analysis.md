# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 5 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. Subjects manually sent trigger events to mark boundaries between video sequences and sleep sequences during the recording sessions.

## File Scan Result

> **Kernel SHA256**: `05c952b5adbb7c51c1e20d55e1cac5b7e2995315d83205c70482ea76be573017`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `error -10` | 6020 | admin | raw | Buffer overflow error in ear-EEG ASICs |
| `error -100` | 62 | admin | raw | Hard reset/power cycle error in ear-EEG ASICs |
| `event` | 12424 | event | raw | General event marker |
| `event_2` | 72 | event | raw | Secondary event marker |
| `oLED` | 1 | admin | raw | Connection loss to ASIC due to loose cable |
| `trigger` | 175 | event | raw | Manual trigger event sent by subject to mark sequence boundaries |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Trigger Boundary Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 30 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `trigger` | 1 | Segment contains trigger boundary marker (video-to-sleep sequence transition) |
  | (no trigger) | 0 | Non-boundary segment (no trigger within window) |
- **Evidence**:
  - README — "After the video sequence, the subject sent triggers to distinguish between the two sequences."
  - sub-001_ses-001_task-sleep_acq-PSGtrigger_events.tsv — Four trigger events with zero duration confirming instantaneous boundary markers at onset times 9664s, 69123s, 172979s, 6079358s
  - Event ID inventory — 175 `trigger` events confirmed across dataset
- **Notes**: Segmentation-based approach with 30s windows and 50% overlap. A segment is labeled y=1 if any `trigger` event falls within its [start, end) interval; otherwise y=0. This creates a 2-class boundary detection task from continuous sleep recordings where triggers mark transitions between video and sleep sequences. The `trigger` event is confirmed as a manual subject-initiated boundary marker, not a hardware error (distinct from `error -10`, `error -100`, `oLED`).

### Potential Task 2: ear-EEG error anomaly detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 10 s *, overlap = 0.0, target_events = [`error -10`, `error -100`, `oLED`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `error -10` | 0 | Buffer overflow error in ear-EEG ASICs |
  | `error -100` | 0 | Hard reset/power cycle error in ear-EEG ASICs |
  | `oLED` | 0 | Connection loss to ASIC due to loose cable |
  | (non-error baseline) | 1 | Normal epoch without hardware error |
- **Evidence**:
  - [task-sleep_acq-earEEGRecordingFailures_events.json] — Explicitly defines Error -10 (buffer overflow), Error -100 (hard reset), and oLED (connection loss) as hardware failure conditions in ear-EEG ASICs with detailed descriptions of data gaps and invalidation rules
- **Notes**: All three error events (`error -10`, `error -100`, `oLED`) are merged into y=0 (anomaly/error class) as they all represent hardware failures requiring data quality flagging. The complementary y=1 class represents normal epochs without any error event. Epoch parameters are inferred from variable-duration error events with 10s as a practical default for anomaly detection windows. This is a Potential Task as no published reference explicitly proposes this anomaly detection formulation, though the dataset's own sidecar documentation thoroughly characterizes these error conditions.

### Potential Task 3: Buffer Overflow vs Hard Reset Error Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, overlap = 0.0 *, target_events = [`error -10`, `error -100`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `error -10` | 0 | Buffer overflow error in ear-EEG ASICs (SD card write interrupt, data gap with 50 inserted samples) |
  | `error -100` | 1 | Hard reset/power cycle error in ear-EEG ASICs (power off/on, data loss with timestamp-based gap estimation) |
- **Evidence**:
  - [task-sleep_acq-earEEGRecordingFailures_events.json] — Maps `Error -10` to buffer overflow from SD card write interrupts/synchronization issues between ASICs, and `Error -100` to hard reset/power cycle with data loss estimation via nearest timestamps
- **Notes**: This is a device diagnostics task distinguishing two distinct hardware failure modes in ear-EEG recordings. The severe class imbalance (6020 vs 62 events) reflects realistic error frequencies but should be noted for modeling. The 5-second window captures immediate error context while minimizing contamination from normal sleep data. Both error types produce data gaps but with different mechanisms and recovery procedures per the events.json sidecar.

## Data Quality Notes

- Substantial hardware error events present: 6,020 buffer overflow errors (`error -10`), 62 hard reset errors (`error -100`), and 1 connection loss event (`oLED`), totaling 6,083 error events across the dataset.
- Severe class imbalance in error types (6020 vs 62 vs 1) may affect modeling for error classification tasks.
- General `event` markers (12,424 occurrences) lack detailed semantic documentation in available metadata; meaning is unspecified beyond "general event marker."
- Missing demographic metadata: subject age, sex, and recording device information are not available in scanned files.
- The `event_2` secondary event marker (72 occurrences) lacks explicit documentation distinguishing it from the primary `event` marker.
- Ear-EEG recordings in home environments are susceptible to motion artifacts, cable looseness, and ASIC buffer issues inherent to the miniaturized hardware design.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
