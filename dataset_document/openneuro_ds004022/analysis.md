# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21 | **Manual Review**:
**Channels**: 18 | **Sampling Rate**: 500 Hz

## Paradigm

Seven patients with orthopedic impairment performed motor imagery tasks involving four right-upper limb movements (reaching, grasping, lifting, and twisting) guided by visual cues. EEG and fNIRS were recorded simultaneously across multiple sessions to study motor imagery-related neural activation in a clinical population. The trial structure consisted of 3 s fixation, 4 s visual cue, 3 s ready state, and 5 s motor imagery execution period. Event markers S 7-S 10 denote the four motor imagery task types, though their specific semantic mapping cannot be determined from available metadata.

## File Scan Result

> **Kernel SHA256**: `86f8ec17196fd19c621c4b469487c054ecd896ae4c5c24a4d8bf1b3332b98045`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | 21 | admin | raw | Run/session start marker |
| `S 10` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 2` | 840 | event | raw | Trial phase onset or sub-event marker |
| `S 3` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 4` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 5` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 6` | 210 | event | raw | Trial phase onset or sub-event marker |
| `S 7` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 8` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `S 9` | 840 | event | raw | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) |
| `boundary` | 21 | admin | raw | Run boundary marker |
| `condition 12` | 21 | admin | raw | Condition label marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: 4-class motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 7` | 0 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 8` | 1 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 9` | 2 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 10` | 3 | Reaching, grasping, lifting, or twisting motor imagery task |
- **Evidence**:
- **Notes**: The specific semantic mapping between S 7-S 10 and the four MI task types (reaching, grasping, lifting, twisting) cannot be determined from available data. All four event IDs are treated as distinct class labels for a 4-way classification task. The epoch window (0-4 s) captures the visual cue period; the actual 5 s imagery period begins after a 3 s ready state, so this task classifies based on cue-period activity rather than imagery-period activity. For imagery-period classification, a longer epoch (tmin=7 s, tmax=12 s from cue onset) would be needed.

### Potential Task 2: 2-class motor imagery Reach vs Grasp
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`S 7`, `S 10`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 7` | 0 | Reach motor imagery |
  | `S 10` | 1 | Grasp motor imagery |
- **Evidence**:
  - task_motorimagery_eeg.json / README — "four right-upper limb movements for MI tasks: reaching, grasping, lifting, and twisting"; trial structure: 3 s fixation, 4 s visual cue, 3 s ready, 5 s MI execution
  - events.tsv absent — event annotations confirmed via EEGLAB .set headers showing `S 7` and `S 10` as trial markers among four motor imagery task types
  - Event count analysis — `S 7` and `S 10` each appear 840 times (40 trials × 21 runs), consistent with balanced 4-class design where each class appears 10 times per run
- **Notes**: Specific S-code-to-task mapping (which of S 7/S 8/S 9/S 10 maps to which of reach/grasp/lift/twist) cannot be definitively determined from available metadata. The labels "Reach" and "Grasp" are assigned based on the candidate's naming convention and the evidence that these two S-codes represent two of the four motor imagery task types. The 4-second epoch window aligns with the 4 s visual cue period during which participants prepare for motor imagery.

### Potential Task 3: 2-class motor imagery Twist vs Lift
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`S 8`, `S 9`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 8` | 0 | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) — Twist (inferred from task description) |
  | `S 9` | 1 | Trial marker for one of four motor imagery task types (reaching, grasping, lifting, or twisting) — Lift (inferred from task description) |
- **Evidence**:
  - `task_motorimagery_eeg.json` / README — Dataset describes four right-upper limb MI tasks: reaching, grasping, lifting, and twisting; S 7-S 10 each appear 840 times (40 trials × 21 runs), corresponding to these four task types
  - Event count analysis — S 8 and S 9 each appear exactly 840 times, consistent with being trial markers for two of the four MI task types
  - `eeg.json` — TaskDescription confirms four MI tasks: "reaching, grasping, lifting, and twisting"
- **Notes**: Specific S-code-to-task semantic mapping cannot be definitively determined from available data (no events.tsv files; event annotations embedded in EEGLAB .set files with limited header exposure). The pairing of S 8/S 9 as "Twist vs Lift" follows the candidate's proposed labeling. Alternative valid pairings exist (e.g., S 7/S 8, S 7/S 9, S 7/S 10, S 8/S 10, S 9/S 10). The epoch window tmin=0, tmax=4 s captures the 4 s visual cue period per README trial structure (3 s fixation, 4 s cue, 3 s ready, 5 s imagery). Values marked with * are inferred from Category SKILL defaults and the dataset's described trial structure.

### Potential Task 4: Rest vs Task State Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 3 s *, target_events = [`S 3`, `S 4`, `S 2`, `S 5`, `S 6`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | S 3, S 4 | 0 | Rest state (trial phase onset/sub-event marker) |
  | S 2, S 5, S 6 | 1 | Active task state (trial phase onset/sub-event marker) |
- **Evidence**:
- **Notes**: The event meanings from the locked ground truth only identify S 3/S 4 and S 2/S 5/S 6 as generic "Trial phase onset or sub-event marker" without semantic differentiation. The rest vs task grouping is inferred from the candidate's evidence summary based on event count patterns (210 occurrences each, suggesting they partition trial phases) and the trial structure described in the README (fixation 3s, cue 4s, ready 3s, MI 5s). However, without explicit timing or ordering information from events.tsv files, the assignment of S 3/S 4 to "rest" and S 2/S 5/S 6 to "task" is speculative. The S 2 event appears in both rest and task groupings across different header samples (e.g., sub-01 run-1 shows S 2 early in annotation list, sub-01 run-2 shows S 2 near start), suggesting it may mark a consistent trial phase like fixation or cue onset. The binary split follows the candidate's proposed paradigm but should be treated as a hypothesis requiring validation against actual event timing data.

### Potential Task 5: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 48–83 (years) | Complete for all 7 subjects; within-clinical-population age variation (all subjects have orthopedic impairment) |
- **Evidence**:
- **Notes**: Segmentation-based regression predicting subject age from 1-second non-overlapping EEG segments. Uses participants.tsv native info column. All subjects have orthopedic impairment, so this captures age variation within a clinical population rather than healthy aging.

### Potential Task 6: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | Male |
  | sex | F | 1 | Female |
- **Evidence**:
  - participants.tsv — N=7 subjects with complete sex data: 3 Male, 4 Female
- **Notes**: Segmentation-based approach for subject-level sex prediction. Each 1-second segment inherits the subject's sex label from participants.tsv. Small sample size (N=7) limits generalizability but task is technically feasible. Epoch parameters inferred from Category SKILL defaults (1-second non-overlapping segments) due to lack of specific segmentation guidance for subject-level demographic classification.

### Potential Task 7: 4-class motor imagery with age covariate
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 7` | 0 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 8` | 1 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 9` | 2 | Reaching, grasping, lifting, or twisting motor imagery task |
  | `S 10` | 3 | Reaching, grasping, lifting, or twisting motor imagery task |
- **Evidence**:
- **Notes**: This task uses the `age` info field as a secondary subject-level label for multi-task or domain adaptation approaches. The primary classification target remains the 4-class motor imagery task encoded by event IDs S 7-S 10. The age values (48-83 years) are continuous and would need discretization or direct use as auxiliary regression targets in multi-task frameworks. The epoch window tmin=0, tmax=4 s captures the 4-second visual cue period during which participants prepare for motor imagery, consistent with the trial structure described in the README (3 s fixation, 4 s visual cue, 3 s ready state, 5 s imagery execution).

## Data Quality Notes

- No events.tsv files present; all event annotations embedded in EEGLAB .set file headers with limited semantic detail, preventing definitive mapping of S-codes to specific motor imagery task types.
- `device` field is missing from metadata, limiting reproducibility and equipment characterization.
- Small sample size (N=7 subjects, 21 files) constrains statistical power and generalizability of any machine learning models trained on this dataset.
- Event counts for S 3-S 6 (210 each) versus S 7-S 10 (840 each) suggest uneven trial phase partitioning that is not fully explained by available documentation.
- The `boundary` and `condition 12` admin markers appear consistently across all 21 runs but their functional role in trial structure is undocumented.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
