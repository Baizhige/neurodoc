# VerbalWorkingMemory

**Dataset**: `openneuro_ds003655` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003655
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 156 | **Channels**: 21 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

A modified Sternberg working memory task requiring either simple retention or mental manipulation (alphabetization) of letter sequences at three load levels (5, 6, or 7 letters). Participants encoded a letter sequence, maintained it across a delay period, then responded to a probe letter. The mental manipulation condition (alphabetization) places additional executive demands on working memory compared to simple retention. EEG measures during encoding, delay, and probe phases capture load-dependent neural activity.

## File Scan Result

> **Kernel SHA256**: `21a0164b0b6cf912dea56980c6fce67abeb2914c32eb269057c411453ddebbf5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `10_y0` | 3120 | event | raw | Probe event marker (retention condition) |
| `11_y1` | 3119 | event | raw | Probe event marker (manipulation condition) |
| `12_y0` | 3120 | event | raw | Probe event marker (retention condition) |
| `13_y1` | 3120 | event | raw | Probe event marker (manipulation condition) |
| `14_y0` | 3066 | event | raw | Probe event marker (retention condition) |
| `15_y1` | 2818 | event | raw | Probe event marker (manipulation condition) |
| `16_y0` | 3120 | event | raw | Probe event marker (retention condition) |
| `17_y1` | 3119 | event | raw | Probe event marker (manipulation condition) |
| `18_y0` | 3120 | event | raw | Probe event marker (retention condition) |
| `19_y1` | 3120 | event | raw | Probe event marker (manipulation condition) |
| `1_y1` | 563 | event | raw | Response-locked event marker (manipulation condition) |
| `20_y0` | 5020 | event | raw | Response event marker (retention condition) |
| `21_y1` | 14956 | event | raw | Response event marker (manipulation condition) |
| `22_y0` | 2927 | event | raw | Probe event marker (retention condition) |
| `23_y1` | 2132 | event | raw | Probe event marker (manipulation condition) |
| `24_y0` | 1467 | event | raw | Probe event marker (retention condition) |
| `25_y1` | 1970 | event | raw | Probe event marker (manipulation condition) |
| `26_y0` | 1419 | event | raw | Probe event marker (retention condition) |
| `27_y1` | 2104 | event | raw | Probe event marker (manipulation condition) |
| `28_y0` | 1582 | event | raw | Probe event marker (retention condition) |
| `29_y1` | 1744 | event | raw | Probe event marker (manipulation condition) |
| `2_y0` | 3120 | event | raw | Delay period event marker (retention condition) |
| `30_y0` | 1419 | event | raw | Probe event marker (retention condition) |
| `31_y1` | 2045 | event | raw | Probe event marker (manipulation condition) |
| `32_y0` | 1840 | event | raw | Probe event marker (retention condition) |
| `33_y1` | 4123 | event | raw | Response event marker (manipulation condition) |
| `34_y0` | 7440 | event | raw | Encoding/response event marker (retention condition) |
| `35_y1` | 11520 | event | raw | Encoding/response event marker (manipulation condition) |
| `36_y0` | 4219 | event | raw | Encoding event marker (retention condition) |
| `37_y1` | 3120 | event | raw | Encoding event marker (manipulation condition) |
| `38_y0` | 3100 | event | raw | Encoding event marker (retention condition) |
| `39_y1` | 2780 | event | raw | Encoding event marker (manipulation condition) |
| `3_y1` | 3120 | event | raw | Delay period event marker (manipulation condition) |
| `40_y0` | 1900 | event | raw | Encoding event marker (retention condition) |
| `41_y1` | 220 | event | raw | Encoding event marker (manipulation condition) |
| `4_y0` | 3119 | event | raw | Delay period event marker (retention condition) |
| `5_y1` | 3120 | event | raw | Delay period event marker (manipulation condition) |
| `6_y0` | 3120 | event | raw | Delay period event marker (retention condition) |
| `7_y1` | 3104 | event | raw | Delay period event marker (manipulation condition) |
| `8_y0` | 731 | event | raw | Baseline/task instruction period marker (retention) |
| `9_y1` | 3120 | event | raw | Delay period event marker (manipulation condition) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Verbal Working Memory - Retention vs Manipulation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -14.2 s, tmax = 2.2 s, target_events = [`11_y1`, `13_y1`, `15_y1`, `17_y1`, `19_y1`, `21_y1`, `23_y1`, `25_y1`, `27_y1`, `29_y1`, `31_y1`, `33_y1`, `35_y1`, `37_y1`, `39_y1`, `41_y1`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `11_y0`, `13_y0`, `15_y0`, `17_y0`, `19_y0`, `21_y0`, `23_y0`, `25_y0`, `27_y0`, `29_y0`, `31_y0`, `33_y0`, `35_y0`, `37_y0`, `39_y0` | 0 | Retention (simple maintenance) condition |
  | `11_y1`, `13_y1`, `15_y1`, `17_y1`, `19_y1`, `21_y1`, `23_y1`, `25_y1`, `27_y1`, `29_y1`, `31_y1`, `33_y1`, `35_y1`, `37_y1`, `39_y1`, `41_y1` | 1 | Manipulation (alphabetization) condition |
- **Super Meta Notes**: Event ID suffix `_y0` = Retention (R), `_y1` = Manipulation (M). Prefix number may encode load level (5/6/7) or event subtype. Cross-reference with events.tsv trial_type column for full condition metadata.
- **Evidence**:
  - DOI: 10.1111/ejn.15457 — Temporally distinct oscillatory codes of retention and manipulation of verbal working memory; theta/alpha/beta differences between conditions during encoding and delay phases
  - DOI: 10.1038/s41598-020-72940-5 — Electrophysiological underpinnings of variation in verbal working memory capacity; executive vs storage components of WM
- **Kernel Notes**: Extends across full trial structure (−14.2 to 2.2 s relative to probe alignment). Baseline: −11.5 to −10.5 s. Numeric event IDs replace conceptual names from analysis.md. Load level extractable from event prefix for ordinal covariates.

### Classical Task 2: Delay Period Working Memory State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 6.0 s, overlap = 0.5, target_events = [`10_y0`, `10_y1`, `12_y0`, `12_y1`, `14_y0`, `14_y1`, `16_y0`, `16_y1`, `18_y0`, `18_y1`, `20_y0`, `20_y1`, `22_y0`, `22_y1`, `24_y0`, `24_y1`, `26_y0`, `26_y1`, `28_y0`, `28_y1`, `30_y0`, `30_y1`, `32_y0`, `32_y1`, `34_y0`, `34_y1`, `36_y0`, `36_y1`, `38_y0`, `38_y1`, `40_y0`, `40_y1`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `10_y0`, `12_y0`, `14_y0`, `16_y0`, `18_y0`, `20_y0`, `22_y0`, `24_y0`, `26_y0`, `28_y0`, `30_y0`, `32_y0`, `34_y0`, `36_y0`, `38_y0`, `40_y0` | 0 | Retention condition during delay phase |
  | `10_y1`, `12_y1`, `14_y1`, `16_y1`, `18_y1`, `20_y1`, `22_y1`, `24_y1`, `26_y1`, `28_y1`, `30_y1`, `32_y1`, `34_y1`, `36_y1`, `38_y1`, `40_y1` | 1 | Manipulation condition during delay phase |
- **Super Meta Notes**: Long-duration delay events (>6 s) with sliding window segmentation (0.5 s overlap). Suffix `_y0` = Retention, `_y1` = Manipulation. Prefix encodes load level or delay subtype.
- **Evidence**:
  - DOI: 10.1111/ejn.15457 — Examines delay period subdividing into Delay1 (−6000 to −3000 ms) and Delay2 (−3000 to 0 ms) with oscillatory trajectory analysis
  - DOI: 10.1038/s41598-020-72940-5 — WM capacity analysis using encoding and delay phase oscillations
- **Kernel Notes**: Sliding windows capture sustained theta/alpha/beta dynamics across early and late delay subphases. Use 0.5 s overlap for temporal trajectory modeling.

### Normal Task 1: Verbal Working Memory Load Level Effects
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -14.2 s, tmax = 2.2 s, target_events = [`11_y0`, `11_y1`, `13_y0`, `13_y1`, `15_y0`, `15_y1`, `17_y0`, `17_y1`, `19_y0`, `19_y1`, `21_y0`, `21_y1`, `23_y0`, `23_y1`, `25_y0`, `25_y1`, `27_y0`, `27_y1`, `29_y0`, `29_y1`, `31_y0`, `31_y1`, `33_y0`, `33_y1`, `35_y0`, `35_y1`, `37_y0`, `37_y1`, `39_y0`, `39_y1`, `41_y0`, `41_y1`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | All probe events | Load level (5, 6, or 7) | Number of letters in the presented sequence |
- **Super Meta Notes**: Load level (5/6/7 letters) derived from event prefix number. Ordinal regression target. Extract from events.tsv trial_type column if prefix mapping is ambiguous.
- **Evidence**:
  - DOI: 10.1038/s41598-020-72940-5 — Analyzes WM capacity variation across three load levels (5/6/7 letters)
  - DOI: 10.1111/ejn.15457 — Uses load levels as within-subject factor in oscillatory analysis
- **Kernel Notes**: Load level available as ordinal covariate for regression or covariate for classification tasks. Cross-reference event prefixes with events.tsv to confirm load-to-prefix mapping.

### Potential Task 1: Stimulus Detection ERP Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`11_y0`, `11_y1`, `13_y0`, `13_y1`, `15_y0`, `15_y1`, `17_y0`, `17_y1`, `19_y0`, `19_y1`, `21_y0`, `21_y1`, `23_y0`, `23_y1`, `25_y0`, `25_y1`, `27_y0`, `27_y1`, `29_y0`, `29_y1`, `31_y0`, `31_y1`, `33_y0`, `33_y1`, `35_y0`, `35_y1`, `37_y0`, `37_y1`, `39_y0`, `39_y1`, `41_y0`, `41_y1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | All probe events | 1 | Stimulus onset (binary presence) |
- **Evidence**: No direct DOI reference. Plausible from paradigm: probe events represent letter stimulus presentations suitable for P300/N200 ERP analysis. Response events available for trial-level accuracy labels (match vs non-match).
- **Kernel Notes**: Tight window captures stimulus-locked ERP components. Baseline: −200 to 0 ms. Combine with Response events for accuracy-based trial rejection.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
