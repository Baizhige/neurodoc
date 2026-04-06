# HD-EEGtask (Dataset 1)

**Dataset**: `openneuro_ds003420` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003420
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 92
**Channels**: 256 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed visual naming and spelling tasks of visually presented objects while high-density 256-channel EEG and speech onset data were recorded. This is Dataset 1 of the conneXion project. Trigger codes 0 and 1 mark stimulus events (likely object presentation onset and response/naming onset). Speech onset timing is also captured for reaction time analysis.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 92 (files) | event | raw | Visual object stimulus onset (or naming task trigger) |
| `0` | 91 (files) | event | raw | Stimulus condition 0 (or response trigger) |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Brain Network State Segmentation in Picture Naming
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s *, target_events = [`1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | BNS1 | 0 | Brain Network State 1: 0-119ms post-stimulus |
  | BNS2 | 1 | Brain Network State 2: 120-150ms post-stimulus |
  | BNS3 | 2 | Brain Network State 3: 151-190ms post-stimulus |
  | BNS4 | 3 | Brain Network State 4: 191-320ms post-stimulus |
  | BNS5 | 4 | Brain Network State 5: 321-480ms post-stimulus |
  | BNS6 | 5 | Brain Network State 6: 481-535ms post-stimulus |
- **Evidence**:
  - DOI: 10.1016/j.cortex.2015.08.019 — Dense 256-channel EEG picture naming task identifies six brain network states (BNSs) through gamma-band (30-45Hz) phase synchronization clustering from -200ms baseline to ~600ms post-stimulus
- **Kernel Notes**: Segment epochs into 6 temporal classes based on post-stimulus latency windows. Use k-means clustering on gamma-band (30-45Hz) source connectivity features to assign BNS labels. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Reaction Time Regression in Visual Object Naming
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.5 s, target_events = [`1`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | continuous | Reaction time / voice onset time (ms) from stimulus onset to vocalization |
- **Super Meta Notes**: Derived from speech recording analysis (Praat software). Kernel must extract audio onset time from the recorded oral responses and compute: y = voice_onset_time - stimulus_onset_time. Only available for subjects with valid speech responses.
- **Evidence**:
  - DOI: 10.1088/1741-2552.aad7b1 — 256-channel EEG visual object naming correlates gamma-band (30-45Hz) network modularity metrics with reaction time (voice onset latency) from stimulus onset to 500ms
- **Kernel Notes**: Extract reaction time from misc channel or derive from audio recordings. Compute correlation between gamma-band network features and reaction time. Handle missing RT values for subjects without vocal responses.

### Classical Task 3: Meaningful vs Meaningless Picture Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.5 s *, target_events = [`1`, `0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Meaningful picture stimulus |
  | `0` | 1 | Meaningless picture stimulus |
- **Evidence**:
  - DOI: 10.1088/1741-2552.aad7b1 — Two-class visual object recognition task comparing meaningful vs meaningless images with reaction time regression; stimulus codes distinguish condition types
- **Kernel Notes**: Classify epochs based on stimulus condition. Meaningful pictures elicit vocal responses (reaction time available); meaningless pictures elicit no vocal response (participants silent). Use event codes from events.tsv to verify condition mapping.

## Data Quality Notes

- Trigger codes 0/1 require semantic decoding from events.tsv or conneXion project documentation.
- High-density 256-channel array; significant computational overhead.
- Speech onset timing recorded - useful for naming latency regression.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review