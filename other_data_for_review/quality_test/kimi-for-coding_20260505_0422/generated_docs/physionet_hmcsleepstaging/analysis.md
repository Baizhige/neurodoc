# HMC Sleep Staging

**Dataset**: `physionet_hmcsleepstaging` | **Year**: 2018 | **URL**: https://physionet.org/content/hmc-sleep-staging/1.0.0/
**Category**: Biological State | **Subjects**: 22 | **Files (Completed)**: 22 | **Channels**: 18 | **Sampling Rate**: 200 Hz | **Manual Review**:

## Paradigm

This dataset contains polysomnographic (PSG) recordings from 22 adult subjects (10 male, 12 female, ages 25-79) collected at the Hillel Yaffe Medical Center in Israel for sleep staging research. Each subject underwent a full-night clinical sleep study following the American Academy of Sleep Medicine (AASM) guidelines. The recordings include EEG, EOG, EMG, and ECG channels, with sleep stages manually scored by expert technicians according to AASM criteria (Wake, N1, N2, N3, REM).

## File Scan Result

> **Kernel SHA256**: `02cc5cb5405dba539353f97eabb03f558a1ad9c11afbdf15d2372f13cae3e943`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ECG` | native (raw misc in EEG file) | raw | native (raw misc in EEG file) |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks



## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
