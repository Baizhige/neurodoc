# CHB-MIT Scalp EEG Database

**Dataset**: `physionet_chbmit` | **Year**: 2010 | **URL**: https://physionet.org/content/chbmit/1.0.0/
**Category**: Biological State | **Subjects**: 23 | **Files (Completed)**: 686 | **Channels**: 23 | **Sampling Rate**: 256 Hz | **Manual Review**: Zhida Shang

## Paradigm

Twenty-three pediatric subjects (22 original cases plus chb24 added later; 5 males aged 3-22, 17 females aged 1.5-19, with chb24 age/sex unknown) with intractable seizures were monitored at Children's Hospital Boston following withdrawal of anti-seizure medication to evaluate surgical candidacy (Shoeb & Guttag, 2010). Note: case chb21 was recorded 1.5 years after chb01 from the same female subject. Long-term continuous EEG was recorded from 23 scalp channels (bipolar montage following the 10-20 system) at 256 Hz with 16-bit resolution. The dataset contains 686 EEG files, of which 129 contain one or more seizures, for a total of 198 annotated seizures. Seizure onset and offset times are documented in per-subject summary text files (`chbNN-summary.txt`); the kernel parses these to create `seizure` annotations spanning each ictal period.

## File Scan Result

> **Kernel SHA256**: `5b18a5f37633b5153a20c7a1573700377f710a8901f40e266ea5f1f3079e57e9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `interictal_complement` | 883 | event | super | Seizure-free complement of the raw seizure intervals within the current recording. |
| `interictal_ge_4h` | 392 | event | super | Seizure-free time at least 4 hours away from any seizure onset or offset. |
| `preictal_20min` | 229 | event | super | Twenty-minute window preceding seizure onset, clipped to non-seizure time. |
| `preictal_30min` | 239 | event | super | Thirty-minute window preceding seizure onset, clipped to non-seizure time. |
| `seizure` | 198 | event | raw | Seizure interval (onset to offset) parsed from the CHB-MIT summary/seizure annotations. |


> Counts in the Event Structure table represent annotation segments written to individual EDF files, not the number of logical seizure episodes. Super-meta events such as preictal_20min and preictal_30min are derived from seizure onset times and then clipped to file boundaries. Therefore, a single seizure may yield more than one preictal annotation segment when its preictal window spans multiple consecutive EDF files. As a result, the total counts for preictal_20min and preictal_30min can be greater than the total count for seizure.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (664/686) | e.g. 11, 14, 22 |
| `amplifier` | missing | N/A |
| `cap` | missing | N/A |
| `handedness` | missing | N/A |
| `sex` | partial (664/686) | e.g. Female, Male |


## Tasks

### Classical Task 1: Binary seizure detection (ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0, target_events = [`interictal_complement`, `seizure`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seizure` | 1 | Ictal (seizure period) |
  | `interictal_complement` | 0 | Interictal (seizure-free) |
- **Evidence**:
  - 10.1016/j.bspc.2024.107379 — CHB-MIT seizure intervals are taken from the dataset summary files, non-seizure data are taken from the remaining recording time, and each subject is represented with 2 s samples for seizure vs non-seizure classification.
  - 10.1038/s41598-025-18479-9 — CHB-MIT is used for binary epileptic seizure detection based on ictal and interictal EEG phases.
  - 10.1038/s41598-025-98389-y — Public EEG datasets including CHB-MIT are divided into 5 s fragments labeled as seizure or no seizure for binary classification, providing an alternative windowing protocol.
- **Notes**: 

### Classical Task 2: Seizure prediction (preictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s, overlap = 0.9, target_events = [`interictal_ge_4h`, `preictal_30min`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `preictal_30min` | 1 | Thirty-minute window preceding seizure onset, clipped to non-seizure time |
  | `interictal_ge_4h` | 0 | Seizure-free time at least 4 hours away from any seizure onset or offset |
- **Evidence**:
  - 10.1088/1741-2552/ada0e5 — CHB-MIT preictal data are defined as the 30 min before seizure onset, interictal data are at least 4 hours before seizure onset and 4 hours after seizure end, and EEG is segmented into 10 s intervals with 90% overlap.
  - 10.1109/access.2020.2976866 — CHB-MIT seizure prediction is formulated as preictal vs interictal classification, with the preictal state described as the 30 min before seizure onset.
  - 10.3390/app12094158 — CHB-MIT preictal/interictal seizure prediction uses a seizure-distance rule for interictal data and evaluates fixed-window EEG representations.
- **Notes**: Use generated super events directly. Extract 10-second windows with 90% overlap only inside `preictal_30min` and `interictal_ge_4h`; this makes `overlap = 9.0 s`. Exclude raw `seizure` intervals, postictal transition time, and any unlabeled seizure-free periods that do not satisfy the >=4-hour interictal rule.

### Potential Task 1: Three-class seizure state classification (preictal vs ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.75, target_events = [`interictal_ge_4h`, `preictal_20min`, `seizure`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `preictal_20min` | 0 | Twenty-minute window preceding seizure onset, clipped to non-seizure time |
  | `seizure` | 1 | Ictal period from annotated seizure onset to offset |
  | `interictal_ge_4h` | 2 | Seizure-free time at least 4 hours away from any seizure onset or offset |
- **Evidence**:
  - 10.54525/bbmd.1526069 — CHB-MIT EEG is organized as a three-class problem with pre-seizure, seizure, and non-seizure labels; the pre-seizure interval is the 20 min before seizure, and spectrogram windows are 4 s long with a 1 s shift.
- **Notes**: 

## Data Quality Notes

- Severe class imbalance: the majority of recordings are seizure-free; balance by undersampling interictal or using cost-sensitive learning.
- Channel count varies: most files have 23 channels; some cases include 24 or 26 channels (extra ECG or vagal nerve stimulus channels); exclude non-EEG channels.
- Patient-specific model training is recommended; cross-patient generalization is difficult.
- Patient-specific seizure detection/prediction should be treated as evaluation protocol variants of Classical Tasks 1-2 rather than separate label tasks; avoid subject leakage, especially between chb01 and chb21.
- Subject chb24 has unknown age and sex.
- Age range: 1.5-22 years (pediatric); EEG morphology differs significantly from adult norms.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
