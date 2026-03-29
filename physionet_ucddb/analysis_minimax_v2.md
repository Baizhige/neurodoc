# UCD Sleep Apnea Database

**Dataset**: `physionet_ucddb` | **Year**: 2011 | **URL**: https://physionet.org/content/ucddb/1.0.0/
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 50 (Case B kernel; 25 PSG .rec + 25 ECG _lifecard.edf) | **Channels**: variable (PSG) | **Sampling Rate**: variable | **Manual Review**: Jiping Cui

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
| `0` | 4707 | long | raw | Wake (30-second epoch) |
| `1` | 3016 | long | raw | NREM Stage 1 (R&K) |
| `2` | 3403 | long | raw | NREM Stage 2 (R&K) |
| `3` | 6985 | long | raw | NREM Stage 3 - slow-wave sleep (R&K) |
| `4` | 673 | long | raw | NREM Stage 4 - deep SWS (R&K) |
| `5` | 1990 | long | raw | REM sleep |
| `8` | 15 | admin | raw | Undefined/artifact epoch (exclude from classification) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are totals across all 25 PSG files. `Sleep stage 8` indicates undefined or movement-time epochs. ECG `_lifecard.edf` files yield `unknown` annotations and should be excluded.

## Tasks

### Primary Task 1: Sleep stage classification (5-class AASM mapped)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`0`, `1`, `2`, `3`, `4`, `5`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event (Raw in `_stage.txt`) | y | Meaning |
  |-----------------------------|---|---------|
  | `0` | 0 | Wake |
  | `1` | 1 | NREM Stage 1 (N1) |
  | `2` | 2 | NREM Stage 2 (N2) |
  | `3`, `4` | 3 | NREM Stage 3 (Deep SWS mapped to AASM N3) |
  | `5` | 4 | REM sleep |
- **Super Meta Notes**: (NOT APPLICABLE - Meta Level = raw)
- **Evidence**:
  - DOI: 10.1371/journal.pone.0256111 — Uses the St. Vincent's Hospital/University College Dublin Sleep Apnea Database containing 25 overnight PSGs for 5-class sleep stage classification (W/N1/N2/N3/R). Explicitly maps legacy R&K scored stages (3 and 4) to the AASM 5-class format (N3); uses discrete 30s epochs (tmin=0s, tmax=30s).
- **Kernel Notes**: Sleep stages are strictly encoded as integers in the raw txt files. The Kernel MUST map both raw events `3` and `4` to the single class `y=3` to adhere to the AASM 5-class standard validated by the reference literature. Exclude artifact/undefined epochs marked as `8`. Case B kernel handles `.rec` file reconstruction.

### Normal Task 2: Sleep Apnea Detection
- **Task Type**: classification (binary)
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 5.0 s
- **Label Route**: `Annotation`
- **Target Definition**: 
  | Event Type in `_respevt.txt` | y | Meaning |
  |------------------------------|---|---------|
  | `APNEA-O`, `APNEA-C`, `APNEA-M` | 1 | Obstructive, Central, or Mixed Apnea |
  | `HYP-O`, `HYP-C` | 1 | Obstructive or Central Hypopnea |
  | `Background` (No event) | 0 | Non-apneic period |
- **Notes**: Apnea/Hypopnea events are explicitly detailed in companion `_respevt.txt` files (including precise onset Time and Duration). The Kernel must parse these external text files, align the HH:MM:SS timestamps with the EEG recording onset, and map them to the corresponding 10-second EEG sliding windows to generate binary labels (1 for presence of event, 0 for normal breathing).


## Data Quality Notes

- Case B kernel; `.rec` files require EDF-via-tempfile workaround; `_lifecard.edf` ECG files are excluded (-> `unknown` annotations in locator).
- Comprehensive clinical demographics are explicitly provided in `SubjectDetails.xls` for all 25 subjects, including Age, Gender, BMI, and the critical clinical metric `PSG AHI` (Apnea-Hypopnea Index).
- **Crucial Kernel Note**: Sleep stages in `_stage.txt` are encoded as pure integers (e.g., 0, 1, 2, 3, 4, 5, 8) representing 30s epochs, NOT as text strings. The Kernel MUST implement a numeric-to-stage mapping dictionary (e.g., 0=Wake, 1=REM, etc. based on UCDDB format standards) to parse these files correctly.
- R&K scoring system (stages 1-4 + REM); not directly comparable to AASM (N1/N2/N3) datasets.
- Small dataset (25 subjects); combine with other sleep databases for robust model training.

## References

- **Reference**: Heneghan C et al. (2011). UCD Sleep Apnea Database. PhysioNet. DOI: https://doi.org/10.13026/C26C7D
