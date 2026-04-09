# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2004/2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz
**Manual Review**: Mr.PJ

## Paradigm

A continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. Five empty squares were shown continuously, one location was attended, and participants pressed a mouse button when a white disk appeared at the attended location. Event codes encode both the attended position and the cued (stimulus) position. The dataset contains only 2 completed files and is a very small subset.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds002578.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `3d205e5aec2abde5988df89f857ab51dbe4e9f4ad3d900313aabe95ff9ff3b25`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.
> **Manual Review Note**: Event meanings updated by human reviewer (Mr.PJ) based on events.json. Kernel should verify and re-derive `Meaning` column from events.json definitions on next scan.


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Picture` | 5939 | event | raw | Generic picture/stimulus presentation marker without condition identity |
| `Response` | 1202 | event | raw | Participant response (mouse button press) marker |
| `33` | 240 | event | raw | Target oddball: attend position 3, cue position 3 |
| `44` | 239 | event | raw | Target oddball: attend position 4, cue position 4 |
| `31` | 240 | event | raw | Non-target distractor: attend position 3, cue position 1 |
| `34` | 239 | event | raw | Non-target distractor: attend position 3, cue position 4 |
| `35` | 240 | event | raw | Non-target distractor: attend position 3, cue position 5 |
| `41` | 238 | event | raw | Non-target distractor: attend position 4, cue position 1 |
| `42` | 239 | event | raw | Non-target distractor: attend position 4, cue position 2 |
| `43` | 240 | event | raw | Non-target distractor: attend position 4, cue position 3 |
| `45` | 239 | event | raw | Non-target distractor: attend position 4, cue position 5 |
| `203` | 1 | admin | raw | Rare code not described in events.json; inspect manually if used |
| `217` | 2 | admin | raw | Rare code not described in events.json; inspect manually if used |
| `237` | 1 | admin | raw | Rare code not described in events.json; inspect manually if used |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
| **Record Count** | 2 | |
| **Age Completeness** | 2/2 (100.0%) | |
| **Sex Completeness** | 2/2 (100.0%) | |
| **Observed Age Examples** | `30` | |
| **Observed Sex Examples** | `Female`, `Male` | |

## Tasks

### Classical Task 1: Visual Oddball Target Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`33`, `44`, `31`, `34`, `35`, `41`, `42`, `43`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `33` | 1 | Target oddball (attend pos 3, cue pos 3) |
  | `44` | 1 | Target oddball (attend pos 4, cue pos 4) |
  | `31` | 0 | Non-target distractor |
  | `34` | 0 | Non-target distractor |
  | `35` | 0 | Non-target distractor |
  | `41` | 0 | Non-target distractor |
  | `42` | 0 | Non-target distractor |
  | `43` | 0 | Non-target distractor |
  | `45` | 0 | Non-target distractor |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477-07.2007 — This 2007 J Neurosci paper analyzes visual oddball EEG data, correlating medial prefrontal theta power with target detection and reaction time, validating the target/non-target event structure used here.
- **Kernel Notes**: Target events 33 and 44 are confirmed target oddballs per events.json. Non-target codes 31,34,35,41,42,43,45 encode attend-position/cue-position combinations.

### Classical Task 2: Target Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`33`, `44`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `33` | continuous | Reaction time derived by pairing target event with subsequent Response marker |
  | `44` | continuous | Reaction time derived by pairing target event with subsequent Response marker |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477-07.2007 — Correlates single-trial low-theta power with continuous reaction time, supporting RT regression on target epochs.
- **Kernel Notes**: Pair target events (33, 44) with subsequent Response marker to derive RT. Verify Response marker timing is within plausible RT window (0.1–1.5 s).


## Data Quality Notes

- Only 2 completed EEG files - extremely limited dataset size.
- No event markers detected despite visual oddball paradigm description.
- High-density 256-channel array; verify electrode positions from channel info files.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update