# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50 | **Channels**: 15 | **Sampling Rate**: 125 Hz
**Manual Review**:

## Paradigm

Participants performed kinesthetic motor imagery of grasping movements with the dominant hand during EEG recording using a low-cost consumer-grade EEG system. Sessions included a preliminary run of actual hand movements followed by motor imagery blocks alternating with resting-state baselines. OpenViBE (OVTK) event triggers mark trial onset, cue type, feedback, and session boundaries. The study evaluates BCI performance using motor imagery and demonstrates applicability of affordable EEG hardware.

## File Scan Result

> **Kernel SHA256**: `241a47b9b12f941e8d556583cd5a833918f0d288d0c8e6ec817b61cb30ed92fb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `OVTK_GDF_Correct` | 697 | event | raw | Trial phase onset: correct feedback |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Trial phase onset: fixation cross displayed |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session boundary: end of session marker |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial phase onset: trial end |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | Trial phase onset: continuous feedback period |
| `OVTK_GDF_Incorrect` | 697 | event | raw | Trial phase onset: incorrect feedback |
| `OVTK_GDF_Right` | 845 | event | raw | Trial phase onset: right hand cue |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial phase onset: trial start |
| `OVTK_GDF_Tongue` | 845 | event | raw | Trial phase onset: tongue cue |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Trial phase onset: baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Trial phase onset: baseline period end |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Trial phase onset: auditory beep cue |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Session boundary: experiment start |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Session boundary: experiment stop |
| `OVTK_StimulationId_Train` | 48 | admin | raw | Session boundary: training/calibration marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class motor imagery vs rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Right` | 0 | right hand motor imagery cue |
  | `OVTK_GDF_Tongue` | 1 | rest/idle condition cue (tongue cue used as rest proxy) |
- **Evidence**:
  - 10.1016/j.dib.2022.108225 — Data in Brief companion paper explicitly states tmin=0.5s, tmax=2.5s for motor imagery vs rest classification; 845 balanced trials per class using right hand MI and rest conditions
  - 10.1016/j.heliyon.2020.e03425 — Original Heliyon feasibility study describing the low-cost 15-channel EEG BCI system with MI vs Rest paradigm using filter-bank CSP
- **Notes**: The task uses OVTK_GDF_Right as motor imagery class and OVTK_GDF_Tongue as the rest/idle class. The README confirms the protocol consists of "kinesthetic imagination of grasping movement (MI) of the dominant hand and rest/idle condition." The task-MIvsRest_events.json indicates value 770='MI' and 772='Rest', but the actual embedded EDF annotations use OVTK_GDF_Right (845 occurrences) and OVTK_GDF_Tongue (845 occurrences) as the class cues, which are perfectly balanced. The OVTK_GDF_Tongue event serves as the rest condition marker in this annotation scheme, consistent with the experimental design where participants alternate between MI and rest periods.

### Classical Task 2: 2-class motor imagery vs rest (alternative: Right=MI, Tongue=rest with standard BCI window)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 3 s *, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | OVTK_GDF_Right | 0 | Motor imagery: right hand grasping |
  | OVTK_GDF_Tongue | 1 | Rest/idle condition (tongue cue used as rest proxy) |
- **Evidence**:
  - 10.1016/j.heliyon.2020.e03425 — Same task as classical MI vs rest but with standard BCI Competition epoch window (tmin=0, tmax=3-4s) since original Heliyon paper did not specify exact timing. Uses OVTK_GDF_Right as motor imagery and OVTK_GDF_Tongue as rest. Filter-bank CSP approach mentioned.
- **Notes**: The original task-MIvsRest_events.json specifies value levels 770='MI'/772='Rest' which do not match the actual OVTK_GDF annotation scheme found in EDF files. Based on the README description of two conditions (kinesthetic imagination of grasping movement of dominant hand and rest/idle condition), OVTK_GDF_Right (right hand cue) is mapped to motor imagery (y=0) and OVTK_GDF_Tongue is used as the rest/idle proxy (y=1). Both events occur 845 times each, perfectly balanced. The epoch window (tmin=0, tmax=3s) is inferred from standard BCI Competition MI protocols as the original paper lacks explicit timing. Run-0 is excluded as it involves real movement, not motor imagery.

### Potential Task 1: 3-class MI vs rest vs feedback state
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2.5 s *, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`, `OVTK_GDF_Feedback_Continuous`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Right` | 0 | Motor imagery: right hand cue |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle: tongue cue (used as rest condition in MI vs Rest protocol) |
  | `OVTK_GDF_Feedback_Continuous` | 2 | Online BCI feedback period |
- **Evidence**:
  - `sub-02_task-MIvsRest_run-1_eeg.edf` header annotations — confirms co-occurrence of `OVTK_GDF_Tongue`, `OVTK_GDF_Feedback_Continuous`, and `OVTK_GDF_Correct`/`OVTK_GDF_Incorrect` in actual runs; `OVTK_GDF_Right` and `OVTK_GDF_Tongue` are balanced task cues (845 occurrences each); `OVTK_GDF_Feedback_Continuous` marks continuous feedback with 1689 occurrences
  - README — describes MI vs Rest protocol with kinesthetic imagination of grasping movement of dominant hand and rest/idle condition; RUN1-RUN4 are equal, consisting of MI vs. Rest conditions
  - `task-MIvsRest_events.json` — specifies value levels 770='MI'/772='Rest' confirming the two-condition protocol structure, though actual annotation stream uses OVTK_GDF codes
- **Notes**: The tongue cue (`OVTK_GDF_Tongue`) serves as the rest/idle condition in this MI vs Rest protocol, as confirmed by the balanced 845/845 occurrence counts with right hand MI cue and the dataset's stated two-condition design. The feedback continuous event captures the online BCI operation state, creating a novel 3-class formulation not explicitly proposed in source literature. Epoch window inferred from midpoint between classical 0.5-2.5s and standard 0-3s approaches.

### Potential Task 2: Feedback Correctness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`OVTK_GDF_Correct`, `OVTK_GDF_Incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Correct` | 0 | Correct feedback (BCI decoded intention correctly) |
  | `OVTK_GDF_Incorrect` | 1 | Incorrect feedback (BCI decoded intention incorrectly) |
- **Evidence**:
- **Notes**: Balanced binary classification (697 each) of BCI feedback outcomes. Epoch window centered on feedback onset with negative tmin to capture pre-feedback anticipatory activity and positive tmax for post-feedback ERP. Not classical due to lack of published task using these specific markers; represents a derived performance-monitoring paradigm from the MI task structure.

### Potential Task 3: Trial Phase Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 1 s *, target_events = [`OVTK_GDF_Start_Of_Trial`, `OVTK_GDF_Cross_On_Screen`, `OVTK_GDF_Feedback_Continuous`, `OVTK_GDF_End_Of_Trial`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Start_Of_Trial` | 0 | Trial phase onset: trial start |
  | `OVTK_GDF_Cross_On_Screen` | 1 | Trial phase onset: fixation cross displayed |
  | `OVTK_GDF_Feedback_Continuous` | 2 | Trial phase onset: continuous feedback period |
  | `OVTK_GDF_End_Of_Trial` | 3 | Trial phase onset: trial end |
- **Evidence**:
- **Notes**: Four distinct trial phase markers form a multi-class classification of BCI trial structure. Phase markers indicate instantaneous state transitions; short 1-second epochs capture the neural signature at each trial phase onset. The 0.5-second tmin/tmax values are inferred from the paradigm structure (phase transitions) and are marked with *. Note: OVTK_GDF_Right and OVTK_GDF_Tongue (845 occurrences each, perfectly balanced) are motor imagery cue events, not trial phase markers, and are excluded from this phase-detection task per binding rules. OVTK_GDF_Correct/Incorrect are feedback outcome markers with different occurrence counts (697 each) and are also excluded as they represent performance feedback rather than trial phase structure.

### Potential Task 4: Baseline vs Task State
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, target_events = [`OVTK_StimulationId_BaselineStart`, `OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_StimulationId_BaselineStart` | 0 | rest baseline period |
  | `OVTK_GDF_Right` | 1 | active task period (motor imagery cue) |
  | `OVTK_GDF_Tongue` | 1 | active task period (motor imagery cue) |
- **Evidence**:
- **Notes**: Both motor imagery cues (Right, Tongue) are merged into a single active task class (y=1) to form a binary rest-vs-task discrimination. The OVTK_StimulationId_BaselineStart marks inter-run rest periods (50 occurrences), while OVTK_GDF_Right and OVTK_GDF_Tongue mark active motor imagery task periods (845 each, 1690 total). This creates a severely imbalanced but fundamentally valid neural state classification. Epoch window length of 3s matches standard motor imagery analysis windows for comparability; values are inferred from task context.

### Potential Task 5: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–30.0 (years) | Narrow 10-year span; all subjects right-handed; N=10 limits statistical power |
- **Evidence**:
  - participants.tsv — age column: complete numeric data for N=10 subjects, range 20–30 years
  - dataset_description.json — "A feasibility study of a complete low-cost consumer-grade brain-computer interface system" (Peterson et al., 2020, Heliyon)
- **Notes**: Segmentation-based approach for subject-level trait prediction. No event structure is leveraged; 4-second windows with 50% overlap provide sufficient samples per subject for regression while preserving spectral content relevant to age-related EEG markers. The narrow age range (20–30 years) in this young-adult cohort limits predictive power but serves as proof-of-concept for biomarker extraction from low-cost EEG hardware.

### Potential Task 6: Gender Classification from Continuous EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | Male |
  | gender | F | 1 | Female |
- **Evidence**:
- **Notes**: Binary demographic classification from 4-second non-overlapping sliding windows of continuous EEG. Small imbalanced sample (N=10, 6M/4F) with 15-channel low-cost device. Standard segmentation approach for subject-level trait prediction; 50% overlap increases effective sample size for training. Gender values derived from participants.tsv native info column.

### Potential Task 7: Continuous EEG Segmentation with Age Label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0 – 30.0 (years) | Subject-level chronological age; continuous segmentation treats each 2s window as a sample with shared subject-level label. N=10 subjects with age range 20–30 years. |
- **Evidence**:
- **Notes**: Archetype C with info-native label: continuous 2-second non-overlapping segmentation of the full EEG recording (including rest baseline periods, inter-trial intervals, and task periods) without event-locked structure. The kernel does not need to compute any derived channels; age is read directly from participants.tsv. This formulation maximizes sample count from the limited 10-subject dataset for age-prediction biomarker evaluation using trait-relevant spectral features in non-task and task-contaminated periods alike. segment_length=2s and overlap=0.0 are inferred from the epoch_hint to increase sample count given small N.

## Data Quality Notes

- `device` field is missing across all files; equipment metadata must be inferred from dataset documentation (low-cost consumer-grade 15-channel EEG system).
- Event annotation scheme uses OVTK_GDF codes rather than the numeric value levels (770/772) specified in `task-MIvsRest_events.json`, creating a documentation-annotation mismatch that requires manual reconciliation.
- `OVTK_GDF_Tongue` is used as the rest/idle condition marker despite its label suggesting tongue motor imagery; this semantic mismatch is confirmed by balanced trial counts (845/845) and README protocol description but may confuse users expecting standard BCI tongue motor imagery.
- Run-0 involves actual hand movement rather than motor imagery and must be excluded from MI analyses per original study design.
- Small sample size (N=10 subjects, 50 files) limits statistical power and generalizability of findings.
- Narrow age range (20–30 years) restricts demographic diversity and age-related biomarker detection sensitivity.
- Dominant hand information is complete but all subjects are right-handed, eliminating handedness as a variable of interest.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
