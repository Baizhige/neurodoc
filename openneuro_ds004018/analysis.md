# EEG recordings for 200 object images presented in RSVP sequences at 5Hz or 20Hz

**Dataset**: `openneuro_ds004018` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004018
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

Rapid Serial Visual Presentation (RSVP) of 200 object images at two presentation frequencies (5 Hz and 20 Hz) to investigate the temporal dynamics of visual object representations. Images were categorized as "stars" or "boats" (two superordinate categories), allowing investigation of how presentation rate affects category-level neural decoding. This is a very small dataset (2 subjects).

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 2
- **Age Completeness**: 2/2 (100.0%)
- **Sex Completeness**: 2/2 (100.0%)
- **Observed Age Examples**: `32.0`
- **Observed Sex Examples**: `Male`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004018.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `a46cd3d36abba2d55cf6bf4c9ff0c8161d9980f73ac77903f5772b73e914675c`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E  1` | 16216 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### MISC Label Summary

<!-- AUTO-KERNEL-MISC:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Label / Source / Meta Level` are kernel-derived facts.

| Label / Field | Source | Meta Level | Meaning |
|---------------|--------|------------|---------|
| `rt` | events.tsv:rt (2/2 files) | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-MISC:END -->

- **Route**: `misc`
- **Role**: Kernel-derived label summary for the current route only.


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
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`stars`, `boats`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stars` | 0 | Star/celestial category RSVP image onset |
  | `boats` | 1 | Boat/vehicle category RSVP image onset |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — Original RSVP study with 200 object images at 5Hz and 20Hz, multi-class category decoding using LDA classifiers on epochs from -100 to 1000ms
- **Kernel Notes**: Extract epochs aligned to `stars` and `boats` onset markers. The paper demonstrates animacy (animate vs inanimate) and superordinate category decoding (e.g., mammals, tools, vehicles). The raw events `stars` and `boats` correspond to celestial vs vehicle superordinate categories. Verify that presentation frequency (5Hz vs 20Hz) is encoded in a separate metadata field or derive from inter-stimulus intervals. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: RSVP Target vs Distractor Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 2.0 s *, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | target | 1 | Target stimulus in RSVP stream |
  | distractor | 0 | Non-target distractor stimulus |
- **Super Meta Notes**: Derived from raw event(s) [`stars`, `boats`] by analyzing trial-level target/distractor annotations in original study metadata. Kernel step: Load target vs distractor labels from original stimulus file (e.g., stimlist.csv) and merge with epoch timestamps based on presentation order.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — Reports target vs distractor binary classification using LDA, with extended epoch window tmin=-0.1s to tmax=2.0s to capture N2/N4 components

### Potential Task 1: Super-meta task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Target Definition**: Continuous or categorical superordinate labels (animacy, category, object identity) derived from original stimulus metadata

- **Kernel Notes**: Derive and version super-meta in kernel. Load original stimulus metadata (200 images) and map each epoch to its animacy label (animate/inanimate), category (10-way), or object identity (50-way). (replaces Potential Task 2 from original analysis.md)

## Data Quality Notes

- Only 2 subjects - extremely limited statistical power for group-level analysis
- RSVP at 5 Hz and 20 Hz: at 20 Hz, images appear for only 50 ms (near threshold for conscious processing)
- Verify that `stars` and `boats` events correspond to onset markers and not sustained states

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update