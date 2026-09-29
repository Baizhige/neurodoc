# TUH EEG Abnormal Corpus

**Dataset**: `tuh_eeg_abnormal` | **Year**: 2019 | **URL**: https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml
**Category**: Biological State | **Subjects**: 2983 | **Files (Completed)**: 2983 | **Channels**: Variable (typically 21-22) | **Sampling Rate**: Variable (typically 250 or 512) Hz | **Manual Review**:

## Paradigm

The Temple University Hospital (TUH) EEG Abnormal Corpus is a large-scale clinical EEG dataset collected for automated abnormality detection. Subjects are patients who underwent routine clinical EEG recordings at Temple University Hospital. The dataset contains approximately 2983 EEG recordings with associated clinical labels indicating whether the recording is normal or abnormal. Recordings were collected using standard 10-20 electrode placement systems with varying channel configurations across different clinical amplifiers.

## File Scan Result

> **Kernel SHA256**: `31d431cf9381d82dc1ca27b50236b23b40a65f402fb05343008cea9e0f664502`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `BURSTS` | native (raw misc in EEG file) | raw |  |
| `IBI` | native (raw misc in EEG file) | raw |  |
| `PHOTIC` | native (raw misc in EEG file) | raw |  |
| `SUPPR` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Value '1' present in all 2983 records; unit (years/months) not specified |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

(No tasks could be grounded from available references and sidecars.)

## Data Quality Notes

- Age field marked complete but value '1' appears in all 2983 records, suggesting placeholder or coded value rather than actual ages; unit (years/months) not specified.
- Sex, handedness, amplifier, and cap metadata are completely missing.
- Sampling rate and channel count vary across recordings (not standardized), requiring per-file inspection.
- MISC channels (BURSTS, IBI, PHOTIC, SUPPR) are present as native annotations but no event structure with event IDs was extracted.
- Clinical abnormality labels are the primary ground truth but are not represented in the event structure table.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
