# Attended Speaker Paradigm (cEEGrid Data)

**Dataset**: `openneuro_ds004015` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004015
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 36 | **Channels**: 18 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A two-competing speaker auditory attention paradigm in which participants were instructed to selectively attend to one of two simultaneously presented audiobooks under varying spatial and loudness conditions. EEG was recorded using a cEEGrid around-the-ear electrode array with 18 channels. The dataset pools data from two studies (Jaeger et al., 2020; Holtze et al., 2021) with slightly different protocols, including variations in calibration procedures and spatial audio conditions (omnidirectional vs. beamforming).

## File Scan Result

> **Kernel SHA256**: `95bccff97766b74a8a2c1cdb30945199d6fec540a29cc7cbe14814d8571c86b6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Beep` | 756 | event | raw | Trial phase onset: start of the beep tone period (20 beeps) |
| `Calib_End` | 102 | admin | raw | Calibration period end |
| `Calib_Start` | 21 | admin | raw | Calibration period start: beginning of 1-minute calibration period |
| `StartTrigger` | 120 | event | raw | Trial phase onset: onset of a 10-minute audio book block |
| `beam` | 420 | event | raw | Trial phase onset: name onset in beamforming condition |
| `boundary` | 21 | admin | raw | Data discontinuity marker: indicates a break in continuous data (e.g. where two xdf files were merged) |
| `omni` | 420 | event | raw | Trial phase onset: name onset in omnidirectional condition |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Spatial Condition Classification (Beamforming vs Omnidirectional)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 10 s *, target_events = [`beam`, `omni`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `beam` | 0 | beamforming condition (attended speaker louder) |
  | `omni` | 1 | omnidirectional condition (both speakers equal loudness) |
- **Evidence**:
  - sub-001/sub-002 events.json — explicit 'Levels' field defines 'beam' as "name onset in beamforming condition" and 'omni' as "name onset in omnidirectional condition"
  - README — describes Holtze et al. 2021 design: 10-minute blocks alternate between omnidirectional and beamforming conditions; first block always omnidirectional, conditions alternate thereafter
  - participants.tsv — 'con_order' column (values: -, OBOB, BOBO) confirms condition alternation pattern for holtze2021 subjects only; jaeger2020 subjects have '-' indicating no condition markers
- **Notes**: Epoch parameters marked with * because the epoch_hint indicates these are inferred for demonstration purposes. The actual condition blocks are 10 minutes long; tmax=10s represents a short window choice rather than the full block. The task is only applicable to holtze2021 subjects (n~21) who have alternating beam/omni condition markers. jaeger2020 subjects (n=15) lack these markers entirely. This is a secondary task derived from the event structure, not the primary AAD (auditory attention detection) objective of the dataset. The classification distinguishes between two spatial audio presentation conditions at block onset.

## Data Quality Notes

- Pooled dataset from two studies with different protocols: Jaeger et al. (2020, n=15, 6 blocks, no calibration, always omnidirectional) and Holtze et al. (2021, n=21, 5 blocks, with calibration, alternating omni/beam conditions).
- `beam`/`omni` spatial condition markers are only present for holtze2021 subjects; jaeger2020 subjects have '-' in `con_order` and lack these event markers entirely.
- 21 `boundary` events indicate data discontinuities where multiple XDF files were merged, which may affect continuous analysis assumptions.
- `device` field is completely missing from info metadata, limiting hardware reproducibility documentation.
- `Calib_Start` count (21) vs `Calib_End` count (102) is imbalanced, suggesting calibration markers may not consistently mark both start and end across all subjects or blocks.
- cEEGrid's 18-channel around-the-ear montage provides limited spatial coverage compared to standard scalp EEG, which may constrain spatial resolution for certain analyses.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
