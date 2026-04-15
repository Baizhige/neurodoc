# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 119 | **Channels**: 63 | **Sampling Rate**: 5000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimates were collected using a visual analogue scale (VAS). High sampling rate (5000 Hz) requires downsampling before epoching.

## File Scan Result

> **Kernel SHA256**: `4daec86681c9d99f62fde71d392c971808265fd218032932bd2292ed20a2867e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Response/R128` | 44303 | event | raw | Button press response onset |
| `Stimulus/S  7` | 1347 | event | raw | Visual stimulus event |
| `Stimulus/S  8` | 1477 | event | raw | Visual stimulus event |
| `Stimulus/S 11` | 2851 | event | raw | Visual stimulus event |
| `Stimulus/S 12` | 2854 | event | raw | Visual stimulus event |
| `Stimulus/S 17` | 1356 | event | raw | Visual stimulus event |
| `Stimulus/S 18` | 1489 | event | raw | Visual stimulus event |
| `Stimulus/S 27` | 5657 | event | raw | Numerosity stimulus trial type A |
| `Stimulus/S 37` | 120 | event | raw | Visual stimulus event |
| `Stimulus/S 38` | 109 | event | raw | Visual stimulus event |
| `Stimulus/S 40` | 6175 | event | raw | Numerosity stimulus trial type B |
| `Stimulus/S 41` | 5703 | event | raw | Numerosity stimulus trial type C |
| `Stimulus/S 43` | 6583 | event | raw | Numerosity stimulus trial type D |
| `Stimulus/S 44` | 475 | event | raw | Visual stimulus event |
| `Stimulus/S128` | 474612 | event | raw | Fixation cross marker |
| `Stimulus/S140` | 3 | event | raw | Practice/calibration event |
| `Stimulus/S145` | 1 | event | raw | Practice/calibration event |
| `Stimulus/S155` | 2 | event | raw | Practice/calibration event |
| `Stimulus/S165` | 39 | event | raw | Block/event marker |
| `Stimulus/S166` | 48 | event | raw | Block/event marker |
| `Stimulus/S169` | 1 | event | raw | Practice/calibration event |
| `Stimulus/S171` | 4364 | event | raw | Confidence rating onset |
| `SyncStatus/Sync On` | 30864 | event | raw | EEG-fMRI sync pulse |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Confidence Regression from EEG during Speeded Perceptual Decisions
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`Response/R128`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---|
  | confidence (continuous 0-1) | Metacognitive confidence rating (0=sure error, 0.5=unsure, 1=sure correct) |
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — EEG amplitude time-locked to first-order response onset used to model confidence via linear regression; multivariate EEG decoding derived single-trial confidence predictions.
- **Kernel Notes**: High sampling rate (5000 Hz) requires downsampling (factor of 10 to 500 Hz or 20 to 250 Hz). The `Response/R128` event (44303 total, ~2215/subject) serves as the response onset anchor for epoching, consistent with the PNAS methodology. Extract confidence values from misc channel `confidence` and align with epochs. The original paper used 0-200ms and 200-450ms post-response windows for temporal decoding analysis.

### Potential Task 1: Stimulus-Locked ERP Analysis for Decision Processing
- **Task Type**: classification/regression (exploratory)
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Stimulus/S 27`, `Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |---|---|---|
  | `Stimulus/S 27` | 1 | Numerosity stimulus trial type A |
  | `Stimulus/S 40` | 2 | Numerosity stimulus trial type B |
  | `Stimulus/S 41` | 3 | Numerosity stimulus trial type C |
  | `Stimulus/S 43` | 4 | Numerosity stimulus trial type D |
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — Paradigm involved numerosity discrimination; stimulus events available for stimulus-locked analysis.
- **Kernel Notes**: High-count stimulus events (S27: 5657, S40: 6175, S41: 5703, S43: 6583) provide sufficient trials for ERP analysis. Exclude S128 (474612 events, fixation marker). Verify trial_type mappings in events.tsv if categorical analysis by condition (committed vs observed) is required. tmax=0.8s captures the full decision period from stimulus onset to confidence rating. Downsample from 5000 Hz before epoching.

### Potential Task 2: Self vs Other Confidence Comparison
- **Task Type**: classification (binary)
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`Response/R128`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---|
  | self (1) | Committed decision (self-reported confidence) |
  | other (0) | Observed decision (confidence in other's choice) |
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — Paradigm explicitly contrasts self vs other confidence; trial_type column in events.tsv may contain condition labels.
- **Kernel Notes**: Requires verification of events.tsv `trial_type` column to map trials to self/other conditions. If confirmed, this enables comparison of neural correlates between self-generated and observed confidence. The misc channel stores confidence ratings for both conditions. Downsample from 5000 Hz before epoching.