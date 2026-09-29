# Motor Imagery vs Rest in Consumer-Grade EEG for BCI Feasibility

**Dataset**: `ds003810` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 46 | **Channels**: 15 | **Sampling Rate**: 125 Hz | **Manual Review**:

## Paradigm

This dataset investigates the feasibility of using a low-cost consumer-grade EEG system for motor imagery-based brain-computer interfaces. Ten healthy subjects (age 20-30, 6 male, 4 female) performed a modified Graz protocol consisting of motor imagery (dominant hand grasping imagination) and rest/idle conditions. Each subject completed one training run (RUN0 with real movement) followed by four motor imagery runs (RUN1-RUN4) with 20 trials per condition per run. EEG was recorded with 15 channels using an OpenBCI-based system at 125 Hz sampling rate. Visual cues (right hand or tongue/rest) were presented on screen, followed by continuous feedback and correct/incorrect feedback markers.

## File Scan Result

> **Kernel SHA256**: `2b7a47bc771270e9496e1f82087f3e11a7b8612fc1ccb4981f1084a51031ae24`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `OVTK_GDF_Correct` | 697 | event | raw | Trial phase onset: correct feedback |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Trial phase onset: fixation cross |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session boundary: end of session |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial phase onset: trial end |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | Trial phase onset: continuous feedback |
| `OVTK_GDF_Incorrect` | 697 | event | raw | Trial phase onset: incorrect feedback |
| `OVTK_GDF_Right` | 845 | event | raw | Trial phase onset: right cue |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial phase onset: trial start |
| `OVTK_GDF_Tongue` | 845 | event | raw | Trial phase onset: tongue cue |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Trial phase onset: baseline start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Trial phase onset: baseline stop |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Trial phase onset: auditory beep cue |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Session boundary: experiment start |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Session boundary: experiment stop |
| `OVTK_StimulationId_Train` | 48 | admin | raw | System marker: training run indicator |

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Classical Task 1: 2-class motor imagery vs rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Right` | 0 | Right hand motor imagery cue |
  | `OVTK_GDF_Tongue` | 1 | Rest/idle condition cue (tongue cue used as rest marker in protocol) |
- **Evidence**:
  - 10.1016/j.dib.2022.108225 — Modified Graz protocol with 2 conditions: motor imagery (grasping of dominant hand) and rest/idle; 20 trials per condition per run, 4 MI runs (RUN1-RUN4), 15 EEG channels at 125 Hz
  - 10.1016/j.heliyon.2020.e03425 — Feasibility study of low-cost consumer-grade BCI system; RUN0 with real movement excluded from MI analysis; task-MIvsRest_events.json defines value 770 as "MI" and 772 as "Rest"
- **Notes**: The task-MIvsRest_events.json sidecar explicitly maps value 770 to "MI" and 772 to "Rest", confirming the two-class structure. OVTK_GDF_Right serves as the motor imagery cue (dominant hand grasping imagination) while OVTK_GDF_Tongue serves as the rest/idle condition cue in this modified protocol. The epoch window 0-4s post-cue is inferred from standard Graz-style MI timing as no explicit window is specified in the references.

### Potential Task 1: age regression from resting segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | continuous age in years (20–30 range) |
- **Evidence**:
  - participants.tsv — age column present for all 10 subjects, range 20–30 years
- **Notes**: Segmentation-based resting-state regression. 2-second non-overlapping segments are used to create multiple samples per recording; each segment inherits the subject's age from participants.tsv. Baseline periods (BaselineStart/BaselineStop) exist in the data but are not used as event anchors due to the segmentation approach. Segment length inferred from typical short-rest analysis windows; overlap set to 0 for independent samples.

### Potential Task 2: Gender Classification from Resting Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | gender | M → 0 (male, N=6); F → 1 (female, N=4) |
- **Evidence**:
- **Notes**: Segmentation-based approach required because no event structure discriminates gender. The 2-second non-overlapping segments are inferred from the resting-state paradigm with ~447s runs and 10 subjects, yielding sufficient samples for binary classification. Gender labels are drawn from participants.tsv, a native info field.

### Potential Task 3: age regression from MI epochs
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`OVTK_GDF_Right`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (range 20–30), broadcast per-subject to all MI epochs. Each epoch from a given subject receives the same age value. |
- **Evidence**:
- **Notes**: Uses native participants.tsv `age` column (B3 archetype, Meta Level = raw). Epoch window inferred from classical MI task paradigm. Age range is narrow (20–30 years) but provides non-trivial variance for regression across 10 subjects. The `OVTK_GDF_Right` event marks right-hand motor imagery cue onset; epochs are extracted around these cues and paired with subject-level age labels.

### Potential Task 4: Age Regression from Rest Epochs
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`OVTK_GDF_Tongue`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (20–30), broadcast from participants.tsv to all rest epochs per subject |
- **Evidence**:
- **Notes**: This task uses OVTK_GDF_Tongue events as rest condition markers (the dataset's events.json maps value 772 to "Rest", and the README describes RUN1-RUN4 as MI vs. Rest conditions). The epoch window is inferred from the classical MI task parameters. Age is a native participants.tsv field, making this a B3 (info-native) archetype with Meta Level = raw. The task is complementary to MI-age regression to test whether rest-state EEG carries age-predictive information comparable to task-state EEG.

## Data Quality Notes

- Low channel count (15 channels) and low sampling rate (125 Hz) limit spectral resolution and spatial coverage compared to research-grade EEG systems.
- Consumer-grade OpenBCI hardware may introduce higher noise levels and lower signal quality than clinical or research amplifiers; feasibility study design means data quality is explicitly a variable of interest.
- RUN0 (training run with real movement) is excluded from motor imagery analysis per the referenced protocol, which may reduce available data if not properly filtered.
- Event count imbalance: OVTK_GDF_Right (845) vs OVTK_GDF_Tongue (845) are balanced, but Correct (697) vs Incorrect (697) feedback counts suggest some trials may be missing feedback markers or were excluded.
- Small sample size (N=10) limits generalizability for subject-level prediction tasks such as age regression and gender classification.
- Narrow age range (20-30 years) compresses variance for age regression tasks, potentially reducing model performance and ecological validity.
- Baseline periods (50 start/stop pairs) do not perfectly align with trial counts, suggesting possible inconsistencies in baseline marking across runs or subjects.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
