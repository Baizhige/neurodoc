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

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: The official BCI Competition III Dataset II documentation defines P300 speller target-versus-nontarget decoding as the benchmark task. Source: https://www.bbci.de/competition/iii/ Official description PDF: `references/desc_II.pdf`


### Normal Task 1: P300 Target vs. Non-Target Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Use **Train files only** (`Subject_A_Train.mat`, `Subject_B_Train.mat`); Test files have no labels and all events are set to `unknown`. Class ratio is approximately 1:5 (target:nontarget); apply class-balancing or cost-sensitive learning. `seq_onset` is a boundary marker only and must be excluded. Reconstruction via Case B kernel concatenates sequences; discontinuities at sequence boundaries may introduce minor edge artifacts.

| Event | y | Meaning |
|-------|---|---------|
| `target_flash` | 1 | Flash of the attended row or column (P300 target) |
| `nontarget_flash` | 0 | Flash of a non-attended row or column |
## Data Quality Notes

- Class imbalance: ~1 target flash per 5-6 non-target flashes; balance before classification.
- Test labels are not publicly available; test files yield `unknown` annotations after kernel processing.
- Case B kernel: original `.mat` data is pre-epoched (3D array) and is reconstructed into a continuous raw signal; treat sequence boundaries marked by `seq_onset` as artificial discontinuities.
- Only 2 subjects; model generalization cannot be assessed from this dataset alone.

## References

- **Reference**: BCI Competition III (2005), Dataset II - P300 Speller. Wadsworth Center, NYS Department of Health. Wolpaw JR, Schalk G, Krusienski DJ. https://www.bbci.de/competition/iii/
