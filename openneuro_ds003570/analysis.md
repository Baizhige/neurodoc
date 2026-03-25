# EEG: Improvisation and Musical Structures (Auditory Oddball Chords)

**Dataset**: `openneuro_ds003570` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003570
**Category**: Sensory/Response | **Subjects**: 34 | **Files (Completed)**: 34
**Channels**: 64 | **Sampling Rate**: 2048 Hz

## Paradigm

Participants listened to sequences of three-chord musical progressions in an oddball paradigm designed to detect functional and exemplar deviants occurring within a stream of standard chord progressions. The study investigates neural responses (mismatch negativity, P600) to harmonic violations and musical structure deviants, probing the auditory system's predictive coding of musical sequences. Only STATUS system markers were detected in the EEG data; the chord-level event annotations may be stored externally.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003570

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STATUS` | 34 | admin | raw | System status marker (only detected event) |

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
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds003570 DOI: https://doi.org/10.18112/openneuro.ds003570.v1.0.0


### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `stim`
- **Target Definition**: N/A (null (no labels, for unsupervised analysis))
- **Notes**: Only STATUS admin markers detected; no chord-level event annotations in EEG triggers. High sampling rate (2048 Hz). If events.tsv contains chord onset information, epoching by event may be feasible with custom preprocessing.
## Data Quality Notes

- Very high sampling rate (2048 Hz); high memory requirements.
- No usable task events detected in EEG triggers beyond STATUS admin marker.
- Chord-level event timing may require reconstruction from audio or behavioral logs.

## References

- **Reference**: `EEG dataset on improvisation and musical structures. OpenNeuro ds003570.`
