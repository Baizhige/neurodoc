# Auditory-Visual Shift Study

**Dataset**: `openneuro_ds002893` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002893
**Category**: Sensory/Response | **Subjects**: 49 | **Files (Completed)**: 52 | **Channels**: 36.0 | **Sampling Rate**: 250.0 Hz

## Paradigm

An interleaved dual-oddball task in which subjects selectively attended to either auditory or visual stimuli while switching between modalities based on spoken and printed attention cue instructions. The study investigated modality-specificity of sensory aging in vision and audition using event-related potentials. Attention states (`attend_auditory`, `attend_visual`) are sustained conditions lasting multiple trials; `shift_attention` marks the transition cue between modalities.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002893

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attend_auditory` | 51 (files) | long | raw | Sustained auditory attention block |
| `attend_visual` | 51 (files) | long | raw | Sustained visual attention block |
| `shift_attention` | 49 (files) | admin | raw | Attention shift cue - transition marker between blocks |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds002893 DOI: https://doi.org/10.18112/openneuro.ds002893.v2.0.0


### Normal Task 1: Attention Modality Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `shift_attention` is a transition cue - it marks the moment of modality switching, not a sustained state; treat as admin. The `attend_*` events mark the onset of sustained attention blocks of multiple seconds.

 | Event | y | Meaning |
 |-------|---|---------|
 | `attend_auditory` | 0 | Sustained auditory attention block |
 | `attend_visual` | 1 | Sustained visual attention block |
## Data Quality Notes

- `shift_attention` marks attention shift cues - not a sustained state; exclude from classification target.
- Count column reflects files-with-event (51 subjects out of 52 files), not per-session trial count.
- Older adult participants (aging study); verify age distribution from participants.tsv.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Modality-specificity of sensory aging in vision and audition: evidence from event-related potentials. Brain research, 1215, pp.53-68.`
