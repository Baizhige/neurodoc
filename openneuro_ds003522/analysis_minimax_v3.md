# EEG: Three-Stimulus Auditory Oddball and Rest in Acute and Chronic TBI

**Dataset**: `openneuro_ds003522` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003522
**Category**: Sensory/Response | **Subjects**: 62 | **Files (Completed)**: 196
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

This study investigates EEG markers in mild traumatic brain injury (mTBI) using a three-stimulus auditory oddball task and resting-state recordings. Participants (sub-acute mTBI patients, chronic mTBI patients, and healthy controls) passively listened to standard, novel, and target tones while performing a target detection task. Resting-state blocks with eyes open and eyes closed were also recorded. The P3a and P3b ERP components - reflecting bottom-up and top-down attentional processes - are the primary measures examined as TBI biomarkers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003522

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Standard Tone` | 194 | short | raw | Frequent standard auditory tone (non-target) |
| `Novel Tone` | 194 | short | raw | Rare novel/distractor tone eliciting P3a |
| `Target Tone` | 194 | short | raw | Rare target tone requiring button press (P3b) |
| `Eyes Open` | 196 | rest | raw | Eyes-open resting-state block marker |
| `Eyes Closed` | 196 | rest | raw | Eyes-closed resting-state block marker |
| `STATUS` | 196 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: ERP Target Detection (P300/Oddball - Binary Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Target Tone`, `Standard Tone`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Standard Tone` | 0 | Non-target frequent tone |
  | `Target Tone` | 1 | Target tone requiring button press (P3b) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2019.107125` — Three-stimulus auditory oddball with P3a (novel) and P3b (target) components as TBI biomarkers
- **Kernel Notes**: Standard vs target classification isolates P3b response. Novel tones (P3a) serve as catch trials and can be excluded or labeled as non-target depending on analysis. Verify event ID mapping from events.tsv.

### Primary Task 2: Three-Stimulus Oddball Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Standard Tone`, `Novel Tone`, `Target Tone`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Standard Tone` | 0 | Standard frequent tone (~80% of trials) |
  | `Novel Tone` | 1 | Novel distractor tone (P3a eliciting) |
  | `Target Tone` | 2 | Target tone requiring response (P3b eliciting) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2019.107125` — Three-stimulus auditory oddball paradigm examining both P3a and P3b components
- **Kernel Notes**: Class imbalance present (~80% standard, ~10% novel, ~10% target). Use weighted loss or class balancing. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Resting-State Classification (Eyes Open vs Closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Eyes Open` | 0 | Eyes-open resting-state block |
  | `Eyes Closed` | 1 | Eyes-closed resting-state block |
- **Notes**: Rest blocks are long-duration annotations. Use segmentation to create fixed-length windows within each rest block. Verify that segment boundaries align with block onsets.

### Normal Task 2: Clinical Group Classification (TBI Stratification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Standard Tone`, `Novel Tone`, `Target Tone`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sub-acute_mTBI` | 0 | Sub-acute mild TBI patient |
  | `chronic_mTBI` | 1 | Chronic mild TBI patient |
  | `control` | 2 | Healthy control |
- **Super Meta Notes**: Derived from subject metadata (not raw events). Kernel step: Parse clinical group from participant TSV file and map to epochs based on subject ID.
- **Notes**: Clinical groups (acute mTBI, chronic mTBI, controls) should be used as stratification variables. Requires merging participant demographic data with epoch labels.

## Data Quality Notes

- Eyes Open/Closed markers are resting block delimiters, not instantaneous trial events; do not epoch them as stimuli.
- Some files contain "Eyes Open: Every 1000 ms" style sub-event annotations; these are timing markers within rest blocks.
- Clinical groups (acute mTBI, chronic mTBI, controls) should be used as stratification variables.

