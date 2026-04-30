# HID (High-Density EEG Operational Dataset)

**Dataset**: `openneuro_ds004851` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004851
**Category**: Complex Applied | **Subjects**: 65 | **Files (Completed)**: 65 | **Channels**: 72 | **Sampling Rate**: 2048 Hz | **Manual Review**:

## Paradigm

High-density EEG (72 channels) was recorded in an operational context involving multiple stimulus categories encoded as hierarchical event codes. The paradigm includes primary stimulus presentations (types A–F) with onset/response event pairs, secondary stimulus categories (80/81 series), and block-level markers (01–19) indicating experimental structure. Subjects performed cognitive tasks under varying workload conditions with both trial-level and block-level event markers.

## File Scan Result

> **Kernel SHA256**: `cfaa22cb59fd5feef36bd7eb0386d427a2ef3fa4d2c8b7d597b4c6f0f3d7f0bd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `HID: block_marker_01` | 65 | event | raw | Trial phase onset: block 1 |
| `HID: block_marker_02` | 65 | event | raw | Trial phase onset: block 2 |
| `HID: block_marker_03` | 65 | event | raw | Trial phase onset: block 3 |
| `HID: block_marker_04` | 65 | event | raw | Trial phase onset: block 4 |
| `HID: block_marker_05` | 65 | event | raw | Trial phase onset: block 5 |
| `HID: block_marker_06` | 65 | event | raw | Trial phase onset: block 6 |
| `HID: block_marker_07` | 65 | event | raw | Trial phase onset: block 7 |
| `HID: block_marker_08` | 65 | event | raw | Trial phase onset: block 8 |
| `HID: block_marker_09` | 65 | event | raw | Trial phase onset: block 9 |
| `HID: block_marker_10` | 64 | event | raw | Trial phase onset: block 10 |
| `HID: block_marker_11` | 65 | event | raw | Trial phase onset: block 11 |
| `HID: block_marker_12` | 65 | event | raw | Trial phase onset: block 12 |
| `HID: block_marker_13` | 65 | event | raw | Trial phase onset: block 13 |
| `HID: block_marker_14` | 65 | event | raw | Trial phase onset: block 14 |
| `HID: block_marker_15` | 63 | event | raw | Trial phase onset: block 15 |
| `HID: block_marker_16` | 63 | event | raw | Trial phase onset: block 16 |
| `HID: block_marker_17` | 63 | event | raw | Trial phase onset: block 17 |
| `HID: block_marker_18` | 62 | event | raw | Trial phase onset: block 18 |
| `HID: block_marker_19` | 62 | event | raw | Trial phase onset: block 19 |
| `HID: secondary_80A_onset` | 195 | event | raw | Secondary task stimulus onset: 80A |
| `HID: secondary_80A_response` | 195 | event | raw | Response to secondary task stimulus 80A |
| `HID: secondary_80B_onset` | 194 | event | raw | Secondary task stimulus onset: 80B |
| `HID: secondary_80B_response` | 194 | event | raw | Response to secondary task stimulus 80B |
| `HID: secondary_80_onset` | 65 | event | raw | Secondary task stimulus onset: 80 |
| `HID: secondary_80_response` | 64 | event | raw | Response to secondary task stimulus 80 |
| `HID: secondary_81_onset` | 973 | event | raw | Secondary task stimulus onset: 81 |
| `HID: secondary_81_response` | 973 | event | raw | Response to secondary task stimulus 81 |
| `HID: stimulus_A_onset` | 2181 | event | raw | Stimulus onset: A |
| `HID: stimulus_A_response` | 2179 | event | raw | Response to stimulus A |
| `HID: stimulus_B_onset` | 1970 | event | raw | Stimulus onset: B |
| `HID: stimulus_B_response` | 1970 | event | raw | Response to stimulus B |
| `HID: stimulus_C_onset` | 204 | event | raw | Stimulus onset: C |
| `HID: stimulus_C_response` | 204 | event | raw | Response to stimulus C |
| `HID: stimulus_D_onset` | 1912 | event | raw | Stimulus onset: D |
| `HID: stimulus_D_response` | 1912 | event | raw | Response to stimulus D |
| `HID: stimulus_E_onset` | 15 | event | raw | Stimulus onset: E |
| `HID: stimulus_E_response` | 15 | event | raw | Response to stimulus E |
| `HID: stimulus_F_onset` | 469 | event | raw | Stimulus onset: F |
| `HID: stimulus_F_response` | 469 | event | raw | Response to stimulus F |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: 6-class stimulus type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`, `HID: stimulus_C_onset`, `HID: stimulus_D_onset`, `HID: stimulus_E_onset`, `HID: stimulus_F_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: stimulus_A_onset` | 0 | Stimulus onset: A |
  | `HID: stimulus_B_onset` | 1 | Stimulus onset: B |
  | `HID: stimulus_C_onset` | 2 | Stimulus onset: C |
  | `HID: stimulus_D_onset` | 3 | Stimulus onset: D |
  | `HID: stimulus_E_onset` | 4 | Stimulus onset: E |
  | `HID: stimulus_F_onset` | 5 | Stimulus onset: F |
- **Evidence**:
  - events.tsv sample (sub-001) — shows trigger codes 1010/1011/1040 etc. matching stimulus onset/response pairs; 1010 corresponds to stimulus_A_onset per frequency alignment (2181 occurrences)
  - Event frequency analysis — stimulus_A_onset: 2181, stimulus_B_onset: 1970, stimulus_C_onset: 204, stimulus_D_onset: 1912, stimulus_E_onset: 15, stimulus_F_onset: 469 trials, forming a 6-class discrimination paradigm
  - EEG file header annotations — confirms numeric trigger codes 1010, 1020, 1040, 1060 present as event markers in raw .set files
- **Notes**: Standard ERP epoching for visual/auditory stimulus discrimination. tmin=-0.2s provides pre-stimulus baseline; tmax=1.0s captures early ERP components (P1, N1, P2) and late components (P300) given expected RT ~500-1000ms. Stimulus E has severely imbalanced class (n=15) which may affect model training. All six stimulus onset events are used as trial anchors with their corresponding responses as secondary markers.

### Potential Task 2: 2-class stimulus A vs B discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: stimulus_A_onset` | 0 | Stimulus onset: A |
  | `HID: stimulus_B_onset` | 1 | Stimulus onset: B |
- **Evidence**:
  - Event counts — Stimulus A onset (2181 trials) and Stimulus B onset (1970 trials) are the two most frequent conditions with nearly balanced trial counts, suitable for binary classification.
- **Notes**: Epoch window (-0.2 to 1.0 s) centered on stimulus onset captures the ERP component for discriminating between stimulus categories A and B. Rare stimulus classes C-F are excluded to avoid class imbalance. The event IDs used (`HID: stimulus_A_onset`, `HID: stimulus_B_onset`) are the string labels recovered from pre-scan of the dataset's event structure, corresponding to numeric trigger codes 1010 and 1020 respectively in the BIDS events.tsv files.

### Potential Task 3: 4-class stimulus ABCD classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`, `HID: stimulus_C_onset`, `HID: stimulus_D_onset`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: stimulus_A_onset` | 0 | Stimulus onset: A |
  | `HID: stimulus_B_onset` | 1 | Stimulus onset: B |
  | `HID: stimulus_C_onset` | 2 | Stimulus onset: C |
  | `HID: stimulus_D_onset` | 3 | Stimulus onset: D |
- **Evidence**:
- **Notes**: Stimulus C has only 204 trials compared to ~1900-2200 for A, B, and D. Class imbalance should be addressed via stratified sampling or class weighting during model training. Epoch window spans pre-stimulus baseline (-200 ms) through 1000 ms post-onset to capture early ERP components (P1, N1, P2) relevant for visual stimulus discrimination. The inferred epoch parameters are based on standard ERP paradigms for multi-class stimulus classification; the actual optimal window may vary and should be validated.

### Potential Task 4: 2-class secondary task 80A vs 80B discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: secondary_80A_onset`, `HID: secondary_80B_onset`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: secondary_80A_onset` | 0 | Secondary task stimulus onset: 80A |
  | `HID: secondary_80B_onset` | 1 | Secondary task stimulus onset: 80B |
- **Evidence**:
  - Dataset event structure — 195 onsets of 80A and 194 onsets of 80B with matched response events, indicating two balanced secondary task conditions
- **Notes**: Nearly perfectly balanced binary classification (195 vs 194 trials) of secondary task subtypes. The 80A and 80B conditions represent distinct secondary/backup task stimuli separate from the primary A-F stimulus set and the other secondary task variants (80, 81). Epoch window includes 200 ms pre-stimulus baseline and 1.0 s post-stimulus, inferred from typical ERP paradigms with similar secondary task demands.

### Potential Task 5: 2-class secondary task 80 vs 81 discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: secondary_80_onset`, `HID: secondary_81_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: secondary_80_onset` | 0 | Secondary task stimulus onset: 80 |
  | `HID: secondary_81_onset` | 1 | Secondary task stimulus onset: 81 |
- **Evidence**:
  - `events.tsv` numeric codes and pre-scan event structure — Secondary task events 8000/8001 map to 80/80A/80B family and 8100/8101 map to 81; counts confirm 65 block-level 80_onset vs 973 trial-level 81_onset events
- **Notes**: This task discriminates between two secondary task categories (80 vs 81) despite a severe class imbalance (65 vs 973 trials). The 80_onset is block-level while 81_onset is trial-level, creating a structural difference in event density that may affect model training. The 80A/80B subtypes are merged into the broader 80 category. Epoch window chosen to capture early ERP components while allowing brief pre-stimulus baseline.

### Potential Task 6: 19-class block identification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 10 s *, overlap = 0.0 *, target_events = [`HID: block_marker_01`, `HID: block_marker_02`, `HID: block_marker_03`, `HID: block_marker_04`, `HID: block_marker_05`, `HID: block_marker_06`, `HID: block_marker_07`, `HID: block_marker_08`, `HID: block_marker_09`, `HID: block_marker_10`, `HID: block_marker_11`, `HID: block_marker_12`, `HID: block_marker_13`, `HID: block_marker_14`, `HID: block_marker_15`, `HID: block_marker_16`, `HID: block_marker_17`, `HID: block_marker_18`, `HID: block_marker_19`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: block_marker_01` | 0 | Trial phase onset: block 1 |
  | `HID: block_marker_02` | 1 | Trial phase onset: block 2 |
  | `HID: block_marker_03` | 2 | Trial phase onset: block 3 |
  | `HID: block_marker_04` | 3 | Trial phase onset: block 4 |
  | `HID: block_marker_05` | 4 | Trial phase onset: block 5 |
  | `HID: block_marker_06` | 5 | Trial phase onset: block 6 |
  | `HID: block_marker_07` | 6 | Trial phase onset: block 7 |
  | `HID: block_marker_08` | 7 | Trial phase onset: block 8 |
  | `HID: block_marker_09` | 8 | Trial phase onset: block 9 |
  | `HID: block_marker_10` | 9 | Trial phase onset: block 10 |
  | `HID: block_marker_11` | 10 | Trial phase onset: block 11 |
  | `HID: block_marker_12` | 11 | Trial phase onset: block 12 |
  | `HID: block_marker_13` | 12 | Trial phase onset: block 13 |
  | `HID: block_marker_14` | 13 | Trial phase onset: block 14 |
  | `HID: block_marker_15` | 14 | Trial phase onset: block 15 |
  | `HID: block_marker_16` | 15 | Trial phase onset: block 16 |
  | `HID: block_marker_17` | 16 | Trial phase onset: block 17 |
  | `HID: block_marker_18` | 17 | Trial phase onset: block 18 |
  | `HID: block_marker_19` | 18 | Trial phase onset: block 19 |
- **Evidence**:
  - Event counts from dataset scan — 19 block markers (HID: block_marker_01 through HID: block_marker_19) with ~62-65 occurrences each across 20 subjects, indicating systematic block-structured experimental design
  - EEG file header annotations confirm numeric trigger codes 7001-7019 map to block markers
- **Notes**: Block-level state classification with 19 classes. All epoch parameters inferred from block structure (long epochs capturing sustained neural state). Low per-class sample count (~62-65 per subject pool) makes this a challenging high-way classification problem. The numeric trigger codes 7001-7019 in events.tsv correspond to these 19 block markers; the string labels were recovered from pre-scan of binary EEGLAB .set file structure.

### Potential Task 7: 2-class early vs late block discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 10 s *, overlap = 0 s *, target_events = [`HID: block_marker_01`, `HID: block_marker_02`, `HID: block_marker_03`, `HID: block_marker_04`, `HID: block_marker_05`, `HID: block_marker_06`, `HID: block_marker_07`, `HID: block_marker_08`, `HID: block_marker_09`, `HID: block_marker_10`, `HID: block_marker_11`, `HID: block_marker_12`, `HID: block_marker_13`, `HID: block_marker_14`, `HID: block_marker_15`, `HID: block_marker_16`, `HID: block_marker_17`, `HID: block_marker_18`, `HID: block_marker_19`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `HID: block_marker_01` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_02` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_03` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_04` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_05` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_06` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_07` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_08` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_09` | 0 | early block (blocks 1-9) |
  | `HID: block_marker_10` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_11` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_12` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_13` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_14` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_15` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_16` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_17` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_18` | 1 | late block (blocks 10-19) |
  | `HID: block_marker_19` | 1 | late block (blocks 10-19) |
- **Evidence**:
  - events.tsv numeric codes 7001-7019 correspond to sequential block markers 1-19, with consistent onset/response pairing patterns and event counts matching block structure
  - EEG file header annotations confirm numeric codes 7001, 7002, 7003, etc. appear as block markers in the raw data
- **Notes**: Long 10-second epochs capture sustained block-level neural state for temporal dynamics analysis. All epoch parameters inferred from paradigm structure (block markers indicate phase onsets, 10s duration chosen to capture sustained state). Early blocks (1-9, y=0) have 585 total events; late blocks (10-19, y=1) have 637 total events with slight imbalance. Overlap set to 0 to avoid redundant sampling of block state.

### Potential Task 8: Stimulus Onset vs Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`, `HID: stimulus_C_onset`, `HID: stimulus_D_onset`, `HID: stimulus_E_onset`, `HID: stimulus_F_onset`, `HID: secondary_80A_onset`, `HID: secondary_80B_onset`, `HID: secondary_81_onset`, `HID: stimulus_A_response`, `HID: stimulus_B_response`, `HID: stimulus_C_response`, `HID: stimulus_D_response`, `HID: stimulus_E_response`, `HID: stimulus_F_response`, `HID: secondary_80A_response`, `HID: secondary_80B_response`, `HID: secondary_81_response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
| Event ID | y | Meaning |
|----------|---|---------|
| `HID: stimulus_A_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_B_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_C_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_D_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_E_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_F_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: secondary_80A_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: secondary_80B_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: secondary_81_onset` | 0 | Stimulus onset (perception/decision phase) |
| `HID: stimulus_A_response` | 1 | Response event (motor execution phase) |
| `HID: stimulus_B_response` | 1 | Response event (motor execution phase) |
| `HID: stimulus_C_response` | 1 | Response event (motor execution phase) |
| `HID: stimulus_D_response` | 1 | Response event (motor execution phase) |
| `HID: stimulus_E_response` | 1 | Response event (motor execution phase) |
| `HID: stimulus_F_response` | 1 | Response event (motor execution phase) |
| `HID: secondary_80A_response` | 1 | Response event (motor execution phase) |
| `HID: secondary_80B_response` | 1 | Response event (motor execution phase) |
| `HID: secondary_81_response` | 1 | Response event (motor execution phase) |
- **Evidence**:
  - events.tsv samples (sub-001) — Shows paired numeric codes 1010/1011, 1040/1041, etc. corresponding to onset/response pairs
  - EEG file header annotations — Confirms trigger codes 1010, 1011, 1040, 1041, 1020, 1021, 1060 present in data
  - Event ID frequency table — All onset and response event IDs have matching counts (e.g., stimulus_A_onset: 2181, stimulus_A_response: 2179), confirming paired trial structure
- **Notes**: All stimulus onset events (primary A-F and secondary 80A/80B/81) are merged to class y=0, representing the perception/decision phase. All corresponding response events are merged to class y=1, representing the motor response execution phase. The slight count mismatches (e.g., 2181 vs 2179) likely reflect occasional missing responses or data quality issues. Epoch window centered on each event captures peri-event ERP differences between sensory-cognitive processing and motor preparation/execution.

### Potential Task 9: Primary vs Secondary Task Discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`, `HID: stimulus_C_onset`, `HID: stimulus_D_onset`, `HID: stimulus_E_onset`, `HID: stimulus_F_onset`, `HID: secondary_80A_onset`, `HID: secondary_80B_onset`, `HID: secondary_81_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  | `HID: stimulus_A_onset` | 0 | Primary task stimulus onset: A |
  | `HID: stimulus_B_onset` | 0 | Primary task stimulus onset: B |
  | `HID: stimulus_C_onset` | 0 | Primary task stimulus onset: C |
  | `HID: stimulus_D_onset` | 0 | Primary task stimulus onset: D |
  | `HID: stimulus_E_onset` | 0 | Primary task stimulus onset: E |
  | `HID: stimulus_F_onset` | 0 | Primary task stimulus onset: F |
  | `HID: secondary_80A_onset` | 1 | Secondary task stimulus onset: 80A |
  | `HID: secondary_80B_onset` | 1 | Secondary task stimulus onset: 80B |
  | `HID: secondary_81_onset` | 1 | Secondary task stimulus onset: 81 |
- **Evidence**:
  - events.tsv sample (sub-001) — shows trigger codes 1010/1011 (stimulus A onset/response), 1040/1041 (stimulus D onset/response), 1020/1021 (stimulus B onset/response), 1060 (stimulus F onset), 7001-7007 (block markers), 8000 (secondary task 80)
  - eeg.set header annotations — confirms numeric trigger codes 1010, 1011, 7001, 1040, 1041, 7002, 7003, 1020, 1021, 1060, 8000 present in raw data
  - Available event ID counts — primary task stimuli A-F total 6751 onsets (2181+1970+204+1912+15+469), secondary task 80A/80B/81 total 1362 onsets (195+194+973)
- **Notes**: All six primary task stimulus types (A-F) are merged to y=0 as they share the same primary task role; all three secondary task stimulus types (80A, 80B, 81) are merged to y=1. The epoch window (-0.2 to 1.0 s) is standard for ERP comparison of early attentional processing and working memory engagement differences between primary and secondary task demands in dual-task paradigms. The string event IDs are recovered from pre-scan event structure mapping; the actual BIDS events.tsv contains corresponding numeric codes (1010/1011 for A, 1020/1021 for B, 1040/1041 for D, 1060 for F, 8000/8001/8010/8011/8020/8021/8100/8101 for secondary tasks, 7001-7019 for blocks).

## Data Quality Notes

- Missing demographic metadata: `subject_age`, `subject_sex`, and `device` fields are all missing from the dataset scan, limiting potential covariate analyses.
- Class imbalance in 6-class stimulus task: Stimulus E has only 15 trials versus ~2000+ for A/B/D, which will severely impact model training if not addressed.
- Moderate class imbalance in stimulus F: 469 trials versus ~1900-2200 for A/B/D.
- Structural event-level mismatch: secondary_80_onset (65 trials, block-level) vs secondary_81_onset (973 trials, trial-level) creates fundamentally different sampling structures that may confound the 80 vs 81 discrimination task.
- Slight onset-response count mismatches: e.g., stimulus_A_onset (2181) vs stimulus_A_response (2179), suggesting occasional missing responses or dropped events.
- Block marker counts vary slightly across blocks (62-65), indicating some subjects may be missing data for certain blocks.
- High sampling rate (2048 Hz) with 72 channels produces large file sizes; preprocessing and epoching will be computationally intensive.
- No known hardware or acquisition artifacts were detected in the automated scan, but manual review is pending to confirm data quality.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
