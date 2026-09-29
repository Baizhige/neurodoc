# figshare_meng2019

**Dataset**: `figshare_meng2019` | **Year**: 2019 | **URL**: https://figshare.com/articles/dataset/EEG_data_for_Meng_et_al_2019/7618042
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 9 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from a motor imagery BCI experiment with three subjects (Subj10, Subj11, Subj12). Each subject participated in three experimental sessions, with three experiments per session. The paradigm involves motor imagery tasks, as indicated by the event structure with two event types (1 and 2) occurring in nearly equal numbers, consistent with a binary classification BCI task. Data were recorded using a 64-channel standard EEG cap at 1000 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `d11f8cf2a1dff68adaf5ebedf6674505708286aec9a5ef0ab338b664eb90fa8c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1` | 7679 | event | raw |  |
| `2` | 7681 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | complete | 64-channel standard cap |
| `experiment` | complete | Values: 1, 2, 3 |
| `handedness` | missing |  |
| `session` | complete | Values: 01, 02, 03 |
| `sex` | missing |  |
| `subject_id` | complete | Values: Subj10, Subj11, Subj12 |

## Tasks



## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
