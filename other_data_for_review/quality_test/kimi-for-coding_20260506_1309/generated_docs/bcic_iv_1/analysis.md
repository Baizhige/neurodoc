# BCI Competition IV Dataset 1

**Dataset**: `bcic_iv_1` | **Year**: 2008 | **URL**: http://www.bbci.de/competition/iv/desc_1.html
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 7 | **Channels**: 59 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Seven healthy subjects performed motor imagery tasks using a custom 59-channel EEG cap with BrainAmp MR plus amplifiers. In each trial, subjects imagined left or right hand movements following a visual cue. The dataset contains two event types marking trial phase onsets for left (-1) and right (1) motor imagery conditions, with 700 trials per class. Data was recorded at 1000 Hz and later downsampled to 100 Hz for competition purposes, though original recordings are available.

## File Scan Result

> **Kernel SHA256**: `844c56afe0088cb28b36e025083f719e6f35afab2ab366b7ef160f8b88bc8bd1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `-1` | 700 | event | raw | Trial phase onset: left |
| `1` | 700 | event | raw | Trial phase onset: right |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (5/7) | samples: 31, 26, 24; count=5, seen=7 |
| `amplifier` | complete | BrainAmp MR plus; count=7, seen=7 |
| `cap` | complete | custom 59-channel cap; count=7, seen=7 |
| `handedness` | partial (5/7) | right; count=5, seen=7 |
| `sex` | partial (5/7) | male, female; count=5, seen=7 |

## Tasks

### Classical Task 1: 2-class motor imagery (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`-1`, `1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `-1` | 0 | left |
  | `1` | 1 | right |
- **Evidence**:
  - 10.1109/icoras.2016.7872610 — "4s task period" for calibration data; uses BCIC IV Dataset 1 for binary motor imagery classification
  - 10.1109/tnsre.2020.3020975 — Uses BCIC IV Dataset 1 for motor imagery classification with multi-band CSP features
  - 10.1109/tnsre.2021.3071140 — Describes fixation 2s then cue at t=2s with MI until cross disappears, suggesting 4s total trial length; sliding time windows with channel selection achieving ~83.8% accuracy
- **Notes**: Event IDs `-1` and `1` are the literal marker values from mrk.y in the .mat files. The mapping to left/right is grounded by: (1) nfo.classes=['left', 'right'] array ordering convention where first class corresponds to negative/lower value (-1), and (2) the EVENT MEANINGS locked ground truth confirming `-1` = "Trial phase onset: left" and `1` = "Trial phase onset: right". Despite the "Trial phase onset" phrasing, these are the class-discriminative markers for motor imagery tasks in this dataset, with the actual MI period following the cue. The 4s epoch window captures the full task period from cue onset as described in the references.


## Data Quality Notes

- Partial demographic metadata: age, handedness, and sex information available for only 5 of 7 subjects.
- Original sampling rate is 1000 Hz, but competition-provided data was downsampled to 100 Hz; verify which version is being used for analysis.
- Event markers (-1, 1) represent trial phase onsets rather than continuous motor imagery periods; actual motor imagery execution follows the cue after a fixation period.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
