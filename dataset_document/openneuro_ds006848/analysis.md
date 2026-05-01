# AlphaDirection1: EEG, ECG, PPG in the resting state and working memory for sequentially and simultaneously presented digits

**Dataset**: `openneuro_ds006848` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006848/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 52 | **Manual Review**: Pending
**Channels**: 65 | **Sampling Rate**: 1000 Hz

## Paradigm

This dataset investigates the directional characteristics of brain alpha waves during resting state and working memory tasks. Participants performed a verbal working memory digit span task with four encoding modes: simultaneous presentation (entire digit set displayed at once), fast sequential (400 ms per digit), slow sequential (1000 ms per digit), and fast sequential with additional delay. Each encoding mode was followed by a retention period and verbal recall. Resting state recordings with alternating eyes-open and eyes-closed periods, along with cartoon clips as separators, were included before the experiment. Data were acquired simultaneously using EEG, ECG, and PPG.

## File Scan Result

> **Kernel SHA256**: `48e0c09d8efe7799c84862c95346506dcc817f9524266beb676ba7a20aac2ab4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S    1` | 3134 | event | raw | Digit "1" sequential encoding onset |
| `Stimulus/S    2` | 3077 | event | raw | Digit "2" sequential encoding onset |
| `Stimulus/S    3` | 3124 | event | raw | Digit "3" sequential encoding onset |
| `Stimulus/S    4` | 3164 | event | raw | Digit "4" sequential encoding onset |
| `Stimulus/S    5` | 3104 | event | raw | Digit "5" sequential encoding onset |
| `Stimulus/S    6` | 3103 | event | raw | Digit "6" sequential encoding onset |
| `Stimulus/S    7` | 3131 | event | raw | Digit "7" sequential encoding onset |
| `Stimulus/S    8` | 3117 | event | raw | Digit "8" sequential encoding onset |
| `Stimulus/S    9` | 3131 | event | raw | Digit "9" sequential encoding onset |
| `Stimulus/S   10` | 3163 | event | raw | Digit "0" sequential encoding onset |
| `Stimulus/S   11` | 1495 | event | raw | Simultaneous encoding: entire digit set presented at once onset |
| `Stimulus/S   20` | 87 | event | raw | Eyes-closed resting state segment onset |
| `Stimulus/S   21` | 88 | event | raw | Eyes-open resting state segment onset |
| `Stimulus/S   22` | 22 | event | raw | Cartoon clip start (intersegment interference) |
| `Stimulus/S   23` | 22 | event | raw | Cartoon clip end |
| `Stimulus/S   28` | 1495 | event | raw | Retention period onset after simultaneous encoding |
| `Stimulus/S   40` | 1499 | event | raw | Retention period onset after fast sequential encoding (400 ms/digit) |
| `Stimulus/S   60` | 1499 | event | raw | Retention period onset after fast sequential encoding with additional delay |
| `Stimulus/S  100` | 1466 | event | raw | Retention period onset after slow sequential encoding (1000 ms/digit) |
| `Stimulus/S  102` | 5956 | event | raw | 2-second baseline segment onset before each trial |
| `Stimulus/S  110` | 5960 | event | raw | Retrieval phase onset: subject begins verbal recall |
| `Stimulus/S  120` | 209 | event | raw | Resting state macro-period onset |
| `Stimulus/S  200` | 29 | event | raw | Experiment end mark |
| `Stimulus/S99999` | 157 | admin | raw | BIDS file boundary mark |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `PPG`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Working Memory Retention EEG Regression (Digits Recalled)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 6.0 s, target_events = [`Stimulus/S   28`, `Stimulus/S   40`, `Stimulus/S   60`, `Stimulus/S  100`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S   40` | 0–7 | Retention_Fast: EEG retention period after fast sequential encoding (400 ms/digit); y = number of digits correctly recalled |
  | `Stimulus/S   60` | 0–7 | Retention_FastDelay: EEG retention period after fast sequential encoding with additional delay gap; y = number of digits correctly recalled |
  | `Stimulus/S  100` | 0–7 | Retention_Slow: EEG retention period after slow sequential encoding (1000 ms/digit); y = number of digits correctly recalled |
  | `Stimulus/S   28` | 0–7 | Retention_Simultaneous: EEG retention period after simultaneous full-set encoding; y = number of digits correctly recalled |
- **Evidence**:
  - DOI: 10.1101/2025.05.04.652111 — "Temporal structure of item presentation modulates brain oscillations in verbal working memory." Directly analyzes EEG from ds006848 using single-trial regression models linking encoding theta/alpha suppression and 6 s retention-period spectral power (theta 4–7 Hz, alpha 8–13 Hz, beta 18–24 Hz) to number of digits recalled across all four presentation modes (Fast, Slow, FastDelay, Simultaneous). Classification = relevant.
- **Kernel Notes**:
  - Epochs anchored at retention-phase onset (S28, S40, S60, S100); paper sub-divides retention into Retention1 (0.6–3 s post-onset) and Retention2 (3–6 s post-onset), excluding the first 0.6 s transient.
  - Extract spectral power features (theta, alpha, beta bands) during the 6 s retention window; per-channel and topographic features recommended.
  - Regression target y (integer 0–7) must be sourced from behavioral response/log files (misc label route); the value is NOT encoded directly in the EEG event stream.
  - Trial-type mapping: Simultaneous encoding → S11 (encoding onset) → S28 (retention onset); Fast sequential → S1–S10 digits at ~400 ms SOA → S40; Slow sequential → S1–S10 digits at ~1000 ms SOA → S100; FastDelay sequential → S60.
  - S102 (Baseline_2s, 2 s pre-trial baseline) precedes each trial; use for baseline correction.
  - Exclude admin events: Boundary (S99999), Start_Cartoon (S22), End_Cartoon (S23), Experiment_End (S200).

---

### Normal Task 1: Encoding Mode Classification (Simultaneous vs. Sequential)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 6.0 s, target_events = [`Stimulus/S   28`, `Stimulus/S   40`, `Stimulus/S   60`, `Stimulus/S  100`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S   28` | 0 | Retention period after simultaneous (full-set) encoding; 1495 trials |
  | `Stimulus/S   40` | 1 | Retention period after fast sequential encoding; 1499 trials |
  | `Stimulus/S   60` | 1 | Retention period after fast sequential encoding with extra delay; 1499 trials |
  | `Stimulus/S  100` | 1 | Retention period after slow sequential encoding; 1466 trials |
- **Evidence**:
  - DOI: 10.1101/2025.05.04.652111 — The paper's primary contrast is simultaneous vs. sequential temporal presentation structure, reporting significant differences in alpha and theta band dynamics during both encoding and retention phases across modes, providing indirect support for EEG-based encoding-mode classification from retention-period activity.
- **Kernel Notes**:
  - Binary label: simultaneous (y=0, N≈1495) vs. sequential (y=1, N≈4464 combined); sequential encompasses all three sequential retention types.
  - For finer multiclass analysis use 4-class variant: Simultaneous=0, Fast=1, FastDelay=2, Slow=3.
  - Sequential class is ~3× more frequent than simultaneous; apply stratified sampling or class-weighted loss during training.
  - Same epoch anchoring and preprocessing as Classical Task 1; baseline correction via S102.
  - Retention-period alpha suppression and theta power are expected discriminating features per the reference paper.

---

### Potential Task 1: Resting State Eyes Open vs. Eyes Closed Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, segment_length = 4.0 s, overlap = 0.0 s, target_events = [`Stimulus/S   20`, `Stimulus/S   21`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S   20` | 0 | Eyes-closed resting state block onset; 87 occurrences across 30 subjects |
  | `Stimulus/S   21` | 1 | Eyes-open resting state block onset; 88 occurrences across 30 subjects |
- **Evidence**:
  - Paradigm: Dataset explicitly records alternating eyes-open/eyes-closed resting state blocks (S20/S21 markers within S120 Rest periods). The paper's core focus on alpha directionality and the canonical Berger effect (alpha suppression during eyes-open) make this a well-motivated EEG classification benchmark even without direct task-specific references.
- **Kernel Notes**:
  - Long-epoch method: anchor on S20/S21 onset, extract up to 30 s per block, then segment into non-overlapping 4 s sub-epochs; each sub-epoch inherits the parent block label.
  - Alpha band power (8–13 Hz) over posterior/occipital channels is the primary discriminating feature; this directly relates to the paper's alpha directionality analyses.
  - S120 (Rest) marks the broader resting macro-period; S20/S21 provide fine-grained eyes-state labels within it.
  - Verify segment duration before cropping: trim each epoch to the earlier of 30 s or the next S20/S21 event to avoid state leakage.
  - ECG (S20/S21 also annotate blocks during which PPG/ECG were recorded) — consider multimodal features if desired.

---

### Potential Task 2: Sequential Encoding Digit Identity Classification (10-Class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`Stimulus/S    1`, `Stimulus/S    2`, `Stimulus/S    3`, `Stimulus/S    4`, `Stimulus/S    5`, `Stimulus/S    6`, `Stimulus/S    7`, `Stimulus/S    8`, `Stimulus/S    9`, `Stimulus/S   10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S   10` | 0 | Digit "0" sequential encoding onset (3163 trials) |
  | `Stimulus/S    1` | 1 | Digit "1" sequential encoding onset (3134 trials) |
  | `Stimulus/S    2` | 2 | Digit "2" sequential encoding onset (3077 trials) |
  | `Stimulus/S    3` | 3 | Digit "3" sequential encoding onset (3124 trials) |
  | `Stimulus/S    4` | 4 | Digit "4" sequential encoding onset (3164 trials) |
  | `Stimulus/S    5` | 5 | Digit "5" sequential encoding onset (3104 trials) |
  | `Stimulus/S    6` | 6 | Digit "6" sequential encoding onset (3103 trials) |
  | `Stimulus/S    7` | 7 | Digit "7" sequential encoding onset (3131 trials) |
  | `Stimulus/S    8` | 8 | Digit "8" sequential encoding onset (3117 trials) |
  | `Stimulus/S    9` | 9 | Digit "9" sequential encoding onset (3131 trials) |
- **Evidence**:
  - Paradigm: Each digit in the sequential encoding stream is individually time-stamped (S1–S10), yielding ~3100 trials per digit class across 30 subjects (~31 000 total). Decoding digit identity from EEG at visual stimulus onset is a plausible BCI/cognitive neuroscience benchmark supported by the paradigm structure alone.
- **Kernel Notes**:
  - 10-class digit identity classification from ERP and time-frequency features locked to each digit presentation onset.
  - Event-ID mapping: S1=digit "1" … S9=digit "9", S10=digit "0" (confirmed by count alignment with Encoding_DigitValue_* entries).
  - Short epoch (−0.1 to 0.8 s) captures early visual and cognitive encoding ERPs; extend tmax to 1.0 s to include later WM-related components.
  - Near-uniform class balance (~3100 trials/class); minimal resampling required.
  - High trial count (~31 000 total) makes this suitable for deep learning (EEGNet, ShallowConvNet) approaches.
  - Encoding presentation rate (Fast 400 ms SOA vs. Slow 1000 ms SOA) is not distinguished at the digit-onset level; consider stratifying or separating models by encoding mode for controlled comparisons.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
