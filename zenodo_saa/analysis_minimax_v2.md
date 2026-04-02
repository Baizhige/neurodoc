# Spatial Auditory Attention EEG Dataset

**Dataset**: `zenodo_saa` | **Year**: 2019 | **URL**: https://zenodo.org/records/3357164
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 41 | **Sampling Rate**: 1024-4096 Hz (subject-variable)

## Paradigm

Eighteen subjects (S12, S13, S15, S21, S27, S28, S31, S33, S36, S37, S38, S39, S40, S42, S46, S47, S50, S51) participated in a spatial auditory attention decoding (SAA) task in which a target speaker was positioned at a fixed azimuth (30 deg) among distractors. EEG was recorded from 32 BioSemi ActiveTwo channels (A1-A32, Ag/AgCl cap) plus 8 external channels (total 41 channels) at variable sampling rates (1024, 2048, or 4096 Hz depending on subject). Stimulus events are encoded as BioSemi trigger codes in the Status channel; the kernel extracts these using `mne.find_events()` and converts them to text annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://zenodo.org/records/3357164

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (numeric BioSemi trigger codes) | varies | short/admin | raw | Stimulus onset, response, and trial boundary markers encoded in Status channel |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Trigger codes include stimulus onset markers (~3856-3966), control codes (65530-65532), and other administrative codes. Exact mapping requires dataset-specific documentation. Primary task: detect spatial attention direction from EEG.
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Spatial auditory attention decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`Needs verification from trigger codes`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | (trigger code for attended speaker) | 0 | Attend to left/right spatial location * |
  | (trigger code for unattended) | 1 | Attend to other location * |
- **Evidence**:
  - DOI: https://doi.org/10.5281/zenodo.3357164 — Spatial Auditory Attention dataset for decoding attended spatial auditory stream/location
- **Kernel Notes**: Trigger codes (~3856-3966) in Status channel mark stimulus onsets. Exact mapping to attention conditions requires dataset README verification. Variable sampling rates (1024-4096 Hz) require per-subject resampling.

### Normal Task 1: Spatial Attention Decoding - Present Stimulus (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s (per stimulus onset event), target_events = see Target Definition
- **Label Route**: `stim`
- **Target Definition**: Requires mapping trigger codes to stimulus/attention labels from the dataset documentation. Stimulus-onset codes (~3856-3966) mark individual sound presentations.
- **Notes**: Trigger code semantics must be verified against the dataset README or companion paper. Variable sampling rates across subjects require per-subject resampling to a common rate.


## Data Quality Notes

- Variable sampling rates (1024-4096 Hz) across subjects; resample to a common rate before cross-subject analysis.
- Trigger code interpretation requires dataset-specific documentation (Status channel values need decoding).
- 41 channels (32 EEG + 8 external); identify and exclude non-EEG channels before analysis.

## References

- **Reference**: Spatial Auditory Attention Dataset. Zenodo. https://zenodo.org/records/3357164
