# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: 14 | **Files (Completed)**: 38 | **Channels**: 65 | **Sampling Rate**: 1450 Hz | **Manual Review**:

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) of the ventral capsule/ventral striatum (VCVS) was toggled ON or OFF. The study investigates how VCVS-DBS modulates prefrontal cortex activity during cognitive control and emotional processing. Clinical outcomes were tracked using MADRS depression severity scales and responder status. EEG was recorded at 1450 Hz from 65 channels across multiple sessions per subject.

## File Scan Result

> **Kernel SHA256**: `488b4b0485c2f75a4a5565ec7262d1b1e3f90e28befead3622af1ad005dc9bc2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_2` | 1296 | event | raw | MSIT stimulus onset: control condition |
| `event_4` | 2592 | event | raw | IAPS image onset |
| `event_6` | 1296 | event | raw | MSIT stimulus onset: interference condition |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: MSIT interference vs control classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.4 s, target_events = [`event_2`, `event_6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_2` | 0 | MSIT stimulus onset: control condition |
  | `event_6` | 1 | MSIT stimulus onset: interference condition |
- **Evidence**:
  - 10.1038/s41467-019-09557-4 — Direct evidence from primary paper. 2-class classification of MSIT interference (event_6, n=1296) vs control (event_2, n=1296) trials during afMSIT under VCVS DBS. Theta band (5-8Hz) PFC activity as primary neural signature.
- **Notes**: Event ID mapping corrected from original analysis.md: locked ground truth confirms event_2=control, event_4=IAPS onset, event_6=interference. Valid 2-class task uses event_2 vs event_6. Epoch window [-1.5, 3.4]s explicitly stated in primary paper, aligned to MSIT stimulus onset.

### Potential Task 1: MSIT stimulus vs IAPS image onset classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_2` | 0 | MSIT control onset |
  | `event_4` | 1 | IAPS image onset |
  | `event_6` | 2 | MSIT interference onset |
- **Evidence**:
  - (none — potential task inferred from event structure)
- **Notes**: Three-class classification of task phase onsets in the afMSIT paradigm. event_2 and event_6 represent the two MSIT conditions (control and interference), while event_4 represents IAPS image presentation. The 1:2:1 count ratio (1296:2592:1296) reflects that IAPS images are shown on all trials, while MSIT stimuli split equally between conditions. Epoch window inferred from classical MSIT task parameters; may need adjustment for IAPS processing dynamics.

### Potential Task 2: 3-class MSIT task phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_4` | 0 | IAPS image onset |
  | `event_2` | 1 | MSIT stimulus onset: control condition |
  | `event_6` | 2 | MSIT stimulus onset: interference condition |
- **Evidence**:
  - task-afmsit_beh.json — describes trial structure with IAPSOnset, MSITOnset, and interference levels (0=control, 1=interference)
  - behavioral TSVs (sub-01/02/04/09/14_task-afmsit_acq-{dbsoff,dbson}_beh.tsv) — confirms fixation→IAPS image→MSIT stimulus sequence with ~50% control/interference split
  - Event count ratio 1296:2592:1296 (event_2:event_4:event_6) — matches IAPS onset on all trials and MSIT conditions split equally
- **Notes**: This task distinguishes three phases of the affective MSIT trial structure: IAPS image presentation (emotional priming), MSIT control trials, and MSIT interference trials. The epoch window captures pre-stimulus baseline (-1.5s) and post-onset cognitive-affective processing (3.4s). Event meanings inferred from behavioral file structure and event count ratios, as no explicit event ID mapping was found in sidecar files.

### Potential Task 3: MADRS baseline severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `info`
- **Label Field**: `madrs_bl`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | madrs_bl | 33–38 (score) | Montgomery-Åsberg Depression Rating Scale baseline total score; continuous numeric range across N=14 subjects; lower scores indicate less severe depression |
- **Evidence**:
  - participants.tsv — `madrs_bl` column: complete numeric data for all 14 subjects, range 33–38
  - task-afmsit_beh.json — describes afMSIT trial structure with MSITOnset and IAPSOnset events
  - behavioral TSVs (sub-01/02/04/09/14_task-afmsit_acq-{dbsoff,dbson}_beh.tsv) — confirm fixation→IAPS image→MSIT stimulus sequence
  - events.tsv/event count ratio (1296:2592:1296) — matches IAPS onset on all trials and MSIT conditions split equally
  - Widge et al. (2019) Nature Communications — primary study reference describing afMSIT task and clinical outcomes
- **Notes**: Archetype B3 (info-native). The `madrs_bl` field is a pre-existing participants.tsv column requiring no kernel derivation. All three event types (event_2 control MSIT, event_4 IAPS image, event_6 interference MSIT) are used as epoch anchors to maximize trial coverage for depression severity biomarker regression. Epoch window inferred from classical task parameters.

### Potential Task 4: MADRS follow-up severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `info`
- **Label Field**: `madrs_fu`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | madrs_fu | 9–38 (score) | Montgomery-Åsberg Depression Rating Scale follow-up score; continuous numeric range with wider variance than baseline (9-38 vs 33-38); post-DBS treatment state; N=14 complete |
- **Evidence**:
  - participants.tsv — `madrs_fu` column present with complete data for all 14 subjects; values range 9–38
  - task-afmsit_beh.json — describes trial structure with MSIT and IAPS components corresponding to event_2, event_4, event_6
  - Widge et al. 2019 (Nature Communications) — DBS effects on cognitive control in treatment-resistant depression; MADRS used as primary clinical outcome measure
- **Notes**: B3 archetype using native participants.tsv column. All three event types (control MSIT, IAPS image, interference MSIT) are epoched to capture neural signatures during cognitive-affective task performance that may predict follow-up depression severity. The epoch window (-1.5 to 3.4s) is inferred from the classical task configuration and provides coverage of anticipatory and early evoked responses.

### Potential Task 5: DBS Responder Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `info`
- **Label Field**: `responder`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | responder | True | 0 | DBS responder (clinical improvement) |
  | responder | False | 1 | DBS non-responder (no clinical improvement) |
- **Evidence**:
  - participants.tsv — `responder` column contains complete binary labels (True/False) for all 14 subjects; 7 responders and 7 non-responders forming balanced classes
  - Widge et al. (2019) Nature Communications — primary study reporting DBS effects on cognitive control in treatment-resistant depression; responder status is the main clinical endpoint alongside MADRS scores
  - task-afmsit_beh.json / behavioral TSVs — confirm afMSIT paradigm with event_2 (MSIT control onset), event_4 (IAPS image onset), event_6 (MSIT interference onset) providing neural epochs for responder prediction
- **Notes**: Binary classification of deep brain stimulation treatment response using EEG activity during cognitive control task (afMSIT). All three event types are pooled to capture neural signatures across control, interference, and affective processing conditions that may distinguish responders from non-responders. Epoch window defaults to same range as classical motor imagery tasks (-1.5 to 3.4s) as no study-specific timing was specified.

### Potential Task 6: Age regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 30–70 (years) | Continuous age values across 14 subjects; substantial 40-year span for regression despite small sample size |
- **Evidence**:
  - participants.tsv — N=14 subjects with complete age data (30.0–70.0 years, mean ~54.3)
  - task-afmsit_beh.json — describes afMSIT trial structure with MSIT stimulus onsets and IAPS image onsets matching event_2, event_4, event_6
  - behavioral TSVs (sub-01/02/04/09/14) — confirm fixation→IAPS image→MSIT stimulus sequence with ~50% control/interference split matching 1:2:1 event count ratio
- **Notes**: Uses all three event types (IAPS image onset, MSIT control onset, MSIT interference onset) to capture age-related neural dynamics across the full afMSIT task. Age is a native participants.tsv column requiring no kernel derivation. Small sample size (N=14) limits statistical power but 40-year age range provides meaningful regression signal.

### Potential Task 7: DBS stimulation frequency regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]`
- **Label Route**: `info`
- **Label Field**: `dbs_stim_freq`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | dbs_stim_freq | 50–130 (Hz) | Deep brain stimulation frequency parameter, varies across subjects (complete for N=14) |
- **Evidence**:
- **Notes**: Native info field from participants.tsv. The DBS stimulation frequency is a continuous numeric parameter (50–130 Hz) that characterizes the stimulation setting for each subject. All three event types (MSIT control, IAPS image, MSIT interference) are epoched and regressed against this subject-level parameter to identify neural correlates of DBS frequency modulation during cognitive-affective task performance.

### Potential Task 8: Hypomania status classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]`
- **Label Route**: `info`
- **Label Field**: `hypomania`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | hypomania | False | 0 | No hypomania adverse effect |
  | hypomania | True | 1 | Hypomania adverse effect present |
- **Evidence**:
- **Notes**: This is a B3 archetype task using native info field `hypomania` from participants.tsv. The label is categorical with partial completeness (13/14 subjects). Despite severe class imbalance (majority False, one True subject), this represents a clinically relevant adverse effect of DBS stimulation. All three task events (event_2 control MSIT, event_4 IAPS image, event_6 interference MSIT) are used as epoching anchors to capture neural signatures across the full affective-cognitive interference paradigm. The epoch window (-1.5 to 3.4s) is inferred from the classical task configuration.

### Potential Task 9: Gender classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | Male |
  | gender | F | 1 | Female |
- **Evidence**:
  - participants.tsv — 14 subjects with complete gender information (6 male, 8 female)
- **Notes**: This is a B3 archetype task using native participants.tsv column. The epoch window is inferred from the classical task parameters. All three event types (IAPS onset, MSIT control, MSIT interference) are pooled as trial anchors, with gender labels applied from the info table. Small sample size (N=14) limits generalizability but provides a proof-of-concept baseline for sex classification from EEG.

### Potential Task 10: Resting state segmentation with MADRS severity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `madrs_bl`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | madrs_bl | 33–38 (score) | Montgomery-Åsberg Depression Rating Scale, baseline assessment; complete across N=14 subjects; higher scores indicate greater depression severity |
- **Evidence**:
  - participants.tsv — `madrs_bl` column contains baseline MADRS scores (range 33-38) for all 14 subjects, complete data
  - README — resting state data referenced with citation to Widge et al. (2016) on ventral capsule/ventral striatum DBS and occipital cross-frequency coupling
  - eeg.json — `TaskName: afmsit` for task data; rest condition described in dataset as "Quiet rest with EYES OPEN" per evidence summary
- **Notes**: Archetype C with native info column. Segmentation-based approach required because resting state recordings have no task events. The 2-second segment length with 50% overlap is a standard default for resting state EEG analysis when no event triggers are available; marked as inferred due to absence of explicit protocol specification in available sidecars.

### Potential Task 11: Resting state segmentation with responder status
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `responder`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | responder | True | 1 | DBS responder |
  | responder | False | 0 | DBS non-responder |
- **Evidence**:
- **Notes**: Segmentation-based task using continuous resting state EEG (task-rest, eyes open) with no event triggers. Fixed 2-second windows with 50% overlap create epochs. Binary classification uses participants.tsv 'responder' field (7 True, 7 False — balanced). Meta Level is raw because 'responder' is a native pre-existing column in participants.tsv.

### Potential Task 12: YBOCS baseline severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `info`
- **Label Field**: `ybocs_bl`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | ybocs_bl | 31.0–34.0 | Y-BOCS baseline severity score; only 2 of 14 subjects have non-missing values (OCD subjects only); extreme sparsity limits viability |
- **Evidence**:
  - participants.tsv — ybocs_bl column present with numeric values for OCD subjects (31.0, 34.0); 2/14 complete
- **Notes**: Native B3 task using pre-existing participants.tsv column. No kernel derivation needed. Despite extreme sparsity (only 2 subjects with data), included for completeness as OCD is in the diagnostic mix of this depression-focused dataset. The epoch window is inferred from the classical task structure and targets neural correlates during the affective MSIT paradigm.

## Data Quality Notes

- Event ID mapping was corrected from original analysis.md draft: event_2=control MSIT, event_4=IAPS image onset, event_6=interference MSIT. The original draft incorrectly mapped event_4 as control trials and event_2 as IAPS picture onset.
- Classical task now correctly uses event_2 vs event_6 for MSIT control vs interference classification, matching the primary paper's 2-class design.
- Small sample size (N=14 subjects, 38 completed files) limits statistical power and generalizability for all machine learning tasks.
- Device information is completely missing from info metadata, preventing equipment-specific quality assessments.
- YBOCS scores (ybocs_bl, ybocs_fu) are severely incomplete (2/14 subjects), making associated regression tasks non-viable for practical use.
- Hypomania label has partial completeness (13/14) and severe class imbalance (only 1 positive case), limiting classification reliability.
- Baseline MADRS range is extremely narrow (33–38), indicating a uniformly severe depression cohort with minimal variance for regression.
- Resting state tasks rely on inferred segmentation parameters (2s windows, 50% overlap) as no explicit protocol was found in sidecar files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
