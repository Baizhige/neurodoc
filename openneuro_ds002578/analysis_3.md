# Visual Oddball Task (256 channels)

**Dataset**: `ds002578` | **Data collection**: 2004 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **EEG recordings**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz

## Paradigm

This dataset contains a continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. The task description in the EEG sidecars states that five empty squares were shown continuously, one location was attended, and participants pressed a mouse button when a white disk appeared at the attended location.

The original `analysis_minimax_v2.md` claim that "no event markers were detected" is incorrect. Both BIDS `_events.tsv` files contain rich event streams, including condition codes, generic `Picture` markers, `Response` markers, and `boundary` markers. However, the event coding is not already normalized into convenient labels such as `target_visual_stimulus`, and reaction-time pairing is not directly provided in the TSV files.

## Validation Basis

- Checked `dataset_description.json`, `README`, `participants.tsv`, `events.json`, both EEG JSON sidecars, and both `_events.tsv` files.
- Reused `test2.py` and `test3.py` to confirm the actual event-value distribution.
- `test.py` could not be run in the current environment because `mne` is not installed, so raw `.set` annotations were not revalidated from the EEGLAB files directly.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: extract raw event codes and normalize them into stable labels.
- **Type 2 (Raw + Super meta integration)**: optionally derive response-linked or RT-linked labels, but only after an explicit event-pairing rule is validated.
- **Type 3 (Label-route orchestration)**: route normalized labels to EEGUnity-compatible channels such as `Annotation` or `stim`.

> **Selected Mode**: Type 1 + Type 3 as default; Type 2 optional
> **Why**: raw condition codes are sufficient for robust stimulus-classification tasks, but not yet sufficient for trustworthy reaction-time labels without extra derivation rules.
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
| `boundary` | 58 | admin | raw | Discontinuous boundary marker; exclude from targets |
| `203` | 1 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |
| `217` | 2 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |
| `237` | 1 | admin/unknown | raw | Rare code not described in `events.json`; inspect manually if used |

Summary of task-relevant coded triggers:

- Target-coded events: `33`, `44` -> 479 total
- Non-target-coded events: `31`, `34`, `35`, `41`, `42`, `43`, `45` -> 1675 total
- The `trial_type`, `response_time`, and `stim_file` columns are present but entirely empty in both `_events.tsv` files.

## Tasks

### Primary Task 1: Target vs Non-target Oddball Classification
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

- **Why this is reliable**: target vs non-target status is explicitly encoded in `events.json`, so no inferred RT pairing is required.
- **Kernel Notes**: prefer epoching on the coded condition markers rather than generic `Picture`, because `Picture` does not preserve target identity.

### Primary Task 2: Condition-code Classification
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

- **Why this is useful**: supports finer-grained decoding of attended position / cue configuration beyond a binary oddball split.

### Optional Derived Task: Response / Reaction-time Modeling
- **Task Type**: classification or regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Recommended Status**: optional, not default
- **Meta Level**: super
- **Current Limitation**:
  - `Response` markers exist, but `response_time` is empty.
  - Simple nearest-neighbor pairing between coded triggers, `Picture`, and `Response` can yield ambiguous or even negative latencies, which means event ordering must be validated before deriving RT labels.
  - The current BIDS event tables do not provide a ready-made one-row-per-trial structure.
- **Safe recommendation**: only add RT labels after building and checking an explicit trial-construction rule on the original event sequence, ideally with the raw EEGLAB annotations loaded through `mne`.

### Normal Task 1: Continuous Segmentation
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

## Recommended Revisions Relative to the Previous Version

- Replace "no event markers were detected" with "event markers exist, but trial labels are encoded as numeric condition codes plus generic `Picture` / `Response` markers."
- Replace `Subjects: N/A` with `Subjects: 2`.
- Replace `Files (Completed): 2` with `EEG recordings: 2`.
- Replace RT-based primary tasks with target/non-target and condition-code classification as the default tasks.
- Keep RT modeling only as an optional derived analysis until pairing rules are validated on the raw event stream.

## References

- `dataset_description.json`
- `README`
- `events.json`
- `sub-001/eeg/sub-001_task-attention_events.tsv`
- `sub-002/eeg/sub-002_task-attention_events.tsv`
