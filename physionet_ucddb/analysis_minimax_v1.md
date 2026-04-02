# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2011 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 (Case B kernel; 25 PSG .rec + 25 ECG _lifecard.edf) | **Channels**: variable (PSG) | **Sampling Rate**: variable

## Paradigm

Twenty-five patients suspected of sleep-disordered breathing underwent overnight polysomnographic (PSG) monitoring at University College Dublin (UCD). PSG files are stored in `.rec` format (EDF-compatible) and contain multiple physiological signals. Sleep stages were scored by expert technicians and stored in companion `_stage.txt` files (30-second epochs: Wake, Stage 1-4, REM). Companion `_lifecard.edf` ECG files are co-located per subject but are not EEG recordings and are skipped by the kernel (-> `unknown` annotations). The Case B kernel reconstructs continuous raw signals from the non-standard `.rec` format.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/ucddb/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage W` | 4707 | long | raw | Wake (30-second epoch) |
| `Sleep stage 1` | 3016 | long | raw | NREM Stage 1 (R&K) |
| `Sleep stage 2` | 3403 | long | raw | NREM Stage 2 (R&K) |
| `Sleep stage 3` | 6985 | long | raw | NREM Stage 3 - slow-wave sleep (R&K) |
| `Sleep stage 4` | 673 | long | raw | NREM Stage 4 - deep SWS (R&K) |
| `Sleep stage REM` | 1990 | long | raw | REM sleep |
| `Sleep stage 8` | 15 | admin | raw | Undefined/artifact epoch (exclude from classification) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are totals across all 25 PSG files. `Sleep stage 8` indicates undefined or movement-time epochs. ECG `_lifecard.edf` files yield `unknown` annotations and should be excluded.

## Tasks

### Primary Task 1: Sleep Stage Classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0 s, target_events = ['Sleep stage W', 'Sleep stage 1', 'Sleep stage 2', 'Sleep stage 3', 'Sleep stage 4', 'Sleep stage REM']
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 (N1) |
  | `Sleep stage 2` | 2 | NREM Stage 2 (N2) |
  | `Sleep stage 3` | 3 | NREM Stage 3 - slow-wave sleep (N3) |
  | `Sleep stage 4` | 3 | NREM Stage 4 - deep SWS (merged to N3 per AASM) |
  | `Sleep stage REM` | 4 | REM sleep |
- **Super Meta Notes**: R&K stages 3-4 are merged into single N3 class per AASM standard; yields 5-class output (W/N1/N2/N3/REM).
- **Evidence**:
  - DOI: 10.1371/journal.pone.0256111 — Paper uses the UCD Sleep Apnea Database (25 overnight PSGs) for 5-class sleep stage classification, mapping R&K stages to AASM format with 30-second epochs.
- **Kernel Notes**: Merge stages 3 and 4 into single N3 label (y=3); exclude `Sleep stage 8` (undefined); resample to 100 Hz for consistency with paper (4×3000 input).

### Normal Task 1: Sleep Stage Classification - 6-Class (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `Sleep stage 8` (undefined epochs). ECG companion files (`_lifecard.edf`) yield `unknown` annotations and must not be used for sleep staging. Case B kernel: `.rec` files are read via `_read_edf_via_tempfile()`.

| Event | y | Meaning |
|-------|---|---------|
| `Sleep stage W` | 0 | Wake |
| `Sleep stage 1` | 1 | NREM Stage 1 |
| `Sleep stage 2` | 2 | NREM Stage 2 |
| `Sleep stage 3` | 3 | NREM Stage 3 |
| `Sleep stage 4` | 4 | NREM Stage 4 |
| `Sleep stage REM` | 5 | REM |


### Normal Task 2: Sleep Apnea Context - Wake vs. Sleep (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event`
- **Epoch Parameters**: Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification.
- **Notes**: Sleep apnea-related breathing events are not included in the current EEG annotations; the dataset can be used for stage classification as a secondary target. Respiratory signals in the PSG recordings can supplement EEG for apnea detection but require custom parsing.

## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Age and sex information may be in `SubjectDetails.xls` within the dataset; the kernel loads demographics from this file if available.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.

## References

- **Reference**: Heneghan C et al. (2011). UCD Sleep Apnea Database. PhysioNet. DOI: https://doi.org/10.13026/C26C7D
