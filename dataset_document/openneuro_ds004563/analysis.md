# Vicarious touch: overlapping neural patterns between seeing and feeling touch

**Dataset**: `openneuro_ds004563` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004563
**Category**: Sensory/Response | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants either saw someone else being touched (vicarious touch, event_4) or felt touch themselves (direct touch, event_1). EEG was recorded to investigate overlapping neural patterns between observed and experienced tactile stimulation. The study tests whether vicarious touch engages somatosensory cortex similarly to directly felt touch.

## File Scan Result

> **Kernel SHA256**: `0f62f39e754af5773c385b0213395765a12cb12a9fb91320468953b18b2f1207`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `direct_touch` | 66893 | event | raw | Derived continuous label for direct touch |
| `event_1` | 18370 | event | raw | Direct touch (tactile stimulation felt) |
| `event_2` | 18478 | event | raw | Unexplained event type (requires verification) |
| `event_4` | 73714 | event | raw | Vicarious touch (visual observation of touch) |
| `event_65536` | 3 | event | raw | Boundary marker (system/admin) |
| `event_8` | 36862 | event | raw | Unexplained event type (requires verification) |
| `unknown` | 66961 | event | raw | Unlabeled/mislabeled events |
> **Event Type Description**:
> - `event`: short stimulus onset marker or derived label, for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | Not available in dataset metadata |
| `subject_sex` | complete | Not available in dataset metadata |
| `device` | missing | Not available in dataset metadata |

## Tasks

### Classical Task 1: Vicarious Touch Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 0.8, target_events = [event_1, event_4]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `event_1` | 0 | Direct touch (tactile stimulation felt) |
| `event_4` | 1 | Vicarious touch (visual observation of touch) |

- **Evidence**: DOI: 10.1101/2022.06.21.497107 (bioRxiv, relevant, classification=supported); DOI: 10.1016/j.neuroimage.2023.120269 (NeuroImage, relevant, classification=supported)
- **Kernel Notes**: Binary classification between direct and vicarious touch conditions. Both events are short stimulus onset markers requiring onset alignment. Window captures early somatosensory components (N80, P60) and later mu-rhythm suppression. Address class imbalance (~4:1 vicarious:direct) during analysis. Route final labels to Annotation channel with dataset-specific schema. Exclude event_65536 (3 boundary markers) from epoching.

---

### Normal Task 1: Raw-Meta Exploration

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, target_events = [event_2, event_8, unknown]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `event_2` | Needs verification | Unexplained event type |
| `event_8` | Needs verification | Unexplained event type |
| `unknown` | Needs verification | Unlabeled/mislabeled events |

- **Evidence**: Partial reference - epoch alignment recommendations only; event counts total 122,401 requiring investigation
- **Kernel Notes**: Longer window (1.0s) allows detection of sustained vicarious responses. Exclude event_65536 (3 boundary markers) from epoching. Verify unknown events mapping before finalizing target labels. Exclude admin markers from target labels.

---

### Potential Task 1: Super-Meta Derivation

- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = null, tmax = null, segment_length = 2.0, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `direct_touch` (derived) | Continuous target | Continuous measure linked to direct touch labels |

- **Evidence**: epoch alignment recommendations - 66,893 direct_touch derived labels suggest continuous/super-meta targets
- **Kernel Notes**: Segmentation with 50% overlap and 2s windows provides continuous coverage for regression targets. Route to misc channel with version tags for reproducibility. Derive and version super-meta in kernel with source schema. Document derivation logic, units, and version tags.

---

### Normal Task 2: Touch Location Decoding (within-condition)

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 0.8, target_events = [event_1, event_4]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `event_1` | 0 or 1 | Within-condition: little finger vs thumb touch location |
| `event_4` | 0 or 1 | Within-condition: little finger vs thumb observed touch |

- **Evidence**: DOI: 10.1101/2022.06.21.497107; DOI: 10.1016/j.neuroimage.2023.120269 (both mention within-trial decoding of touch location: little finger vs thumb)
- **Kernel Notes**: Requires sub-condition labels for touch location. May require additional annotation or event refinement. Verify location encoding from dataset documentation before implementation.