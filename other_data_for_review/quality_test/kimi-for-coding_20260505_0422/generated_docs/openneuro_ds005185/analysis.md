# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 145 | **Channels**: 14 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

This dataset contains continuous overnight sleep recordings from 20 healthy subjects (13 female, 7 male, ages 22–36) using an ear-EEG device (cEEGrid electrodes around the ear) for unobtrusive sleep monitoring. Each subject completed 4–16 recording sessions, yielding continuous sleep EEG data collected in naturalistic home settings. Subjects maintained sleep diaries with event annotations in Danish (e.g., "Gik i seng"/went to bed, "Lights Out", "Stod op"/got up, "Vågen"/awake), and the recordings include standard biocalibration procedures and electrode tests.

## File Scan Result

> **Kernel SHA256**: `43879847c78dc11bf3559f2e9e0f029fdf96fe985ccc5718ab6782d8e382542e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
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
| `event_1` | 25 | admin | raw | System trigger code 1 (equipment-specific marker) |
| `event_131071` | 8 | admin | raw | System trigger code 131071 (equipment-specific marker) |
| `event_2` | 88 | admin | raw | System trigger code 2 (equipment-specific marker) |
| `event_3` | 16 | admin | raw | System trigger code 3 (equipment-specific marker) |
| `event_4` | 19 | admin | raw | System trigger code 4 (equipment-specific marker) |
| `event_5` | 51 | admin | raw | System trigger code 5 (equipment-specific marker) |
| `event_6` | 34 | admin | raw | System trigger code 6 (equipment-specific marker) |
| `event_7` | 20 | admin | raw | System trigger code 7 (equipment-specific marker) |
| `event_8` | 6 | admin | raw | System trigger code 8 (equipment-specific marker) |
| `event_9` | 2 | admin | raw | System trigger code 9 (equipment-specific marker) |
| `trigger` | 30726 | admin | raw | System trigger marker (generic equipment trigger) |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `written_time` | native (raw misc in EEG file) | raw | Present in diary events as 'writtenTime' column. Contains subject-reported clock times (e.g., 23.05, 23.07, 23.10) corresponding to events like Start of recording, Sync, Electrodetest, Went to bed, Lights Out, Got up. Described as 'The time as written in the diary'. Not a continuous channel but event-level metadata. |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Available in participants.tsv. Sample values: 23, 23, 24, 25, 24, 26, 25 (all female in sample). |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing | Available in participants.tsv. Sample shows all 'f' (female). |

## Tasks

### Potential Task 1: Age Regression from Sleep EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (22–36); each 30 s segment inherits the subject's age as regression target. |
- **Evidence**:
  - participants.tsv — Age values confirmed complete for all 20 subjects (range 22–36 years, sample: 23, 24, 25).
  - dataset_description.json — "Ear-EEG Sleep Monitoring 2019 (EESM19)" with 20 subjects, 4–16 sessions each of continuous sleep recording.
  - task-sleep_events.json — Defines 30-second epoch structure for sleep scoring, confirming standard sleep epoch length.
- **Notes**: Standard 30-second segmentation with 50% overlap is the canonical approach for sleep EEG analysis (matching PSG epoch conventions). Since age is a subject-level variable from participants.tsv and no trial-level structure exists for age prediction, segmentation with subject-level label propagation is the appropriate design. No kernel derivation needed—age is a native info field.

### Potential Task 2: Sex Classification from Sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | sex | 0 = f (female, N=13), 1 = m (male, N=7); binary classification from participants.tsv |
- **Evidence**:
- **Notes**: Subject-level sex label applied uniformly to all 30-second segments from each recording. Segmentation enables treating continuous sleep EEG as multiple samples per subject. Class imbalance is 65% female / 35% male.



## Data Quality Notes

- Event annotations are in Danish with inconsistent casing and spelling variants (e.g., "Vågen" vs "vågen", "Tog propper ud" vs "tog propper ud" vs "tog propperne ud"), which may complicate automated event parsing.
- Large number of generic `trigger` events (30,726) with unspecified meaning alongside numbered system trigger codes (event_1 through event_131071); the relationship between these admin triggers and diary events is undocumented.
- Sleep diary events are sparse, subjective, and irregularly distributed across recordings—many recordings have only a handful of diary annotations while others have dozens.
- `age` and `sex` info fields are marked missing in the scan despite being available in participants.tsv, indicating incomplete metadata extraction into the EEG file headers.
- No standard sleep stage scoring labels (e.g., Wake/N1/N2/N3/REM) are present in the event structure, limiting direct sleep stage classification tasks.
- Channel count of 14 is relatively low for sleep monitoring and reflects the ear-EEG montage limitation; spatial coverage is restricted compared to full PSG.
- One event contains apparent typo "Toietl" instead of "Toilet".

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
