# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2020-2022/2023/2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 4/13 | **Sampling Rate**: 250 Hz | **Manual Review**: Yikai Dong

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. Subjects manually sent trigger events to mark boundaries between video sequences and sleep sequences during the recording sessions.

## File Scan Result

> **Kernel SHA256**: `bc63a68f9ba26c0981ba24bc421dde0b1f1f07f31c18c348a3eacd3f53b7c533`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Artefact` | 1032 | admin | raw | Manual scoring artefact / unusable signal epoch |
| `Sleep stage N1` | 2662 | event | raw | N1 sleep epoch |
| `Sleep stage N2` | 15122 | event | raw | N2 sleep epoch |
| `Sleep stage N3` | 5161 | event | raw | N3 sleep epoch |
| `Sleep stage R` | 6259 | event | raw | REM sleep epoch |
| `Sleep stage W` | 2879 | event | raw | Wake epoch |
| `error -10` | 12535 | admin | raw |  |
| `error -100` | 118 | admin | raw |  |
| `event_2` | 72 | admin | raw |  |
| `oLED` | 6 | admin | raw |  |
| `trigger` | 243 | admin | raw |  |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `amplifier` | missing | N/A |
| `cap` | missing | N/A |
| `handedness` | missing | N/A |
| `sex` | missing | N/A |


## Tasks

### Classical Task 1: Five-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | wake epoch |
  | `Sleep stage N1` | 1 | N1 sleep epoch |
  | `Sleep stage N2` | 2 | N2 sleep epoch |
  | `Sleep stage N3` | 3 | N3 sleep epoch |
  | `Sleep stage R` | 4 | REM sleep epoch |
- **Evidence**:
  - OpenNeuro ds005178 `task-sleep_acq-scoring_events.json` defines manual sleep scoring levels Wake, REM, N1, N2, N3, and Artefact.
  - OpenNeuro ds005178 README describes at-home sleep recordings from 10 healthy participants with PSG plus ear-EEG for the first two recordings.
  - 10.1038/s41597-025-04579-8 describes EESM23 as an OpenNeuro ear-EEG sleep monitoring dataset with manual scoring stored as event files.
- **Notes**: Use only manually scored sleep-stage annotations. Exclude `Artefact`, trigger markers, and ear-EEG recording-failure markers from the target classes. Manual scoring files are available for the PSG sleep recordings, not for every ear-EEG-only session.

## Data Quality Notes

- Manual sleep scoring is available through `acq-scoring_events.tsv` files for the PSG sleep recordings; later ear-EEG-only sessions do not all have manual sleep-stage labels.
- `Artefact` is a manual scoring label for unusable signal epochs and should be excluded from the five-class sleep-stage target.
- `trigger` and `event_2` are boundary/marker events, not sleep-stage labels; `event_2` lacks sufficient public semantic documentation for task use.
- `error -10`, `error -100`, and `oLED` are ear-EEG recording-failure markers documented in `task-sleep_acq-earEEGRecordingFailures_events.json`.
- The public BIDS files do not include `participants.tsv`; subject age, sex, and handedness are unavailable.
- Channel configuration varies by acquisition: ear-EEG files have 4 EEG channels plus trigger, while PSG files have 13 physiological channels plus trigger.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
