# BCI Competition III Dataset II (P300 Speller)

**Dataset**: `bcic_iii_2` | **Year**: 2005 | **URL**: https://www.bbci.de/competition/iii/download/
**Category**: Action/Output | **Subjects**: 2 | **Files (Completed)**: 4 (Case B kernel; 2 Train + 2 Test) | **Channels**: 64 | **Sampling Rate**: 240 Hz

## Paradigm

Two subjects (A and B) attended to individual letters in a 6x6 character matrix while rows and columns flashed sequentially (BCI Competition III, 2005). Each character trial consisted of 15 sequences, each sequence comprising 12 flashes (6 rows + 6 columns). The P300 event-related potential, peaking ~300 ms after the target row or column flash, encodes the attended character. The training set contains 85 labeled characters per subject; the test set contains 100 characters without disclosed labels. The original `.mat` files are in a pre-epoched 3D format and are reconstructed into continuous raw data by the Case B kernel, which concatenates the 85 training sequences end-to-end.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iii/download/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `seq_onset` | 85 | admin | raw | Onset of each of the 85 character sequences (boundary marker) |
| `target_flash` | 2550 | short | raw | Flash of the row or column containing the target character |
| `nontarget_flash` | ~12750 | short | raw | Flash of a row or column not containing the target character |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts per Train file (1 file per subject). Test files have no class labels -> all annotations set to `unknown`.

## Tasks

### Primary Task 1: P300 Target Detection (ERP Binary Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 0.667 s *, target_events = [`target_flash`, `nontarget_flash`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `target_flash` | 1 | Flash of row/column containing attended character (P300 present) |
  | `nontarget_flash` | 0 | Flash of row/column not containing attended character |
- **Evidence**:
  - DOI: 10.1109/TBME.2008.915728 — Uses BCI Competition III Dataset II for binary classification of post-stimulus EEG signals as target (P300 present) vs non-target, extracting epochs from 0 to 667ms after stimulus onset.
  - DOI: 10.1016/j.asoc.2021.108176 — Extracts epochs in [0, 800] ms from stimulus onsets and classifies target versus non-target flashes.
  - DOI: 10.1016/j.heliyon.2023.e15380 — Evaluates P300 detection with 667 ms window length, downsampled to 40 Hz.
  - DOI: 10.1088/1741-2560/12.2.026009 — Uses 667 ms epoch length for standard target versus non-target classification.
  - DOI: 10.1109/access.2019.2919143 — Selects epochs from 0.2-0.6s post-stimulus for binary classification of attended versus unattended events.
  - DOI: 10.1109/access.2020.2968360 — Applies 800ms epoch window (tmin=0s, tmax=0.8s) for P300 detection.
  - DOI: 10.3389/fnins.2024.1360709 — Extracts 665ms epochs after each row/column intensification to classify target vs non-target flashes.
- **Kernel Notes**: Apply bandpass filter 0.1-30 Hz (Butterworth). Downsample to 25-40 Hz to reduce dimensionality. Use Train files only (Subject_A_Train.mat, Subject_B_Train.mat); Test files have no labels (all `unknown`). Class ratio is ~1:5 (target:nontarget); apply class-balancing or cost-sensitive learning. (replaces Normal Task 1 from original analysis.md)

## Data Quality Notes

- Class imbalance: ~1 target flash per 5-6 non-target flashes; balance before classification.
- Test labels are not publicly available; test files yield `unknown` annotations after kernel processing.
- Case B kernel: original `.mat` data is pre-epoched (3D array) and is reconstructed into a continuous raw signal; treat sequence boundaries marked by `seq_onset` as artificial discontinuities.
- Only 2 subjects; model generalization cannot be assessed from this dataset alone.

