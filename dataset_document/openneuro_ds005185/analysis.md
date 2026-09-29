# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2018-2020/2019/2024/2025 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 516 | **Channels**: 25 | **Sampling Rate**: 256/500 Hz | **Manual Review**: anonymous for review

## Paradigm

This dataset records home-based ear-EEG sleep monitoring from 20 healthy participants and is split into two parts. The official README states that data collection took place between 2018 and 2020 and that the first publication was in 2019. Part a contains 20 subjects with four nights each of simultaneous partial PSG, ear-EEG, and wrist-worn actigraphy in the home. Part b contains 10 of those subjects with an additional 12 nights using ear-EEG, actigraphy, and a single EOG electrode. PSG nights are sessions 1-4 and each PSG night has official scoring acquisition event files. The event structure also contains Danish diary/protocol annotations, synchronization and trigger markers, electrode-test/biocalibration annotations, and ASSR-related raw event codes.

## File Scan Result

> **Kernel SHA256**: `babb43ee6f8ce05ae72cbf3c197d37f6e1a36aed5e13e2c9c9ad39b2c1d766f4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Biocalibrations` | 79 | event | raw |  |
| `Biocalibrations start` | 11 | event | raw |  |
| `ElektrodeTest` | 1 | event | raw |  |
| `Gik i seng` | 80 | event | raw |  |
| `Højre prop ud/ind` | 1 | event | raw |  |
| `Højre prop ude i 5 min.` | 1 | event | raw |  |
| `Kort højre prop ude` | 1 | event | raw |  |
| `Lights Out` | 94 | event | raw |  |
| `Sov uroligt` | 1 | event | raw |  |
| `Stadig vågen` | 1 | event | raw |  |
| `Start af måling` | 75 | event | raw |  |
| `Stod op` | 70 | event | raw |  |
| `Stoppede måling` | 2 | event | raw |  |
| `Sync` | 77 | event | raw |  |
| `Tog propper ud` | 1 | event | raw |  |
| `Tog propperne ud` | 1 | event | raw |  |
| `Toietl` | 1 | event | raw |  |
| `Vågen` | 7 | event | raw |  |
| `Vågen i nat` | 1 | event | raw |  |
| `Vågen længe` | 1 | event | raw |  |
| `Vågen-gik i seng` | 1 | event | raw |  |
| `Vågen-stod op` | 1 | event | raw |  |
| `elektrodetest 2` | 1 | event | raw |  |
| `højre prop ude igen` | 2 | event | raw |  |
| `højre øreprop i igen` | 2 | event | raw |  |
| `højre øreprop ude` | 2 | event | raw |  |
| `i seng igen` | 2 | event | raw |  |
| `meget vågen i ca. 2 timer` | 1 | event | raw |  |
| `opvågning` | 1 | event | raw |  |
| `på toilet` | 2 | event | raw |  |
| `satte propperne i` | 2 | event | raw |  |
| `sluk mobita` | 1 | event | raw |  |
| `slukkede mobita` | 1 | event | raw |  |
| `tog propper ud` | 1 | event | raw |  |
| `tog propperne ud` | 1 | event | raw |  |
| `tog venstre prop ud` | 1 | event | raw |  |
| `vågen` | 6 | event | raw |  |
| `vågen i lidt tid` | 2 | event | raw |  |
| `vågnede` | 1 | event | raw |  |
| `Electrodetest` | 198 | event | raw |  |
| `Forsøg på at sove` | 1 | event | raw |  |
| `Got up` | 126 | event | raw |  |
| `Højre prop ud/ind` | 1 | event | raw |  |
| `Højre prop ude i 5 min.` | 1 | event | raw |  |
| `Kort højre prop ude` | 1 | event | raw |  |
| `Lights Out` | 199 | event | raw |  |
| `Løs elektrode` | 1 | event | raw |  |
| `Mega vågen` | 1 | event | raw |  |
| `Opvågnen` | 1 | event | raw |  |
| `Opvågning` | 1 | event | raw |  |
| `Sov uroligt` | 1 | event | raw |  |
| `Stadig vågen` | 1 | event | raw |  |
| `Start of recording` | 200 | event | raw |  |
| `Stod op for at slukke lys` | 1 | event | raw |  |
| `Stoppede måling` | 2 | event | raw |  |
| `Stoppede målingen` | 1 | event | raw |  |
| `Sync` | 197 | event | raw |  |
| `Tog propper ud` | 1 | event | raw |  |
| `Tog propperne ud` | 2 | event | raw |  |
| `Tog venstre prop ud` | 1 | event | raw |  |
| `Toietl` | 1 | event | raw |  |
| `Vågen` | 15 | event | raw |  |
| `Vågen i nat` | 1 | event | raw |  |
| `Vågen længe` | 1 | event | raw |  |
| `Vågen-gik i seng` | 1 | event | raw |  |
| `Vågen-stod op` | 1 | event | raw |  |
| `Went to bed` | 199 | event | raw |  |
| `elektrodetest 2` | 1 | event | raw |  |
| `event_1` | 25 | event | raw |  |
| `event_131071` | 8 | event | raw |  |
| `event_2` | 88 | event | raw |  |
| `event_3` | 16 | event | raw |  |
| `event_4` | 19 | event | raw |  |
| `event_5` | 51 | event | raw |  |
| `event_6` | 34 | event | raw |  |
| `event_7` | 20 | event | raw |  |
| `event_8` | 6 | event | raw |  |
| `event_9` | 2 | event | raw |  |
| `genereret af lyde` | 1 | event | raw |  |
| `højre prop ude igen` | 1 | event | raw |  |
| `højre øreprop i igen` | 1 | event | raw |  |
| `højre øreprop ude` | 1 | event | raw |  |
| `i seng igen` | 1 | event | raw |  |
| `meget vågen i ca. 2 timer` | 1 | event | raw |  |
| `opvågning` | 1 | event | raw |  |
| `på toilet` | 1 | event | raw |  |
| `rettede på prop` | 1 | event | raw |  |
| `rettede øreprop til` | 1 | event | raw |  |
| `scoring1_1-W` | 11408 | event | raw | Manual sleep scoring by scorer 1: Wake |
| `scoring1_2-REM` | 13675 | event | raw | Manual sleep scoring by scorer 1: REM sleep |
| `scoring1_3-N1` | 5510 | event | raw | Manual sleep scoring by scorer 1: N1 sleep |
| `scoring1_4-N2` | 32478 | event | raw | Manual sleep scoring by scorer 1: N2 sleep |
| `scoring1_5-N3` | 12836 | event | raw | Manual sleep scoring by scorer 1: N3 sleep |
| `scoring1_7-Artefact` | 2871 | event | raw | Manual sleep scoring by scorer 1: Artefact; exclude from sleep-stage targets |
| `scoring2_1-W` | 12464 | event | raw | Manual sleep scoring by scorer 2: Wake |
| `scoring2_2-REM` | 14263 | event | raw | Manual sleep scoring by scorer 2: REM sleep |
| `scoring2_3-N1` | 3713 | event | raw | Manual sleep scoring by scorer 2: N1 sleep |
| `scoring2_4-N2` | 31305 | event | raw | Manual sleep scoring by scorer 2: N2 sleep |
| `scoring2_5-N3` | 16167 | event | raw | Manual sleep scoring by scorer 2: N3 sleep |
| `scoring2_7-Artefact` | 886 | event | raw | Manual sleep scoring by scorer 2: Artefact; exclude from sleep-stage targets |
| `tog højre øreprop ud` | 1 | event | raw |  |
| `tog propper ud` | 1 | event | raw |  |
| `tog venstre prop ud` | 1 | event | raw |  |
| `trigger` | 30726 | event | raw |  |
| `vågen` | 8 | event | raw |  |
| `vågen i lidt tid` | 1 | event | raw |  |
| `vågnede uden prop` | 1 | event | raw |  |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Mapped from `participants.tsv` column `age`; age in 2019, range 22-36 years. |
| `sex` | complete | Mapped from `participants.tsv` column `sex`; values `f` = 13, `m` = 7. |
| `device` | complete | README identifies the EEG recorder as TMSi Mobita; amplifier/cap details are also captured in scan-derived fields. |
| `acq` | partial (356/516) | e.g. PSG, earEEG |
| `amplifier` | complete | e.g. TMSi Mobita |
| `cap` | complete | e.g. custom ear-EEG earpieces, custom ear-EEG earpieces with partial PSG electrodes, custom self-applied ear-EEG earpieces with single EOG electrode |
| `dataset` | complete | e.g. openneuro_ds005185 |
| `eeg_channel_count` | complete | e.g. 20, 22, 18 |
| `eeg_reference` | complete | e.g. average, common |
| `emg_channel_count` | complete | e.g. 0, 3 |
| `eog_channel_count` | complete | e.g. 0, 2, 1 |
| `misc_channel_count` | complete | e.g. 0 |
| `power_line_frequency_hz` | complete | e.g. 50 |
| `recording_type` | complete | e.g. EEG |
| `sampling_rate_hz` | complete | e.g. 256.0, 500.0 |
| `session` | complete | e.g. ses-001, ses-002, ses-003 |
| `sleep_diary_available` | complete | e.g. False, True |
| `sleep_scoring1_available` | complete | e.g. False, True |
| `sleep_scoring2_available` | complete | e.g. False, True |
| `sleep_stage_event_format` | complete | e.g. scoring<scorer>_<code>-<stage> |
| `source_file` | complete | e.g. edf_used_to_score1.edf, edf_used_to_score2.edf, sub-001_ses-001_task-ASSR_acq-PSG_eeg.set |
| `subject_id` | complete | e.g. sub-001, sub-002, sub-003 |
| `task` | partial (356/516) | e.g. ASSR, sleep, electrodeTestLab |
| `task_description` | partial (156/516) | e.g. Auditory Steady State Response: 40 Hz amplitude modulated noise, with accompanying trigger signal, was played to the subject. By focusing on the 40 Hz SNR in the recorded data, an objective signal quality could be determined., Subject watched a short video clip with various instructions (jaw clenching, eyes open/closed, eyes moving left & right), to be able to compare those results to the ASSR results. |


## Tasks

### Classical Task 1: Scorer 1 5-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`scoring1_1-W`, `scoring1_2-REM`, `scoring1_3-N1`, `scoring1_4-N2`, `scoring1_5-N3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `scoring1_1-W` | 0 | Wake, scorer 1 |
  | `scoring1_3-N1` | 1 | N1 sleep, scorer 1 |
  | `scoring1_4-N2` | 2 | N2 sleep, scorer 1 |
  | `scoring1_5-N3` | 3 | N3 sleep, scorer 1 |
  | `scoring1_2-REM` | 4 | REM sleep, scorer 1 |
- **Evidence**:
  - OpenNeuro ds005185 README — PSG nights are sessions 1-4 and each PSG night has an additional scoring acquisition event file.
  - OpenNeuro `task-sleep_events.json` — `Scoring1` defines manual sleep scoring by scorer 1 with Wake, REM, N1, N2, N3, Artefact, and Unscored levels.
  - Full official S3 audit — 80 scorer-1 scoring files; all scoring rows have `duration = 30`.
  - 10.1038/s41597-025-04579-8 — Data descriptor states EESM19 manual scorings are included as `.tsv` event files and PSG recordings were scored twice by different technicians.
  - 10.1038/s41598-019-53115-3 — First EESM19 publication supports whole-night ear-EEG sleep-stage analysis.
- **Notes**: `scoring1_7-Artefact` is excluded from target events. Scorer 1 is kept separate from scorer 2; no scorer merging or adjudication is assumed.

### Classical Task 2: Scorer 2 5-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`scoring2_1-W`, `scoring2_2-REM`, `scoring2_3-N1`, `scoring2_4-N2`, `scoring2_5-N3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `scoring2_1-W` | 0 | Wake, scorer 2 |
  | `scoring2_3-N1` | 1 | N1 sleep, scorer 2 |
  | `scoring2_4-N2` | 2 | N2 sleep, scorer 2 |
  | `scoring2_5-N3` | 3 | N3 sleep, scorer 2 |
  | `scoring2_2-REM` | 4 | REM sleep, scorer 2 |
- **Evidence**:
  - OpenNeuro ds005185 README — PSG nights are sessions 1-4 and each PSG night has an additional scoring acquisition event file.
  - OpenNeuro `task-sleep_events.json` — `Scoring2` defines manual sleep scoring by scorer 2 with Wake, REM, N1, N2, N3, Artefact, and Unscored levels.
  - Full official S3 audit — 80 scorer-2 scoring files; all scoring rows have `duration = 30`.
  - 10.1038/s41597-025-04579-8 — Data descriptor states EESM19 PSG recordings were manually scored twice and scorings are included as `.tsv` event files.
  - 10.1038/s41598-019-53115-3 — First EESM19 publication supports whole-night ear-EEG sleep-stage analysis.
- **Notes**: `scoring2_7-Artefact` is excluded from target events. Scorer 2 is kept separate from scorer 1; no scorer merging or adjudication is assumed.

### Potential Task 1: Age regression from sleep EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping; numeric age in years, range 22-36 |
- **Evidence**:
  - OpenNeuro ds005185 `participants.tsv` and `participants.json` — age is available for all 20 participants and is defined as age in 2019.
- **Notes**: Subject-level metadata task, not a core published sleep-staging benchmark. Segmenting EEG does not increase the number of independent subject-level age labels.

### Potential Task 2: Sex classification from sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | f -> 0; m -> 1 |
- **Evidence**:
  - OpenNeuro ds005185 `participants.tsv` and `participants.json` — sex is complete for all 20 participants; distribution is 13 f / 7 m.
- **Notes**: Subject-level metadata task, not a core published sleep-staging benchmark.

## Data Quality Notes

- Sleep stage labels (W/N1/N2/N3/REM) are not present in raw EEG event markers and must be extracted from PSG annotation sidecar files.
- Danish-language event annotations dominate the event structure, which may require translation for broader usability; multiple spelling variants exist (e.g., `Vågen` vs `vågen`, `Tog propper ud` vs `tog propper ud`).
- ASSR task events (event_4 through event_9) appear in the scan with low counts but their provenance cannot be verified from events.tsv files, creating uncertainty for task construction.
- The extremely high count of `trigger` events (30,726) relative to all other events suggests dense synchronization pulses that may need downsampling or exclusion during epoching.
- Multiple event ID systems are in use: string descriptions with Danish text, numeric event codes (event_1 through event_131071), and a generic `trigger` marker, which may complicate event parsing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
