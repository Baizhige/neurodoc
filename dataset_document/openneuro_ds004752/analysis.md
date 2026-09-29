# Dataset of Intracranial EEG, Scalp EEG and Beamforming Sources from Epilepsy Patients - Verbal Working Memory

**Dataset**: `openneuro_ds004752` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004752
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 134 | **Channels**: 64 | **Sampling Rate**: 2000 Hz | **Manual Review**: Pending

## Paradigm

Epilepsy patients performed a modified Sternberg verbal working memory task consisting of encoding, maintenance, and recall phases while simultaneous scalp and intracranial EEG were recorded. The dataset includes iEEG from depth electrodes, scalp EEG, single-unit neuron spike times, and electrode localizations, enabling multi-level analysis of memory processes. No trial-level event annotations are available in the BIDS events.tsv.

## File Scan Result

> **Kernel SHA256**: `cbbd8a347512f0de5e8601d7dd5fb4127fc0c64a004723fed5204e1db86d3f6f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `system: high_sampling_rate_2000Hz` | 98 | event | raw | High sampling rate indicator (2000 Hz) |
| `system: paradigm_sternberg_vwm` | 134 | event | raw | Sternberg verbal working memory paradigm marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Verbal Working Memory Phase Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: encoding phase: tmin=0.0, tmax=2.0; maintenance phase: tmin=0.0, tmax=3.0
- **Label Route**: `event`
- **Target Definition**:

| Event ID | Value | Meaning |
|---|---|---|
| stimulus_onset | continuous | Encoding phase onset; Granger causality direction (auditory→hippocampus during encoding) |
| probe_onset | continuous | Recall phase onset; Granger causality direction (hippocampus→auditory during maintenance) |
| response | binary | Correct (1) vs incorrect (0) recall response |
- **Meta Level**: super
- **Evidence**: DOI: 10.7554/eLife.78677 | 15 participants, 71 sessions, modified Sternberg verbal WM task (4/6/8 letters). Analyzes theta-band [4–8 Hz] Granger causality between hippocampus and auditory cortex during encoding and maintenance phases. Reveals directional information flow reversal between encoding and recall phases. |
- **Kernel Notes**: This dataset is derived from the same data collection as the eLife publication. The original dataset includes per-trial metadata (set size, match/mismatch, response correctness, RT) and event markers (stimulus_onset, probe_onset, response). Verify availability in behavioral log files if not present in BIDS events.tsv. High sampling rate (2000 Hz) allows detailed theta-band analysis.

---

### Potential Task 1: Working Memory Load Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: encoding: tmin=0.0, tmax=2.0; maintenance: tmin=0.0, tmax=3.0
- **Label Route**: `event`
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| stimulus_onset | 3 classes | Set size 4 (low WM load) vs 6 (medium) vs 8 (high) |
| probe_onset | 3 classes | Set size 4 vs 6 vs 8 |
- **Meta Level**: super
- **Evidence**: DOI: 10.1038/s41467-023-38571-w | DOI: 10.1038/s41467-025-60681-w | 14/13 patients, iEEG from amygdala/hippocampus/entorhinal cortex. Uses multivariate RSA and SVM decoding to classify WM load from neural power features [1–40 Hz]. Set size modulation of neural activity enables classification of 3 load levels. |
- **Kernel Notes**: Requires trial-level set size labels. Multivariate pattern analysis of iEEG power features can decode WM load across memory circuit regions. Consider cross-regional decoding generalization.

---

### Potential Task 1: Continuous Segmentation (Fallback)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `misc`
- **Target Definition**: None (no event markers in BIDS events.tsv)
- **Meta Level**: raw
- **Target Definition**:

| MISC Channel Name | Y Mapping Notes |
|---|---|
| Needs verification | No MISC channels found in File Scan Result; fallback segmentation task without event markers. Requires manual verification of available auxiliary channels or alternative Y derivation strategy. |

- **Evidence**: DOI: 10.7554/eLife.78677 | Paradigm phases (encoding 2s, maintenance 3s) are conceptually documented but not timestamped in available event files. |
- **Kernel Notes**: Use only if behavioral log files with trial timing are unavailable. Sliding-window segmentation creates pseudo-trials for continuous analysis. Downsample to 250–500 Hz before segmentation to reduce computational load while preserving theta-band [4–8 Hz] content relevant for WM research. Exclude ictal periods from epilepsy patients.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
