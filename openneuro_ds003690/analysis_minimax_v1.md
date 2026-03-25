# EEG, ECG and Pupil Data from Young and Older Adults: Rest and Auditory Cued Reaction Time Tasks

**Dataset**: `openneuro_ds003690` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003690
**Category**: Sensory/Response | **Subjects**: 75 | **Files (Completed)**: 375
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Young and older adults performed auditory-cued simple reaction time and go/no-go tasks to investigate age-related differences in neural and physiological activity. An auditory cue preceded each trial; participants pressed a button to go stimuli and withheld responses to no-go stimuli. Error feedback tones were provided after commission errors. Resting-state EEG was also recorded. The study examines how aging affects preparatory neural activity, inhibitory control, and pupil dilation responses.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: reaction time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003690

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `cue` | 375 | short | raw | Auditory warning cue preceding stimulus |
| `go` | 300 | short | raw | Go stimulus (respond with button press) |
| `no-go` | 150 | short | raw | No-go stimulus (withhold response) |
| `button press` | 300 | short | raw | Participant button-press response |
| `error of commission` | 64 | short | raw | Commission error (response to no-go) |
| `error feedback tone` | 179 | short | raw | Auditory error feedback tone |
| `task start` | 320 | short | raw | Task block start marker |
| `task end` | 375 | short | raw | Task block end marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Go/No-go Response Inhibition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 6.0 s, target_events = [`go`, `no-go`, `cue-only`]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `go` | 1 | Go stimulus (button press required) |
  | `no-go` | 0 | No-go stimulus (withhold response) |
  | `cue-only` | -1 | Cue only with no target presented |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — This paper analyzes EEG/ECG/pupil data from 36 young and 39 older adults performing cued simple RT and go/no-go auditory tasks, using cue-locked EEG epochs from -0.2s to 6s for ERP analysis.

### Primary Task 2: Simple Reaction Time Detection
- **Task Type**: classification (fast vs slow response) | regression (reaction time prediction)
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 4.5 s, target_events = [`go`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `go` (fast) | 0 | Fast reaction time (below median RT) |
  | `go` (slow) | 1 | Slow reaction time (above median RT) |
- **Super Meta Notes**: Labels derived from button press event timing relative to go stimulus onset. Median split or quartile classification applied to reaction times. Alternatively, continuous RT values stored in `misc` channel for regression.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — This paper analyzes simple reaction time detection task using beta oscillation epochs from -1s to 4.5s, examining the relationship between cortical activity and reaction time.

### Primary Task 3: Beta Oscillation Analysis during Motor Preparation
- **Task Type**: regression (beta power prediction)
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 4.5 s, target_events = [`go`, `no-go`], baseline = (-0.45, -0.02) s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**: Continuous beta band power (13-30 Hz) derived via FFT on epochs
- **Super Meta Notes**: Kernel should compute beta power in specified baseline and post-stimulus windows, then predict reaction time or classification label.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — This paper examines beta oscillations from -1s to 4.5s with baseline correction (-450ms to -20ms) for motor preparation analysis.

### Normal Task 1: Go/No-go classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Go:No-go ratio is 2:1 (~300 go vs ~150 no-go); mild class imbalance. 375 files from 75 subjects x 5 sessions each. Age group (young/older) in participants.tsv can be used as a grouping variable.

| Event | y | Meaning |
 |-------|---|------|
| `go` | 1 | Go stimulation (reaction required) |
| `no-go` | 0 | No-go stimulation (requires suppression) |


### Normal Task 2: Correct/Error Suppression Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Commission errors (64 total) are rare compared to correct inhibitions; severe class imbalance requires oversampling or weighted loss.

| Event | y | Meaning |
 |-------|---|------|
| `no-go` (correct inhibition) | 0 | Correct inhibition no-go |
| `error of commission` | 1 | Error response (key pressed during no-go) |

## Data Quality Notes

- 66-channel EEG; includes ECG and pupil data (non-EEG channels should be excluded).
- Longitudinal design with 5 sessions per subject; verify session consistency.
- Age group comparison (young vs older) is the primary experimental variable.

## References

- **Reference**: `Age-related differences in EEG, ECG and pupilography during auditory cued reaction time tasks. OpenNeuro ds003690.`
