# T22 (Semi-Automated Driving Trust Paradigm)

**Dataset**: `openneuro_ds004844` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004844
**Category**: Complex Applied | **Subjects**: 68 | **Files (Completed)**: 68 | **Channels**: 72 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Simulated semi-automated driving in a leader-follower paradigm focused on predicting and influencing trust-based decisions regarding control authority hand-off and take-over between human and automation. EEG was recorded during sustained driving across multiple automation levels with varying driving conditions (adaptive cruise, manual, normal, slow, stopped). Event codes include both high-level semantic markers and 7-digit hierarchical identifiers encoding driving state and automation mode.

## File Scan Result

> **Kernel SHA256**: `73a9ee3558379d3ca8d7e3f011233c4e66ad62b0bd2b2038d80e74c34fcd323c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `automation_sustained` | 1003 | event | raw | Sustained automation period |
| `driving_state_adaptive_cruise` | 8978 | event | raw | Adaptive cruise control driving state |
| `driving_state_adaptive_cruise_extended` | 21 | event | raw | Extended adaptive cruise period |
| `driving_state_manual` | 9941 | event | raw | Manual driving state |
| `driving_state_normal` | 3231 | event | raw | Normal driving state |
| `driving_state_slow` | 2880 | event | raw | Slow speed driving state |
| `driving_state_stopped` | 1983 | event | raw | Stopped driving state |
| `event_1121001` | 1 | event | raw | Event marker |
| `event_1121002` | 1 | event | raw | Event marker |
| `event_1211001` | 566 | event | raw | Handoff event marker |
| `event_1211002` | 566 | event | raw | Handoff event marker |
| `event_1234001` | 545 | event | raw | Event marker |
| `event_1234002` | 545 | event | raw | Event marker |
| `event_1310002` | 963 | event | raw | Driving state marker (digit 1-3: automation level) |
| `event_1320001` | 940 | event | raw | Driving state marker |
| `event_1320002` | 940 | event | raw | Driving state marker |
| `event_1330001` | 362 | event | raw | Driving state marker |
| `event_1330002` | 362 | event | raw | Driving state marker |
| `event_1340001` | 356 | event | raw | Driving state marker |
| `event_1340002` | 356 | event | raw | Driving state marker |
| `event_1420001` | 1289 | event | raw | Driving state marker |
| `event_1420002` | 1289 | event | raw | Driving state marker |
| `event_1510001` | 729 | event | raw | Driving state marker |
| `event_1510002` | 729 | event | raw | Driving state marker |
| `event_1520001` | 566 | event | raw | Driving state marker |
| `event_1520002` | 566 | event | raw | Driving state marker |
| `event_2121001` | 17 | event | raw | Event marker |
| `event_2121002` | 17 | event | raw | Event marker |
| `event_2131001` | 50 | event | raw | Event marker |
| `event_2131002` | 50 | event | raw | Event marker |
| `event_2132001` | 1 | event | raw | Event marker |
| `event_2132002` | 1 | event | raw | Event marker |
| `event_2320001` | 1520 | event | raw | Driving state marker |
| `event_2320002` | 1520 | event | raw | Driving state marker |
| `event_2412212` | 566 | event | raw | Handoff event marker |
| `event_2422111` | 545 | event | raw | Event marker |
| `event_2422112` | 545 | event | raw | Event marker |
| `event_2532001` | 9 | event | raw | Event marker |
| `event_2542001` | 1179 | event | raw | Driving state marker |
| `event_2714112` | 1591 | event | raw | Takeover request event |
| `event_2714211` | 1289 | event | raw | Event marker |
| `event_2714212` | 1289 | event | raw | Event marker |
| `event_2724311` | 729 | event | raw | Event marker |
| `event_2724312` | 729 | event | raw | Event marker |
| `event_2724411` | 566 | event | raw | Event marker |
| `event_2724412` | 566 | event | raw | Event marker |
| `event_2734121` | 471 | event | raw | Event marker |
| `event_2734122` | 471 | event | raw | Event marker |
| `event_2734221` | 1512 | event | raw | Event marker |
| `event_2734222` | 1512 | event | raw | Event marker |
| `event_2744322` | 1003 | event | raw | Event marker |
| `event_2744421` | 1877 | event | raw | Event marker |
| `event_2744422` | 1877 | event | raw | Event marker |
| `event_2753021` | 21 | event | raw | Event marker |
| `event_2753022` | 21 | event | raw | Event marker |
| `event_2773031` | 9 | event | raw | Event marker |
| `event_2773032` | 9 | event | raw | Event marker |
| `event_2783031` | 1119 | event | raw | Event marker |
| `event_2783032` | 1119 | event | raw | Event marker |
| `event_2793032` | 69 | event | raw | Trust event extended |
| `event_2822001` | 676 | event | raw | Event marker |
| `event_2822002` | 676 | event | raw | Event marker |
| `event_2832001` | 673 | event | raw | Event marker |
| `event_2832002` | 673 | event | raw | Event marker |
| `event_2921001` | 271 | event | raw | Event marker |
| `event_2921002` | 271 | event | raw | Event marker |
| `event_2931001` | 269 | event | raw | Event marker |
| `event_2931002` | 269 | event | raw | Event marker |
| `event_3120001` | 676 | event | raw | Event marker |
| `event_3120002` | 676 | event | raw | Event marker |
| `event_3130001` | 673 | event | raw | Event marker |
| `event_3130002` | 673 | event | raw | Event marker |
| `event_3210001` | 1548 | event | raw | Event marker |
| `event_3210002` | 1548 | event | raw | Event marker |
| `event_3221001` | 810 | event | raw | Event marker |
| `event_3221002` | 810 | event | raw | Event marker |
| `event_3222001` | 269 | event | raw | Event marker |
| `event_3222002` | 269 | event | raw | Event marker |
| `event_3231001` | 134 | event | raw | Event marker |
| `event_3231002` | 134 | event | raw | Event marker |
| `event_3232001` | 270 | event | raw | Event marker |
| `event_3232002` | 270 | event | raw | Event marker |
| `event_3240001` | 202 | event | raw | Event marker |
| `event_3240002` | 202 | event | raw | Event marker |
| `event_4111201` | 923 | event | raw | Trust/decision event |
| `event_4112101` | 185 | event | raw | Trust/decision event |
| `event_4112201` | 17 | event | raw | Trust/decision event |
| `event_4112301` | 107 | event | raw | Trust/decision event |
| `event_4121101` | 594 | event | raw | Trust/decision event |
| `event_4121201` | 195 | event | raw | Trust/decision event |
| `event_4121301` | 1 | event | raw | Trust/decision event |
| `event_4122101` | 913 | event | raw | Trust/decision event |
| `event_4122201` | 37 | event | raw | Trust/decision event |
| `event_4122301` | 275 | event | raw | Trust/decision event |
| `event_4211301` | 539 | event | raw | Trust/decision event |
| `event_4222101` | 173 | event | raw | Trust/decision event |
| `event_4232101` | 229 | event | raw | Trust/decision event |
| `event_4242101` | 102 | event | raw | Trust/decision event |
| `event_4311001` | 12 | event | raw | Event marker |
| `event_4313001` | 9 | event | raw | Event marker |
| `event_4331001` | 3 | event | raw | Event marker |
| `event_4333001` | 6 | event | raw | Event marker |
| `full_automation_active` | 8716 | event | raw | Full automation mode active |
| `handoff_to_automation` | 566 | event | raw | Control handoff to automation |
| `manual_control_offset` | 1591 | event | raw | Manual control offset event |
| `manual_control_onset` | 1591 | event | raw | Manual control onset event |
| `partial_automation_active` | 1884 | event | raw | Partial automation mode active |
| `partial_automation_active_alt` | 1884 | event | raw | Partial automation mode active (alt marker) |
| `partial_automation_state_1` | 1884 | event | raw | Partial automation state 1 |
| `partial_automation_state_2` | 1884 | event | raw | Partial automation state 2 |
| `session_end` | 68 | event | raw | Recording session end |
| `session_start` | 68 | event | raw | Recording session start |
| `trust_critical_takeover_request` | 1591 | event | raw | Trust-critical takeover request |
| `trust_event_extended` | 69 | event | raw | Extended trust event |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

(No tasks could be synthesized.)

## Data Quality Notes

- High-level semantic event labels have been extracted (e.g., `driving_state_*`, `automation_*`, `trust_*`) alongside raw numeric codes.
- 7-digit hierarchical codes follow pattern: digits encode automation level, driving condition, and event subtype.
- All 68 subjects have complete recording sessions with session_start and session_end markers.
- Primary research focus is trust-critical hand-off and take-over events between human and automation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from event streams including both high-level semantic markers and 7-digit hierarchical identifiers.
- **Type 2 (Raw + Super meta integration)**: Derive automation level and driving condition categories from hierarchical event code structure.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels with reproducible schema for downstream classification tasks.

> **Selected Mode**: Type 1 + Type 2 + Type 3
> **Why**: Combination enables both raw marker preservation and high-level semantic labeling for trust-based driving classification tasks.