# MigraineDB (other_migrainedb)

**Dataset**: `other_migrainedb` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: Sensory/Response | **Subjects**: 35 | **Files (Completed)**: 11 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from 17 migraine patients and 18 age-matched healthy controls during visual and auditory steady-state stimulation. Participants were presented with visual (vertical grating pattern) and auditory (modulated tone) stimuli that varied in temporal frequency (4Hz and 6Hz). The experiment was conducted using a Biosemi ActiveTwo amplifier with a 64-channel cap (with some recordings using 128-channel HD-EEG configurations).

## File Scan Result

> **Kernel SHA256**: `7e281f0c4ead5dc222ef49e6e346c1aa27c0d9861b19754c7db38cb51bef0fac`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 7754 | event | raw | Stimulus condition 1 onset (frequency condition 1, e.g., 4Hz) |
| `event_11` | 828 | event | raw | Auditory trial onset marker |
| `event_2` | 7754 | event | raw | Stimulus condition 2 onset (frequency condition 2, e.g., 6Hz) |
| `event_20` | 70 | admin | raw | Block boundary or run segment marker |
| `event_22` | 628 | event | raw | Visual trial onset marker |
| `event_23` | 1 | admin | raw | System marker (rare, possibly recording sync or error) |
| `event_30` | 83 | admin | raw | Block start/end marker or condition transition |
| `event_5` | 27 | admin | raw | System marker (possibly recording start/stop or subject/session identifier) |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `Status` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Dataset contains 17 migraine patients and 18 age-matched healthy controls; exact ages not specified in available evidence |
| `amplifier` | complete | Biosemi ActiveTwo |
| `cap` | complete | Biosemi 64-channel cap (note: README describes 128 customized electrode locations for HD-EEG recordings) |
| `handedness` | missing |  |
| `sex` | missing | Dataset contains 12 female migraine patients out of 17; gender distribution of controls not fully specified in available evidence |

## Tasks

### Potential Task 1: SSVEP 2-class frequency discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2 s *, target_events = [`event_1`, `event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_1 | 0 | Stimulus condition 1 onset (frequency condition 1, e.g., 4Hz) |
  | event_2 | 1 | Stimulus condition 2 onset (frequency condition 2, e.g., 6Hz) |
- **Evidence**:
  - README — "visual (vertical grating pattern) ... stimulation which varied in temporal frequency (4 and 6Hz)"
  - events.json/sidecar analysis — event_1 and event_2 are the high-count stimulus condition onsets matching the two frequency conditions; event_22 marks visual trial onsets but does not distinguish conditions
- **Notes**: SSVEP paradigm with two temporal frequencies (4Hz and 6Hz) indicated by event_1 and event_2. Epoch timing inferred from standard SSVEP analysis windows; 2-second epochs provide sufficient cycles for frequency discrimination (8 cycles at 4Hz, 12 cycles at 6Hz).

### Potential Task 2: SSAEP 2-class frequency discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2 s *, target_events = [`event_1`, `event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_1` | 0 | Stimulus condition 1 onset (frequency condition 1, e.g., 4Hz) |
  | `event_2` | 1 | Stimulus condition 2 onset (frequency condition 2, e.g., 6Hz) |
- **Evidence**:
  - Dataset README and events.json sidecar — SSAEP paradigm with two temporal frequency conditions (4Hz and 6Hz) indicated by event_1 and event_2 onset markers; ~828 auditory trials (event_11) across subjects with condition markers event_1 (7694 occurrences) and event_2 (7722 occurrences) representing the two frequency discrimination classes.
- **Notes**: Epoch timing inferred from standard SSAEP analysis windows (1-2s) to allow frequency resolution of steady-state auditory evoked potentials; no explicit epoch timing in sidecars. The two high-count event IDs (event_1, event_2) correspond to the two frequency conditions in the .txt annotation file condition codes (1,2), with counts matching ~200 trials × multiple runs across subjects.

### Potential Task 3: Visual vs auditory modality classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 1 s *, target_events = [`event_11`, `event_22`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_11 | 0 | Auditory trial onset |
  | event_22 | 1 | Visual trial onset |
- **Evidence**:
  - Event count analysis — event_11 (n≈828) and event_22 (n≈628) approximate auditory and visual trial counts respectively from .txt annotation files across 11 subjects
  - README — "visual (vertical grating pattern) and auditory (modulated tone) stimulation which varied in temporal frequency (4 and 6Hz)"
  - events.json sidecar — event_11: "Auditory trial onset marker", event_22: "Visual trial onset marker"
- **Notes**: Early sensory evoked differences between visual and auditory processing occur within first 100-300ms; 1s epoch captures initial transient and some steady-state. No explicit timing in sidecars, so parameters are inferred from typical evoked response latencies for cross-modal sensory discrimination.

## Data Quality Notes

- Age and sex metadata are missing from the EEG files; only partial demographic information is available from the README (12 of 17 migraine patients are female, but control group gender distribution is unspecified).
- Handedness information is completely missing for all subjects.
- Channel count discrepancy: the README describes 128 customized electrode locations for HD-EEG recordings, but the scanned files show 64 channels with Biosemi 64-channel cap metadata; this suggests mixed recording configurations across subjects or sessions.
- Only 11 of 35 subjects' files were successfully completed in the scan, indicating potential data availability or processing issues for the remaining 24 subjects.
- Event counts for event_1 and event_2 (7754 each) greatly exceed event_11 (828) and event_22 (628), suggesting that event_1 and event_2 may mark condition onsets within trials rather than individual trial onsets, or that multiple condition markers occur per trial.
- Epoch timing parameters for all tasks are inferred rather than explicitly documented in sidecars.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
