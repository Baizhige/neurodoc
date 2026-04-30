# EEG: Visual Working Memory + Cabergoline Challenge

**Dataset**: `openneuro_ds003519` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003519
**Category**: High-level Mental | **Subjects**: 27 | **Files (Completed)**: 54 | **Manual Review**: Pending
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a visuospatial working memory task under a double-blind Cabergoline (dopamine D2/D3 agonist) drug challenge to investigate pharmacological modulation of working memory processing. The task involved memorizing spatial locations of stimuli followed by a probe stimulus requiring a match/non-match judgment. Distractor stimuli were presented during the retention interval. The study examines individual differences in working memory capacity and dopaminergic modulation. Two sessions per subject (drug vs placebo crossover design) with 54 total files (27 subjects × 2 sessions).

## File Scan Result

> **Kernel SHA256**: `1cb8589b573d43f9a98bd9145188ef7418a29b000ebe134761dc3b9b6d18d0f4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 2688 | event | raw | Fixation cross onset (baseline/trial start marker) |
| `S  2` | 2690 | event | raw | Trial-level marker (stimulus preparation/fixation break) |
| `S  3` | 2699 | event | raw | Delay interval marker (pre-distractor period) |
| `S100` | 4049 | event | raw | Memory stimulus onset (encoding phase) |
| `S101` | 4048 | event | raw | Probe stimulus presentation (retrieval/decision phase) |
| `S200` | 938 | event | raw | Distractor stimulus onset (low load condition) |
| `S201` | 7089 | event | raw | Distractor stimulus onset (high load condition) |
| `boundary` | 54 | event | raw | Data segment boundary marker (continuous recording breaks) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Working Memory Encoding vs Retrieval Phase Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S100`, `S101`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `S100` | 0 | Memory stimulus onset (encoding phase) |
  | `S101` | 1 | Probe stimulus presentation (retrieval/decision phase) |
- **Evidence**:
  - DOI: 10.3758/s13415-018-0584-6 — Original source paper defining the VSWM paradigm with Stim Onset (encoding) and Question Mark Probe (retrieval) events; epoch parameters tmin=-0.2s, tmax~1.5s for probe-locked ERPs
- **Kernel Notes**: Map actual file event codes (S100/S101) to paradigm-defined stimulus types based on timing patterns. S100 with higher count (4049 vs 4048) likely corresponds to study stimulus; S101 to probe. Epoch window captures ERP components: P1, N1 for encoding; N2pc, contralateral delay activity for retrieval. Session (drug vs placebo) can be included as covariate at super level. **NOTE**: Original analysis.md documents `Stim Onset`/`Question Mark Probe` but actual files contain `S100`/`S101` — verify mapping against BIDS sidecar files.

### Potential Task 1: Distractor Interference Effect Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S200`, `S201`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `S200` | 0 | Standard load condition (e.g., 3-target trials) |
  | `S201` | 1 | High load condition with distractors (e.g., 3+2 distractor trials) |
- **Evidence**: No direct DOI reference; task is plausible from paradigm description.
- **Kernel Notes**: Paradigm includes distractor stimuli during retention interval to probe working memory capacity. Original paper (10.3758/s13415-018-0584-6) compares Condition 3 vs Condition 3+2 (distractor effect). S200/S201 event codes may correspond to different load conditions. Requires verification against stimulus presentation logs or behavioral data (response accuracy/RT) to confirm label mapping.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
