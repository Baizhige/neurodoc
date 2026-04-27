# EEG/ECG/EMG During Music Therapy in ICU Burn Patients

**Dataset**: `openneuro_ds004840` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004840
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 68 | **Channels**: 10 | **Sampling Rate**: 1024 Hz
**Manual Review**:

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

### Potential Task 3: Age Regression from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–65.0 (years) | Complete for all 9 subjects; burn patients in ICU music therapy study |
- **Evidence**:
- **Notes**: Segmentation-based regression task using 4-second non-overlapping/overlapping EEG segments to predict subject age from spectral or connectivity features. Age range 18-65 years spans adult lifespan, though N=9 limits generalizability. No event anchors needed due to segmentation approach; all continuous EEG data across pre/post music therapy and intervention phases are used.

### Potential Task 4: Burn Severity Regression from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `burn_severity`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | burn_severity | 1–2 (ordinal) | Burn severity score: 1=Termic, 2=Electric; complete for all 9 subjects. Limited range (N=9, only 2 unique values) but treated as regression target. |
- **Evidence**:
- **Notes**: Segmentation-based regression task using 4-second non-overlapping/overlapping windows across continuous EEG recordings. The burn_severity field is a native participants.tsv column (B3 archetype, Meta Level=raw). Despite only two distinct values in this small cohort, the task is framed as regression to explore whether EEG patterns during music therapy sessions correlate with injury severity. The limited dynamic range (1–2) and small sample size (N=9) make this an exploratory potential task rather than a robust benchmark. Segment length and overlap inferred from clinical segmentation SKILL defaults.

### Potential Task 5: Burn Severity Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `burn_severity`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | burn_severity | 1 | 0 | Mild burn severity (TBSA < 20%) |
  | burn_severity | 2 | 1 | Severe burn severity (TBSA ≥ 20%) |
- **Evidence**:
  - participants.tsv — burn_severity column with values {1, 2} for all 9 subjects; confirmed complete with no missing data
  - dataset_description.json — describes study of adult burn patients in ICU with electrophysiological measures
  - README — confirms 9 participants in intervention group subset with EEG recordings during music therapy sessions
- **Notes**: Binary classification of burn severity from resting-state and music-therapy EEG segments. The burn_severity values 1 and 2 are mapped to y=0 and y=1 respectively for 0-based sequential integer labels. Small sample size (N=9) with likely class imbalance given 7 subjects with severity=1 and 2 subjects with severity=2 in available data. Segmentation-based epoching treats all continuous EEG equally regardless of task phase, making this a disorder classification task from overall brain activity patterns.

### Potential Task 6: Sex Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | Male |
  | sex | F | 1 | Female |
- **Evidence**:
  - participants.tsv — sex field complete for all 9 subjects (8 M, 1 F)
- **Notes**: Severe class imbalance (8:1) with only 1 female subject; task is technically possible but likely unreliable for generalization. Included for completeness as sex is a complete categorical field in participants.tsv. All subjects are adult burn patients in ICU during music therapy sessions.

### Potential Task 7: Medication Type Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `medication`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | medication | Oxycodone | 0 | Patient taking Oxycodone |
  | medication | Hydrocodone | 1 | Patient taking Hydrocodone |
  | medication | Hydromorphone | 2 | Patient taking Hydromorphone |
  | medication | Acetaminophen | 3 | Patient taking Acetaminophen |
  | medication | - | 4 | No medication / control |
- **Evidence**:
  - participants.tsv — medication column contains 5 distinct categories: Oxycodone, Hydrocodone, Hydromorphone, Acetaminophen, and - (none)
- **Notes**: Highly exploratory task with small sample (N=9) and 5 medication categories. The `-` value in participants.tsv indicates no medication (control). Classification tests whether psychoactive medication effects are detectable in resting-state EEG during music therapy. Segmentation approach used since no event-level medication labels exist; medication is a per-subject info field applied uniformly to all segments from that subject.

### Potential Task 8: Burn Type Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `burn_type`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | burn_type | Termic | 0 | Thermal burn injury |
  | burn_type | Electric | 1 | Electrical burn injury |
- **Evidence**:
  - participants.tsv — `burn_type` column contains categorical labels (Termic, Electric) with complete coverage across all 9 subjects
  - README §1.1 — Dataset involves adult burn patients in ICU with electrophysiological measures; burn_type distinguishes thermal vs electrical injury mechanisms
- **Notes**: Binary classification of burn injury mechanism from segmented EEG. Uses 4-second non-overlapping segments with 50% overlap as SKILL default for clinical segmentation. The info field `burn_type` is a native participants.tsv column (archetype B3), so Meta Level = raw. Class imbalance expected (7 Termic vs 2 Electric subjects) but task tests whether neural signatures during music therapy/resting states differ by injury type.

### Potential Task 9: Segmented Resting-State with Age Labels
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–65.0 (years) | Subject chronological age from participants.tsv; continuous EEG segments across all phases (PRE, MTI, POST) used for age-related neural pattern regression |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Segmentation-based epoching with no event discrimination; all continuous EEG data from PRE, MTI, and POST phases are concatenated and segmented into 4-second windows with 50% overlap. Age is a native participants.tsv column requiring no kernel derivation. The regression target is subject age, testing whether spectral or connectivity features of resting-state EEG predict chronological age in a clinical ICU burn population.

### Potential Task 10: Segmented Resting-State with HADS Baseline Anxiety Labels
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `A-HADS_baseline`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | A-HADS_baseline | 0–11 (score) | Hospital Anxiety and Depression Scale (HADS) anxiety subscale measured at baseline; continuous EEG segments from all available task periods (PRE, MTI, POST) are segmented and associated with this subject-level score |
- **Evidence**:
  - (none — potential task)
- **Notes**: Archetype C with info-native label. Pure segmentation of all continuous EEG data across the three task phases (preMusicTherapy, musicTherapy, postMusicTherapy) into 4-second non-overlapping windows with 50% overlap. The A-HADS_baseline score is a subject-level clinical measure obtained before any intervention, testing whether pre-existing anxiety levels are encoded in resting/task EEG patterns. No event markers are used for epoching; all data contributes. Values marked with * indicate SKILL defaults inferred from resting-state clinical segmentation conventions.

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
