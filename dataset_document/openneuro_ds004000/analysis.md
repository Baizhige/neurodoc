# Fribourg Ultimatum Game in Schizophrenia Study

**Dataset**: `openneuro_ds004000` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004000
**Category**: High-level Mental | **Subjects**: 43 | **Files (Completed)**: 86 | **Channels**: 132 | **Sampling Rate**: 2048 Hz | **Manual Review**:

## Paradigm

A social decision-making study investigating fairness processing and social cognition in psychosis. Patients with schizophrenia and age-matched healthy controls played the Ultimatum Game in both responder (accepting/rejecting offers) and proposer (making offers) roles across multiple experimental blocks. EEG was recorded while participants decided whether to accept or reject monetary offers presented by human or computer partners, enabling analysis of ERPs (P2, FRN, P300) related to fairness evaluation and social decision-making.

## File Scan Result

> **Kernel SHA256**: `bb5699d4c626a491c710b60079283172bc4b15d36ff7209d179aa129452861ab`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 7315 | admin | raw | Data segment boundary marker |
| `Response/R  1` | 1587 | event | raw | Participant button press response |
| `Response/R  3` | 1 | event | raw | Participant button press response (alternate code) |
| `Stimulus/S  1` | 2303 | event | raw | Stimulus onset: experimental event S1 |
| `Stimulus/S  2` | 1303 | event | raw | Stimulus onset: experimental event S2 |
| `Stimulus/S  3` | 1896 | event | raw | Stimulus onset: experimental event S3 |
| `Stimulus/S  4` | 1598 | event | raw | Stimulus onset: experimental event S4 |
| `Stimulus/S 64` | 5839 | event | raw | Trial phase onset: fixation or trial start |
| `Stimulus/S 96` | 6339 | event | raw | Trial phase onset: offer presentation |
| `Stimulus/S128` | 3681 | event | raw | Trial phase onset: decision period |
| `Stimulus/S160` | 3720 | event | raw | Trial phase onset: feedback presentation |
| `Stimulus/S193` | 239 | event | raw | Stimulus onset: condition-specific event S193 |
| `Stimulus/S194` | 262 | event | raw | Stimulus onset: condition-specific event S194 |
| `Stimulus/S195` | 311 | event | raw | Stimulus onset: condition-specific event S195 |
| `Stimulus/S196` | 625 | event | raw | Stimulus onset: condition-specific event S196 |
| `Stimulus/S197` | 774 | event | raw | Stimulus onset: condition-specific event S197 |
| `Stimulus/S198` | 564 | event | raw | Stimulus onset: condition-specific event S198 |
| `Stimulus/S199` | 281 | event | raw | Stimulus onset: condition-specific event S199 |
| `Stimulus/S200` | 227 | event | raw | Stimulus onset: condition-specific event S200 |
| `Stimulus/S201` | 215 | event | raw | Stimulus onset: condition-specific event S201 |
| `Stimulus/S225` | 413 | event | raw | Stimulus onset: condition-specific event S225 |
| `Stimulus/S226` | 410 | event | raw | Stimulus onset: condition-specific event S226 |
| `Stimulus/S227` | 412 | event | raw | Stimulus onset: condition-specific event S227 |
| `Stimulus/S228` | 413 | event | raw | Stimulus onset: condition-specific event S228 |
| `Stimulus/S229` | 417 | event | raw | Stimulus onset: condition-specific event S229 |
| `Stimulus/S230` | 413 | event | raw | Stimulus onset: condition-specific event S230 |
| `Stimulus/S231` | 422 | event | raw | Stimulus onset: condition-specific event S231 |
| `Stimulus/S232` | 400 | event | raw | Stimulus onset: condition-specific event S232 |
| `Stimulus/S233` | 420 | event | raw | Stimulus onset: condition-specific event S233 |
| `Time 0/` | 7401 | admin | raw | Time zero reference marker |
| `UserDefined/Blink` | 14850 | admin | raw | Ocular artifact: blink detected by ICA (channel 129) |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `EXG1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `EXG1`, `EXG2`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class proposer vs responder condition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 64` | 0 | proposer role: trial phase onset (fixation/trial start) |
  | `Stimulus/S128` | 0 | proposer role: trial phase onset (decision period) |
  | `Stimulus/S 96` | 1 | responder role: trial phase onset (offer presentation) |
  | `Stimulus/S160` | 1 | responder role: trial phase onset (feedback presentation) |
- **Evidence**:
  - 10.1016/j.schres.2017.05.037 — Original study comparing proposer vs responder conditions in Ultimatum Game with schizophrenia patients and healthy controls
  - 10.1016/j.schres.2023.01.029 — Reanalysis confirming proposer vs responder comparison as core task contrast
  - README — "Participants were asked to play the UG in both roles, both as responder and proposer"; task-proposer and task-responder files present
  - eeg.json — TaskName indicates separate "responder" and "proposer" tasks
  - .vmrk header samples — S 64/S128 observed in proposer files; S 96/S160 observed in responder files; distinct event codes across roles enable role classification
- **Notes**: Event codes are task-specific: S 64 and S128 appear exclusively in proposer runs, while S 96 and S160 appear exclusively in responder runs. This creates a natural 2-class classification problem where the event identity itself encodes the participant's role. The y=0/1 mapping groups all proposer-phase events together and all responder-phase events together, reflecting the binary role distinction. The epoch window (-0.2 to 0.8s) captures the ERP around trial phase onsets, covering early sensory and cognitive processing associated with role-specific task demands.

### Potential Task 1: 4-class trial phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 2 s *, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 64` | 0 | fixation or trial start |
  | `Stimulus/S 96` | 1 | offer presentation |
  | `Stimulus/S128` | 2 | decision period |
  | `Stimulus/S160` | 3 | feedback presentation |
- **Evidence**:
  - BrainVision .vmrk marker files (sub-001, sub-002, sub-003, sub-010, sub-025) — Stimulus/S 64 and Stimulus/S 96 directly observed; S128 and S160 confirmed from pre-scan event counts across all files
  - README — "The task is playing the Ultimatum Game" with proposer/responder roles; 30 repetitions per block
  - eeg.json (sub-000_task-proposer_run-1) — TaskDescription describes trial structure with offer, decision, and feedback phases
- **Notes**: Event structure supports a natural 4-class trial phase detection task based on the Ultimatum Game trial structure (fixation/trial start → offer presentation → decision period → feedback presentation). The 6s trial duration with 4 phases implies approximately 1.5s per phase; 2s window captures each phase with buffer. No direct publication reference supports this specific 4-class formulation, but the event codes and trial structure are clearly present in the data.

## Data Quality Notes

- Missing demographic metadata: subject_age, subject_sex, and device fields are not available in the dataset metadata.
- Very low count for `Response/R  3` (n=1) compared to `Response/R  1` (n=1587), suggesting alternate response code was rarely used or may be a recording artifact.
- `UserDefined/Blink` markers (n=14850) indicate automated blink detection was applied via ICA on channel 129; users should verify blink correction quality.
- EXG1 and EXG2 auxiliary channels are present but their specific roles (e.g., EOG, EMG) and units require verification.
- Event code meanings for Stimulus/S193-S233 are condition-specific but exact experimental conditions (offer fairness levels, partner types) are inferred from structure rather than explicitly documented in data headers.
- The `group` label is complete and available in participants.tsv, enabling group-level analyses.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
