# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: 14 | **Files (Completed)**: 38 | **Channels**: 65 | **Sampling Rate**: 1450 Hz | **Manual Review**:

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) of the ventral capsule/ventral striatum (VCVS) was toggled ON or OFF. The study investigates how VCVS-DBS modulates prefrontal cortex activity during cognitive control and emotional processing. Clinical outcomes were tracked using MADRS depression severity scales and responder status. EEG was recorded at 1450 Hz from 65 channels across multiple sessions per subject.

## File Scan Result

> **Kernel SHA256**: `97e1ccfdf964187e12fb09d66ab06a119e6b48de47d328b7186ab0e92bdaac5e`
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
| `age` | complete | N/A |
| `sex` | complete | N/A |
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
