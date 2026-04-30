# KU Leuven Auditory Attention Decoding Dataset

**Dataset**: `zenodo_kul` | **Year**: 2020 | **URL**: https://zenodo.org/records/4004271
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 15 | **Channels**: 64 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

Fifteen subjects performed a dichotic listening auditory attention decoding (AAD) task (Biesmans et al., 2017). Two competing story narratives were presented simultaneously, one to each ear, and subjects were instructed to attend to one. EEG was recorded from 64 channels (BioSemi ActiveTwo, standard 10-20 layout) at 128 Hz. Each MATLAB `.mat` file contains 20 trials (10 attended-left + 10 attended-right), stored as a Python list of trial dictionaries. The Case B kernel concatenates all 20 trials from each file into a single continuous raw signal and creates per-trial annotations indicating the attended ear.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attended_left` | 150 (10/subject x 15 subjects) | event | raw | Subject attends to the left-ear speaker |
| `attended_right` | 150 (10/subject x 15 subjects) | event | raw | Subject attends to the right-ear speaker |

>
> Case B kernel: 20 trials (each ~62.5 s at 128 Hz) concatenated into one continuous raw per file.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Dichotic Auditory Attention Decoding (Left vs. Right Ear)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s *, overlap = 0.0, target_events = [`attended_left`, `attended_right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attended_left` | 0 | Attended ear: left |
  | `attended_right` | 1 | Attended ear: right |
- **Evidence**:
  - DOI: 10.1109/TBME.2019.2911728 — Uses KU Leuven AAD dataset for auditory attention detection by reconstructing speech envelope from 64-channel EEG and classifying which ear was attended based on correlation analysis. Trials are ~60s duration.
- **Kernel Notes**: Uses speech envelope reconstruction via least-squares estimation; compares decoder output correlation with left vs. right speaker envelopes to determine attended ear. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Auditory Attention Decoding - Left vs. Right Ear (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, use trial duration from annotation, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Case B kernel uses `scipy.io.loadmat(simplify_cells=True)` and a custom `load()` method. Annotation durations match individual trial lengths. Balanced design: 10 trials per class per subject.

| Event | y | Meaning |
|-------|---|---------|
| `attended_left` | 0 | Attended ear: left |
| `attended_right` | 1 | Attended ear: right |

## Data Quality Notes

- Low sampling rate (128 Hz); limits high-frequency analysis but is standard for EEG-AAD.
- 15 subjects only; relatively small cohort for robust model evaluation.
- No age or sex information available in the public release.
- Each file contains 20 trials; the Case B kernel creates discontinuities at trial boundaries (artificial concatenation).

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
