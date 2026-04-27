# EEG recordings for 200 object images presented in RSVP sequences at 5Hz or 20Hz

**Dataset**: `openneuro_ds004018` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004018
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 63 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Rapid Serial Visual Presentation (RSVP) of 200 object images at two presentation frequencies (5 Hz and 20 Hz) to investigate the temporal dynamics of visual object representations. Images were categorized as "stars" or "boats" (two superordinate categories), allowing investigation of how presentation rate affects category-level neural decoding. This is a very small dataset (2 subjects).

## File Scan Result

> **Kernel SHA256**: `bc3ce5ec9f3b496c0d56da90177a7013c47f26490de533945a7641c986a4e033`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: RSVP Object Category Classification (stars vs boats)

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|  
  | `stars` | 0 | Star/celestial category RSVP image onset |
  | `boats` | 1 | Boat/vehicle category RSVP image onset |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — 16 participants, 200 visual objects, RSVP at 5Hz (200ms ISI) and 20Hz (50ms ISI), LDA classifiers for category decoding, boats vs stars as primary target stimuli with 8 exemplars each. Window from -100ms baseline to 1000ms captures N1/P1/N2 components for visual object category processing.
- **Kernel Notes**: Kernel scan shows empty event counts; actual `stars`/`boats` labels need extraction from BIDS events.tsv directly. Verify that `stars` and `boats` event codes are properly parsed from raw BIDS structure. Presentation frequency (5Hz vs 20Hz) should be encoded as a covariate per-epoch since it affects temporal dynamics of category decoding. Very small dataset (2 subjects) limits statistical power; use within-subject cross-validation.

### Classical Task 2: RSVP Target vs Distractor Binary Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 2.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|  
  | `target` | 1 | Target stimulus in RSVP stream |
  | `distractor` | 0 | Non-target distractor stimulus |
- **Super Meta Notes**: Labels derived from original study stimulus metadata (stimlist.csv or equivalent). Kernel step: Load target vs distractor annotations from original stimulus files and merge with epoch timestamps based on presentation order. The `rt` field (raw level) may provide additional response-time context for target detection analysis.
- **Evidence**:
  - DOI: 10.1016.j.neuroimage.2018.12.046 — Extended 2.1s epoch window (tmin=-0.1s to tmax=2.0s) for target detection analysis capturing N2/N4 components; LDA binary classification of target vs distractor events.
- **Kernel Notes**: Extract `stars` and `boats` epochs as base events, then map to target/distractor labels via stimulus metadata. Extended window captures later semantic processing stages beyond early visual components. Encode presentation_frequency (5Hz vs 20Hz) as metadata covariate. No misc channels detected in kernel scan; verify RT field availability in BIDS sidecar.

### Potential Task 1: Super-meta RSVP Category Decoding

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|  
  | `animate` | 0 | Animate/living category superordinate label |
  | `inanimate` | 1 | Inanimate/non-living category superordinate label |
- **Super Meta Notes**: Derive animacy labels (animate vs inanimate) from original stimulus metadata for all 200 images. `stars` are celestial/inanimate objects; `boats` are vehicles/inanimate objects. For more varied super-meta, include object identity labels (specific object identities within categories) if stimulus metadata provides this level of detail.
- **Kernel Notes**: Load original stimulus metadata (200 images) and map each epoch to its animacy and category labels. Version super-meta labels in kernel output. Consider multi-level classification (animacy → category → identity) as hierarchical super-meta approach. Very small dataset (2 subjects) limits generalization; use within-subject cross-validation. No device information available; device field missing in BIDS metadata.