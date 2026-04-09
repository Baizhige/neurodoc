# Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot)

**Dataset**: `openneuro_ds004802` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004802
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 79
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

A pilot EEG study investigating the neural underpinnings of loneliness by contrasting social hypersensitivity (amplified neural responses to social stimuli) and hyperalertness (heightened attention to potential social threats). Participants viewed social and non-social stimuli while EEG was recorded. Trigger codes encode stimulus type, valence, and response conditions. Code 20 dominates the event structure (49,726 total) and may represent a high-frequency refresh or fixation signal.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004802.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `91ebf6584f11451e6aace0e08d5a223a4ffd7cd0a64242e90fcfad7fa65898b6`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `20` | 49726 | event | raw | Unresolved from current kernel facts |
| `111` | 4144 | event | raw | Unresolved from current kernel facts |
| `25` | 2823 | event | raw | Unresolved from current kernel facts |
| `24` | 2817 | event | raw | Unresolved from current kernel facts |
| `21` | 2747 | event | raw | Unresolved from current kernel facts |
| `23` | 2667 | event | raw | Unresolved from current kernel facts |
| `22` | 2666 | event | raw | Unresolved from current kernel facts |
| `42` | 2319 | event | raw | Unresolved from current kernel facts |
| `44` | 2316 | event | raw | Unresolved from current kernel facts |
| `43` | 2246 | event | raw | Unresolved from current kernel facts |
| `61` | 2221 | event | raw | Unresolved from current kernel facts |
| `62` | 2185 | event | raw | Unresolved from current kernel facts |
| `65` | 2182 | event | raw | Unresolved from current kernel facts |
| `45` | 2174 | event | raw | Unresolved from current kernel facts |
| `41` | 2165 | event | raw | Unresolved from current kernel facts |
| `63` | 2070 | event | raw | Unresolved from current kernel facts |
| `64` | 2066 | event | raw | Unresolved from current kernel facts |
| `26` | 1993 | event | raw | Unresolved from current kernel facts |
| `46` | 1643 | event | raw | Unresolved from current kernel facts |
| `66` | 1584 | event | raw | Unresolved from current kernel facts |
| `47` | 969 | event | raw | Unresolved from current kernel facts |
| `27` | 933 | event | raw | Unresolved from current kernel facts |
| `67` | 715 | event | raw | Unresolved from current kernel facts |
| `68` | 299 | event | raw | Unresolved from current kernel facts |
| `16` | 264 | event | raw | Unresolved from current kernel facts |
| `13` | 261 | event | raw | Unresolved from current kernel facts |
| `200` | 259 | event | raw | Unresolved from current kernel facts |
| `48` | 259 | event | raw | Unresolved from current kernel facts |
| `31` | 224 | event | raw | Unresolved from current kernel facts |
| `35` | 222 | event | raw | Unresolved from current kernel facts |
| `53` | 190 | event | raw | Unresolved from current kernel facts |
| `54` | 189 | event | raw | Unresolved from current kernel facts |
| `12` | 188 | event | raw | Unresolved from current kernel facts |
| `14` | 151 | event | raw | Unresolved from current kernel facts |
| `11` | 150 | event | raw | Unresolved from current kernel facts |
| `28` | 150 | event | raw | Unresolved from current kernel facts |
| `33` | 150 | event | raw | Unresolved from current kernel facts |
| `56` | 114 | event | raw | Unresolved from current kernel facts |
| `15` | 112 | event | raw | Unresolved from current kernel facts |
| `36` | 111 | event | raw | Unresolved from current kernel facts |
| `17` | 76 | event | raw | Unresolved from current kernel facts |
| `34` | 76 | event | raw | Unresolved from current kernel facts |
| `55` | 76 | event | raw | Unresolved from current kernel facts |
| `52` | 75 | event | raw | Unresolved from current kernel facts |
| `57` | 75 | event | raw | Unresolved from current kernel facts |
| `32` | 74 | event | raw | Unresolved from current kernel facts |
| `51` | 38 | event | raw | Unresolved from current kernel facts |
| `254` | 7 | event | raw | Unresolved from current kernel facts |
| `100` | 5 | event | raw | Unresolved from current kernel facts |
| `101` | 5 | event | raw | Unresolved from current kernel facts |
| `65536` | 1 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [Needs verification - see Kernel Notes]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | (unconfirmed) | 0 | Target stimulus * |
  | (unconfirmed) | 1 | Non-target stimulus * |
- **Kernel Notes**: Verify event ID mapping from events.tsv. This dataset uses codes for stimulus type, valence, and response conditions; confirm which codes correspond to target vs non-target for P300/oddball paradigm. Code 20 (n=49,726) appears to be fixation/refresh, not stimulus-related.
- **Evidence**: DOI: 10.18112/openneuro.ds004802.v1.0.0 — "Loneliness in the Brain" pilot EEG study; paradigm involves social vs non-social stimuli, but exact target/non-target split not explicitly described in metadata.

### Potential Task 1: Stimulus classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30+ distinct trigger codes; full decode from events.tsv required. Code 20 dominates (49,726 total) - likely a fixation/refresh signal rather than stimulus.

| Event | y | Meaning |
|-------|---|------|
| `20` | 0 | Primary stimulus trigger |
| `111` | 1 | Trigger code 111 |
| `25` | 2 | Trigger code 25 |
| `24` | 3 | Trigger code 24 |
| `21` | 4 | Trigger code 21 |
| `23` | 5 | Trigger code 23 |
| `22` | 6 | Trigger code 22 |
| `42` | 7 | Trigger code 42 |
| `44` | 8 | Trigger code 44 |
| `43` | 9 | Trigger code 43 |
| `61` | 10 | Trigger code 61 |
| `62` | 11 | Trigger code 62 |
| `65` | 12 | Trigger code 65 |

## Data Quality Notes

- 30+ distinct trigger codes - check events.tsv decode table.
- Code 20 (49,726 total) is anomalously high - may be a fixation/refresh signal rather than stimulus.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update