# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 39 | **Files (Completed)**: 117 | **Channels**: 128 | **Sampling Rate**: 512 Hz
**Manual Review**: Jiping Cui

## Paradigm

This dataset contains ultra high-density EEG recordings from 39 available participants: 18 interictal migraine participants, 18 matched healthy controls, and 3 additional healthy control recordings (`C2`, `C6`, `C12`) that were released with the dataset but not included in the matched analysis file. Recordings were acquired with a BioSemi ActiveTwo system (128 channels, 512 Hz) under three conditions: steady-state visual stimulation (SSVEP, 4 Hz and 6 Hz), steady-state auditory stimulation (SSAEP, 4 Hz and 6 Hz), and eyes-open resting state. The associated publication analyzed a subset of these data rather than the full released dataset: `M13` lacked SSAEP recording, and `M2`, `M6`, and `M18` were excluded from the main analysis because of medication before recording. The dataset therefore distinguishes between raw available participants and publication analysis subsets.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `4Hz auditory feedback end for Health` | 221 | event | raw | End of the post-stimulus feedback/response interval after a 4 Hz auditory trial |
| `4Hz auditory feedback end for migraine` | 181 | event | raw | End of the post-stimulus feedback/response interval after a 4 Hz auditory trial |
| `4Hz auditory stimulation start for Health` | 2100 | event | raw | Onset of a 2 s 4 Hz amplitude-modulated auditory stimulus |
| `4Hz auditory stimulation start for migraine` | 1706 | event | raw | Onset of a 2 s 4 Hz amplitude-modulated auditory stimulus |
| `4Hz vision feedback end for Health` | 226 | event | raw | End of the post-stimulus feedback/response interval after a 4 Hz visual trial |
| `4Hz vision feedback end for migraine` | 200 | event | raw | End of the post-stimulus feedback/response interval after a 4 Hz visual trial |
| `4Hz vision stimulation start for Health` | 2016 | event | raw | Onset of a 2 s 4 Hz visual flicker/grating stimulus |
| `4Hz vision stimulation start for migraine` | 1787 | event | raw | Onset of a 2 s 4 Hz visual flicker/grating stimulus |
| `6Hz auditory feedback end for Health` | 176 | event | raw | End of the post-stimulus feedback/response interval after a 6 Hz auditory trial |
| `6Hz auditory feedback end for migraine` | 137 | event | raw | End of the post-stimulus feedback/response interval after a 6 Hz auditory trial |
| `6Hz auditory stimulation start for Health` | 2099 | event | raw | Onset of a 2 s 6 Hz amplitude-modulated auditory stimulus |
| `6Hz auditory stimulation start for migraine` | 1705 | event | raw | Onset of a 2 s 6 Hz amplitude-modulated auditory stimulus |
| `6Hz vision feedback end for Health` | 165 | event | raw | End of the post-stimulus feedback/response interval after a 6 Hz visual trial |
| `6Hz vision feedback end for migraine` | 150 | event | raw | End of the post-stimulus feedback/response interval after a 6 Hz visual trial |
| `6Hz vision stimulation start for Health` | 2016 | event | raw | Onset of a 2 s 6 Hz visual flicker/grating stimulus |
| `6Hz vision stimulation start for migraine` | 1779 | event | raw | Onset of a 2 s 6 Hz visual flicker/grating stimulus |
| `resting Health` | 21 | event | raw | Resting-state condition marker (eyes open, fixation) |
| `resting migraine` | 18 | event | raw | Resting-state condition marker (eyes open, fixation) |


> The original task triggers described in the protocol are numeric labels (`1`, `2`, `11`, `22` for sensory tasks; `1`/`2` for resting-state block start/end). The scanned event names shown here are interpreted labels rather than the raw trigger codes.
> `stimulation start` markers correspond to stimulus onset for 2 s visual or auditory trials.
> `feedback end` markers correspond to the end of the post-stimulus feedback/response interval and are not generic trial-end markers; they occur only in feedback/response trials.
> The group suffixes (`for Health`, `for migraine`) encode subject class in the event name itself, so event names should be normalized before building frequency/modality tasks to avoid label leakage.
> Resting-state markers appear to be recording-level condition markers in the current scan output; the protocol describes six 2 min resting blocks, but block-level start/end markers are not explicitly represented here.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | partial (108/117) | 36/39 participants |
| `subject_sex` | partial (108/117) | 36/39 participants |
| `device` | missing | Need Update. |


## Tasks

### Classical Task 1: Migraine Patient vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`M-series subjects (M1-M18)`, `C-series subjects (C1-C21)`]
- **Label Route**: `info`
- **Meta Level**: super
- **Target Definition**:
  | Info | y | Meaning |
  |-------|---|---------|
  | `M-series subjects (M1-M18)` | 1 | Migraine patient |
  | `C-series subjects (C1-C21)` | 0 | Healthy control |
- **Evidence**:
  - DOI: 10.1093/braincomms/fcab061 — This paper analyzes EEG coherence patterns to compare 14 interictal migraine patients with 18 healthy controls during visual/auditory stimulation (4Hz and 6Hz, 2s epochs) and resting state (2-s non-overlapping intervals), finding significantly lower alpha-band coherence in frontal clusters for migraineurs.
- **Kernel Notes**: 

### Potential Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz vision stimulation start`, `6Hz vision stimulation start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `4Hz vision stimulation start` | 0 | 4 Hz flicker stimulus |
  | `6Hz vision stimulation start` | 1 | 6 Hz flicker stimulus |
- **Evidence**:
  - DOI: **Kernel Notes**: — 
- **Kernel Notes**: 

### Potential Task 2: Migraine Patient vs. Control - Resting State (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0, length = 5.0 s, target_events = [`subject ID prefix `M``, `subject ID prefix `C``]
- **Label Route**: `info`
- **Meta Level**: super
- **Target Definition**:
  | Info | y | Meaning |
  |-------|---|---------|
  | `subject ID prefix `M`` | 1 | Migraine participant |
  | `subject ID prefix `C`` | 0 | Healthy control |
- **Evidence**:
  - DOI: **Kernel Notes**: — 
- **Kernel Notes**: 

## Data Quality Notes

- Group labels are subject-level metadata derived from the subject ID prefix (`M` = migraine, `C` = control), not native task labels. Raw scanned event names may also contain group-specific suffixes and should be normalized before task construction to avoid label leakage.
- Subject age/sex metadata are available for the 36 matched-analysis participants in `Migraine_Control_Demographics.csv`, but not for the extra released controls (`C2`, `C6`, `C12`).
- Subject `M13` lacks the SSAEP recording, so auditory-task availability differs from the nominal participant count.
- The released dataset and the publication analysis subset are not identical: `M2`, `M6`, and `M18` were excluded from the main paper analysis because of medication, and `C2`, `C6`, `C12` are extra released controls not included in the matched-analysis metadata file.
- The protocol defines numeric trigger codes for stimulus onset/feedback and six 2 min resting blocks, whereas the scanned event table contains interpreted text labels; event semantics should be checked carefully before epoching.
- `feedback end` markers correspond to the end of the post-stimulus feedback/response interval and are not generic trial-end markers; they occur only in feedback trials.
- Recordings use a 128-channel high-density montage, which increases spatial detail but also makes channel handling and interpolation choices more consequential.
- The associated publication analyzed both sensory and resting EEG in 2 s windows; resting-state analyses used non-overlapping 2 s intervals.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
