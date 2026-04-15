# BCIT Speed Control

**Dataset**: `openneuro_ds004122` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004122
**Category**: Complex Applied | **Subjects**: 63 | **Files (Completed)**: 63
**Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

A simulated driving task assessing driver fatigue and performance through a speed control manipulation: subjects drove under either manual speed control (maintaining speed without cruise control) or automated speed control (cruise control active), while also performing manual steering corrections for lateral vehicle perturbations. The study investigates how automation of one driving sub-task affects neural fatigue signatures.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4210` | 63 files | event | raw | Perturbation onset |
| `4220` | 63 files | event | raw | Perturbation event |
| `4230` | 63 files | event | raw | Perturbation/direction event |
| `4311` | 63 files | event | raw | Lateral perturbation type 1 |
| `4312` | 63 files | event | raw | Lateral perturbation type 2 |
| `3200` | 63 files | event | raw | Speed control state marker |
| `3111` | 63 files | event | raw | Perturbation onset |
| `3310` | 63 files | event | raw | Performance metric event |
| `1211` | 63 files | event | raw | Lane correction event |
| `1212` | 59 files | event | raw | Lane correction event |
| `1121`-`1122` | 63 files | event | raw | Driver response events |
| `1111`-`1112` | 63 files | event | raw | Driver response events |
| `2621`-`2622` | 61 files | event | raw | Behavioral response / auditory cue |
| `3112` | 59 files | event | raw | Perturbation response |
| `4411` | 5 files | event | raw | Rare event |
| `4421` | 6 files | event | raw | Rare event |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Lateral Perturbation Direction (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = [`4311`, `4312`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `4311` | 0 | Lateral perturbation - type 1 |
  | `4312` | 1 | Lateral perturbation - type 2 |
- **Evidence**: No paper evidence specifically references this dataset with this task.
- **Kernel Notes**: Verify event ID mapping from events.tsv. Speed control condition (manual vs. automated) may serve as between-subjects variable.

## Data Quality Notes

- 74-channel BioSemi ActiveTwo; 1024 Hz sampling
- Speed control condition variable requires session metadata from participants.tsv
- Full event code decoding requires BCIT codebook


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: failed

---

> **auto_eeg FAILED**: No reference is classified as 'relevant' or 'partial'. All 34 references are either irrelevant (different datasets/years/groups), junk (wrong domain), or uncertain (only administrative metadata). The dataset's clear event structure and paradigm description in analysis.md cannot compensate for the absence of supporting literature references as required by the feasibility criteria.
