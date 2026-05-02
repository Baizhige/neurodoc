# NOD-EEG

**Dataset**: `openneuro_ds005787` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005787
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 896 | **Channels**: 64 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

The NOD-EEG dataset contains 64-channel EEG recordings from a stimulus-response paradigm. Each trial includes a stimulus onset (`stim_on`), participant button-press response (`resp`), and block boundary markers (`begin`, `end`). The precise experimental task and stimuli are described in the dataset README.

## File Scan Result

> **Kernel SHA256**: `62fd264d1aa86ab37d154435cbc658ea3ee3b878224b0a992c6fb84e9fca31a4`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `resp` | 2273060 | event | raw | Participant button-press response |
| `stim_on` | 112000 | event | raw | Stimulus onset |
| `begin` | 896 | event | raw | Block begin marker |
| `end` | 896 | event | raw | Block end marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus-Response (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`stim_on`, `resp`, `begin`, `end`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stim_on` | 0 | Stimulus onset |
  | `resp` | 1 | Button-press response |
  | `begin` | 2 | Block begin |
  | `end` | 3 | Block end |
- **Kernel Notes**: Very high count for `resp` (2.27M total); verify no duplicate events. Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching. Epoch parameters tmin/tmax are estimated defaults — verify against experimental protocol in dataset README.
- **Notes**: The available raw events (`stim_on`, `resp`, `begin`, `end`) represent a basic stimulus-response paradigm. The specific cognitive task (e.g., Image Net classification as mentioned in BIDS metadata) requires verification from dataset documentation to define meaningful epoch windows and label groupings.

## Data Quality Notes

- Very high total event count for `resp`; verify no duplicate events.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: failed
