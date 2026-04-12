# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2007 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 | **Channels**: 14/16 | **Sampling Rate**: 8/64/128
**Manual Review**: Jiping Cui

## Paradigm

Twenty-five patients suspected of sleep-disordered breathing underwent overnight polysomnographic (PSG) monitoring at University College Dublin (UCD). PSG files are stored in `.rec` format (EDF-compatible) and contain multiple physiological signals. Sleep stages were scored by expert technicians and stored in companion `_stage.txt` files as integer codes for each 30-second epoch (e.g., 0=Wake, 1-4=NREM Stages, 5=REM). Companion `_lifecard.edf` ECG files are co-located per subject but are not EEG recordings and are skipped by the kernel (-> `unknown` annotations). The Case B kernel reconstructs continuous raw signals from the non-standard `.rec` format.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Sleep stage W` | 4707 | event | raw | Wake (30-second epoch) |
| `Sleep stage 1` | 3016 | event | raw | NREM Stage 1 (R&K) |
| `Sleep stage 2` | 3403 | event | raw | NREM Stage 2 (R&K) |
| `Sleep stage 3` | 6985 | event | raw | NREM Stage 3 - slow-wave sleep (R&K) |
| `Sleep stage 4` | 673 | event | raw | NREM Stage 4 - deep SWS (R&K) |
| `Sleep stage REM` | 1990 | event | raw | REM sleep |
| `Sleep stage 8` | 15 | admin | raw | Undefined/artifact epoch (exclude from classification) |


> Counts are totals across all 25 PSG files. Event 8 indicates undefined or movement-time epochs. ECG `_lifecard.edf` files yield `unknown` annotations and should be excluded.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Need Update. |
| `subject_sex` | missing | Need Update. |
| `device` | missing | Need Update. |


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
- **Kernel Notes**: 

### Classical Task 2: Sleep Apnea Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 0, target_events = [`APNEA-O`, `APNEA-C`, `APNEA-M`, `HYP-O`, `HYP-C`, `Background (no event)`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `APNEA-O`, `APNEA-C`, `APNEA-M` | 1 | Obstructive, Central, or Mixed Apnea |
  | `HYP-O`, `HYP-C` | 1 | Obstructive or Central Hypopnea |
  | `Background (no event)` | 0 | Non-apneic period |
- **Evidence**:
  - DOI: 10.1109/TENSYMP50017.2020.9230848 — Employs non-overlapping 10-second EEG segments and explicitly targets the binary classification of Apnea/Hypopnea events (SA) against normal breathing (NSA). (Note: The paper uses overlapping 2s sub-frames internally for feature extraction, but the macro epoching is non-overlapping 10s).
- **Kernel Notes**: 

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Comprehensive clinical demographics in `SubjectDetails.xls` for all 25 subjects: Age, Gender, BMI, and PSG AHI (Apnea-Hypopnea Index).
- Sleep stages in `_stage.txt` are encoded as pure integers (0,1,2,3,4,5,8) representing 30s epochs — kernel must implement numeric-to-stage mapping.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
