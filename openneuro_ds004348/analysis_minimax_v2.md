# Ear-EEG Sleep Monitoring 2017 (EESM17)

**Dataset**: `openneuro_ds004348` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004348
**Category**: Biological State | **Subjects**: 9 | **Files (Completed)**: 36
**Channels**: 35 | **Sampling Rate**: 200 Hz

## Paradigm

Nightly sleep monitoring and pre-sleep resting recordings using ear-EEG and partial polysomnography in a naturalistic home environment. Subjects wore ear-mounted EEG devices during sleep, allowing investigation of sleep stage classification and comparison between ear-EEG and conventional PSG signals.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004348

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Lights Off` | 9 | long | raw | Lights-off marker (sleep onset reference) |
| `Lights On` | 9 | long | raw | Lights-on marker (sleep end reference) |
| `Awake` | 1 | long | raw | Wakefulness annotation |
| `Artifact` | 9 | admin | raw | Artifact annotation |
| `Arousal` | 9 | admin | raw | Arousal annotation |
| `Beginning of Recording` | 9 | admin | raw | Recording start marker |
| `End of Study` | 9 | admin | raw | Recording end marker |
| `Montage` | 9 | admin | raw | Montage configuration event |
| `Started Analyzer - Sleep Events` | 9 | admin | raw | Analyzer start marker |
| `Started Analyzer - ECG` | 9 | admin | raw | ECG analyzer start |
| `Stopped Analyzer - ECG` | 9 | admin | raw | ECG analyzer stop |
| `Started Analyzer - Auto-Staging` | 9 | admin | raw | Auto-staging start |
| `Stopped Analyzer - Auto-Staging` | 9 | admin | raw | Auto-staging stop |
| `512` | 9 | admin | raw | Numerical trigger code 512 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Awake`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | W | 0 | Wake stage |
  | NREM1 | 1 | Non-REM Stage 1 |
  | NREM2 | 2 | Non-REM Stage 2 |
  | NREM3 | 3 | Non-REM Stage 3 (slow wave) |
  | REM | 4 | Rapid Eye Movement |
- **Super Meta Notes**: Derived from manual PSG scoring by trained clinical experts following AASM guidelines. The dataset contains annotation files with AASM sleep stage labels. Kernel step: Read sleep stage annotations from the PSG annotation files (e.g., Hypnogram or XML), extract 30-s epochs aligned to AASM standard scoring windows, and map to W/NREM1/NREM2/NREM3/REM labels.
- **Evidence**:
  - DOI: 10.1186/s12938-017-0400-5 — Uses a dataset of nine healthy subjects recorded simultaneously with PSG and ear-EEG for one night each, training a random forest classifier to automatically score sleep stages (W/REM/NREM1/NREM2/NREM3) from ear-EEG data and comparing to manual expert scoring. Confirms 30-s non-overlapping epochs per AASM guidelines.
- **Kernel Notes**: Use `epoch_by_long_event_hdf5` with 30-s epochs to align with AASM scoring. Extract sleep stage labels from annotation files (not raw event markers). The `Awake` annotation can serve as a boundary marker for wake periods. Filter out `Artifact` and `Arousal` annotations from training data. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Pre-sleep resting state analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Target Definition**: Resting-state EEG segments from pre-sleep period (between "Beginning of Recording" and "Lights Off").
- **Notes**: The dataset includes pre-sleep resting recordings that can be used for baseline EEG characterization.


## Data Quality Notes

- Sleep stage annotations are in PSG annotation files, not directly as trial events
- Artifact markers must be excluded from analysis windows
- 35 channels includes non-EEG channels (ECG, respiratory belt, etc.)
- Only 9 subjects; limited generalization

## References

- **Reference**: `Ear-EEG Sleep Monitoring 2017 (EESM17)`
