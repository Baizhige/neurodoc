# Large Motor Imagery EEG Dataset (figshare_largemi)

**Dataset**: `figshare_largemi` | **Year**: 2018 | **URL**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698
**Category**: Action/Output | **Subjects**: 92 | **Files (Completed)**: 1080 | **Channels**: 22 | **Sampling Rate**: 200 Hz | **Manual Review**:

## Paradigm

This dataset comprises EEG recordings from 92 healthy subjects performing multiple motor imagery (MI) paradigms: CLA (cued left/right hand), HaLT (cued left/right hand, left/right leg, tongue, passive), FREEFORM (self-paced left/right hand), and 5F (individual finger MI: thumb, index, middle, ring, pinky). Data were recorded with 22 Ag/AgCl electrodes positioned according to the international 10-20 system at 200 Hz sampling rate. Subjects performed imagined movements cued by on-screen arrows or, in the FREEFORM paradigm, controlled a cursor via self-paced MI with keypress feedback.

## File Scan Result

> **Kernel SHA256**: `55c7ba678b40646b57bb2155917f45d4e518b74b1905b4514176ac74095f0adf`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1` | 16210 | event | raw | Trial phase onset: motor imagery cue 1 (left hand MI in CLA/HaLT/FREEFORM paradigms; thumb MI in 5F paradigm) |
| `2` | 15681 | event | raw | Trial phase onset: motor imagery cue 2 (right hand MI in CLA/HaLT/FREEFORM paradigms; index finger MI in 5F paradigm) |
| `3` | 14409 | event | raw | Trial phase onset: motor imagery cue 3 (passive state/rest in CLA/HaLT paradigms; middle finger MI in 5F paradigm) |
| `4` | 9255 | event | raw |  |
| `5` | 9586 | event | raw |  |
| `6` | 5522 | event | raw |  |
| `90` | 47 | admin | raw | System marker: session start boundary |
| `91` | 128 | admin | raw | System marker: session end boundary |
| `92` | 47 | admin | raw | System marker: trigger synchronization or calibration pulse |
| `99` | 265 | admin | raw | System marker: end of recording or experiment termination |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (75/92) | age ranges: 20-25, 25-30, 30-35 (n=75) |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | partial (75/92) | sex values: male, female (n=75) |

## Tasks

### Classical Task 1: 2-class left/right hand motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 0 | left hand MI (CLA/HaLT/FREEFORM paradigms) |
  | `2` | 1 | right hand MI (CLA/HaLT/FREEFORM paradigms) |
- **Evidence**:
  - 10.1109/TNSRE.2022.3186442 — TNSRE 2022 paper explicitly uses Kaya2018 dataset for 2-class left/right hand MI inter-subject benchmark with 85.1±9.5% accuracy
  - 10.1038/sdata.2018.211 — Original Kaya2018 dataset documentation; supports 2-class as natural subset of 6-class paradigm
  - 1Description.txt — Marker codes: '1-left hand MI, 2-right hand MI, 3-passive state, 4-left leg MI, 5-tongue MI, 6-right leg MI' for CLA/HaLT/FreeForm paradigms
  - Raw MAT file structure (CLA-SubjectJ-170508-3St-LRHand-Inter.mat, FREEFORMSubjectC1512102StLRHand.mat) — Confirms event IDs 1 and 2 present in marker channels alongside data
- **Notes**: This task uses only events 1 and 2 from the full 6-class CLA/HaLT/FREEFORM paradigms, excluding other MI classes (legs, tongue, passive). The 2-class left/right hand subset is a well-established benchmark configuration in the motor imagery literature. Epoch timing inferred from parent paradigm structure with ~3s total trial duration (1s cue period plus variable ISI).

### Classical Task 2: 5-class finger motor imagery (5F)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, target_events = [`1`, `2`, `3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 0 | thumb MI |
  | `2` | 1 | index finger MI |
  | `3` | 2 | middle finger MI |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Official descriptor documents 5F paradigm with 5 finger classes: thumb (1), index (2), middle (3), ring (4), pinky (5)
  - 1Description.txt — Confirms '1-thumb MI, 2-index finger MI, 3-middle finger MI, 4-ring finger MI' for 5F paradigm; event IDs 1-3 confirmed in raw data with established meanings
- **Notes**: Event IDs 4 and 5 (ring finger MI, pinky MI) are documented in description text but not confirmed by direct sampling in available raw data. Task uses only the 3 confirmed event IDs. The 5-class paradigm is documented but only 3 classes are verifiable from available event ID evidence. Epoch timing inferred from official descriptor (~3s trials with 1s cue and variable ISI) matching other paradigms in dataset.

### Classical Task 3: 2-class freeform left/right motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 0 | left hand MI (FREEFORM paradigm) |
  | `2` | 1 | right hand MI (FREEFORM paradigm) |
- **Evidence**:
  - 10.1038/sdata.2018.211 — Official descriptor documents FREEFORM paradigm with left/right keypress control ('d'/'l' keys). 1Description.txt notes 'FREEFORM=FREE STYLE 5F' and 'L=Left, R=Right'. Raw whosmat on FREEFORMSubjectC1512102StLRHand.mat shows marker values [0,1,2,99], confirming event IDs 1 and 2 for left/right. This is a distinct 2-class paradigm from the standard left/right hand MI in CLA.
- **Notes**: FREEFORM is a distinct interactive paradigm where subjects freely control left/right hand MI via keypress, unlike the cued CLA paradigm. Event IDs 1 and 2 are grounded by direct documentation in 1Description.txt ('1-left hand MI, 2-right hand MI' for FreeForm) and confirmed by raw marker values in FREEFORM .mat files. tmin/tmax inferred from standard motor imagery trial structure (~3s with 1s cue period) per epoch_hint.


## Data Quality Notes

- Event IDs 4, 5, and 6 have no documented meanings in the File Scan Result; their interpretation (left leg MI, tongue MI, right leg MI per 1Description.txt) is only available through external task documentation.
- Metadata completeness is limited: amplifier, cap, and handedness fields are entirely missing; age and sex are only available for 75 of 92 subjects.
- The 5F finger MI paradigm documents 5 classes but only events 1-3 are confirmed in available raw data; events 4-5 (ring finger, pinky) could not be verified.
- Multiple paradigms (CLA, HaLT, FREEFORM, 5F) share event ID values with different meanings depending on paradigm context, requiring careful paradigm-specific labeling.
- Epoch timing parameters (tmin=0s, tmax=3s) are inferred from documentation rather than directly encoded in data files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
