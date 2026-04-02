# 8-Channel SSVEP EEG Dataset with Artifact Trials

**Dataset**: `openneuro_ds004745` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004745
**Category**: Sensory/Response | **Subjects**: 6 | **Files (Completed)**: 6
**Channels**: 8 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed Steady-State Visual Evoked Potential (SSVEP) tasks at stimulation frequencies of 2 Hz, 4 Hz, and 8 Hz, under both static artifact-free and voluntary movement artifact conditions. The dataset was created to test artifact removal algorithms for SSVEP-based BCIs under realistic conditions with deliberate motion contamination. Multiple trigger codes mark different frequency and artifact conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004745

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `10` | 44 | short | raw | Trigger code 10 - likely artifact or rest condition |
| `4` | 38 | short | raw | 4 Hz SSVEP frequency onset |
| `2` | 36 | short | raw | 2 Hz SSVEP frequency onset |
| `1` | 36 | short | raw | Trigger code 1 |
| `3` | 36 | short | raw | Trigger code 3 |
| `5` | 36 | short | raw | Trigger code 5 |
| `6` | 36 | short | raw | Trigger code 6 |
| `7` | 36 | short | raw | Trigger code 7 |
| `8` | 38 | short | raw | 8 Hz SSVEP frequency onset |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: SSVEP frequency condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5 *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 0 | 2 Hz SSVEP condition |
  | `4` | 1 | 4 Hz SSVEP condition |
  | `8` | 2 | 8 Hz SSVEP condition |
  | `10` | 3 | Artifact/rest condition |
- **Evidence**:
  - DOI: 10.1109/embc46164.2021.9629771 — "This paper evaluates ASR artifact removal on 8-channel SSVEP EEG data from 6 subjects performing tasks at 2Hz, 4Hz, and 8Hz stimulation frequencies under both artifact-free and artifact conditions, computing Frequency-Tagged Response (FTR) as the SSVEP measure."
- **Kernel Notes**: Kernel extracts sliding windows of 10 s with 50-75% overlap from raw signal, then assigns label based on which SSVEP condition (2/4/8 Hz or artifact/rest) was active during that window. Requires events.tsv to determine condition timing for label assignment. Bandpass filter 0.15-40Hz applied as preprocessing. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: SSVEP frequency condition classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 6 subjects - very small dataset. Full trigger decode needed from events.tsv. Deliberate motion artifacts present in some trials.

| Event | y | Meaning |
|-------|---|------|
| `2` | 0 | 2 Hz SSVEP condition |
| `4` | 1 | 4 Hz SSVEP condition |
| `8` | 2 | 8 Hz SSVEP condition |
| `10` | 3 | Artifact/rest condition |


## Data Quality Notes

- Only 6 subjects and 8 channels - limited for generalization.
- Deliberate motion artifacts present in some trials; note artifact condition labels.

## References

- **Reference**: `Kumaravel et al., (IEEE EMBC 2021)`
