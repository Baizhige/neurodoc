# Prediction Error

**Dataset**: `openneuro_ds003846` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003846
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 50
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

A virtual reality haptic interaction study where participants reached out to touch spawned virtual boxes while receiving varied combinations of visual, vibrotactile, and electrical muscle stimulation (EMS) feedback. Trials were marked as "normal" (congruent feedback) or "conflict" (incongruent prediction error condition), allowing investigation of multisensory prediction error processing. Three feedback modality conditions were run in separate sessions: visual-only, vibrotactile-only, and combined EMS conditions.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `box` | 559 files | event | raw | Box spawned or box touched event |
| `vibroFeedback` | 198 files | event | raw | Vibrotactile feedback onset |
| `block` | 79 files | event | raw | Block start marker |
| `visualFeedback` | 50 files | event | raw | Visual feedback onset |


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

### Classical Task 1: Prediction Error Detection (Match vs Mismatch)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`box`] (replaces Potential Task 1 from original analysis.md)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `box` (match/congruent) | 0 | Normal (congruent) trial with expected feedback |
  | `box` (mismatch/incongruent) | 1 | Conflict (prediction error) trial with incongruent feedback |
- **Super Meta Notes**: Derived from raw event `box` by extracting the `normal_or_conflict` field embedded in the event annotation string. Kernel step: parse event description for `normal_or_conflict:normal` (label 0) vs `normal_or_conflict:conflict` (label 1).
- **Evidence**:
  - DOI: `10.3389/fnrgo.2024.1411305` — Binary classification of match (congruent/normal) vs mismatch (incongruent/conflict/prediction error) trials from openneuro_ds003846 dataset, using ERP epoch -0.1s to 0.6s relative to tap event.
- **Kernel Notes**: Extract events matching 'box' pattern, parse embedded annotation fields to derive normal_or_conflict label, epoch with tmin=-0.1s tmax=0.6s window centered on tap/box:touched event. The current analysis.md already contains a Potential Task covering this; this Classical Task replaces it with parameters directly supported by the extraction.

### Potential Task 1: Normal vs Conflict Prediction Error (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Events are richly annotated with metadata (reaction time, trial number, ISI, cube identity). The normal/conflict label is embedded in the event string. Epoch on box:touched events and extract the normal_or_conflict field for the label. Reaction time is also available as a regression target.

| Event | y | Meaning |
 |-------|---|------|
 | `box:touched;...normal_or_conflict:normal` | 0 | Normal (congruent) trial - box touched, expected feedback |
 | `box:touched;...normal_or_conflict:conflict` | 1 | Conflict (prediction error) trial - incongruent feedback |

### Potential Task 2: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `event`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds003846 DOI: 10.18112/openneuro.ds003846.v2.0.2

## Data Quality Notes

- Events contain full JSON-like annotation strings; label extraction requires parsing the event description
- Multiple sessions per subject (EMS, Vibro, Visual) with differing session lengths
- Sampling rate is ~500 Hz (exact value varies slightly across files)


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review