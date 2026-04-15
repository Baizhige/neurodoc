# TNO (Military Cognitive Workload)

## Paradigm

(See existing draft)

## File Scan Result

> **Kernel SHA256**: `c5dc3937add692a393a97efed66bd67f13ac6b2e75a2e44dbe45b44a1cf25dbb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `11001` | 42 | event | raw |  |
| `11002` | 42 | event | raw |  |
| `12101` | 165 | event | raw |  |
| `12102` | 166 | event | raw |  |
| `12201` | 166 | event | raw |  |
| `12202` | 168 | event | raw |  |
| `13001` | 3663 | event | raw |  |
| `13002` | 3663 | event | raw |  |
| `14111` | 9228 | event | raw |  |
| `14112` | 9228 | event | raw |  |
| `14121` | 1680 | event | raw |  |
| `14122` | 1680 | event | raw |  |
| `14211` | 42922 | event | raw |  |
| `14212` | 42922 | event | raw |  |
| `14231` | 1115 | event | raw |  |
| `14232` | 1115 | event | raw |  |
| `15111` | 1823 | event | raw |  |
| `15121` | 1840 | event | raw |  |
| `15211` | 1823 | event | raw |  |
| `15221` | 1840 | event | raw |  |
| `15311` | 1823 | event | raw |  |
| `15321` | 1840 | event | raw |  |
| `15411` | 1823 | event | raw |  |
| `15421` | 1840 | event | raw |  |
| `15511` | 1823 | event | raw |  |
| `15521` | 1840 | event | raw |  |
| `15611` | 1823 | event | raw |  |
| `15621` | 1840 | event | raw |  |
| `16101` | 1134 | event | raw |  |
| `16102` | 1134 | event | raw |  |
| `16201` | 689 | event | raw |  |
| `16202` | 689 | event | raw |  |
| `21111` | 9228 | event | raw |  |
| `21121` | 1115 | event | raw |  |
| `21201` | 3663 | event | raw |  |
| `21311` | 1134 | event | raw |  |
| `21321` | 689 | event | raw |  |
| `31202` | 3 | event | raw |  |
| `31301` | 2 | event | raw |  |
| `31302` | 2 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Cognitive Workload Level Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `13001` | 0 | Low workload condition |
| `13002` | 1 | Low workload condition variant |
| `14111` | 2 | Medium workload condition |
| `14112` | 3 | Medium workload condition variant |
| `14211` | 4 | High workload condition |
| `14212` | 5 | High workload condition variant |

- **Evidence**: TNO military cognitive workload study with hierarchically encoded task conditions. Source: https://openneuro.org/datasets/ds004660 DOI: https://doi.org/10.18112/openneuro.ds004660.v1.0.2
- **Kernel Notes**: 5-digit hierarchical code structure: first 2 digits (13, 14, 15) likely encode workload level category. High-count events (13001/13002: 3663, 14111/14112: 9228, 14211/14212: 42922) suggest progressive workload difficulty. Trigger decoding schema must be versioned per kernel responsibility guidelines.

### Normal Task 2: Task Type Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `12101` | 0 | Task type A - variant 1 |
| `12102` | 1 | Task type A - variant 2 |
| `12201` | 2 | Task type B - variant 1 |
| `12202` | 3 | Task type B - variant 2 |
| `21111` | 4 | Task type C |
| `21201` | 5 | Task type D |
| `21311` | 6 | Task type E |
| `21321` | 7 | Task type E variant |

- **Evidence**: Military-relevant paradigm with multiple task types encoded in 5-digit hierarchical scheme. TNO dataset documentation indicates surveillance/target detection dual-task conditions. Source: https://openneuro.org/datasets/ds004660 DOI: https://doi.org/10.18112/openneuro.ds004660.v1.0.2
- **Kernel Notes**: Events 121xx/122xx (medium counts ~165-168) likely represent subtask conditions within larger blocks. Events 21xxx likely encode secondary task conditions. Aggregation by first 2 digits may be required for practical classification.

### Potential Task 1: Secondary Task Performance Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `15111` | 0 | Secondary task condition 1 |
| `15121` | 1 | Secondary task condition 1 variant |
| `15211` | 2 | Secondary task condition 2 |
| `15221` | 3 | Secondary task condition 2 variant |
| `15311` | 4 | Secondary task condition 3 |
| `15321` | 5 | Secondary task condition 3 variant |
| `15411` | 6 | Secondary task condition 4 |
| `15421` | 7 | Secondary task condition 4 variant |
| `15511` | 8 | Secondary task condition 5 |
| `15521` | 9 | Secondary task condition 5 variant |
| `15611` | 10 | Secondary task condition 6 |
| `15621` | 11 | Secondary task condition 6 variant |

- **Evidence**: Plausible dual-task paradigm structure from hierarchical encoding pattern (15xxx series). Military workload studies commonly employ primary + secondary task paradigms.
- **Kernel Notes**: All 15xxx events have similar counts (~1823-1840), suggesting balanced experimental design across secondary task conditions. Paired variants (15111/15121, etc.) likely encode task parameter or difficulty within each condition type.

### Potential Task 2: Dual-Task Integration Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `14111` | 0 | Primary task only |
| `14121` | 1 | Primary + secondary dual-task |
| `15111` | 2 | Secondary task only |
| `14211` | 3 | High workload primary |
| `15511` | 4 | High workload secondary |

- **Evidence**: Paradigm description suggests dual-task/surveillance conditions. Cross-block event correlation analysis may reveal task integration patterns. TNO dataset documentation supports multi-task military workload paradigm.
- **Kernel Notes**: Requires super-meta integration across primary (14xxx) and secondary (15xxx) task blocks. Kernel Type 2 responsibilities apply - derive high-level labels not directly in raw events. Consider event co-occurrence patterns within trial windows for dual-task epoch labeling.

### Potential Task 3: Response Inhibition/Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `16101` | 0 | Response type 1 |
| `16102` | 1 | Response type 1 variant |
| `16201` | 2 | Response type 2 |
| `16202` | 3 | Response type 2 variant |

- **Evidence**: Response-locked events (161xx/162xx with counts ~689-1134) plausible as response markers in target detection paradigm.
- **Kernel Notes**: Event counts suggest response-locked markers rather than stimulus-locked. Consider separate epoching aligned to response onset if behavioral analysis required. Low count events (31202: 3, 31301: 2, 31302: 2) likely system markers - excluded from epoching.

