# Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset

**Dataset**: `openneuro_ds005345` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005345
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 28 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

Participants engaged in naturalistic listening to excerpts of "Le Petit Prince" (The Little Prince) under single-talker and multi-talker conditions during simultaneous EEG and 7T fMRI recording. The study investigates neural processing of speech under cocktail-party-style listening conditions with attended and unattended talker manipulations. EEG was recorded with a 64-channel actiCAP system at 500 Hz while participants listened to extended narrative blocks lasting up to 10 minutes. Event markers indicate block onsets for single-talker (Stimulus/S 11) and four multi-talker variants (Stimulus/S 31-S 34) with different attention and talker gender configurations.

## File Scan Result

> **Kernel SHA256**: `f3e0d978cfe4a7ea00dde0136943c950c3ce25aa1e4e0842777d18365c3d9c21`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/actiCAP Data On` | 26 | admin | raw | EEG system initialization: actiCAP recording started |
| `Stimulus/S 11` | 20 | event | raw | Trial phase onset: run/block start |
| `Stimulus/S 31` | 6 | event | raw | Stimulus onset: experimental condition 1 |
| `Stimulus/S 32` | 6 | event | raw | Stimulus onset: experimental condition 2 |
| `Stimulus/S 33` | 6 | event | raw | Stimulus onset: experimental condition 3 |
| `Stimulus/S 34` | 6 | event | raw | Stimulus onset: experimental condition 4 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 5-class listening condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 600 s, overlap = 0.0, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 11` | 0 | single-talker (block onset) |
  | `Stimulus/S 31` | 1 | mix_f attended |
  | `Stimulus/S 32` | 2 | mix_m attended |
  | `Stimulus/S 33` | 3 | mix_f unattended |
  | `Stimulus/S 34` | 4 | mix_m unattended |
- **Evidence**:
  - 10.1101/2025.04.03.646958 — 5-class listening condition classification with epochs spanning -0.5s to 600s after block onset for sustained naturalistic listening states; classes include single-talker (S 11), mix_f attended (S 31), mix_m attended (S 32), mix_f unattended (S 33), mix_m unattended (S 34)
  - 10.1038/s41597-025-05158-7 — Validated multitalker EEG dataset with 25 participants, 64-channel EEG at 500 Hz; confirms long-event epoching for sustained listening conditions
- **Notes**: The 5 event IDs correspond to 5 distinct listening conditions in a cocktail party paradigm. S 11 marks single-talker blocks (20 occurrences), while S 31-34 mark four mixed-talker conditions with attended/unattended female/male talkers (6 occurrences each). The long epoch duration (600s) captures sustained naturalistic listening states rather than transient responses.

### Potential Task 1: 2-class attention load classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 600.0 s *, overlap = 0.0, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 11` | 0 | single-talker / attended (low attention load) |
  | `Stimulus/S 31` | 0 | attended multi-talker condition 1 (low attention load) |
  | `Stimulus/S 32` | 0 | attended multi-talker condition 2 (low attention load) |
  | `Stimulus/S 33` | 1 | unattended multi-talker condition 3 (high attention load) |
  | `Stimulus/S 34` | 1 | unattended multi-talker condition 4 (high attention load) |
- **Evidence**:
  - 10.1101/2025.04.03.646958 — Preprint describing LPP multi-talker dataset with cocktail-party listening paradigm and attention manipulation
  - 10.1038/s41597-025-05158-7 — Data descriptor for LPP multi-talker 7T fMRI and EEG dataset with single-talker, attended multi-talker, and unattended multi-talker conditions
- **Notes**: Derived from 5-class task by merging conditions along attended-vs-unattended dimension. y=0 combines single-talker (S 11) with attended multi-talker conditions (S 31, S 32); y=1 combines unattended multi-talker conditions (S 33, S 34). Epoch parameters inherited from 5-class variant with inferred long-event structure. Event meanings for S 31-S 34 are not explicitly documented in BIDS sidecars; mappings inferred from event frequency patterns and annotation directory structure (single_female, single_male, mix conditions). The 4 stimulus codes exceed 3 annotated conditions, suggesting one code may mark rest/silent baseline.

### Potential Task 2: 2-class single-talker vs multi-talker classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 600.0 s *, overlap = 0.0, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 11` | 0 | single-talker condition |
  | `Stimulus/S 31` | 1 | multi-talker condition |
  | `Stimulus/S 32` | 1 | multi-talker condition |
  | `Stimulus/S 33` | 1 | multi-talker condition |
  | `Stimulus/S 34` | 1 | multi-talker condition |
- **Evidence**:
  - 10.1101/2025.04.03.646958 — Derived from 5-class task by collapsing all multi-talker variants; y=0: single-talker (S 11), y=1: all multi-talker conditions (S 31-S 34)
  - 10.1038/s41597-025-05158-7 — Dataset descriptor for LPP Multi-talker naturalistic listening paradigm with single-talker and multi-talker conditions
- **Notes**: Collapses four distinct stimulus codes (S 31-S 34) into a single multi-talker class (y=1) versus single-talker (S 11, y=0). This tests the basic cocktail-party vs clear speech detection dimension. The long epochs (600s) reflect the block-structured naturalistic listening design where each stimulus event marks the onset of an extended narrative block. Event meanings for S 11 and S 31-S 34 are inferred from frequency patterns and annotation directory structure; the 4 stimulus codes exceed the 3 annotated conditions (single_female, single_male, mix), suggesting one code may mark a rest/silent baseline condition not represented in annotation files.

### Potential Task 3: Age Regression from Naturalistic EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–28.0 (years) | Continuous age values from participants.tsv; N=25-26 subjects with complete age data. Mean age 24.04 ± 2.28 years. |
- **Evidence**:
  - participants.tsv — Complete age data for all subjects (range 20-28 years, mean 24.04, SD 2.28)
  - README — "25 native Mandarin Chinese speakers (14 females, mean age = 24.04 ± 2.28 years)"
  - dataset_description.json — Confirms multitalker naturalistic listening paradigm with EEG recordings
- **Notes**: Segmentation-based epoching appropriate for continuous naturalistic listening data without trial structure. 6-second segments balance frequency resolution and approximate stationarity for regression on age-related EEG features. No event markers needed; continuous data segmented uniformly. Age is a native participants.tsv column requiring no kernel derivation.

### Potential Task 4: Sex Classification from Naturalistic EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — N=26 subjects with sex labels (F=15, M=11), complete coverage
  - dataset_description.json — "Le Petit Prince (LPP) Multi-talker: Naturalistic 7T fMRI and EEG Dataset"
  - README — 25 native Mandarin Chinese speakers (14 females) participated in EEG experiment listening to multitalker narratives
- **Notes**: Segmentation-based epoching with 6-second non-overlapping windows for subject-level sex prediction from continuous naturalistic listening EEG. Class balance is adequate for binary classification (F=15, M=11).

### Potential Task 5: Continuous Age Regression from Segmented Naturalistic EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–28.0 (years) | Per-subject continuous target; all segments from a subject share the same age value. Native participants.tsv column. |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Segmentation-based task with no event dependency — all continuous EEG data is sliced into non-overlapping 6-second segments. Age is drawn directly from participants.tsv (native info field, Meta Level = raw). The 6-second segment length is inferred from SKILL defaults for naturalistic continuous listening data; overlap is set to 0.0 for non-overlapping segments. This task is identical in label structure to a B3 age regression but explicitly framed as segmentation with empty event dependency.

## Data Quality Notes

- `device` field is missing across all files; equipment metadata must be inferred from `Comment/actiCAP Data On` event markers indicating actiCAP hardware.
- EEG and fMRI acquisition times (`eeg_acq_time` and `fmri_acq_time`) are separated by approximately 3 years (EEG: 2021, fMRI: 2024), indicating these are not simultaneous recordings but rather a longitudinal or separate acquisition design; users should verify cross-modal alignment assumptions.
- Event meanings for `Stimulus/S 31` through `Stimulus/S 34` are inferred from frequency patterns and annotation directory structure rather than explicit BIDS sidecar documentation; manual verification recommended before analysis.
- The 4 stimulus codes (S 31-S 34) exceed the 3 annotated conditions visible in directory structures (single_female, single_male, mix), suggesting one code may mark a rest/silent baseline condition not represented in annotation files.
- Long epoch duration of 600s may exceed actual block durations in some cases; users should verify tmax alignment with actual stimulus lengths if blocks are shorter than 10 minutes.
- Subject count discrepancy between README (25 participants) and participants.tsv (26 rows) should be reconciled; one subject may lack complete EEG data.
- `Manual Review` status is Pending; event ID mappings and condition labels require expert validation before pipeline execution.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
