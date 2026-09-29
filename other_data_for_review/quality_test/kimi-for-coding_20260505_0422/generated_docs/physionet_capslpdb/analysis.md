# CAP Sleep Database

**Dataset**: `physionet_capslpdb` | **Year**: 2012 | **URL**: https://physionet.org/content/capslpdb/1.0.0/
**Category**: Biological State | **Subjects**: 108 | **Files (Completed)**: 108 | **Channels**: 9 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

The CAP Sleep Database contains polysomnographic recordings from 108 subjects used for sleep staging and cyclic alternating pattern (CAP) analysis. Subjects underwent overnight sleep monitoring with EEG and other physiological signals recorded during natural sleep. The database is designed for studying sleep microstructure, particularly the detection of CAP phases which are associated with sleep instability and various sleep disorders.

## File Scan Result

> **Kernel SHA256**: `e8db40c3ba8481dacb9a0a5a1ff3b8944319db222f4477742cad7ac40a4724f9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `A1` | native (raw misc in EEG file) | raw |  |
| `A2` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

(All candidate tasks dropped during v3 schema fill — see logs.)

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
