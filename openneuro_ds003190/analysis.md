# Assessment of the visual stimuli properties in P300 paradigm

**Dataset**: `openneuro_ds003190` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003190
**Category**: Sensory/Response | **Subjects**: 19 | **Files (Completed)**: 384
**Channels**: 9 | **Sampling Rate**: 256 Hz

## Paradigm

A P300 ERP experiment evaluating the effects of stimulus count and visual presentation styles (standard flash vs. cartoon face) on EEG brain activity. The experiment used a P300-based BCI paradigm with target and non-target stimulus flashes. Codes 1-9 represent different stimulus conditions or counts; codes 100-203 range encode specific stimulus configurations. The dataset has 19 subjects with many runs (384 files total).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003190

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 382 (files) | short | raw | P300 stimulus condition 1 (non-target flashx) |
| `2` | 382 (files) | short | raw | P300 stimulus condition 2 (non-target flashx) |
| `3` | 382 (files) | short | raw | P300 stimulus condition 3 |
| `4` | 382 (files) | short | raw | P300 stimulus condition 4 |
| `200` | 382 (files) | short | raw | P300 stimulus configuration 200 |
| `201` | 382 (files) | short | raw | P300 stimulus configuration 201 |
| `202` | 382 (files) | short | raw | P300 stimulus configuration 202 |
| `203` | 382 (files) | short | raw | P300 stimulus configuration 203 |
| `101` | 363 (files) | short | raw | P300 target flash condition 101 |
| `102` | 354 (files) | short | raw | P300 target flash condition 102 |
| `103` | 368 (files) | short | raw | P300 target flash condition 103 |
| `104` | 370 (files) | short | raw | P300 target flash condition 104 |
| `5` | 326 (files) | short | raw | P300 stimulus condition 5 |
| `105` | 305 (files) | short | raw | P300 target flash condition 105 |
| `6` | 224 (files) | short | raw | P300 stimulus condition 6 |
| `106` | 212 (files) | short | raw | P300 target flash condition 106 |
| `7` | 169 (files) | short | raw | P300 stimulus condition 7 |
| `107` | 161 (files) | short | raw | P300 target flash condition 107 |
| `8` | 112 (files) | short | raw | P300 stimulus condition 8 |
| `108` | 110 (files) | short | raw | P300 target flash condition 108 |
| `9` | 56 (files) | short | raw | P300 stimulus condition 9 |
| `109` | 47 (files) | short | raw | P300 target flash condition 109 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds003190 DOI: https://doi.org/10.18112/openneuro.ds003190.v1.0.1


### Normal Task 1: P300 Target vs Non-Target Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Specific kernel decodes numeric codes into semantic labels (target_flash, nontarget_flash). 9-channel EEG is very sparse; focus on occipital and parietal channels for P300. Regression target `response_time` available.

| Event | y | Meaning |
 |-------|---|------|
 | `target_flash` | 0 | Target stimulus flash (P300 target) |
 | `nontarget_flash` | 1 | Non-target stimulus flash |
## Data Quality Notes

- Very sparse 9-channel EEG; limited spatial coverage.
- 384 files across 19 subjects = ~20 runs/subject; verify session structure.
- Numeric trigger codes require specific kernel to decode semantic P300 target/non-target labels.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Assessment of the visual stimuli properties in P300 paradigm`
