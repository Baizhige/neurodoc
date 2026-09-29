# ODE (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004850` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004850
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

An EEG dataset (ODE) recorded during a social-cognitive paradigm with hierarchically encoded stimulus conditions. Shares the identical event structure with the STRONG (ds004849) and InsurgentCivilian (ds004852) datasets, suggesting these are companion recordings from the same experimental series. The single aggregated file requires events.tsv decoding for full interpretation.

## File Scan Result

> **Kernel SHA256**: `31636b65a6427342d9c506e28c468dea21e109d2a46056099133515cdfd5f388`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- No events detected in file scan result, contradicting the draft's detailed event structure description and task definitions with specific event IDs.
- All subject metadata fields (age, sex, device) are missing, preventing demographic and equipment characterization.
- Single aggregated file with only 1 subject and 1 completed file severely limits generalizability and subject-level analysis.
- Sampling rate of 128 Hz is relatively low for ERP analysis, potentially limiting temporal resolution of cognitive components.
- Event table in File Scan Result is completely empty despite draft referencing 12-class paradigm with specific event codes (2200, 72011, 52011, etc.).
- Companion dataset relationship to ds004849 and ds004852 claimed but cannot be verified from current scan data.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
