# OpenBMI Dataset

**Dataset**: `other_openbmi` | **Year**: 2019 | **URL**: http://openbmi.org | **Category**: Complex Applied | **Subjects**: 54 | **Files (Completed)**: 0 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

The OpenBMI dataset is a large-scale EEG dataset collected for motor imagery-based brain-computer interface (BCI) research. Fifty-four healthy subjects performed motor imagery tasks involving left hand, right hand, both feet, and tongue movements. EEG signals were recorded using a BrainAmp amplifier with an EasyCap 64-channel montage at 1000 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `07ceb2b2f16bf2c1d657585cb06320c60a7157e955c7fc83c9db956a58b1f906`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | complete | BrainAmp |
| `cap` | complete | EasyCap |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

(No tasks could be grounded from available references and sidecars.)

## Data Quality Notes

- No event structure was detected during file scanning; event markers may be stored in separate files or in a format not parsed by the current scan.
- All demographic fields (age, handedness, sex) are missing from the scanned metadata.
- Zero files reported as completed in the scan despite 54 subjects in the dataset, suggesting potential file access, format, or parsing issues.
- Manual review is required to verify data accessibility and event marker locations.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
