# EEG: Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms

**Dataset**: `openneuro_ds003638` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003638
**Category**: High-level Mental | **Subjects**: 57 | **Files (Completed)**: 57
**Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

This study employs three cross-species behavioral paradigms (5-Choice Continuous Performance Task [5CCPT], Probabilistic Reward/Punishment task [PRBP], and Pavlovian-to-Instrumental Transfer [PST]) to identify electrophysiological biomarkers associated with various behavioral dimensions including attention, impulsivity, and reward sensitivity. All 57 subjects completed all three paradigms in a single session. Stimulus events are encoded as numeric trigger codes (65281-65287 range) with behavioral responses marked by dedicated event codes.

## File Scan Result

> **Kernel SHA256**: `e2c2e371d51eb263216d014c69af0620a485e5e2670b66f0567a375a1d6d2c74`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_130816` | 166 | event | raw | Task initialization/sync event |
| `event_131070` | 170 | event | raw | Task initialization/sync event |
| `event_131071` | 1 | event | raw | Session start marker |
| `event_65281` | 1476 | event | raw | 5CCPT stimulus code 1 (circle) |
| `event_65282` | 1475 | event | raw | 5CCPT stimulus code 2 (cross) |
| `event_65283` | 1476 | event | raw | 5CCPT stimulus code 3 (diamond) |
| `event_65284` | 1475 | event | raw | 5CCPT stimulus code 4 (square) |
| `event_65285` | 1476 | event | raw | 5CCPT stimulus code 5 (triangle) |
| `event_65286` | 1476 | event | raw | 5CCPT stimulus code 6 (star) |
| `event_65287` | 2911 | event | raw | 5CCPT stimulus code 7 (target/hit) |
| `event_65291` | 1355 | event | raw | PRBP feedback code (probabilistic outcome) |
| `event_65292` | 1254 | event | raw | PRBP feedback code (probabilistic outcome) |
| `event_65293` | 1371 | event | raw | PRBP feedback code (high/low reward) |
| `event_65294` | 1325 | event | raw | PRBP feedback code (high/low punishment) |
| `event_65295` | 1338 | event | raw | PRBP feedback code (feedback valence) |
| `event_65301` | 2006 | event | raw | Response code 1 (5CCPT response) |
| `event_65302` | 4427 | event | raw | Response code 2 (5CCPT response) |
| `event_65303` | 2859 | event | raw | Response code 3 (5CCPT response) |
| `event_65305` | 2126 | event | raw | Response code 5 (5CCPT response) |
| `event_65310` | 1412 | event | raw | Response code 10 (5CCPT response) |
| `event_65311` | 8199 | event | raw | Response code 11 (5CCPT response/hit) |
| `event_65312` | 4865 | event | raw | Response code 12 (5CCPT response) |
| `event_65313` | 38 | event | raw | Response code 13 (5CCPT response) |
| `event_65316` | 12 | event | raw | PST cue code (rare event) |
| `event_65319` | 3323 | event | raw | PRBP/PST event code |
| `event_65320` | 3936 | event | raw | PRBP/PST event code |
| `event_65321` | 90 | event | raw | PST cue code A |
| `event_65322` | 37 | event | raw | PST cue code B |
| `event_65323` | 54 | event | raw | PST cue code C |
| `event_65324` | 44 | event | raw | PST cue code |
| `event_65325` | 47 | event | raw | PST cue code |
| `event_65326` | 1487 | event | raw | PRBP trial start/code |
| `event_65327` | 1487 | event | raw | PRBP trial start/code |
| `event_65330` | 1826 | event | raw | Task event code |
| `event_65336` | 979 | event | raw | 5CCPT block/code |
| `event_65337` | 981 | event | raw | 5CCPT block/code |
| `event_65338` | 2 | event | raw | PST rare event |
| `event_65339` | 623 | event | raw | 5CCPT block event |
| `event_65340` | 641 | event | raw | 5CCPT block event |
| `event_65341` | 3 | event | raw | Rare/error event |
| `event_65342` | 3 | event | raw | Rare/error event |
| `event_65343` | 45 | event | raw | PST cue event |
| `event_65344` | 3 | event | raw | Rare/error event |
| `event_65345` | 3 | event | raw | Rare/error event |
| `event_65346` | 602 | event | raw | 5CCPT block event |
| `event_65347` | 603 | event | raw | 5CCPT block event |
| `event_65349` | 204 | event | raw | Task event |
| `event_65360` | 425 | event | raw | PRBP/PST event |
| `event_65361` | 1679 | event | raw | PRBP/PST event |
| `event_65362` | 1232 | event | raw | PRBP/PST event |
| `event_65363` | 1496 | event | raw | PRBP/PST event |
| `event_65364` | 581 | event | raw | PRBP/PST event |
| `event_65366` | 834 | event | raw | PRBP/PST event |
| `event_65396` | 22281 | event | raw | Response/feedback baseline (most frequent) |
| `event_65397` | 14138 | event | raw | Response/feedback event |
| `event_65398` | 370 | event | raw | PST cue type |
| `event_65399` | 370 | event | raw | PST cue type |
| `event_65401` | 322 | event | raw | PST cue event |
| `event_65402` | 322 | event | raw | PST cue event |
| `event_65406` | 1 | event | raw | Session end marker |
| `event_65407` | 1 | event | raw | Session end marker |


### MISC Label Summary
*No misc channels detected in this dataset.*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 5C-CPT Target vs Nontarget Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [see Target Definition]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 65281-65286 (stimulus codes, nontarget range) | 0 | Nontarget stimuli (5C-CPT correct rejections) |
  | 65287 (target stimulus code) | 1 | Target stimuli (5C-CPT hits) |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Primary dataset publication; describes 57 subjects, 73 channels at 512 Hz, and 5C-CPT paradigm with target/nontarget event codes. Paper explicitly identifies target vs nontarget as a primary classification dimension.
- **Kernel Notes**: Event code 65287 appears as the highest-count stimulus event (2911 occurrences) and likely represents target stimuli (hits). The 65281-65286 codes with ~1475-1476 counts each likely represent the 6 nontarget stimulus shapes. The paper specifies cue-locked analysis with tmin=-0.5s, tmax=+1.0s.

### Classical Task 2: Probabilistic Reward/Punishment (PRBP) Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [feedback event codes]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 65291-65295 | 0 | High probability reward/punishment feedback |
  | 65396, 65397 (high-frequency baseline events) | 1 | Low probability feedback / error feedback |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Paper describes PRBP task with probabilistic reward/punishment outcomes and identifies feedback-related EEG biomarkers (delta for reward learning).
- **Kernel Notes**: The most frequent events (65396: 22281, 65397: 14138) likely represent feedback baseline responses. The 65291-65295 range with ~1300-1370 counts each likely represents specific feedback conditions (high/low reward/punishment). Analysis may use feedback-locked epochs with tmin=+0.25s, tmax=+0.55s as suggested by the paper.

### Classical Task 3: Pavlovian-to-Instrumental Transfer (PST) Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [31 PST, 32 PST, 39 PST equivalents]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 65321 | 0 | Pavlovian cue Type A (appetitive) |
  | 65322 | 1 | Pavlovian cue Type B (aversive) |
  | 65323 | 2 | Pavlovian cue Type C (neutral) |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Paper describes PST task with three Pavlovian cue types (codes 31, 32, 39) and theta-band biomarkers for cognitive control.
- **Kernel Notes**: Low-count events in scan output (65321:90, 65322:37, 65323:54) correspond to PST cue markers. Additional PST markers include 65398-65399 (370 each) and 65401-65402 (322 each). Verify exact mapping in events.tsv. Standard stimulus-locked window covers cue processing and anticipation period.

### Normal Task 1: Response-Locked 5C-CPT Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0 s, target_events = [response event codes]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 65301-65313 range (response codes) | 0 | Correct responses |
  | 65311 (highest count response) | 1 | Target responses (hits) |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Paper specifies response-locked analysis for 5C-CPT with tmin=-0.5s, tmax=0s.
- **Kernel Notes**: Response codes 65301-65313 with counts ranging from 38 to 8199 likely represent different response outcomes. 65311 (8199) likely represents hit responses following target stimuli. Response-locked epochs capture motor preparation and execution; may complement stimulus-locked analysis for impulsivity assessment.

### Potential Task 1: Cross-Task Biomarker Integration
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, concatenated across all three paradigms
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Combined task events | Behavioral dimension score | Attention, impulsivity, or reward sensitivity measures |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Paper explicitly integrates biomarkers across paradigms to predict behavioral dimensions; identifies alpha for motivation, theta for cognitive control, delta for reward learning.
- **Kernel Notes**: Requires behavioral scores from task performance metrics; meta-level analysis across paradigms.

### Potential Task 2: Alpha Power Motivation Biomarker
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 1.5 s, target_events = [all stimulus events]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Stimulus events | Alpha power | Motivation/intrinsic reward signal |
- **Evidence**:
  - DOI: 10.1038/s41398-021-01562-w — Paper identifies alpha-band activity as biomarker for motivation across paradigms.
- **Kernel Notes**: Time-frequency analysis recommended for alpha band (8-12 Hz) extraction during post-stimulus window.