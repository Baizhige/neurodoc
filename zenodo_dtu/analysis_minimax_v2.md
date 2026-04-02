# DTU Auditory Attention Decoding Dataset

**Dataset**: `zenodo_dtu` | **Year**: 2018 | **URL**: https://zenodo.org/records/1199011
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

Eighteen subjects (S1-S18) participated in an auditory attention decoding (AAD) task in which two competing speakers were presented simultaneously and subjects were asked to attend to one speaker (Fuglsang et al., 2018). EEG was recorded from 64 channels (BioSemi ActiveTwo, 512 Hz) plus additional auxiliary channels (total 73). Each subject's recording is stored as a single MATLAB `.mat` file containing EEG data, stimulus onsets (`data.stimu`), and attended speaker labels (`data.attended`). The kernel extracts per-trial onset times and attended speaker indices to create trial-level annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://zenodo.org/records/1199011

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attend_speaker_1` | varies | long | raw | Subject attends to speaker 1 for the trial duration |
| `attend_speaker_2` | varies | long | raw | Subject attends to speaker 2 for the trial duration |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Note: The status_summary indicates that `stimu` and `attended` fields may be missing in some versions of the dataset (Needs verification:Needs verification); verify field availability before processing.
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimu`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Binary auditory attention decoding (speaker 1 vs speaker 2)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = use trial duration from annotation, overlap = 0.0 s, target_events = [`attend_speaker_1`, `attend_speaker_2`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attend_speaker_1` | 0 | Attend to speaker 1 |
  | `attend_speaker_2` | 1 | Attend to speaker 2 |
- **Super Meta Notes**: (not applicable - raw meta)
- **Evidence**:
  - DOI: 10.1088/2057.1976.ae09b2 — Uses DTU dataset (18 subjects) for binary left/right auditory attention classification, achieving 88.2% accuracy with a 2-second window.
- **Kernel Notes**: Raw annotations `attend_speaker_1` and `attend_speaker_2` already exist as per-trial labels in the dataset. The kernel extracts these as long events spanning the full trial duration. If `.mat` files are missing `stimu` or `attended` fields, kernel should produce `unknown` annotations. Users can apply additional windowing (e.g., 2s) inside the kernel if needed for specific model architectures.

### Normal Task 1: Auditory Attention Decoding - Speaker 1 vs. Speaker 2 (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, use trial duration from annotation, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Annotations are per-trial; trial boundaries from `data.stimu` onset times. If the dataset's `.mat` file is missing `stimu` or `attended` fields, the kernel will produce `unknown` annotations.

| Event | y | Meaning |
|-------|---|---------|
| `attend_speaker_1` | 0 | Attend to speaker 1 |
| `attend_speaker_2` | 1 | Attend to speaker 2 |


## Data Quality Notes

- MATLAB `.mat` field names (`data.stimu`, `data.attended`) must be present; verify before processing.
- One file per subject (18 files total); each file contains all trials for that subject.
- Stimulus audio files (speech signals) are required for full stimulus-reconstruction AAD decoding.

## References

- **Reference**: Fuglsang SA et al. (2018). Noise-robust cortical tracking of attended speech in real-world acoustic scenes. *NeuroImage*, 156, 435-444. https://zenodo.org/records/1199011
