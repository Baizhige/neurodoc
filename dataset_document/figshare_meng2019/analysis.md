# EEG Dataset for Cursor BCI (Meng 2019)

**Dataset**: `figshare_meng2019` | **Year**: 2019 | **URL**: https://doi.org/10.6084/m9.figshare.7959572
**Category**: Action/Output | **Subjects**: 42 | **Files (Completed)**: 126 | **Channels**: 62/64 | **Sampling Rate**: 100/128 Hz | **Manual Review**: anonymous for review

## Paradigm

Participants performed a one-dimensional cursor BCI task using mental imagery in three experiments (Meng et al., 2019). EEG was recorded from 62/64 channels. Subjects imagined motor or other mental activities to move a cursor toward a target positioned Left or Right Side. The dataset covers three experiments (Exp1, Exp2, Exp3); Exp1 and Exp2 used a Neuroscan SynAmps RT amplifier, while Exp3 used a Biosemi Active Two system. The paradigm recorded both target intent events (what the subject was trying to do) and result events (what the BCI decoded), enabling analysis of mental imagery decoding accuracy.

## File Scan Result


> **Kernel SHA256**: `611ecb0061d5421f7b3f18f42bbe84280cb89edb888a676dde2ba49e90154dd2`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Sampled (3/126 files)
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `result cursor minus` | ~166 | event | raw | BCI decoded - direction (feedback signal) |
| `result cursor plus` | ~168 | event | raw | BCI decoded + direction (feedback signal) |
| `target cursor minus` | ~183 | event | raw | Target positioned below center; subject imagines left movement |
| `target cursor plus` | ~182 | event | raw | Target positioned above center; subject imagines right movement |
| `target rest` | ~365 | event | raw | Target at center; subject imagines neutral/rest state |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | missing | N/A |
| `device` | missing | Exp1 and Exp2 used a Neuroscan SynAmps RT amplifier, while Exp3 used a Biosemi Active Two system. |

## Tasks

### Potential Task 1: Two-class motor imagery cursor direction decoding (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 1.5 s, tmax = 4.5 s, target_events = [`target cursor plus`, `target cursor minus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `target cursor plus` | 1 | Left-hand motor imagery (cursor moves up/+) |
  | `target cursor minus` | 0 | Right-hand motor imagery (cursor moves down/-) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2019.00128 — This paper analyzes the same figshare dataset from 42 subjects performing left/right hand motor imagery to control a cursor BCI, evaluating behavioral performance and ERD/ERS patterns.
- **Notes**: 

## Data Quality Notes

- Sex information is not available in the dataset metadata.
- Three experiments (Exp1, Exp2, Exp3) use different amplifier systems; process per-experiment or normalize across systems.
- Subject count is not explicitly stated; estimate from unique subject folders in file paths.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
