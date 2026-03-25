# Large Spanish EEG

**Dataset**: `openneuro_ds004279` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004279
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 60
**Channels**: 69 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed speech perception and silent speech production tasks involving 30 daily Spanish sentences. Each sentence trial followed a fixed structure: a rest period, a preparation cue, a perception phase (hearing the sentence), and a production phase (silently producing the sentence). The study investigated EEG correlates of perceived and silently produced speech.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004279

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `perception_N` (N=1-30) | 60x7 | long | raw | Perception phase onset for sentence N |
| `production_N` (N=1-30) | 60x7 | long | raw | Silent production phase onset for sentence N |
| `preparation_N` (N=1-30) | 60x7 | long | raw | Preparation cue onset for sentence N |
| `rest_N` (N=1-30) | 60x7 | rest | raw | Rest period onset for sentence N |
| `bad_artifact` | 60xvariable | admin | raw | Bad artifact annotation |
| `Impedance_test` | 60x2 | admin | raw | Impedance check marker |
| `bad_before_experiment` | 60x1 | admin | raw | Pre-experiment bad segment |
| `bad_after_experiment` | 60x1 | admin | raw | Post-experiment bad segment |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: 30-Class Sentence Identity Classification from Perceived Speech
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`perception_1`, `perception_2`, `perception_3`, `perception_4`, `perception_5`, `perception_6`, `perception_7`, `perception_8`, `perception_9`, `perception_10`, `perception_11`, `perception_12`, `perception_13`, `perception_14`, `perception_15`, `perception_16`, `perception_17`, `perception_18`, `perception_19`, `perception_20`, `perception_21`, `perception_22`, `perception_23`, `perception_24`, `perception_25`, `perception_26`, `perception_27`, `perception_28`, `perception_29`, `perception_30`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `perception_1` | 0 | Sentence 1 perception phase |
  | `perception_2` | 1 | Sentence 2 perception phase |
  | ... | ... | ... |
  | `perception_30` | 29 | Sentence 30 perception phase |
- **Kernel Notes**: Downsample data to 250 Hz before epoching. Trim trials to exactly 3 s (750 data points) as reported in paper. Verify event ID mapping from events.tsv — the paper uses perception phase events only for 30-class sentence identity decoding.
- **Evidence**:
  - DOI: 10.1088/1741-2552.ad88a3 — This study collected EEG from 56 participants performing speech perception with 30 Spanish sentences and trained deep neural networks (EEGNet, DeepConvNet, ShallowConvNet) to classify sentence identity into 30 classes using a 3-second window (tmin=0s, tmax=3s) relative to perception onset.

### Normal Task 1: Perception vs Production Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Group all perception_N events as class 0 and all production_N events as class 1. Each sentence has 7 repetitions per subject. bad_artifact, Impedance_test, and bad_* events are admin markers excluded from epoching.

| Event | y | Meaning |
|-------|---|---------|
| `perception_1`...`perception_30` | 0 | Speech perception phase |
| `production_1`...`production_30` | 1 | Silent speech production phase |


## Data Quality Notes

- 90+ distinct event types (perception/production/preparation/rest for 30 sentences)
- bad_artifact count varies by subject (31-39 per file)
- Group sentence-level events by phase type for practical classification

## References

- **Reference**: `Valle, C., Mendez-Orellana, C., Herff, C., & Rodriguez-Fernandez, M. (2024). Identification of perceived sentences using deep neural networks in EEG. Journal of neural engineering, 21(5), 056044.`
