# Exo-EEG Experiment

**Dataset**: `openneuro_ds007180` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007180
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 63 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

EEG was recorded during interaction with an exoskeleton in a gait or robotic-assisted movement task. Participants performed motor tasks with varying exoskeleton assistance levels and movement conditions across 12 movement types. BrainVision trigger codes (S-prefixed) encode specific movement types, assistance conditions (two levels), and stimulus phases across 47 distinct event categories. The dataset includes both executed and imagined movement trials across upper and lower limb conditions.

## File Scan Result

> **Kernel SHA256**: `285edc6ad3d6ac3ecf0ff53ece92dfbba1db2e6d56f9b640bb7d11eaadbc07fb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 11` | 1884 | event | raw | Movement type 1 — assistance condition A |
| `Stimulus/S 12` | 1884 | event | raw | Movement type 1 — assistance condition B |
| `Stimulus/S 13` | 1750 | event | raw | Movement type 1 — condition-3 epoch |
| `Stimulus/S 16` | 134 | event | raw | Anomalous/transition marker — type 1 |
| `Stimulus/S 21` | 1885 | event | raw | Movement type 2 — assistance condition A |
| `Stimulus/S 22` | 1885 | event | raw | Movement type 2 — assistance condition B |
| `Stimulus/S 23` | 1750 | event | raw | Movement type 2 — condition-3 epoch |
| `Stimulus/S 26` | 135 | event | raw | Anomalous/transition marker — type 2 |
| `Stimulus/S 31` | 1876 | event | raw | Movement type 3 — assistance condition A |
| `Stimulus/S 32` | 1876 | event | raw | Movement type 3 — assistance condition B |
| `Stimulus/S 33` | 1750 | event | raw | Movement type 3 — condition-3 epoch |
| `Stimulus/S 36` | 126 | event | raw | Anomalous/transition marker — type 3 |
| `Stimulus/S 41` | 1872 | event | raw | Movement type 4 — assistance condition A |
| `Stimulus/S 42` | 1872 | event | raw | Movement type 4 — assistance condition B |
| `Stimulus/S 43` | 1750 | event | raw | Movement type 4 — condition-3 epoch |
| `Stimulus/S 46` | 122 | event | raw | Anomalous/transition marker — type 4 |
| `Stimulus/S 51` | 1862 | event | raw | Movement type 5 — assistance condition A |
| `Stimulus/S 52` | 1862 | event | raw | Movement type 5 — assistance condition B |
| `Stimulus/S 53` | 1750 | event | raw | Movement type 5 — condition-3 epoch |
| `Stimulus/S 56` | 112 | event | raw | Anomalous/transition marker — type 5 |
| `Stimulus/S 61` | 1861 | event | raw | Movement type 6 — assistance condition A |
| `Stimulus/S 62` | 1861 | event | raw | Movement type 6 — assistance condition B |
| `Stimulus/S 63` | 1750 | event | raw | Movement type 6 — condition-3 epoch |
| `Stimulus/S 66` | 111 | event | raw | Anomalous/transition marker — type 6 |
| `Stimulus/S 71` | 1863 | event | raw | Movement type 7 — assistance condition A |
| `Stimulus/S 72` | 1863 | event | raw | Movement type 7 — assistance condition B |
| `Stimulus/S 73` | 1750 | event | raw | Movement type 7 — condition-3 epoch |
| `Stimulus/S 76` | 113 | event | raw | Anomalous/transition marker — type 7 |
| `Stimulus/S 81` | 1847 | event | raw | Movement type 8 — assistance condition A |
| `Stimulus/S 82` | 1847 | event | raw | Movement type 8 — assistance condition B |
| `Stimulus/S 83` | 1750 | event | raw | Movement type 8 — condition-3 epoch |
| `Stimulus/S 86` | 97 | event | raw | Anomalous/transition marker — type 8 |
| `Stimulus/S 91` | 1289 | event | raw | Movement type 9 — assistance condition A |
| `Stimulus/S 92` | 1289 | event | raw | Movement type 9 — assistance condition B |
| `Stimulus/S 93` | 1250 | event | raw | Movement type 9 — condition-3 epoch |
| `Stimulus/S 96` | 39 | event | raw | Anomalous/transition marker — type 9 |
| `Stimulus/S101` | 1294 | event | raw | Movement type 10 — assistance condition A |
| `Stimulus/S102` | 1294 | event | raw | Movement type 10 — assistance condition B |
| `Stimulus/S103` | 1250 | event | raw | Movement type 10 — condition-3 epoch |
| `Stimulus/S106` | 44 | event | raw | Anomalous/transition marker — type 10 |
| `Stimulus/S111` | 1286 | event | raw | Movement type 11 — assistance condition A |
| `Stimulus/S112` | 1286 | event | raw | Movement type 11 — assistance condition B |
| `Stimulus/S113` | 1250 | event | raw | Movement type 11 — condition-3 epoch |
| `Stimulus/S116` | 36 | event | raw | Anomalous/transition marker — type 11 |
| `Stimulus/S121` | 1281 | event | raw | Movement type 12 — assistance condition A |
| `Stimulus/S122` | 1281 | event | raw | Movement type 12 — assistance condition B |
| `Stimulus/S123` | 1250 | event | raw | Movement type 12 — condition-3 epoch |
| `Stimulus/S126` | 31 | event | raw | Anomalous/transition marker — type 12 |
| `Stimulus/S255` | 75 | event | raw | Global error/reset marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Upper Limb Movement Type Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 0.4 s, target_events = [`S13`, `S23`, `S33`, `S43`, `S53`, `S63`, `S73`, `S83`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|-------|
| `S13` | 0 | Movement type 1 — condition-3 epoch |
| `S23` | 1 | Movement type 2 — condition-3 epoch |
| `S33` | 2 | Movement type 3 — condition-3 epoch |
| `S43` | 3 | Movement type 4 — condition-3 epoch |
| `S53` | 4 | Movement type 5 — condition-3 epoch |
| `S63` | 5 | Movement type 6 — condition-3 epoch |
| `S73` | 6 | Movement type 7 — condition-3 epoch |
| `S83` | 7 | Movement type 8 — condition-3 epoch |

- **Evidence**:
  - DOI: 10.1371/journal.pone.0182578 — Cited in epoch alignment context as classifying upper limb movements (elbow flexion/extension, forearm supination/pronation, hand open/close, rest, and imagination) from low-frequency EEG during exoskeleton-assisted movement; indirect classification support (not present in formal reference extraction list).
- **Kernel Notes**: All eight SXX3 events carry exactly 1750 occurrences each, indicating a perfectly balanced condition marker — strongly preferred as the primary classification target. Apply 0.3–3 Hz bandpass filter consistent with low-frequency MI literature. The symmetric [-0.4, 0.4] s window captures both movement preparation and early execution phases relative to stimulus onset. Verify movement-type semantic mapping (e.g., elbow vs hand vs forearm) against the dataset events.tsv before assigning human-readable class names. Subject-wise z-scoring recommended to mitigate cross-subject variability introduced by individual exoskeleton fitting configurations.

---

### Potential Task 1: Full 12-Class Movement Set Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 0.4 s, target_events = [`S13`, `S23`, `S33`, `S43`, `S53`, `S63`, `S73`, `S83`, `S93`, `S103`, `S113`, `S123`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|-------|
| `S13` | 0 | Movement type 1 — condition-3 epoch |
| `S23` | 1 | Movement type 2 — condition-3 epoch |
| `S33` | 2 | Movement type 3 — condition-3 epoch |
| `S43` | 3 | Movement type 4 — condition-3 epoch |
| `S53` | 4 | Movement type 5 — condition-3 epoch |
| `S63` | 5 | Movement type 6 — condition-3 epoch |
| `S73` | 6 | Movement type 7 — condition-3 epoch |
| `S83` | 7 | Movement type 8 — condition-3 epoch |
| `S93` | 8 | Movement type 9 — condition-3 epoch |
| `S103` | 9 | Movement type 10 — condition-3 epoch |
| `S113` | 10 | Movement type 11 — condition-3 epoch |
| `S123` | 11 | Movement type 12 — condition-3 epoch |

- **Evidence**: Structural inference from event code pattern — all SXX3 events share a consistent count (1250–1750 per type) and the suffix-3 digit is uniform across all 12 movement-type groups, plausibly extending the 8-class paradigm to a full 12-class set. No direct reference available.
- **Kernel Notes**: S93–S123 yield ~1250 trials versus ~1750 for S13–S83, suggesting S9X–S12X may encode a distinct sub-paradigm block (e.g., different task phase, bilateral vs unilateral, or imagined vs executed extension). Kernel must verify sub-paradigm identity before merging all 12 classes. Apply class-balancing (downsample to 1250 trials per class) if merged. The S96/S106/S116/S126 low-count events (31–44 occurrences) are excluded from target_events and likely encode error or transition markers.

---

### Potential Task 2: Exoskeleton Assistance Condition Binary Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S11`, `S12`, `S21`, `S22`, `S31`, `S32`, `S41`, `S42`, `S51`, `S52`, `S61`, `S62`, `S71`, `S72`, `S81`, `S82`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|-------|
| `S11` | 0 | Movement type 1 — assistance condition A |
| `S12` | 1 | Movement type 1 — assistance condition B |
| `S21` | 0 | Movement type 2 — assistance condition A |
| `S22` | 1 | Movement type 2 — assistance condition B |
| `S31` | 0 | Movement type 3 — assistance condition A |
| `S32` | 1 | Movement type 3 — assistance condition B |
| `S41` | 0 | Movement type 4 — assistance condition A |
| `S42` | 1 | Movement type 4 — assistance condition B |
| `S51` | 0 | Movement type 5 — assistance condition A |
| `S52` | 1 | Movement type 5 — assistance condition B |
| `S61` | 0 | Movement type 6 — assistance condition A |
| `S62` | 1 | Movement type 6 — assistance condition B |
| `S71` | 0 | Movement type 7 — assistance condition A |
| `S72` | 1 | Movement type 7 — assistance condition B |
| `S81` | 0 | Movement type 8 — assistance condition A |
| `S82` | 1 | Movement type 8 — assistance condition B |

- **Evidence**: Structural inference from symmetric SXX1/SXX2 pairing across all 8 primary movement types with near-equal per-event counts (~1847–1885), consistent with a two-level within-movement manipulation (e.g., powered vs unpowered exoskeleton, or high vs low assistance torque). No direct reference available.
- **Kernel Notes**: Label assignment pools across movement types: suffix digit 1 → y=0 (condition A), suffix digit 2 → y=1 (condition B). Movement type identity must be stored as a metadata covariate, and movement-type-stratified cross-validation is strongly recommended to prevent movement class leaking into assistance-condition decoding. The asymmetric [-0.2, 1.0] s window accommodates sustained exoskeleton torque response following stimulus onset. SXX6 low-count events (97–135 occurrences) are excluded; they likely encode anomalous or transition trials and should be marked as artifacts during preprocessing.
