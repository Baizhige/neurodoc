# IEEE ICASSP 2024 EEG Competition Dataset

**Dataset**: `ieee_icassp_competition_2024` | **Year**: 2024 | **URL**: https://2024.ieeeicassp.org/
**Category**: High-level Mental | **Subjects**: 48 | **Files (Completed)**: 96 | **Channels**: 73 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Forty-eight subjects participated in two EEG-based speech BCI paradigms recorded with a 72-channel BioSemi ActiveTwo cap (plus Status stim channel, total 73) at 256 Hz. Task II_II (Imagined + Inner Speech): subjects imagined speaking or performed inner speech, with two stimulus classes (trigger codes 101 and 102, ~200 events each per session). Task RBII (Real Speech + BCI): subjects produced real speech with BCI feedback under the same two class scheme. Each subject contributed one file per task type (48 x 2 = 96 BDF files). Trigger codes are stored in the BioSemi Status stim channel and extracted via `mne.find_events()`.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Sampled

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `101` | ~9600 (200/file x 48) | short | raw | Stimulus class 1 onset (imagined/inner speech condition 1) |
| `102` | ~9600 (200/file x 48) | short | raw | Stimulus class 2 onset (imagined/inner speech condition 2) |
| `3` | varies | short | raw | Auxiliary trigger (task boundary or response marker) |
| `4` | varies | short | raw | Auxiliary trigger (task boundary or response marker) |
| `65536` | ~144 (3/file x 48) | admin | raw | BioSemi system trigger |
| `65790` | ~192 (4/file x 48) | admin | raw | BioSemi system trigger |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Trigger codes are stored as integer-string annotations converted from BioSemi Status stim channel values. Events 65536 and 65790 are BioSemi hardware codes and should be excluded from analysis.

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

- **File Format**: BDF
- **Total Files**: 96 (48 subjects x 2 paradigms)
- **Paradigms**: II_II (Imagined/Inner Speech), RBII (Real Speech with BCI feedback)
- **Status Channel**: BioSemi Status stim channel stores trigger codes

## Tasks

### Primary Task 1: Speech BCI challenge classification (inner/overt tracks)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Competition-provided trial labels for imagined/inner speech and real speech tracks.
- **Evidence**: IEEE ICASSP 2024 EEG BCI Grand Challenge defines supervised speech-BCI classification as the core task. Source: https://2024.ieeeicassp.org/ DOI: https://doi.org/10.1109/icasspw62465.2024.10626244


### Normal Task 1: Imagined/Inner Speech Classification - Class 1 vs. Class 2 (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s (per stimulus onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Filter to II_II task files (filename contains `II_II`) for imagined/inner speech paradigm, or RBII files for real speech BCI. Exclude events 65536 and 65790 (BioSemi system codes). The kernel stores all Status stim channel values as string annotations.

| Event | y | Meaning |
|-------|---|---------|
| `101` | 0 | Stimulus class 1 |
| `102` | 1 | Stimulus class 2 |


### Normal Task 2: Real Speech BCI Classification - Class 1 vs. Class 2 (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s (per stimulus onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Filter to RBII task files (filename contains `RBII`). Same event codes as Task 1; task type is identified from filename pattern.

| Event | y | Meaning |
|-------|---|- --------|
| `101` | 0 | Stimulus class 1 |
| `102` | 1 | Stimulus class 2 |

## Data Quality Notes

- Two distinct paradigms (II_II and RBII) stored in separate files; analyze separately.
- Trigger code semantics (exact speech content per class) require the competition documentation for full interpretation.
- 73 channels include 72 EEG + 1 Status stim channel; exclude Status before analysis.
- 4 auxiliary channels (M1, M2, NAS, plus EOG channels) are present; identify and remove non-EEG channels.
- No age or sex information available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
