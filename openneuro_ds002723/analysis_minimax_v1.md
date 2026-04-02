# A dataset recorded during development of an affective brain-computer music interface: testing session

**Dataset**: `openneuro_ds002723` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002723
**Category**: Complex Applied | **Subjects**: 8 | **Files (Completed)**: 44 | **Channels**: 37.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants interacted with a real-time affective brain-computer music interface (BCMI) that modified music on-the-fly based on detected emotional states, aiming to induce specific target affective trajectories. This is the testing session of the BCI system (see also ds002722 calibration and ds002724 training sessions). Codes 1-9 encode the target or detected affective music conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002723

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2` | 44 (files) | long | raw | Affective music condition 2 |
| `6` | 44 (files) | long | raw | Affective music condition 6 |
| `9` | 42 (files) | long | raw | Affective music condition 9 |
| `4` | 42 (files) | long | raw | Affective music condition 4 |
| `5` | 39 (files) | long | raw | Affective music condition 5 |
| `7` | 38 (files) | long | raw | Affective music condition 7 |
| `1` | 29 (files) | long | raw | Affective music condition 1 |
| `3` | 28 (files) | long | raw | Affective music condition 3 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Affective Music Condition Classification (Binary Target vs. Detected)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 0 | Affective music condition 2 (target or detected) |
  | `6` | 1 | Affective music condition 6 (target or detected) |
  | `9` | 2 | Affective music condition 9 (target or detected) |
  | `4` | 3 | Affective music condition 4 (target or detected) |
  | `5` | 4 | Affective music condition 5 (target or detected) |
  | `7` | 5 | Affective music condition 7 (target or detected) |
  | `1` | 6 | Affective music condition 1 (target or detected) |
  | `3` | 7 | Affective music condition 3 (target or detected) |
- **Evidence**:
  - DOI: 10.1038/s41597.020.0507-6 — This paper describes the BCMI testing dataset (openneuro_ds002723) containing EEG, ECG, and GSR recordings from 8 participants during real-time evaluation of an affective brain-computer music interface that plays 8 different synthetic music conditions to induce and modify affective states. Events are long (>=2s) markers for sustained music conditions lasting 40 seconds.
- **Kernel Notes**: Use onset markers (event codes 1-9 excluding 8) to epoch the full 40-second sustained music condition. Labels are taken directly from event markers (raw meta). Exclude event code 8 (not present in dataset).

### Primary Task 2: Affective Music Condition Classification (Onset-locked)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music condition onset), target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 0 | Music condition 2 |
  | `6` | 1 | Music condition 6 |
  | `9` | 2 | Music condition 9 |
  | `4` | 3 | Music condition 4 |
  | `5` | 4 | Music condition 5 |
  | `7` | 5 | Music condition 7 |
  | `1` | 6 | Music condition 1 |
  | `3` | 7 | Music condition 3 |
- **Evidence**:
  - DOI: 10.1038/s41597.020.0507-6 — The paper describes the BCMI testing dataset (ds002723) containing EEG recordings from 8 participants during evaluation of the Brain-Computer Music Interface system, where music conditions 1-9 were used as affective state markers (excluding condition 8).
- **Kernel Notes**: Epoch short windows centered on condition onset transitions (tmin=-0.2s captures baseline, tmax=1.0s captures early neural response). Small dataset (8 subjects, 44 files); consider cross-subject validation.

### Normal Task 1: Affective Music Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music condition onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 8 affective conditions; decode exact valence/arousal mapping from Daly et al. 2018. Small dataset (8 subjects, 44 files). Music conditions are sustained 40-second states; these onset markers epoch at transition points.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2` | 0 | Music condition 2 |
 | `6` | 1 | Music condition 6 |
 | `9` | 2 | Music condition 9 |
 | `4` | 3 | Music condition 4 |
 | `5` | 4 | Music condition 5 |
 | `7` | 5 | Music condition 7 |
 | `1` | 6 | Music condition 1 |
 | `3` | 7 | Music condition 3 |

## Data Quality Notes

- Small dataset: 8 subjects, 44 files.
- 37-channel array includes physiological channels; verify EEG-only channel selection.
- Decode code-to-condition mapping from Daly et al. 2018 (Scientific Data).
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Neural and physiological data from participants listening to affective music, Scientific Data, 2018`
