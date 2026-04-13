# SHU Motor Imagery EEG Dataset

**Dataset**: `figshare_shudb` | **Year**: 2022 | **URL**: https://figshare.com/articles/software/shu_dataset/19228725/1
**Category**: Action/Output | **Subjects**: 25 | **Files (Completed)**: 232 | **Channels**: 32 | **Sampling Rate**: 250 Hz

## Paradigm

Twenty-five healthy subjects (sub-001 to sub-025) performed cued left/right hand motor imagery across 5 sessions collected on different days. EEG was recorded with a 32-channel Ag/AgCl cap from Wuhan Greentech Technology Co., LTD and a wireless amplifier manufactured by Brickcom. Each session contained 100 trials, although a small number of trials in some sessions were removed during preprocessing. The dataset is organized according to EEG-BIDS: processed session-level EEG is provided as `.edf` files with accompanying `.tsv` event files, and trial-level classification-ready data is also provided as `.mat` files containing `data` and `labels`.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `left` | ~10900 (total) | event | raw | Left-hand motor imagery cue onset |
| `right` | ~10900 (total) | event | raw | Right-hand motor imagery cue onset |


> 387 files. Total counts are 255,100 trials across 25 subjects and 5 sessions each (100 trials per session), with a small number of trials removed in some sessions due to bad-segment rejection.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | Brickcom wireless amplifier; 32-channel Ag/AgCl cap from Wuhan Greentech Technology Co., LTD |


## Tasks

### Classical Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 4.0 s, tmax = 8.0 s, target_events = [`left`, `right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left` | 0 | Left-hand motor imagery |
  | `right` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1038/s41597 — 022-01647-1 — Original Paper. Uses 4-second EEG epochs extracted from 7.5s trials for binary classification between left and right hand motor imagery
  - DOI: 10.1016/j.heliyon.2024.e37343 — Validates multi-session left vs right hand motor imagery classification using CNN-based feature extraction with 4s MI window
  - DOI: 10.1016/j.jneumeth.2025.110483 — Validates on SHU dataset achieving 87.2% within-session and 67.2% cross-session accuracy for left/right hand MI
  - DOI: 10.1109/jbhi.2024.3467090 — Evaluates binary motor imagery classification on SHU dataset achieving 69.3% accuracy
  - DOI: 10.31083/j.jin2308153 — Evaluates 3D-CNN models for two-class motor imagery classification on SHU dataset
- **Kernel Notes**: 

## Data Quality Notes

- 25 healthy subjects (age 20–24, 12 females).
- Each subject completed 5 sessions. Each session nominally contains 100 trials, but some sessions are missing a small number of trials after bad-segment rejection.
- EEG was recorded with a 32-channel Ag/AgCl cap (standard 10-10 system) from Wuhan Greentech Technology Co., LTD and a wireless amplifier manufactured by Brickcom.
- The released files follow EEG-BIDS organization: processed session-level EEG is stored as `.edf` with accompanying `.tsv` event files, and trial-level data is also provided as `.mat` files.
- Bad segments were removed before release; preprocessing included baseline removal and 0.5-40 Hz FIR band-pass filtering.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
