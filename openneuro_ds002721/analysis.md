# An EEG dataset recorded during affective music listening

**Dataset**: `openneuro_ds002721` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds002721
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 185 | **Channels**: 19.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants listened to 40 music clips from film scores while their EEG was recorded, to investigate the neural correlates of music-induced emotional states. Each 40-second music clip is marked at onset with a numeric trigger code (800-908 range encode specific music tracks; 32768 and 257 are likely system markers). The study is part of a series with ds002722 (calibration) and ds002723/ds002724 (BCI sessions). Emotion ratings may be available in behavioral logs.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002721

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `32768` | 124 (files) | admin | raw | System/hardware trigger - likely session marker |
| `1092` | 124 (files) | admin | raw | System code - likely hardware sync |
| `800`-`808` range | 124 (files each) | long | raw | Music clip onset - specific track identifiers |
| `833`-`840` range | 111-123 (files) | long | raw | Music clip onset - specific track identifiers |
| `902`-`908` range | 118-123 (files) | long | raw | Music clip onset - specific track identifiers |
| `786`, `788` | 124 (files) | long | raw | Music clip onset - specific track identifiers |
| `257` | 120 (files) | admin | raw | System code - likely hardware marker |
| `33575`, `33571` | 112-119 (files) | admin | raw | Large codes - likely system/admin markers |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Run
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002721 DOI: https://doi.org/10.1016/j.neulet.2014.05.003


### Normal Task 1: Music Clip Onset Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Codes 32768, 1092, 257, 33575, 33571 are system/admin markers - excluded. Each music clip is ~40 seconds; these onset markers are short events marking start of a sustained music stimulus. Valence/arousal ratings from behavioral logs could serve as regression targets.

 | Event | y | Meaning |
 |-------|---|---------|
 | `800` | 0 | Music clip onset (track 800) |
 | `801` | 1 | Music clip onset (track 801) |
 | `802` | 2 | Music clip onset (track 802) |
 | `803` | 3 | Music clip onset (track 803) |
 | `804` | 4 | Music clip onset (track 804) |
 | `805` | 5 | Music clip onset (track 805) |
 | `806` | 6 | Music clip onset (track 806) |
 | `807` | 7 | Music clip onset (track 807) |
 | `808` | 8 | Music clip onset (track 808) |
 | `786` | 9 | Music clip onset (track 786) |
 | `788` | 10 | Music clip onset (track 788) |
 | `833` | 11 | Music clip onset (track 833) |
 | `834` | 12 | Music clip onset (track 834) |
 | `835` | 13 | Music clip onset (track 835) |
 | `836` | 14 | Music clip onset (track 836) |
 | `837` | 15 | Music clip onset (track 837) |
 | `838` | 16 | Music clip onset (track 838) |
 | `839` | 17 | Music clip onset (track 839) |
 | `840` | 18 | Music clip onset (track 840) |
 | `902` | 19 | Music clip onset (track 902) |
 | `903` | 20 | Music clip onset (track 903) |
 | `904` | 21 | Music clip onset (track 904) |
 | `905` | 22 | Music clip onset (track 905) |
 | `906` | 23 | Music clip onset (track 906) |
 | `907` | 24 | Music clip onset (track 907) |
 | `908` | 25 | Music clip onset (track 908) |
## Data Quality Notes

- 30 distinct event types; codes 32768, 33575, 33571 are likely hardware sync markers.
- 19-channel EEG; low spatial resolution.
- Verify event code mapping from dataset README or paper (Scientific Data 2018).
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Neural and physiological data from participants listening to affective music (Scientific Data, 2018)`
