# BCIT Speed Control

**Dataset**: `openneuro_ds004122` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004122
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 32 | **Channels**: 74 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

A simulated driving task assessing driver fatigue and performance through a speed control manipulation: subjects drove under either manual speed control (maintaining speed without cruise control) or automated speed control (cruise control active), while also performing manual steering corrections for lateral vehicle perturbations. The study investigates how automation of one driving sub-task affects neural fatigue signatures.

## File Scan Result

> **Kernel SHA256**: `346e3a371a26942ac2dcdada07e4c7eacaac1795abc6836ff6e497cd309f904c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `correction_duration` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `perturbation_to_correction_latency` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `proactive_reactive_index` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `time_into_session` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `correction_duration`, `perturbation_to_correction_latency`, `proactive_reactive_index`, `time_into_session`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Subject count discrepancy: existing draft states 63 subjects but File Scan Result and Tasks indicate 32 subjects with complete year_of_birth data
- All 32 subjects have group=Normal with no clinical/control contrast available
- subject_age and subject_sex fields are missing for all subjects; only year_of_birth is available for demographic prediction
- device field is missing; equipment details (74-channel BioSemi ActiveTwo) come from prior documentation, not from scanned metadata
- Event structure table in File Scan Result is empty; no events were detected during scan despite prior documentation listing extensive event codes
- MISC channels present in raw files (correction_duration, perturbation_to_correction_latency, proactive_reactive_index, time_into_session) require verification of role and units
- Speed control condition (manual vs. automated) referenced in paradigm description is not present in scanned info fields; may require session-level metadata extraction

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
