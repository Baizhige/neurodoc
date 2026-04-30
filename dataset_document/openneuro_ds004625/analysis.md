# Mind in Motion: Young Adults Walking Over Uneven Terrain

**Dataset**: `openneuro_ds004625` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004625
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 543 | **Channels**: 284 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants walked over uneven terrain at different speeds while high-density EEG, EMG, and kinematic data were simultaneously recorded, with a seated resting condition also included. The study examines neural correlates of locomotor control and gait adaptation during ambulatory tasks. Gait events (heel-strikes, toe-offs) were synchronized with EEG via force-sensitive insoles.

## File Scan Result

> **Kernel SHA256**: `eec29ae51dff17785ba0eb410e00b3b9ac95a5f5192003e7cbe81d79322222a6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CGY-M  1` | 676 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `CGY-T  1` | 2786 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `CWR-M  1` | 269 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `CWR-T  1` | 3 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `LHS` | 65124 | event | raw | Left Foot Strike |
| `LS-Sync` | 536 | admin | raw | Unexplained synchronization marker - not observed in events.tsv samples |
| `LTO` | 65105 | event | raw | Left Foot Off |
| `NGY-M  1` | 10 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `RHS` | 63800 | event | raw | Right Foot Strike |
| `RTO` | 63792 | event | raw | Right Foot Off |
| `TrialEnd` | 543 | event | raw | Trial phase onset: trial end |
| `TrialStart` | 543 | event | raw | Trial phase onset: trial start |
| `boundary` | 543 | admin | raw | Recording boundary marker |
| `spare-M  1` | 635 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `spare-T  1` | 14 | admin | raw | Unexplained system marker - not observed in events.tsv samples |
| `spare-boundary` | 3 | admin | raw | Unexplained system marker - not observed in events.tsv samples |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 4-class gait event classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| LHS | 0 | Left Foot Strike |
| LTO | 1 | Left Foot Off |
| RHS | 2 | Right Foot Strike |
| RTO | 3 | Right Foot Off |

- **Evidence**:
  - 10.1162/imag.a.1039 — Primary reference defining 4-class gait event classification with epochs locked to gait events at tmin=-0.2s, tmax=1.0s for spectral analysis of EEG during walking
  - 10.3390/s23020928 — Supporting reference for gait event classification using high-density EEG during uneven terrain walking
  - task-UnevenTerrain_events.json — Confirmed event mappings: RHS='Right Foot Strike', LHS='Left Foot Strike', RTO='Right Foot Off', LTO='Left Foot Off'
  - events.tsv samples — Gait cycle events (LHS, LTO, RHS, RTO) confirmed present in all walking task files with ~260,000 total events across 32 subjects
- **Notes**: Native event route (archetype A); no kernel derivation required. Event IDs directly encode four distinct phases of the gait cycle, enabling classification of cortical dynamics associated with each locomotor event.

### Potential Task 1: 2-class heel strike vs toe off classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `RHS`, `LTO`, `RTO`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | LHS | 0 | Left Foot Strike (heel strike) |
  | RHS | 0 | Right Foot Strike (heel strike) |
  | LTO | 1 | Left Foot Off (toe off) |
  | RTO | 1 | Right Foot Off (toe off) |
- **Evidence**:
  - 10.1162/imag.a.1039 — Biomechanically meaningful grouping of gait events: heel strikes (LHS/RHS merged) vs toe offs (LTO/RTO merged) for fundamental stance-to-swing transition classification
- **Notes**: Two-class simplification of the 4-class gait phase task. Heel strikes (foot contact, y=0) and toe offs (foot lift-off, y=1) represent the fundamental binary division of the gait cycle between stance phase initiation and swing phase initiation. Lateralization (left/right) is intentionally collapsed to focus on the universal biomechanical transition. Same temporal window (-0.2 to 1.0s) as the 4-class variant since the cortical dynamics preceding and following these phase transitions are biomechanically equivalent regardless of limb.

### Potential Task 2: 2-class left vs right limb classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | LHS | 0 | Left Foot Strike |
  | LTO | 0 | Left Foot Off |
  | RHS | 1 | Right Foot Strike |
  | RTO | 1 | Right Foot Off |
- **Evidence**:
  - 10.1162/imag.a.1039 — Alternative grouping of gait events by limb: left limb events (LHS, LTO merged as y=0) vs right limb events (RHS, RTO merged as y=1). Tests lateralized cortical activation during walking. Same ~260,000 events with balanced left/right distribution.
- **Notes**: Left limb events (LHS=Left Foot Strike, LTO=Left Foot Off) are merged to y=0; right limb events (RHS=Right Foot Strike, RTO=Right Foot Off) are merged to y=1. This creates a lateralized limb classification from gait cycle events. Epoch parameters unchanged from parent gait-locked paradigm (-0.2 to 1.0 s).

### Potential Task 3: Rest vs Walking State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 10 s *, overlap = 5 s *, target_events = [`TrialStart`, `TrialEnd`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `TrialStart` (rest trial) | 0 | Seated rest condition (3-minute baseline, no gait events) |
  | `TrialStart` (walking trial) | 1 | Active walking condition (with gait cycle events: LHS/RHS/LTO/RTO) |
- **Evidence**:
- **Notes**: Classification is performed by distinguishing rest trials (task-rest, containing only TrialStart/TrialEnd with no gait events) from walking trials (task-0p25/task-0p5/task-0p75/task-1p0/task-flat/task-low/task-med/task-high, which contain gait cycle events LHS/RHS/LTO/RTO). Since both conditions use `TrialStart` as the anchor event, the kernel must differentiate classes by checking whether the trial contains gait events (walking) or lacks them (rest). The `TrialEnd` event is included in target_events to allow proper epoching of the full sustained state period. Overlapping 10-second windows with 5-second overlap provide sufficient samples for state comparison while capturing sustained neural dynamics.

### Potential Task 4: Age Regression from EEG Gait Dynamics
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 2 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 20.0–35.0 (years) | Subject-level chronological age; regression target applied to all epochs from same subject |
- **Evidence**:
  - 10.1162/imag.a.1039 — Age prediction from electrocortical dynamics during uneven terrain walking in young adults (ages 20-35, N=32)
- **Notes**: Segmentation-based approach with no discriminating event structure for age prediction. Uses subject-level info field `age` from participants.tsv (native, pre-existing source). Epoch parameters inferred from SKILL clinical defaults for subject-level regression tasks: 6-s windows with 2-s overlap to capture gait cycle dynamics while maintaining sufficient samples per subject.

### Potential Task 5: Gender Classification from EEG Gait Dynamics
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | Male |
  | gender | F | 1 | Female |
- **Evidence**:
- **Notes**: Segmentation-based approach for subject-level classification. 6-second windows with 2-second overlap extract locomotor EEG patterns during walking. The binary gender labels (M/F) are perfectly balanced (16 each) in participants.tsv, enabling robust cross-validation. All walking task conditions (flat, low, medium, high terrain; 0.25-1.0 m/s speeds) contribute segments, capturing neural gait dynamics across varying locomotor demands. No event anchors are used; continuous EEG is segmented and labeled by subject-level demographic info.

### Potential Task 6: Handedness Classification from EEG Gait Dynamics
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 2 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | R | 0 | right-handed |
  | handedness | L | 1 | left-handed |
- **Evidence**:
- **Notes**: Segmentation-based subject-level classification using 6-second windows with 2-second overlap. Handedness is a complete native participants.tsv column (sample: R, L). Expected severe class imbalance with predominantly right-handed participants (32 subjects, likely ~29-30 R vs ~2-3 L based on population prevalence). Technically valid but likely underpowered for left-handed class. No kernel derivation needed — label is native info field.

### Potential Task 7: Prescribed Speed Regression from EEG Gait Dynamics
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 2.0 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `speed`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | speed | 0.67–1.20 (m/s) | Prescribed comfortable treadmill walking speed from participants.tsv; complete for all 32 subjects |
- **Evidence**:
  - participants.tsv — `speed` column complete (N=32, range 0.67–1.20 m/s); sample values [0.860, 0.870, 0.910, 0.670, 0.780, 1.200, 0.700]
- **Notes**: Segmentation-based subject-level regression. Each subject contributes multiple 6-s EEG segments from walking task recordings; all segments from a given subject share the same speed label. The kernel does not need to compute any derived channels — speed is a native participants.tsv column.

### Potential Task 8: Continuous Walking State Segmentation with Age Label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–35.0 (years) | Subject chronological age from participants.tsv; applied to all segments from that subject |
- **Evidence**:
  - 10.1162/imag.a.1039 — Studies age differences in electrocortical dynamics during walking; supports using age as regression target for EEG segments
- **Notes**: Archetype C with info-native label: continuous walking EEG is segmented into 6-s non-overlapping windows (no event locking), with subject age from participants.tsv as the regression target. The kernel does not need to derive any channels; age is a pre-existing info field. This complements event-locked approaches by using the full continuous signal without gait-cycle alignment.

### Potential Task 9: Continuous Walking State Segmentation with Gender Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | F | 0 | Female |
  | gender | M | 1 | Male |
- **Evidence**:
- **Notes**: Archetype C with info-native label. The continuous walking EEG signal is segmented into non-overlapping 6-second windows for classification. Gender is drawn from participants.tsv as a native info field (16 female, 16 male), yielding a balanced binary classification task. No event-based epoching is used; the full continuous dynamics of unconstrained walking are preserved in each segment.

### Potential Task 10: Resting-State Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 2.0 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–35.0 (years) | Subject chronological age from participants.tsv; resting-state EEG segments used as features for age prediction |
- **Evidence**:
  - [README] — "Participants completed two trials for each condition for three minutes and a seated rest trial for three minutes"
  - [participants.tsv] — Age column present for all 32 subjects, range 20.0–35.0 years
  - [events.tsv samples, task-rest] — TrialStart/TrialEnd mark rest trial boundaries
- **Notes**: Archetype C with segmentation on rest trial data. No derived channels needed; age is native participants.tsv column. Segmentation uses 6-s windows with 2-s overlap across the 3-minute rest period, yielding approximately 45 segments per subject. This task provides a baseline comparison to walking-active models by testing whether resting-state EEG alone can predict age.

## Data Quality Notes

- Multiple unexplained system markers (`CGY-M 1`, `CGY-T 1`, `CWR-M 1`, `CWR-T 1`, `NGY-M 1`, `spare-M 1`, `spare-T 1`, `spare-boundary`) are flagged as "not observed in events.tsv samples" — their actual presence in data files vs. metadata files is uncertain and requires verification.
- The `device` field is completely missing from Info metadata, limiting hardware traceability.
- Gait event counts are extremely high (~65,000 per type), suggesting dense event spacing during continuous walking; epoch overlap contamination must be carefully checked.
- Administrative events (`boundary`, `LS-Sync`, `spare-boundary`) should be excluded from all event-locked analyses.
- Handedness classification (Potential Task 6) is expected to suffer from severe class imbalance based on population prevalence (~90% right-handed), making it likely underpowered despite technical validity.
- Rest vs Walking State Classification (Potential Task 3) requires kernel-level logic to distinguish trial types since both use `TrialStart` as anchor — this depends on accurate task metadata in filenames or events.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
