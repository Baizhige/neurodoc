# Trance Channeling EEG Dataset

**Dataset**: openneuro_ds004040 | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds004040
**Category**: Neuroscience | **Subjects**: 13 | **Files (Completed)**: 26 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Thirteen experienced trance channelers performed alternating 5-minute blocks of trance channeling (a mediumistic altered state of consciousness) and matched resting state conditions across two separate recording sessions. The study investigates neural correlates of voluntarily induced altered states of consciousness compared to wakeful rest. Each session contains three trance blocks and three rest blocks with precise onset/offset markers available as event triggers.

## File Scan Result

> **Kernel SHA256**: `4c4ac885d1933f478f54add7603debc5eb65aafd3b4d0cb549e8a4e1c349dbc3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `rest1_end` | 26 | event | raw | Rest block 1 offset |
| `rest1_start` | 26 | event | raw | Rest block 1 onset |
| `rest2_end` | 26 | event | raw | Rest block 2 offset |
| `rest2_start` | 26 | event | raw | Rest block 2 onset |
| `rest3_end` | 26 | event | raw | Rest block 3 offset |
| `rest3_start` | 26 | event | raw | Rest block 3 onset |
| `trance1_end` | 26 | event | raw | Trance channeling block 1 offset |
| `trance1_start` | 26 | event | raw | Trance channeling block 1 onset |
| `trance2_end` | 26 | event | raw | Trance channeling block 2 offset |
| `trance2_start` | 26 | event | raw | Trance channeling block 2 onset |
| `trance3_end` | 26 | event | raw | Trance channeling block 3 offset |
| `trance3_start` | 26 | event | raw | Trance channeling block 3 onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Trance vs. Rest Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 300.0, overlap = null, target_events = [trance1_start, trance2_start, trance3_start, rest1_start, rest2_start, rest3_start]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| trance1_start | 1 | Trance channeling block 1 onset |
| trance2_start | 1 | Trance channeling block 2 onset |
| trance3_start | 1 | Trance channeling block 3 onset |
| rest1_start | 0 | Rest block 1 onset |
| rest2_start | 0 | Rest block 2 onset |
| rest3_start | 0 | Rest block 3 onset |

- **Evidence**: Beaver et al. (2021) - DOI: 10.12688/f1000research.17157.2; OpenNeuro ds004040 - DOI: https://doi.org/10.18112/openneuro.ds004040.v1.0.0
- **Kernel Notes**: Use onset events (trance*_start, rest*_start) as target_events. Block labels derive from event prefix. Within-subject design (13 subjects × 2 sessions = 26 files) provides paired comparison opportunity.

### Normal Task 1: Within-Block Temporal Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| trance1_start | 1 | Trance block 1 epoch segment |
| trance2_start | 1 | Trance block 2 epoch segment |
| trance3_start | 1 | Trance block 3 epoch segment |
| rest1_start | 0 | Rest block 1 epoch segment |
| rest2_start | 0 | Rest block 2 epoch segment |
| rest3_start | 0 | Rest block 3 epoch segment |

- **Evidence**: OpenNeuro ds004040 - DOI: https://doi.org/10.18112/openneuro.ds004040.v1.0.0
- **Kernel Notes**: Sliding 2s windows with 50% overlap generate sufficient samples for classification from limited subject pool. Each 5-minute block yields ~298 segments per epoched reference point. Labels propagate from block-level onset to all derived segments.