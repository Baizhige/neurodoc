# EEG, ECG and Pupil Data from Young and Older Adults: Rest and Auditory Cued Reaction Time Tasks

**Dataset**: `openneuro_ds003690` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003690
**Category**: Sensory/Response | **Subjects**: 75 | **Files (Completed)**: 375
**Channels**: 66 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Young and older adults performed auditory-cued simple reaction time and go/no-go tasks to investigate age-related differences in neural and physiological activity. An auditory cue preceded each trial; participants pressed a button to go stimuli and withheld responses to no-go stimuli. Error feedback tones were provided after commission errors. The study examines how aging affects preparatory neural activity, inhibitory control, and pupil dilation responses.

## File Scan Result

> **Kernel SHA256**: `238667d2d976c5230122a5fe62e3c988484a923ef0279c5bc9b5158bb5f13c2a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 20250 | event | raw | Auditory stimulus onset marker |
| `10` | 375 | event | raw | Auditory warning cue preceding stimulus |
| `11` | 99 | event | raw | Auxiliary trial event marker |
| `2` | 13500 | event | raw | Button press response |
| `3` | 254 | event | raw | Error feedback tone |
| `4` | 1500 | event | raw | No-go stimulus |
| `5` | 13525 | event | raw | Go stimulus |
| `6` | 88 | event | raw | Error of commission (response to no-go) |
| `7` | 88 | event | raw | Auxiliary error event marker |
| `9` | 320 | event | raw | Task block start marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Go/No-go Response Inhibition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 6.0 s, target_events = [`cue`, `go`, `no-go`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `go` | 1 | Go stimulus requiring button press |
  | `no-go` | 0 | No-go stimulus requiring response withholding |
  | `cue` | 2 | Cue-only trial (no target presented) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — "analyzes simultaneous EEG, ECG, and pupillogram from 75 subjects (36 young, 39 older) performing detection and go/no-go tasks"
- **Kernel Notes**: Cue-locked epochs. Baseline correction: -0.2s to 0s relative to cue onset. Window covers full ERP response (-0.2s to 6s) and beta oscillation range (-1s to 4.5s). Exclude error of commission trials from label mapping. Event ID mapping required: verify semantic names (`cue`, `go`, `no-go`) against actual numeric IDs in dataset.

### Classical Task 2: Simple Reaction Time Detection
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`cue`, `button press`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `cue` → `button press` | reaction_time (ms) | Time from cue onset to button press response |
- **Super Meta Notes**: Derived from raw events `cue` and `button press` by computing time difference between cue onset timestamp and subsequent button press timestamp. Kernel step: align epochs to cue onset, extract button press timestamp within epoch, compute delta in milliseconds.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — "simple reaction time detection task with analysis of reaction time relationships to cortical activity"
- **Kernel Notes**: Filter to valid button press responses only. Exclude error of commission trials. Preserve derivation metadata: unit=ms, source=cue-to-button-press delta, version=1.

### Classical Task 3: Commission Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`no-go`, `error of commission`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `no-go` (correct inhibition) | 0 | Correct response withholding |
  | `error of commission` | 1 | Incorrect response to no-go stimulus |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — analyzes response inhibition and error processing
- **Kernel Notes**: Epochs aligned to no-go stimulus onset. Low error count (64) relative to no-go trials (150) may limit statistical power. Verify event ID mapping for `error of commission` against numeric IDs.

### Potential Task 1: Error Feedback Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`error of commission`, `error feedback tone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `error of commission` | 1 | Commission error occurs |
  | `error feedback tone` | 0 | Feedback presented (may follow commission or other error) |
- **Evidence**:
  - DOI: 10.1016.j.neuroimage.2019.06.004 — paradigm includes error feedback tones after commission errors
- **Kernel Notes**: Count mismatch (179 feedback tones vs 64 commission errors) suggests some feedback tones follow non-commission errors or multiple errors per trial. Requires careful trial matching before epoching.

### Potential Task 2: Beta Oscillation Analysis (Go vs No-go)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 4.5 s, target_events = [`go`, `no-go`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `go` | 1 | Go stimulus requiring response |
  | `no-go` | 0 | No-go stimulus requiring inhibition |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.06.004 — Extended window for frequency-domain analysis of sensorimotor beta activity during response preparation and execution
- **Kernel Notes**: Extended tmax captures beta oscillation window. Focus on alpha/beta band (13-30 Hz) for motor task paradigm. Use same epoch alignment as Classical Task 1.