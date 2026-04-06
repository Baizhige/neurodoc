# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2011 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 | **Channels**: variable | **Sampling Rate**: variable
**Manual Review**: Jiping Cui

## Paradigm

Twenty-five patients suspected of sleep-disordered breathing underwent overnight polysomnographic (PSG) monitoring at University College Dublin (UCD). PSG files are stored in `.rec` format (EDF-compatible) and contain multiple physiological signals. Sleep stages were scored by expert technicians and stored in companion `_stage.txt` files (30-second epochs: Wake, Stage 1-4, REM). Companion `_lifecard.edf` ECG files are co-located per subject but are not EEG recordings and are skipped by the kernel (-> `unknown` annotations). The Case B kernel reconstructs continuous raw signals from the non-standard `.rec` format.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage W` | 4707 | event | raw | Wake (30-second epoch) |
| `Sleep stage 1` | 3016 | event | raw | NREM Stage 1 (R&K) |
| `Sleep stage 2` | 3403 | event | raw | NREM Stage 2 (R&K) |
| `Sleep stage 3` | 6985 | event | raw | NREM Stage 3 - slow-wave sleep (R&K) |
| `Sleep stage 4` | 673 | event | raw | NREM Stage 4 - deep SWS (R&K) |
| `Sleep stage REM` | 1990 | event | raw | REM sleep |
| `Sleep stage 8` | 15 | admin | raw | Undefined/artifact epoch (exclude from classification) |

>
> Counts are totals across all 25 PSG files. `Sleep stage 8` indicates undefined or movement-time epochs. ECG `_lifecard.edf` files yield `unknown` annotations and should be excluded.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Sleep Stage Classification (5-class AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 (N1) |
  | `Sleep stage 2` | 2 | NREM Stage 2 (N2) |
  | `Sleep stage 3` | 3 | NREM Stage 3 (Deep SWS, AASM N3) |
  | `Sleep stage 4` | 3 | NREM Stage 4 merged into N3 per AASM standard |
  | `Sleep stage REM` | 4 | REM sleep |
- **Evidence**:
  - DOI: 10.1371/journal.pone.0256111 — Uses the UCD Sleep Apnea Database (25 overnight PSGs) for 5-class sleep stage classification (W/N1/N2/N3/R); explicitly maps R&K stages 3 and 4 to the single AASM N3 class; uses 30s epochs (tmin=0s, tmax=30s).
- **Kernel Notes**: Kernel MUST map both `Sleep stage 3` and `Sleep stage 4` to y=3 (AASM N3). Exclude `Sleep stage 8` (undefined/artifact epochs). Case B kernel handles `.rec` file reconstruction.

### Classical Task 2: Sleep Apnea Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event Type in `_respevt.txt` | y | Meaning |
  |------------------------------|---|---------|
  | `APNEA-O`, `APNEA-C`, `APNEA-M` | 1 | Obstructive, Central, or Mixed Apnea |
  | `HYP-O`, `HYP-C` | 1 | Obstructive or Central Hypopnea |
  | Background (no event) | 0 | Non-apneic period |
- **Evidence**:
  - DOI: 10.1109/TENSYMP49402.2020.9230848 — Uses 10-second EEG frames from UCD sleep database for binary apnea/non-apnea classification.
- **Kernel Notes**: Apnea/Hypopnea events are in companion `_respevt.txt` files with precise HH:MM:SS onset and duration. Kernel must parse these files, align timestamps with EEG recording onset, and map to 10-second sliding windows (label=1 if any apnea/hypopnea event overlaps the window, else 0).

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Comprehensive clinical demographics in `SubjectDetails.xls` for all 25 subjects: Age, Gender, BMI, and PSG AHI (Apnea-Hypopnea Index).
- Sleep stages in `_stage.txt` are encoded as pure integers (0,1,2,3,4,5,8) representing 30s epochs — kernel must implement numeric-to-stage mapping.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review