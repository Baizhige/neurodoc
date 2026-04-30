# Capacity for Movement is an Organisational Principle in Object Representations: EEG Data from Experiment 2

**Dataset**: `openneuro_ds003887` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003887
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 48 | **Manual Review**: Pending
**Channels**: 127 | **Sampling Rate**: 250 Hz

## Paradigm

Participants performed time-pressured categorization of static images based on movement capacity and completed a passive viewing task using Rapid Serial Visual Presentation (RSVP). This second experiment extends Experiment 1 by testing whether movement capacity organization in neural object representations generalizes across different task contexts and classification criteria.

## File Scan Result

> **Kernel SHA256**: `1684c7a58a7a66d24b19e3f6e1ee3ebc0699fd3edc146da0c1943527eb111094`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 38400 | event | raw | Object category 1 |
| `E  2` | 38400 | event | raw | Object category 2 |
| `E  3` | 38400 | event | raw | Object category 3 |
| `E  4` | 960 | event | raw | Block boundary |
| `E  5` | 38400 | event | raw | Object category 5 |
| `E  8` | 115200 | event | raw | Movement-capable objects (animate) |
| `E  9` | 115200 | event | raw | Non-movement-capable objects (inanimate) |
| `Event/E  1` | 38400 | event | raw | Object category 1 |
| `Event/E  2` | 38400 | event | raw | Object category 2 |
| `Event/E  3` | 38400 | event | raw | Object category 3 |
| `Event/E  4` | 960 | event | raw | Block boundary |
| `Event/E  5` | 38400 | event | raw | Object category 5 |
| `Event/E  8` | 115200 | event | raw | Movement-capable objects (animate) |
| `Event/E  9` | 115200 | event | raw | Non-movement-capable objects (inanimate) |
| `boundary` | 24 | event | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Movement Capacity Binary Classification (E8 vs E9)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [E 8, E 9]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `E 8` | 0 | Movement-capable objects (animate) |
| `E 9` | 1 | Non-movement-capable objects (inanimate) |

- **Evidence**: DOI: 10.1016/j.neuroimage.2022.119517 | DOI: 10.31234/osf.io/3x2qh
- **Kernel Notes**: Primary binary classification comparing movement-capable (E8, ~115k trials) vs non-movement-capable (E9, ~115k trials) object representations. E8 and E9 are the dominant event types (~3x more frequent than E1-E5 categories), making this the most statistically robust comparison. Event-related EEG epochs aligned to stimulus onset capture neural dynamics of movement capacity processing in RSVP paradigm.

### Classical Task 2: Full Object Category Multiclass Classification (E1-E5, E8-E9)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [E 1, E 2, E 3, E 5, E 8, E 9]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `E 1` | 0 | Object category 1 |
| `E 2` | 1 | Object category 2 |
| `E 3` | 2 | Object category 3 |
| `E 5` | 3 | Object category 5 |
| `E 8` | 4 | Object category 8 (movement-capable / animate) |
| `E 9` | 5 | Object category 9 (no movement / inanimate) |

- **Evidence**: DOI: 10.1016/j.neuroimage.2022.119517 | DOI: 10.31234/osf.io/3x2qh
- **Kernel Notes**: Six-category classification including all object categories. Note: E1-E5 events (~38k each) have approximately 1/3 the trials of E8-E9 events (~115k each), creating class imbalance. E4 events (block boundaries, ~960 total) are excluded as admin markers. Papers confirm MVPA classification across condition labels capturing object category and movement capacity representations.

### Potential Task 1: Animacy vs Inanimacy Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [E 8, E 9]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `E 8` | 0 | Animate objects |
| `E 9` | 1 | Inanimate objects |

- **Evidence**: DOI: 10.1016/j.neuroimage.2022.119517 (animacy subcategories mentioned)
- **Kernel Notes**: Animacy classification derived from movement capacity labels as super-level meta. Movement capacity and animacy are closely related organizational principles; E8 represents animate/movement-capable objects, E9 represents inanimate/non-moving objects. Type 2 meta integration required to route animacy labels separately from raw movement capacity labels.

### Normal Task 1: Temporal Dynamics of Movement Capacity Representation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [E 8, E 9], baseline = [-0.2, 0.0]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: Same as Classical Task 1
- **Evidence**: DOI: 10.1016/j.neuroimage.2022.119517 | DOI: 10.31234/osf.io/3x2qh
- **Kernel Notes**: Time-resolved MVPA analysis examining when neural classifiers can distinguish movement-capable vs non-movement-capable objects. Standard stimulus-locked epoch window (-0.2s to 1.0s) captures early visual ERP components and later categorization-related activity. Baseline correction applied to remove pre-stimulus drift.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
