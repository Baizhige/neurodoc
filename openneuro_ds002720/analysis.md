# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2018 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 18 | **Files (Completed)**: 165 | **Channels**: 19 | **Sampling Rate**: 1000 Hz
**Manual Review**: Mr.PJ

## Paradigm

Participants used EEG self-regulation to control the tempo of music in a tempo-based brain-computer music interface (BCMI). One condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. Each labeled event spans a full 20-second music clip interval. The dataset contains multiple runs per participant.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 1275 | event | raw | Lower alpha condition (20-second interval) |
| `2` | 1250 | event | raw | Raise alpha condition (20-second interval) |

> **Manual Review Note**: Event IDs corrected by human reviewer (Mr.PJ) — original entries used `motor_imagery`/`relaxation` derived from paradigm description; actual BIDS event IDs are numeric `1`/`2` per events.json. Kernel should confirm event ID format on next scan.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Alpha-State BCMI Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Lower alpha condition |
  | `2` | 1 | Raise alpha condition |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — Describes the BCMI tempo dataset (openneuro_ds002720) recorded during development of a tempo-based BCMI where participants regulated alpha levels to control music tempo; event JSON explicitly defines event 1 as Lower alpha and event 2 as Raise alpha.
- **Kernel Notes**: Use long-event decoding over the full 20-second labeled interval. Twenty-two event files are empty — not every EEG file contains labeled events.

### Classical Task 2: Continuous Segmentation Within BCMI Runs
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Lower alpha condition segment |
  | `2` | 1 | Raise alpha condition segment |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — Segmentation alternative for cases where full 20-second long-event decoding is not desired.
- **Kernel Notes**: Segment within labeled 20-second windows. Filter out the 22 empty event files before processing.

## Data Quality Notes

- The dataset contains 18 subjects, not 19.
- Twenty-two event files are empty — not every EEG file contains labeled events.
- All non-empty events have duration exactly 20 seconds.
- The event tables contain only `onset`, `duration`, and `trial_type`; no `response_time` or behavioral metadata.
- All channel files contain 19 EEG channels with no auxiliary EOG/ECG channels.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review