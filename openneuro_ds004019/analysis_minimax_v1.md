# Effect of obesity on arithmetic processing in preteens with high and low math skills. An event-related potentials study

**Dataset**: `openneuro_ds004019` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004019
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 62
**Channels**: 132 | **Sampling Rate**: 500 Hz

## Paradigm

Obese and non-obese preteens (ages 9-10) performed a delayed-verification arithmetic task to evaluate the effects of weight status and math skill level on arithmetic processing. Participants viewed an arithmetic problem (prob), then a delay (bgin), then a verification digit (face) and responded (resp). Trigger codes 0 and 1 encode response correctness (0=incorrect, 1=correct). The study uses ERPs to investigate neural correlates of arithmetic cognition in the context of childhood obesity.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004019

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | ~14,880 | short | raw | Trial beginning / delay period onset |
| `prob` | ~14,880 | short | raw | Arithmetic problem onset |
| `ch++` | ~14,880 | short | raw | Choice/comparison stimulus onset |
| `face` | ~14,880 | short | raw | Verification digit (face stimulus) onset |
| `resp` | ~14,600 | short | raw | Participant button-press response |
| `1` | ~14,364 | short | raw | Correct response (1=correct) |
| `0` | ~6,156 | short | raw | Incorrect response (0=incorrect) |
| `sync` | ~310 | admin | raw | Hardware sync pulse |
| `CELL` | ~248 | admin | raw | Cell/block marker |
| `SESS` | 62 | admin | raw | Session start marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Arithmetic Verification Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1`, `0`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-||
  | `0` | 0 | Incorrect arithmetic response |
  | `1` | 1 | Correct arithmetic response |
- **Evidence**:
  - DOI: 10.3389/fnhum.2022.760234_pdf — This paper analyzes ERP components (P150, P300, N400) time-locked to answer choice presentation to compare obese vs non-obese preteens with high/low math skills on arithmetic verification tasks, using correct vs incorrect response events (1 and 0) for epoching.
- **Kernel Notes**: Epoch relative to `face` or `ch++` (answer choice onset) events. Exclude admin markers (sync, CELL, SESS). Address class imbalance (~70% correct) via weighted loss or sampling.

### Normal Task 1: Correct vs Incorrect Arithmetic (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: sync, CELL, SESS are admin markers and must be excluded. The `1` and `0` events mark response correctness concurrent with `resp`. Class imbalance (~70% correct across subjects) should be addressed. Obesity group label is in participants.tsv.

| Event | y | Meaning |
 |-------|---|------|
 | `1` | 1 | Correct arithmetic response |
 | `0` | 0 | Incorrect arithmetic response |

## Data Quality Notes

- 132-channel EGI cap (E1-E128 + ECG/Respiration/SP channels); remove non-EEG channels before analysis
- sync/CELL/SESS are admin markers to exclude
- Class imbalance: ~70% correct trials - apply undersampling or weighted loss

## References

- **Reference**: `Effect of obesity on arithmetic processing in preteens with high and low math skills. An event-related potentials study.`
