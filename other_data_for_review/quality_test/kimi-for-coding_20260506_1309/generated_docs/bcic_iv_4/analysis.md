# BCI Competition IV Dataset 4

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: http://www.bbci.de/competition/iv/desc_4.html
**Category**: Action/Output | **Subjects**: 5 | **Files (Completed)**: 5 | **Channels**: 62 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset contains continuous finger flexion data from 5 subjects who performed self-paced finger movements. Subjects were instructed to move their fingers in a continuous, fluid manner rather than discrete movements. EEG was recorded using 62 channels while subjects performed naturalistic finger flexion tasks, with the goal of predicting continuous finger position from neural signals.

## File Scan Result

> **Kernel SHA256**: `b4608621080accfb2db482cebebc6ad2224669d3e80dabffd80c1fc36192ac8e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `continuous_finger_flexion` | 3 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `train_dg_0` | native (raw misc in EEG file) | raw |  |
| `train_dg_1` | native (raw misc in EEG file) | raw |  |
| `train_dg_2` | native (raw misc in EEG file) | raw |  |
| `train_dg_3` | native (raw misc in EEG file) | raw |  |
| `train_dg_4` | native (raw misc in EEG file) | raw |  |

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
