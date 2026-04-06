# Auditory and Visual Rhythm Omission EEG

**Dataset**: `openneuro_ds002218` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002218
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 18
**Channels**: 32 | **Sampling Rate**: 256 Hz

## Paradigm

Participants passively perceived rhythmic auditory tone sequences and visual flashing stimuli that occasionally omitted an expected beat, to study predictive neural activity (mismatch responses) versus sensory evoked responses. The paradigm investigates how the brain generates predictions based on temporal regularities and detects violations of expected rhythmic patterns. Only BioSemi STATUS admin markers are detectable in the locator metadata; no decoded trial events are available from the locator pipeline.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 18
- **Age Completeness**: 0/18 (0.0%)
- **Sex Completeness**: 0/18 (0.0%)
- **Observed Age Examples**: N/A
- **Observed Sex Examples**: N/A
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds002218.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `d54b70d1ef6dde18c0f2ee358ed5003ce0320b944a1e4438a1173e7a0f9890a6`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 33483 | event | raw | Unresolved from current kernel facts |
| `3` | 33480 | event | raw | Unresolved from current kernel facts |
| `2` | 2520 | event | raw | Unresolved from current kernel facts |
| `4` | 2520 | event | raw | Unresolved from current kernel facts |
| `5` | 2520 | event | raw | Unresolved from current kernel facts |
| `6` | 2520 | event | raw | Unresolved from current kernel facts |
| `0, Impedance` | 16 | event | raw | Impedance |
| `__` | 2 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Auditory/Visual Rhythm Omission Classification (Beta Band Entrainment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.67 s, tmax = +1.67 s, target_events = [`tone_non-omission`, `tone_omission`, `flash_non-omission`, `flash_omission`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `tone_non-omission` | 0 | Auditory rhythm non-omission trial (regular tone) |
  | `tone_omission` | 1 | Auditory rhythm omission trial (expected tone missing) |
  | `flash_non-omission` | 2 | Visual rhythm non-omission trial (regular flash) |
  | `flash_omission` | 3 | Visual rhythm omission trial (expected flash missing) |
- **Evidence**:
  - DOI: 10.1111/ejn.15314 — EEG analysis of induced and evoked beta band activity (14-30 Hz) during an auditory/visual rhythm omission paradigm, epoching from -1.67s to +1.67s around each tone or flash onset
  - DOI: 10.1101/2020.11.29.402701 — Same dataset analysis investigating induced and evoked beta band activity with four-class omission paradigm
- **Kernel Notes**: Verify event ID mapping from events.tsv. The raw events list shows only `STATUS` admin markers; actual stimulus events may need extraction from events.tsv files. Each stimulus train had 100 events with 7 randomly placed omissions. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null(only STATUS admin events; no trial markers decoded))
- **Notes**: STATUS is a BioSemi CM_in_range hardware marker. If events.tsv contains decoded rhythm onset/omission events (separate from the locator metadata), they could be used for ERP analysis - verify directly from raw events.tsv.

## Data Quality Notes

- Only `STATUS` events found in locator metadata - BioSemi admin markers only.
- The actual auditory/visual rhythm and omission events may be encoded in the `events.tsv` files but were not decoded by the locator pipeline; check events.tsv directly.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update