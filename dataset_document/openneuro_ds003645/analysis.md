# Face Processing MEEG Dataset with HED Annotation

**Dataset**: `openneuro_ds003645` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003645
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 114 | **Channels**: 395 | **Sampling Rate**: 1100 Hz | **Manual Review**: Pending

## Paradigm

Participants performed a simple perceptual task judging the spatial symmetry of famous, unfamiliar, and scrambled faces during simultaneous MEG and EEG (MEEG) recording. This is a replication of the Wakeman and Henson (2015) dataset with Hierarchical Event Descriptor (HED) annotations added. The study serves as a reference dataset for multimodal neuroimaging analysis methods, with face symmetry judgment as the overt task while examining neural responses to face identity and familiarity.

## File Scan Result

> **Kernel SHA256**: `1bcb7fd82e5ba3373573a9b83d8aac6ed8740dc6d4f796cb4d70b7ea4f8d6061`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 2749 | event | super | Famous/familiar face stimulus (condition 1) |
| `event_2` | 2748 | event | super | Famous/familiar face stimulus (condition 2) |
| `event_3` | 2747 | event | super | Unfamiliar face stimulus (condition 1) |
| `event_4` | 2748 | event | super | Unfamiliar face stimulus (condition 2) |
| `event_5` | 2748 | event | super | Unfamiliar face stimulus (condition 3) |
| `event_6` | 2749 | event | super | Scrambled face stimulus (condition 1) |
| `event_7` | 2749 | event | super | Scrambled face stimulus (condition 2) |
| `event_8` | 2749 | event | super | Scrambled face stimulus (condition 3) |
| `event_9` | 2749 | event | super | Scrambled face stimulus (condition 4) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Face Type Classification (Famous/Unfamiliar/Scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7, event_8, event_9]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | event_1 | 0 | Famous/familiar face stimulus (condition 1) |
  | event_2 | 0 | Famous/familiar face stimulus (condition 2) |
  | event_3 | 1 | Unfamiliar face stimulus (condition 1) |
  | event_4 | 1 | Unfamiliar face stimulus (condition 2) |
  | event_5 | 1 | Unfamiliar face stimulus (condition 3) |
  | event_6 | 2 | Scrambled face stimulus (condition 1) |
  | event_7 | 2 | Scrambled face stimulus (condition 2) |
  | event_8 | 2 | Scrambled face stimulus (condition 3) |
  | event_9 | 2 | Scrambled face stimulus (condition 4) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2021.118766 — HED-annotated face processing MEEG dataset (ds003645) demonstrating super-level event metadata for three-class face perception (famous/familiar vs unfamiliar vs scrambled) with epochs extracted from -500ms to +1200ms around stimulus onset.
  - DOI: 10.1038/sdata.2015.1 — Original Wakeman and Henson face processing MEEG dataset with three-class face perception paradigm.
- **Kernel Notes**: Raw event IDs are event_1 through event_9 (9 conditions). The 9 events encode face type (famous/familiar, unfamiliar, scrambled) combined with symmetry judgment conditions. Map events 1-2 to famous/familiar (y=0), events 3-5 to unfamiliar (y=1), events 6-9 to scrambled (y=2) using HED sidecar annotations for validation. Extract only EEG channels (~64-70) from the 395-channel MEEG data before epoching. Verify event-to-condition mapping against HED JSON sidecar files in the BIDS dataset.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
