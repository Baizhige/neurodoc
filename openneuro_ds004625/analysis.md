# Mind in Motion: Young Adults Walking Over Uneven Terrain

**Dataset**: `openneuro_ds004625` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004625
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 543 | **Channels**: 284 | **Sampling Rate**: 500 Hz

## Paradigm

Participants walked over uneven terrain at different speeds while high-density EEG, EMG, and kinematic data were simultaneously recorded, with a seated resting condition also included. The study examines neural correlates of locomotor control and gait adaptation during ambulatory tasks. Gait events (heel-strikes, toe-offs) were synchronized with EEG via force-sensitive insoles.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LHS` | 65124 | event | raw | Left heel strike |
| `LTO` | 65105 | event | raw | Left toe off |
| `RHS` | 63800 | event | raw | Right heel strike |
| `RTO` | 63792 | event | raw | Right toe off |
| `CGY-T 1` | 2786 | event | raw | Terrain change trigger |
| `CGY-M 1` | 676 | event | raw | Gait measurement marker |
| `spare-M 1` | 635 | event | raw | Spare measurement marker |
| `boundary` | 543 | admin | raw | Segment boundary (exclude) |
| `TrialStart` | 543 | event | raw | Trial start marker |
| `TrialEnd` | 543 | event | raw | Trial end marker |
| `LS-Sync` | 536 | admin | raw | Insole sync pulse (exclude) |
| `CWR-M 1` | 269 | event | raw | Cobblestone walk marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Gait Event Classification (LHS/LTO/RHS/RTO)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `LHS` | 0 | Left heel strike |
  | `LTO` | 1 | Left toe off |
  | `RHS` | 2 | Right heel strike |
  | `RTO` | 3 | Right toe off |
- **Evidence**:
  - DOI: 10.3389/fnagi.2025.1644741 — Shows gait event classification during uneven terrain walking, using high-density EEG to examine neural correlates of locomotor control
- **Kernel Notes**: High-density 284-channel EEG requires ICA-based artifact rejection for motion artifacts. Exclude administrative events (`boundary`, `LS-Sync`). Use TrialStart/TrialEnd to define walking bouts. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Terrain Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`CGY-T 1`, `CWR-M 1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `CGY-T 1` | 0 | Terrain change trigger |
  | `CWR-M 1` | 1 | Cobblestone walk marker (specific terrain type) |
- **Evidence**:
  - DOI: 10.3389/fnagi.2025.1644741 — Measures walking speed across four terrain conditions (flat, low, medium, high) during uneven terrain walking
- **Kernel Notes**: Verify terrain type mapping from events.tsv — `CGY-T 1` may indicate transition to specific terrain, `CWR-M 1` indicates cobblestone condition. Additional terrain labels may need derivation from trial metadata.

### Classical Task 3: Gait Speed Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 7.0 s, overlap = 0.86 * (approximately 6s overlap for 1s slide)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Continuous walking speed values (m/s) extracted from kinematic measurements during walking bouts
- **Evidence**:
  - DOI: 10.3389/fnagi.2025.1644741 — Measures walking speed over middle 3m of terrain mat across different terrain conditions
  - DOI: 10.1109/JBHI.2019.2914940 — Validates gait speed estimation methodology (window=7s with 6s overlap)
- **Kernel Notes**: Speed values should be extracted from kinematic/force-sensitive insole data synchronized with EEG. Apply to segments within TrialStart/TrialEnd boundaries only. Requires fusion of kinematic channel data for speed labels.

## Data Quality Notes

- High-density EEG (284 channels) with significant motion artifacts from walking.
- boundary and LS-Sync markers are administrative - exclude.
- Mobile EEG data - apply ICA-based artifact correction.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review