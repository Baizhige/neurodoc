# EEG Motor Movement/Imagery Dataset (EEGMMIDB)

**Dataset**: `physionet_eegmmidb` | **Year**: 2009 | **URL**: https://physionet.org/content/eegmmidb/1.0.0/
**Category**: Action/Output | **Subjects**: 109 | **Files (Completed)**: 1502 | **Channels**: 64 | **Sampling Rate**: 160 Hz | **Manual Review**:

## Paradigm

This dataset comprises 109 healthy subjects performing motor execution and motor imagery tasks across 14 runs per subject. Subjects performed actual fist/foot movements (runs 3-6, 11-14) and imagined movements (runs 7-10) while seated in a chair with a computer monitor displaying task cues. EEG was recorded using the BCI2000 system with a 64-channel electrode cap according to the international 10-10 system. Each run consists of multiple trials with alternating baseline rest periods (~4.1-4.2s) and task periods (~4.1s), with event markers T0 (rest), T1 (task condition 1), and T2 (task condition 2) indicating trial phase onsets.

## File Scan Result

> **Kernel SHA256**: `1a950693afd82bf814a7f7014737f8860f9f3780be51cc2c31ab15ebb4414a0b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `T0` | 19893 | event | raw | Trial phase onset: inter-trial baseline/rest period (duration ~4.1-4.2s) |
| `T1` | 9858 | event | raw | Trial phase onset: task condition 1 (duration ~4.1s) |
| `T2` | 9818 | event | raw | Trial phase onset: task condition 2 (duration ~4.1s) |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `run_number` | missing |  |
| `run_type` | missing |  |
| `sex` | missing |  |
| `subject_id` | missing |  |

## Tasks

### Classical Task 1: 2-class rest vs task state detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4.1 s *, target_events = [`T0`, `T1`, `T2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T0 | 0 | rest (inter-trial baseline period) |
  | T1 | 1 | task (merged task conditions) |
  | T2 | 1 | task (merged task conditions) |
- **Evidence**:
  - 10.3389/fnins.2021.660032 — Binary classification of motor task vs rest using 2-second sliding windows; 70.54-76.07% accuracy reported for binary motor task vs rest discrimination. T1 and T2 merged into single task class versus T0 rest class.
- **Notes**: T1 and T2 are merged into a single 'task' class (y=1) per the reference approach, which performs binary rest vs task discrimination rather than distinguishing between the two task conditions. T0 serves as the rest/baseline class (y=0). Epoch window covers the full ~4.1s trial duration as indicated by event durations in the dataset; the reference used 2-second sliding windows with overlap, but full-trial epoching at 0-4.1s is standard for event-based paradigms.

### Classical Task 2: 4-class motor imagery and execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.1 s, target_events = [`T1`, `T2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T1 | 0 | task condition 1 (run-dependent: left fist / both fists / imagined left / imagined both / actual left / actual both) |
  | T2 | 1 | task condition 2 (run-dependent: right fist / both feet / imagined right / imagined both / actual right / actual both) |
- **Evidence**:
  - 10.1088/1741-2552/ad905d — 4-class classification: left hand, right hand, both hands, both feet; 87.1% cross-subject, 99.1% within-subject accuracy
  - 10.1109/embc.2018.8512590 — 4-class motor imagery and execution using EEGMMIDB
  - 10.1109/tla.2018.8291481 — 4-class classification on EEGMMIDB dataset
- **Notes**: This task requires run-dependent decoding since T1/T2 meanings vary by run (runs 3-4: left/right fist; runs 5-6: both fists/both feet; runs 7-8: imagined left/right; runs 9-10: imagined both; runs 11-12: actual left/right; runs 13-14: actual both). The kernel must extract run_number from filename/events metadata to disambiguate T1/T2 labels. The 4-class formulation collapses across imagery vs execution modalities (left, right, both hands, both feet), yielding a 4-way classification rather than the raw T1/T2 binary split. Event T0 (rest/baseline) is excluded from target_events as it is not a task condition.

### Classical Task 3: 2-class left vs right hand motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.1 s, target_events = [`T1`, `T2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T1 | 0 | Task condition 1 (left hand — actual runs 3-4, imagined runs 7-8) |
  | T2 | 1 | Task condition 2 (right hand — actual runs 3-4, imagined runs 7-8) |
- **Evidence**:
  - 10.1088/1741-2552/ad905d — 2-class left hand vs right hand classification using runs 3-4 (actual) and 7-8 (imagined); 79.4% accuracy reported for combined contraction and imagery; 87.1% for cross-subject with deep learning
  - 10.15368/theses.2017.62 — 4.1-second epochs used for left/right hand motor imagery classification; T1=left hand, T2=right hand
- **Notes**: This task uses event route with raw meta level. T1 and T2 are trial phase onset markers for two task conditions. The official dataset documentation (outside the locked ground truth) establishes that T1/T2 correspond to left/right hand in runs 3-4 (actual movement) and runs 7-8 (imagined movement). The kernel's must_derive_misc `run_number` channel enables filtering to the specific runs where T1/T2 have consistent left/right semantics, but the classification labels themselves come directly from the event IDs (raw meta level).

### Classical Task 4: 2-class both fists vs both feet motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4.1 s *, target_events = [`T1`, `T2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T1 | 0 | task condition 1 (both fists — actual or imagined) |
  | T2 | 1 | task condition 2 (both feet — actual or imagined) |
- **Evidence**:
  - 10.1088/1741-2552/ad905d — 2-class both fists vs both feet classification using runs 5-6 (actual) and 9-10 (imagined)
  - 10.1109/embc.2018.8512590 — T1/T2 motor imagery decoding on PhysioNet EEGMMIDB
  - 10.1109/tla.2018.8291481 — Standard 4-class decomposition including fists/feet conditions
- **Notes**: This task uses T1/T2 event markers directly. The event meanings are phase markers ('task condition 1/2') per the locked ground truth, not explicit MI class labels. The mapping to 'both fists'/'both feet' is established by the dataset's run-specific paradigm structure: runs 5-6 (actual movement) and runs 9-10 (imagined movement) use T1/T2 exclusively for the fists/feet conditions, per the dataset documentation. The kernel must filter to runs 5-6 and 9-10 using the derived `run_number` channel to ensure correct semantic binding. Epoch parameters are inferred from the standard ~4.1s trial duration observed across task runs.

### Classical Task 5: Readiness Potential Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 0.5 s *, overlap = 0.0 s *, target_events = [`T1`, `T2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | T1 | 0 | Task condition 1 onset — readiness potential latency regression target (time to movement, ~400ms pre-movement) |
  | T2 | 0 | Task condition 2 onset — readiness potential latency regression target (time to movement, ~400ms pre-movement) |
- **Evidence**:
  - 10.1016/j.cmpbup.2021.100027 — Continuous readiness potential (RP) detection on Cz channel. RP latency at -384.9±296.5 ms before movement onset. Binary detection formulation (RP present vs absent) with TPR 76.5±8.27%, FP/min 2.4±1.07. Uses continuous single-channel EEG without standard trial splitting.
- **Notes**: This task adapts continuous RP detection to event-anchored regression. The readiness potential is a negative cortical potential preceding voluntary movement onset by ~400ms. Since T1/T2 mark trial phase onsets (not movement onsets themselves), the regression target represents the time from trial onset to the anticipated movement execution within the task period. The epoch window [-2.0, 0.5]s captures the pre-movement RP build-up relative to trial onset. Both T1 and T2 are treated identically as regression targets (value=0) since the dataset does not distinguish motor conditions at the event level; the actual RP latency variability would be learned from the EEG signal characteristics rather than event labels. Overlap set to 0.0 as default for long-event epoching when not specified.

### Potential Task 1: 3-class rest vs task condition 1 vs task condition 2
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4.1 s *, target_events = [`T0`, `T1`, `T2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `T0` | 0 | rest / inter-trial baseline period |
  | `T1` | 1 | task condition 1 |
  | `T2` | 2 | task condition 2 |
- **Evidence**:
- **Notes**: Event IDs T0, T1, T2 are trial phase onset markers (not MI class labels). T0 marks inter-trial baseline/rest periods (~4.1-4.2s), while T1 and T2 mark two distinct task conditions. The 3-class formulation treats these phase markers as states for classification: rest vs task condition 1 vs task condition 2. Epoch parameters are inferred from the ~4.1s event durations observed in R03-R14 task runs; tmin/tmax values marked with * are inferred. Events are native to the raw files (Meta Level = raw).

### Potential Task 2: 2-class task condition 1 vs task condition 2
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4.1 s *, target_events = [`T1`, `T2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T1 | 0 | task condition 1 |
  | T2 | 1 | task condition 2 |
- **Evidence**:
- **Notes**: Event-based classification using native T1/T2 trial phase markers. T0 rest periods are excluded. The ~4.1s epoch window aligns with the known duration of task conditions in this dataset. T1 and T2 meanings are inferred from their alternating appearance with T0 baseline separators across task runs R03-R14; no explicit semantic labels beyond 'task condition 1/2' were found in source files.

### Potential Task 3: Rest vs Task with Run-Type Stratification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4.1 s *, target_events = [`T0`, `T1`, `T2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | T0 | 0 | rest (inter-trial baseline period) |
  | T1 | 1 | task (merged task conditions) |
  | T2 | 1 | task (merged task conditions) |
- **Evidence**:
- **Notes**: This task merges T1 and T2 into a single task-positive class (y=1) versus T0 rest baseline (y=0), forming a binary rest-vs-task detection problem. The run_type derived misc channel (source_field: events.tsv:run_id) enables stratified cross-validation that balances actual motor execution runs (R03-R06, R11-R12) and imagined motor imagery runs (R07-R10, R13-R14) across folds, testing generalization across these modalities. Note that run_type is NOT used as the classification target; it serves only as a stratification variable. The epoch parameters are inferred from the documented ~4.1s trial phase durations in the EEGMMIDB task runs.

## Data Quality Notes

- All metadata fields (age, amplifier, cap, handedness, run_number, run_type, sex, subject_id) are missing from the Info scan, requiring filename parsing and event metadata derivation for critical task decoding.
- T1/T2 event meanings are run-dependent and not self-describing in the raw event markers; correct task labeling requires external knowledge of the EEGMMIDB run structure or filename-derived run_number.
- The dataset contains both actual motor execution and imagined motor imagery runs, which have substantially different EEG characteristics (mu/beta suppression patterns, EMG contamination); mixing these without run-type awareness may degrade classification performance.
- Event durations show slight variation (~4.1-4.2s for T0, ~4.1s for T1/T2); epoch windows using fixed 4.1s may occasionally truncate or pad trials slightly.
- Some subjects have incomplete data (fewer than 14 runs); task formulations requiring specific run subsets will have variable sample counts per subject.
- The readiness potential regression task uses an unconventional formulation since T1/T2 mark trial onsets rather than true movement onsets; the ~400ms RP latency is approximate and subject-dependent.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
