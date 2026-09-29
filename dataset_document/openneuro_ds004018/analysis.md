# EEG recordings for 200 object images presented in RSVP sequences at 5Hz or 20Hz

**Dataset**: `openneuro_ds004018` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004018
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 63 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Rapid Serial Visual Presentation (RSVP) of 200 object images at two presentation frequencies (5 Hz and 20 Hz) to investigate the temporal dynamics of visual object representations. Images were categorized as "stars" or "boats" (two superordinate categories), allowing investigation of how presentation rate affects category-level neural decoding. This is a very small dataset (2 subjects).

## File Scan Result

> **Kernel SHA256**: `a8db2663ac572e90e5379c1a425ae5e272fe68e7689a03f29a0f7c72ebca8588`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: RSVP Object Category Classification (stars vs boats)

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stars` | 0 | Star/celestial category RSVP image onset |
  | `boats` | 1 | Boat/vehicle category RSVP image onset |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — 16 participants, 200 visual objects, RSVP at 5Hz (200ms ISI) and 20Hz (50ms ISI), LDA classifiers for category decoding, boats vs stars as primary target stimuli with 8 exemplars each. Window from -100ms baseline to 1000ms captures N1/P1/N2 components for visual object category processing.
- **Kernel Notes**: Kernel scan shows empty event counts; actual `stars`/`boats` labels need extraction from BIDS events.tsv directly. Verify that `stars` and `boats` event codes are properly parsed from raw BIDS structure. Presentation frequency (5Hz vs 20Hz) should be encoded as a covariate per-epoch since it affects temporal dynamics of category decoding. Very small dataset (2 subjects) limits statistical power; use within-subject cross-validation.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
