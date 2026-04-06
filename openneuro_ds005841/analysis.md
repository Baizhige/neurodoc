# EEG Experiment measuring ERPs in VR

**Dataset**: `openneuro_ds005841` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005841
**Category**: Complex Applied | **Subjects**: 48 | **Files (Completed)**: 288 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

An investigation of event-related potentials (ERPs) during visual tasks performed within a virtual reality (VR) environment. Stimuli vary along two orthogonal dimensions: lighting (DARK vs LIGHT) and reference type (RAND = random/unpredictable vs REF = reference/predictable). The 2x2 design yields four event codes measuring visual ERP responses under prediction-error conditions.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RAND_DARK` | 288 | event | raw | Random (unpredictable) stimulus - dark condition |
| `RAND_LIGHT` | 288 | event | raw | Random (unpredictable) stimulus - light condition |
| `REF_DARK` | 288 | event | raw | Reference (predictable) stimulus - dark condition |
| `REF_LIGHT` | 288 | event | raw | Reference (predictable) stimulus - light condition |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: VR Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`RAND_DARK`, `RAND_LIGHT`, `REF_DARK`, `REF_LIGHT`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `RAND_DARK` | 0 | Random (unpredictable) dark stimulus |
  | `RAND_LIGHT` | 1 | Random (unpredictable) light stimulus |
  | `REF_DARK` | 2 | Reference (predictable) dark stimulus |
  | `REF_LIGHT` | 3 | Reference (predictable) light stimulus |
- **Kernel Notes**: Apply bandpass filter (1-40 Hz), then epoch with tmin=-0.2s, tmax=1.0s around each event. Balanced 4-class design (288 trials per class). Primary contrasts: RAND vs REF (prediction error) and DARK vs LIGHT (luminance).

## Data Quality Notes

- VR environment may introduce motion artifacts; apply ICA for artifact removal.
- 48 subjects x 6 sessions = 288 files; verify session-level consistency.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review