# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 39 | **Files (Completed)**: 117 | **Channels**: 144 | **Sampling Rate**: 512 Hz

## Paradigm

Thirty-nine subjects (18 interictal migraine patients: M1-M18; 21 healthy controls: C1-C21) underwent high-density EEG recording (BioSemi ActiveTwo, 144 channels, 512 Hz) in three task conditions (Chiang et al., 2020): (1) **SSVEP** - steady-state visual evoked potential, flickering stimuli at 4 Hz and 6 Hz; (2) **SSAEP** - steady-state auditory evoked potential, tone sequences at 4 Hz and 6 Hz; (3) **resting state**. The dataset enables comparison of sensory processing in migraine patients vs. healthy controls in the interictal (between-attack) period.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4Hz vision stimulation start` | varies | short | raw | SSVEP 4 Hz flicker onset |
| `6Hz vision stimulation start` | varies | short | raw | SSVEP 6 Hz flicker onset |
| `4Hz vision feedback end` | varies | admin | raw | SSVEP 4 Hz block end marker |
| `6Hz vision feedback end` | varies | admin | raw | SSVEP 6 Hz block end marker |
| `4Hz auditory stimulation start` | varies | short | raw | SSAEP 4 Hz tone onset |
| `6Hz auditory stimulation start` | varies | short | raw | SSAEP 6 Hz tone onset |
| `4Hz auditory feedback end` | varies | admin | raw | SSAEP 4 Hz block end marker |
| `6Hz auditory feedback end` | varies | admin | raw | SSAEP 6 Hz block end marker |
| `resting state block start` | varies | rest | raw | Resting state block onset |
| `resting state block end` | varies | admin | raw | Resting state block end marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `4Hz vision stimulation start`, `6Hz vision stimulation start`, `4Hz auditory stimulation start`, `6Hz auditory stimulation start`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Migraine vs Control Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` (for SSVEP/SSAEP epochs) and `epoch_by_segmentation_hdf5` (for resting state)
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz vision stimulation start`, `6Hz vision stimulation start`, `4Hz auditory stimulation start`, `6Hz auditory stimulation start`, `resting state block start`] | segment_length = 2.0 s, overlap = 0.0 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | C-series subject | 0 | Healthy control |
  | M-series subject | 1 | Migraine patient |
- **Super Meta Notes**: Group labels are derived from subject ID prefix: 'M' prefix indicates migraine patient, 'C' prefix indicates healthy control. This is a super-label derived from metadata, not from raw event markers. Both sensory stimulation epochs (SSVEP/SSAEP, 2s duration) and resting state segments (2-s non-overlapping intervals) can be used for this group-level classification.
- **Evidence**:
  - DOI: 10.1093/braincomms.fcab061 — This paper analyzes EEG coherence patterns to compare 14 interictal migraine patients (after medication-excluded) with 18 healthy controls during visual/auditory stimulation (4Hz and 6Hz, 2s epochs) and resting state (2-s non-overlapping intervals), finding significantly lower alpha-band coherence in frontal clusters for migraineurs.
- **Kernel Notes**: Apply group label post-hoc by extracting subject prefix from filename. For resting state, use epoch_by_segmentation_hdf5 with segment_length=2.0s and overlap=0.0 within resting state block boundaries.

### Primary Task 2: SSVEP target/frequency decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `stim` or `Annotation`
- **Target Definition**: Stimulus frequency or target index
- **Evidence**: SSVEP paradigm is explicitly stated in dataset metadata/reference. Source: https://kilthub.cmu.edu/articles/dataset/12636731 DOI: https://doi.org/10.21236/ada393961

### Normal Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `4Hz vision stimulation start` | 0 | 4 Hz flicker stimulus |
| `6Hz vision stimulation start` | 1 | 6 Hz flicker stimulus |


### Normal Task 2: Migraine Patient vs. Control - Resting State (epoch_by_segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s (within `resting state block start` / end boundaries)
- **Label Route**: `Annotation`
- **Target Definition**: N/A (group label from subject ID: M-series = migraine, C-series = healthy)
- **Notes**: Group labels (migraine vs. control) are encoded in the subject ID (M/C prefix in filename). Apply the group label post-hoc after segmentation.

## Data Quality Notes

- Group labels must be derived from the subject ID prefix (M for migraine, C for control).
- Age range: 19-54 years; sex: mixed male/female.
- High channel count (144); spatial filtering / source localization may be useful.
- Sensory task and resting state recordings provide complementary views of migraine-related cortical changes.

## References

- **Reference**: Chiang AKI et al. (2020). Ultra high-density EEG recording of interictal migraine and controls sensory and rest. KiltHub CMU. https://kilthub.cmu.edu/articles/dataset/12636731
