# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz

## Paradigm

A visual oddball task designed to study selective attention using event-related potentials with high-density 256-channel electrode coverage. Despite the task description implying trial-level stimuli (standard vs. oddball), no event markers were detected in the BIDS EEG files. The dataset contains only 2 completed files and is a very small subset.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 2
- **Age Completeness**: 2/2 (100.0%)
- **Sex Completeness**: 2/2 (100.0%)
- **Observed Age Examples**: `30`
- **Observed Sex Examples**: `Female`, `Male`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds002578.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `3d205e5aec2abde5988df89f857ab51dbe4e9f4ad3d900313aabe95ff9ff3b25`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Picture` | 5939 | event | raw | Unresolved from current kernel facts |
| `Response` | 1202 | event | raw | Unresolved from current kernel facts |
| `31` | 240 | event | raw | Unresolved from current kernel facts |
| `33` | 240 | event | raw | Unresolved from current kernel facts |
| `35` | 240 | event | raw | Unresolved from current kernel facts |
| `43` | 240 | event | raw | Unresolved from current kernel facts |
| `34` | 239 | event | raw | Unresolved from current kernel facts |
| `42` | 239 | event | raw | Unresolved from current kernel facts |
| `44` | 239 | event | raw | Unresolved from current kernel facts |
| `45` | 239 | event | raw | Unresolved from current kernel facts |
| `41` | 238 | event | raw | Unresolved from current kernel facts |
| `217` | 2 | event | raw | Unresolved from current kernel facts |
| `203` | 1 | event | raw | Unresolved from current kernel facts |
| `237` | 1 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Visual Oddball Target Detection with Reaction Time Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`target_visual_stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `target_visual_stimulus` | 1 | Fast response (RT below median) |
  | `target_visual_stimulus` | 0 | Slow response (RT above median) |
- **Super Meta Notes**: Labels derived from raw target stimulus events combined with button press response times. Kernel step: Extract target stimulus onset events, compute RT from stimulus to button_press_response, binarize using median RT threshold (fast=1, slow=0).
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477.07.2007 — This 2007 J Neurosci paper analyzes visual oddball EEG data to show that larger medial prefrontal theta (4.5 Hz) complexes precede faster motor responses (button presses), using ICA to decompose 31-channel (and 253-channel) target response epochs and correlate single-trial low-theta power with reaction time quantiles.
- **Kernel Notes**: Verify event ID mapping from events.tsv. If `target_visual_stimulus` is not present, check for standard oddball event labels (e.g., 'target', 'oddball'). Button press events required for RT calculation; verify presence in raw data. Parameter tmax=2s allows capture of P300 response post-stimulus. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Continuous Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`target_visual_stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `target_visual_stimulus` | continuous | Reaction time in milliseconds |
- **Super Meta Notes**: Derived from raw events [`target_visual_stimulus`, `button_press_response`] by computing time difference between target stimulus onset and button press. Kernel step: For each target stimulus epoch, find subsequent button press event, calculate RT = button_press_time - stimulus_onset_time.
- **Evidence**:
  - DOI: 10.1523/jneurosci.3477.07.2007 — This 2007 J Neurosci paper analyzes visual oddball EEG data to show that larger medial prefrontal theta (4.5 Hz) complexes precede faster motor responses (button presses), correlating single-trial low-theta power with continuous reaction time values.
- **Kernel Notes**: Requires both target stimulus and button press events. Verify event IDs from events.tsv. Output continuous RT values in milliseconds (or seconds). If button press events unavailable, fall back to classification task above.

### Potential Task 1: Resting / Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null - no trial-level labels available)
- **Notes**: Only 2 completed files available - very small dataset. High-density 256-channel EEG provides spatial richness. Check events.tsv directly for potential trial markers not captured in locator pipeline.

## Data Quality Notes

- Only 2 completed EEG files - extremely limited dataset size.
- No event markers detected despite visual oddball paradigm description.
- High-density 256-channel array; verify electrode positions from channel info files.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update