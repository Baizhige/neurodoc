# InsurgentCivilian (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004852` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004852
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz
**Manual Review**: Pending

## Paradigm

An EEG dataset recorded during a dual-paradigm session combining Nback working memory tasks (event IDs 2090-2098) with social-cognitive threat detection (insurgent/civilian classification). The high event count for code 2200 (n=1627) suggests stimulus recycling or re-display within trials. Single aggregated file prevents per-subject separation. Shares structural similarities with companion datasets ds004849 and ds004850 based on similar event code patterns. Low sampling rate (128 Hz) limits fine-grained ERP analysis but supports classification-level features.

## File Scan Result

> **Kernel SHA256**: `0e385a62ce3257d5b19414ec65ae879560a1369d20d64b27ce775596df5ae917`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 195 | event | raw | Response/button press event |
| `1103` | 120 | event | raw | Task-related marker |
| `1113` | 75 | event | raw | Task-related marker |
| `2090` | 66 | event | raw | 0-back condition |
| `2091` | 114 | event | raw | 1-back condition |
| `2092` | 96 | event | raw | 2-back condition |
| `2093` | 124 | event | raw | 3-back condition |
| `2094` | 90 | event | raw | 4-back condition |
| `2095` | 86 | event | raw | 5-back condition |
| `2096` | 111 | event | raw | 6-back condition |
| `2097` | 109 | event | raw | 7-back condition |
| `2098` | 104 | event | raw | 8-back condition |
| `2200` | 1627 | event | raw | Dominant stimulus code (recycling/re-display) |
| `2201` | 173 | event | raw | Primary condition code (variant) |
| `3` | 15 | event | raw | Administration event |
| `307` | 1 | event | raw | Rare administration marker |
| `4` | 15 | event | raw | Administration event |
| `5` | 32 | event | raw | Administration event |
| `51001` | 5 | event | raw | Category 5 sub-condition |
| `51011` | 170 | event | raw | Category 5 stimulus variant |
| `51110` | 19 | event | raw | Category 5 sub-condition |
| `52001` | 16 | event | raw | Category 5 sub-condition |
| `52011` | 332 | event | raw | Category 5 stimulus |
| `52100` | 1 | event | raw | Category 5 sub-condition |
| `52101` | 1 | event | raw | Category 5 sub-condition |
| `52110` | 14 | event | raw | Category 5 sub-condition |
| `52111` | 21 | event | raw | Category 5 sub-condition |
| `53001` | 34 | event | raw | Category 5 sub-condition |
| `53011` | 308 | event | raw | Category 5 stimulus |
| `53100` | 3 | event | raw | Category 5 sub-condition |
| `53110` | 19 | event | raw | Category 5 sub-condition |
| `53111` | 16 | event | raw | Category 5 sub-condition |
| `54001` | 41 | event | raw | Category 5 sub-condition |
| `54011` | 307 | event | raw | Category 5 stimulus |
| `54100` | 3 | event | raw | Category 5 sub-condition |
| `54101` | 2 | event | raw | Category 5 sub-condition |
| `54110` | 16 | event | raw | Category 5 sub-condition |
| `54111` | 13 | event | raw | Category 5 sub-condition |
| `55000` | 1 | event | raw | Category 5 sub-condition |
| `55001` | 36 | event | raw | Category 5 sub-condition |
| `55010` | 1 | event | raw | Category 5 sub-condition |
| `55011` | 317 | event | raw | Category 5 stimulus |
| `55100` | 2 | event | raw | Category 5 sub-condition |
| `55101` | 3 | event | raw | Category 5 sub-condition |
| `55110` | 19 | event | raw | Category 5 sub-condition |
| `55111` | 16 | event | raw | Category 5 sub-condition |
| `71001` | 6 | event | raw | Category 7 sub-condition |
| `71011` | 174 | event | raw | Category 7 stimulus variant |
| `71110` | 19 | event | raw | Category 7 sub-condition |
| `72001` | 19 | event | raw | Category 7 sub-condition |
| `72011` | 338 | event | raw | Category 7 stimulus |
| `72100` | 1 | event | raw | Category 7 sub-condition |
| `72101` | 1 | event | raw | Category 7 sub-condition |
| `72110` | 14 | event | raw | Category 7 sub-condition |
| `72111` | 21 | event | raw | Category 7 sub-condition |
| `73001` | 38 | event | raw | Category 7 sub-condition |
| `73011` | 316 | event | raw | Category 7 stimulus variant |
| `73100` | 3 | event | raw | Category 7 sub-condition |
| `73110` | 19 | event | raw | Category 7 sub-condition |
| `73111` | 16 | event | raw | Category 7 sub-condition |
| `74001` | 43 | event | raw | Category 7 sub-condition |
| `74011` | 312 | event | raw | Category 7 stimulus variant |
| `74100` | 3 | event | raw | Category 7 sub-condition |
| `74101` | 2 | event | raw | Category 7 sub-condition |
| `74110` | 16 | event | raw | Category 7 sub-condition |
| `74111` | 14 | event | raw | Category 7 sub-condition |
| `75000` | 1 | event | raw | Category 7 sub-condition |
| `75001` | 40 | event | raw | Category 7 sub-condition |
| `75010` | 1 | event | raw | Category 7 sub-condition |
| `75011` | 320 | event | raw | Category 7 stimulus variant |
| `75100` | 2 | event | raw | Category 7 sub-condition |
| `75101` | 3 | event | raw | Category 7 sub-condition |
| `75110` | 19 | event | raw | Category 7 sub-condition |
| `75111` | 16 | event | raw | Category 7 sub-condition |
| `boundary` | 8 | event | raw | Segment boundary marker (data concatenation) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Nback Working Memory Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `2090` | 0 | 0-back condition |
| `2091` | 1 | 1-back condition |
| `2092` | 2 | 2-back condition |
| `2093` | 3 | 3-back condition |
| `2094` | 4 | 4-back condition |
| `2095` | 5 | 5-back condition |
| `2096` | 6 | 6-back condition |
| `2097` | 7 | 7-back condition |
| `2098` | 8 | 8-back condition |

- **Evidence**: OpenNeuro BIDS metadata confirms Nback task structure; event IDs 2090-2098 (counts 66-124) consistent with Nback condition encoding. DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: The 2090-2098 series provides balanced trial counts across conditions (66-124 range), consistent with Nback working memory paradigm. Single aggregated file prevents per-subject separation. Low sampling rate (128 Hz) may limit temporal precision for fine-grained ERP analysis but is sufficient for classification-level features.

### Classical Task 2: Stimulus Category Classification (Insurgent vs Civilian)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [72011, 52011, 75011, 55011, 73011, 74011, 53011, 54011, 71011, 51011, 2201]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `72011` | 0 | Category 7 stimulus (insurgent/civilian threat) |
| `52011` | 1 | Category 5 stimulus |
| `75011` | 2 | Category 7 stimulus variant |
| `55011` | 3 | Category 5 stimulus variant |
| `73011` | 4 | Category 7 stimulus variant |
| `74011` | 5 | Category 7 stimulus variant |
| `53011` | 6 | Category 5 stimulus variant |
| `54011` | 7 | Category 5 stimulus variant |
| `71011` | 8 | Category 7 stimulus variant |
| `51011` | 9 | Category 5 stimulus variant |
| `2201` | 10 | Primary condition code variant |

- **Evidence**: Paradigm described as social-cognitive threat detection (insurgent/civilian classification) on OpenNeuro. DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: Event codes 72xxx and 52xxx likely encode stimulus categories for threat detection. Balanced counts (~300 each) indicate multi-class classification design. Excludes dominant recycling code 2200 (n=1627). Cross-reference with companion datasets ds004849 (STRONG) and ds004850 (ODE) which share identical event structure.

### Normal Task 3: Response-related Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.5 s, target_events = [1]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `1` | 0 | Response/button press event |

- **Evidence**: Event ID 1 with count 195 (n=195) is consistent with response events in threat-detection paradigms (participant button press to classify stimulus as insurgent/civilian). DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: Response events provide trial-level accuracy information when aligned with stimulus events. May enable response-locked ERP analysis (N200, P300 components) for evaluating decision-making processes. Count of 195 suggests ~195 valid trials across all conditions.

### Potential Task 4: Mixed Stimulus Lock Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [2200]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `2200` | 0 | Dominant stimulus code (recycling/re-display) |

- **Evidence**: Event 2200 with 1627 occurrences suggests repeated stimulus presentation within trials (recycling/re-display). DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: High event count for 2200 (n=1627) indicates non-standard trial structure—likely stimulus recycling within Nback trials. May require trial-epoch alignment correction. Excluded from primary stimulus classification analysis due to ambiguity.

### Potential Task 5: Administrative Event Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.1 s, target_events = [3, 4, 5]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `3` | 0 | Administration event |
| `4` | 1 | Administration event |
| `5` | 2 | Administration event |

- **Evidence**: Events 3 (n=15), 4 (n=15), 5 (n=32) likely represent experiment control markers. DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: Low-count events flagged as 'admin' type in paradigm scan. Should be excluded from primary classification but retained for artifact annotation and data quality verification.

### Potential Task 6: Boundary Event Analysis
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 s, target_events = [boundary]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `boundary` | 0 | Segment boundary marker |

- **Evidence**: 8 boundary events indicate data concatenation points requiring segmentation alignment. DOI: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
- **Kernel Notes**: Boundary events require special handling during epoch extraction. Recommend epoch exclusion or flagging near boundary regions to prevent artifact contamination from concatenation.