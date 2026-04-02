# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 2 | **Channels**: 256.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

A visual oddball task designed to study selective attention using event-related potentials with high-density 256-channel electrode coverage. Despite the task description implying trial-level stimuli (standard vs. oddball), no event markers were detected in the BIDS EEG files. The dataset contains only 2 completed files and is a very small subset.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002578

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Visual Oddball Target Response Classification (Fast vs Slow)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`target_visual_stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `fast_response` | 1 | Reaction time below median (faster motor response) |
  | `slow_response` | 0 | Reaction time above median (slower motor response) |
- **Super Meta Notes**: Labels derived from raw event markers — target visual stimulus onset events and button press response events. Reaction time is computed from stimulus onset to button press; median split defines fast vs slow classes.
- **Evidence**:
  - DOI: `10.1523/jneurosci.3477.07.2007` — This 2007 J Neurosci paper analyzes visual oddball EEG data to show that larger medial prefrontal theta (4.5 Hz) complexes precede faster motor responses (button presses), using ICA to decompose 31-channel (and 253-channel) target response epochs and correlate single-trial low-theta power with reaction time quantiles.
- **Kernel Notes**: Extract target_visual_stimulus events and associated button_press_response events. Compute reaction time (RT) for each trial. Apply median split to create binary labels (fast=1, slow=0). Epoch window is 3s total: 1s before target onset to 2s after. Dataset uses 256 Hz sampling.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: Only 2 completed files available - very small dataset. High-density 256-channel EEG provides spatial richness. Check events.tsv directly for potential trial markers not captured in locator pipeline.

## Data Quality Notes

- Only 2 completed EEG files - extremely limited dataset size.
- No event markers detected despite visual oddball paradigm description.
- High-density 256-channel array; verify electrode positions from channel info files.

## References

- **Reference**: `Visual Oddball Task (256 channels)`
