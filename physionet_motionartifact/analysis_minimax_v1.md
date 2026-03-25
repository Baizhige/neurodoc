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

### Primary Task 1: Motion Artifact Binary Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`R`, `F`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `R` | 0 | Clean (undisturbed) interval |
  | `F` | 1 | Motion-artifact-contaminated (disturbed) interval |
- **Evidence**:
  - DOI: https://doi.org/10.13026/C2988P — PhysioNet dataset contains EEG and fNIRS recordings with paired disturbed/undisturbed transducers; trigger annotations mark transitions between clean (R) and artifact-contaminated (F) intervals
  - DOI: https://doi.org/10.13026/C2988P — Provides paired recordings using trigger signals (R for rise=clean, F for fall=artifact-contaminated) and accelerometer ground truth to benchmark artifact removal algorithms
- **Kernel Notes**: Extract epochs around R and F trigger events marking clean/artifact interval transitions. Use tmin=-1.0s to capture pre-transition context and tmax=2.0s to capture the interval type. Label epochs with y=0 for R (clean) and y=1 for F (artifact). Process EEG (eeg_1-23) and fNIRS (fnirs_1-9) separately as they have different sampling rates (2048 Hz vs 200 Hz).

### Normal Task 1: Physical Activity Classification - Resting-State Segmentation (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A - activity labels must be assigned post-hoc from filename metadata (see notes)
- **Notes**: No event annotations are present; the kernel only records the recording ID in the description field. To assign activity labels for supervised learning, map recording IDs to physical activities using the dataset README. For artifact detection tasks, all recordings can be treated as motion-contaminated (except rest recordings).

### Normal Task 2: WPD-based Motion Artifact Correction (Super Meta)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 9.0 min *, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**: Ground truth clean signals from paired undisturbed channel (20mm for EEG, 30mm for fNIRS)
- **Notes**: Evaluate wavelet packet decomposition (WPD) methods by comparing denoised output against reference ground truth. Requires downsampling EEG from 2048Hz to 256Hz and decomposing to j=4 level (16 sub-bands).

## Data Quality Notes

- No structured event annotations; classification labels must be derived from filename-based recording IDs.
- Mixed signal types: EEG (eeg_1-eeg_23, 10 channels, 2048 Hz) and fNIRS (fnirs_1-fnirs_9, 12 channels, 200 Hz) in the same locator; process these file types separately.
- Age and sex information are not available.
- Primary use case is motion artifact removal/detection benchmarking, not cognitive task decoding.

## References

- **Reference**: Schultz T, Kluge T. Motion artifact dataset for EEG and fNIRS. PhysioNet. DOI: https://doi.org/10.13026/C2988P
