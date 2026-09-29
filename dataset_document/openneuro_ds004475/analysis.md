# Mobile EEG split-belt walking study

**Dataset**: `openneuro_ds004475` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004475
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 30 | **Manual Review**: Pending
**Channels**: 260 | **Sampling Rate**: 512 Hz

## Paradigm

A mobile brain-body imaging experiment investigating brain activity during gait adaptation using abrupt and gradual split-belt treadmill walking. Participants walked on a split-belt treadmill with different belt speeds while high-density EEG (260 channels) and gait events (heel strikes, toe-offs) were recorded to study locomotor adaptation and associated cortical dynamics. The paradigm includes baseline walking (B1–B3), split-belt adaptation blocks (SB1–SB2), and perturbation trials (P1–P2) with continuous recording across multiple walking conditions.

## File Scan Result

> **Kernel SHA256**: `73b427ccd5ad7cec62287b5f21e9faa6c1a2faf4eeb2401d2535385f509d5030`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `B1` | 30 | event | raw | Baseline block 1 start |
| `B2` | 30 | event | raw | Baseline block 2 start |
| `B3` | 30 | event | raw | Baseline block 3 start |
| `BUTTON` | 428 | event | raw | Button press event |
| `End 1` | 7 | admin | raw | Session segment end marker |
| `End 2` | 1 | admin | raw | Session segment end marker |
| `End B1` | 30 | admin | raw | End of baseline block 1 |
| `End B2` | 30 | admin | raw | End of baseline block 2 |
| `End B3` | 30 | admin | raw | End of baseline block 3 |
| `End P1` | 30 | admin | raw | End of perturbation block 1 |
| `End P2` | 30 | admin | raw | End of perturbation block 2 |
| `End SB1` | 30 | admin | raw | End of split-belt block 1 |
| `End SB2` | 30 | admin | raw | End of split-belt block 2 |
| `LHS` | 77083 | event | raw | Left heel strike (gait event) |
| `LTO` | 77071 | event | raw | Left toe-off (gait event) |
| `P1` | 30 | event | raw | Perturbation block 1 start |
| `P2` | 30 | event | raw | Perturbation block 2 start |
| `RHS` | 77599 | event | raw | Right heel strike (gait event) |
| `RTO` | 77080 | event | raw | Right toe-off (gait event) |
| `SB1` | 30 | event | raw | Split-belt block 1 start (tied speed) |
| `SB2` | 30 | event | raw | Split-belt block 2 start (differential speed) |
| `Start 2` | 1 | admin | raw | Session continuation marker |
| `TRIG` | 47995 | event | raw | External trigger marker |
| `continue B2` | 2 | admin | raw | Session continue marker |
| `continue P1` | 1 | admin | raw | Session continue marker |
| `continue SB1` | 1 | admin | raw | Session continue marker |
| `continue SB2` | 1 | admin | raw | Session continue marker |
| `pause B2` | 2 | admin | raw | Session pause marker |
| `pause P1` | 1 | admin | raw | Session pause marker |
| `pause SB1` | 1 | admin | raw | Session pause marker |
| `pause SB2` | 1 | admin | raw | Session pause marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Gait Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|----------|
  | `LHS` | 0 | Left heel strike |
  | `LTO` | 1 | Left toe-off |
  | `RHS` | 2 | Right heel strike |
  | `RTO` | 3 | Right toe-off |
- **Evidence**:
  - DOI: `10.1113/jp284505` — This paper analyzes high-density EEG recorded during split-belt treadmill walking from 30 participants (dataset openneuro_ds004475) to examine spectral power changes in alpha, beta, and theta bands across gait adaptation stages, using gait events (heel strikes and toe-offs) detected from force plates as epoching points.
- **Kernel Notes**: Gait events (LHS/RHS/RTO/LTO) are the fundamental unit of analysis in this locomotor paradigm. High event counts (~77k per type) reflect continuous walking across multiple conditions and are appropriate for event-related epoching. The epoch window (tmin=-0.2s to tmax=1.0s) captures the pre-event baseline and full post-event gait cycle dynamics. Channel filtering to EEG-only subset is required (260 total channels includes non-EEG motion capture markers).

---

### Potential Task 1: Walking Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = segment_length, target_events = [`SB1`, `SB2`], segment_length = 20–60 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|----------|
  | `SB1` | 0 | Split-belt block 1 (tied speed, baseline adaptation) |
  | `SB2` | 1 | Split-belt block 2 (differential speed, active adaptation) |
- **Evidence**: Plausible from paradigm — SB1 and SB2 markers explicitly denote distinct walking conditions (tied vs. split belt speeds) within the experimental protocol. Gait patterns differ substantially between conditions, allowing classifier training.
- **Kernel Notes**: SB1/SB2 blocks capture the core experimental manipulation. Consider excluding transition periods (first 5–10 seconds per block) to focus on steady-state adaptation. Admin markers (End SB1, End SB2) should be excluded.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
