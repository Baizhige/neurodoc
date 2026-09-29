# Kaggle INRIA BCI Challenge 2015

**Dataset**: `kaggle_inria` | **Year**: 2015 | **URL**: https://www.kaggle.com/c/inria-bci-challenge
**Category**: Action/Output | **Subjects**: 26 | **Files (Completed)**: 135 | **Channels**: 56 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset was created for the INRIA BCI Challenge 2015 on Kaggle. Subjects performed a two-class motor imagery task involving imagined hand or foot movements. EEG was recorded using a BrainAmp MR plus amplifier (Brain Products) with an extended 10-20 cap configuration of 61 channels. The data was collected at a high sampling rate of 1000 Hz and later downsampled for the competition.

## File Scan Result

> **Kernel SHA256**: `0af01e665f4689e34f337e49b27c64aeceafc351d81566ea70831fa0f90c5b85`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | partial (130/135) | BrainAmp MR plus (Brain Products) |
| `cap` | partial (130/135) | extended 10-20 (61 channels) |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

(No tasks could be grounded from available references and sidecars.)

## Data Quality Notes

- No event markers were detected in the scanned files; event structure table is empty.
- Subject metadata (age, sex, handedness) is completely missing from all files.
- Amplifier and cap information is only partially available (130/135 files).
- Channel count discrepancy: metadata indicates 61 channels (extended 10-20), but dataset description suggests 56 channels were used; this requires manual verification.
- The high 1000 Hz sampling rate may require downsampling for practical BCI analysis.
- No task information could be automatically extracted; manual review of competition documentation is needed to confirm paradigm details.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
