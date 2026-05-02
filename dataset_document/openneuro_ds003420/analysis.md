# conneXion Dataset 1: HD-EEG Visual Naming

**Dataset**: `openneuro_ds003420` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003420
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 92 | **Channels**: 256 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants performed visual naming and spelling tasks of visually presented objects (both meaningful and meaningless pictures) while high-density 256-channel EEG and speech onset data were recorded. This is Dataset 1 of the conneXion project. Participants vocalized responses for meaningful pictures (naming task), while meaningless pictures served as a control condition eliciting no vocal response. Trigger codes D249 and D250 mark stimulus events for meaningful and meaningless conditions respectively, with speech onset timing captured for reaction time analysis.

## File Scan Result

> **Kernel SHA256**: `74d4809704a3eab21b88ed2a18c6cabdcffce6be8046d3c66e50a76f627cef33`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Brain Network State Segmentation in Picture Naming
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`trigger/D249`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | BNS1 | 0 | Brain Network State 1: 0-119ms post-stimulus |
  | BNS2 | 1 | Brain Network State 2: 120-150ms post-stimulus |
  | BNS3 | 2 | Brain Network State 3: 151-190ms post-stimulus |
  | BNS4 | 3 | Brain Network State 4: 191-320ms post-stimulus |
  | BNS5 | 4 | Brain Network State 5: 321-480ms post-stimulus |
  | BNS6 | 5 | Brain Network State 6: 481-535ms post-stimulus |
- **Evidence**:
  - DOI: 10.1016/j.cortex.2015.08.019 — Dense 256-channel EEG picture naming task identifies six brain network states (BNSs) through gamma-band (30-45Hz) phase synchronization clustering from -200ms baseline to ~600ms post-stimulus
- **Kernel Notes**: Segment epochs into 6 temporal classes based on post-stimulus latency windows. Use k-means clustering on gamma-band (30-45Hz) source connectivity features to assign BNS labels. Verify trigger/D249 corresponds to stimulus onset marker in events.tsv before epoching.

---

### Classical Task 2: Reaction Time Regression in Visual Object Naming
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.5 s, target_events = [`trigger/D249`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | Needs verification | Reaction time / voice onset time (ms) from stimulus onset to vocalization; derived from speech recording analysis (Praat software). No MISC channels found in File Scan Result — requires manual verification of audio channel or alternative RT source |
- **Super Meta Notes**: Derived from speech recording analysis (Praat software). Kernel must extract audio onset time from the recorded oral responses and compute: y = voice_onset_time - stimulus_onset_time. Only available for subjects with valid speech responses (meaningful picture trials).
- **Evidence**:
  - DOI: 10.1088/1741-2552.aad7b1 — 256-channel EEG visual object naming correlates gamma-band (30-45Hz) network modularity metrics with reaction time (voice onset latency) from stimulus onset to 500ms
- **Kernel Notes**: Extract reaction time from misc channel or derive from audio recordings. Compute correlation between gamma-band network features and reaction time. Handle missing RT values for subjects without vocal responses (trigger/D250 meaningless picture trials excluded). Verify trigger/D249 semantic meaning in events.tsv.

---

### Classical Task 3: Meaningful vs Meaningless Picture Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.5 s, target_events = [`trigger/D249`, `trigger/D250`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `trigger/D249` | 0 | Meaningful picture stimulus (naming response expected) |
  | `trigger/D250` | 1 | Meaningless picture stimulus (silent response) |
- **Evidence**:
  - DOI: 10.1088/1741-2552.aad7b1 — Two-class visual object recognition task comparing meaningful vs meaningless images with reaction time regression; stimulus codes distinguish condition types
- **Kernel Notes**: Classify epochs based on stimulus condition. Meaningful pictures (trigger/D249) elicit vocal responses (reaction time available); meaningless pictures (trigger/D250) elicit no vocal response (participants silent). Critical: verify trigger/D249 and trigger/D250 condition mapping in events.tsv since analysis.md documented generic IDs 0/1 that do not match actual event nomenclature. Use events.tsv semantic decoding to confirm which trigger corresponds to meaningful vs meaningless conditions.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
