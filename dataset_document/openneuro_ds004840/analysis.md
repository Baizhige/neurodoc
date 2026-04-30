# EEG/ECG/EMG During Music Therapy in ICU Burn Patients

**Dataset**: `openneuro_ds004840` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004840
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 68 | **Channels**: 10 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

Electrophysiological recordings (EEG, ECG, EMG) of adult burn patients in a clinical ICU environment during Music-Assisted Relaxation (MAR) therapy sessions. No event markers are present in the raw EEG data; however, phase events (PRE/MTI/POST) are derived from protocol timing metadata and mapped as events in the dataset. The study investigates physiological responses to music therapy as a pain and anxiety management intervention in ICU patients.

## File Scan Result

> **Kernel SHA256**: `d781d8bb83998be99a967f1595e5f0364ba2fe656956f059154b9ae9192e29a8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `phase:MTI` | 65 | event | raw | Trial phase onset: Music therapy intervention (MTI) - Music-Assisted Relaxation period |
| `phase:POST` | 42 | event | raw | Trial phase onset: Post-intervention period - resting state measured during patient reincorporation after MAR |
| `phase:PRE` | 68 | event | raw | Trial phase onset: Pre-intervention period - resting state baseline with eyes closed or fixed at a point |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-class music therapy phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 300 s *, overlap = 0.5 *, target_events = [`phase:PRE`, `phase:MTI`, `phase:POST`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `phase:PRE` | 0 | Pre-intervention baseline resting state (eyes closed or fixed) |
  | `phase:MTI` | 1 | Music therapy intervention - Music-Assisted Relaxation (MAR) |
  | `phase:POST` | 2 | Post-intervention recovery resting state |
- **Evidence**:
  - 10.1038/s41598-024-73211-3 — Three-class classification of EEG epochs into PRE (5 min eyes-closed resting baseline), MTI (~15 min Music-Assisted Relaxation), and POST (5 min resting recovery); spectral power analysis (delta, theta, alpha, beta) and HRV LF/HF ratio changes across phases
- **Notes**: tmax=300s (5 min) chosen for PRE/POST phases; MTI phase is longer (~15 min) but truncated to 300s for balanced epoching. overlap=0.5 (50%) per epoch_hint rationale for sustained resting/intervention states. segment_length=3s from SKILL default for clinical resting-state comparison. Values marked with * due to inferred=true in epoch_hint.

### Potential Task 1: 2-class pre/post music therapy classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, overlap = 0.5 *, target_events = [`phase:PRE`, `phase:POST`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `phase:PRE` | 0 | Pre-intervention baseline resting state (eyes closed or fixed) |
  | `phase:POST` | 1 | Post-intervention resting state during patient reincorporation after MAR |
- **Evidence**:
  - 10.1038/s41598-024-73211-3 — Binary variant of three-phase task collapsing to PRE vs POST for stronger contrast between baseline and intervention/recovery states; derived from same paper showing significant spectral differences between pre-intervention baseline and music therapy periods
- **Notes**: This 2-class variant excludes the MTI (music therapy intervention) phase to focus on comparing pure baseline (PRE) against post-intervention recovery state (POST). The epoch parameters use 3-second windows with 50% overlap, inferred from the candidate's epoch_hint indicating a long-event approach for sustained state classification. The shorter 3s windows are appropriate given both PRE and POST phases have matched durations (~5 min).

### Potential Task 2: 2-class intervention vs baseline classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, overlap = 0.5 *, target_events = [`phase:PRE`, `phase:MTI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `phase:PRE` | 0 | Pre-intervention baseline resting state (eyes closed or fixed) |
  | `phase:MTI` | 1 | Music therapy intervention - Music-Assisted Relaxation (MAR) |
- **Evidence**:
  - 10.1038/s41598-024-73211-3 — Binary classification of PRE (baseline resting) vs MTI (active music therapy intervention). Direct test of music therapy effect on brain state. Paper reports significant delta/theta power changes and EMG mean frequency decrease during MTI compared to PRE. Most clinically relevant contrast for evaluating MAR therapy efficacy.
- **Notes**: Long-event segmentation with 3s windows and 50% overlap used to extract stable spectral features from sustained 5-min PRE baseline and ~15-min MTI periods. tmax inferred from segment_length=3.0s in epoch_hint; overlap inferred as 0.5 (50%) for standard sliding window analysis of sustained phases. This is an archetype A task using trial phase onset markers as class labels for rest-vs-intervention brain state classification.

## Data Quality Notes

- Small sample size (N=9) severely limits statistical power and generalizability for all tasks, especially classification/regression tasks derived from info fields.
- Severe class imbalances expected for sex (8M:1F), burn_type (7 Termic:2 Electric), and burn_severity (7:2) classification tasks.
- Clinical ICU environment introduces substantial noise from medical equipment, patient motion, and electromagnetic interference; expect reduced signal quality compared to controlled lab recordings.
- Phase event counts are imbalanced across conditions (PRE=68, MTI=65, POST=42), with POST phase having notably fewer events.
- `device` field is completely missing from info metadata, limiting hardware reproducibility and channel location validation.
- Some info fields have inconsistent typing (e.g., VAS_PRE_session2 marked as categorical despite numeric values, A-HADS_last marked as categorical despite numeric values).
- Medication classification task has 5 categories for only 9 subjects, making reliable training extremely unlikely.
- No event markers present in raw EEG data; all phase events are derived from protocol timing metadata, introducing potential timing alignment uncertainties.
- ECG and EMG channels are present in the dataset but not explicitly utilized in any defined tasks; EEGUnity may need to handle multi-modal physiological data appropriately.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
