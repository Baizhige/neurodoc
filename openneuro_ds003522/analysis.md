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

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://doi.org/10.1016/j.neuropsychologia.2019.107125


### Normal Task 1: Oddball three-category classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Classic 3-stimulus oddball. Standard tones are ~80% frequent (~184/file), novel and target each ~10% (~38/file). Class imbalance: undersample standards or weight loss. Eyes-open/closed events are resting-state block markers lasting several minutes each and are not trial-level stimuli.

| Event | y | Meaning |
 |-------|---|------|
| `Standard Tone` | 0 | Standard frequent tone |
| `Novel Tone` | 1 | Novel interference tone (P3a) |
| `Target Tone` | 2 | Target pitch (P3b) |
## Data Quality Notes

- Eyes Open/Closed markers are resting block delimiters, not instantaneous trial events; do not epoch them as stimuli.
- Some files contain "Eyes Open: Every 1000 ms" style sub-event annotations; these are timing markers within rest blocks.
- Clinical groups (acute mTBI, chronic mTBI, controls) should be used as stratification variables.

## References

- **Reference**: `ERPs predict symptomatic distress and recovery in sub-acute mild traumatic brain injury. Neuropsychologia, 2019. DOI: 10.1016/j.neuropsychologia.2019.107125`
