# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50 | **Channels**: 15 | **Sampling Rate**: 125 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants without prior BCI experience performed a motor imagery vs rest protocol during EEG recording with a low-cost consumer-grade EEG system. The protocol included one familiarization run (RUN0), with actual dominant-hand grasping movements and rest trials, followed by four formal MI vs rest runs (RUN1-RUN4) whose protocol design specified 20 trials per condition per run. OpenViBE/OVTK annotations mark trial phases, condition cues, baseline periods, and session boundaries; markers named as feedback should be interpreted as protocol phase markers because no real feedback was presented to participants. The study evaluates offline motor-imagery detection and demonstrates the feasibility of affordable EEG hardware for MI-BCI research.

## File Scan Result

> **Kernel SHA256**: `28da8b02b8c556ef27d3c8fd26e82bcaa29756b38d38475b254a7c9394307bb0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `OVTK_GDF_Correct` | 697 | admin | raw | OpenViBE protocol tag; often co-occurs with `OVTK_GDF_Incorrect` and is not usable as a correct-feedback label |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Trial preparation phase onset: fixation cross |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session boundary: end of session |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial end marker |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | OpenViBE trial sub-stage marker after the task period; no actual feedback was presented in this experiment |
| `OVTK_GDF_Incorrect` | 697 | admin | raw | OpenViBE protocol tag; often co-occurs with `OVTK_GDF_Correct` and is not usable as an error-feedback label |
| `OVTK_GDF_Right` | 845 | event | raw | Condition cue: motor imagery of dominant-hand grasping in RUN1-RUN4; actual grasping cue in RUN0 |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial onset marker |
| `OVTK_GDF_Tongue` | 845 | event | raw | Condition cue: rest/idle condition; this OpenViBE/GDF label does not indicate tongue imagery in this dataset |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Run-level baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Run-level baseline period stop |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Auditory cue marker |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Session boundary: experiment start |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Session boundary: experiment stop |
| `OVTK_StimulationId_Train` | 48 | admin | raw | System marker: training/calibration |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Derived from the `age` column of `participants.tsv`; range 20-30 years |
| `sex` | complete | Derived from the `gender` column of `participants.tsv`; `M` = 6, `F` = 4 |
| `device` | complete | Data in Brief reports EEG acquisition with Electro-Cap System II connected to OpenBCI Cyton + Daisy; this device information is not repeated in each per-run `eeg.json` |
| `participant_id` | complete | Native `participants.tsv` column; 10 participants: `sub-02` to `sub-12`, excluding `sub-01` and `sub-11` |
| `gender` | complete | Native `participants.tsv` column; values are `M` and `F` |
| `age` | complete | Native `participants.tsv` column; unit is years, range 20-30 |
| `dominant hand` | complete | Native `participants.tsv` column; all participants are `R` |


## Tasks

### Classical Task 1: 2-class motor imagery vs rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Right` | 0 | Motor imagery of dominant-hand grasping |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle condition |
- **Evidence**:
  - 10.1016/j.dib.2022.108225 - The Data in Brief paper explicitly states that RUN1-RUN4 are MI vs rest runs, with 20 trials per condition per formal run, and that the event markers for motor imagery and rest are `OVTK_GDF_Right` and `OVTK_GDF_Tongue`, respectively.
  - 10.1016/j.heliyon.2020.e03425 - The original Heliyon paper describes dominant-hand grasping motor imagery vs rest/idle and uses EEG segments from 0.5 to 2.5 s after the cue in the single-time-window analysis.
  - `task-MIvsRest_events.json` - The BIDS sidecar defines value levels `770 = MI` and `772 = Rest`, confirming the two-condition paradigm structure.
  - README - States that RUN1-RUN4 consist of MI vs Rest conditions and that RUN0 involves real grasping movement for familiarization.
- **Notes**: Use RUN1-RUN4 for the formal MI vs rest task. RUN0 is a familiarization run in which `OVTK_GDF_Right` marks actual grasping rather than motor imagery, so RUN0 should be excluded or explicitly filtered at the file/run level. `OVTK_GDF_Tongue` is an OpenViBE/GDF naming reuse; in this dataset it represents rest/idle, not tongue motor imagery.

### Potential Task 1: Motor imagery vs rest with pre-cue context
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.0 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Right` | 0 | Motor imagery of dominant-hand grasping |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle condition |
- **Evidence**:
  - `task-MIvsRest_events.json` - The value column defines `770 = MI` and `772 = Rest` as condition codes.
  - README - RUN1-RUN4 consist of MI vs Rest conditions with kinesthetic imagination of dominant-hand grasping vs rest/idle.
  - Per-run `eeg.json` files - Formal runs are named with task labels such as `MIvsRestRUN1`.
  - EDF annotation audit - `OVTK_GDF_Right` and `OVTK_GDF_Tongue` are present as raw condition cues in formal MI runs.
- **Notes**: This is an alternative epoching strategy using the same condition events as the classical task but a wider window. `tmin = -0.5 s` captures short pre-cue context rather than the full fixation period; the full fixation cross starts earlier in the trial. This task is a candidate extension and should not replace the classical 0.5-2.5 s window supported by the Heliyon analysis.

### Potential Task 2: Fixation cross vs trial end marker classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`OVTK_GDF_Cross_On_Screen`, `OVTK_GDF_End_Of_Trial`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_GDF_Cross_On_Screen` | 0 | Fixation / trial preparation phase onset |
  | `OVTK_GDF_End_Of_Trial` | 1 | Trial end marker |
- **Evidence**:
  - EDF annotation audit - Both markers are directly present in EDF annotations; `OVTK_GDF_Cross_On_Screen` appears 1691 times and `OVTK_GDF_End_Of_Trial` appears 1689 times.
  - 10.1016/j.heliyon.2020.e03425 - The protocol describes fixation before the task cue and a post-task trial/break structure.
- **Notes**: `OVTK_GDF_Feedback_Continuous` is excluded because it is largely co-timed with `OVTK_GDF_End_Of_Trial` in the EDF annotations and this experiment did not provide actual feedback. Treating `Feedback_Continuous` and `End_Of_Trial` as separate classes would risk duplicate windows with conflicting labels.

### Potential Task 3: Baseline vs motor-imagery task state
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`OVTK_GDF_Right`, `OVTK_StimulationId_BaselineStart`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `OVTK_StimulationId_BaselineStart` | 0 | Run-level baseline period onset |
  | `OVTK_GDF_Right` | 1 | Motor imagery cue onset in formal MI runs |
- **Evidence**:
  - README - RUN1-RUN4 consist of MI vs Rest conditions, while baseline periods are marked by `OVTK_StimulationId_BaselineStart` and `OVTK_StimulationId_BaselineStop`.
  - 10.1016/j.heliyon.2020.e03425 - The protocol includes baseline EEG before the stimulation protocol and task cues during trials.
  - EDF annotation audit - `OVTK_StimulationId_BaselineStart` and `OVTK_GDF_Right` are both directly present in EDF annotations.
- **Notes**: This candidate task contrasts run-level baseline onset with active motor-imagery cue onset. The class counts are naturally imbalanced because baseline start appears once per run, whereas `OVTK_GDF_Right` is a trial-level cue. Implementations should restrict `OVTK_GDF_Right` to RUN1-RUN4 to avoid mixing RUN0 actual grasping with formal motor imagery.

### Potential Task 4: Age regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - `participants.tsv` - `age` is a native column with values for all 10 participants.
  - `participants.json` - Defines `age` as participant age with units in years.
- **Notes**: This is a subject-level metadata regression candidate. Labels come directly from the native `participants.tsv` column, so `Label Route = info` and `Meta Level = raw`. Because N = 10 and the age range is narrow, this task should be treated only as a low-sample-size candidate analysis, not as a core benchmark.

### Potential Task 5: Sex/gender classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | Male -> 0; Female -> 1 |
- **Evidence**:
  - `participants.tsv` - `gender` is a native column with values for all 10 participants.
  - `participants.json` - Defines `gender` as participant sex and maps `M` to male and `F` to female.
- **Notes**: This is a subject-level metadata classification candidate. The class distribution is `M` = 6 and `F` = 4. Segmentation creates multiple windows but does not increase the number of independent participants, so segment counts should not be interpreted as independent subject counts.

## Data Quality Notes

- `OVTK_GDF_Tongue` is repurposed from standard GDF nomenclature to indicate the rest/idle condition in this dataset; it should not be interpreted as tongue motor imagery.
- RUN0 is a familiarization run in which `OVTK_GDF_Right` marks actual dominant-hand grasping. Formal MI vs rest tasks should use RUN1-RUN4 or explicitly filter RUN0.
- Data in Brief and Heliyon both state that no actual feedback was presented. `OVTK_GDF_Feedback_Continuous` is therefore a protocol phase marker, and `OVTK_GDF_Correct` / `OVTK_GDF_Incorrect` should not be used as feedback correctness labels.
- `OVTK_GDF_Correct` and `OVTK_GDF_Incorrect` often co-occur at the same annotation onset, which further prevents their use as a correct-vs-incorrect feedback classification target.
- `OVTK_GDF_Feedback_Continuous` is largely co-timed with `OVTK_GDF_End_Of_Trial`; using them as separate target classes may create duplicate windows with conflicting labels.
- The dataset is small: 10 participants and 50 EEG EDF files. Age and sex/gender tasks are subject-level metadata candidates and have limited statistical power.
- Event counts show a slight imbalance between `OVTK_GDF_Start_Of_Trial` / `OVTK_GDF_Cross_On_Screen` and `OVTK_GDF_End_Of_Trial` / `OVTK_GDF_Feedback_Continuous`, indicating minor annotation boundary irregularities.
- The numeric code mapping in `task-MIvsRest_events.json` records `770 = MI` and `772 = Rest`; the EDF annotations expose OVTK description strings, and the `OVTK_GDF_Right` / `OVTK_GDF_Tongue` MI-rest mapping is confirmed by the Data in Brief paper.
- The EEG device model is documented in the Data in Brief paper but is not repeated in each per-run `eeg.json`.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
