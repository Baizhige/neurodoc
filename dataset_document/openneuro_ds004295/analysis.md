# Reward Gain and Punishment Avoidance Reversal Learning

**Dataset**: `openneuro_ds004295` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004295
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26 | **Manual Review**: Pending
**Channels**: 66 | **Sampling Rate**: 1024 Hz

## Paradigm

A reversal learning task comparing brain activity during reward gain (monetary) versus punishment avoidance (white noise) reinforcement. Participants learned stimulus-response associations that reversed mid-task, requiring cognitive flexibility. EEG was recorded to investigate feedback-related neural signatures under different reinforcement conditions.

## File Scan Result

> **Kernel SHA256**: `43d5116bfe11eb48d8d017563fbe04fc0fae31511c95d0b05154f3987f3dc20c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 53` | 442 | event | raw | Stimulus trigger (low frequency) — condition-specific, decode from events.tsv |
| `S 54` | 2029 | event | raw | Stimulus trigger (high frequency) — condition-specific, decode from events.tsv |
| `S 56` | 1724 | event | raw | Stimulus trigger (high frequency) — condition-specific, decode from events.tsv |
| `S 73` | 629 | event | raw | Stimulus trigger (moderate frequency) — condition variant, decode from events.tsv |
| `S 74` | 2438 | event | raw | Stimulus trigger (highest frequency) — primary stimulus type, decode from events.tsv |
| `S 76` | 1441 | event | raw | Stimulus trigger (moderate frequency) — condition variant, decode from events.tsv |
| `S101` | 26 | event | raw | Sample stimulus trigger (one per subject) |
| `S150` | 106 | event | raw | Block/phase trigger (~22 subjects) — secondary task component, decode from events.tsv |
| `S151` | 105 | event | raw | Block/phase trigger (~22 subjects) — secondary task component, decode from events.tsv |
| `S201` | 26 | event | raw | Probe stimulus trigger (one per subject) |
| `feedback_negative` | 3730 | event | raw | Decoded negative feedback (reward loss / punishment failure) |
| `feedback_positive` | 3560 | event | raw | Decoded positive feedback (reward gain / punishment avoidance success) |
| `probe_stimulus` | 26 | event | raw | Decoded probe stimulus (second in pair) |
| `sample_stimulus` | 26 | event | raw | Decoded sample stimulus (first in pair) |
| `stimulus` | 27954 | event | raw | Generic stimulus trigger — decode to extract reinforcement condition (reward/punishment) and reversal phase (pre/post) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Feedback Valence Classification (Reward Gain vs Punishment Avoidance)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.0 s, target_events = [`feedback_positive`, `feedback_negative`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `feedback_positive` | 0 | Positive feedback (reward gain / punishment avoidance success) |
  | `feedback_negative` | 1 | Negative feedback (reward loss / punishment failure) |
- **Super Meta Notes**: N/A
- **Evidence**:
  - DOI: 10.1111/psyp.14235 — Single-trial regression examining frontal midline theta (FMθ) responses to positive vs negative feedback in reward and punishment reversal learning tasks. 26 participants, EEG recorded during feedback processing, feedback valence as primary 2-class predictor.
- **Kernel Notes**: Verify mapping between raw BrainVision codes (S 52 → feedback_positive, S 51 → feedback_negative) and decoded semantic labels by cross-referencing events.tsv. Raw S 52/S 51 counts (141/139 per subject) roughly align with decoded feedback_positive/feedback_negative counts (3560/3730 total across 26 subjects), confirming preprocessing completed partial decoding. Kernel should validate this mapping and preserve event-to-label correspondence for downstream analysis.

---

### Potential Task 1: Reversal Learning Stimulus Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stimulus` (prereversal, reward) | 0 | Stimulus presented before reversal cue in reward condition — Needs verification: derived from raw codes S 53/S 54/S 56 |
  | `stimulus` (prereversal, punishment) | 1 | Stimulus presented before reversal cue in punishment condition — Needs verification: derived from raw codes S 73/S 74/S 76 |
  | `stimulus` (postreversal, reward) | 2 | Stimulus presented after reversal cue in reward condition — Needs verification |
  | `stimulus` (postreversal, punishment) | 3 | Stimulus presented after reversal cue in punishment condition — Needs verification |
- **Super Meta Notes**: N/A
- **Evidence**: N/A
- **Kernel Notes**: The `stimulus` event (27954 total) encodes multiple condition variants via raw BrainVision codes (S 53, S 54, S 56, S 73, S 74, S 76) requiring kernel-level semantic decoding to extract reinforcement condition (reward/punishment) and reversal phase (pre/post). Count patterns suggest condition-specific triggers: S 54 (2029) and S 56 (1724) may be frequent stimulus types, while S 73 (629) and S 76 (1441) are moderate frequency variants. The kernel must decode raw trigger codes to assign multi-class labels based on stimulus identity, reinforcement condition, and temporal relationship to reversal cue. Cross-validate with S150/S151 (appear in ~22 subjects, possibly separate task block) if available.

---

### Potential Task 1: Sample-Probe Paradigm Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`sample_stimulus`, `probe_stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `sample_stimulus` | 0 | Sample stimulus (first in pair, S100) |
  | `probe_stimulus` | 1 | Probe stimulus (second in pair, S200) |
- **Super Meta Notes**: N/A
- **Evidence**: N/A
- **Kernel Notes**: Events `sample_stimulus` (26 total) and `probe_stimulus` (26 total) appear once per subject, corresponding to raw S100 and S200 triggers. These encode a pair-learning component of the paradigm requiring epoch-level comparison between sample and probe phases. The kernel should verify mapping to raw codes and preserve temporal relationship between sample-probe pairs for subsequent analysis.

---

### Potential Task 2: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, segmentation_events = derived from stimulus or response events
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | `response_time` | Continuous trial-by-trial response latency in ms; channel not present in MISC Label Summary — Needs verification: verify existence in derived channels or reconstruct from events.tsv timing |
- **Super Meta Notes**: N/A
- **Evidence**: N/A
- **Kernel Notes**: `response_time` stored in misc channel (route: misc) serves as continuous regression target for trial-by-trial analysis. Kernel must preserve derivation metadata including source, unit (ms), and version. Segmentation should align epochs around response events extracted from stimulus events or derived from raw events.tsv timing analysis. Narrow window (±0.5s) focuses on motor response and immediate post-response processing.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
