# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 516 | **Channels**: 25 | **Sampling Rate**: 500 Hz

## Paradigm

Naturalistic multi-night sleep monitoring using ear-EEG and polysomnography (PSG) in a home environment collected in 2019. Participants self-applied in-ear EEG electrodes over multiple nights for sleep staging and feasibility assessment. Event markers are Danish-language protocol annotations (lights out, going to bed, waking up), synchronization pulses, and calibration periods. The dominant event is `trigger` (30,726 total) - a PSG synchronization pulse. Sleep stage labels are derived from PSG annotations rather than EEG event markers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005185

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger` | 30726 | admin | raw | Synchronization trigger between ear-EEG and PSG (exclude) |
| `Lights Out` | 94 | rest | raw | Lights out - sleep onset marker |
| `Gik i seng` | 80 | rest | raw | "Went to bed" (Danish) |
| `Biocalibrations` | 79 | admin | raw | Biocalibration period (exclude) |
| `Sync` | 77 | admin | raw | Synchronization marker (exclude) |
| `Start af maling` | 75 | admin | raw | "Start of recording" (Danish, exclude) |
| `Stod op` | 70 | rest | raw | "Got up" (Danish) - wake marker |
| `Biocalibrations start` | 11 | admin | raw | Biocalibration start (exclude) |
| `Vagen` / `vagen` | 13 | rest | raw | "Awake" (Danish) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `trigger`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification (W/N1/N2/N3/REM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage REM`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Sleep stage W | 0 | Wake (AASM standard) |
  | Sleep stage N1 | 1 | N1 sleep stage |
  | Sleep stage N2 | 2 | N2 sleep stage |
  | Sleep stage N3 | 3 | N3 sleep stage |
  | Sleep stage REM | 4 | REM sleep stage |
- **Super Meta Notes**: Derived from manual PSG sleep scoring by trained technicians following AASM v2.5 guidelines. Each PSG recording was scored twice by different technicians. Epochs marked as 'unscored' by manual scorers (approximately 5%) were excluded. The scorer had no access to ear-EEG data during scoring. Kernel step: Load PSG-derived sleep stage annotations from dataset sidecar files and merge with corresponding EEG epochs; filter out unscored epochs.
- **Evidence**:
  - DOI: 10.1038/s41598-019-53115-3 — Automatic sleep staging using ear-EEG with 5-class classification (W/N1/N2/N3/REM) using 30-second epochs, random forest classifier, Cohen's kappa of 0.73
  - DOI: 10.1038/s41597-025-04579-8 — Data descriptor for EESM19 dataset confirming AASM-standard PSG scoring used as ground truth for sleep stage labels
- **Kernel Notes**: Sleep stage labels are NOT present in raw EEG event markers — they must be extracted from PSG annotation sidecar files. Use `epoch_by_long_event_hdf5` with 30-second windows matching the AASM standard epoch length. Verify epoch boundaries align with PSG scoring timestamps.

### Normal Task 1: Sleep Monitoring Segmentation (segmentation)
- **Task Type**: classification
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `stim`
- **Target Definition**: None
- **Notes**: All event markers are Danish-language protocol annotations or sync triggers - not suitable as EEG classification targets. Sleep stage labels (N1/N2/N3/REM/Wake) should be obtained from PSG annotation files. `trigger` (30,726) is a high-frequency sync pulse - exclude.


## Data Quality Notes

- `trigger` (30,726) is a sync pulse - exclude from classification.
- All event markers are protocol annotations, not neural response labels.
- 25-channel ear-EEG with limited spatial resolution.
- PSG reference annotations required for sleep staging labels.

## References

- **Reference**: `Ear-EEG Sleep Monitoring 2019 (EESM19)`
