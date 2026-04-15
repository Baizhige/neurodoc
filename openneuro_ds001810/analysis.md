# EEG study of the attentional blink; before, during, and after transcranial Direct Current Stimulation (tDCS)

**Dataset**: `openneuro_ds001810` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001810
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 527 | **Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants performed an attentional blink (AB) task using a Rapid Serial Visual Presentation (RSVP) stream to identify two targets (T1 and T2) embedded in a stream of distractors. EEG was recorded before, during, and after receiving anodal or cathodal transcranial Direct Current Stimulation (tDCS) to study how cortical excitability modulates the attentional blink - the impaired detection of T2 when it follows T1 within ~500 ms. BioSemi STATUS channel encodes trial conditions as numeric codes.

## File Scan Result

> **Kernel SHA256**: `2703333aa1996b7cde606d0917ec1d35e20c9d3e923c432e6adb7fd71f5f9d6d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RSVP_stream_item` | 51145 | event | raw | RSVP stream visual stimulus item |
| `STATUS_-6` | 408405 | event | raw | BioSemi hardware status code (baseline/continuous) |
| `STATUS_126976` | 21 | event | raw | BioSemi hardware status marker |
| `STATUS_127230` | 226 | event | raw | BioSemi hardware status marker |
| `T1_T2_lag8` | 51144 | event | raw | T2 presented at lag-8 position (outside AB window) |
| `T1_onset` | 34082 | event | raw | T1 target onset marker |
| `T1_present_T2_present_lag3` | 51144 | event | raw | T2 presented at lag-3 position (within AB window) |
| `T1_target` | 51144 | event | raw | T1 target identification event |
| `T2_onset_variant1` | 23288 | event | raw | T2 onset at lag-3 (AB-susceptible) |
| `T2_onset_variant2` | 27597 | event | raw | T2 onset at lag-8 (control) |
| `T2_target` | 51115 | event | raw | T2 target identification event |
| `response_hit` | 40784 | event | raw | Correct T2 detection response |
| `response_miss` | 10216 | event | raw | Incorrect T2 detection (missed within AB window) |
| `stimulus_lag_variant` | 17062 | event | raw | Stimulus lag variant marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: T2 Detection Classification Across Attentional Blink Conditions

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [T2_onset_variant1, T2_onset_variant2]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-|-------|-------|
| T2_onset_variant1 | 0 | T2 at AB-susceptible lag (lag-3) |
| T2_onset_variant2 | 1 | T2 at control lag (lag-8) |

- **Evidence** (DOI): None available for this dataset; task supported by paradigm description and event structure alignment.
- **Kernel Notes**: T2_onset_variant1 (~23.3k) and T2_onset_variant2 (~27.6k) likely encode T2 at different lag positions. The ~51k STATUS/61450 events represent RSVP stream items. CM_in_range (61440) and CM_out_of_range (61694) are BioSemi hardware markers excluded from analysis.

### Potential Task 2: T2 Detection Accuracy Prediction

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [T2_onset_variant1, T2_onset_variant2]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-|-------|-------|
| response_hit | 0 | Correct T2 detection |
| response_miss | 1 | Incorrect T2 detection (missed within AB window) |

- **Evidence** (DOI): None available for this dataset; task plausible from paradigm (RSVP AB task with response recording).
- **Kernel Notes**: response_hit (~40.8k) and response_miss (~10.2k) encode behavioral outcomes. Epochs should be aligned to T2 onset, then labeled by subsequent response. The ~31k imbalance between total T2 trials and responses may reflect no-response catch trials.

### Potential Task 3: Response Time Regression

- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [T2_onset_variant1, T2_onset_variant2]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|-|-------|-------|
| response_time | continuous | RT from T2 onset to behavioral response |

- **Evidence** (DOI): None available for this dataset; continuous RT labels stored in misc route.
- **Kernel Notes**: response_time is a continuous variable stored via misc route. Preserve derivation metadata (unit: likely seconds/ms, version) for regression modeling. RT may vary as a function of tDCS phase (pre/during/post) and stimulation type (anodal/cathodal).

### Potential Task 4: T1 Processing Event-Related Potential

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [T1_onset]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-|-------|-------|
| T1_onset | 0 | T1 target onset |

- **Evidence** (DOI): None available; task plausible from paradigm (T1 is first target in RSVP stream).
- **Kernel Notes**: T1_onset (~34k) marks first target identification. Useful for examining T1 processing as baseline for AB effect. Combined with T2 onset epochs, enables lag-dependent comparison of ERP components (e.g., N2pc, P3).