# Auditory and Visual Rhythm Omission EEG

**Dataset**: `openneuro_ds002218` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002218
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 18
**Channels**: 32 | **Sampling Rate**: 256 Hz

## Paradigm

Participants passively perceived rhythmic auditory tone sequences and visual flashing stimuli that occasionally omitted an expected beat, to study predictive neural activity (mismatch responses) versus sensory evoked responses. The paradigm investigates how the brain generates predictions based on temporal regularities and detects violations of expected rhythmic patterns. Only BioSemi STATUS admin markers are detectable in the locator metadata; no decoded trial events are available from the locator pipeline.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002218

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STATUS` | 18 (files) | admin | raw | BioSemi system status marker - exclude from epoch |

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

### Primary Task 1: Auditory/Visual Rhythm Omission Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.67 s, tmax = 1.67 s, target_events = [`visual_non_omission`, `visual_omission`, `auditory_non_omission`, `auditory_omission`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `visual_non_omission` | 0 | Visual flash stimulus (non-omitted) |
  | `visual_omission` | 1 | Expected visual flash that was omitted |
  | `auditory_non_omission` | 2 | Auditory tone stimulus (non-omitted) |
  | `auditory_omission` | 3 | Expected auditory tone that was omitted |
- **Evidence**:
  - DOI: 10.1111/ejn.15314 — This paper analyzes EEG data from OpenNeuro dataset ds002218 to examine modality-specific beta band activity during auditory and visual rhythm entrainment using an omission paradigm with epochs from -1.67s to +1.67s relative to tone/flash onset.
  - DOI: 10.1101/2020.11.29.402701 — This paper analyzes EEG data from the same openneuro_ds002218 dataset (18 subjects, 32-channel, 256Hz) using an omission paradigm with auditory and visual rhythms, epoching from -1.67s to +1.67s around each tone/flash/omission event to investigate induced and evoked beta band activity.
- **Kernel Notes**: Verify that events.tsv contains decoded trial events for auditory/visual non-omission and omission conditions. The original experiment used 100-event stimulus trains with 7 randomly placed omissions per train. Labels are derived from experimental design structure, not raw STATUS markers.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null(only STATUS admin events; no trial markers decoded))
- **Notes**: STATUS is a BioSemi CM_in_range hardware marker. If events.tsv contains decoded rhythm onset/omission events (separate from the locator metadata), they could be used for ERP analysis - verify directly from raw events.tsv.

## Data Quality Notes

- Only `STATUS` events found in locator metadata - BioSemi admin markers only.
- The actual auditory/visual rhythm and omission events may be encoded in the `events.tsv` files but were not decoded by the locator pipeline; check events.tsv directly.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: Comstock DC, Ross JM, Balasubramaniam R. Modality-specific frequency band activity during neural entrainment to auditory and visual rhythms. *European Journal of Neuroscience*. DOI: https://doi.org/10.1111/ejn.15314
