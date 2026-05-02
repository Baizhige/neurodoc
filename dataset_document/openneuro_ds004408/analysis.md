# EEG responses to continuous naturalistic speech

**Dataset**: `openneuro_ds004408` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004408
**Category**: High-level Mental | **Subjects**: 380 | **Files (Completed)**: 380 | **Channels**: 128 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants listened to continuous segments of an audiobook version of 'The Old Man and the Sea' to record EEG responses to naturalistic narrative speech and language processing. The study investigates low-frequency cortical entrainment to speech and phoneme-level processing. No trial-level event markers are present; recordings are continuous.

## File Scan Result

> **Kernel SHA256**: `8e9a91232fa4a37c6a0304f730ff7b624b2eff6c88aa6f94502449158028c102`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `continuous_speech_listening` | 380 | admin | raw | Dataset-level paradigm descriptor: continuous naturalistic speech listening task |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

(All candidate tasks dropped during v3 schema fill — see logs.)

## Data Quality Notes

- Substantial missing metadata: subject_age, subject_sex, device, hand, weight, and height fields are all incomplete or missing.
- The draft reference indicates `sex` was previously marked complete, but the authoritative scan shows it as missing — this discrepancy should be flagged for manual review.
- No trial-level event markers are present; only a single dataset-level admin event descriptor exists per recording, limiting automatic epoching options.
- All candidate tasks were dropped during v3 schema fill, indicating insufficient structured event information for automated task extraction.
- Continuous naturalistic paradigm requires external stimulus alignment (speech envelope, phoneme annotations, linguistic features) for any meaningful analysis.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
