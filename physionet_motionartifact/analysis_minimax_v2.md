# EEG/fNIRS Motion Artifact Dataset

**Dataset**: `physionet_motionartifact` | **Year**: 2018 | **URL**: https://physionet.org/content/motion-artifact/1.0.0/
**Category**: Others | **Subjects**: 32 | **Files (Completed)**: 32 | **Channels**: 10 (EEG) or 12 (fNIRS) | **Sampling Rate**: 2048 Hz (EEG), 200 Hz (fNIRS)

## Paradigm

Thirty-two recordings (23 EEG + 9 fNIRS) were collected from subjects performing various physical activities: cycling, running, walking, push-ups, pull-ups, stretching, and rest (Schultz & Kluge, 2018). The purpose is to provide a benchmark dataset for motion artifact detection and removal algorithms. EEG was recorded from 10 channels (gel electrodes) at 2048 Hz; fNIRS from 12 channels at 200 Hz. Each recording corresponds to one subject performing one activity. Activity labels are encoded in the filename (recording ID: `eeg_1` through `eeg_23`; `fnirs_1` through `fnirs_9`) and documented in a companion README.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/motion-artifact/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (none) | - | - | raw | No event annotations present; activity label is implicit in recording ID |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Motion Artifact Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s *, target_events = ['R', 'F']
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `R` | 0 | Clean interval (rise) |
  | `F` | 1 | Motion-contaminated interval (fall) |
- **Evidence**:
  - DOI: 10.13026/C2988P — PhysioNet dataset provides paired EEG/fNIRS with trigger annotations marking clean (R) and artifact-contaminated (F) intervals for benchmarking artifact removal algorithms.
- **Kernel Notes**: Extract epochs anchored at R (clean) and F (artifact) trigger events. Each epoch represents a ~2 second interval. Labels: R→0 (clean), F→1 (contaminated). Verify exact trigger labels from events.tsv. (replaces Primary Task 1 from original analysis.md)

### Normal Task 1: Physical Activity Classification - Resting-State Segmentation (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A - activity labels must be assigned post-hoc from filename metadata (see notes)
- **Notes**: No event annotations are present; the kernel only records the recording ID in the description field. To assign activity labels for supervised learning, map recording IDs to physical activities using the dataset README. For artifact detection tasks, all recordings can be treated as motion-contaminated (except rest recordings).


## Data Quality Notes

- No structured event annotations; classification labels must be derived from filename-based recording IDs.
- Mixed signal types: EEG (eeg_1-eeg_23, 10 channels, 2048 Hz) and fNIRS (fnirs_1-fnirs_9, 12 channels, 200 Hz) in the same locator; process these file types separately.
- Age and sex information are not available.
- Primary use case is motion artifact removal/detection benchmarking, not cognitive task decoding.

## References

- **Reference**: Schultz T, Kluge T. Motion artifact dataset for EEG and fNIRS. PhysioNet. DOI: https://doi.org/10.13026/C2988P
