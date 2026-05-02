# Sternberg Working Memory

**Dataset**: `openneuro_ds004117` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004117
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 85 | **Channels**: 71 | **Sampling Rate**: 250 Hz | **Manual Review**: Pending

## Paradigm

A modified Sternberg working memory task in which participants selectively memorized sets of 3, 5, or 7 target letters (marked with lowercase 'g' prefix, e.g., gH) while ignoring identical-font distractor letters. After a retention period, a probe letter was presented and participants indicated with auditory feedback whether it was in the memorized set. The study investigates frontal midline EEG dynamics (particularly theta oscillations) during working memory maintenance.

## File Scan Result

> **Kernel SHA256**: `a1aa1febcae4dcd7ad1da31abd8aa672c8470335dd76fcd47621ceee42df047e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Working Memory Encoding - Memorize vs Ignore Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`WM`, `nonWM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `WM` | 1 | Working memory encoding trial (Memorize letters) |
  | `nonWM` | 0 | Non-working-memory distractor trial (Ignore letters) |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2005.04.014` — Frontal midline theta dynamics analysis during modified Sternberg working memory task, classifying Memorize vs Ignore letter trials with memory load manipulation (3, 5, 7 letters), using 3-s epochs (tmin=-1.0s, tmax=2.0s) relative to letter onset.
  - DOI: `10.1371/journal.pone.0030135` — Independent EEG sources analysis using the same SCCN 71-channel Sternberg WM dataset, validating Memorize vs Ignore trial classification paradigm.
- **Kernel Notes**: Extract epochs around WM and nonWM event markers. Exclude event ID `255` (admin/system marker). The WM event marks trial start where participants memorize g-prefixed target letters; nonWM marks distractor trials to ignore. Optionally analyze memory load (3, 5, 7 letters) as secondary analysis by examining preceding WM trial context. Primary frequency band of interest is frontal midline theta (4-8 Hz).

---

### Classical Task 2: Memory Load Classification (3, 5, 7 items)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`WM`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `WM` (load=3) | 0 | Working memory encoding with 3 letters |
  | `WM` (load=5) | 1 | Working memory encoding with 5 letters |
  | `WM` (load=7) | 2 | Working memory encoding with 7 letters |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2005.04.014` — Analyzed theta power changes with memory load (3, 5, 7 letters), showing increased frontal midline theta for higher memory loads.
- **Kernel Notes**: Requires super-meta level labeling derived from trial metadata specifying set size. Load level (3/5/7) must be parsed from events.tsv sidecar or derived from count of preceding g-prefixed letter events within each WM trial context. Verify set-size encoding in dataset documentation before analysis. Exclude event ID `255` (admin/system marker).

---

### Potential Task 1: WM vs Non-WM Letter Encoding (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`WM`, `nonWM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `WM` | 1 | Working memory encoding trial |
  | `nonWM` | 0 | Non-working-memory (distractor) trial |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2005.04.014` — Supports fine-grained analysis of letter-specific processing during the Sternberg WM paradigm.
- **Kernel Notes**: Shorter epoch window focused on individual letter presentation events (gA-gZ for memorization targets, A-Z for distractors). Captures early ERP components (N100, P200) and letter-specific processing. Exclude event ID `255` (admin/system marker). Fine-grained letter event analysis (A-Z, gA-gZ) may provide additional ERP resolution but requires careful event code mapping. 23 subjects x ~3.7 sessions on average = 85 files.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
