# Face Processing MEEG Dataset with HED Annotation

**Dataset**: `openneuro_ds003645` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003645
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 114
**Channels**: 395 | **Sampling Rate**: 1100 Hz

## Paradigm

Participants performed a simple perceptual task judging the spatial symmetry of famous, unfamiliar, and scrambled faces during simultaneous MEG and EEG (MEEG) recording. This is a replication of the Wakeman and Henson (2015) dataset with Hierarchical Event Descriptor (HED) annotations added. The study serves as a reference dataset for multimodal neuroimaging analysis methods, with face symmetry judgment as the overt task while examining neural responses to face identity and familiarity.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No EEG trigger markers detected; events encoded in HED annotations or MEEG-specific channels |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Face Type Classification (Famous vs Unfamiliar vs Scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [`trial_type` from events.tsv] *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | famous/familiar_face | 0 | Famous/familiar face stimulus |
  | unfamiliar_face | 1 | Unfamiliar/non-famous face stimulus |
  | scrambled_face | 2 | Scrambled face stimulus (control) |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — Wakeman and Henson face processing MEEG dataset with three-class face perception (famous vs unfamiliar vs scrambled), epochs extracted from -500ms to +1200ms around stimulus onset for ERP analysis.
- **Kernel Notes**: Verify raw event IDs from events.tsv (BIDS trial_type column). Expected values: 'famous'/'familiar'/'Famous_Familiar' and 'unfamiliar'/'Unfamiliar' and 'scrambled'/'Scrambled'. Map to exact raw event IDs present in dataset. Dataset uses HED annotations; may need to parse HED sidecar for event extraction.

### Potential Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null - HED annotation requires additional parsing)
- **Notes**: 395-channel MEEG dataset (MEG + EEG combined); only EEG channels are relevant here. Very high channel count. Face stimuli (famous/unfamiliar/scrambled) are annotated via HED; standard BIDS event reading should recover trial_type if events.tsv is properly formatted.

## Data Quality Notes

- MEEG dataset; 395 channels include both MEG and EEG sensors. Isolate EEG channels before analysis.
- No EEG trigger events detected in the EEG .set files; events may be in MEEG-format files or HED sidecar.
- Very high sampling rate (1100 Hz) and channel count; high computational requirements.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review