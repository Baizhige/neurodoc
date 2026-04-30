# 3M-CPSEED: EEG Dataset for Chinese Pinyin Production in Overt, Silent-Intended, and Imagined Speech

**Dataset**: `openneuro_ds006465` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006465
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 84 | **Channels**: 33 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Participants performed three modes of speech production - overt (spoken aloud), silent-intended (mouthed without sound), and imagined (mental speech without movement) - for specific Chinese Pinyin sounds including initials and finals. The dataset enables comparison of neural signatures across overt, silent, and imagined speech conditions. Each trial consisted of a visual cue followed by a production phase and a response confirmation. Numeric event codes encode specific phoneme types and experimental block markers.

## File Scan Result

> **Kernel SHA256**: `8d982b8f1dc1dee89fd6d8b12eabee17634bc734ad5fdf3d830146a792f0b5df`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 1843 | event | raw | Primary phoneme trigger (pinyin syllable code) |
| `event_100499` | 1 | event | raw |  |
| `event_120823` | 3 | event | raw | System/technical event |
| `event_122056` | 1 | event | raw |  |
| `event_123418` | 1 | event | raw |  |
| `event_126117` | 1 | event | raw |  |
| `event_126365` | 1 | event | raw |  |
| `event_127548` | 1 | event | raw |  |
| `event_127688` | 3 | event | raw | System/technical event |
| `event_127743` | 1 | event | raw |  |
| `event_127850` | 1 | event | raw |  |
| `event_128227` | 2 | event | raw | System/technical event |
| `event_128228` | 1 | event | raw |  |
| `event_128335` | 2 | event | raw | System/technical event |
| `event_128393` | 1 | event | raw |  |
| `event_128418` | 1 | event | raw |  |
| `event_128477` | 1 | event | raw |  |
| `event_128511` | 1 | event | raw |  |
| `event_128566` | 1 | event | raw |  |
| `event_128601` | 1 | event | raw |  |
| `event_128835` | 2 | event | raw | System/technical event |
| `event_128884` | 1 | event | raw |  |
| `event_129083` | 1 | event | raw |  |
| `event_129129` | 3 | event | raw | System/technical event |
| `event_129441` | 1 | event | raw |  |
| `event_129467` | 1 | event | raw |  |
| `event_129597` | 1 | event | raw |  |
| `event_129641` | 1 | event | raw |  |
| `event_129682` | 1 | event | raw |  |
| `event_129707` | 3 | event | raw | System/technical event |
| `event_129771` | 1 | event | raw |  |
| `event_129841` | 1 | event | raw |  |
| `event_129848` | 1 | event | raw |  |
| `event_129923` | 1 | event | raw |  |
| `event_129933` | 1 | event | raw |  |
| `event_129965` | 1 | event | raw |  |
| `event_130033` | 2 | event | raw | System/technical event |
| `event_130055` | 1 | event | raw |  |
| `event_130091` | 1 | event | raw |  |
| `event_130107` | 1 | event | raw |  |
| `event_130148` | 1 | event | raw |  |
| `event_130164` | 1 | event | raw |  |
| `event_130236` | 1 | event | raw |  |
| `event_130309` | 1 | event | raw |  |
| `event_130360` | 1 | event | raw |  |
| `event_130383` | 1 | event | raw |  |
| `event_130384` | 1 | event | raw |  |
| `event_130409` | 1 | event | raw |  |
| `event_130442` | 1 | event | raw |  |
| `event_130580` | 1 | event | raw |  |
| `event_130593` | 1 | event | raw |  |
| `event_131061` | 51 | event | raw | Trial/block marker: speech mode encoding |
| `event_131062` | 52 | event | raw | Trial/block marker: speech mode encoding |
| `event_131063` | 50 | event | raw | Trial/block marker: speech mode encoding |
| `event_131070` | 50 | event | raw | Trial/block marker: speech mode encoding |
| `event_131071` | 50 | event | raw | Trial/block marker: speech mode encoding |
| `event_80666` | 1 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Pinyin Syllable Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_1` | 0 | Phoneme trigger (primary numeric code; decode specific Pinyin from raw events.tsv) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — validates 3M-CPSEED dataset with >55% accuracy for pairwise pinyin syllable classification; 10 phoneme classes (a, i, u, ü, m, f, j, l, k, ch) encoded as numeric event codes
- **Kernel Notes**: Primary phoneme trigger `event_1` has 1843 occurrences across dataset. Verify raw events.tsv to decode actual phoneme identity and confirm all 10 pinyin categories are present. Bandpass filter 0.5-40 Hz recommended. Exclude response-related events.

### Classical Task 2: Speech Production Mode Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`event_131061`, `event_131062`, `event_131063`, `event_131070`, `event_131071`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_131061` | 0 | Trial marker: overt speech block |
  | `event_131062` | 0 | Trial marker: overt speech block |
  | `event_131063` | 0 | Trial marker: overt speech block |
  | `event_131070` | 1 | Trial marker: silent-intended speech block |
  | `event_131071` | 1 | Trial marker: silent-intended speech block |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — validates EEGNet-based binary classification achieving 60-73% accuracy for speech mode discrimination (overt vs silent vs imagined); experimental design specifies distinct temporal windows per mode
- **Kernel Notes**: Events 131061-131071 (~50-52 counts each) likely encode trial-level markers or condition blocks. Verify raw BIDS events.tsv to confirm mapping to overt/silent/imagined speech modes. Derive mode labels from block assignment or temporal position within experimental structure. Bandpass filter 0.5-40 Hz.

### Normal Task 1: Multi-Block Speech Mode Classification (3-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s, target_events = [`event_131061`, `event_131062`, `event_131063`, `event_131070`, `event_131071`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Overt speech block markers | 0 | Overt speech (spoken aloud) |
  | Silent-intended block markers | 1 | Silent-intended (mouthed without sound) |
  | Imagined speech block markers | 2 | Imagined (mental speech) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — supports 3-class discrimination across overt, mouthed, and imagined speech; paper establishes experimental paradigm with 4 blocks per subject
- **Kernel Notes**: Requires verification of raw events.tsv to identify imagined speech block markers (events 131064-131069 may correspond). Extract extended epochs covering full trial duration (10s) to capture mode-specific neural dynamics. Temporal windowing may be needed to isolate distinct production phases.

### Potential Task 1: Pinyin Syllable × Speech Mode Cross-Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_1`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_1` | (phoneme, mode) | Combined label: phoneme type × speech production mode |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — paradigm supports joint analysis of phoneme identity and speech mode; 10 phonemes × 3 modes = 30-class classification potential
- **Kernel Notes**: Combines pinyin syllable identity with speech mode into compound labels. Requires combining `event_1` triggers with block-level mode markers. High-dimensional classification problem; may benefit from hierarchical or multi-task approach.

### Potential Task 2: Phoneme-Specific Neural Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`event_1`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_1` | see events.tsv | Per-epoch annotation of phoneme identity and timing |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — experimental design specifies 10 distinct pinyin phonemes with known temporal profiles; event_1 aggregates all phoneme triggers for epoch extraction
- **Kernel Notes**: Primary task is epoch extraction from phoneme trigger events. Subsequent analysis (decoding, ERP averaging, time-frequency) can be applied post-epoch. Verify events.tsv for phoneme-level annotations within individual trial records.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
