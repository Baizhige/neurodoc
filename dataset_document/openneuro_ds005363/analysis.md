# Object Recognition in Healthy Aging (ORHA) - EEG
**Manual Review**:
## Paradigm

(See existing draft)

## File Scan Result

> **Kernel SHA256**: `3583aa1b5e26ec08b61adb74d32b02e0aed8f95e571755adc8e85e26a46feaf0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/ControlBox is not connected via USB` | 22 | event | raw |  |
| `Comment/actiCAP Data On` | 44 | event | raw |  |
| `Comment/actiCAP USB Power On` | 21 | event | raw |  |
| `New Segment/` | 2 | event | raw |  |
| `Stimulus/S 01` | 1314 | event | raw |  |
| `Stimulus/S 02` | 1315 | event | raw |  |
| `Stimulus/S 03` | 1313 | event | raw |  |
| `Stimulus/S 04` | 1315 | event | raw |  |
| `Stimulus/S 05` | 1315 | event | raw |  |
| `Stimulus/S 06` | 1314 | event | raw |  |
| `Stimulus/S 07` | 1315 | event | raw |  |
| `Stimulus/S 08` | 1315 | event | raw |  |
| `Stimulus/S 09` | 1314 | event | raw |  |
| `Stimulus/S 10` | 1315 | event | raw |  |
| `Stimulus/S 11` | 1315 | event | raw |  |
| `Stimulus/S 12` | 1314 | event | raw |  |
| `Stimulus/S 13` | 1314 | event | raw |  |
| `Stimulus/S 14` | 1314 | event | raw |  |
| `Stimulus/S 15` | 1315 | event | raw |  |
| `Stimulus/S 16` | 1314 | event | raw |  |
| `Stimulus/S 17` | 1314 | event | raw |  |
| `Stimulus/S 18` | 1314 | event | raw |  |
| `Stimulus/S 19` | 1315 | event | raw |  |
| `Stimulus/S 20` | 1314 | event | raw |  |
| `Stimulus/S 21` | 1314 | event | raw |  |
| `Stimulus/S 22` | 1314 | event | raw |  |
| `Stimulus/S 23` | 1315 | event | raw |  |
| `Stimulus/S 24` | 1315 | event | raw |  |
| `Stimulus/S 25` | 1315 | event | raw |  |
| `Stimulus/S 26` | 1315 | event | raw |  |
| `Stimulus/S 27` | 1315 | event | raw |  |
| `Stimulus/S 28` | 1314 | event | raw |  |
| `Stimulus/S 29` | 1314 | event | raw |  |
| `Stimulus/S 30` | 1315 | event | raw |  |
| `Stimulus/S 31` | 1314 | event | raw |  |
| `Stimulus/S 32` | 1314 | event | raw |  |
| `Stimulus/S 33` | 1313 | event | raw |  |
| `Stimulus/S 34` | 1315 | event | raw |  |
| `Stimulus/S 35` | 1315 | event | raw |  |
| `Stimulus/S 36` | 1314 | event | raw |  |
| `Stimulus/S 37` | 1314 | event | raw |  |
| `Stimulus/S 38` | 1314 | event | raw |  |
| `Stimulus/S 39` | 1314 | event | raw |  |
| `Stimulus/S 40` | 1315 | event | raw |  |
| `Stimulus/S 41` | 1314 | event | raw |  |
| `Stimulus/S 42` | 1314 | event | raw |  |
| `Stimulus/S 43` | 1314 | event | raw |  |
| `Stimulus/S 44` | 1315 | event | raw |  |
| `Stimulus/S 45` | 1314 | event | raw |  |
| `Stimulus/S 46` | 1315 | event | raw |  |
| `Stimulus/S 47` | 1315 | event | raw |  |
| `Stimulus/S 48` | 1314 | event | raw |  |
| `Stimulus/S 49` | 1315 | event | raw |  |
| `Stimulus/S 50` | 1314 | event | raw |  |
| `Stimulus/S 51` | 1313 | event | raw |  |
| `Stimulus/S 52` | 1315 | event | raw |  |
| `Stimulus/S 53` | 1315 | event | raw |  |
| `Stimulus/S 54` | 1315 | event | raw |  |
| `Stimulus/S 55` | 1314 | event | raw |  |
| `Stimulus/S 56` | 1314 | event | raw |  |
| `Stimulus/S 57` | 1315 | event | raw |  |
| `Stimulus/S 58` | 1313 | event | raw |  |
| `Stimulus/S 59` | 1315 | event | raw |  |
| `Stimulus/S 60` | 1315 | event | raw |  |
| `Stimulus/S 61` | 1315 | event | raw |  |
| `Stimulus/S 62` | 1314 | event | raw |  |
| `Stimulus/S 63` | 1314 | event | raw |  |
| `Stimulus/S 64` | 1315 | event | raw |  |
| `Stimulus/S101` | 43 | event | raw |  |
| `Stimulus/S102` | 41 | event | raw |  |
| `Stimulus/S103` | 41 | event | raw |  |
| `Stimulus/S104` | 41 | event | raw |  |
| `Stimulus/S105` | 41 | event | raw |  |
| `Stimulus/S106` | 41 | event | raw |  |
| `Stimulus/S107` | 41 | event | raw |  |
| `Stimulus/S108` | 41 | event | raw |  |
| `Stimulus/S199` | 328 | event | raw |  |
| `Stimulus/S255` | 2 | event | raw |  |
| `admin: fixation_marker` | 20476 | event | raw |  |
| `animate` | 8524 | event | raw |  |
| `inanimate` | 12505 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Category Classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 65`, `Stimulus/S 66`, `Stimulus/S 67`, `Stimulus/S 68`, `Stimulus/S 69`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 65` | 0 | Visual category 1 (faces) |
  | `Stimulus/S 66` | 1 | Visual category 2 (animals) |
  | `Stimulus/S 67` | 2 | Visual category 3 (places) |
  | `Stimulus/S 68` | 3 | Visual category 4 (objects) |
  | `Stimulus/S 69` | 4 | Visual category 5 (objects) |
- **Evidence**:
  - DOI: 10.1016/j.cub.2025.03.062 — Explicitly investigates 4-category visual object recognition (faces, animals, places, objects) using S65-S69 event codes with multivariate EEG classification across 86 subjects (43 older, 43 younger).
- **Kernel Notes**: Include 200ms pre-stimulus baseline for proper baseline correction. Exclude S99 fixation marker (21460 events) to avoid event density issues. S4-S57 encode individual exemplar identities (~1315 trials each, 60+ items)—reserved for RSA task. S255 (2 events) likely experimental outlier; exclude.

### Potential Task 1: Representational Similarity Analysis (RSA) - Exemplar Level
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = [`Stimulus/S 4`, `Stimulus/S 5`, `Stimulus/S 6`, `Stimulus/S 7`, `Stimulus/S 8`, `Stimulus/S 9`, `Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 13`, `Stimulus/S 14`, `Stimulus/S 15`, `Stimulus/S 16`, `Stimulus/S 17`, `Stimulus/S 18`, `Stimulus/S 19`, `Stimulus/S 20`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 23`, `Stimulus/S 24`, `Stimulus/S 25`, `Stimulus/S 26`, `Stimulus/S 27`, `Stimulus/S 28`, `Stimulus/S 29`, `Stimulus/S 30`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`, `Stimulus/S 35`, `Stimulus/S 36`, `Stimulus/S 37`, `Stimulus/S 38`, `Stimulus/S 39`, `Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 42`, `Stimulus/S 43`, `Stimulus/S 44`, `Stimulus/S 45`, `Stimulus/S 46`, `Stimulus/S 47`, `Stimulus/S 48`, `Stimulus/S 49`, `Stimulus/S 50`, `Stimulus/S 51`, `Stimulus/S 52`, `Stimulus/S 53`, `Stimulus/S 54`, `Stimulus/S 55`, `Stimulus/S 56`, `Stimulus/S 57`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 4` | 0 | Exemplar image 1 |
  | `Stimulus/S 5` | 1 | Exemplar image 2 |
  | `Stimulus/S 6` | 2 | Exemplar image 3 |
  | `Stimulus/S 7` | 3 | Exemplar image 4 |
  | ... | ... | ... |
  | `Stimulus/S 57` | 53 | Exemplar image 54 |
- **Evidence**:
  - DOI: 10.1016/j.cub.2025.03.062 — Uses representational similarity analysis on EEG responses to individual exemplar images (64 images across 4 categories) to track age-related changes in neural object coding patterns.
- **Kernel Notes**: 60+ exemplar codes with ~1313-1315 trials each provide sufficient stimulus diversity for RSA. Standard 1s post-stimulus window captures neural object coding patterns. Exclude category codes S65-S69 (used for classification tasks) and fixation markers S99/admin: fixation_marker.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
