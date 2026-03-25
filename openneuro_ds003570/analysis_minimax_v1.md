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

### Primary Task 1: Brain-behavior regression (predicting musical training from connectivity)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 1.2 s, target_events = [`standard`, `exemplar_deviant`, `function_deviant`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `standard` epochs → connectivity compute → condition average | continuous | 85% of trials; no harmonic violation |
  | `exemplar_deviant` epochs → connectivity compute → condition average | continuous | 7.5% of trials; same functional class, different chord inversion |
  | `function_deviant` epochs → connectivity compute → condition average | continuous | 7.5% of trials; different functional class (harmonic violation) |
- **Super Meta Notes**: For each subject: (1) epoch by event around second chord onset for each condition, (2) compute connectivity/bandpower separately for standard, exemplar_deviant, and function_deviant epochs, (3) compute difference predictors: Psi(Ex)-Psi(Fu) and log.BP(Ex)-log.BP(Fu), (4) use these difference predictors to predict: imp.hours (weekly improvisation hours), cl.hours (weekly classical hours), dIES (difference in inverse efficiency score).
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2021.118458 — Uses OpenNeuro ds003570 EEG data from musicians performing an auditory oddball task to predict self-reported improvisation and classical training hours from brain connectivity differences between exemplar and function deviants.
- **Kernel Notes**: Requires external events.tsv or behavioral logs to identify chord onsets. Epochs extracted -400 to 1200ms relative to second chord onset. Compute connectivity (e.g., coherence, PLV) or bandpower for each condition, then derive exemplar-function difference as predictor for regression.

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
