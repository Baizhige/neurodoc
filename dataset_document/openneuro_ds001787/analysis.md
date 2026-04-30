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

### Classical Task 1: Meditator Expertise Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | group | expert | 0 | Expert meditator (≥10 years daily practice) |
  | group | novice | 1 | Novice meditator |
- **Evidence**:
  - https://openneuro.org/datasets/ds001787 — 24 subjects with binary group labels: 12 expert meditators and 12 novices
  - doi:10.18112/openneuro.ds001787.v1.1.1 — Continuous meditation EEG with group column in participants.tsv providing complete native labels
- **Notes**: Segmentation-based epoching captures sustained meditation state without event anchoring. The 10-second windows with no overlap are standard for continuous state analysis in meditation EEG studies.

### Classical Task 2: Age Regression from Meditation EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 29.0–78.0 (years) | 23 of 24 subjects have age values; one missing |
- **Evidence**:
  - https://openneuro.org/datasets/ds001787 — OpenNeuro dataset page for EEG meditation study with 24 subjects
  - doi:10.18112/openneuro.ds001787.v1.1.1 — Dataset DOI; participants.tsv contains age column with values 29.0–78.0 years
  - README — Describes continuous meditation recording with ~2-minute interruptions for self-report; original 2048 Hz downsampled to 256 Hz
  - eeg.json — Confirms continuous recording at 256 Hz with 64 EEG channels
- **Notes**: Native participants.tsv column 'age' used directly; no derivation required. Segmentation into 10-second windows with no overlap for continuous meditation state prediction. Age is a per-subject scalar applied to all segments from that subject.

### Potential Task 1: Gender Classification from Meditation EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | Male |
  | gender | F | 1 | Female |
- **Evidence**:
  - participants.tsv — N=24 subjects with complete gender labels: 12 male (M) and 12 female (F), balanced classes
- **Notes**: Segmentation-based approach for continuous meditation recordings. 10-second non-overlapping windows are used to create epochs from the continuous EEG, with gender label drawn from the native participants.tsv column. Binary classification task with balanced classes.

### Potential Task 2: GSR amplitude regression from meditation EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `GSR1`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | GSR1 | continuous (μS) | Galvanic skin response amplitude from BioSemi ActiveTwo misc channel; native continuous signal for regression against EEG features |
- **Evidence**:
  - 10.3389/fnins.2022.765585 — Reference paper explicitly analyzes ISA-GSR coupling during meditation; GSR1 and GSR2 are continuous native misc channels on the raw object (BioSemi ActiveTwo with 15 misc channels)
- **Notes**: B1 archetype (native misc channel regression). GSR1 selected as primary GSR channel; GSR2 also available as redundant backup. Segment length of 10s inferred from paper's analysis of sustained meditation states (first 30s period after meditation onset), with non-overlapping windows for independent samples.

### Potential Task 3: Respiration-EEG Coupling Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `Resp`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | Resp | respiration amplitude (arbitrary units, BioSemi ActiveTwo) | Continuous respiration signal; native misc channel recorded during meditation |
- **Evidence**:
- **Notes**: Native misc channel "Resp" is present in the BioSemi ActiveTwo channel set (confirmed in eeg.json: MiscChannelCount=15, and Resp appears in native misc channel catalog). The task uses 10-second non-overlapping windows to capture multiple respiratory cycles at typical resting rates (~12-20 breaths/min ≈ 3-5 s/cycle). The regression target is the continuous respiration signal amplitude, enabling investigation of EEG-respiration coupling during meditation practice.

### Potential Task 4: Temperature-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `Temp`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | Temp | Temperature (°C or arbitrary units) | Continuous temperature recording from BioSemi ActiveTwo setup; slow-varying physiological signal |
- **Evidence**:
  - `eeg.json` — BioSemi ActiveTwo recording with MiscChannelCount=15, confirming auxiliary channels including Temp
  - `README` — Meditation study with continuous recording; temperature as autonomic correlate of meditative state
- **Notes**: Native misc channel `Temp` is a continuous non-EEG signal already present in the raw BDF files. No kernel derivation needed; the regression target is read directly from the `Temp` channel. The 10-second segmentation window is chosen because temperature changes slowly relative to EEG dynamics, providing sufficient samples per epoch for stable regression targets.

### Potential Task 5: Plethysmography-EEG Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `Plet`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|-------------|-------|
  | Plet | blood volume pulse (a.u.) | Continuous plethysmography signal; target is the mean or sample-wise amplitude within each 10-second EEG segment. Cardiac pulsation ~1-2 Hz yields ~10-20 beats per window. |
- **Evidence**:
  - [eeg.json, README] — Dataset includes native MISC channel `Plet` (plethysmography) among 15 misc channels; continuous recording during meditation task with ~2-minute interruption intervals for self-report.
- **Notes**: Archetype B1: native misc channel `Plet` is directly available on the raw data as a continuous peripheral physiological recording. No kernel derivation needed. The 10-second segmentation windows are chosen to capture multiple cardiac cycles for stable cardiovascular-EEG coupling estimation.

### Potential Task 6: Expert-Novice Age-Matched Stratification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | group | expert | 0 | Meditation expert |
  | group | novice | 1 | Meditation novice |
- **Evidence**:
  - (none — potential task)
- **Notes**: Archetype C with native info field `group` (expert/novice) as classification target. Age range 29-78 years spans both groups and may confound expertise-related EEG differences; kernel should stratify by age or residualize age effects during model training. Standard 10s non-overlapping segmentation applied to continuous meditation recordings with ~2-minute interruption intervals. No event-based epoching used.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
