# BCI Competition IV-2b (BCIC IV-2b)

**Dataset**: `bcic_iv_2b` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2b.pdf
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 270 | **Channels**: 3 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from 9 subjects performing 2-class motor imagery tasks. Subjects imagined movements of their left hand (class 1) or right hand (class 2) in response to visual cues. Data were recorded using 3 bipolar EEG channels (C3, Cz, C4) with a sampling rate of 250 Hz. Each subject participated in multiple sessions including training sessions (with known labels) and evaluation sessions (without disclosed labels for competition purposes).

## File Scan Result

> **Kernel SHA256**: `28ab94f2b9506a5fb53abf1042120ffcf8306806685dc7eba5ba3abac5a767ec`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1023` | 1253 | event | raw | Trial phase onset: trial end |
| `1077` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `1078` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `1079` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `1081` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `276` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `277` | 43 | event | raw | Trial phase onset: eye movement calibration |
| `32766` | 262 | admin | raw | System marker: Start of recording |
| `768` | 6520 | event | raw | Trial phase onset: trial start |
| `769` | 1840 | event | raw | Trial phase onset: motor imagery cue type 1 |
| `770` | 1840 | event | raw | Trial phase onset: motor imagery cue type 2 |
| `781` | 4280 | event | raw | Trial phase onset: feedback/unknown cue type 1 |
| `783` | 2840 | event | raw | Trial phase onset: feedback/unknown cue type 2 |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | complete | standard_1020 |
| `handedness` | missing |  |
| `session_type` | complete | T, E |
| `sex` | missing |  |
| `subject_id` | complete | B0101, B0102, B0103 |

## Tasks

### Classical Task 1: 2-class motor imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`769`, `770`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `769` | 0 | motor imagery cue type 1 (left hand) |
  | `770` | 1 | motor imagery cue type 2 (right hand) |
- **Evidence**:
  - desc_2b.pdf — Official BCI Competition IV-2b dataset description: 2-class motor imagery paradigm with left hand vs right hand classification
  - 10.1016/j.neucom.2018.04.087 — Peer-reviewed paper using BCI IV-2b for left/right hand MI classification
  - 10.1038/s41598-025-96611-5 — Peer-reviewed paper confirming 2-class motor imagery on BCI IV-2b
  - 10.1109/tnsre.2022.3156076 — Peer-reviewed paper using BCI IV-2b with event codes 769/770 for training
  - 10.1109/tnsre.2023.3241846 — Peer-reviewed paper confirming left/right hand MI classification on BCI IV-2b
  - 10.1109/tnsre.2023.3242280 — Peer-reviewed paper using standard 0-4s epoch for BCI IV-2b motor imagery
  - 10.1186/s12859-018-2365-1 — Peer-reviewed paper with 2-class MI on BCI IV-2b
  - 10.3389/fnins.2020.00918 — Peer-reviewed paper confirming 769/770 as class labels in training sessions
  - 10.3390/s19010210 — Peer-reviewed paper using BCI IV-2b 2-class motor imagery
  - 10.3390/s20164485 — Peer-reviewed paper with left/right hand classification on BCI IV-2b
- **Notes**: Event codes 769 and 770 are training session markers with known class labels; evaluation sessions use 781/783 without disclosed labels. The .mat companion files contain classlabel arrays with values [1,2] confirming two classes. Epoch window 0-4s is standard for BCI Competition IV-2b following the 4-second imagery period in screening sessions. Left/right hand semantic mapping is inferred from the 2-class motor imagery paradigm convention, though the locked meanings only specify "cue type 1" and "cue type 2".



## Data Quality Notes

- Subject demographic fields (age, sex, handedness) are missing across all files.
- Only 3 bipolar channels (C3, Cz, C4) limits spatial resolution compared to full 10-20 montages.
- Evaluation session event codes (781, 783) have unknown class labels by design for competition purposes; only training sessions (769, 770) provide ground truth.
- Event counts show substantial imbalance between training cues (769/770: 1840 each) and feedback/unknown cues (781: 4280, 783: 2840), reflecting different session structures.
- The .mat companion files are required to resolve class labels and should be verified for consistency with event markers.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
