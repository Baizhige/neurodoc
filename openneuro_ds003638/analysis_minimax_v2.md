# EEG: Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms

**Dataset**: `openneuro_ds003638` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003638
**Category**: High-level Mental | **Subjects**: 57 | **Files (Completed)**: 57
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

This study employs three cross-species behavioral paradigms (5-Choice Continuous Performance Task [5CCPT], Probabilistic Reward/Punishment task [PRBP], and Pavlovian-to-Instrumental Transfer [PST]) to identify electrophysiological biomarkers associated with various behavioral dimensions including attention, impulsivity, and reward sensitivity. All 57 subjects completed all three paradigms in a single session. Event markers are encoded as numeric codes with paradigm suffix (e.g., "N 5CCPT", "N PRBP", "N PST").

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003638

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1 5CCPT`-`80 5CCPT` | 57 each | short | raw | 5-Choice CPT numeric trigger codes |
| `116 PRBP`, `117 PRBP` | 57 each | short | raw | Probabilistic reward/punishment task trigger codes |
| `31 PST`, `32 PST`, `39 PST` | 56-57 each | short | raw | Pavlovian-to-Instrumental Transfer task trigger codes |
| `STATUS` | 57 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: 5C-CPT Target vs Nontarget Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`1 5CCPT`, `2 5CCPT`, `3 5CCPT`, `4 5CCPT`, `5 5CCPT`, `6 5CCPT`, `7 5CCPT`, `8 5CCPT`, `9 5CCPT`, `10 5CCPT`, `11 5CCPT`, `12 5CCPT`, `13 5CCPT`, `14 5CCPT`, `15 5CCPT`, `16 5CCPT`, `17 5CCPT`, `18 5CCPT`, `19 5CCPT`, `20 5CCPT`, `21 5CCPT`, `22 5CCPT`, `23 5CCPT`, `24 5CCPT`, `25 5CCPT`, `26 5CCPT`, `27 5CCPT`, `28 5CCPT`, `29 5CCPT`, `30 5CCPT`, `31 5CCPT`, `32 5CCPT`, `33 5CCPT`, `34 5CCPT`, `35 5CCPT`, `36 5CCPT`, `37 5CCPT`, `38 5CCPT`, `39 5CCPT`, `40 5CCPT`, `41 5CCPT`, `42 5CCPT`, `43 5CCPT`, `44 5CCPT`, `45 5CCPT`, `46 5CCPT`, `47 5CCPT`, `48 5CCPT`, `49 5CCPT`, `50 5CCPT`, `51 5CCPT`, `52 5CCPT`, `53 5CCPT`, `54 5CCPT`, `55 5CCPT`, `56 5CCPT`, `57 5CCPT`, `58 5CCPT`, `59 5CCPT`, `60 5CCPT`, `61 5CCPT`, `62 5CCPT`, `63 5CCPT`, `64 5CCPT`, `65 5CCPT`, `66 5CCPT`, `67 5CCPT`, `68 5CCPT`, `69 5CCPT`, `70 5CCPT`, `71 5CCPT`, `72 5CCPT`, `73 5CCPT`, `74 5CCPT`, `75 5CCPT`, `76 5CCPT`, `77 5CCPT`, `78 5CCPT`, `79 5CCPT`, `80 5CCPT`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1 5CCPT`-`40 5CCPT` | 0 | Nontarget stimuli (5C-CPT correct rejections) * |
  | `41 5CCPT`-`80 5CCPT` | 1 | Target stimuli (5C-CPT hits) * |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — EEG time-frequency analysis comparing target vs nontarget conditions in 5C-CPT paradigm from OpenNeuro ds003638
- **Kernel Notes**: Event codes 1-40 typically denote nontargets, 41-80 denote targets in 5C-CPT. Verify mapping from events.tsv. Epoch parameters derived from paper: cue-locked tmin=-0.5s, tmax=+1.0s; response-locked tmin=-0.5s, tmax=0s. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Probabilistic Reward/Punishment (PRBP) High vs Low Probability Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`116 PRBP`, `117 PRBP`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `116 PRBP` | 0 | High probability reward/punishment condition * |
  | `117 PRBP` | 1 | Low probability reward/punishment condition * |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — EEG analysis comparing high vs low probability reward conditions in probabilistic learning task from OpenNeuro ds003638
- **Kernel Notes**: Event codes 116 and 117 correspond to high and low probability conditions. Verify from events.tsv which code maps to which probability level. Epoch parameters from paper: feedback-locked tmin=+0.25s, tmax=+0.55s.

### Primary Task 3: Pavlovian-to-Instrumental Transfer (PST) Early vs Late Trials
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`31 PST`, `32 PST`, `39 PST`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31 PST` | 0 | Early trials (first 50s of task) * |
  | `32 PST` | 1 | Late trials (last 50s of task) * |
  | `39 PST` | 2 | PST condition marker * |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — EEG analysis comparing early vs late trials in PRBT (PST) paradigm for effortful motivation biomarker identification
- **Kernel Notes**: Early vs late trial classification based on temporal position within PST block. Events 31 and 32 likely encode early/late conditions; verify mapping from events.tsv. Paper uses 1-s epochs averaged for first and last 50s of task.

### Primary Task 4: Cross-Paradigm Behavioral Dimension Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`1 5CCPT`, `2 5CCPT`, `3 5CCPT`, `4 5CCPT`, `5 5CCPT`, `6 5CCPT`, `7 5CCPT`, `8 5CCPT`, `9 5CCPT`, `10 5CCPT`, `11 5CCPT`, `12 5CCPT`, `13 5CCPT`, `14 5CCPT`, `15 5CCPT`, `16 5CCPT`, `17 5CCPT`, `18 5CCPT`, `19 5CCPT`, `20 5CCPT`, `21 5CCPT`, `22 5CCPT`, `23 5CCPT`, `24 5CCPT`, `25 5CCPT`, `26 5CCPT`, `27 5CCPT`, `28 5CCPT`, `29 5CCPT`, `30 5CCPT`, `31 5CCPT`, `32 5CCPT`, `33 5CCPT`, `34 5CCPT`, `35 5CCPT`, `36 5CCPT`, `37 5CCPT`, `38 5CCPT`, `39 5CCPT`, `40 5CCPT`, `41 5CCPT`, `42 5CCPT`, `43 5CCPT`, `44 5CCPT`, `45 5CCPT`, `46 5CCPT`, `47 5CCPT`, `48 5CCPT`, `49 5CCPT`, `50 5CCPT`, `116 PRBP`, `117 PRBP`, `31 PST`, `32 PST`, `39 PST`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 5CCPT events | 0 | Attention system (attentional control) |
  | PRBP events | 1 | Positive valence system (reward sensitivity) |
  | PST events | 2 | Cognitive system (cognitive control/effort) |
- **Super Meta Notes**: Derived from raw event paradigm suffixes (`5CCPT`, `PRBP`, `PST`). Kernel step: Group all 5CCPT events as attention-related, PRBP events as reward/positive valence, PST events as cognitive control. Maps three cross-species paradigms to RDoC behavioral dimension categories.
- **Evidence**:
  - DOI: (not identified in extraction) — Random forest/SVM classification of EEG features into four behavioral dimensions: positive valence, negative valence, cognitive, and attention systems
- **Kernel Notes**: Requires grouping events by paradigm suffix. Paper reports 4-class classification but only 3 paradigms available in this dataset (5CCPT→attention, PRBP→positive valence, PST→cognitive). Negative valence may require derived labels not directly available.

### Normal Task 1: 5CCPT stimulus classification (need to decode event meaning)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric trigger codes require decoding from events.tsv or dataset README. Events with suffix `5CCPT` correspond to the 5-Choice CPT; `PRBP` to reward/punishment; `PST` to Pavlovian transfer. Exact meaning of each numeric code must be verified from dataset documentation.

| Event | y | Meaning |
 |-------|---|------|
| `41 5CCPT` | 0 | 5CCPT correct response (need to confirm from events.tsv) |
| `43 5CCPT` | 1 | 5CCPT commission error (need to confirm from events.tsv) |


## Data Quality Notes

- 30+ distinct numeric trigger types; decode from events.tsv before epoching.
- All three paradigms recorded in a single 57-file session; paradigm blocks need to be separated by trigger suffix.
- `STATUS` is a single admin marker per file; exclude from epoching.

## References

- **Reference**: `Electrophysiological biomarkers of behavioral dimensions from cross-species paradigms. OpenNeuro ds003638.`
