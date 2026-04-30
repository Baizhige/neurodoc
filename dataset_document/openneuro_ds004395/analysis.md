# Penn Electrophysiology of Encoding and Retrieval Study (PEERS)

**Dataset**: `openneuro_ds004395` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004395
**Category**: High-level Mental | **Subjects**: 300 | **Files (Completed)**: 6480 | **Manual Review**: Pending
**Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

A large-scale study investigating the electrophysiological correlates of memory encoding and retrieval using various free recall tasks. Participants encoded word lists and subsequently recalled them (free recall), also performing recognition memory tasks. The study provides a rich dataset for ERP analysis of encoding success, retrieval effort, and memory-related oscillations.

## File Scan Result

> **Kernel SHA256**: `9d157f1bc9002373cf993976877bffb0f85323ccced6baad5b1ae2e0ee065340`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_15` | 811374 | event | raw | Recognition/recall-related stimulus events |
| `event_65536` | 21 | event | raw | Session or block-level special marker |
| `event_65544` | 588 | event | raw | Distractor or rest-period marker |
| `event_65551` | 113 | event | raw | Break or reward-state marker |
| `event_8` | 5804724 | event | raw | Word presentation during encoding phase |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Memory Encoding Success Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`WORD`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `WORD` | 0 | Not subsequently recalled |
  | `WORD` | 1 | Successfully recalled |
- **Evidence**: DOI: 10.1038/s41467-024-46926-0 — "EEG decoders track memory dynamics" (Nature Communications, 2024). 98 participants, 24 sessions, logistic regression classifiers on spectral features (theta, alpha, beta, HFA) from scalp EEG. Predicts encoding success by linking WORD events to REC_WORD_VV (voice-verified recall) labels.
- **Kernel Notes**: Epoch window (-0.2s to 1.0s) captures N170/P300 ERP complex during word encoding. Classification: recalled vs. not-recalled items. Cross-reference REC_WORD_VV for ground truth successful encoding labels.

### Classical Task 2: Recognition Memory Old/New Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.2 s, target_events = [`RECOG_TARGET`, `RECOG_LURE`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `RECOG_TARGET` | 0 | Old item (previously seen) |
  | `RECOG_LURE` | 1 | New item (lure/foil) |
- **Evidence**:
  - DOI: 10.1038/s41467-024-46926-0 — Demonstrates EEG decoders on PEERS recognition memory data.
  - DOI: 10.31234/osf.io/64j58 — Single-trial logistic regression classifiers on 100ms time windows (500-800ms) to predict DDM drift rate for recognition memory decisions.
- **Kernel Notes**: Stimulus-locked epochs aligned to RECOG_TARGET (old) and RECOG_LURE (new) onset. Window covers pre-stimulus baseline, stimulus processing, and response period. Can extend to confidence-based classification using RECOG_CONF labels.

### Normal Task 1: Free Recall Retrieval Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`REC_WORD`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `REC_WORD` | 0 | Intrusion/incorrect recall |
  | `REC_WORD` | 1 | Correct recall |
- **Evidence**: DOI: 10.1038/s41467-024-46926-0 — "EEG decoders track memory dynamics" uses REC_WORD and REC_WORD_VV events for retrieval success classification. Validates that EEG spectral features in pre-retrieval window (500ms preceding recall) predict correct vs. intrusion recall.
- **Kernel Notes**: Epoch window captures recall initiation and vocalization period. Cross-reference REC_WORD_VV (voice-verified) for ground truth successful retrieval. REC_START marks recall period onset; use for period segmentation if needed.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
