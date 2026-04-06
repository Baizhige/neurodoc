# EEG: Visual Working Memory in Acute TBI

**Dataset**: `openneuro_ds003523` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003523
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 219
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

A visual working memory task with intermittent mind-wandering probes was administered longitudinally to healthy controls and patients with sub-acute mild traumatic brain injury (mTBI). Participants memorized visual stimuli during encoding, maintained them across a delay period, and responded to probe stimuli. Occasional mind-wandering probes assessed attentional state. The dataset spans multiple time points post-injury to track recovery of executive functioning, with ERP markers (P3b) serving as neurophysiological outcome measures.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stim Onset` | 657 | event | raw | Visual study stimulus onset |
| `Question Mark Probe` | 434 | event | raw | Working memory probe stimulus |
| `Response` | 434 | event | raw | Participant button-press response |
| `Mind Wandering` | 406 | event | raw | Mind-wandering probe response marker |
| `Mind Wandering Probe` | 217 | event | raw | Mind-wandering probe stimulus |
| `STATUS` | 219 | admin | raw | System status marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stim Onset`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Mind-Wandering vs On-Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 3.0 s *, target_events = [`Mind Wandering Probe`, `Mind Wandering`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mind Wandering` | 0 | Mind-wandering state (probe response indicating off-task) |
  | `Mind Wandering Probe` | 1 | On-task state (probe response indicating focused attention) |
- **Evidence**:
  - DOI: 10.1111/ejn.14863 — SVM classifiers on EEG alpha oscillations distinguish mind-wandering from on-task states based on participant self-reports during visual search and SART tasks
- **Kernel Notes**: Extract epochs time-locked to Mind Wandering Probe stimulus events. Use corresponding Mind Wandering response events to derive binary labels (mind-wandering vs on-task). Verify event ID mapping from events.tsv. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Mind-Wandering Intensity Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Mind Wandering Probe`, `Response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `Mind Wandering Probe` | 1-7 | Continuous MW intensity score from probe responses |
- **Evidence**:
  - DOI: 10.3389/fnhum.2017.00365 — SVR regression predicts mind-wandering intensity (1-7 scale) from EEG power and coherence features during Sustained Attention to Response Task
- **Kernel Notes**: Extract epochs time-locked to mind-wandering probe stimuli. Map response values to 1-7 Likert scale for regression target. Requires extracting rating information from events or annotations. Verify event ID mapping and response value extraction from events.tsv.

### Potential Task 1: Stimulus type classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Longitudinal dataset; multiple sessions per subject across recovery timepoints. Mind-wandering probes can support on-task vs off-task classification with careful labeling.

| Event | y | Meaning |
|-------|---|------|
| `Stim Onset` | 0 | Memory stimulus presentation (encoding phase) |
| `Question Mark Probe` | 1 | Probe stimulus presentation (retrieval stage) |

## Data Quality Notes

- Longitudinal design: multiple sessions per subject at different post-injury timepoints.
- Clinical group and time-point information in participants.tsv; use as stratification variables.
- Mind Wandering Probe and Mind Wandering events can be used to classify attentional state.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review