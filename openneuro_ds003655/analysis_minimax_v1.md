# VerbalWorkingMemory

**Dataset**: `openneuro_ds003655` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003655
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 156
**Channels**: 21 | **Sampling Rate**: 500 Hz

## Paradigm

A modified Sternberg working memory task requiring either simple retention or mental manipulation (alphabetization) of letter sequences at three load levels (5, 6, or 7 letters). Participants encoded a letter sequence, maintained it across a delay period, then responded to a probe letter. The mental manipulation condition (alphabetization) places additional executive demands on working memory compared to simple retention. EEG measures during encoding, delay, and probe phases capture load-dependent neural activity.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003655

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `encoding` | 936 | short | raw | Letter sequence encoding phase onset |
| `delay period` | 936 | long | raw | Working memory retention/manipulation delay period |
| `probe` | 936 | short | raw | Probe letter presentation |
| `start of the baseline period` | 936 | short | raw | Baseline period onset (pre-trial) |
| `start of the trial` | 156 | short | raw | Trial start marker |
| `presentation of the task instruction` | 156 | short | raw | Task instruction display onset |
| `Response` | 1807 | short | raw | Participant button-press response |
| `STATUS` | 156 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Retention vs Manipulation Classification from Probe ERP
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -14.2 s, tmax = 2.2 s, target_events = [`probe`] *
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `probe: 5R` / `6R` / `7R` | 0 | Retention condition (keep letters in order) |
  | `probe: 5M` / `6M` / `7M` | 1 | Manipulation condition (alphabetize letters) |
- **Evidence**:
  - DOI: `10.1111/ejn.15457` — Exploratory reanalysis examining oscillatory brain activity differences between retention and manipulation conditions during encoding and delay phases; epochs extracted from -14200 to 2200 ms relative to probe onset with baseline -11500 to -10500 ms

### Primary Task 2: Encoding Phase Classification (Retention vs Manipulation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -14.2 s *, tmax = 2.2 s *, target_events = [`encoding`] *
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `encoding: 5R` / `6R` / `7R` | 0 | Retention condition encoding phase |
  | `encoding: 5M` / `6M` / `7M` | 1 | Manipulation condition encoding phase |
- **Evidence**:
  - DOI: `10.1111/ejn.15457` — Paper examines oscillatory activity differences during encoding phase between retention and manipulation conditions; target_events includes `encoding` and condition labels

### Primary Task 3: Delay Period Classification (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 6.0 s, overlap = 0.5, target_events = [`delay period`] *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `delay period: 5R` / `6R` / `7R` | 0 | Simple retention (Retention) condition |
  | `delay period: 5M` / `6M` / `7M` | 1 | Mental manipulation (Manipulation) condition |
- **Evidence**:
  - DOI: `10.1111/ejn.15457` — Paper examines oscillatory differences during delay period; delay period divided into Delay1 (-6000 to -3000 ms) and Delay2 (-3000 to 0 ms), indicating ~6 s total delay duration

### Normal Task 1: Delay period analysis - keep vs operation (binary, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Delay periods typically last several seconds (>=2 s). Event subtypes encode both load level (5/6/7) and condition (R=Retention, M=Manipulation). Load level can be used as a regression target or ordinal label.

| Event | y | Meaning |
 |-------|---|------|
| `delay period: 5R` / `6R` / `7R` | 0 | Simple retention (Retention) condition |
| `delay period: 5M` / `6M` / `7M` | 1 | Mental arithmetic operation (Manipulation) conditions |


### Normal Task 2: Detect stimulus ERP (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Probe events are short (<1 s); suitable for ERP epoching. Match/non-match accuracy from Response events can be used as trial-level correctness labels.

| Event | y | Meaning |
 |-------|---|------|
| `probe: 5R` / `6R` / `7R` | 0 | Keep condition detection |
| `probe: 5M` / `6M` / `7M` | 1 | Operating condition detection |

## Data Quality Notes

- 21-channel EEG; limited spatial resolution but sufficient for frontal working memory analyses.
- Event subtypes encoded in trial_type column (e.g., "delay period: 5M"); parse carefully.
- Multiple sessions per subject (156 files / ~26 subjects ~ 6 files each).

## References

- **Reference**: `VerbalWorkingMemory EEG dataset. OpenNeuro ds003655.`
