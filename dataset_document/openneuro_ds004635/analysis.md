# Gaffrey Lab Infant EEG Microstates Reliability

**Dataset**: `openneuro_ds004635` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004635
**Category**: Biological State | **Subjects**: 48 | **Files (Completed)**: 1 | **Channels**: 129 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Infants watched a series of engaging and relaxing videos to facilitate recording of spontaneous EEG activity. The dataset was collected to assess the test-retest reliability of EEG microstate metrics in infants. The single aggregated file contains data from 48 infants with recording-boundary markers; no active task was required.

## File Scan Result

> **Kernel SHA256**: `579ff38edceb732e54126de9b90c5c74352adca4bc60bd785fcaf2b0cc022ec2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TRSP` | 10 | admin | raw | System marker: Ignore (technical marker) |
| `bgin` | 10 | admin | raw | System marker: Ignore (technical marker) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Segment vs Transition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 1.0 s *, target_events = ['bgin', 'TRSP']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `bgin` | 0 | System marker: segment beginning (Ignore) |
  | `TRSP` | 1 | System marker: transition/boundary (Ignore) |
- **Evidence**:
  - task-resting_events.json — 'value' column Levels: 'bgin'='Ignore', 'TRSP'='Ignore'
  - sub-S1_task-resting_events.tsv — bgin and TRSP alternate throughout recording as technical markers
- **Notes**: This is a low-level technical marker discrimination task using explicitly designated 'Ignore' admin markers. Both event types are system markers with no expected neural correlate; included for completeness but of limited scientific value. The 0.5s pre- and 1.0s post-onset windows are inferred defaults for brief technical markers.

## Data Quality Notes

- Single aggregated file prevents subject-level separation; all 48 infants' data are combined into one recording with boundary markers.
- `age` and `sex` fields are missing from info, but `Age` and `Gender` are present and complete as native participants.tsv columns.
- `device` field is missing; no equipment metadata available in scan.
- Only 10 events each for `TRSP` and `bgin`, which are admin/technical markers explicitly designated to ignore; very limited event structure for task-based analysis.
- Event counts differ from original draft (10 vs previously noted 10 for both types, but types reclassified as admin vs event); the authoritative scan shows admin type with "System marker: Ignore" meaning.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
