# Capacity for movement is an organisational principle in object representations: EEG data from Experiment 1

**Dataset**: `openneuro_ds003885` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003885
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 48
**Channels**: 127 | **Sampling Rate**: 250 Hz

## Paradigm

Participants performed a semantic classification task (alive vs. not alive) and a passive viewing task using RSVP streams of images to investigate the neural representations of object movement and aliveness. Images spanned animate and inanimate categories with varying degrees of movement capacity, presented at ~3 Hz in RSVP. The study aimed to decode movement-related object properties from EEG representational geometry.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 8` | ~115,200 | event | raw | RSVP image onset - condition 8 |
| `E 9` | ~115,200 | event | raw | RSVP image onset - condition 9 |
| `E 1` | ~38,400 | event | raw | RSVP image onset - condition 1 |
| `E 2` | ~38,400 | event | raw | RSVP image onset - condition 2 |
| `E 3` | ~38,400 | event | raw | RSVP image onset - condition 3 |
| `E 5` | ~38,400 | event | raw | RSVP image onset - condition 5 |
| `E 4` | ~960 | event | raw | Block boundary or special event |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Six-class Object Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`, `E 5`, `E 8`, `E 9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `E 1` | 0 | Animals (living) |
  | `E 2` | 1 | Plants (living) |
  | `E 3` | 2 | Still natural objects |
  | `E 5` | 3 | Still artificial objects |
  | `E 8` | 4 | Moving natural objects |
  | `E 9` | 5 | Moving artificial objects |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119517 — Uses EEG data from openneuro.ds003885 to decode six object categories (animals, plants, still natural, still artificial, moving natural, moving artificial) from neural responses using LDA classifiers, with epochs extracted from -0.3s to 1.0s relative to stimulus onset.
  - DOI: 10.1038/s41598-025-27703-5 — Reanalyzes the dataset to test how electrode density affects decoding accuracy for six natural image categories.
  - DOI: 10.1101/2025.07.07.663494 — Re-analyzes the dataset to test decoding performance across electrode densities, classifying EEG epochs into six natural image categories.
- **Kernel Notes**: Map raw event IDs E 1, E 2, E 3, E 5, E 8, E 9 to six semantic categories based on the experimental design. The dataset contains RSVP image presentations at ~3 Hz; epochs are extracted around each stimulus onset. Label y=0-5 corresponds to the six object categories. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Data from derivatives/eeglab; preprocessed with EEGLAB
- 128 channels recorded but analysis.md reports 127 (one likely reference or EOG)
- Very consistent event counts across all 24 subjects


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review