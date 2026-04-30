# Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts

**Dataset**: `openneuro_ds004784` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004784
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 10 | **Channels**: 264 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Technical validation study using an electrically conductive head phantom to simulate brain activity under various artifact conditions (motion, muscle, eye movements) for testing EEG cleaning algorithms. The phantom dataset contains 264-channel EEG recordings with 30 total event markers across 10 files, representing different artifact conditions for algorithm validation.

## File Scan Result

> **Kernel SHA256**: `378b290db8f4cdd7ef26187d6b45c976123447f38a189a6cae217bdfccca83dd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65343` | 10 | admin | raw | Recording onset/initial trigger (metadata labels 'other numbered events' as nonsensical to be ignored) |
| `65471` | 20 | event | raw | Trial phase onset: trial start and stop (5 minutes between markers) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

(All candidate tasks dropped during v3 schema fill — see logs.)

## Data Quality Notes

- No human subjects; data collected from conductive head phantom, so `subject_age` and `subject_sex` fields are not applicable.
- Event ID `65343` labeled as admin trigger with note that metadata describes 'other numbered events' as nonsensical and to be ignored; this conflicts with prior draft interpretation of these as artifact condition markers.
- Event ID `65471` described as trial phase onset with 5-minute intervals between markers, suggesting long continuous segments rather than discrete trial structure.
- `device` field is missing across all files, limiting hardware provenance information.
- `group` field is complete and indicates 'phantom' category, confirming non-human data source.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
