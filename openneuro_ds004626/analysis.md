# Can We Dissociate Hypervigilance to Social Threats from Altered Perceptual Decision-Making in Lonely Individualsx

**Dataset**: `openneuro_ds004626` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004626
**Category**: High-level Mental | **Subjects**: 52 | **Files (Completed)**: 52
**Channels**: 68 | **Sampling Rate**: 1000 Hz

## Paradigm

A perceptual decision-making task investigating whether lonely individuals exhibit hypervigilance toward social threats, combining Drift Diffusion Modeling (DDM) with ERP analysis. Participants viewed social and non-social threat stimuli and made rapid perceptual judgements. ERP components (P1, N2pc, LPP) and computational decision parameters were compared across loneliness severity groups.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `208` | 36977 | event | raw | High-frequency stimulus/response trigger |
| `998` | 35001 | event | raw | Secondary trigger (trial boundary/ITI) |
| `236` | 6240 | event | raw | Stimulus trigger code |
| `146` | 6239 | event | raw | Stimulus trigger code |
| `206` | 6238 | event | raw | Stimulus trigger code |
| `186` | 6238 | event | raw | Stimulus trigger code |
| `142` | 6237 | event | raw | Stimulus trigger code |
| `210` | 6233 | event | raw | Stimulus trigger code |
| `999` | 2363 | admin | raw | Trial-end/admin marker (exclude) |
| `248` | 1560 | event | raw | Trigger code |
| `255` | 1560 | admin | raw | S255 admin sync trigger (exclude) |
| `300` | 1528 | event | raw | Trigger code |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Stimulus Trigger Classification (Dot Probe Task)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`208`, `998`, `236`, `146`, `206`, `186`, `142`, `210`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `208` | 0 | High-frequency stimulus/response trigger |
  | `998` | 1 | Secondary trigger (trial boundary/ITI) |
  | `236` | 2 | Stimulus trigger code |
  | `146` | 3 | Stimulus trigger code |
  | `206` | 4 | Stimulus trigger code |
  | `186` | 5 | Stimulus trigger code |
  | `142` | 6 | Stimulus trigger code |
  | `210` | 7 | Stimulus trigger code |
- **Evidence**:
  - DOI: 10.1111/psyp.14406 — The paper analyzes EEG data from 52 participants performing a dot-probe task with angry/neutral face stimuli, extracting N2pc ERP components in 700ms epochs (tmin=-0.2s, tmax=0.5s relative to probe onset) and classifying 8 trigger codes.
- **Kernel Notes**: Exclude event IDs 255 (admin sync) and 999 (trial-end/admin) from epoching. Verify full decode table from events.tsv if more granular stimulus labels (e.g., angry vs neutral faces) are needed. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Publisher-defined BIDS task: Dot Probe
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1111/psyp.14406

## Data Quality Notes

- 30+ distinct numeric trigger codes - check events.tsv for full decode table.
- Codes 255 and 999 are administrative and must be excluded.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review