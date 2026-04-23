# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 5 | **Sampling Rate**: 250 Hz
**Manual Review**:

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. The `trigger` event marks synchronization pulses between the ear-EEG and PSG systems.

## File Scan Result

> **Kernel SHA256**: `ad6e2962d008d80162dbd7188aa01eb2e42f1f83076e8b2442f5fbffdf3c3259`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_2` | 72 | event | raw | Trigger event 2: second synchronization trigger between ear-EEG and PSG devices |
| `trigger` | 175 | event | raw | Trigger onset marker from ear-EEG CSV data stream (Trigger column) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep vs. Video Sequence Classification (Trigger-Boundary Based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 30 s *, overlap = 0.5 *`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `trigger` | 1 | trigger onset marker — marks boundary between video and sleep sequences |
  | (no trigger, any segment) | 0 | non-boundary segment (either within video sequence or within sleep sequence) |
- **Evidence**:
  - `sub-001_ses-001_task-sleep_acq-PSGtrigger_events.tsv` — trigger events with onset timestamps at boundaries between sequences
  - `README` — "After the video sequence, the subject sent triggers to distinguish between the two sequences"
  - `events.tsv` samples — confirmed trigger event values with zero duration, marking instantaneous boundaries
- **Notes**: Reformulated from single-class trigger detection to a proper 2-class classification. Segments containing a trigger event (y=1) mark sequence boundaries. All other segments (y=0) are non-boundary periods within either the video or sleep sequence. The 30s window with 50% overlap is standard for sleep/continuous monitoring paradigms per Category SKILL. This captures the sustained biological state context rather than treating instantaneous triggers as discrete events.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
