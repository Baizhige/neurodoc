# Moral conviction and metacognitive ability shape multiple stages of information processing

**Dataset**: `openneuro_ds004067` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004067
**Category**: High-level Mental | **Subjects**: 80 | **Files (Completed)**: 83
**Channels**: 63 | **Sampling Rate**: 2000 Hz

## Paradigm

Participants evaluated their support for sociopolitical protest photographs following social influence cues from a fictitious community to assess how moral conviction and metacognitive ability modulate information processing. EEG was recorded while participants viewed protest photos (supporting or opposing social movements), received social feedback (high/low/medium agreement), and provided attitude ratings. The study examined how moral convictions and metacognitive ability shape early and late stages of social information processing.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004067

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/PhotoSupport` | ~7,290 | short | raw | Photo onset - support-framing protest image |
| `Stimulus/PhotoOppose` | ~7,290 | short | raw | Photo onset - oppose-framing protest image |
| `Stimulus/SocLow` | ~4,860 | short | raw | Social influence cue - low agreement |
| `Stimulus/SocHigh` | ~4,860 | short | raw | Social influence cue - high agreement |
| `Stimulus/SocMed` | ~4,860 | short | raw | Social influence cue - medium agreement |
| `Stimulus/Moral_Support` | ~5,688 | short | raw | Moral attitude cue - support |
| `Stimulus/Moral_Oppose` | ~5,688 | short | raw | Moral attitude cue - oppose |
| `Stimulus/Nonmoral_Oppose` | ~5,400 | short | raw | Non-moral attitude cue - oppose |
| `Stimulus/Nonmoral_Neutral` | ~4,968 | short | raw | Non-moral attitude cue - neutral |
| `Stimulus/Nonmoral_Support` | ~4,560 | short | raw | Non-moral attitude cue - support |
| `Stimulus/Resp1`-`Resp5` | variable | short | raw | Participant rating response (1-5 scale) |
| `Stimulus/ProtestStart` | ~80 | admin | raw | Block start marker |
| `Stimulus/ProtestEnd` | ~80 | admin | raw | Block end marker |
| `Stimulus/RestStart` | ~79 | rest | raw | Resting block start |
| `Stimulus/RestEnd` | ~79 | rest | raw | Resting block end |
| `Stimulus/ClipTaskStart` | ~79 | admin | raw | Clip task start |
| `Stimulus/ClipTaskEnd` | ~79 | admin | raw | Clip task end |
| `Stimulus/Social5/6start`-`end` | ~79 | admin | raw | Social clip block markers |
| `Stimulus/Heroic6/7start`-`end` | ~79 | admin | raw | Heroic clip block markers |
| `Stimulus/S 2` | ~79 | admin | raw | System/sync marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/PhotoSupport`, `Stimulus/PhotoOppose`, `Stimulus/SocLow`, `Stimulus/SocHigh`, `Stimulus/SocMed`, `Stimulus/Moral_Support`, `Stimulus/Moral_Oppose`, `Stimulus/Nonmoral_Oppose`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Sociopolitical Judgment Task
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004067 DOI: https://doi.org/10.17605/OSF.IO/8KPEF


### Normal Task 1: Support vs Oppose Photo Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: ProtestStart/End, ClipTaskStart/End, Social*start/end, Heroic*start/end, RestStart/End, and S 2 are all admin/structural markers to exclude. Resp1-Resp5 encode 5-point rating responses and can be used for regression. Social cues (SocLow/Med/High) can be used for a 3-class social influence task.

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus/PhotoSupport` | 0 | Support-framing sociopolitical protest photo |
 | `Stimulus/PhotoOppose` | 1 | Oppose-framing sociopolitical protest photo |
## Data Quality Notes

- Large number of event types; careful exclusion of admin markers required
- RestStart/RestEnd delimit resting-state blocks within the recording
- High sampling rate (2000 Hz); consider downsampling to 500-1000 Hz

## References

- **Reference**: `Moral conviction and metacognitive ability shape multiple stages of information processing`
