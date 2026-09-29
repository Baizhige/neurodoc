# EEG During Mental Arithmetic Tasks

**Dataset**: `physionet_eegmat` | **Year**: 2018 | **URL**: https://doi.org/10.13026/C2JQ1P
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 21 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from 36 healthy adult subjects during two conditions: a resting baseline and a mental arithmetic task. For the mental arithmetic task, subjects were instructed to silently perform serial subtraction (e.g., subtracting 7 from a given number continuously) for approximately 60 seconds. Each subject completed both conditions in separate recording sessions, resulting in two EDF files per subject (suffix _1 for rest, _2 for mental arithmetic). Recordings were made using a Neurocom 21-channel EEG system with silver/silver chloride electrodes arranged according to the International 10/20 system, referenced to interconnected ear electrodes.

## File Scan Result

> **Kernel SHA256**: `277e7cc6fb101a216dd966818c8e6341ac6c708f96702ce6f903f62fadb83888`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `mental_arithmetic` | 36 | event | raw |  |
| `rest_baseline` | 36 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `Count quality` | missing | Count quality is defined in subjects_info.xlsx column 'Count quality': 0 = Group 'B' (bad quality count, n=12, mean=7 ops/4min, SD=3.6), 1 = Group 'G' (good quality count, n=24, mean=21 ops/4min, SD=7.4) |
| `age` | missing | Age information is available in subjects_info.xlsx file which provides basic information about each subject |
| `amplifier` | missing | Neurocom EEG 23-channel system (Ukraine, XAI-MEDICA) |
| `cap` | missing | Silver/silver chloride electrodes placed according to International 10/20 scheme, all referenced to interconnected ear reference |
| `handedness` | missing |  |
| `sex` | missing | Gender information is available in subjects_info.xlsx file which provides basic information about each subject |

## Tasks

### Classical Task 1: Rest vs Mental Arithmetic Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, overlap = 0.0, target_events = [`rest_baseline`, `mental_arithmetic`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `rest_baseline` | 0 | Resting baseline EEG (file suffix _1) |
  | `mental_arithmetic` | 1 | Mental arithmetic task EEG (file suffix _2) |
- **Evidence**:
  - https://doi.org/10.13026/C2JQ1P — Official PhysioNet dataset documentation describing two conditions per subject: rest baseline (_1 files) and mental arithmetic task (_2 files)
  - https://doi.org/10.1109/INDICON49873.2020.9342140 — Paper using this dataset for rest vs mental arithmetic binary classification with 60-second segments
  - https://doi.org/10.1109/JSEN.2023.3337519 — Paper analyzing EEG mental arithmetic tasks using 60-second continuous epochs from this dataset
- **Notes**: This is an archetype A (event route) task. The dataset uses separate EDF files per condition rather than internal event markers; the kernel must map file suffixes (_1 → rest_baseline event, _2 → mental_arithmetic event) to create synthetic long events spanning the full recording duration. The tmax=60s captures the standard block length; some files extend to ~180s but 60s represents the canonical task/rest epoch used in the literature.



## Data Quality Notes

- Subject metadata (age, sex, count quality) is stored in a separate subjects_info.xlsx file not integrated into the EDF headers; manual merge required for demographic analyses.
- Count quality groups subjects into 'good' (n=24) and 'bad' (n=12) counters based on arithmetic performance, which may serve as a confound or secondary stratification variable.
- The amplifier field notes a 23-channel system but only 21 EEG channels are present in the data files (likely excluding EOG or reference channels from the count).
- No handedness information is available for any subject.
- Some recordings exceed the canonical 60-second task block length (up to ~180s); the standard literature convention uses 60-second epochs.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
