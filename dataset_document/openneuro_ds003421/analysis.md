# HD-EEGtask (Dataset 2)

**Dataset**: `openneuro_ds003421` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003421
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 80 | **Manual Review**: Pending
**Channels**: 257 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants completed a multi-condition experiment including resting state, visual and auditory object naming tasks, and a recognition-based working memory task, with high-density 257-channel EEG recording. This is Dataset 2 of the conneXion project (companion to ds003420). Trigger codes 0 and 1 mark stimulus onset and response events; the specific kernel provides speech onset timing as `response_time` for regression analysis.

## File Scan Result

> **Kernel SHA256**: `80f72fbeeaad8d1b86fa438eb424325cb767158946812bbb41972163629f7fe7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger/DIN1` | 5512 | event | raw | Stimulus onset trigger from EGI system |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Object Naming Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.5 s, overlap = 0.5, target_events = ["1", "0"] (conditions mapped to stimulus categories)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---|
| "1" | 0 | Visual stimulus category: animals |
| "0" | 1 | Visual stimulus category: tools |

- **Evidence**: DOI: 10.1109/tpami.2017.2750160 (binary classification of stimulus categories animals vs. tools during visual picture naming task; 256-channel dense EEG at 1 KHz; network similarity analysis between categories)
- **Kernel Notes**: Trigger codes 0/1 require semantic decoding from events.tsv to map to specific stimulus categories (animals vs. tools). High-density 257-channel array increases computational overhead. Long event epoching captures sustained processing periods during naming. Verify condition assignments against conneXion project documentation.

### Potential Task 1: Working Memory Recognition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, segment_length = 2.0 s, overlap = null, target_events = ["1", "0"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---|
| "1" | recognition_target | Recognition-based working memory trial condition 1 |
| "0" | recognition_target | Recognition-based working memory trial condition 0 |

- **Evidence**: DOI: 10.1038/s41597-021-00821-1 (paradigm description includes recognition-based working memory task; dataset documentation confirms multi-condition design)
- **Kernel Notes**: Segmentation approach recommended for recognition WM task requiring condition-specific epochs. Segment length of 2.0s aligns with typical trial structure. Verify trigger mapping against events.tsv for accurate condition labeling.

### Potential Task 2: Auditory vs. Visual Modality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.5 s, overlap = 0.5, target_events = ["1", "0"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---|
| "1" | modality | Stimulus modality: visual |
| "0" | modality | Stimulus modality: auditory |

- **Evidence**: DOI: 10.1038/s41597-021-00821-1 (dataset includes both visual and auditory object naming tasks; paradigm documentation confirms modality variation)
- **Kernel Notes**: Plausible task from paradigm alone (no direct classification reference). Trigger codes 0/1 may encode modality differences. Requires events.tsv validation for semantic mapping. Long event epoching captures sustained processing for modality discrimination.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
