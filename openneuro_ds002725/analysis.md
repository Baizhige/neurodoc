# A dataset recording joint EEG-fMRI during affective music listening

**Dataset**: `openneuro_ds002725` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002725
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 105 | **Channels**: 47 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants listened to music stimuli designed to elicit emotional responses (approach/withdrawal behavior) and self-reported their felt affective states during simultaneous EEG-fMRI recording. The study investigated how EEG reflects subcortical brain activity related to emotional responses to music. Codes 1283/1285 are likely BrainVision fMRI sync codes; 34053 may be a BrainVision hardware code; 47/10/1 may be music condition/block markers.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `47` | 105 (files) | event | raw | Music block marker (likely condition or trial count) |
| `10` | 105 (files) | event | raw | Music onset marker (condition 10x) |
| `1` | 105 (files) | event | raw | Music onset marker (condition 1x) |
| `1283` | 105 (files) | admin | raw | BrainVision fMRI sync code - likely admin |
| `1285` | 105 (files) | admin | raw | BrainVision fMRI sync code - likely admin |
| `34053` | 105 (files) | admin | raw | Large BrainVision hardware code - admin |
| `265` | 94 (files) | event | raw | Music condition marker |
| `768` | 84 (files) | event | raw | Music condition marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Music Condition Classification (Synthetic vs Classical)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`265`, `768`] *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | 0 | Synthetic/generated music condition (40s trials) |
  | `768` | 1 | Classical music condition (2-3min trials) |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — "This paper presents the joint EEG-fMRI dataset (ds002725) where 21 participants listened to synthetic and classical music while reporting felt affective states via FEELTRACE"
- **Kernel Notes**: Event IDs 265 and 768 mapped to music conditions based on paper description of synthetic (generated) vs classical music trials. Verify mapping from events.tsv and dataset documentation. Epoch length 40s matches synthetic music trial duration; classical trials vary 2-3min.

### Classical Task 2: Affective State Classification (Valence/Arousal from FEELTRACE)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.5, target_events = [`synthetic_music`, `classical_music`] *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `synthetic_music` | continuous | FEELTRACE valence rating during synthetic music (0-1 scale) |
  | `classical_music` | continuous | FEELTRACE arousal rating during classical music (0-1 scale) |
- **Super Meta Notes**: Derived from raw events [`265`, `768`] by extracting continuous FEELTRACE self-report timestamps and interpolating to epoch-aligned labels. Kernel step: Load FEELTRACE csv files (if available in derivatives), map valence/arousal values to each epoch based on timestamps.
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — "continuous FEELTRACE valence/arousal labels for affective state" during music listening
- **Kernel Notes**: Requires FEELTRACE derivative files. If unavailable, kernel must extract continuous affective labels from participant ratings. Verify presence of behavioral data in dataset.

### Potential Task 1: Affective Music State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`47`, `10`, `1`, `265`, `768`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `47` | 0 | Music block/condition marker 47 |
  | `10` | 1 | Music block/condition marker 10 |
  | `1` | 2 | Music block/condition marker 1 |
  | `265` | 3 | Synthetic music condition |
  | `768` | 4 | Classical music condition |
- **Notes**: Codes 1283, 1285, 34053 are BrainVision system/fMRI sync markers - excluded. Decode exact music condition meaning from paper (subcortical approach/withdrawal). 47-channel EEG includes MRI-compatible electrodes. fMRI gradient artifact correction required.
- **Kernel Notes**: (replaces Potential Task 1 from original analysis.md) — Changed epoch method from epoch_by_event_hdf5 to epoch_by_long_event_hdf5 to match sustained music listening paradigm (40s-3min epochs).

## Data Quality Notes

- EEG recorded in MRI scanner; MRI gradient artifacts require dedicated removal pipeline.
- Codes 1283, 1285, 34053 are BrainVision system/fMRI codes - exclude from analysis.
- 47-channel EEG; verify channel positions and identify MRI-compatible electrode set.
- Decode music condition codes from Daly et al. / Sharman et al. paper.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review