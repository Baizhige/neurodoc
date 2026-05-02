# Auditory Gamma Entrainment

**Dataset**: `openneuro_ds003800` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003800
**Category**: Sensory/Response | **Subjects**: 8 | **Files (Completed)**: 24 | **Manual Review**:
**Channels**: 19 | **Sampling Rate**: 250 Hz

## Paradigm

Elderly participants with dementia received 40 Hz amplitude-modulated (AM) auditory stimulation to induce gamma-band entrainment of brain oscillations. The paradigm alternated between active 40 Hz AM stimulation (Stimulus) periods and quiet rest periods. The study investigates whether auditory gamma entrainment can modulate neural oscillations in a dementia population, potentially as a therapeutic intervention. EEG was recorded using a standard 10-20 system.

## File Scan Result

> **Kernel SHA256**: `e6959baf7172128448178128b96e9921e3939b7476219ea3e516462b0f400235`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 65 | event | raw | Trial phase onset: rest |
| `Stimulus` | 78 | event | raw | Trial phase onset: stimulus |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Stimulus vs Rest Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`Rest`, `Stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Rest | 0 | Trial phase onset: rest |
  | Stimulus | 1 | Trial phase onset: stimulus |
- **Evidence**:
  - 10.18178/ijpmbs.13.1.14-18 — Binary classification of 40 Hz AM auditory stimulation periods versus quiet rest periods. Stimulus trials are 40s duration (event code 2), rest trials are 20s duration (event code 1). Six stimulus and five rest periods per session alternating throughout the 340s recording.
  - sub-001_task-AuditoryGammaEntrainment_events.json — Explicitly maps value '1' to 'Rest' and value '2' to 'Stimulus' in the Levels field under the value column.
  - sub-001_task-AuditoryGammaEntrainment_events.tsv — Shows alternating 20s Rest/40s Stimulus blocks with consistent event codes across all trials.
- **Notes**: Long-event epoching captures full stimulation/rest periods. Note that Rest epochs are only 20s duration while tmax=40s; this will result in shorter effective epochs for Rest trials. The tmax=40s is set to accommodate the longer Stimulus periods per the reference specification.

## Data Quality Notes

- Metadata conflict: File Scan Result indicates 13 subjects with complete Age/Gender data, but dataset header shows only 8 subjects with 24 completed files. The Tasks section references 13 participants in participants.tsv, suggesting some subjects may lack EEG recordings or have incomplete data.
- Missing standard BIDS fields: `age` and `sex` are missing at the EEG metadata level, though `Age` and `Gender` are available via participants.tsv (archetype B3).
- `Group` field is entirely missing, preventing group-level analyses (e.g., dementia severity stratification).
- `MMSE` coverage is partial (12/13), with one missing value; however, README and participants.tsv disagree on which subject is missing MMSE data.
- Rest recordings are missing for sub-06 and sub-13, affecting Potential Task 4 and reducing effective sample size for rest-based analyses.
- `device` field is missing, limiting reproducibility of equipment specifications.
- Rest epochs are only 20s duration while Stimulus epochs are 40s; the fixed tmax=40s in Classical Task 1 will produce shorter effective Rest epochs, which may affect classification performance.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
