# Ultra High-Density EEG - Interictal Migraine and Controls

**Dataset**: `other_migrainedb` | **Year**: 2020 | **URL**: https://kilthub.cmu.edu/articles/dataset/Ultra_high-density_EEG_recording_of_interictal_migraine_and_controls_sensory_and_rest/12636731
**Category**: Biological State | **Subjects**: 35 | **Files (Completed)**: 117 | **Channels**: 128 | **Sampling Rate**: 512 Hz | **Manual Review**: Jiping Cui

## Paradigm

The dataset contains high-density EEG recordings from interictal migraine patients and healthy controls during three conditions: (1) **SSVEP** - steady-state visual evoked potentials elicited by visual stimuli flickering at 4 Hz and 6 Hz; (2) **SSAEP** - steady-state auditory evoked potentials elicited by amplitude-modulated tones at 4 Hz and 6 Hz; and (3) **resting state**. EEG was recorded using a BioSemi ActiveTwo system with a customized 128-channel high-density EEG montage, sampled at 512 Hz (Chamanzar et al., 2020).

According to the dataset documentation, the main study reports 17 interictal migraine patients and 18 age- and gender-matched healthy controls. The demographic table lists migraine participants M1-M18, but M13 lacks the SSAEP recording and was excluded from the main study dataset; M2, M6, and M18 were also excluded from some analyses because of medication. The matched control group consists of 18 controls, while C2, C6, and C12 are additional healthy control subjects available in the dataset rather than missing-data subjects.

The dataset enables comparison of sensory processing and resting-state EEG activity between migraine patients in the interictal period and healthy controls.

## File Scan Result

> **Kernel SHA256**: `04696b9de008be8dc5f92ddbac8703374e60d9fbe7d14a0898fb627163677e2f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `4Hz auditory feedback end for Health` | 221 | event | raw | 4 Hz auditory steady-state stimulus end (healthy controls) |
| `4Hz auditory feedback end for migraine` | 181 | event | raw | 4 Hz auditory steady-state stimulus end (migraine patients) |
| `4Hz auditory stimulation start for Health` | 2100 | event | raw | 4 Hz auditory steady-state stimulus onset (healthy controls) |
| `4Hz auditory stimulation start for migraine` | 1706 | event | raw | 4 Hz auditory steady-state stimulus onset (migraine patients) |
| `4Hz vision feedback end for Health` | 226 | event | raw | 4 Hz visual steady-state stimulus end (healthy controls) |
| `4Hz vision feedback end for migraine` | 200 | event | raw | 4 Hz visual steady-state stimulus end (migraine patients) |
| `4Hz vision stimulation start for Health` | 2016 | event | raw | 4 Hz visual steady-state stimulus onset (healthy controls) |
| `4Hz vision stimulation start for migraine` | 1787 | event | raw | 4 Hz visual steady-state stimulus onset (migraine patients) |
| `6Hz auditory feedback end for Health` | 176 | event | raw | 6 Hz auditory steady-state stimulus end (healthy controls) |
| `6Hz auditory feedback end for migraine` | 137 | event | raw | 6 Hz auditory steady-state stimulus end (migraine patients) |
| `6Hz auditory stimulation start for Health` | 2099 | event | raw | 6 Hz auditory steady-state stimulus onset (healthy controls) |
| `6Hz auditory stimulation start for migraine` | 1705 | event | raw | 6 Hz auditory steady-state stimulus onset (migraine patients) |
| `6Hz vision feedback end for Health` | 165 | event | raw | 6 Hz visual steady-state stimulus end (healthy controls) |
| `6Hz vision feedback end for migraine` | 150 | event | raw | 6 Hz visual steady-state stimulus end (migraine patients) |
| `6Hz vision stimulation start for Health` | 2016 | event | raw | 6 Hz visual steady-state stimulus onset (healthy controls) |
| `6Hz vision stimulation start for migraine` | 1779 | event | raw | 6 Hz visual steady-state stimulus onset (migraine patients) |
| `resting Health` | 21 | event | raw | Resting-state EEG recording (healthy controls) |
| `resting migraine` | 18 | event | raw | Resting-state EEG recording (migraine patients) |


> The task events are encoded as numeric trigger values in the BioSemi Status channel. For sensory tasks, the main epoch labels described in the protocol are 1 and 2 for the onset of 4 Hz and 6 Hz stimulation, respectively, and 11 and 22 for response/feedback-related markers following 4 Hz and 6 Hz trials. The stimulus-onset markers correspond to the start of the 2 s visual or auditory stimulation. The 11/22 markers are not generic trial-end markers; they are emitted only for feedback/response trials in which a response was detected. In addition to these epoch labels, the stimulus scripts also send task-level markers such as 30 near the start of the task and 20 near the end.
> 
> For resting state, the protocol defines label 1 as the start of a resting block and label 2 as the end of a resting block. The available BDF files do contain such 1/2 resting-state block markers, although the markers visible in the current subset may not fully cover all six 2 min blocks described in the protocol.
> 
> Any scanned event names that include group suffixes such as healthy/control or migraine should be treated as interpreted labels rather than raw trigger codes. These group labels should be removed or normalized before constructing modality- or frequency-classification tasks to avoid label leakage.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (108/117) | N/A |
| `sex` | partial (108/117) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Migraine Patient vs Healthy Control Classification (SSVEP/SSAEP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz auditory stimulation start for Health`, `4Hz auditory stimulation start for migraine`, `4Hz vision stimulation start for Health`, `4Hz vision stimulation start for migraine`, `6Hz auditory stimulation start for Health`, `6Hz auditory stimulation start for migraine`, `6Hz vision stimulation start for Health`, `6Hz vision stimulation start for migraine`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `4Hz vision stimulation start for Health` | 0 | Healthy control |
  | `6Hz vision stimulation start for Health` | 0 | Healthy control |
  | `4Hz auditory stimulation start for Health` | 0 | Healthy control |
  | `6Hz auditory stimulation start for Health` | 0 | Healthy control |
  | `4Hz vision stimulation start for migraine` | 1 | Interictal migraine patient |
  | `6Hz vision stimulation start for migraine` | 1 | Interictal migraine patient |
  | `4Hz auditory stimulation start for migraine` | 1 | Interictal migraine patient |
  | `6Hz auditory stimulation start for migraine` | 1 | Interictal migraine patient |
- **Evidence**:
  - Protocol: sensory-task labels `1` and `2` mark the onset of 4 Hz and 6 Hz stimulation, respectively; each visual or auditory stimulus lasts 2 s. Labels `11` and `22` are response/feedback-related markers and should not be treated as generic trial-end markers.
  - 10.1093/braincomms/fcab061 — Chamanzar et al. compare high-density EEG responses between interictal migraine participants and healthy controls during 4 Hz / 6 Hz visual and auditory stimulation and resting state.
- **Notes**: Uses Event Structure labels that encode group membership (`for Health` vs `for migraine`). M13 lacks SSAEP/auditory data and should be excluded from SSAEP-specific analyses. C2, C6, and C12 are additional available healthy controls rather than missing-data controls. Use subject-level train/test splitting to avoid leakage across epochs from the same participant.

### Potential Task 1: SSVEP Frequency Classification - 4 Hz vs. 6 Hz
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`4Hz vision stimulation start for Health`, `4Hz vision stimulation start for migraine`, `6Hz vision stimulation start for Health`, `6Hz vision stimulation start for migraine`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `4Hz vision stimulation start for Health` | 0 | 4 Hz visual flicker stimulus |
  | `4Hz vision stimulation start for migraine` | 0 | 4 Hz visual flicker stimulus |
  | `6Hz vision stimulation start for Health` | 1 | 6 Hz visual flicker stimulus |
  | `6Hz vision stimulation start for migraine` | 1 | 6 Hz visual flicker stimulus |
- **Evidence**:
  - Protocol: SSVEP trials used Gaussian-filtered vertical sine-wave gratings alternating contrast sinusoidally at 4 Hz or 6 Hz for 2 s. Labels `1` and `2` indicate 4 Hz and 6 Hz stimulus onset, respectively.
  - 10.1093/braincomms/fcab061 — The visual stimulation condition includes 4 Hz and 6 Hz steady-state visual stimulation, enabling frequency-specific SSVEP analysis.
- **Notes**: Restrict this task to SSVEP/visual recordings. The group suffixes are included only because they are part of the available Event Structure IDs; the classification target should be frequency, not subject group.

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
> **Status**: completed
