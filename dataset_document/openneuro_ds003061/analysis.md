# EEG data from an auditory oddball task

**Dataset**: `openneuro_ds003061` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003061
**Category**: Sensory/Response | **Subjects**: 39 | **Files (Completed)**: 39 | **Manual Review**: Pending
**Channels**: 79 | **Sampling Rate**: 256 Hz

## Paradigm

An auditory three-stimulus oddball task in which participants pressed a key in response to infrequent target tones among frequent standard tones and rare distractor tones. The paradigm is designed to elicit P300 event-related potentials. Event labels `oddball` (target tone onset), `standard` (non-target tone), `noise` (distractor tone), and `response` (keypress) are present in all 39 files, with pre-classified trial types available directly from the event stream.

## File Scan Result

> **Kernel SHA256**: `590cef96bf678dafeb0e4d820a1eae0922a577f8f75c8c73fe24db793bf95e50`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `condition 5` | 2 | event | raw | Experimental condition marker (unclassified) |
| `ignore` | 139 | event | raw | Ignored or excluded trial marker |
| `noise` | 4243 | event | raw | Distractor noise tone onset (~15% frequency) |
| `noise_with_reponse` | 21 | event | raw | Noise stimulus with erroneous keypress response |
| `oddball` | 586 | event | raw | Oddball target tone onset (1000Hz, ~15% frequency) |
| `oddball_with_reponse` | 3667 | event | raw | Oddball target with correct keypress response |
| `response` | 3771 | event | raw | Participant keypress response |
| `standard` | 19855 | event | raw | Standard non-target tone onset (500Hz, ~70% frequency) |
| `standard_with_reponse` | 80 | event | raw | Standard tone with erroneous keypress response |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores auxiliary continuous channels including EXG (auxiliary electrodes), Erg (physiological signals), and Plet (plethysmograph).
- **Candidate Labels**: `EXG1`, `EXG2`, `EXG3`, `EXG4`, `EXG5`, `EXG6`, `EXG7`, `EXG8`, `Erg1`, `Erg2`, `Plet`
- **Kernel Note**: Verify channel roles and units; EXG channels may contain external electrode data, Erg channels likely contain physiological responses (e.g., respiration, GSR), and Plet contains plethysmograph signal for heart rate monitoring.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Auditory Oddball Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`oddball`, `standard`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `standard` | 0 | Standard non-target tone (500Hz, ~70% frequency) |
  | `oddball` | 1 | Oddball target tone (1000Hz, ~15% frequency) |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Auditory oddball binary classification with target (1000Hz) vs standard (500Hz) tones; epochs -0.5 to 1.5s capture full P300 window (300-700ms); dataset ds003061 explicitly used.
- **Kernel Notes**: Use pre-classified `oddball` (586 trials) and `standard` (19855 trials) events directly; no metadata join required. Filter out `standard_with_response` (80 trials) as erroneous responses to non-targets. Response correctness can be validated by checking for corresponding `response` event after oddball trials.

---

### Classical Task 2: Correct Response Filtering (Oddball Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`oddball_with_response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `oddball_with_response` | 1 | Correct oddball response (target tone with keypress) |
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Validates target trials require button press; reaction time computed from stimulus to response.
- **Kernel Notes**: `oddball_with_response` (3667 trials) represents trials with both oddball stimulus and subsequent response event. Shorter window (-0.2 to 1.0s) focuses on early perception and P300 rather than motor execution. Reaction time = time(response) - time(stimulus) for each trial. Compare with `oddball` events to identify missed responses.

---

### Potential Task 1: Three-Way Stimulus Classification (Standard/Oddball/Noise)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`standard`, `oddball`, `noise`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `standard` | 0 | Standard non-target tone (500Hz, ~70%) |
  | `oddball` | 1 | Oddball target tone (1000Hz, ~15%) |
  | `noise` | 2 | Distractor noise tone (~15%) |
- **Kernel Notes**: Three-stimulus oddball paradigm includes standard, oddball target, and noise distractor stimuli. Available event counts: standard (19855), oddball (586), noise (4243). All three event types present in raw event stream. Exclude `standard_with_response` (80) and `noise_with_response` (21) as erroneous responses.

---

### Potential Task 2: Reaction Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`oddball_with_response`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | Needs verification | Reaction time computed as time(response) - time(stimulus) for each `oddball_with_response` trial (in seconds). No MISC channels present in dataset; RT must be derived from event timestamps. |
- **Regression Target**: `response_time` (from `misc` channel or computed as time(response) - time(stimulus))
- **Kernel Notes**: Compute RT = timestamp(response) - timestamp(stimulus) for each oddball_with_response trial. RT provides continuous target for regression, capturing variability in decision speed. Motor-related components (MRN, LRP) appear ~100-200ms around response; shorter window (-0.2 to 1.0s) captures perception-to-action pipeline.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
