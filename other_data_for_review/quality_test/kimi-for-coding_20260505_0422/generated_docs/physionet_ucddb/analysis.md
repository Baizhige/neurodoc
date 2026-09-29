# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2000 | **URL**: https://physionet.org/content/ucddb/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 | **Channels**: 7 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

This dataset contains overnight polysomnography recordings from 25 adult subjects (21 males, 4 females) with suspected sleep-disordered breathing. Each subject was recorded for approximately 8 hours of sleep using a Lifecard CF ambulatory recorder with a standard 10-20 electrode cap. Recordings include EEG, ECG, respiration (abdominal and airflow), and oxygen saturation (SpO2) signals collected during natural sleep in a clinical setting for sleep apnea diagnosis.

## File Scan Result

> **Kernel SHA256**: `6b201c9527cebf683c67f59d4490ef6008d6de145ca6f031257918a946c0f981`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `SpO2` | native (raw misc in EEG file) | raw |  |
| `abdo` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | No values found in 50 records |
| `ahi` | missing | No values found in 50 records |
| `amplifier` | complete | All 50 records: Lifecard CF |
| `bmi` | missing | No values found in 50 records |
| `cap` | complete | All 50 records: standard 10-20 |
| `handedness` | missing | No values found in 50 records |
| `odi` | missing | No values found in 50 records |
| `sex` | missing | No values found in 50 records |

## Tasks

(All candidate tasks dropped during v3 schema fill — see logs.)

## Data Quality Notes

- No event annotations were extracted during scanning (empty Event Structure table)
- All demographic fields (age, sex, BMI, handedness) and clinical indices (AHI, ODI) are missing from metadata despite being documented in the original dataset source
- 50 files from 25 subjects suggests each subject has 2 files (likely split-night recordings or separate channels), but this should be verified
- SpO2 and abdominal respiration channels are present as MISC labels but may need proper channel type assignment for sleep analysis
- Missing event annotations limit automated sleep stage scoring or apnea event detection capabilities

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
