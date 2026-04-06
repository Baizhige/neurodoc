# Subcortical responses to music and speech are alike while cortical responses diverge

**Dataset**: `openneuro_ds004356` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004356
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 24
**Channels**: 34 | **Sampling Rate**: 10000 Hz

## Paradigm

The study measures subcortical Auditory Brainstem Responses (ABR) to continuous clicks, music genres, and speech stimuli using a deconvolution method. Participants passively listened to 12 different audio categories (Chinese speech, English speech, 8 music genres, acoustic guitar, and click trains) to compare subcortical and cortical neural encoding across stimulus types.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `click` | 22x10 | event | raw | Continuous click train stimulus |
| `acoustic` | 22x40 | event | raw | Acoustic guitar stimulus |
| `classical` | 22x40 | event | raw | Classical music stimulus |
| `jazz` | 22x40 | event | raw | Jazz music stimulus |
| `pop` | 22x40 | event | raw | Pop music stimulus |
| `metal` | 22x40 | event | raw | Metal music stimulus |
| `hiphop` | 22x40 | event | raw | Hip-hop music stimulus |
| `chn_aud` | 22x40 | event | raw | Chinese speech stimulus |
| `eng_aud` | 22x40 | event | raw | English speech stimulus |
| `news` | 22x40 | event | raw | News speech stimulus |
| `talk` | 22x40 | event | raw | Talk speech stimulus |
| `interview` | 22x40 | event | raw | Interview speech stimulus |
| `lecture` | 22x40 | event | raw | Lecture speech stimulus |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Music vs Speech Binary Classification from Auditory Brainstem Responses
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12 s *, overlap = 0.0 *, target_events = [`acoustic`, `classical`, `jazz`, `pop`, `metal`, `hiphop`, `chn_aud`, `eng_aud`, `news`, `talk`, `interview`, `lecture`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `acoustic` | 0 | Music stimulus |
  | `classical` | 0 | Music stimulus |
  | `jazz` | 0 | Music stimulus |
  | `pop` | 0 | Music stimulus |
  | `metal` | 0 | Music stimulus |
  | `hiphop` | 0 | Music stimulus |
  | `chn_aud` | 1 | Speech stimulus |
  | `eng_aud` | 1 | Speech stimulus |
  | `news` | 1 | Speech stimulus |
  | `talk` | 1 | Speech stimulus |
  | `interview` | 1 | Speech stimulus |
  | `lecture` | 1 | Speech stimulus |
- **Evidence**:
  - DOI: 10.1038/s41598-023-50438-0 — Binary classification of music vs speech based on auditory brainstem responses (ABR) using deconvolution on continuous 12s stimuli from OpenNeuro dataset ds004356
- **Kernel Notes**: Extract continuous stimulus blocks (12s duration). Apply bandpass filtering appropriate for subcortical ABR analysis (e.g., 70-2000 Hz) or cortical analysis (e.g., 0.5-40 Hz). The paper analyzes both subcortical kernel [0,15]ms and cortical kernel [0,200]ms responses. Use label 0 for music categories, label 1 for speech categories. (replaces Classical Task 1 and Potential Task 1 from original analysis.md)

### Classical Task 2: Click Train ABR Control Task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12 s *, overlap = 0.0 *, target_events = [`click`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `click` | 0 | Click train control stimulus |
- **Evidence**:
  - DOI: 10.1038/s41598-023-50438-0 — Uses click train stimuli as control condition for measuring auditory brainstem responses
- **Kernel Notes**: Extract continuous click train blocks (12s duration). Click trains serve as a reference/control condition for ABR analysis to establish baseline brainstem response characteristics. Apply appropriate ABR filtering (70-2000 Hz).

## Data Quality Notes

- Very high sampling rate (10 kHz) designed for subcortical ABR; bandpass filtering required for cortical analysis
- 2 subjects have 2 files each (24 files, 22 subjects)
- Balanced stimulus presentation (40 trials per condition for most categories)


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review