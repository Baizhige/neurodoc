# Visual Oddball Task (256 channels)

**Dataset**: `ds002578` | **Data collection**: 2004 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **EEG recordings**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz

## Paradigm

This dataset contains a continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. The task description in the EEG sidecars states that five empty squares were shown continuously, one location was attended, and participants pressed a mouse button when a white disk appeared at the attended location.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: extract raw event codes and normalize them into stable labels.
- **Type 2 (Raw + Super meta integration)**: optionally derive response-linked or RT-linked labels, but only after an explicit event-pairing rule is validated.
- **Type 3 (Label-route orchestration)**: route normalized labels to EEGUnity-compatible channels such as `Annotation` or `stim`.

> **Selected Mode**: Type 2 + Type 3
> **Why**: raw condition codes support direct stimulus classification, and reaction time should be represented as a derived label produced through super meta integration.
> **Primary Label Routes**: `Annotation`, optionally `stim`

## Event Structure

`events.json` defines the semantic meaning of the coded event values. Across both subjects, the verified totals are:

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `33` | 240 | short | raw | Target, oddball, attend position 3 / cue position 3 |
| `44` | 239 | short | raw | Target, oddball, attend position 4 / cue position 4 |
| `31` | 240 | short | raw | Non-target distractor, attend position 3 / cue position 1 |
| `34` | 239 | short | raw | Non-target distractor, attend position 3 / cue position 4 |
| `35` | 240 | short | raw | Non-target distractor, attend position 3 / cue position 5 |
| `41` | 238 | short | raw | Non-target distractor, attend position 4 / cue position 1 |
| `42` | 239 | short | raw | Non-target distractor, attend position 4 / cue position 2 |
| `43` | 240 | short | raw | Non-target distractor, attend position 4 / cue position 3 |
| `45` | 239 | short | raw | Non-target distractor, attend position 4 / cue position 5 |
| `Picture` | 5939 | short | raw | Generic picture/stimulus presentation marker without condition identity |
| `Response` | 1202 | short | raw | Participant response marker |
| `target_rt` | derived | short | super meta integration | Reaction time derived by pairing validated target events (`33`, `44`) with participant responses |
| `boundary` | 58 | admin | raw | Discontinuous boundary marker; exclude from targets |
| `203` | 1 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |
| `217` | 2 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |
| `237` | 1 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |

Summary of task-relevant coded triggers:

- Target-coded events: `33`, `44` -> 479 total
- Non-target-coded events: `31`, `34`, `35`, `41`, `42`, `43`, `45` -> 1675 total
- The `trial_type`, `response_time`, and `stim_file` columns are present but entirely empty in both `_events.tsv` files.

## Tasks

### Primary Task 1: Target-response Reaction Time Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 0.8 s`, `target_events = ['33', '44']`
- **Label Route**: `Annotation`
- **Meta Level**: super meta integration
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `33`, `44` | continuous | Reaction time for validated correct target-response trials |
- **Super Meta Notes**: derive `target_rt` by pairing target-coded events (`33`, `44`) with their associated participant responses and retaining only correct target-response trials.
- **Evidence**:
  - DOI: `10.1523/JNEUROSCI.3477-07.2007` studies this visual selective-attention oddball paradigm, analyzes correct target-response trials with responses 150-1000 ms after target onset, and relates single-trial EEG activity to reaction time. The paper also reports two 253-channel recordings used for source localization support.
- **Kernel Notes**: this is the most literature-supported primary task. The current BIDS `_events.tsv` files do not provide precomputed `response_time`, so trial construction and RT derivation must be done explicitly before label generation.

### Normal Task 1: Target vs Non-target Oddball Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 0.8 s`, `target_events = ['33', '44', '31', '34', '35', '41', '42', '43', '45']`
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `33`, `44` | 1 | Target / oddball stimulus |
  | `31`, `34`, `35`, `41`, `42`, `43`, `45` | 0 | Non-target / distractor stimulus |
- **Notes**: event semantics are directly supported by `events.json`, but this is a downstream decoding formulation rather than the main analysis explicitly reported in the cited paper.

### Normal Task 2: Condition-code Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 0.8 s`, `target_events = ['31', '33', '34', '35', '41', '42', '43', '44', '45']`
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31` | 31 | Non-target, attend 3 / cue 1 |
  | `33` | 33 | Target, attend 3 / cue 3 |
  | `34` | 34 | Non-target, attend 3 / cue 4 |
  | `35` | 35 | Non-target, attend 3 / cue 5 |
  | `41` | 41 | Non-target, attend 4 / cue 1 |
  | `42` | 42 | Non-target, attend 4 / cue 2 |
  | `43` | 43 | Non-target, attend 4 / cue 3 |
  | `44` | 44 | Target, attend 4 / cue 4 |
  | `45` | 45 | Non-target, attend 4 / cue 5 |
- **Notes**: useful for finer-grained condition decoding, but not explicitly framed as the primary task in the cited paper.

### Normal Task 3: Continuous Segmentation
- **Task Type**: regression / self-supervised pretraining support
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s`, `overlap = 0.5`
- **Label Route**: `Annotation`
- **Target Definition**: `null`
- **Notes**: useful as a generic fallback, but this dataset does contain trial-related events, so segmentation should not replace event-based paradigms when task decoding is the goal.

## Data Quality Notes
- The dataset is small: 2 subjects and 2 EEG recordings.
- Event markers are present and abundant; the main issue is semantic normalization, not event absence.
- EEG sidecars confirm 256 EEG channels and 256 Hz sampling.
- The unusual codes `203`, `217`, and `237` are rare and not documented in `events.json`; exclude them from default supervised targets unless manually interpreted.
- `participants.tsv` contains a duplicated `participant_id` column header, which is a minor metadata formatting issue.

## References
- `dataset_description.json`
- `README`
- `events.json`
- `sub-001/eeg/sub-001_task-attention_events.tsv`
- `sub-002/eeg/sub-002_task-attention_events.tsv`
