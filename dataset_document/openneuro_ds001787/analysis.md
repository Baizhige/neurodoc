# EEG Meditation Study

**Dataset**: `openneuro_ds001787` | **Year**: 2018/2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Twenty-four meditators (12 expert with ≥10 years daily practice, 12 novices) engaged in sustained meditation sessions. The released BDF files contain 80 channels (64 EEG, 15 auxiliary/misc physiological channels, and one BioSemi Status channel) sampled at 256 Hz after downsampling from the original 2048 Hz recordings. Approximately every two minutes, a brief probe interrupted the session to assess concentration level or mind-wandering, with subjects providing button-press responses. The study examines neural correlates of sustained attention, including infraslow activity coupled with autonomic markers like galvanic skin response.

## File Scan Result

> **Kernel SHA256**: `377803ea82e8e3e2c7cbb78f82abd7bb1a5a1723dac9b49a67ff799a39eb1fc4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `128` | 983 | event | raw | First question onset during the meditation probe |
| `16` | 2 | event | raw | Involuntary response marker |
| `2` | 1131 | event | raw | Response 1 to one of the probe questions |
| `254` | 5 | event | raw | BioSemi STATUS marker; administrative trigger not tied to a probe response |
| `4` | 754 | event | raw | Response 2 to one of the probe questions |
| `8` | 258 | event | raw | Response 3 to one of the probe questions |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `EXG1` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG2` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG3` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG4` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG5` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG6` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG7` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `EXG8` | native (raw misc in EEG file) | raw | Native BioSemi EXG auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Erg1` | native (raw misc in EEG file) | raw | Native BioSemi auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Erg2` | native (raw misc in EEG file) | raw | Native BioSemi auxiliary channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `GSR1` | native (raw misc in EEG file) | raw | Native galvanic skin response channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `GSR2` | native (raw misc in EEG file) | raw | Native galvanic skin response channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Plet` | native (raw misc in EEG file) | raw | Native plethysmography/PPG channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Resp` | native (raw misc in EEG file) | raw | Native respiration channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |
| `Temp` | native (raw misc in EEG file) | raw | Native temperature channel; units are n/a in channels.tsv; sample-aligned with EEG and not derived |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | partial (38/40) | N/A |
| `subject_sex` | complete | N/A |
| `device` | complete | N/A |
| `amplifier` | complete | e.g. BIOSEMI ActiveTwo |
| `cap` | complete | e.g. BioSemi 64-channel cap |
| `group` | complete | e.g. expert, novice |

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
> **Status**: wait_manual_review
