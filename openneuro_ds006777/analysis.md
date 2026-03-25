# SFARI AVSRT EEG

**Dataset**: `openneuro_ds006777` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006777
**Category**: Sensory/Response | **Subjects**: 132 | **Files (Completed)**: 132 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

An audiovisual simple reaction-time task (AVSRT) in which participants press a button as quickly as possible upon detecting auditory, visual, or simultaneous audiovisual stimuli. The paradigm measures unimodal vs. multimodal stimulus processing and associated reaction times. The dataset is from the SFARI (Simons Foundation Autism Research Initiative) collection, likely including participants with autism spectrum disorder and neurotypical controls.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: reaction time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006777

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Response_button` | 46353 | short | raw | Participant button-press response |
| `Visual_stim` | 16250 | short | raw | Visual stimulus onset |
| `Audiovisual_stim` | 16130 | short | raw | Simultaneous audiovisual stimulus onset |
| `Auditory_stim` | 15995 | short | raw | Auditory stimulus onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Visual_stim`, `Audiovisual_stim`, `Auditory_stim`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Audiovisual reaction-time decoding and RT modeling
- **Task Type**: classification/regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation` and `misc`
- **Target Definition**: Stimulus modality labels (auditory/visual/audiovisual) and reaction-time target derived from stimulus-response pairing.
- **Evidence**: AVSRT paradigm is designed to compare modality effects and reaction time in simple response trials. Source: https://openneuro.org/datasets/ds006777 DOI: https://doi.org/10.18112/openneuro.ds006777.v1.0.0


### Normal Task 1: Stimulus Modality Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Three balanced modality conditions (Auditory/Visual/Audiovisual ~16000 each) well-suited for multiclass decoding. `Response_button` is a motor response event; exclude from stimulus classification if needed.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Response_button` | 0 | Button-press response |
 | `Audiovisual_stim` | 1 | Simultaneous audiovisual stimulus |
 | `Auditory_stim` | 2 | Auditory-only stimulus |
 | `Visual_stim` | 3 | Visual-only stimulus |
## Data Quality Notes

- SFARI autism cohort; likely includes participants with ASD and neurotypical controls.
- `Response_button` is a motor event marker, not a stimulus; consider excluding from stimulus decoding.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `SFARI AVSRT EEG`
