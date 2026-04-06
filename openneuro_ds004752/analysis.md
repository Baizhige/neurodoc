# Dataset of Intracranial EEG, Scalp EEG and Beamforming Sources from Epilepsy Patients - Verbal Working Memory

**Dataset**: `openneuro_ds004752` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004752
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 136
**Channels**: 64 | **Sampling Rate**: 2000 Hz

## Paradigm

Epilepsy patients performed a modified Sternberg verbal working memory task consisting of encoding, maintenance, and recall phases while simultaneous scalp and intracranial EEG were recorded. The dataset includes iEEG from depth electrodes, scalp EEG, single-unit neuron spike times, and electrode localizations, enabling multi-level analysis of memory processes. No trial-level event annotations are available in the BIDS events.tsv.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: None (no event tag)
- **Notes**: No trial-level events available in events.tsv. EEG is continuous during task performance. Use sliding-window segmentation. Trial timing may be available in accompanying behavioral logs not captured in BIDS events.tsv.

## Data Quality Notes

- No event markers - trial-epoch structure not available from events.tsv.
- Very high sampling rate (2000 Hz) - downsample before analysis.
- Epilepsy patients; ictal episodes should be identified and excluded.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review