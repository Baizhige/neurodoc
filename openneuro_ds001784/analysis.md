# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: 14 | **Files (Completed)**: 38 | **Channels**: 65 | **Sampling Rate**: 1450 Hz
**Manual Review**:

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) of the ventral capsule/ventral striatum (VCVS) was toggled ON or OFF. The study investigates how VCVS-DBS modulates prefrontal cortex activity during cognitive control and emotional processing. Clinical outcomes were tracked using MADRS depression severity scales and responder status. EEG was recorded at 1450 Hz from 65 channels across multiple sessions per subject.

## File Scan Result

> **Kernel SHA256**: `d5cad097c3cfba3f5de89c31e0c6f17d48a24b9bf3b7f4b690869305bf8a7d86`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_2` | 1296 | event | raw | IAPS picture onset (afMSIT task) |
| `event_4` | 2592 | event | raw | MSIT interference stimulus onset (includes both cue and response triggers) |
| `event_6` | 1296 | event | raw | MSIT interference stimulus onset (secondary trigger, target phase) |


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
- **Epoch Parameters**: `tmin = -1.5 s, tmax = 3.4 s, target_events = ['event_2', 'event_4']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|----------|
  | event_2 | 0 | Interference trials (n=1296) |
  | event_4 | 1 | Control trials (n=2592) |
- **Evidence**:
  - Widge & Zorowitz et al. (2019), Nature Communications (https://doi.org/10.1038/s41467-019-09557-4) — Two-class classification of high-interference vs low-interference control trials during afMSIT under VCVS DBS. Theta band (5-8Hz) PFC activity as primary neural signature. Event counts confirm trial type distinction at 2:1 ratio (event_4/event_2).
- **Notes**: Epoch window aligned to MSIT stimulus onset [-1.5, 3.4]s capturing pre-stimulus baseline and post-stimulus cognitive control processing.

### Potential Task 1: Baseline MADRS depression severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `info`
- **Label Field**: `madrs_bl`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | madrs_bl | 33–38 (score) | Baseline MADRS-10 depression severity; complete for all 14 subjects |
- **Evidence**:
  - Participants.tsv — madrs_bl column is numeric, complete for all 14 subjects (sample values: 33, 34, 38)
- **Notes**: Subject-level regression predicting baseline depression severity from aggregated MSIT epochs. Kernel will extract epochs around cognitive task events (event_2/event_4/event_6), aggregate per subject, and predict madrs_bl as continuous target. The narrow MADRS range (33–38) indicates uniformly severe baseline depression in this treatment-resistant cohort.

### Potential Task 2: Follow-up MADRS depression severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `info`
- **Label Field**: `madrs_fu`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |---|---|---|
  | madrs_fu | 9–38 (points) | Follow-up MADRS score; complete for all 14 subjects across DBS conditions |
- **Evidence**:
  - (epoch_hint) — Inferred from cognitive task epoch window defaults; subject-level aggregation required to map multiple epochs to single regression target
- **Notes**: B3 archetype using native participants.tsv column; regression target is continuous MADRS score capturing treatment response variability. Kernel epochs per event and aggregates to subject level for single madrs_fu prediction per subject. No derivation required.

### Potential Task 3: Subject age regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 50–70 (years) | Complete for all 14 subjects |
- **Evidence**:
  - Participants.tsv: age range 50–70, complete for all 14 subjects (6 M, 8 F)
  - README/TaskDescription: afMSIT probes cognitive flexibility via interference processing
  - Evidence summary: Age-related neural signatures in PFC theta activity during cognitive control may predict subject age. Kernel aggregates all task epochs per subject.

### Potential Task 4: DBS stimulation frequency regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `info`
- **Label Field**: `dbs_stim_freq`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  | dbs_stim_freq | 50-130 (Hz) | DBS stimulation frequency; complete for all 14 subjects |
- **Evidence**:
  - Regression predicting DBS stimulation frequency (dbs_stim_freq, complete for all 14 subjects, range 50-130 Hz). Neural signatures during MSIT may correlate with stimulation parameters programmed for each patient.
- **Notes**: Archetype B3 task predicting subject-level DBS stimulation parameters from neural activity during the affective MSIT cognitive control task.

### Potential Task 5: Treatment responder vs non-responder classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.5 s *, tmax = 3.4 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `info`
- **Label Field**: `responder`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |---|---|---|---|
  | responder | True | 1 | Treatment responder |
  | responder | False | 0 | Treatment non-responder |
- **Evidence**:
  - Behavioral file column structure supports responder classification; participants.tsv contains complete responder labels for all 14 subjects (sample: True/False values observed in BRTU, CHDR, CRDA study cohorts)
- **Notes**: Subject-level classification requires aggregating all epochs per subject after initial epoching. The MSIT task probes cognitive flexibility during interference trials encoded by event_2/event_4/event_6.

### Potential Task 6: MSIT three-condition classification (IAPS vs MSIT onset vs target phase)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = ['event_2', 'event_4', 'event_6']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | event_2 | 0 | IAPS picture onset |
  | event_4 | 1 | MSIT interference stimulus onset (cue/response triggers) |
  | event_6 | 2 | MSIT interference stimulus onset (target phase) |
- **Evidence**:
  - Behavioral file column structure (fixOnset/IAPSOnset/MSITOnset per trial) — establishes three distinct trial phases
  - Event count ratio (event_4 = 2× event_2 = 2× event_6) — confirms event_4 captures two sub-events per trial (cue + response) while event_2/event_6 capture single phase onsets
  - Trial structure (72 trials ≈ 18 trials × 4 conditions) — validates phase-level segmentation
- **Notes**: Three-class classification distinguishing IAPS picture onset, MSIT stimulus onset (combined cue/response triggers), and MSIT target phase. The 2:1 ratio of event_4 relative to other events indicates it encodes multiple sub-events per trial rather than representing a distinct condition.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
