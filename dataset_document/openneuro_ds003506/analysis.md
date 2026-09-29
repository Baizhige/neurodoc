# EEG: Reinforcement Learning in Parkinson's

**Dataset**: `openneuro_ds003506` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003506
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 84 | **Manual Review**: Pending
**Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

This study investigates the Reward Positivity (RewP) EEG component in Parkinson's disease (PD) patients compared to matched healthy controls. Participants completed a reinforcement learning task with both volitional (self-initiated) and instructed (cue-driven) choices, earning rewards or receiving no-reward feedback based on their selections. The RewP, a frontocentral ERP component, scales with reward prediction error and mirrors dopamine-driven learning. The study examines whether PD diminishes this signal, given dopaminergic dysfunction in PD.

## File Scan Result

> **Kernel SHA256**: `43fc486262aaf080d06247cb006cbeeb73e1d3557111020bed104176440d990e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 5631 | event | raw | Instructed choice condition marker |
| `S  2` | 5727 | event | raw | Volitional choice condition marker |
| `S  3` | 21837 | event | raw | Feedback stimulus (reward +1, no-reward 0) |
| `S  4` | 10918 | event | raw | Imperative stimulus requiring response |
| `S  5` | 10728 | event | raw | Instruction presentation (Match/Choose) |
| `S  6` | 164 | event | raw | Cue or probe stimulus |
| `S  7` | 53 | event | raw | Left-hand button press response |
| `S 10` | 3393 | event | raw | Right-hand button press response |
| `S 11` | 7749 | event | raw |  |
| `boundary` | 84 | admin | raw | HDF5 boundary marker for epoch concatenation |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Positional tracking channels storing continuous or derived coordinate data
- **Candidate Labels**: `X`, `Y`, `Z`
- **Kernel Note**: Verify channel roles and units. These non-EEG channels should be excluded before ERP analysis.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Reward vs. No-Reward Feedback Classification (RewP ERP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -6.0 s, tmax = 2.0 s, target_events = [`S  3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  3` (reward) | 1 | Reward feedback (positive outcome, +1) |
  | `S  3` (no-reward) | 0 | No-reward feedback (negative outcome, 0) |
- **Evidence**:
  - DOI: `10.1016/j.brainres.2019.146541` — Supports Reward Positivity (RewP) analysis comparing EEG responses to reward (+1) versus no-reward (0) feedback in Parkinson's disease patients and healthy controls during a reinforcement learning paradigm.
- **Kernel Notes**: Event code mapping required: `S  3` (21,837 events) corresponds to feedback stimulus events. Apply baseline correction using -0.2 s to 0 s pre-stimulus interval. Verify reward/no-reward split from accompanying events.tsv. Exclude boundary markers. Non-EEG channels (X, Y, Z positional, VEOG) should be excluded before analysis.

---

### Classical Task 2: Response Side Classification (Motor Execution)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S  7`, `S 10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  7` | 0 | Left-hand button press response |
  | `S 10` | 1 | Right-hand button press response |
- **Evidence**:
  - DOI: `10.1016/j.brainres.2019.146541` — The reinforcement learning task involves left/right button press responses to imperative stimuli, enabling motor lateralization analysis.
- **Kernel Notes**: Event code mapping required: `S  7` (53 events) and `S 10` (3,393 events) correspond to button choice responses. The large count discrepancy suggests different trial types or response conditions; verify mapping in events.tsv. Epoch window captures movement-related potentials and lateralized readiness.

---

### Potential Task 1: Volitional vs. Instructed Choice Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`S  1`, `S  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  1` | 0 | Instructed choice condition |
  | `S  2` | 1 | Volitional choice condition |
- **Evidence**:
  - DOI: `10.1016/j.brainres.2019.146541` — The paradigm explicitly includes both volitional (self-initiated) and instructed (cue-driven) choice trials.
- **Kernel Notes**: Event code mapping required: `S  1` (5,631 events) and `S  2` (5,727 events) likely represent instruction/event codes for the two choice conditions. Verify volitional/instructed mapping from events.tsv. The analysis.md references 'Instr' markers (168 total) but these may map differently in the actual event structure.

---

### Potential Task 1: Instruction Type Classification (Match vs. Choose)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 1.5 s, target_events = [`S  5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Classify epochs based on instruction type indicating whether participants should make a free choice ('Choose') or match a target ('Match').
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  5` | Needs verification | Instruction type (Match vs. Choose) — verify from events.tsv whether trial-level encoding distinguishes Match ('match target') vs. Choose ('free choice') conditions |

- **Notes**: Event code mapping required: `S  5` (10,728 events) may represent instruction presentation events. The analysis.md mentions 'Instr' markers (168 total) for Match/Choose instructions. Verify mapping from events.tsv before analysis. Exclude boundary markers (84 occurrences) from epoching.

---

### Potential Task 2: Imperative Stimulus-Response Alignment
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Epochs aligned to imperative stimulus onset to capture stimulus-locked ERPs and response preparation.
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  4` | Needs verification | Imperative stimulus onset — verify from events.tsv whether binary classification labels (e.g., stimulus type or required response) can be derived for this event |

- **Notes**: Event code mapping required: `S  4` (10,918 events) likely corresponds to imperative stimulus requiring response. The analysis.md references 'Imperative Stimulus' (84 events per file) but actual event counts suggest multiple stimulus types. Verify mapping in events.tsv.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
