# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50 | **Channels**: 15 | **Sampling Rate**: 125 Hz
**Manual Review**:

## Paradigm

Participants performed kinesthetic motor imagery of grasping movements with the dominant hand during EEG recording using a low-cost consumer-grade EEG system. Sessions included a preliminary run of actual hand movements (RUN0) followed by motor imagery blocks alternating with resting-state baselines (RUN1-RUN4). OpenViBE (OVTK) event triggers mark trial onset, cue type, feedback, and session boundaries. The study evaluates BCI performance using motor imagery and demonstrates applicability of affordable EEG hardware.

## File Scan Result

> **Kernel SHA256**: `1c1ce2b498db2c62a25bae192b266f958d71e5bfc606f104f1c535ac01bbd383`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `OVTK_GDF_Correct` | 697 | event | raw | Correct classification feedback |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Trial phase onset: fixation cross |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session boundary: end of session |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial phase onset: end of trial |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | Trial phase onset: continuous feedback |
| `OVTK_GDF_Incorrect` | 697 | event | raw | Incorrect classification feedback |
| `OVTK_GDF_Right` | 845 | event | raw | Trial phase onset: right hand condition |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial phase onset: start of trial |
| `OVTK_GDF_Tongue` | 845 | event | raw | Trial phase onset: tongue condition |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Trial phase onset: baseline start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Trial phase onset: baseline stop |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Auditory cue onset |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Session boundary: experiment start |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Session boundary: experiment stop |
| `OVTK_StimulationId_Train` | 48 | admin | raw | System marker: training/calibration |


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
- **Epoch Parameters**: `tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| `OVTK_GDF_Right` | 0 | Motor imagery (dominant hand grasping) |
| `OVTK_GDF_Tongue` | 1 | Rest/idle condition |

- **Evidence**:
  - 10.1016/j.dib.2022.108225 — Data in Brief descriptor paper explicitly describes 2-class MI vs rest paradigm with 80 trials per class per subject; tmin=0.5s, tmax=2.5s with baseline correction; RUN0 contains real movement, RUN1-RUN4 contain MI vs rest
  - 10.1016/j.heliyon.2020.e03425 — Original Heliyon paper describes BCI protocol with kinesthetic imagination of grasping movement of dominant hand vs rest/idle condition; EMG acquired for protocol control
  - task-MIvsRest_events.json — BIDS sidecar defines value levels: 770='MI', 772='Rest', confirming two-condition paradigm structure
  - README — States RUN1-RUN4 consist of MI vs Rest conditions; RUN0 involves real grasping movement for familiarization
- **Notes**: Event IDs `OVTK_GDF_Right` and `OVTK_GDF_Tongue` serve as condition markers for the two-class MI vs rest paradigm. The label 'Tongue' is repurposed from standard GDF nomenclature in this dataset to mark the rest/idle condition rather than actual tongue motor imagery. The exact numeric code mapping (770/772) referenced in events.json is embedded in EDF annotation values and not directly visible in annotation description strings, but the paired structure (845 occurrences each) and paradigm description confirm these as the two class labels.

### Potential Task 1: Motor Imagery vs Rest with Baseline
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | OVTK_GDF_Right | 0 | Motor imagery (dominant hand grasping) |
  | OVTK_GDF_Tongue | 1 | Rest/idle condition |
- **Evidence**:
  - task-MIvsRest_events.json — value column defines 770='MI' and 772='Rest' as condition codes
  - README — RUN1-RUN4 consist of MI vs. Rest conditions with kinesthetic imagination of dominant hand grasping vs. rest/idle
  - eeg.json — TaskName='MIvsRestRUN1' for motor imagery runs
  - EEG header sample (sub-02 run-1) — confirms OVTK_GDF_Right and OVTK_GDF_Tongue as the two condition markers present in MI runs
- **Notes**: Alternative epoching strategy extending tmin to -0.5s to capture pre-cue fixation cross period (OVTK_GDF_Cross_On_Screen precedes condition cue by ~1s), enabling baseline correction prior to motor imagery onset. Same event IDs as classical task but different temporal window for enhanced signal-to-noise via baseline normalization. The mapping of OVTK_GDF_Right→MI and OVTK_GDF_Tongue→Rest follows the paradigm structure where two conditions alternate; 'Tongue' is repurposed from standard GDF nomenclature for the rest condition in this two-class protocol.

### Potential Task 2: Feedback Correctness Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`OVTK_GDF_Correct`, `OVTK_GDF_Incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | OVTK_GDF_Correct | 0 | Correct classification feedback |
  | OVTK_GDF_Incorrect | 1 | Incorrect classification feedback |
- **Evidence**:
  - Event counts — OVTK_GDF_Correct (n=697) and OVTK_GDF_Incorrect (n=697) appear in equal numbers as paired feedback markers in runs 1-4
  - EEG header sample (sub-02 run-1) — confirms both events present in MI vs Rest runs with feedback
  - task-MIvsRest_events.json — value 770='MI', 772='Rest' contextualizes the BCI feedback paradigm
  - README — RUN1-RUN4 involve MI vs Rest conditions with online BCI feedback enabling correctness prediction
- **Notes**: Feedback events mark the BCI system's classification decision (correct/incorrect), enabling prediction of feedback correctness from EEG. Epoch window (-0.2 to 1.0s) centered on feedback onset captures error-related negativity (ERN) ~100ms and positive error potential (Pe) ~200-400ms post-feedback. Both tmin and tmax are inferred from canonical ERN/Pe component timing.

### Potential Task 3: Trial Phase Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2 s *, target_events = [`OVTK_GDF_Cross_On_Screen`, `OVTK_GDF_Feedback_Continuous`, `OVTK_GDF_End_Of_Trial`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_GDF_Cross_On_Screen` | 0 | fixation cross onset |
  | `OVTK_GDF_Feedback_Continuous` | 1 | continuous feedback phase onset |
  | `OVTK_GDF_End_Of_Trial` | 2 | trial end phase onset |
- **Evidence**:
  - events.tsv / events.json — trial structure markers with counts: Cross_On_Screen (1691), Feedback_Continuous (1689), End_Of_Trial (1689); README confirms RUN1-RUN4 MI vs Rest paradigm with sequential trial phases
- **Notes**: Three-class classification of cognitive/attentional state based on trial phase markers. The 2-second window captures sustained phase-specific activity. The sequential non-overlapping nature of trial phases (fixation → cue/imagery → feedback → end) ensures no within-window contamination. Note that `OVTK_GDF_Right` and `OVTK_GDF_Tongue` are condition markers (MI vs Rest) and are excluded here in favor of pure phase markers that index cognitive state independently of motor imagery content.

### Potential Task 4: Baseline vs Task State
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 3 s *, target_events = [`OVTK_StimulationId_BaselineStart`, `OVTK_GDF_Right`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `OVTK_StimulationId_BaselineStart` | 0 | Rest/baseline period onset |
  | `OVTK_GDF_Right` | 1 | Active task period onset (right hand motor imagery) |
- **Evidence**:
  - README — "RUN1-RUN4 were equal, consisting of MI vs.Rest conditions" with baseline periods bracketed by OVTK_StimulationId_BaselineStart/Stop markers
  - task-MIvsRest_events.json — value 770='MI', 772='Rest' confirms two-condition paradigm
  - EEG header sample — OVTK_StimulationId_BaselineStart and OVTK_GDF_Right both present as event annotations
- **Notes**: This task contrasts rest/idle periods (marked by BaselineStart) with active motor imagery periods (marked by Right cue onset). The 3-second epoch window matches standard MI epoch lengths for fair comparison between conditions. OVTK_GDF_Tongue is excluded as a target event to maintain clear class separation: baseline markers unambiguously indicate rest, while Right cues indicate active task engagement. The pairing of Right/Tongue as condition markers (845 occurrences each) suggests they alternate as MI conditions; using only Right provides a clean binary rest-vs-active discrimination without needing to resolve the exact MI/Rest mapping ambiguity noted in evidence.

### Potential Task 5: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20–30 (years) | Continuous age from participants.tsv; narrow range with non-trivial variance (SD~3.5 years, N=10) |
- **Evidence**:
- **Notes**: Segmentation-based subject-level regression task. No event structure needed; sliding 4-second windows with 50% overlap applied across continuous 125Hz recordings to maximize data usage. Age values are native to participants.tsv (B3 archetype, raw meta level).

### Potential Task 6: sex classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | male |
  | gender | F | 1 | female |
- **Evidence**:
- **Notes**: Subject-level biomarker task using 4-second non-overlapping segments of continuous EEG. The `gender` field in participants.tsv provides binary labels (6 male, 4 female). Segmentation allows pooling many samples per subject to train a classifier that generalizes across subjects. Small sample size (N=10) limits generalizability but enables proof-of-concept sex decoding from low-cost EEG features.

### Potential Task 7: continuous EEG segmentation with age label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0 – 30.0 (years) | Subject-level continuous age from participants.tsv; all 10 subjects right-handed |
- **Evidence**:
- **Notes**: Archetype C with native info field. Sliding window segmentation (4s windows, 50% overlap) applied to continuous EEG recordings across all runs (RUN0 real grasping, RUN1-RUN4 MI vs Rest). No event-based epoching required. Age is a native participants.tsv column, so Meta Level = raw. The kernel simply reads the pre-existing `age` column and assigns it to all segments from the corresponding subject.

## Data Quality Notes

- `device` field is missing from metadata, limiting hardware traceability for reproducibility analyses.
- The `OVTK_GDF_Tongue` event label is repurposed from standard GDF nomenclature to indicate rest/idle condition rather than actual tongue motor imagery, which may cause confusion if interpreted literally.
- Small sample size (N=10 subjects, 50 files) limits statistical power and cross-subject generalizability.
- Event counts show slight imbalance between `OVTK_GDF_Start_Of_Trial` (1691) and `OVTK_GDF_End_Of_Trial` (1689), suggesting potential dropped trials or annotation edge cases.
- The numeric code mapping (770='MI', 772='Rest') referenced in task-MIvsRest_events.json is embedded in EDF annotation values and not directly visible in annotation description strings.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
