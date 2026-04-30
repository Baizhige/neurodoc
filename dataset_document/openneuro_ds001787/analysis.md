# EEG Meditation Study

**Dataset**: `openneuro_ds001787` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Twenty-four meditators (12 expert with ≥10 years daily practice, 12 novices) engaged in sustained meditation sessions continuously recorded at 256 Hz. Approximately every two minutes, a brief probe interrupted the session to assess concentration level or mind-wandering, with subjects providing button-press responses. The study examines neural correlates of sustained attention, including infraslow activity coupled with autonomic markers like galvanic skin response.

## File Scan Result

> **Kernel SHA256**: `a4bdc0abf3528185c2c555d74381ad494021cdfafb528ab69250f7b1a8398a99`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `B1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B10` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B11` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B12` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B13` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B14` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B15` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B16` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B17` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B18` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B19` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B20` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B21` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B22` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B23` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B24` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B25` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B26` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B27` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B28` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B29` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B3` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B30` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B31` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B32` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B4` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B5` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B6` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B7` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B8` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `B9` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG3` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG4` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG5` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG6` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG7` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG8` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Erg1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Erg2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `GSR1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `GSR2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Plet` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Resp` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Status` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `Temp` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `B1`, `B10`, `B11`, `B12`, `B13`, `B14`, `B15`, `B16`, `B17`, `B18`, `B19`, `B2`, `B20`, `B21`, `B22`, `B23`, `B24`, `B25`, `B26`, `B27`, `B28`, `B29`, `B3`, `B30`, `B31`, `B32`, `B4`, `B5`, `B6`, `B7`, `B8`, `B9`, `EXG1`, `EXG2`, `EXG3`, `EXG4`, `EXG5`, `EXG6`, `EXG7`, `EXG8`, `Erg1`, `Erg2`, `GSR1`, `GSR2`, `Plet`, `Resp`, `Status`, `Temp`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: GSR amplitude regression from meditation EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |------------------|-----------------|
  | GSR1 | no mapping |
- **Evidence**:
  - 10.3389/fnins.2022.765585 — Reference paper explicitly analyzes ISA-GSR coupling during meditation; GSR1 and GSR2 are continuous native misc channels on the raw object (BioSemi ActiveTwo with 15 misc channels)
- **Notes**: B1 archetype (native misc channel regression). GSR1 selected as primary GSR channel; GSR2 also available as redundant backup. Segment length of 10s inferred from paper's analysis of sustained meditation states (first 30s period after meditation onset), with non-overlapping windows for independent samples.

### Potential Task 2: Respiration-EEG Coupling Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |------------------|-----------------|
  | Resp | no mapping |
- **Evidence**:
- **Notes**: Native misc channel "Resp" is present in the BioSemi ActiveTwo channel set (confirmed in eeg.json: MiscChannelCount=15, and Resp appears in native misc channel catalog). The task uses 10-second non-overlapping windows to capture multiple respiratory cycles at typical resting rates (~12-20 breaths/min ≈ 3-5 s/cycle). The regression target is the continuous respiration signal amplitude, enabling investigation of EEG-respiration coupling during meditation practice.

### Potential Task 3: Temperature-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |------------------|-----------------|
  | Temp | no mapping |
- **Evidence**:
  - `eeg.json` — BioSemi ActiveTwo recording with MiscChannelCount=15, confirming auxiliary channels including Temp
  - `README` — Meditation study with continuous recording; temperature as autonomic correlate of meditative state
- **Notes**: Native misc channel `Temp` is a continuous non-EEG signal already present in the raw BDF files. No kernel derivation needed; the regression target is read directly from the `Temp` channel. The 10-second segmentation window is chosen because temperature changes slowly relative to EEG dynamics, providing sufficient samples per epoch for stable regression targets.

### Potential Task 4: Plethysmography-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |------------------|-----------------|
  | Plet | no mapping |
- **Evidence**:
  - [eeg.json, README] — Dataset includes native MISC channel `Plet` (plethysmography) among 15 misc channels; continuous recording during meditation task with ~2-minute interruption intervals for self-report.
- **Notes**: Archetype B1: native misc channel `Plet` is directly available on the raw data as a continuous peripheral physiological recording. No kernel derivation needed. The 10-second segmentation windows are chosen to capture multiple cardiac cycles for stable cardiovascular-EEG coupling estimation.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
