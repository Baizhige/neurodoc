# Face Processing MEEG Dataset with HED Annotation

**Dataset**: `openneuro_ds003645` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003645
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 114
**Channels**: 395 | **Sampling Rate**: 1100 Hz

## Paradigm

Participants performed a simple perceptual task judging the spatial symmetry of famous, unfamiliar, and scrambled faces during simultaneous MEG and EEG (MEEG) recording. This is a replication of the Wakeman and Henson (2015) dataset with Hierarchical Event Descriptor (HED) annotations added. The study serves as a reference dataset for multimodal neuroimaging analysis methods, with face symmetry judgment as the overt task while examining neural responses to face identity and familiarity.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003645

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No EEG trigger markers detected; events encoded in HED annotations or MEEG-specific channels |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Face Type Classification (Famous vs Unfamiliar vs Scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = ['Famous/Familiar Faces', 'Unfamiliar (Nonfamous) Faces', 'Scrambled Faces']
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Famous/Familiar Faces` | 0 | Famous/familiar face stimulus |
  | `Unfamiliar (Nonfamous) Faces` | 1 | Unfamiliar (non-famous) face stimulus |
  | `Scrambled Faces` | 2 | Phase-scrambled face control stimulus |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — Original Wakeman-Henson face processing MEEG dataset (OpenFMRI ds000117, replicated as OpenNeuro ds003645) where participants performed symmetry judgment on famous, unfamiliar, and scrambled face stimuli while EEG and MEG were recorded at 1100 Hz, with epochs extracted from -500 to +1200 ms around stimulus onset for ERP analysis comparing face vs scrambled face and familiar vs unfamiliar face conditions.
- **Kernel Notes**: The dataset uses three-class face type classification. Events are derived from experimental condition markers in the data. The primary analysis window for face processing ERP components (N170, N200, N400) is typically -100 ms to 800 ms post-stimulus, but full epochs span -500 ms to 1200 ms for initial preprocessing. Participants judged spatial symmetry of faces while EEG/MEG recorded.

### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (HED annotation requires additional parsing))
- **Notes**: 395-channel MEEG dataset (MEG + EEG combined); only EEG channels are relevant here. Very high channel count. Face stimuli (famous/unfamiliar/scrambled) are annotated via HED; standard BIDS event reading should recover trial_type if events.tsv is properly formatted.

## Data Quality Notes

- MEEG dataset; 395 channels include both MEG and EEG sensors. Isolate EEG channels before analysis.
- No EEG trigger events detected in the EEG .set files; events may be in MEEG-format files or HED sidecar.
- Very high sampling rate (1100 Hz) and channel count; high computational requirements.

## References

- **Reference**: `Wakeman and Henson (2015) / Robbins et al. (2021). Face processing MEEG dataset with HED annotation.`
