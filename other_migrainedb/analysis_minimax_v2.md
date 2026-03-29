# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 36 | **Files (Completed)**: 117 | **Channels**: 128 | **Sampling Rate**: 512 Hz | **Manual Review**: Jiping Cui

## Paradigm

Thirty-six subjects (18 interictal migraine patients: M1-M18; 18 healthy controls: C1-C21, with C2, C6, C12 missing) underwent high-density EEG recording (BioSemi ActiveTwo, 128 channels, 512 Hz) in three task conditions (Chiang et al., 2020): 
- (1) **SSVEP** - steady-state visual evoked potential, flickering stimuli at 4 Hz and 6 Hz; 
- (2) **SSAEP** - steady-state auditory evoked potential, tone sequences at 4 Hz and 6 Hz;
- (3) **resting state**. The dataset enables comparison of sensory processing in migraine patients vs. healthy controls in the interictal (between-attack) period.

*Note: Subject M13 is missing data for the SSAEP task, which accounts for some literature citing only 17 migraine patients.*

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
| `1` | varies | long | raw | 4Hz stimulation onset (SSVEP/SSAEP) OR Resting block start |
| `2` | varies | long | raw | 6Hz stimulation onset (SSVEP/SSAEP) OR Resting block end |
| `11` | varies | admin | raw | 4Hz feedback end marker (SSVEP/SSAEP) |
| `22` | varies | admin | raw | 6Hz feedback end marker (SSVEP/SSAEP) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

> **Kernel Note (Critical)**: Event IDs are heavily overloaded across tasks. Marker `1` indicates "4Hz onset" in sensory tasks, but means "block start" in the resting state task. Data loaders/Kernels MUST use task-level metadata (e.g., task names in filenames like `_task-rest_` vs `_task-SSVEP_`) to disambiguate markers before downstream processing.
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `1`, `2`, `11`, `22` 
- **Kernel Note**: Keep trigger decoding table versioned and auditable. **Crucially, the decoding pipeline MUST implement conditional logic based on the paradigm (SSVEP vs. SSAEP vs. Resting) to assign the correct semantics to overloaded markers `1` and `2`.**

## Tasks

### Primary Task 1: Migraine Patient vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: 
  - Stimulus epochs: tmin = 0.0 s, tmax = 2.0 s, target_events = [`1`, `2`] *(Note: Must be filtered by SSVEP/SSAEP task files)*
  - Resting state: segment_length = 2.0 s, overlap = 0.0 s, target_events = [`1`] *(Note: Must be filtered by resting state task files)*
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | M-series subjects (M1-M18) | 1 | Migraine patient |
  | C-series subjects (C1-C21) | 0 | Healthy control |
- **Super Meta Notes**: Derived from subject ID prefix: 'M' prefix indicates migraine patient, 'C' prefix indicates healthy control. This is a super-label derived from metadata, not from raw event markers. Kernel step: Parse subject filename to extract prefix (M/C), map to binary label (1/0), apply uniformly to all epochs from that subject.
- **Evidence**:
  - DOI: 10.1093/braincomms.fcab061 — This paper analyzes EEG coherence patterns to compare 14 interictal migraine patients with 18 healthy controls during visual/auditory stimulation (4Hz and 6Hz, 2s epochs) and resting state (2-s non-overlapping intervals), finding significantly lower alpha-band coherence in frontal clusters for migraineurs.
- **Kernel Notes**: For stimulus epochs: extract epochs time-locked to event `1` or `2` (strictly within sensory task files), apply subject's group label. For resting state: segment within block boundaries (initiated by event `1` in resting task files) using 2-s non-overlapping windows, apply subject's group label. Combine both modalities for full group classification pipeline.

### Normal Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`1`, `2`] *(Filtered by SSVEP task files)*
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `1` (in SSVEP task) | 0 | 4 Hz flicker stimulus |
| `2` (in SSVEP task) | 1 | 6 Hz flicker stimulus |

### Normal Task 2: Migraine Patient vs. Control - Resting State (epoch_by_segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s (within `resting state block start` / end boundaries)
- **Label Route**: `Annotation`
- **Target Definition**: N/A (group label from subject ID: M-series = migraine, C-series = healthy)
- **Notes**: Group labels (migraine vs. control) are encoded in the subject ID (M/C prefix in filename). Apply the group label post-hoc after segmentation. (replaces Normal Task 2 from original analysis.md)


## Data Quality Notes

- Group labels must be derived from the subject ID prefix (M for migraine, C for control).
- Age range: 19-54 years; sex: mixed male/female.
- High channel count (128); spatial filtering / source localization may be useful.
- Sensory task and resting state recordings provide complementary views of migraine-related cortical changes.

## References

- **Reference**: Chiang AKI et al. (2020). Ultra high-density EEG recording of interictal migraine and controls sensory and rest. KiltHub CMU. https://kilthub.cmu.edu/articles/dataset/12636731
