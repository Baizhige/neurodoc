# PEARL-Neuro Database (Alzheimer's Risk Genes, Lifestyle, Neuroimaging)

**Dataset**: `openneuro_ds004796` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004796
**Category**: High-level Mental| **Subjects**: 192 | **Files (Completed)**: 192 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

The PEARL-Neuro database comprises EEG recordings from 192 middle-aged participants (ages 50–63) enriched for Alzheimer's disease risk factors. Participants completed three EEG paradigms: a Multi-Source Interference Task (MSIT) measuring cognitive control, a Sternberg working memory task with varying cognitive load, and resting-state recordings with alternating eyes-open and eyes-closed conditions. EEG was recorded with 64 channels at 1000 Hz sampling rate using a BioSemi ActiveTwo system. The dataset is uniquely characterized by extensive phenotypic data including APOE and PICALM genotyping, neuropsychological assessments (CVLT, Raven's matrices, NEO-FFI), lifestyle factors, and blood biochemistry markers.

## File Scan Result

> **Kernel SHA256**: `cb3ea08c0ec3f44324c639f7dc78714e5fca88453dc60d76c468b6ab7c62b0dc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 7 | admin | raw | Data segment boundary marker |
| `Stimulus/S  1` | 10282 | event | raw | Response: button no. 1 (MSIT); Eyes-open condition start (rest); Response: not true (sternberg) |
| `Stimulus/S  2` | 9918 | event | raw | Response: button no. 2 (MSIT); Eyes-open condition start (rest); Response: true (sternberg) |
| `Stimulus/S  3` | 6246 | event | raw | Response: button no. 3 (MSIT); Low-demanding condition trial (sternberg) |
| `Stimulus/S  4` | 8495 | event | raw | Trial from FS condition (MSIT); Eyes-closed condition start (rest); High-demanding condition trial (sternberg) |
| `Stimulus/S  5` | 6564 | event | raw | Trial from 00 condition (MSIT) |
| `Stimulus/S 10` | 706 | event | raw | Start of a break (MSIT, sternberg); Unlabeled rest period marker (rest) |
| `Stimulus/S 11` | 3821 | event | raw | Retention period onset (sternberg); Unlabeled rest period marker (rest) |
| `Stimulus/S 12` | 11237 | event | raw | Probe stimulus onset (sternberg) |
| `Time 0/` | 1 | admin | raw | Recording time zero reference marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: MSIT condition classification (FS vs 00)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 0.84 s *, target_events = [`Stimulus/S  4`, `Stimulus/S  5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  4` | 0 | Trial from FS condition (MSIT) |
  | `Stimulus/S  5` | 1 | Trial from 00 condition (MSIT) |
- **Evidence**:
- **Notes**: 2-class classification of MSIT trial conditions using the intrinsic task structure. S 4 (FS condition) and S 5 (00 condition) are the actual experimental condition markers per task-msit_events.json. S 1-3 are response buttons, not conditions. Epoch window of 0-0.84s covers the stimulus-response interval for condition-level decoding. Inferred parameters marked with * due to lack of explicit reference for condition-specific classification timing.

### Potential Task 2: MSIT Response Button Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| `Stimulus/S  1` | 0 | Response: button no. 1 (MSIT) |
| `Stimulus/S  2` | 1 | Response: button no. 2 (MSIT) |
| `Stimulus/S  3` | 2 | Response: button no. 3 (MSIT) |

- **Evidence**:
  - task-msit_events.json — "S  1": "Response: button no. 1", "S  2": "Response: button no. 2", "S  3": "Response: button no. 3"
  - sub-01_task-msit_events.tsv — Confirms event_type values S  1, S  2, S  3 appear with trial_type="response" in actual recordings
  - eeg.json / README — MSIT task description: participants identify the deviant digit among three digits and respond with button press 1, 2, or 3
- **Notes**: Response-locked epoch window inferred from stimulus-locked documentation. The -0.5 to +0.5s window captures pre-response motor preparation (readiness potential) and post-response motor execution/feedback. Event IDs correspond to actual button responses in the MSIT paradigm, making this a motor response classification task rather than stimulus classification. The three response buttons are equiprobable motor outputs that may be discriminable by response-locked EEG signatures.

### Potential Task 3: Sternberg demand level classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 12.36 s *, target_events = [`Stimulus/S  3`, `Stimulus/S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  3` | 0 | Low-demanding condition trial (sternberg) |
  | `Stimulus/S  4` | 1 | High-demanding condition trial (sternberg) |
- **Evidence**:
  - task-sternberg_events.json — Defines S 3 as "Low-demanding condition trial" and S 4 as "High-demanding condition trial"
  - sub-01_task-sternberg_events.tsv — Contains actual occurrences of S 3 and S 4 events with trial_type="stimulus"
  - EVENT MEANINGS — LOCKED GROUND TRUTH — Confirms scope=task-sternberg for both events
- **Notes**: The 12.36 s epoch duration is inferred from the candidate's epoch_hint to capture the full Sternberg trial structure including encoding, retention (S 11), and probe (S 12) phases. This allows decoding of working memory load from the complete trial period. The two demand conditions (S 3 vs S 4) represent the experimental manipulation of cognitive load in the Sternberg working memory paradigm.

### Potential Task 4: Sternberg response type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Response: not true (sternberg) |
  | `Stimulus/S  2` | 1 | Response: true (sternberg) |
- **Evidence**:
  - task-sternberg_events.json — defines S 1 as "Response: not true" and S 2 as "Response: true"
  - sub-01_task-sternberg_events.tsv — shows S 1 and S 2 events occur as response events following probe (S 12) stimuli
- **Notes**: Response-locked epochs centered on participant responses during Sternberg working memory probe phase. The 1-second window (-0.5 to +0.5 s) captures pre-response decision buildup and post-response motor execution. Both response types have high event counts (>9900 each), supporting robust binary classification of memory retrieval confidence/decision outcomes.

### Potential Task 5: Sternberg phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 3 s *, target_events = [`Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 10` | 0 | Break start (inter-trial interval) |
  | `Stimulus/S 11` | 1 | Retention period onset |
  | `Stimulus/S 12` | 2 | Probe stimulus onset |
- **Evidence**:
  - task-sternberg_events.json — Defines S 11 as "Retention" and S 12 as "Probe"; S 10 as "Start of a break"
  - sub-01_task-sternberg_events.tsv — Contains actual occurrences of S 3 (stimulus), S 11, S 12 (stimulus), S 1 (response) confirming the phase sequence in Sternberg task
  - EVENT MEANINGS locked ground truth — Confirms S 11: "Retention period onset (sternberg)", S 12: "Probe stimulus onset (sternberg)", S 10: "Start of a break (MSIT, sternberg)"
- **Notes**: Three-class classification of Sternberg working memory task phases. S 10 serves as break/interval baseline, S 11 marks retention period where memory maintenance occurs, and S 12 marks probe presentation requiring retrieval and response. Note that S 10 is shared with MSIT task as break start; the task context (sternberg) distinguishes its usage here. Epoch timing inferred from standard working memory phase durations.

### Potential Task 6: Resting-state eyes-open vs eyes-closed classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`Stimulus/S  2`, `Stimulus/S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  2` | 0 | Eyes-open condition start (rest) |
  | `Stimulus/S  4` | 1 | Eyes-closed condition start (rest) |
- **Evidence**:
  - 10.1109/ICDMW69685.2025.00218 — Uses resting-state EEG with spectral analysis for dementia risk stratification; alpha power modulation between eyes-open and eyes-closed conditions is a classical biomarker.
- **Notes**: The task-rest_events.json explicitly defines S 2 as "Eyes-open condition start" and S 4 as "Eyes-closed condition start". The 4-second epoch length is inferred from spectral analysis conventions in resting-state EEG literature and is appropriate given that eyes-open/closed blocks are typically 30-120 seconds long, allowing multiple epochs per condition. Both events are confirmed present in the rest task recordings with substantial counts (S 2: 9918, S 4: 8495 across the dataset).

## Data Quality Notes

- Event ID `Stimulus/S  1` through `Stimulus/S  5` have overloaded meanings that depend on task context (MSIT, Sternberg, or rest), requiring task-specific filtering for correct interpretation.
- The `device` field is completely missing from info metadata, preventing automated equipment verification.
- Blood biochemistry fields (leukocytes through HSV_r) have substantial missing data (76/192, ~40% missing), limiting power for tasks using these targets.
- Several psychometric and health fields show minor incompleteness: `session_order` (70/192), `education` (174/192), `learning_deficits` (175/192), `allergies` (73/192), `other_diseases` (189/192), and multiple MINI-COPE subscales (~187-190/192).
- The `APOE_rs429358` field contains a `T/?` value indicating unresolved genotype, which may require special handling in haplotype derivation.
- Event counts for `Stimulus/S 10` (706) are substantially lower than other events, reflecting its role as break marker rather than trial event.
- Resting-state event meanings for S 1, S 2, S 3, S 4, S 10, S 11 differ from their task-specific meanings and are marked as "Unlabeled rest period marker" or condition starts in the ground truth.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
