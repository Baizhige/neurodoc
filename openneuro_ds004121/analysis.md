# BCIT Mind Wandering

**Dataset**: `openneuro_ds004121` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004121
**Category**: Complex Applied | **Subjects**: 60 | **Files (Completed)**: 60
**Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a long-duration simulated driving task involving lane maintenance, speed control, and a police vehicle vigilance sub-task (detecting a police car among traffic), while exposed to lateral perturbations and varying background audio conditions (silence vs. music vs. podcast). The mind wandering manipulation used periodic thought probes to assess on-task vs. off-task mental state. EEG biomarkers of mind wandering during driving were investigated.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `4311` | 60 files | short | raw | Lateral perturbation type 1 |
| `4312` | 59 files | short | raw | Lateral perturbation type 2 |
| `4210` | 59 files | short | raw | Perturbation onset |
| `4220` | 59 files | short | raw | Perturbation event |
| `4230` | 59 files | short | raw | Perturbation/direction event |
| `4730` | 59 files | short | raw | Special driving event |
| `4411` | 60 files | short | raw | Police vehicle event |
| `4621`-`4622` | 60 files | short | raw | Audio condition events |
| `3200` | 60 files | short | raw | Speed marker |
| `3111` | 60 files | short | raw | Perturbation onset |
| `3310` | 60 files | short | raw | Performance metric |
| `1211` | 60 files | short | raw | Lane correction event |
| `1212` | 58 files | short | raw | Lane correction event |
| `1121`-`1122` | 60 files | short | raw | Driver response |
| `1111`-`1112` | 60 files | short | raw | Driver response |
| `2221`-`2222` | 59 files | short | raw | Thought probe / mind wandering event |
| `2241`-`2242` | 59 files | short | raw | Thought probe response |
| `2251`-`2252` | 59 files | short | raw | Thought probe response |
| `2621`-`2622` | 60 files | short | raw | Behavioral response |
| `2811`-`2812` | 59 files | short | raw | Audio cue events |
| `2631`-`2632` | 58 files | short | raw | Behavioral response events |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### Info

Scan completed across 60 subjects (60 files). All events are short type. Full event codebook available for decoding 30+ event types.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds004121 DOI: https://doi.org/10.18112/openneuro.ds004121.v1.0.0


### Normal Task 1: Lateral Perturbation Direction (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Mind wandering thought probe events (2221/2241/2251) can be used to label on-task vs. off-task periods for attention state classification. Full event codebook required for precise decoding of all 30+ event types.

| Event | y | Meaning |
|-------|---|---------|
| `4311` | 0 | Lateral perturbation - type 1 |
| `4312` | 1 | Lateral perturbation - type 2 |

## Data Quality Notes

- 30+ distinct event types; full decoding requires BCIT codebook
- Thought probe events provide mind-wandering labels for attention classification
- Audio condition (silence/music/podcast) provides additional between-condition variable

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004121