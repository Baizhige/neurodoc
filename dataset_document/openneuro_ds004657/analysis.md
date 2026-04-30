# Driving with Autonomous Aids

**Dataset**: `openneuro_ds004657` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004657
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 119 | **Channels**: 74 | **Sampling Rate**: 1024 Hz | **Manual Review**: Pending

## Paradigm

Participants performed a semi-automated driving task involving lane maintenance and collision avoidance to evaluate human trust in automation across manual and varying autonomous assistance conditions. The study used a high-density EEG system (74 channels) at 1024 Hz sampling rate to capture neural correlates of mental workload during different road scenarios. The 7-digit hierarchical trigger codes encode driving condition, task phase, and condition variant, with dominant codes (231, 411) representing primary road types and lower-frequency codes representing complex intersection or high-traffic scenarios.

## File Scan Result

> **Kernel SHA256**: `b679e822b19f01636c5c85db16529502472020a1b36962ac3697fdae63407672`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Driving 1110001` | 105 | event | raw | Driving condition 111, variant 1 (main road, low traffic) |
| `Driving 1110002` | 105 | event | raw | Driving condition 111, variant 2 (main road, low traffic) |
| `Driving 1120001` | 3 | event | raw | Driving condition 112, variant 1 (main road variant) |
| `Driving 1120002` | 3 | event | raw | Driving condition 112, variant 2 (main road variant) |
| `Driving 1211001` | 651 | event | raw | Driving condition 121, variant 1 (urban road) |
| `Driving 1211002` | 651 | event | raw | Driving condition 121, variant 2 (urban road) |
| `Driving 1222001` | 107 | event | raw | Driving condition 122, variant 1 (urban road variant) |
| `Driving 1222002` | 107 | event | raw | Driving condition 122, variant 2 (urban road variant) |
| `Driving 1223001` | 173 | event | raw | Driving condition 122, variant 3 (urban road variant) |
| `Driving 1223002` | 173 | event | raw | Driving condition 122, variant 4 (urban road variant) |
| `Driving 1232001` | 115 | event | raw | Driving condition 123, variant 1 (urban road high density) |
| `Driving 1232002` | 115 | event | raw | Driving condition 123, variant 2 (urban road high density) |
| `Driving 1233001` | 189 | event | raw | Driving condition 123, variant 3 (urban road high density) |
| `Driving 1233002` | 189 | event | raw | Driving condition 123, variant 4 (urban road high density) |
| `Driving 1310001` | 1041 | event | raw | Driving condition 131, variant 1 (secondary road normal) |
| `Driving 1310002` | 1041 | event | raw | Driving condition 131, variant 2 (secondary road normal) |
| `Driving 132 V1` | 1175 | event | raw | Driving condition 132, variant 1 (high-traffic urban) |
| `Driving 132 V2` | 1175 | event | raw | Driving condition 132, variant 2 (high-traffic urban) |
| `Driving 1330001` | 436 | event | raw | Driving condition 133, variant 1 (urban intersection) |
| `Driving 1330002` | 436 | event | raw | Driving condition 133, variant 2 (urban intersection) |
| `Driving 1340001` | 432 | event | raw | Driving condition 134, variant 1 (urban complex) |
| `Driving 1340002` | 432 | event | raw | Driving condition 134, variant 2 (urban complex) |
| `Driving 141 V1` | 1383 | event | raw | Driving condition 141, variant 1 (complex intersection) |
| `Driving 141 V2` | 1383 | event | raw | Driving condition 141, variant 2 (complex intersection) |
| `Driving 142 V1` | 1226 | event | raw | Driving condition 142, variant 1 (secondary road variant) |
| `Driving 142 V2` | 1226 | event | raw | Driving condition 142, variant 2 (secondary road variant) |
| `Driving 1510001` | 256 | event | raw | Driving condition 151, variant 1 (secondary road) |
| `Driving 1510002` | 256 | event | raw | Driving condition 151, variant 2 (secondary road) |
| `Driving 1520001` | 475 | event | raw | Driving condition 152, variant 1 (secondary road) |
| `Driving 1520002` | 475 | event | raw | Driving condition 152, variant 2 (secondary road) |
| `Driving 2121001` | 22 | event | raw | Driving condition 212, variant 1 (highway) |
| `Driving 2121002` | 22 | event | raw | Driving condition 212, variant 2 (highway) |
| `Driving 2122001` | 1 | event | raw | Driving condition 212, variant 3 (highway variant) |
| `Driving 2122002` | 1 | event | raw | Driving condition 212, variant 4 (highway variant) |
| `Driving 2131001` | 79 | event | raw | Driving condition 213, variant 1 (highway) |
| `Driving 2131002` | 79 | event | raw | Driving condition 213, variant 2 (highway) |
| `Driving 2132001` | 1 | event | raw | Driving condition 213, variant 3 (highway variant) |
| `Driving 2132002` | 1 | event | raw | Driving condition 213, variant 4 (highway variant) |
| `Driving 231 V1` | 10367 | event | raw | Driving condition 231, variant 1 (main road, normal traffic) |
| `Driving 231 V2` | 10367 | event | raw | Driving condition 231, variant 2 (main road, normal traffic) |
| `Driving 232 V1` | 1819 | event | raw | Driving condition 232, variant 1 (secondary road, rush hour) |
| `Driving 232 V2` | 1819 | event | raw | Driving condition 232, variant 2 (secondary road, rush hour) |
| `Driving 2411021` | 651 | event | raw | Driving condition 241, variant 021 (complex scenario) |
| `Driving 2411022` | 651 | event | raw | Driving condition 241, variant 022 (complex scenario) |
| `Driving 2421011` | 584 | event | raw | Driving condition 242, variant 011 (complex scenario) |
| `Driving 2421012` | 584 | event | raw | Driving condition 242, variant 012 (complex scenario) |
| `Driving 2511001` | 124 | event | raw | Driving condition 251, variant 1 (secondary road) |
| `Driving 2521001` | 5 | event | raw | Driving condition 252, variant 1 (secondary road) |
| `Driving 2531001` | 16 | event | raw | Driving condition 253, variant 1 (secondary road) |
| `Driving 254 V1` | 1174 | event | raw | Driving condition 254, variant 1 (secondary road high traffic) |
| `Driving 2551001` | 693 | event | raw | Driving condition 255, variant 1 (secondary road) |
| `Driving 256 V1` | 1081 | event | raw | Driving condition 256, variant 1 (secondary road) |
| `Driving 2571001` | 917 | event | raw | Driving condition 257, variant 1 (secondary road) |
| `Driving 2611001` | 714 | event | raw | Driving condition 261, variant 1 (complex scenario) |
| `Driving 2611002` | 714 | event | raw | Driving condition 261, variant 2 (complex scenario) |
| `Driving 2622001` | 256 | event | raw | Driving condition 262, variant 1 (complex scenario) |
| `Driving 2622002` | 256 | event | raw | Driving condition 262, variant 2 (complex scenario) |
| `Driving 2632001` | 475 | event | raw | Driving condition 263, variant 1 (complex scenario) |
| `Driving 2632002` | 475 | event | raw | Driving condition 263, variant 2 (complex scenario) |
| `Driving 2731121` | 292 | event | raw | Driving condition 273, variant 121 (complex intersection) |
| `Driving 2731122` | 292 | event | raw | Driving condition 273, variant 122 (complex intersection) |
| `Driving 2731221` | 401 | event | raw | Driving condition 273, variant 221 (complex intersection) |
| `Driving 2731222` | 401 | event | raw | Driving condition 273, variant 222 (complex intersection) |
| `Driving 2741321` | 54 | event | raw | Driving condition 274, variant 321 (complex scenario) |
| `Driving 2741322` | 54 | event | raw | Driving condition 274, variant 322 (complex scenario) |
| `Driving 2741421` | 1027 | event | raw | Driving condition 274, variant 421 (complex scenario) |
| `Driving 2741422` | 1027 | event | raw | Driving condition 274, variant 422 (complex scenario) |
| `Driving 2751021` | 124 | event | raw | Driving condition 275, variant 021 (complex scenario) |
| `Driving 2751022` | 124 | event | raw | Driving condition 275, variant 022 (complex scenario) |
| `Driving 2752021` | 124 | event | raw | Driving condition 275, variant 021 (secondary scenario) |
| `Driving 2752022` | 124 | event | raw | Driving condition 275, variant 022 (secondary scenario) |
| `Driving 2761021` | 5 | event | raw | Driving condition 276, variant 021 (complex scenario) |
| `Driving 2761022` | 5 | event | raw | Driving condition 276, variant 022 (complex scenario) |
| `Driving 2762021` | 5 | event | raw | Driving condition 276, variant 021 (secondary scenario) |
| `Driving 2762022` | 5 | event | raw | Driving condition 276, variant 022 (secondary scenario) |
| `Driving 2771021` | 16 | event | raw | Driving condition 277, variant 021 (complex scenario) |
| `Driving 2771022` | 16 | event | raw | Driving condition 277, variant 022 (complex scenario) |
| `Driving 2772021` | 16 | event | raw | Driving condition 277, variant 021 (secondary scenario) |
| `Driving 2772022` | 16 | event | raw | Driving condition 277, variant 022 (secondary scenario) |
| `Driving 278 V021` | 1094 | event | raw | Driving condition 278, variant 021 (complex urban) |
| `Driving 278 V022` | 1094 | event | raw | Driving condition 278, variant 022 (complex urban) |
| `Driving 2791021` | 104 | event | raw | Driving condition 279, variant 021 (complex scenario) |
| `Driving 2791022` | 104 | event | raw | Driving condition 279, variant 022 (complex scenario) |
| `Driving 2801001` | 919 | event | raw | Driving condition 280, variant 1 (complex scenario) |
| `Driving 2801002` | 919 | event | raw | Driving condition 280, variant 2 (complex scenario) |
| `Driving 3100001` | 919 | event | raw | Driving condition 310, variant 1 (highway) |
| `Driving 3100002` | 919 | event | raw | Driving condition 310, variant 2 (highway) |
| `Driving 411 V1` | 10051 | event | raw | Driving condition 411, variant 1 (highway segment) |
| `Driving 4111201` | 871 | event | raw | Driving condition 411, sub-condition 12, variant 01 |
| `Driving 4111301` | 1 | event | raw | Driving condition 411, sub-condition 13, variant 01 |
| `Driving 4112101` | 199 | event | raw | Driving condition 411, sub-condition 21, variant 01 |
| `Driving 4112201` | 41 | event | raw | Driving condition 411, sub-condition 22, variant 01 |
| `Driving 4112301` | 151 | event | raw | Driving condition 411, sub-condition 23, variant 01 |
| `Driving 4121101` | 937 | event | raw | Driving condition 412, sub-condition 11, variant 01 |
| `Driving 4121201` | 223 | event | raw | Driving condition 412, sub-condition 12, variant 01 |
| `Driving 4122101` | 795 | event | raw | Driving condition 412, sub-condition 21, variant 01 |
| `Driving 4122201` | 23 | event | raw | Driving condition 412, sub-condition 22, variant 01 |
| `Driving 4122301` | 313 | event | raw | Driving condition 412, sub-condition 23, variant 01 |
| `Driving 4211201` | 276 | event | raw | Driving condition 421, sub-condition 12, variant 01 |
| `Driving 4211301` | 300 | event | raw | Driving condition 421, sub-condition 13, variant 01 |
| `Driving 4222101` | 336 | event | raw | Driving condition 422, sub-condition 21, variant 01 |
| `Driving 4232101` | 200 | event | raw | Driving condition 423, sub-condition 21, variant 01 |
| `Driving 4242101` | 20 | event | raw | Driving condition 424, sub-condition 21, variant 01 |
| `Driving 4311001` | 72 | event | raw | Driving condition 431, variant 1 (complex intersection) |
| `Driving 4312001` | 19 | event | raw | Driving condition 431, variant 2 (complex intersection) |
| `Driving 4313001` | 33 | event | raw | Driving condition 431, variant 3 (complex intersection) |
| `Driving 4322001` | 2 | event | raw | Driving condition 432, variant 1 (complex intersection) |
| `Driving 4323001` | 3 | event | raw | Driving condition 432, variant 2 (complex intersection) |
| `Driving 4331001` | 10 | event | raw | Driving condition 433, variant 1 (complex intersection) |
| `Driving 4332001` | 3 | event | raw | Driving condition 433, variant 2 (complex intersection) |
| `Driving 4333001` | 3 | event | raw | Driving condition 433, variant 3 (complex intersection) |
| `Driving 6110001` | 16 | event | raw | Driving condition 611, variant 1 (autonomous aid) |
| `Driving 6110002` | 16 | event | raw | Driving condition 611, variant 2 (autonomous aid) |
| `Driving 6220001` | 16 | event | raw | Driving condition 622, variant 1 (autonomous aid) |
| `Driving 6220002` | 16 | event | raw | Driving condition 622, variant 2 (autonomous aid) |
| `Driving 6230001` | 16 | event | raw | Driving condition 623, variant 1 (autonomous aid) |
| `Driving 6230002` | 16 | event | raw | Driving condition 623, variant 2 (autonomous aid) |
| `Driving 6240001` | 16 | event | raw | Driving condition 624, variant 1 (autonomous aid) |
| `Driving 6240002` | 16 | event | raw | Driving condition 624, variant 2 (autonomous aid) |
| `Driving 6321101` | 320 | event | raw | Driving condition 632, sub-condition 11, variant 01 |
| `Driving 6321102` | 320 | event | raw | Driving condition 632, sub-condition 11, variant 02 |
| `Driving 6321201` | 320 | event | raw | Driving condition 632, sub-condition 12, variant 01 |
| `Driving 6321202` | 320 | event | raw | Driving condition 632, sub-condition 12, variant 02 |
| `Driving 6331101` | 80 | event | raw | Driving condition 633, sub-condition 11, variant 01 |
| `Driving 6331201` | 80 | event | raw | Driving condition 633, sub-condition 12, variant 01 |
| `Driving 6331301` | 80 | event | raw | Driving condition 633, sub-condition 13, variant 01 |
| `Driving 6331401` | 80 | event | raw | Driving condition 633, sub-condition 14, variant 01 |
| `Driving 6341001` | 320 | event | raw | Driving condition 634, sub-condition 10, variant 01 |
| `Driving 6342001` | 320 | event | raw | Driving condition 634, sub-condition 20, variant 01 |
| `Driving 6343001` | 320 | event | raw | Driving condition 634, sub-condition 30, variant 01 |
| `Driving 6344001` | 320 | event | raw | Driving condition 634, sub-condition 40, variant 01 |
| `Driving 7111001` | 320 | event | raw | Driving condition 711, variant 1 (autonomous mode) |
| `Driving 7112001` | 320 | event | raw | Driving condition 711, variant 2 (autonomous mode) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Mental Workload Classification (Easy vs Hard Road Complexity)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.875
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------||---|
  | `Driving 231 V1` | 0 | Easy road complexity (main road, normal traffic) |
  | `Driving 231 V2` | 0 | Easy road complexity (main road, normal traffic) |
  | `Driving 411 V1` | 0 | Easy road complexity (highway segment) |
  | `Driving 132 V1` | 1 | Hard road complexity (high-traffic urban) |
  | `Driving 132 V2` | 1 | Hard road complexity (high-traffic urban) |
  | `Driving 141 V1` | 1 | Hard road complexity (complex intersection) |
  | `Driving 141 V2` | 1 | Hard road complexity (complex intersection) |
  | `Driving 232 V1` | 1 | Hard road complexity (secondary road) |
  | `Driving 232 V2` | 1 | Hard road complexity (secondary road) |
  | `Driving 142 V1` | 1 | Hard road complexity (secondary road variant) |
  | `Driving 142 V2` | 1 | Hard road complexity (secondary road variant) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2018.00509 [partial] — EEG-based mental workload classification using asSWLDA classifier; discriminates Easy (main road, normal hour) vs Hard (secondary road, rush hour) road conditions in real driving.
- **Kernel Notes**: 
  - Event ID mapping: 7-digit codes in source analysis map to "Driving XXX V#" format in events.tsv (e.g., 2310001 → "Driving 231 V1", 4111101 → "Driving 411 V1")
  - Labels (Easy/Hard) derived by grouping leading digits per dataset README: 1xx → Easy (main roads, low complexity), 2xx-4xx → Hard (secondary roads, high-traffic urban, complex scenarios)
  - High overlap (0.875) captures dynamic workload fluctuations during sustained driving states
  - Compute 8s moving average for WL score as referenced in paper
  - Dominant classes (231/411 with ~10k each) vs minority classes (~1k-1.8k) — stratification recommended

### Potential Task 1: Driving Condition Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------||---|
  | `Driving 231 V1` | 0 | Driving condition 231, variant 1 (dominant, ~10k) |
  | `Driving 231 V2` | 1 | Driving condition 231, variant 2 (dominant, ~10k) |
  | `Driving 411 V1` | 2 | Driving condition 411, variant 1 (dominant, ~10k) |
  | `Driving 232 V1` | 3 | Driving condition 232, variant 1 (minority, ~1.8k) |
  | `Driving 232 V2` | 4 | Driving condition 232, variant 2 (minority, ~1.8k) |
  | `Driving 141 V1` | 5 | Driving condition 141, variant 1 (minority, ~1.4k) |
  | `Driving 141 V2` | 6 | Driving condition 141, variant 2 (minority, ~1.4k) |
- **Evidence**: None (no DOI reference)
- **Kernel Notes**:
  - 7-digit codes in analysis.md correspond to "Driving XXX V#" format in events.tsv
  - Severe class imbalance: dominant classes (231 V1/V2, 411 V1) ~10k each vs minority classes ~1k-1.8k each
  - Consider grouping by leading 3 digits (e.g., 231, 411, 232, 141) to reduce cardinality before classification
  - Binary V1/V2 variants within each condition — may collapse for higher-level condition grouping
  - No explicit condition duration markers in events.tsv — infer from adjacent code transitions

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
