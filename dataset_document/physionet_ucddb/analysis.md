# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2007 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 | **Channels**: 14/16 | **Sampling Rate**: 8/64/128 | **Manual Review**:

## Paradigm

Twenty-five adult subjects suspected of sleep-disordered breathing underwent full overnight polysomnographic (PSG) monitoring at St. Vincent's University Hospital Sleep Disorders Clinic, Dublin, in the St. Vincent's University Hospital / University College Dublin Sleep Apnea Database. The PSG recordings are stored as EDF-format files with a `.rec` suffix and contain multiple physiological signals, including EEG (C3-A2, C4-A1), EOG, submental EMG, ECG, airflow, respiratory movement, oxygen saturation, snoring/body position, and pulse-related channels. Sleep stages were scored by an experienced sleep technologist according to Rechtschaffen and Kales rules and stored in companion `_stage.txt` files as 30-second epoch labels: 0 = Wake, 1 = REM, 2 = Stage 1, 3 = Stage 2, 4 = Stage 3, 5 = Stage 4, 6 = Artifact, and 7 = Indeterminate.

Companion `_lifecard.edf` files contain simultaneous three-channel Holter ECG recordings from a Reynolds Lifecard CF system and should not be treated as EEG/PSG sleep-staging recordings. For EEG benchmark processing, these Lifecard ECG files should be skipped or handled separately from the PSG `.rec` files.

## File Scan Result

> **Kernel SHA256**: `5a21cd5a5bcc0c99b7409bc5a0d9fd94e0dfe13724b983a03aaf2a5a769a952f`
> **EEGUnity Version**: `0.8.2`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Sleep stage 1` | 3016 | event | raw | NREM Stage 1 (R&K scoring) |
| `Sleep stage 2` | 3403 | event | raw | NREM Stage 2 (R&K scoring) |
| `Sleep stage 3` | 6985 | event | raw | NREM Stage 3 / slow-wave sleep (R&K scoring) |
| `Sleep stage 4` | 673 | event | raw | NREM Stage 4 / deep slow-wave sleep (R&K scoring) |
| `Sleep stage 8` | 15 | event | raw | Undefined or artifact epoch; exclude from standard sleep-stage classification |
| `Sleep stage REM` | 1990 | event | raw | Rapid eye movement sleep |
| `Sleep stage W` | 4707 | event | raw | Wake |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Classical Task 1: Sleep Stage Classification (5-class AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage REM`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 (N1) |
  | `Sleep stage 2` | 2 | NREM Stage 2 (N2) |
  | `Sleep stage 3` | 3 | NREM Stage 3 (AASM N3; merged with stage 4) |
  | `Sleep stage 4` | 3 | NREM Stage 4 (merged into AASM N3) |
  | `Sleep stage REM` | 4 | REM sleep |
- **Evidence**:
  - 10.1371/journal.pone.0256111 — 5-class sleep stage classification (W/N1/N2/N3/REM) using UCD Sleep Apnea Database; explicitly maps R&K stages 3 and 4 to single AASM N3 class; uses 30s epochs (tmin=0s, tmax=30s, no overlap); excludes undefined/artifact epochs.
- **Notes**: --

### Classical Task 2: Sleep Apnea Detection
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 0.5, target_events = []
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `apnea_label` | Binary 0/1: 0 = no apnea/hypopnea event overlaps the 10 s window; 1 = at least one apnea/hypopnea event overlaps the 10 s window. Derived from `_respevt.txt` files (not a native signal channel). Needs verification: channel not present in MISC Label Summary. |
- **Evidence**:
  - 10.1109/TENSYMP49402.2020.9230848 — Binary apnea/non-apnea classification using 10-second EEG frames with 50% overlap from the UCD sleep apnea database; positive class includes obstructive, central, and mixed apnea/hypopnea events.
- **Notes**: --

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Comprehensive clinical demographics in `SubjectDetails.xls` for all 25 subjects: Age, Gender, BMI, and PSG AHI (Apnea-Hypopnea Index).
- Sleep stages in `_stage.txt` are encoded as pure integers (0,1,2,3,4,5,8) representing 30s epochs — kernel must implement numeric-to-stage mapping.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
