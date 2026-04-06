# EEG, ECG and Pupil Data from Young and Older Adults: Rest and Auditory Cued Reaction Time Tasks

**Dataset**: `openneuro_ds003690` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003690
**Category**: Sensory/Response | **Subjects**: 75 | **Files (Completed)**: 375
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Young and older adults performed auditory-cued simple reaction time and go/no-go tasks to investigate age-related differences in neural and physiological activity. An auditory cue preceded each trial; participants pressed a button to go stimuli and withheld responses to no-go stimuli. Error feedback tones were provided after commission errors. Resting-state EEG was also recorded. The study examines how aging affects preparatory neural activity, inhibitory control, and pupil dilation responses.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `cue` | 375 | event | raw | Auditory warning cue preceding stimulus |
| `go` | 300 | event | raw | Go stimulus (respond with button press) |
| `no-go` | 150 | event | raw | No-go stimulus (withhold response) |
| `button press` | 300 | event | raw | Participant button-press response |
| `error of commission` | 64 | event | raw | Commission error (response to no-go) |
| `error feedback tone` | 179 | event | raw | Auditory error feedback tone |
| `task start` | 320 | event | raw | Task block start marker |
| `task end` | 375 | event | raw | Task block end marker |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Go/No-go Response Inhibition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 6.0 s *, target_events = [`go`, `no-go`, `cue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `go` | 1 | Go stimulus (button press required) |
  | `no-go` | 0 | No-go stimulus (withhold response) |
  | `cue` | 2 | Cue-only trial (no target presented) * |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — "This paper analyzes EEG/ECG/pupil data from 36 young and 39 older adults performing cued simple RT and go/no-go auditory tasks"
- **Kernel Notes**: Epochs are cue-locked. Paper uses -0.2s to 6s for ERP analysis and -1s to 4.5s for beta oscillation analysis. Use tmax=6.0s to capture full ERP window. Baseline correction: -200ms to cue onset. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Simple Reaction Time Detection
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s *, target_events = [`cue`, `button press`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `cue` → `button press` | reaction_time (ms) | Time from cue onset to button press response |
- **Super Meta Notes**: Derived from raw events [`cue`, `button press`] by computing time difference between cue onset and button press event timestamps. Kernel step: extract timestamps for cue and subsequent button press events, compute delta in milliseconds.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — "simple reaction time detection task" with analysis of reaction time relationships to cortical activity
- **Kernel Notes**: Filter trials to those with valid button press responses. Exclude error of commission trials from RT computation.

### Classical Task 3: Commission Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s *, target_events = [`no-go`, `error of commission`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `no-go` (correct inhibition) | 0 | Correct response withholding |
  | `error of commission` | 1 | Incorrect response to no-go stimulus |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — analyzes response inhibition and error processing
- **Kernel Notes**: Epoch aligned to no-go stimulus onset. Label 1 (error) applies to error of commission events that occur after no-go. (replaces Potential Task 2 from original analysis.md)

### Potential Task 1: Beta Oscillation Analysis (Go vs No-go)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 4.5 s, target_events = [`go`, `no-go`]
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Beta band (13-30 Hz) analysis window per paper specification. Baseline: -450ms to -20ms.

| Event | y | Meaning |
|-------|---|------|
| `go` | 1 | Go trial (response required) |
| `no-go` | 0 | No-go trial (withhold response) |

## Data Quality Notes

- 66-channel EEG; includes ECG and pupil data (non-EEG channels should be excluded).
- Longitudinal design with 5 sessions per subject; verify session consistency.
- Age group comparison (young vs older) is the primary experimental variable.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review