# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 36 | **Files (Completed)**: 117 | **Channels**: 128 | **Sampling Rate**: 512 Hz
**Manual Review**: Jiping Cui

## Paradigm

Thirty-six subjects (18 interictal migraine patients: M1-M18; 18 healthy controls: C1-C21, with C2, C6, C12 missing data) underwent high-density EEG recording (BioSemi ActiveTwo, 128 channels, 512 Hz) in three task conditions (Chiang et al., 2020): (1) **SSVEP** - steady-state visual evoked potential, flickering stimuli at 4 Hz and 6 Hz; (2) **SSAEP** - steady-state auditory evoked potential, tone sequences at 4 Hz and 6 Hz; (3) **resting state**. The dataset enables comparison of sensory processing in migraine patients vs. healthy controls in the interictal (between-attack) period.

*Note: Subject M13 is missing data for the SSAEP task, which accounts for some literature citing only 17 migraine patients.*

## File Scan Result


> **Kernel SHA256**: `544fe6fad1eb26fcf2b990ee48fcaf4bfecaad1ae0564a4eb2d9cfa0fd06fb2b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4Hz auditory feedback end for Health` | 221 | event | raw |  |
| `4Hz auditory feedback end for migraine` | 181 | event | raw |  |
| `4Hz auditory stimulation start for Health` | 2100 | event | raw |  |
| `4Hz auditory stimulation start for migraine` | 1706 | event | raw |  |
| `4Hz vision feedback end for Health` | 226 | event | raw |  |
| `4Hz vision feedback end for migraine` | 200 | event | raw |  |
| `4Hz vision stimulation start for Health` | 2016 | event | raw |  |
| `4Hz vision stimulation start for migraine` | 1787 | event | raw |  |
| `6Hz auditory feedback end for Health` | 176 | event | raw |  |
| `6Hz auditory feedback end for migraine` | 137 | event | raw |  |
| `6Hz auditory stimulation start for Health` | 2099 | event | raw |  |
| `6Hz auditory stimulation start for migraine` | 1705 | event | raw |  |
| `6Hz vision feedback end for Health` | 165 | event | raw |  |
| `6Hz vision feedback end for migraine` | 150 | event | raw |  |
| `6Hz vision stimulation start for Health` | 2016 | event | raw |  |
| `6Hz vision stimulation start for migraine` | 1779 | event | raw |  |
| `resting Health` | 21 | event | raw |  |
| `resting migraine` | 18 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | partial (108/117) | N/A |
| `subject_sex` | partial (108/117) | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Migraine Patient vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` | `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: 
  - Stimulus epochs: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz vision stimulation start`, `6Hz vision stimulation start`, `4Hz auditory stimulation start`, `6Hz auditory stimulation start`]
  - Resting state: segment_length = 2.0 s, overlap = 0.0 s, target_events = [`resting state block start`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | M-series subjects (M1-M18) | 1 | Migraine patient |
  | C-series subjects (C1-C21) | 0 | Healthy control |
- **Super Meta Notes**: Derived from subject ID prefix: 'M' prefix indicates migraine patient, 'C' prefix indicates healthy control. This is a super-label derived from metadata, not from raw event markers. Kernel step: Parse subject filename to extract prefix (M/C), map to binary label (1/0), apply uniformly to all epochs from that subject.
- **Evidence**:
  - DOI: 10.1093/braincomms.fcab061 — This paper analyzes EEG coherence patterns to compare 14 interictal migraine patients with 18 healthy controls during visual/auditory stimulation (4Hz and 6Hz, 2s epochs) and resting state (2-s non-overlapping intervals), finding significantly lower alpha-band coherence in frontal clusters for migraineurs.
- **Kernel Notes**: For stimulus epochs: extract epochs time-locked to any stimulation onset event (4Hz/6Hz vision/auditory), apply subject's group label. For resting state: segment within resting state block boundaries using 2-s non-overlapping windows, apply subject's group label. Combine both modalities for full group classification pipeline.

### Potential Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `4Hz vision stimulation start` | 0 | 4 Hz flicker stimulus |
| `6Hz vision stimulation start` | 1 | 6 Hz flicker stimulus |

### Potential Task 2: Migraine Patient vs. Control - Resting State (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s (within `resting state block start` / end boundaries)
- **Label Route**: `event`
- **Target Definition**: N/A (group label from subject ID: M-series = migraine, C-series = healthy)
- **Notes**: Group labels (migraine vs. control) are encoded in the subject ID (M/C prefix in filename). Apply the group label post-hoc after segmentation. (replaces Potential Task 2 from original analysis.md)

## Data Quality Notes

- Group labels must be derived from the subject ID prefix (M for migraine, C for control).
- Age range: 19-54 years; sex: mixed male/female.
- High channel count (128); spatial filtering / source localization may be useful.
- Sensory task and resting state recordings provide complementary views of migraine-related cortical changes.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review