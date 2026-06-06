# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21 | **Channels**: 18 | **Sampling Rate**: 500 | **Manual Review**:
## Paradigm

Seven participants with orthopedic impairment performed four right-upper-limb motor imagery tasks (reaching, grasping, lifting, and twisting) while 18-channel EEG and fNIRS were recorded simultaneously. Each participant completed three sessions; each session contained 40 trials with the four MI tasks presented in random order. Each trial consisted of 3 s fixation, a 4 s visual cue indicating the movement task, a 3 s ready/gray-screen period to reduce afterimage effects, and a 5 s instructed motor imagery period. Event markers `S 7`-`S 10` label the four MI task types, but their exact mapping to reaching/grasping/lifting/twisting is not recoverable from the available metadata.

## File Scan Result

> **Kernel SHA256**: `4f77771818c2331570de94279750023b5e5994decf339084f5b5b350a702d446`
> **EEGUnity Version**: `0.8.2`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `S 1` | 21 | event | raw |  |
| `S 10` | 840 | event | raw |  |
| `S 2` | 840 | event | raw |  |
| `S 3` | 210 | event | raw |  |
| `S 4` | 210 | event | raw |  |
| `S 5` | 210 | event | raw |  |
| `S 6` | 210 | event | raw |  |
| `S 7` | 840 | event | raw |  |
| `S 8` | 840 | event | raw |  |
| `S 9` | 840 | event | raw |  |
| `boundary` | 21 | event | raw |  |
| `condition 12` | 21 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `Hand Dominance` | complete | e.g. R, L |
| `Years Since Diagnosis` | complete | e.g. 21, 32, 73 |
| `age` | complete | e.g. 75, 48, 78 |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | complete | e.g. right, left |
| `sex` | missing |  |

## Tasks

### Classical Task 1: Four-Class Right-Upper-Limb Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 7.0 s, tmax = 14.5 s, target_events = [`S 3`, `S 4`, `S 5`, `S 6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `S 3` | 0 | Motor imagery condition 1: one of reaching, grasping, lifting, twisting |
  | `S 4` | 1 | Motor imagery condition 2: one of reaching, grasping, lifting, twisting |
  | `S 5` | 2 | Motor imagery condition 3: one of reaching, grasping, lifting, twisting |
  | `S 6` | 3 | Motor imagery condition 4: one of reaching, grasping, lifting, twisting |
- **Evidence**:
  - 10.18112/openneuro.ds004022.v1.0.0 — Official README
  - 10.3389/fnhum.2025.1583342 — Table 3: confirms 18 channels, 7 participants, 3 sessions/participant, 40 trials/session, 4 MI tasks, and trial structure `3s fixation, 4s cue, 3s ready, 5s MI`.
- **Notes**: `S 3-S 6` are confirmed as the four mutually exclusive MI condition markers by raw event counts and event order. The exact semantic mapping to reaching/grasping/lifting/twisting is not documented, so do not assign `S 3 = Reach` etc. `S 7-S 10` should not be used as class labels because all four occur once in every trial. The epoch window is cue-marker relative and chosen to cover the later MI period; if the kernel supports context labels, a cleaner implementation is to epoch `S 8` to `S 10` and label each epoch by the preceding `S 3-S 6` marker.

## Data Quality Notes

- No run-level `events.tsv` files are present; event annotations are embedded in EEGLAB `.set` headers, so event semantics must be inferred from raw event order and counts.
- The exact mapping from `S 3`, `S 4`, `S 5`, and `S 6` to reaching, grasping, lifting, and twisting is not documented in the README, BIDS sidecars, or reference papers.
- `S 7-S 10` occur once in every trial and are trial phase markers, not four-class MI labels; they should not be used directly as target classes.
- The likely MI execution window is later than the `S 3-S 6` condition marker; epoch timing should account for the trial sequence `S 2 -> S 3/S 4/S 5/S 6 -> S 7 -> S 8 -> S 9 -> S 10`.
- The dataset is small: 7 participants and 21 EEG runs, so subject leakage and weak cross-subject generalization are major evaluation risks.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
