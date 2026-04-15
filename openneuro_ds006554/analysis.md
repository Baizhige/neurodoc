# Social Observation EEG Raw Data

**Dataset**: `openneuro_ds006554` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006554
**Category**: Complex Applied | **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

EEG was recorded while participants engaged in social observation tasks, likely involving ecological social stimuli such as videos or images of human social interactions. The dataset contains 55 distinct condition codes organized by tens-digit groupings (10s, 20s, 30s, 40s, 50s, 60s, 80s), suggesting a multi-factorial experimental design combining social conditions, stimulus types, and response categories. The paradigm appears designed to investigate neural correlates of social perception, mentalizing, and social cognition across 47 subjects.

## File Scan Result

> **Kernel SHA256**: `6c067a4038008f41ec790c6e02d14669379b3300d6c278260a0103129d61eba4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 6 | event | raw | Recording boundary marker |
| `condition_11` | 2820 | event | raw | Social observation condition 11 |
| `condition_12` | 3056 | event | raw | Social observation condition 12 |
| `condition_13` | 3051 | event | raw | Social observation condition 13 |
| `condition_14` | 2815 | event | raw | Social observation condition 14 |
| `condition_15` | 2819 | event | raw | Social observation condition 15 |
| `condition_16` | 3053 | event | raw | Social observation condition 16 |
| `condition_21` | 3054 | event | raw | Social observation condition 21 |
| `condition_22` | 2820 | event | raw | Social observation condition 22 |
| `condition_23` | 2821 | event | raw | Social observation condition 23 |
| `condition_24` | 3052 | event | raw | Social observation condition 24 |
| `condition_25` | 3052 | event | raw | Social observation condition 25 |
| `condition_26` | 2818 | event | raw | Social observation condition 26 |
| `condition_30` | 4097 | event | raw | Social observation condition 30 |
| `condition_31` | 3861 | event | raw | Social observation condition 31 |
| `condition_32` | 2942 | event | raw | Social observation condition 32 |
| `condition_33` | 2781 | event | raw | Social observation condition 33 |
| `condition_34` | 801 | event | raw | Social observation condition 34 |
| `condition_35` | 1392 | event | raw | Social observation condition 35 |
| `condition_36` | 1322 | event | raw | Social observation condition 36 |
| `condition_37` | 1542 | event | raw | Social observation condition 37 |
| `condition_38` | 1325 | event | raw | Social observation condition 38 |
| `condition_39` | 356 | event | raw | Social observation condition 39 |
| `condition_40` | 1818 | event | raw | Social observation condition 40 |
| `condition_41` | 1734 | event | raw | Social observation condition 41 |
| `condition_42` | 1797 | event | raw | Social observation condition 42 |
| `condition_43` | 1668 | event | raw | Social observation condition 43 |
| `condition_44` | 384 | event | raw | Social observation condition 44 |
| `condition_45` | 1576 | event | raw | Social observation condition 45 |
| `condition_46` | 1497 | event | raw | Social observation condition 46 |
| `condition_47` | 1402 | event | raw | Social observation condition 47 |
| `condition_48` | 1445 | event | raw | Social observation condition 48 |
| `condition_49` | 758 | event | raw | Social observation condition 49 |
| `condition_51` | 1867 | event | raw | Social observation condition 51 |
| `condition_60` | 4578 | event | raw | Social observation condition 60 |
| `condition_61` | 4397 | event | raw | Social observation condition 61 |
| `condition_62` | 3408 | event | raw | Social observation condition 62 |
| `condition_63` | 3266 | event | raw | Social observation condition 63 |
| `condition_64` | 872 | event | raw | Social observation condition 64 |
| `condition_65` | 707 | event | raw | Social observation condition 65 |
| `condition_66` | 663 | event | raw | Social observation condition 66 |
| `condition_67` | 1755 | event | raw | Social observation condition 67 |
| `condition_68` | 2611 | event | raw | Social observation condition 68 |
| `condition_69` | 289 | event | raw | Social observation condition 69 |
| `condition_80` | 1334 | event | raw | Social observation condition 80 |
| `condition_81` | 1257 | event | raw | Social observation condition 81 |
| `condition_82` | 1316 | event | raw | Social observation condition 82 |
| `condition_83` | 1252 | event | raw | Social observation condition 83 |
| `condition_84` | 308 | event | raw | Social observation condition 84 |
| `condition_85` | 720 | event | raw | Social observation condition 85 |
| `condition_86` | 680 | event | raw | Social observation condition 86 |
| `condition_87` | 2762 | event | raw | Social observation condition 87 |
| `condition_88` | 1668 | event | raw | Social observation condition 88 |
| `condition_89` | 828 | event | raw | Social observation condition 89 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Social Condition Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, baseline = (None, 0), target_events = ["condition_11", "condition_12", "condition_13", "condition_14", "condition_15", "condition_16", "condition_21", "condition_22", "condition_23", "condition_24", "condition_25", "condition_26", "condition_30", "condition_31", "condition_32", "condition_33", "condition_35", "condition_36", "condition_37", "condition_42", "condition_43", "condition_48", "condition_60", "condition_61", "condition_62", "condition_63", "condition_67", "condition_68", "condition_87", "condition_88"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| condition_11 | 0 | Social condition 11 |
| condition_12 | 1 | Social condition 12 |
| condition_13 | 2 | Social condition 13 |
| condition_14 | 3 | Social condition 14 |
| condition_15 | 4 | Social condition 15 |
| condition_16 | 5 | Social condition 16 |
| condition_21 | 6 | Social condition 21 |
| condition_22 | 7 | Social condition 22 |
| condition_23 | 8 | Social condition 23 |
| condition_24 | 9 | Social condition 24 |
| condition_25 | 10 | Social condition 25 |
| condition_26 | 11 | Social condition 26 |
| condition_30 | 12 | Social condition 30 |
| condition_31 | 13 | Social condition 31 |
| condition_32 | 14 | Social condition 32 |
| condition_33 | 15 | Social condition 33 |
| condition_35 | 16 | Social condition 35 |
| condition_36 | 17 | Social condition 36 |
| condition_37 | 18 | Social condition 37 |
| condition_42 | 19 | Social condition 42 |
| condition_43 | 20 | Social condition 43 |
| condition_48 | 21 | Social condition 48 |
| condition_60 | 22 | Social condition 60 |
| condition_61 | 23 | Social condition 61 |
| condition_62 | 24 | Social condition 62 |
| condition_63 | 25 | Social condition 63 |
| condition_67 | 26 | Social condition 67 |
| condition_68 | 27 | Social condition 68 |
| condition_87 | 28 | Social condition 87 |
| condition_88 | 29 | Social condition 88 |

- **Evidence**: None (no reference papers available)
- **Kernel Notes**: Social observation paradigm with 30 distinct condition codes. The tens-digit grouping (10s, 20s, 30s, 60s, 80s) may represent factor levels (e.g., stimulus type × emotion × viewpoint). Consider reduced-class grouping for hierarchical classification. Perfectly balanced design across 47 subjects supports cross-subject decoding. Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.