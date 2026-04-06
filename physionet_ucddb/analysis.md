# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2011 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 (Case B kernel; 25 PSG .rec + 25 ECG _lifecard.edf) | **Channels**: variable (PSG) | **Sampling Rate**: variable

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

### Classical Task 1: Sleep stage classification (6-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 |
  | `Sleep stage 2` | 2 | NREM Stage 2 |
  | `Sleep stage 3` | 3 | NREM Stage 3 (slow-wave) |
  | `Sleep stage 4` | 4 | NREM Stage 4 (deep SWS) |
  | `Sleep stage REM` | 5 | REM sleep |
- **Super Meta Notes**: (NOT APPLICABLE - Meta Level = raw)
- **Evidence**:
  - DOI: 10.1371/journal.pone.0256111 — Uses the St. Vincent's Hospital/University College Dublin Sleep Apnea Database containing 25 overnight PSGs for 5-class sleep stage classification (W/N1/N2/N3/R), with R&K scored stages mapped to AASM 5-class format; uses 30s epochs (tmin=0s, tmax=30s).
- **Kernel Notes**: Exclude `Sleep stage 8` (undefined/artifact epochs). R&K stages 3 and 4 may optionally be merged to N3 per AASM standard if 5-class output is desired. Case B kernel handles `.rec` file reconstruction. (replaces Potential Task 1 from original analysis.md)

### Potential Task 2: Sleep Apnea Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` *or* `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 10 s, overlap = 0.5 *, target_events = [`apnea`, `non-apnea`] *
- **Label Route**: `event`
- **Target Definition**: Requires verification - apnea event annotations not currently present in raw event list.
- **Notes**: IEEE paper (10.1109/TENSYMP49402.2020.9230848) uses 10-second EEG frames for apnea/non-apnea classification. Raw EEG annotations for apnea events may need to be derived from external sources or respiratory signals in PSG. **This task requires verifying that apnea event annotations exist or can be derived from the dataset before implementation.**

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Age and sex information may be in `SubjectDetails.xls` within the dataset; the kernel loads demographics from this file if available.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review