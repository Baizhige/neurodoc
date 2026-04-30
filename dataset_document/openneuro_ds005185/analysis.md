# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 516 | **Channels**: 25 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Naturalistic multi-night sleep monitoring using ear-EEG and polysomnography (PSG) in a home environment collected in 2019. Participants self-applied in-ear EEG electrodes over multiple nights for sleep staging and feasibility assessment. Event markers include Danish-language protocol annotations (lights out, going to bed, waking up), synchronization pulses, biocalibration periods, and ASSR stimulus conditions. The dominant event is `trigger` (30,726 total), a system trigger marker used for synchronization between recording systems.

## File Scan Result

> **Kernel SHA256**: `72bd902f86d674ca5c847830f226a8c52a7e171d239fee0b661644595134676b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| ` Biocalibrations ` | 79 | event | raw |  |
| ` Biocalibrations start ` | 11 | event | raw |  |
| ` ElektrodeTest ` | 1 | event | raw |  |
| ` Gik i seng ` | 80 | event | raw |  |
| ` Højre prop ud/ind ` | 1 | event | raw |  |
| ` Højre prop ude i 5 min. ` | 1 | event | raw |  |
| ` Kort højre prop ude ` | 1 | event | raw |  |
| ` Lights Out ` | 94 | event | raw |  |
| ` Sov uroligt ` | 1 | event | raw |  |
| ` Stadig vågen ` | 1 | event | raw |  |
| ` Start af måling ` | 75 | event | raw |  |
| ` Stod op ` | 70 | event | raw |  |
| ` Stoppede måling ` | 2 | event | raw |  |
| ` Sync ` | 77 | event | raw |  |
| ` Tog propper ud ` | 1 | event | raw |  |
| ` Tog propperne ud ` | 1 | event | raw |  |
| ` Toietl ` | 1 | event | raw |  |
| ` Vågen ` | 7 | event | raw |  |
| ` Vågen i nat ` | 1 | event | raw |  |
| ` Vågen længe ` | 1 | event | raw |  |
| ` Vågen-gik i seng ` | 1 | event | raw |  |
| ` Vågen-stod op ` | 1 | event | raw |  |
| ` elektrodetest 2 ` | 1 | event | raw |  |
| ` højre prop ude igen ` | 2 | event | raw |  |
| ` højre øreprop i igen ` | 2 | event | raw |  |
| ` højre øreprop ude ` | 2 | event | raw |  |
| ` i seng igen ` | 2 | event | raw |  |
| ` meget vågen i ca. 2 timer ` | 1 | event | raw |  |
| ` opvågning ` | 1 | event | raw |  |
| ` på toilet ` | 2 | event | raw |  |
| ` satte propperne i ` | 2 | event | raw |  |
| ` sluk mobita ` | 1 | event | raw |  |
| ` slukkede mobita ` | 1 | event | raw |  |
| ` tog propper ud ` | 1 | event | raw |  |
| ` tog propperne ud ` | 1 | event | raw |  |
| ` tog venstre prop ud ` | 1 | event | raw |  |
| ` vågen ` | 6 | event | raw |  |
| ` vågen i lidt tid ` | 2 | event | raw |  |
| ` vågnede ` | 1 | event | raw |  |
| `event_1` | 25 | event | raw | Trial phase onset: Biocalibrations start |
| `event_131071` | 8 | admin | raw | System trigger sync marker |
| `event_2` | 88 | event | raw | Trial phase onset: Biocalibrations |
| `event_3` | 16 | event | raw | Trial phase onset: ElektrodeTest |
| `event_4` | 19 | event | raw | Trial phase onset: ASSR stimulus condition 1 |
| `event_5` | 51 | event | raw | Trial phase onset: ASSR stimulus condition 2 |
| `event_6` | 34 | event | raw | Trial phase onset: ASSR stimulus condition 3 |
| `event_7` | 20 | event | raw | Trial phase onset: ASSR stimulus condition 4 |
| `event_8` | 6 | event | raw | Trial phase onset: ASSR stimulus condition 5 |
| `event_9` | 2 | event | raw | Trial phase onset: ASSR stimulus condition 6 |
| `trigger` | 30726 | admin | raw | System trigger marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from Sleep EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 22.0–36.0 (years) | Continuous chronological age from participants.tsv; N=20 subjects with mean ~26 years. Each 30-second segment inherits the subject's age as regression target. |
- **Evidence**:
- **Notes**: Segmentation-based regression task using standard 30-second sleep epoch length. No event structure required since target (age) is subject-level continuous variable. Independent segments (0 overlap) treated as samples for age prediction model.

### Potential Task 2: Sex Classification from Sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | f | 0 | female |
  | sex | m | 1 | male |
- **Evidence**:
  - participants.tsv — 20 subjects with complete sex labels (13 female, 7 male); confirmed f/m encoding
- **Notes**: 30-second segments match standard sleep epoch length used in clinical sleep staging. Sex is a subject-level constant label broadcast to all segments from the same subject. Classification is binary with y ∈ {0, 1}.

### Potential Task 3: continuous sleep monitoring segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 22.0–36.0 (years) | Subject chronological age from participants.tsv; predicted from 30-s unannotated ear-EEG segments |
- **Evidence**:
  - participants.tsv — age column complete for all 20 subjects (range 22–36 years)
  - README — describes 16-night subjects (sessions 1–4 with PSG, sessions 5–16 ear-EEG only without scoring), enabling continuous monitoring without stage labels
  - task-sleep_acq-diary_events.json — confirms sleep acquisition diary structure; nights without scoring events lack hypnogram labels
- **Notes**: Archetype C (segmentation + info-native). The 30-second segment length with 50% overlap is standard for wearable EEG analysis and sleep monitoring applications. This task leverages the subset of 16-night subjects where most nights (sessions 5–16) have no PSG scoring, making them suitable for continuous unannotated segmentation. Age prediction from raw EEG segments demonstrates biological state inference without full PSG montage or manual sleep staging.

### Potential Task 4: ASSR stimulus condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s *, tmax = 5 s *, target_events = [`event_4`, `event_5`, `event_6`, `event_7`, `event_8`, `event_9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_4 | 0 | ASSR stimulus condition 1 |
  | event_5 | 1 | ASSR stimulus condition 2 |
  | event_6 | 2 | ASSR stimulus condition 3 |
  | event_7 | 3 | ASSR stimulus condition 4 |
  | event_8 | 4 | ASSR stimulus condition 5 |
  | event_9 | 5 | ASSR stimulus condition 6 |
- **Evidence**:
  - eeg.json — TaskName="ASSR", TaskDescription describes 40 Hz amplitude modulated noise with trigger signal for objective signal quality determination
  - Event meanings (locked) — event_4 through event_9 map to ASSR stimulus conditions 1-6 respectively, scoped to task-ASSR
- **Notes**: Potential task: no actual events.tsv files were found for ASSR tasks after exhaustive search, making this candidate uncertain despite the clear event meaning mappings. The event counts for event_4 (19), event_5 (51), event_6 (34), event_7 (20), event_8 (6), and event_9 (2) suggest these events do appear in the data, but their provenance cannot be verified from TSV files. Epoch timing inferred from ASSR paradigm requirements (6-second window to capture 40 Hz response stabilization).

## Data Quality Notes

- Sleep stage labels (W/N1/N2/N3/REM) are not present in raw EEG event markers and must be extracted from PSG annotation sidecar files; these were available in the original dataset but are not reflected in the current event structure scan.
- The `device` info field is completely missing across all files, limiting hardware-specific analyses.
- Danish-language event annotations dominate the event structure, which may require translation for broader usability; multiple spelling variants exist (e.g., `Vågen` vs `vågen`, `Tog propper ud` vs `tog propper ud`).
- ASSR task events (event_4 through event_9) appear in the scan with low counts but their provenance cannot be verified from events.tsv files, creating uncertainty for task construction.
- The extremely high count of `trigger` events (30,726) relative to all other events suggests dense synchronization pulses that may need downsampling or exclusion during epoching.
- Multiple event ID systems are in use: string descriptions with Danish text, numeric event codes (event_1 through event_131071), and a generic `trigger` marker, which may complicate event parsing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
