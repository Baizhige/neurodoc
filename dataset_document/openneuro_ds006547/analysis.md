# Visual EEG Study (BrainVision -> BIDS)

**Dataset**: `openneuro_ds006547` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006547
**Category**: Sensory/Response | **Subjects**: 31 | **Files (Completed)**: 31 | **Channels**: 67 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

High-density EEG recordings were collected during a visual stimulation task using a BrainVision system, subsequently converted to BIDS format. Participants viewed visual stimuli under multiple conditions encoded by numeric BrainVision trigger codes (S1 through S56, excluding S23–S40). The 38 distinct stimulus codes appear to represent two blocks or condition families (S1–S22 and S41–S56), likely covering perceptual and attentional manipulations in a visual paradigm.

## File Scan Result

> **Kernel SHA256**: `5f07d91df056b31b718f6b5c67d8f12ea772dd78c5ac295ce7bf538cb864b664`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 22 | event | raw | Segmentation marker (start of recording or block) |
| `Stimulus/S  1` | 606 | event | raw | Visual condition S1 |
| `Stimulus/S  2` | 601 | event | raw | Visual condition S2 |
| `Stimulus/S  3` | 597 | event | raw | Visual condition S3 |
| `Stimulus/S  4` | 552 | event | raw | Visual condition S4 |
| `Stimulus/S  5` | 634 | event | raw | Visual condition S5 |
| `Stimulus/S  6` | 571 | event | raw | Visual condition S6 |
| `Stimulus/S  7` | 507 | event | raw | Visual condition S7 |
| `Stimulus/S  8` | 512 | event | raw | Visual condition S8 |
| `Stimulus/S  9` | 514 | event | raw | Visual condition S9 |
| `Stimulus/S 10` | 507 | event | raw | Visual condition S10 |
| `Stimulus/S 11` | 593 | event | raw | Visual condition S11 |
| `Stimulus/S 12` | 590 | event | raw | Visual condition S12 |
| `Stimulus/S 13` | 558 | event | raw | Visual condition S13 |
| `Stimulus/S 14` | 552 | event | raw | Visual condition S14 |
| `Stimulus/S 15` | 589 | event | raw | Visual condition S15 |
| `Stimulus/S 16` | 519 | event | raw | Visual condition S16 |
| `Stimulus/S 17` | 513 | event | raw | Visual condition S17 |
| `Stimulus/S 18` | 597 | event | raw | Visual condition S18 |
| `Stimulus/S 19` | 528 | event | raw | Visual condition S19 |
| `Stimulus/S 20` | 681 | event | raw | Visual condition S20 |
| `Stimulus/S 21` | 513 | event | raw | Visual condition S21 |
| `Stimulus/S 22` | 506 | event | raw | Visual condition S22 |
| `Stimulus/S 41` | 559 | event | raw | Visual condition S41 |
| `Stimulus/S 42` | 594 | event | raw | Visual condition S42 |
| `Stimulus/S 43` | 522 | event | raw | Visual condition S43 |
| `Stimulus/S 44` | 510 | event | raw | Visual condition S44 |
| `Stimulus/S 45` | 513 | event | raw | Visual condition S45 |
| `Stimulus/S 46` | 591 | event | raw | Visual condition S46 |
| `Stimulus/S 47` | 580 | event | raw | Visual condition S47 |
| `Stimulus/S 48` | 634 | event | raw | Visual condition S48 |
| `Stimulus/S 49` | 595 | event | raw | Visual condition S49 |
| `Stimulus/S 50` | 602 | event | raw | Visual condition S50 |
| `Stimulus/S 51` | 552 | event | raw | Visual condition S51 |
| `Stimulus/S 52` | 634 | event | raw | Visual condition S52 |
| `Stimulus/S 53` | 594 | event | raw | Visual condition S53 |
| `Stimulus/S 54` | 552 | event | raw | Visual condition S54 |
| `Stimulus/S 55` | 549 | event | raw | Visual condition S55 |
| `Stimulus/S 56` | 640 | event | raw | Visual condition S56 |
| `Stimulus/S128` | 1 | event | raw | System marker (exclude from analysis) |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores auxiliary physiological and stimulus-synchronization channels.
- **Candidate Labels**: `ecg`, `optical`, `photosensor`, `resp`
- **Kernel Note**: `ecg` (electrocardiogram), `optical` (optical sensor), `photosensor` (stimulus trigger sync), `resp` (respiratory belt). Verify channel roles and units before use.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Visual Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, baseline = (None, 0)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `Stimulus/S  1` | 0 | Visual condition S1 |
| `Stimulus/S  2` | 1 | Visual condition S2 |
| `Stimulus/S  3` | 2 | Visual condition S3 |
| `Stimulus/S  4` | 3 | Visual condition S4 |
| `Stimulus/S  5` | 4 | Visual condition S5 |
| `Stimulus/S  6` | 5 | Visual condition S6 |
| `Stimulus/S  7` | 6 | Visual condition S7 |
| `Stimulus/S  8` | 7 | Visual condition S8 |
| `Stimulus/S  9` | 8 | Visual condition S9 |
| `Stimulus/S 10` | 9 | Visual condition S10 |
| `Stimulus/S 11` | 10 | Visual condition S11 |
| `Stimulus/S 12` | 11 | Visual condition S12 |
| `Stimulus/S 13` | 12 | Visual condition S13 |
| `Stimulus/S 14` | 13 | Visual condition S14 |
| `Stimulus/S 15` | 14 | Visual condition S15 |
| `Stimulus/S 16` | 15 | Visual condition S16 |
| `Stimulus/S 17` | 16 | Visual condition S17 |
| `Stimulus/S 18` | 17 | Visual condition S18 |
| `Stimulus/S 19` | 18 | Visual condition S19 |
| `Stimulus/S 20` | 19 | Visual condition S20 |
| `Stimulus/S 21` | 20 | Visual condition S21 |
| `Stimulus/S 22` | 21 | Visual condition S22 |
| `Stimulus/S 41` | 22 | Visual condition S41 |
| `Stimulus/S 42` | 23 | Visual condition S42 |
| `Stimulus/S 43` | 24 | Visual condition S43 |
| `Stimulus/S 44` | 25 | Visual condition S44 |
| `Stimulus/S 45` | 26 | Visual condition S45 |
| `Stimulus/S 46` | 27 | Visual condition S46 |
| `Stimulus/S 47` | 28 | Visual condition S47 |
| `Stimulus/S 48` | 29 | Visual condition S48 |
| `Stimulus/S 49` | 30 | Visual condition S49 |
| `Stimulus/S 50` | 31 | Visual condition S50 |
| `Stimulus/S 51` | 32 | Visual condition S51 |
| `Stimulus/S 52` | 33 | Visual condition S52 |
| `Stimulus/S 53` | 34 | Visual condition S53 |
| `Stimulus/S 54` | 35 | Visual condition S54 |
| `Stimulus/S 55` | 36 | Visual condition S55 |
| `Stimulus/S 56` | 37 | Visual condition S56 |

- **Evidence**: N/A (no references available)
- **Kernel Notes**: 
  - 38 distinct visual stimulus codes mapped to unique class labels.
  - Exclude `Stimulus/S128` (n=1, likely system marker).
  - S1-S22 and S41-S56 ranges may represent distinct experimental blocks or condition families; verify against paradigm documentation.
  - Event spacing inconsistent: "S  1" (double space) vs "S 5" (single space) in raw labels; normalize on read.
  - Trial counts vary (506-681) indicating unbalanced classes; stratification recommended for train/test splits.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
