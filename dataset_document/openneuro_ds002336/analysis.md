# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP1

**Dataset**: `openneuro_ds002336` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002336
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 107 | **Channels**: 64 | **Sampling Rate**: 5000 Hz
**Manual Review**:

## Paradigm

Simultaneous EEG-fMRI acquisition during a kinesthetic motor imagery neurofeedback task. Subjects performed right-hand motor imagery or motor execution during sustained task blocks alternating with rest blocks, while receiving unimodal (EEG or fMRI) or bimodal neurofeedback. Each task block (Task-NF: neurofeedback, Task-ME: motor execution, Task-MI: motor imagery) is a sustained mental state lasting several seconds. BrainVision format with MRI artifact markers (TPULSE, R128) that must be excluded.

## File Scan Result

> **Kernel SHA256**: `b8765f797051b568f914682c5c07b2c71452b6c67b90de5d6877e88536ae30d8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 41 | admin | raw | Recording segment start |
| `Pulse Artifact/R` | 23308 | admin | raw | Cardiac pulse artifact marker (channel 32) |
| `Response/R128` | 18223 | admin | raw | Regular timing synchronization marker |
| `Stimulus/S  1` | 152 | event | raw | Trial phase onset: Task-ME |
| `Stimulus/S  2` | 740 | event | raw | Trial phase onset: Task |
| `Stimulus/S 99` | 880 | event | raw | Trial phase onset: Rest |
| `TPULSE/TEND` | 51 | admin | raw | Pulse timing marker (TEND) |
| `TPULSE/TPEAK` | 51 | admin | raw | Pulse timing marker (TPEAK) |
| `TPULSE/TSTART` | 51 | admin | raw | Pulse timing marker (TSTART) |
| `Time 0/` | 44 | admin | raw | Time reference point |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ECG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `ECG` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
- **Candidate Labels**: `ECG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Rest vs Task state classification (S 99 vs S 2)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0 s *, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 99` | 0 | Rest phase onset |
  | `Stimulus/S  2` | 1 | Task phase onset (motor imagery / neurofeedback) |
- **Evidence**:
  - 10.1038/s41597-020-0498-3 — Dataset descriptor confirming simultaneous EEG-fMRI during motor imagery neurofeedback with Rest and Task block structure
  - 10.1101/862375 — Original paper describing XP1 dataset with 20-second alternating Rest/Task blocks for MI and NF tasks
  - 10.3389/fnhum.2017.00193 — Perronnet et al. (2017) describing unimodal vs bimodal EEG-fMRI neurofeedback paradigm with Rest (S 99) and Task (S 2) markers
- **Notes**: Event route archetype A with raw meta level. Sustained 20-second blocks confirmed in events.tsv samples (duration=20s for both Rest and Task-MI). Epoch parameters inferred from standard long-event defaults: 4-second window captures stable neurofeedback period while avoiding transition edges. Overlap=0 s inferred as default for non-overlapping epochs. MRI artifact markers (Pulse Artifact/R, Response/R128, TPULSE/*) and administrative markers (New Segment/, Time 0/) are excluded from target_events as required.

### Potential Task 2: Motor Execution vs Rest state classification (S 1 vs S 99)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, overlap = 0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S 99`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Motor Execution (Task-ME onset) |
  | `Stimulus/S 99` | 1 | Rest (Rest onset) |
- **Evidence**:
  - 10.1038/s41597-020-0498-3 — Dataset descriptor; describes motorloc task with motor execution blocks
  - 10.1101/862375 — Original paper describing simultaneous EEG-fMRI during motor imagery and motor execution tasks
  - 10.3389/fnhum.2017.00193 — Primary publication describing XP1 paradigm with motor execution localizer (motorloc) task
- **Notes**: Limited to motorloc task files where Stimulus/S 1 appears. Stimulus/S 1 marks Task-ME (motor execution) onset specifically in motorloc task; Stimulus/S 99 marks Rest onset across all tasks. Overlap set to 0 s by default for long-event epochs since no overlap was specified in epoch_hint. The 3-second window captures initial motor execution period; actual motor execution blocks are 20s long per events.tsv but classification focuses on onset-driven state discrimination.

### Potential Task 3: Task condition classification (S 1 vs S 2)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, overlap = 0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Motor Execution (Task-ME, motorloc runs) |
  | `Stimulus/S  2` | 1 | Motor Imagery / Neurofeedback (MI/NF runs) |
- **Evidence**:
  - 10.1038/s41597-020-0498-3 — Dataset descriptor confirming motorloc (ME) and MI/NF tasks with distinct event markers
  - 10.1101/862375 — Methods paper describing simultaneous EEG-fMRI during motor imagery neurofeedback and motor execution localizer
  - 10.3389/fnhum.2017.00193 — Original study detailing unimodal vs bimodal neurofeedback paradigm with Task-MI and Task-ME conditions
- **Notes**: Cross-task classification comparing motor execution (S 1, from motorloc runs only) against motor imagery/neurofeedback task onset (S 2, from MIpre/MIpost/eegNF/eegfmriNF/fmriNF runs). Both event types mark task phase onset but in different experimental paradigms. The 3s window is conservative given the 20s block duration; overlap=0 is default for long-event epoching when not specified. Epoch parameters inferred from block structure and cross-condition comparison requirements.

### Potential Task 4: Age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0 – 39.0 (years) | Continuous age from participants.tsv; N=10 subjects, each segment inherits subject's age as regression target |
- **Evidence**:
  - participants.tsv — age column complete for all N=10 subjects, range 19.0–39.0 years
  - analysis.md Potential Task 1 — 4-second windows with 50% overlap during sustained Rest blocks (20s), yielding ~7 segments per block
- **Notes**: Segmentation-based regression task using sliding windows over continuous EEG. No event-based epoching required; target_events=[] per segmentation method. Age is a native participants.tsv column (info route, archetype C with native info column → Meta Level = raw). Limited sample size (N=10) noted as limitation.

### Potential Task 5: Sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | male |
  | sex | F | 1 | female |
- **Evidence**:
- **Notes**: Segmentation-based classification using 4-second non-overlapping windows (50% overlap) of continuous resting-state/task EEG. Each segment inherits the subject's sex label from participants.tsv. Highly imbalanced dataset with 8 male and 2 female subjects. The small sample size (N=10) makes this a high-risk potential task with limited generalizability. No event markers are used for epoching since this is a pure segmentation approach on continuous data.

### Potential Task 6: ECG regression from continuous recordings
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `ECG`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | ECG | continuous (mV) | Native ECG channel recorded simultaneously with EEG; regression target is the ECG signal amplitude within each window |
- **Evidence**:
  - EEG File Header Sample (sub-xp101_task-eegNF_eeg_pp.vhdr, sub-xp101_task-eegfmriNF_eeg_pp.vhdr) — ECG listed among 64 channels in raw EEG recordings, confirming native continuous misc channel presence
  - README / dataset_description.json — simultaneous EEG-fMRI acquisition with physiological monitoring; ECG standard for cardiac artifact detection and physiological correlation studies
  - events.tsv samples (task-MIpre, task-MIpost) — continuous 20s Rest/Task blocks with no per-trial ECG labels, supporting segmentation approach for continuous regression target
- **Notes**: Archetype B1 native misc channel. ECG is a continuous non-EEG channel already present in the raw recordings. The kernel does not need to derive this channel; it is loaded directly from the native misc channels. Segmentation into 4s windows with 50% overlap is standard for physiological correlation analysis between EEG and cardiac activity. Values marked with * are inferred from the epoch_hint as no explicit dataset documentation specifies these exact parameters.

### Potential Task 7: Rest vs Task state classification from long epochs (all task types)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0.0 *, target_events = [`Stimulus/S  2`, `Stimulus/S 99`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 99` | 0 | Rest (trial phase onset: Rest) |
  | `Stimulus/S  2` | 1 | Task (trial phase onset: Task, encompassing MIpre, MIpost, eegNF, eegfmriNF, fmriNF conditions) |
- **Evidence**:
  - 10.1038/s41597-020-0498-3 — Dataset descriptor confirming simultaneous EEG-fMRI during motor imagery and neurofeedback tasks with Rest/Task block structure
  - 10.1101/862375 — BioRxiv preprint describing XP1 dataset with three NF run types (bimodal EEG-fMRI NF, unimodal EEG-NF, fMRI-NF) and Rest/Task alternation
  - 10.3389/fnhum.2017.00193 — Original study describing unimodal vs bimodal EEG-fMRI neurofeedback paradigm with 20-second Rest/Task blocks
- **Notes**: Sustained 20s blocks are consistently used across all five task variants (MIpre, MIpost, eegNF, eegfmriNF, fmriNF). The 4-second window captures stable state-related EEG signatures while allowing multiple non-overlapping epochs per 20s block. S 2 serves as the unified task marker across all neurofeedback and motor imagery conditions, as confirmed by events.tsv files showing trial_type values Task-MI, Task-EEG, Task-EEGfMRI, and Task-fMRI all map to Stimulus/S  2 trigger.

## Data Quality Notes

- Very high sampling rate (5000 Hz) with dense MRI artifact markers (Pulse Artifact/R: 23,308; Response/R128: 18,223) requires careful artifact handling before any analysis.
- ECG channel is present as native misc but its role and unit need verification; it is also marked for Super Meta derivation.
- `device` field is completely missing from info metadata, limiting equipment provenance tracking.
- Small sample size (N=10 subjects) severely limits generalizability for all demographic prediction tasks (age regression, sex classification).
- Sex classification is highly imbalanced (8 male, 2 female).
- Multiple overlapping task definitions exist for Rest vs Task classification (Potential Tasks 1 and 7); users should verify which S 2/S 99 pairing matches their analytical needs.
- Stimulus/S 1 (motor execution) only appears in motorloc task files, limiting cross-task comparability.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
