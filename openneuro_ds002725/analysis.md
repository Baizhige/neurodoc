# A dataset recording joint EEG-fMRI during affective music listening

**Dataset**: `openneuro_ds002725` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002725
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 105 | **Channels**: 47.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants listened to music stimuli designed to elicit emotional responses (approach/withdrawal behavior) and self-reported their felt affective states during simultaneous EEG-fMRI recording. The study investigated how EEG reflects subcortical brain activity related to emotional responses to music. Codes 1283/1285 are likely BrainVision fMRI sync codes; 34053 may be a BrainVision hardware code; 47/10/1 may be music condition/block markers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002725

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `47` | 105 (files) | long | raw | Music block marker (likely condition or trial count) |
| `10` | 105 (files) | long | raw | Music onset marker (condition 10x) |
| `1` | 105 (files) | long | raw | Music onset marker (condition 1x) |
| `1283` | 105 (files) | admin | raw | BrainVision fMRI sync code - likely admin |
| `1285` | 105 (files) | admin | raw | BrainVision fMRI sync code - likely admin |
| `34053` | 105 (files) | admin | raw | Large BrainVision hardware code - admin |
| `265` | 94 (files) | long | raw | Music condition marker |
| `768` | 84 (files) | long | raw | Music condition marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Generated Music
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002725 DOI: https://doi.org/10.1038/s41598-019-45105-2


### Primary Task 2: Publisher-defined BIDS task: Classical Music
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002725 DOI: https://doi.org/10.1038/s41598-019-45105-2


### Primary Task 3: Publisher-defined BIDS task: Gen Music01
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002725 DOI: https://doi.org/10.1038/s41598-019-45105-2


### Normal Task 1: Affective Music State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Codes 1283, 1285, 34053 are BrainVision system/fMRI sync markers - excluded. Decode exact music condition meaning from paper (subcortical approach/withdrawal). 47-channel EEG includes MRI-compatible electrodes. fMRI gradient artifact correction required.

 | Event | y | Meaning |
 |-------|---|---------|
 | `47` | 0 | Music block/condition marker 47 |
 | `10` | 1 | Music block/condition marker 10 |
 | `1` | 2 | Music block/condition marker 1 |
 | `265` | 3 | Music condition marker 265 |
 | `768` | 4 | Music condition marker 768 |
## Data Quality Notes

- EEG recorded in MRI scanner; MRI gradient artifacts require dedicated removal pipeline.
- Codes 1283, 1285, 34053 are BrainVision system/fMRI codes - exclude from analysis.
- 47-channel EEG; verify channel positions and identify MRI-compatible electrode set.
- Decode music condition codes from Daly et al. / Sharman et al. paper.

## References

- **Reference**: `Electroencephalography reflects the activity of sub-cortical brain regions during approach-withdrawal behaviour while listening to music`
