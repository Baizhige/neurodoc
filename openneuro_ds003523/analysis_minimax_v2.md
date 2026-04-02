# EEG: Visual Working Memory in Acute TBI

**Dataset**: `openneuro_ds003523` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003523
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 219
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

A visual working memory task with intermittent mind-wandering probes was administered longitudinally to healthy controls and patients with sub-acute mild traumatic brain injury (mTBI). Participants memorized visual stimuli during encoding, maintained them across a delay period, and responded to probe stimuli. Occasional mind-wandering probes assessed attentional state. The dataset spans multiple time points post-injury to track recovery of executive functioning, with ERP markers (P3b) serving as neurophysiological outcome measures.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003523

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stim Onset` | 657 | short | raw | Visual study stimulus onset |
| `Question Mark Probe` | 434 | short | raw | Working memory probe stimulus |
| `Response` | 434 | short | raw | Participant button-press response |
| `Mind Wandering` | 406 | short | raw | Mind-wandering probe response marker |
| `Mind Wandering Probe` | 217 | short | raw | Mind-wandering probe stimulus |
| `STATUS` | 219 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stim Onset`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Mind-Wandering vs On-Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 3.0 s *, target_events = [`Mind Wandering Probe`, `Mind Wandering`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mind Wandering` | 0 | Mind-wandering state (probe response indicating off-task) |
  | `Mind Wandering Probe` | 1 | On-task state (probe response indicating focused attention) |
- **Evidence**:
  - DOI: 10.1111/ejn.14863 — SVM classifiers on EEG alpha oscillations distinguish mind-wandering from on-task states based on participant self-reports during visual search and SART tasks
- **Kernel Notes**: Extract epochs time-locked to Mind Wandering Probe stimulus events. Use corresponding Mind Wandering response events to derive binary labels (mind-wandering vs on-task). Verify event ID mapping from events.tsv. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Mind-Wandering Intensity Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Mind Wandering Probe`, `Response`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `Mind Wandering Probe` | 1-7 | Continuous MW intensity score from probe responses |
- **Evidence**:
  - DOI: 10.3389/fnhum.2017.00365 — SVR regression predicts mind-wandering intensity (1-7 scale) from EEG power and coherence features during Sustained Attention to Response Task
- **Kernel Notes**: Extract epochs time-locked to mind-wandering probe stimuli. Map response values to 1-7 Likert scale for regression target. Requires extracting rating information from events or annotations. Verify event ID mapping and response value extraction from events.tsv.

### Normal Task 1: Stimulus type classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `ERPs predict symptomatic distress and recovery in sub-acute mild traumatic brain injury. Neuropsychologia, 2019. DOI: 10.1016/j.neuropsychologia.2019.107125`
