# Continuous Feedback Processing

**Dataset**: `openneuro_ds004262` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004262
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 31 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants predicted the final height of an animated rising bar based on cues with varying predictability to study continuous feedback processing and prediction error. Each trial involved observing bar motion and registering a prediction, allowing examination of EEG correlates of reward prediction error and uncertainty-driven learning. The experiment used 36 distinct stimulus subtypes encoding six levels of cue predictability (6 conditions × 6 repetitions per block).

## File Scan Result

> **Kernel SHA256**: `cad549713572c87ba802dbc4c8ada39917c843044eb47f32b4c645a61b17be7f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Active Shielding: On` | 21 | admin | raw | Active shielding status marker from scanner |
| `Stimulus/S  1` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  2` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  3` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  4` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  5` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  6` | 525 | event | raw | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 11` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 12` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 13` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 14` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 15` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 16` | 525 | event | raw | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 21` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 22` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 23` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 24` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 25` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 26` | 525 | event | raw | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 31` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 32` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 33` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 34` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 35` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 36` | 525 | event | raw | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 41` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 42` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 43` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 44` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 45` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 46` | 525 | event | raw | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 51` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 52` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 53` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 54` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 55` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 56` | 525 | event | raw | Highest predictability cue; reward magnitude from events.tsv |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Continuous Feedback Prediction Error Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 2.0 s (relative to Stimulus onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous behavioral variable derived from events.tsv columns (predicted height vs. actual height).
- **Notes**: Regression-based analysis of prediction error during continuous feedback. The 36 stimulus subtypes (S  1–S 56) encode cue predictability levels, while events.tsv metadata columns contain continuous variables (predicted height, actual height) for computing prediction error as the regression target. Reward magnitude and predictability serve as model regressors. This is the primary analysis from the original publication.

| Event | y | Meaning |
|-------|---|----------|
| `Stimulus/S  1` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  2` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  3` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  4` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  5` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S  6` | continuous | Low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 11` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 12` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 13` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 14` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 15` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 16` | continuous | Medium-low predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 21` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 22` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 23` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 24` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 25` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 26` | continuous | Medium predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 31` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 32` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 33` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 34` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 35` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 36` | continuous | Medium-high predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 41` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 42` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 43` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 44` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 45` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 46` | continuous | High predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 51` | continuous | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 52` | continuous | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 53` | continuous | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 54` | continuous | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 55` | continuous | Highest predictability cue; reward magnitude from events.tsv |
| `Stimulus/S 56` | continuous | Highest predictability cue; reward magnitude from events.tsv |

- **Evidence (DOI)**:
  - https://doi.org/10.1101/2022.10.06.511117 (Preprint: "The Neural Correlates of Continuous Feedback Processing")
  - https://doi.org/10.1111/psyp.14399 (Published: Psychophysiology 2023)
- **Kernel Notes**: No offset events mark animation endpoints; reward magnitude and prediction error must be derived from events.tsv behavioral columns. The 36 stimulus subtypes group into 6 predictability levels (first digit: 1=low, 6=highest) for model regressors alongside continuous reward value.

### Potential Task 1: Stimulus Predictability Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to Stimulus onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Predictability level inferred from stimulus subtype (first digit of event name).
- **Notes**: Six-class classification based on cue predictability (S  1-6 = low, S 11-16 = medium-low, S 21-26 = medium, S 31-36 = medium-high, S 41-46 = high, S 51-56 = highest). Supports analysis of how neural responses differ with uncertainty level during bar observation. Secondary analysis complementary to the primary regression task.

| Event | y | Meaning |
|-------|---|----------|
| `Stimulus/S  1` | 1 | Low predictability |
| `Stimulus/S  2` | 1 | Low predictability |
| `Stimulus/S  3` | 1 | Low predictability |
| `Stimulus/S  4` | 1 | Low predictability |
| `Stimulus/S  5` | 1 | Low predictability |
| `Stimulus/S  6` | 1 | Low predictability |
| `Stimulus/S 11` | 2 | Medium-low predictability |
| `Stimulus/S 12` | 2 | Medium-low predictability |
| `Stimulus/S 13` | 2 | Medium-low predictability |
| `Stimulus/S 14` | 2 | Medium-low predictability |
| `Stimulus/S 15` | 2 | Medium-low predictability |
| `Stimulus/S 16` | 2 | Medium-low predictability |
| `Stimulus/S 21` | 3 | Medium predictability |
| `Stimulus/S 22` | 3 | Medium predictability |
| `Stimulus/S 23` | 3 | Medium predictability |
| `Stimulus/S 24` | 3 | Medium predictability |
| `Stimulus/S 25` | 3 | Medium predictability |
| `Stimulus/S 26` | 3 | Medium predictability |
| `Stimulus/S 31` | 4 | Medium-high predictability |
| `Stimulus/S 32` | 4 | Medium-high predictability |
| `Stimulus/S 33` | 4 | Medium-high predictability |
| `Stimulus/S 34` | 4 | Medium-high predictability |
| `Stimulus/S 35` | 4 | Medium-high predictability |
| `Stimulus/S 36` | 4 | Medium-high predictability |
| `Stimulus/S 41` | 5 | High predictability |
| `Stimulus/S 42` | 5 | High predictability |
| `Stimulus/S 43` | 5 | High predictability |
| `Stimulus/S 44` | 5 | High predictability |
| `Stimulus/S 45` | 5 | High predictability |
| `Stimulus/S 46` | 5 | High predictability |
| `Stimulus/S 51` | 6 | Highest predictability |
| `Stimulus/S 52` | 6 | Highest predictability |
| `Stimulus/S 53` | 6 | Highest predictability |
| `Stimulus/S 54` | 6 | Highest predictability |
| `Stimulus/S 55` | 6 | Highest predictability |
| `Stimulus/S 56` | 6 | Highest predictability |

- **Evidence (DOI)**: None (inferred from paradigm: varying predictability cues support differential processing classification)
- **Kernel Notes**: Predictability mapping based on first digit of 36 stimulus subtypes (6 conditions × 6 repetitions per block). Requires parsing event name to extract condition code. Without explicit condition labels in event names, classification relies on inferred structure from paradigm description.