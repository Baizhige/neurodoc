# EEG: Visual Working Memory in Acute TBI

**Dataset**: `openneuro_ds003523` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003523
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 219 | **Manual Review**: Pending
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

A visual working memory task with intermittent mind-wandering probes was administered longitudinally to healthy controls and patients with sub-acute mild traumatic brain injury (mTBI). Participants memorized visual stimuli during encoding, maintained them across a delay period, and responded to probe stimuli. Occasional mind-wandering probes assessed attentional state. The dataset spans multiple time points post-injury to track recovery of executive functioning, with ERP markers (P3b) serving as neurophysiological outcome measures.

## File Scan Result

> **Kernel SHA256**: `b66177aaa892f125082a49a625f590b686f8a1f18bff06511c47fb48374ad921`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Mind Wandering Probe` | 6434 | event | raw | Mind-wandering probe stimulus onset |
| `Mind Wandering: No` | 4300 | event | raw | Probe response indicating on-task state |
| `Mind Wandering: Yes` | 2002 | event | raw | Probe response indicating mind-wandering state |
| `Question Mark Probe: "In"` | 16098 | event | raw | Working memory probe response "In" (item in memory) |
| `Question Mark Probe: "Out"` | 16096 | event | raw | Working memory probe response "Out" (item not in memory) |
| `Response: Correct` | 5375 | event | raw | Correct behavioral response |
| `Response: Inorrect` | 26476 | event | raw | Incorrect behavioral response |
| `STATUS` | 1574 | event | raw | System status marker |
| `Stim Onset: 3 Red` | 10833 | event | raw | Visual stimulus onset (3 red items) |
| `Stim Onset: 3 Red + 2 yellow` | 10898 | event | raw | Visual stimulus onset (3 red + 2 yellow items) |
| `Stim Onset: 5 Red` | 10858 | event | raw | Visual stimulus onset (5 red items) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Mind-Wandering State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`Mind Wandering Probe`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `Mind Wandering: Yes` | 0 | Mind-wandering state (off-task, probe response indicating self-reported wandering) |
  | `Mind Wandering: No` | 1 | On-task state (probe response indicating sustained attention) |
- **Evidence**:
  - DOI: 10.1111/ejn.14863 — SVM classifiers on EEG alpha oscillations distinguish mind-wandering from on-task states based on participant self-reports during visual search and SART tasks
- **Kernel Notes**: Extract epochs time-locked to 'Mind Wandering Probe' stimulus events (6434). Use 'Mind Wandering: Yes' (2002, y=0) and 'Mind Wandering: No' (4300, y=1) response events to derive binary labels. Event ID mapping differs from generic descriptions in original analysis.md—verify label mapping carefully in events.tsv. The -1s to 2s window captures pre-probe baseline, probe processing (P3b), and response preparation phases.

---

### Potential Task 1: Mind-Wandering Intensity Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Mind Wandering Probe`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `Mind Wandering Probe` | Needs verification | Continuous mind-wandering intensity score from probe responses (1-7 scale expected; verify exact value encoding in events.tsv) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2017.00365 — SVR regression predicts mind-wandering intensity (1-7 scale) from EEG power and coherence features during Sustained Attention to Response Task
- **Kernel Notes**: Extract epochs time-locked to 'Mind Wandering Probe' stimulus onsets. Map response values to 1-7 Likert scale for regression target. Requires extracting rating information from events.tsv stimulus/response columns or annotations. The short -0.2s to 0.8s window focuses on P3b component relevant to probe evaluation. Verify response value extraction from events.tsv parsing.

---

### Potential Task 2: Memory Stimulus vs. Retrieval Probe Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stim Onset: 3 Red`, `Stim Onset: 3 Red + 2 yellow`, `Stim Onset: 5 Red`, `Question Mark Probe: "In"`, `Question Mark Probe: "Out"`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `Stim Onset: 3 Red` | 0 | Memory encoding stimulus (3 red items) |
  | `Stim Onset: 3 Red + 2 yellow` | 0 | Memory encoding stimulus (3 red + 2 yellow items) |
  | `Stim Onset: 5 Red` | 0 | Memory encoding stimulus (5 red items) |
  | `Question Mark Probe: "In"` | 1 | Retrieval probe (memory check: response "In") |
  | `Question Mark Probe: "Out"` | 1 | Retrieval probe (memory check: response "Out") |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.116978 — EEG classification of encoding vs. retrieval phases in working memory tasks distinguishes distinct neural signatures
- **Kernel Notes**: Group 'Stim Onset' variants (10833, 10898, 10858) as encoding phase (y=0) and 'Question Mark Probe' variants (16098, 16096) as retrieval phase (y=1). The -0.2s to 1.0s window captures early visual components (P1/N1) and memory-related processing. Longitudinal design: multiple sessions per subject require session-level epoch indexing. Verify stimulus type annotations in events.tsv for additional label refinement.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
