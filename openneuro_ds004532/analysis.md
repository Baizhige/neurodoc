# EEG: Probabilistic Selection Task (PST) + PST with Cabergoline Challenge

**Dataset**: `openneuro_ds004532` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004532
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 80 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants performed the Probabilistic Selection Task (PST) across two sessions: a placebo session and a session with cabergoline (a dopamine D2/D3 agonist). The PST involves learning to select symbols with higher reward probability through feedback. Events encode training stimuli (Trn Stim), test stimuli (Tst Stim), feedback (FB), and outcomes (correct/incorrect). The study investigates dopaminergic modulation of reinforcement learning, with 40 subjects completing both sessions (80 total files).

## File Scan Result

> **Kernel SHA256**: `14f3c5fd1ced57e9a77ddf96c36a0cfedce46e05ae91e4a9a23528ed44f8ff6c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `FB` | 2122 | event | raw | Feedback onset |
| `S  7` | 110 | event | raw |  |
| `S 12` | 548 | event | raw |  |
| `S 13` | 548 | event | raw |  |
| `S 14` | 548 | event | raw |  |
| `S 15` | 548 | event | raw |  |
| `S 16` | 548 | event | raw |  |
| `S 21` | 548 | event | raw |  |
| `S 23` | 548 | event | raw |  |
| `S 24` | 547 | event | raw |  |
| `S 25` | 548 | event | raw |  |
| `S 26` | 547 | event | raw |  |
| `S 31` | 548 | event | raw |  |
| `S 32` | 548 | event | raw |  |
| `S 34` | 548 | event | raw |  |
| `S 35` | 548 | event | raw |  |
| `S 36` | 548 | event | raw |  |
| `S 41` | 548 | event | raw |  |
| `S 42` | 548 | event | raw |  |
| `S 43` | 548 | event | raw |  |
| `S 45` | 548 | event | raw |  |
| `S 46` | 548 | event | raw |  |
| `S 51` | 548 | event | raw |  |
| `S 52` | 548 | event | raw |  |
| `S 53` | 548 | event | raw |  |
| `S 54` | 547 | event | raw |  |
| `S 55` | 1 | event | raw |  |
| `S 56` | 548 | event | raw |  |
| `S 61` | 548 | event | raw |  |
| `S 62` | 548 | event | raw |  |
| `S 63` | 548 | event | raw |  |
| `S 64` | 548 | event | raw |  |
| `S 65` | 548 | event | raw |  |
| `S101` | 9897 | event | raw | Experimental marker (type 1) |
| `S102` | 9922 | event | raw | Experimental marker (type 2) |
| `S103` | 3972 | event | raw | Experimental marker (type 3) |
| `S104` | 4001 | event | raw | Experimental marker (type 4) |
| `S105` | 110 | event | raw | Experimental marker (type 5) |
| `S116` | 4646 | event | raw |  |
| `S121` | 1 | event | raw |  |
| `S124` | 1 | event | raw |  |
| `S125` | 4650 | event | raw |  |
| `S134` | 4646 | event | raw |  |
| `S143` | 4646 | event | raw |  |
| `S152` | 4646 | event | raw |  |
| `S161` | 4642 | event | raw |  |
| `S211` | 1 | event | raw |  |
| `S222` | 2 | event | raw |  |
| `S255` | 76 | event | raw |  |
| `Trn Stim` | 6060 | event | raw | Training stimulus onset |
| `Tst Stim` | 6029 | event | raw | Test stimulus onset |
| `admin: marker-8` | 15853 | admin | raw | Hardware status marker |
| `admin: marker-9` | 11940 | admin | raw | Hardware status marker |
| `boundary` | 137 | event | raw | Data file boundary marker |
| `correct` | 2098 | event | raw | Correct response outcome |
| `incorrect` | 131 | event | raw | Incorrect response outcome |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary Outcome Classification (correct vs incorrect)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 5.0 s, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `correct` | 0 | Correct response (reward) |
  | `incorrect` | 1 | Incorrect response (punishment) |
- **Super Meta Notes**: (NONE - meta_level is raw)
- **Evidence**:
  - DOI: 10.1038/ncomms6394
  - DOI: 10.1038/ncomms6394 (duplicate from multiple source files)
- **Kernel Notes**: Epoch around `FB` (feedback onset) to capture the neural response to outcome, including feedback-related negativity (FRN) and P300. Labels are derived from `correct` and `incorrect` events that immediately follow each FB event. Baseline correction: -300 to -200 ms prior to feedback onset per the referenced paper. **WARNING**: Severe class imbalance detected—correct (2098) vs incorrect (131) events in ~16:1 ratio. Consider class weighting, oversampling, or balanced subset selection during training. STATUS and admin markers should be excluded from analysis.

### Potential Task 1: Binary Outcome Classification (short window variant)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `correct` | 0 | Correct response (reward) |
  | `incorrect` | 1 | Incorrect response (punishment) |
- **Notes**: Shortened feedback-locked window focusing on early outcome processing phase (FRN/P300 components) while reducing potential contamination from adjacent events. Labels derived from `correct`/`incorrect` events following FB. This variation offers a more computationally efficient approach with potentially cleaner ERP components at the cost of missing later outcome processing phases.
