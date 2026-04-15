# Fribourg Ultimatum Game in Schizophrenia Study

**Dataset**: `openneuro_ds004000` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004000
**Category**: High-level Mental | **Subjects**: 43 | **Files (Completed)**: 86 | **Channels**: 132 | **Sampling Rate**: 2048 Hz
**Manual Review**: Pending

## Paradigm

A social decision-making study investigating fairness processing and social cognition in psychosis. Patients with schizophrenia and age-matched healthy controls played the Ultimatum Game in both responder (accepting/rejecting offers) and proposer (making offers) roles across multiple experimental blocks. EEG was recorded while participants decided whether to accept or reject monetary offers presented by human or computer partners, enabling analysis of ERPs (P2, FRN, P300) related to fairness evaluation and social decision-making.

## File Scan Result

> **Kernel SHA256**: `be7cd81d21e6eea509dcc4e38668159d2168b9f6425faca05ccc6b9f56c18a72`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 7315 | event | raw | Segment boundary marker |
| `Response/R  1` | 1587 | event | raw | Button press response (accept) |
| `Response/R  3` | 1 | event | raw | Button press response (reject) |
| `Stimulus/S  1` | 2303 | event | raw | Phase/instruction marker |
| `Stimulus/S  2` | 1303 | event | raw | Phase/instruction marker |
| `Stimulus/S  3` | 1896 | event | raw | Phase/instruction marker |
| `Stimulus/S  4` | 1598 | event | raw | Phase/instruction marker |
| `Stimulus/S 64` | 5839 | event | raw | Offer onset - responder condition block 1 |
| `Stimulus/S 96` | 6339 | event | raw | Offer onset - responder condition block 2 |
| `Stimulus/S128` | 3681 | event | raw | Offer onset - responder condition block 3 |
| `Stimulus/S160` | 3720 | event | raw | Offer onset - responder condition block 4 |
| `Stimulus/S193` | 239 | event | raw | Low offer marker (unfair) - partner type A |
| `Stimulus/S194` | 262 | event | raw | Offer marker - partner type A |
| `Stimulus/S195` | 311 | event | raw | Offer marker - partner type A |
| `Stimulus/S196` | 625 | event | raw | Offer marker - partner type A |
| `Stimulus/S197` | 774 | event | raw | Offer marker - partner type A |
| `Stimulus/S198` | 564 | event | raw | Offer marker - partner type A |
| `Stimulus/S199` | 281 | event | raw | Offer marker - partner type A |
| `Stimulus/S200` | 227 | event | raw | Offer marker - partner type A |
| `Stimulus/S201` | 215 | event | raw | High offer marker (fair) - partner type A |
| `Stimulus/S225` | 413 | event | raw | Low offer marker (unfair) - partner type B |
| `Stimulus/S226` | 410 | event | raw | Offer marker - partner type B |
| `Stimulus/S227` | 412 | event | raw | Offer marker - partner type B |
| `Stimulus/S228` | 413 | event | raw | Offer marker - partner type B |
| `Stimulus/S229` | 417 | event | raw | Offer marker - partner type B |
| `Stimulus/S230` | 413 | event | raw | Offer marker - partner type B |
| `Stimulus/S231` | 422 | event | raw | Offer marker - partner type B |
| `Stimulus/S232` | 400 | event | raw | Offer marker - partner type B |
| `Stimulus/S233` | 420 | event | raw | High offer marker (fair) - partner type B |
| `Time 0/` | 7401 | event | raw | Recording start time marker |
| `UserDefined/Blink` | 14850 | admin | raw | Blink artifact marker |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Extra channels storing auxiliary biological signals
- **Candidate Labels**: `EXG1`, `EXG2`
- **Kernel Note**: Verify channel roles and units. These may contain EOG or other auxiliary recordings.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Group Classification - Schizophrenia vs Healthy Controls during Ultimatum Game Responder Condition (ERP Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 64` | 0 | Healthy control (HC) participant |
  | `Stimulus/S 64` | 1 | Schizophrenia patient (SCZ) |
- **Super Meta Notes**: Labels derived from clinical diagnosis (participants.tsv) not raw event markers. Kernel must load participant diagnosis and merge with epoch labels based on subject ID. The stimulus onset events S64/S96/S128/S160 represent offer/condition markers in the responder condition.
- **Evidence**:
  - DOI: 10.1016/j.schres.2017.05.037 — EEG study investigates differences in ERPs (P2, FRN) between schizophrenic patients and healthy controls during Ultimatum Game responder condition, finding reduced FRN amplitude in patients. Validates epoch window centering on stimulus onset for ERP component extraction.
- **Kernel Notes**: Extract epochs aligned to stimulus onset markers; merge with participant group labels from participants.tsv by subject ID; verify mapping of S64/S96/S128/S160 to responder condition from events.tsv; exclude blink artifacts marked via UserDefined/Blink.

### Classical Task 2: Group Classification - Schizophrenia vs Healthy Controls during Ultimatum Game Responder Condition (Functional Connectivity)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.7 s, overlap = 0.0, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Segment | y | Meaning |
  |---------|---|---------|
  | Any segment | 0 | Healthy control (HC) participant |
  | Any segment | 1 | Schizophrenia patient (SCZ) |
- **Super Meta Notes**: Labels derived from clinical diagnosis (participants.tsv) not raw event markers. Analysis focuses on pre-stimulus window (-0.7s to 0s) during responder condition. Kernel must compute functional connectivity metrics within alpha band (8-13 Hz) for each segment.
- **Evidence**:
  - DOI: 10.1016/j.schres.2023.01.029 — Uses openneuro_ds004000 dataset to analyze EEG dynamic functional connectivity comparing healthy controls and schizophrenia patients during Ultimatum Game responder condition, finding significant fronto-occipital alpha-band connectivity differences in pre-stimulus window. Confirms dataset identity and supports segmentation approach.
- **Kernel Notes**: Segment continuous data using 0.7s sliding windows aligned to stimulus onset events with no overlap; compute imaginary coherence in alpha band (8-13 Hz); merge segment labels with participant clinical diagnosis from participants.tsv; exclude segments containing blink artifacts.

### Potential Task 1: Button Press Response Classification during Ultimatum Game Decision
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.8 s, target_events = [`Response/R 1`, `Response/R 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Response/R 1` | 0 | Accept offer response |
  | `Response/R 1` | 1 | Reject offer response |
  | `Response/R 3` | 0 | Accept offer response |
  | `Response/R 3` | 1 | Reject offer response |
- **Potential Meta Notes**: Response events R1/R3 indicate button presses for accept/reject decisions. However, these events appear in only 6/1 files respectively, suggesting alternative response encoding or response-locked analysis may require epoching from preceding stimulus events. Behavioral analysis of accept/reject patterns is plausible from paradigm alone.
- **Evidence**: N/A
- **Kernel Notes**: Verify response event coding scheme in events.tsv; if R1/R3 presence is limited, consider epoching from stimulus onset and aligning to response events post-hoc; verify mapping of R1 vs R3 to accept/reject.

### Normal Task 1: Fairness Processing Analysis during Ultimatum Game Responder Condition
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`Stimulus/S193`, `Stimulus/S194`, `Stimulus/S195`, `Stimulus/S196`, `Stimulus/S197`, `Stimulus/S198`, `Stimulus/S199`, `Stimulus/S200`, `Stimulus/S201`, `Stimulus/S225`, `Stimulus/S226`, `Stimulus/S227`, `Stimulus/S228`, `Stimulus/S229`, `Stimulus/S230`, `Stimulus/S231`, `Stimulus/S232`, `Stimulus/S233`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S193`-`S201` | 0-8 | Offer amount (fairness condition) |
  | `Stimulus/S225`-`S233` | 0-8 | Offer amount (fairness condition) |
- **Normal Meta Notes**: Condition-specific markers (S193-S233) encode offer types representing different fairness levels. These markers appear in 28-42 files suggesting variable condition presentation across participants. FRN and P300 ERP components should differentiate between unfair/fair offers.
- **Evidence**: DOI: 10.1016/j.schres.2017.05.037 — Supports fairness processing analysis via ERP components (FRN, P2) modulated by offer unfairness.
- **Kernel Notes**: Map condition-specific markers to offer values using events.tsv; include only participants with complete condition presentation; verify S193-S201 and S225-S233 marker correspondence to different offer types.