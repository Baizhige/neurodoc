# HID (High-Density EEG Operational Dataset)

**Dataset**: `openneuro_ds004851` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004851
**Category**: Complex Applied | **Subjects**: 65 | **Files (Completed)**: 65 | **Channels**: 72 | **Sampling Rate**: 2048 Hz
**Manual Review**: Pending

## Paradigm

High-density EEG (72 channels) recorded in an operational context involving multiple stimulus categories encoded as hierarchical event codes. The paradigm includes primary stimulus presentations (types A–F) with onset/response event pairs, secondary stimulus categories (80/81 series), and block-level markers (01–19) indicating experimental structure. Subjects performed cognitive tasks under varying workload conditions with both trial-level and block-level event markers.

## File Scan Result

> **Kernel SHA256**: `0bf1ebd0422e86e94f0e912a9e166ca58503dcc3693f700d733fb6511e2ef2e5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `HID: block_marker_01` | 65 | event | raw | Block marker identifier 01 |
| `HID: block_marker_02` | 65 | event | raw | Block marker identifier 02 |
| `HID: block_marker_03` | 65 | event | raw | Block marker identifier 03 |
| `HID: block_marker_04` | 65 | event | raw | Block marker identifier 04 |
| `HID: block_marker_05` | 65 | event | raw | Block marker identifier 05 |
| `HID: block_marker_06` | 65 | event | raw | Block marker identifier 06 |
| `HID: block_marker_07` | 65 | event | raw | Block marker identifier 07 |
| `HID: block_marker_08` | 65 | event | raw | Block marker identifier 08 |
| `HID: block_marker_09` | 65 | event | raw | Block marker identifier 09 |
| `HID: block_marker_10` | 64 | event | raw | Block marker identifier 10 |
| `HID: block_marker_11` | 65 | event | raw | Block marker identifier 11 |
| `HID: block_marker_12` | 65 | event | raw | Block marker identifier 12 |
| `HID: block_marker_13` | 65 | event | raw | Block marker identifier 13 |
| `HID: block_marker_14` | 65 | event | raw | Block marker identifier 14 |
| `HID: block_marker_15` | 63 | event | raw | Block marker identifier 15 |
| `HID: block_marker_16` | 63 | event | raw | Block marker identifier 16 |
| `HID: block_marker_17` | 63 | event | raw | Block marker identifier 17 |
| `HID: block_marker_18` | 62 | event | raw | Block marker identifier 18 |
| `HID: block_marker_19` | 62 | event | raw | Block marker identifier 19 |
| `HID: secondary_80A_onset` | 195 | event | raw | Secondary stimulus 80A onset |
| `HID: secondary_80A_response` | 195 | event | raw | Secondary stimulus 80A response |
| `HID: secondary_80B_onset` | 194 | event | raw | Secondary stimulus 80B onset |
| `HID: secondary_80B_response` | 194 | event | raw | Secondary stimulus 80B response |
| `HID: secondary_80_onset` | 65 | event | raw | Secondary stimulus 80 block-level onset |
| `HID: secondary_80_response` | 64 | event | raw | Secondary stimulus 80 block-level response |
| `HID: secondary_81_onset` | 973 | event | raw | Secondary stimulus 81 trial-level onset |
| `HID: secondary_81_response` | 973 | event | raw | Secondary stimulus 81 trial-level response |
| `HID: stimulus_A_onset` | 2181 | event | raw | Primary stimulus type A onset |
| `HID: stimulus_A_response` | 2179 | event | raw | Primary stimulus type A response |
| `HID: stimulus_B_onset` | 1970 | event | raw | Primary stimulus type B onset |
| `HID: stimulus_B_response` | 1970 | event | raw | Primary stimulus type B response |
| `HID: stimulus_C_onset` | 204 | event | raw | Primary stimulus type C onset |
| `HID: stimulus_C_response` | 204 | event | raw | Primary stimulus type C response |
| `HID: stimulus_D_onset` | 1912 | event | raw | Primary stimulus type D onset |
| `HID: stimulus_D_response` | 1912 | event | raw | Primary stimulus type D response |
| `HID: stimulus_E_onset` | 15 | event | raw | Primary stimulus type E onset |
| `HID: stimulus_E_response` | 15 | event | raw | Primary stimulus type E response |
| `HID: stimulus_F_onset` | 469 | event | raw | Primary stimulus type F onset |
| `HID: stimulus_F_response` | 469 | event | raw | Primary stimulus type F response |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Primary Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`HID: stimulus_A_onset`, `HID: stimulus_B_onset`, `HID: stimulus_C_onset`, `HID: stimulus_D_onset`, `HID: stimulus_E_onset`, `HID: stimulus_F_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HID: stimulus_A_onset` | 0 | Primary stimulus type A |
  | `HID: stimulus_B_onset` | 1 | Primary stimulus type B |
  | `HID: stimulus_C_onset` | 2 | Primary stimulus type C |
  | `HID: stimulus_D_onset` | 3 | Primary stimulus type D |
  | `HID: stimulus_E_onset` | 4 | Primary stimulus type E |
  | `HID: stimulus_F_onset` | 5 | Primary stimulus type F |
- **Evidence**: DOI not available — task defined based on paradigm structure and epoch alignment recommendations from kernel analysis
- **Kernel Notes**: 6-class stimulus classification from operational paradigm. Counts range from 15 (E) to 2181 (A) — imbalanced dataset requiring careful stratification. Recommend baseline correction using -0.2 to 0 s interval. Onset/response event pairs available for validation. High sampling rate (2048 Hz) — consider anti-aliasing filter before epoching.

### Potential Task 2: Secondary Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`HID: secondary_81_onset`, `HID: secondary_80A_onset`, `HID: secondary_80B_onset`, `HID: secondary_80_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HID: secondary_81_onset` | 0 | Secondary stimulus category 81 (trial-level, 973x) |
  | `HID: secondary_80A_onset` | 1 | Secondary stimulus category 80A (195x) |
  | `HID: secondary_80B_onset` | 2 | Secondary stimulus category 80B (194x) |
  | `HID: secondary_80_onset` | 3 | Secondary stimulus category 80 block marker (65x) |
- **Evidence**: DOI not available — task defined based on paradigm structure and epoch alignment recommendations
- **Kernel Notes**: 4-class secondary stimulus classification. secondary_81_onset is trial-level (973x); secondary_80_onset is block-level (65x) and may require separate handling. secondary_80A/B are trial-level with 194-195 counts. Event codes 8xxx map to secondary stimulus categories per paradigm description. Response events available for validation analysis.

### Potential Task 3: Block-Level Marker Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 5.0 s, target_events = [`HID: block_marker_01` through `HID: block_marker_19`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HID: block_marker_01` through `HID: block_marker_19` | 0–18 | Block identifier (19 distinct blocks) |
- **Evidence**: DOI not available — task defined based on kernel event analysis showing 70xx codes (7001-7019) appear exactly 65 times (once per subject)
- **Kernel Notes**: Block markers at 7001-7019 occur once per subject (65x) indicating trial design structure. Long epoch window allows analysis of block-level state transitions and sustained cognitive workload effects. Do NOT include in stimulus-level epoching — separate handling required per epoch alignment complications.