# BCIT Traffic Complexity

**Dataset**: `openneuro_ds004123` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004123
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 30
**Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a simulated driving task with varying levels of visual traffic complexity (low, medium, high density of surrounding vehicles) while correcting for lateral vehicle perturbations. EEG was recorded to assess how increasing traffic complexity interacts with fatigue-related neural signatures. Part of the BCIT driving fatigue dataset series examining environmental complexity effects on driver workload.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `4311` | 30 files | short | raw | Lateral perturbation type 1 |
| `4312` | 30 files | short | raw | Lateral perturbation type 2 |
| `4210` | 30 files | short | raw | Perturbation onset |
| `4220` | 30 files | short | raw | Perturbation event |
| `4230` | 30 files | short | raw | Perturbation/direction event |
| `4411` | 30 files | short | raw | Special event |
| `3200` | 30 files | short | raw | Speed marker |
| `3111` | 30 files | short | raw | Perturbation onset |
| `3310` | 30 files | short | raw | Performance metric |
| `3210` | 30 files | short | raw | Traffic complexity marker - low |
| `3230` | 30 files | short | raw | Traffic complexity marker - medium |
| `3240` | 30 files | short | raw | Traffic complexity marker - high |
| `1211` | 30 files | short | raw | Lane correction event |
| `1212` | 30 files | short | raw | Lane correction event |
| `1121`-`1122` | 30 files | short | raw | Driver response events |
| `1111`-`1112` | 30 files | short | raw | Driver response events |
| `2221`-`2222` | 30 files | short | raw | Behavioral response events |
| `2241`-`2242` | 30 files | short | raw | Behavioral response events |
| `2251`-`2252` | 30 files | short | raw | Behavioral response events |
| `2621`-`2622` | 30 files | short | raw | Auditory/behavioral events |
| `2711`-`2712` | 30 files | short | raw | Traffic event markers |
| `2811`-`2812` | 30 files | short | raw | Traffic event markers |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### Info

Placeholder for additional file scan metadata.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds004123 DOI: https://doi.org/10.18112/openneuro.ds004123.v1.0.0


### Normal Task 1: Traffic Complexity Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Traffic complexity conditions (3210/3230/3240) are the primary manipulation variable. Only 30 subjects - small cohort. Full event code decoding requires BCIT codebook.

| Event | y | Meaning |
|-------|---|------|
| `3210` | 0 | Low traffic complexity |
| `3230` | 1 | Medium traffic complexity |
| `3240` | 2 | High traffic complexity |
## Data Quality Notes

- 30 subjects - smallest subject count in the BCIT driving series
- 30 distinct event types; full decoding requires BCIT codebook documentation
- Traffic complexity codes (3210/3230/3240) are the key classification targets

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004123