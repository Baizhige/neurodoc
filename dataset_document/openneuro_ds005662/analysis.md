# A high-quality EEG dataset for studying visual touch perception

**Dataset**: `openneuro_ds005662` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005662
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 65 | **Sampling Rate**: 2048 Hz | **Manual Review**: Pending

## Paradigm

Participants viewed rapid streams of videos depicting touch to a hand or an object to investigate visual touch perception. The experiment used target and non-target trials to measure brain responses to observed touch. EEG recordings were captured continuously at 2048 Hz, with discrete event markers (event_40708 and event_40704) indicating stimulus onsets for epoch segmentation.

## File Scan Result

> **Kernel SHA256**: `ae6939484ae682db3726c4e319b9322ca64e4283bd38ac5c8be8b4302f28db0e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_106240` | 1 | event | raw | Unclassified event marker |
| `event_106244` | 1 | event | raw | Unclassified event marker |
| `event_260` | 1 | event | raw | Unclassified event marker |
| `event_27652` | 2 | event | raw | Unclassified event marker |
| `event_32516` | 118 | event | raw | Rare stimulus or response event |
| `event_32772` | 1 | event | raw | Unclassified event marker |
| `event_36100` | 1 | event | raw | Unclassified event marker |
| `event_40704` | 9130 | event | raw | Secondary stimulus onset (lower-frequency marker) |
| `event_40708` | 235546 | event | raw | Primary stimulus onset (high-frequency marker) |
| `event_512` | 3 | event | raw | Unclassified event marker |
| `event_516` | 36 | event | raw | Unclassified event marker |
| `event_57092` | 4 | event | raw | Unclassified event marker |
| `event_65280` | 1 | event | raw | Unclassified event marker |
| `event_65284` | 67 | event | raw | Unclassified event marker |
| `event_66052` | 3 | event | raw | Unclassified event marker |
| `event_98052` | 5 | event | raw | Unclassified event marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Touch Perception - Perspective Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`event_40708`, `event_40704`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_40708` | 0 | self-perspective touch video |
  | `event_40708` | 1 | other-perspective touch video |
  | `event_40704` | 0 | self-perspective touch video |
  | `event_40704` | 1 | other-perspective touch video |
- **Super Meta Notes**: Labels derived from video metadata (perspective field: self vs other). Kernel step: (1) Read video filenames/timestamps linked to event_40708/event_40704, (2) Match to Validated Touch-Video Database metadata, (3) Extract perspective label (0=self, 1=other). Verify event-to-video mapping via stimulus log or BIDS sidecar. CRITICAL: Original analysis.md incorrectly stated "no_events"; actual stimulus events are event_40708 (235k) and event_40704 (9k).
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — MVPA decoding of self vs other perspective from EEG epochs time-locked to stimulus onset; 90 unique videos in 4 orientations with 2,880 trials total
  - DOI: 10.1038/s41597-026-06714-5 — Validation dataset for visual touch perception, perspective 2-class classification confirmed decodable
- **Kernel Notes**: High event count (235k) suggests rapid stimulus presentation (~600ms videos). Align epochs to primary stimulus marker (event_40708). Validate epoch counts against expected ~100 trials/subject × 80 subjects.

### Classical Task 2: Visual Touch Perception - Material Classification (8 categories)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`event_40708`, `event_40704`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_40708` | 0 | wood material |
  | `event_40708` | 1 | plastic material |
  | `event_40708` | 2 | glass material |
  | `event_40708` | 3 | metal material |
  | `event_40708` | 4 | fabric material |
  | `event_40708` | 5 | rubber material |
  | `event_40708` | 6 | ceramic material |
  | `event_40708` | 7 | other material |
- **Super Meta Notes**: Labels derived from video metadata (material field: 8 categories). Kernel step: Match event timestamps to video filenames, then lookup material category from Validated Touch-Video Database. Corrected from original "no_events" placeholder.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — MVPA decoding of 8 material categories from EEG epochs
  - DOI: 10.1038/s41597-026-06714-5 — Multi-class material classification (8 categories) using MVPA validated
- **Kernel Notes**: 8-class problem has lower expected decodability than 2-class perspective. Consider temporal windows focused on mid-latency components (200-400ms).

### Classical Task 3: Visual Touch Perception - Hand Orientation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`event_40708`, `event_40704`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_40708` | 0 | left hand, self-perspective |
  | `event_40708` | 1 | right hand, self-perspective |
  | `event_40708` | 2 | left hand, other-perspective |
  | `event_40708` | 3 | right hand, other-perspective |
- **Super Meta Notes**: Labels derived from video metadata (combining hand laterality + perspective). Kernel step: Extract 4-category label from video filenames or metadata fields. Corrected from original "no_events" placeholder.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — Decoding hand orientation (left/right hand × self/other perspective = 4 categories)
  - DOI: 10.1038/s41597-026-06714-5 — Hand orientation 4-class classification validated
- **Kernel Notes**: 4-class classification; verify expected trial counts per class (~720 trials/class across dataset).

### Potential Task 4: Visual Touch Perception - Valence Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`event_40708`, `event_40704`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_40708` | continuous | valence rating (negative to positive scale from Validated Touch-Video Database) |
  | `event_40708` | continuous | arousal rating (low to high) |
- **Super Meta Notes**: Valence/arousal ratings available in Validated Touch-Video Database but NOT validated in EEG decoding papers. Paradigm plausible (affective response to observed touch), but requires independent validation.
- **Evidence**: None — valence/arousal regression NOT supported by references (DOIs only validate classification tasks for perspective and material).
- **Kernel Notes**: Requires external metadata lookup; no direct evidence this signal is decodable from EEG in this dataset.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
