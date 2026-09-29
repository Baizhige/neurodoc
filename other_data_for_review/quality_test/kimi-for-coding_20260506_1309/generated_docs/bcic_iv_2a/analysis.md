# BCI Competition IV 2a

**Dataset**: `bcic_iv_2a` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2a.html
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 288 | **Channels**: 22 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

This dataset comprises EEG recordings from 9 healthy subjects performing 4-class motor imagery tasks. Subjects were cued to imagine movements of the left hand, right hand, both feet, or tongue. Data were recorded using a g.tec GAMMAsys amplifier with 22 Ag/AgCl electrodes placed according to the international 10-20 system. Each subject participated in two sessions on different days, with each session containing 288 trials (72 per class).

## File Scan Result

> **Kernel SHA256**: `1fd8cd3352fc0426e4b2dcdead0dae2c4f1cdb23026acf8bab41e621deb5586f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1023` | 488 | admin | raw | System marker: trial rejection or artifact flag |
| `1072` | 18 | event | raw | Trial phase onset: feedback or display event |
| `276` | 17 | event | raw | Trial phase onset: fixation or display event |
| `277` | 17 | event | raw | Trial phase onset: fixation or display event |
| `32766` | 160 | admin | raw | System marker: recording boundary or session start/stop |
| `768` | 5184 | event | raw | Trial phase onset: trial start or preparation cue |
| `769` | 648 | event | raw | Trial phase onset: class-specific cue (training, class 1) |
| `770` | 648 | event | raw | Trial phase onset: class-specific cue (training, class 2) |
| `771` | 648 | event | raw | Trial phase onset: class-specific cue (training, class 3) |
| `772` | 648 | event | raw | Trial phase onset: class-specific cue (training, class 4) |
| `783` | 2592 | event | raw | Trial phase onset: evaluation cue with hidden class label |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | complete | g.tec GAMMAsys |
| `cap` | complete | standard_1020_22ch |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Classical Task 1: 4-class motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`769`, `770`, `771`, `772`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `769` | 0 | class-specific cue (training, class 1) |
  | `770` | 1 | class-specific cue (training, class 2) |
  | `771` | 2 | class-specific cue (training, class 3) |
  | `772` | 3 | class-specific cue (training, class 4) |
- **Evidence**:
  - desc_2a.pdf — Official BCI Competition IV 2a description; defines 4 MI classes with event codes 769-772 for training data
  - 10.3389/fnins.2012.00039 — Classic EEG motor imagery decoding benchmark establishing the 4-class paradigm
  - 10.1109/tnnls.2018.2789927 — Deep learning evaluation on BCIC IV 2a using 0.5-4s epochs from cue onset
  - 10.1109/access.2021.3056088 — Comprehensive review confirming 769-772 as class-specific training cues and 783 as evaluation cue
- **Notes**: Event IDs 769-772 are locked as class-specific cues per dataset sidecar. The canonical 4-class mapping (left hand, right hand, both feet, tongue) is well-established in literature though sidecar meanings use generic class numbering. Evaluation files use 783 with hidden labels from .mat classlabel arrays; this task focuses on the directly-labeled training protocol. Epoch window inferred from common practice capturing preparation and early MI phase.


## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
