# Runabout: A Mobile EEG Study of Auditory Oddball Processing in Laboratory and Real-World Conditions

**Dataset**: `openneuro_ds003620` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003620
**Category**: Complex Applied | **Subjects**: 44 | **Files (Completed)**: 271
**Channels**: 35 | **Sampling Rate**: 250 Hz

## Paradigm

Participants performed an auditory oddball task under three levels of environmental complexity and physical activity: sitting in a laboratory, walking on a sports field (oval), and navigating a university campus. The paradigm examined how cognitive and motor demands of real-world locomotion affect P300 oddball responses. Target tones required mental counting ("count" condition) or were simply listened to ("don't count" condition), with both counted and uncounted targets interleaved across environments.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003620

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `t_count_lab` | 134 | short | raw | Target tone, count condition, laboratory |
| `t_count_oval` | 134 | short | raw | Target tone, count condition, oval |
| `t_count_campus` | 134 | short | raw | Target tone, count condition, campus |
| `ntcount_lab` | 134 | short | raw | Non-target (standard) tone, count condition, laboratory |
| `ntcount_oval` | 134 | short | raw | Non-target tone, count condition, oval |
| `ntcount_campus` | 134 | short | raw | Non-target tone, count condition, campus |
| `t_Count_lab` | 80 | short | raw | Target tone, Count (capital) condition, laboratory |
| `t_Count_oval` | 80 | short | raw | Target tone, Count condition, oval |
| `t_Count_campus` | 80 | short | raw | Target tone, Count condition, campus |
| `ntCount_lab` | 80 | short | raw | Non-target tone, Count condition, laboratory |
| `ntCount_oval` | 80 | short | raw | Non-target tone, Count condition, oval |
| `ntCount_campus` | 80 | short | raw | Non-target tone, Count condition, campus |
| `t_Dontcount_lab` | 208 | short | raw | Target tone, don't-count condition, laboratory |
| `t_Dontcount_oval` | 214 | short | raw | Target tone, don't-count condition, oval |
| `t_Dontcount_campus` | 214 | short | raw | Target tone, don't-count condition, campus |
| `ntDontcount_lab` | 208 | short | raw | Non-target tone, don't-count condition, laboratory |
| `ntDontcount_oval` | 214 | short | raw | Non-target tone, don't-count condition, oval |
| `ntDontcount_campus` | 214 | short | raw | Non-target tone, don't-count condition, campus |
| `empty` | 226 | admin | raw | Empty/padding event marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus`, `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `t_count_*`, `t_Count_*`, `t_Dontcount_*` | 1 | Target tone (deviant) |
  | `ntcount_*`, `ntCount_*`, `ntDontcount_*` | 0 | Non-target tone (standard) |
- **Evidence**:
  - DOI: 10.1038/s41598.021.01772.8 — This study used data from OpenNeuro dataset ds003620 to analyze MMN and P3 event-related potentials elicited by deviant vs standard tones in an auditory oddball paradigm across lab, field, and campus environments, epoching from -200ms to 800ms relative to event onset.
- **Kernel Notes**: Epoch window targets the P300 component latency range (300-600ms post-stimulus). Include all environment variants (lab, oval, campus) to maximize样本. Motion artifacts more prevalent in oval/campus conditions; consider quality filtering.

### Normal Task 1: Target/non-target classification (binary, cross-environment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Event names encode environment (lab/oval/campus) and condition (count/Count/Dontcount). The `Stimulus/` prefixed variants in some files are duplicates. Pool by target (t_) vs non-target (nt_) for a tractable binary task. Mobile EEG; motion artifacts expected during walking conditions.

| Event | y | Meaning |
 |-------|---|------|
| `t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus` | 1 | Target tone (all target variants) |
| `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus` | 0 | Non-target tone (all standard variants) |

## Data Quality Notes

- Mobile EEG recording; significant motion artifacts during outdoor walking conditions (oval, campus).
- Lowercase vs uppercase variants (count/Count) may reflect different recording sessions or systems.
- `empty` event is an admin placeholder; exclude from epoching.
- `Stimulus/`-prefixed variants appear in a subset of files and are redundant with non-prefixed versions.

## References

- **Reference**: `Runabout: A mobile EEG study of auditory oddball processing in laboratory and real-world conditions. OpenNeuro ds003620.`
