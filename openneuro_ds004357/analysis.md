# Features-EEG

**Dataset**: `openneuro_ds004357` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004357
**Category**: Sensory/Response | **Subjects**: 16 | **Files (Completed)**: 16 | **Channels**: 127 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of Gabor-like stimuli at 6.67 Hz and 20 Hz while performing an orthogonal fixation color change detection task. Three event types encode different stimulus feature or condition categories, enabling investigation of how visual features (orientation, contrast, spatial frequency, color) are dynamically encoded in EEG responses.

## File Scan Result

> **Kernel SHA256**: `no_kernel`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E  1` | 322780 | event | raw | Stimulus feature condition 1 (orientation/contrast/SF/color level 1) |
| `Event/E  2` | 322781 | event | raw | Stimulus feature condition 2 (orientation/contrast/SF/color level 2) |
| `Event/E  3` | 1260 | event | raw | Stimulus feature condition 3 (orientation/contrast/SF/color level 3) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Feature Decoding from RSVP Stimuli
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Stimulus feature condition 1 (orientation/contrast/SF/color level 1) |
  | `Event/E 2` | 1 | Stimulus feature condition 2 (orientation/contrast/SF/color level 2) |
  | `Event/E 3` | 2 | Stimulus feature condition 3 (orientation/contrast/SF/color level 3) |
- **Super Meta Notes**: Labels derived from experimental condition log mapping to 4 visual feature dimensions (orientation, contrast, spatial frequency, color). Separate binary/multiclass decoders for each feature. Epochs aligned to stimulus onset markers.
- **Evidence**:
  - DOI: 10.1038/s41598.025.27703-5 — MVPA decoding of visual grating stimuli using epochs from -0.1s to 0.6s post-stimulus on ds004357 (N=16, 128-channel EEG)
  - DOI: 10.1371/journal.pcbi.1011760 — Visual feature decoding (4 visual features × multiple levels) from RSVP EEG epochs on same dataset
- **Kernel Notes**: Severe class imbalance (E1/E2 ~161k trials vs E3 ~1260 total). Apply class weighting or stratified sampling. At 20 Hz RSVP (50ms ISI), 0.6s window captures ~12 stimuli; account for overlap. 127-channel high-density EEG suitable for MVPA.

### Potential Task 1: Extended Window Visual Feature Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Stimulus feature condition 1 |
  | `Event/E 2` | 1 | Stimulus feature condition 2 |
  | `Event/E 3` | 2 | Stimulus feature condition 3 |
- **Super Meta Notes**: Extended window captures both early sensory (P1/N1) and late cognitive components (P300, sustained processing) relevant to feature integration across RSVP stream. Accommodates slower frequency condition (6.67 Hz ≈ 150ms ISI).
- **Evidence**:
  - DOI: 10.1038/s41598.025.27703-5 — Extended analysis windows may reveal late sustained visual feature representations
- **Kernel Notes**: Extended window enables examination of sustained visual processing. Same class imbalance handling required. Computational cost higher with 1.2s window vs 0.7s window.

### Potential Task 2: Per-Feature Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Feature level group A |
  | `Event/E 2` | 1 | Feature level group B |
  | `Event/E 3` | 2 | Feature level group C |
- **Super Meta Notes**: Binary decoders trained per visual feature dimension (orientation, contrast, spatial frequency, color) rather than multiclass. Reduces class imbalance issues when grouping conditions.
- **Kernel Notes**: Consider one-vs-rest or per-feature binary classifiers. Group E1/E2/E3 into feature-specific condition pairs. Validate label mapping from experimental design documentation.

### Potential Task 3: Temporal Dynamics of Feature Decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Stimulus feature condition 1 |
  | `Event/E 2` | 1 | Stimulus feature condition 2 |
  | `Event/E 3` | 2 | Stimulus feature condition 3 |
- **Super Meta Notes**: Time-resolved MVPA to track temporal evolution of visual feature coding across RSVP presentation. Investigate whether features are decoded at different latencies.
- **Kernel Notes**: Apply sliding window or time-generalization MVPA. Use shorter time bins (e.g., 100ms) to capture temporal dynamics. Requires careful cross-validation to avoid temporal leakage.
