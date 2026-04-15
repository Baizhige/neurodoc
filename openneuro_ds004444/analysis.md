# The BMI-HDEEG dataset 1

**Dataset**: `openneuro_ds004444` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004444
**Category**: Action/Output | **Subjects**: 465 | **Files (Completed)**: 465 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Brain-computer interfacing task based on sensorimotor rhythms (SMR) using high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the first of four BMI-HDEEG datasets, enabling classification of motor imagery across all four classes.

## File Scan Result

> **Kernel SHA256**: `28d939307e70ca3bf3d0c71a9c74138292e505ab4c123b042340e6d4a60d5494`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), baseline = (-0.5, 0.0) s, target_events = ["1", "2", "3", "4"]
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: raw
- **Kernel Notes**: Alignment assumption: event markers indicate cue onset (not offset). Extended epoch window (tmin=-0.5s to tmax=4.0s) captures pre-cue baseline for correction and full motor imagery period. Numerical event codes 1-4 decoded to semantic MI labels at kernel level. **Complication**: Scan shows event_3 (feet MI) with 0 events across dataset; kernel must handle missing class gracefully or filter to 3-class subset.

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Left hand motor imagery |
| `2` | 1 | Right hand motor imagery |
| `3` | 2 | Feet motor imagery |
| `4` | 3 | Tongue motor imagery |

- **Evidence**: DOI 10.1038/s41597-023-02260-6 (data descriptor for BMI-HDEEG Dataset 1; confirms 4-class MI paradigm with events 1-4 mapped to left hand, right hand, feet, tongue respectively; validates tmin=-0.5s, tmax=4.0s epoch parameters; 128-channel high-density EEG at 1000 Hz)

### Potential Task 1: Binary Hand Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), baseline = (-0.5, 0.0) s, target_events = ["1", "2"]
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: raw
- **Kernel Notes**: Binary left vs right hand MI subset. Both classes confirmed present in scan (event_1: 18598, event_2: 9300). Excludes feet and tongue MI for cleaner spatial pattern analysis at motor cortex.

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Left hand motor imagery |
| `2` | 1 | Right hand motor imagery |

### Potential Task 2: Three-Class Motor Imagery Classification (No Feet)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), baseline = (-0.5, 0.0) s, target_events = ["1", "2", "4"]
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: raw
- **Kernel Notes**: Three-class MI using available events (left hand, right hand, tongue). Excludes feet MI due to missing event_3 data. Pragmatic alternative when full 4-class task fails due to data quality.

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Left hand motor imagery |
| `2` | 1 | Right hand motor imagery |
| `4` | 2 | Tongue motor imagery |