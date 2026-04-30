# Real World Table Tennis

**Dataset**: `openneuro_ds004505` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004505
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants played real table tennis matches in cooperative (rallying) and competitive (point-scoring) conditions with a partner. EEG was recorded during actual gameplay using a mobile EEG system with synchronized IMU sensors. Hit events were detected via IMU acceleration peaks (>0.75g threshold) verified against video data. Serve and hit markers distinguish roles (subject vs responder) during competitive play. The study investigates motor cortex dynamics during ecological real-world sport.

## File Scan Result

> **Kernel SHA256**: `8141bb392a9d76ad1dea3132e85829b020e0959d5d13641e6593b27ab7c2ff8f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Hit_res_competitive` | 73 | event | raw | Trial phase onset: Hit response in competitive condition |
| `Hit_sub_competitive` | 78 | event | raw | Trial phase onset: Hit subject action in competitive condition |
| `M  1` | 48497 | event | raw | Sync event recorded with BrainVision system |
| `Master/M  1` | 48516 | event | raw | Sync event recorded with BrainVision system (master recording) |
| `Serve_res_competitive` | 20 | event | raw | Trial phase onset: Serve response in competitive condition |
| `Serve_sub_competitive` | 16 | event | raw | Trial phase onset: Serve subject action in competitive condition |
| `Subject_hit` | 37556 | event | raw | The participant's paddle made contact with the ball |
| `Subject_receive` | 19097 | event | raw | The ball machine fed OR the human opponent's paddle made contact with the ball |
| `System/In sync` | 126 | admin | raw | System synchronization status: in sync |
| `System/Out of sync` | 130 | admin | raw | System synchronization status: out of sync |
| `boundary` | 403 | admin | raw | Data boundary marker (segment/epoch boundary) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class hit role classification (competitive)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`Hit_res_competitive`, `Hit_sub_competitive`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Hit_res_competitive` | 0 | Responder hit in competitive condition (opponent hit the ball) |
  | `Hit_sub_competitive` | 1 | Subject hit in competitive condition (participant hit the ball) |
- **Evidence**:
  - 10.1523/ENEURO.0463-22.2023 — Classification of subject vs responder hits in competitive table tennis; spectral/ERP analyses time-locked to hit events
  - 10.1016/j.dib.2023.110024 — Dataset descriptor confirming event IDs with IMU-based detection; 73 responder hits and 78 subject hits available
- **Notes**: Event route classification using two distinct hit event types from competitive table tennis condition. Both classes are trial phase onsets marking when either the opponent (responder) or participant (subject) made contact with the ball, enabling classification of hit role from EEG signatures.

### Potential Task 1: 2-class hit vs receive classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Subject_hit`, `Subject_receive`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Subject_hit | 0 | The participant's paddle made contact with the ball |
  | Subject_receive | 1 | The ball machine fed OR the human opponent's paddle made contact with the ball |
- **Evidence**:
  - sub-01_task-TableTennis_events.json — "Subject_hit": "The participant's paddle made contact with the ball"; "Subject_receive": "The ball machine fed OR the human opponent's paddle made contact with the ball"
- **Notes**: Epoch window inferred from SKILL default for real movement with pre-stimulus baseline (-0.2 to 1.0 s). This is a motor action detection task distinguishing self-initiated paddle contact from incoming ball reception. Large class imbalance exists (Subject_hit: 37,556 events vs Subject_receive: 19,097 events, ~2:1 ratio).

### Potential Task 2: 2-class serve role classification (competitive)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Serve_res_competitive`, `Serve_sub_competitive`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Serve_res_competitive` | 0 | Trial phase onset: Serve response in competitive condition (responder serve) |
  | `Serve_sub_competitive` | 1 | Trial phase onset: Serve subject action in competitive condition (subject serve) |
- **Evidence**:
- **Notes**: Very small sample size (36 total events: 20 responder serves, 16 subject serves) makes this task marginal for ML. Epoch window inferred from SKILL default for discrete motor actions (-0.2 to 1.0 s). Events are trial phase markers for serve actions in competitive condition, not motor imagery classes.

### Potential Task 3: 4-class competitive action type
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Hit_sub_competitive`, `Hit_res_competitive`, `Serve_sub_competitive`, `Serve_res_competitive`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Hit_sub_competitive` | 0 | Subject hit in competitive condition |
  | `Hit_res_competitive` | 1 | Responder hit in competitive condition |
  | `Serve_sub_competitive` | 2 | Subject serve in competitive condition |
  | `Serve_res_competitive` | 3 | Responder serve in competitive condition |
- **Evidence**:
- **Notes**: Four-way classification of competitive action types combining hit and serve events for both subject and responder roles. Severe class imbalance noted (serves ~5x rarer than hits). Event meanings inferred from naming patterns in pre-scan raw event counts; these competitive condition markers do not appear in processed events.json files but are present in the raw event stream.

### Potential Task 4: 2-class subject action type (hit vs serve)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Hit_sub_competitive`, `Serve_sub_competitive`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Hit_sub_competitive` | 0 | Hit subject action in competitive condition (reactive, mid-rally) |
  | `Serve_sub_competitive` | 1 | Serve subject action in competitive condition (self-initiated, start of rally) |
- **Evidence**:
  - `events.tsv` samples and event counts — `Hit_sub_competitive` (78 events) and `Serve_sub_competitive` (16 events) appear as trial phase onset markers in competitive condition
  - `sub-01_task-TableTennis_events.json` — defines `value` column levels for confirmed events; competitive condition inferred from event naming pattern
- **Notes**: Small serve sample size (16 events) is marginal for reliable classification. Both classes represent subject-initiated motor actions with different cognitive demands: hitting is reactive (mid-rally response to opponent), while serving is self-initiated (start of rally). Epoch window [-0.2, 1.0] s centered on trial phase onset captures pre-movement readiness potential and early execution, following SKILL default for real movement paradigms. Inferred parameters marked with *.

### Potential Task 5: Age Regression from Continuous EEG During Table Tennis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 23–29 (years) | Complete for all 25 participants; subject-level label applied to all epochs from that subject |
- **Evidence**:
- **Notes**: Archetype C (segmentation + info-native): naturalistic sport viewing paradigm lacks trial structure suitable for event-based epoching. Uses sliding window segmentation (2s windows, 50% overlap) across continuous 60-minute table tennis gameplay data. Age is a native participants.tsv column with complete coverage (N=25, range 23-29). Each subject's age value is broadcast to all segmented epochs from that subject for regression target. No kernel derivation needed—label is directly available from BIDS metadata.

### Potential Task 6: Gender Classification from Continuous Table Tennis EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | F | 0 | Female participant |
  | Gender | M | 1 | Male participant |
- **Evidence**:
- **Notes**: Archetype C with segmentation approach since no event structure discriminates gender. Continuous 60-minute table tennis EEG is segmented into 2-second non-overlapping windows (50% overlap) with subject-level gender labels (F=0, M=1) drawn from participants.tsv. This is a subject-level classification task where each segment from a given participant shares the same gender label. The 2-second window size and 50% overlap are SKILL defaults for naturalistic/continuous data, marked as inferred.

### Potential Task 7: Questionnaire Response Pattern Classification (Q1)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question1 | a | 0 | Response category a |
  | Question1 | b | 1 | Response category b |
  | Question1 | c | 2 | Response category c |
- **Evidence**:
  - participants.tsv — Question1 column is complete with 3 categorical values (a, b, c) across all 25 subjects
- **Notes**: Archetype C with segmentation. The 2-second window length and 50% overlap are SKILL defaults for naturalistic/continuous EEG data (no event-locked structure for this subject-level label). Each subject receives a single label from their Question1 response, and all segments from that subject inherit this label for classification. The psychological construct underlying Question1 is unknown from available metadata.

### Potential Task 8: Questionnaire Response Pattern Classification (Q2)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question2`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question2 | a | 0 | Response category a |
  | Question2 | b | 1 | Response category b |
- **Evidence**:
- **Notes**: Archetype C with segmentation-based epoching. Subject-level binary classification using Question2 responses from participants.tsv. Since this is a naturalistic/continuous dataset with no trial structure suitable for event-based epoching, 2-second sliding windows with 50% overlap are used. Each subject receives a single label (a or b) based on their questionnaire response, and all windows from that subject share the same label. The construct being measured by Question2 is not specified in available documentation.

### Potential Task 9: Questionnaire Response Pattern Classification (Q3)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question3`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question3 | a | 0 | Response category a |
  | Question3 | b | 1 | Response category b |
  | Question3 | c | 2 | Response category c |
- **Evidence**:
  - participants.tsv — Question3 column complete with 3 categorical values (a, b, c) across N=25 subjects; sample values [c, b, a]
- **Notes**: Archetype C with segmentation: continuous EEG is segmented into 2-second non-overlapping windows (50% overlap) and each window inherits the subject-level Question3 label. This creates a subject-level classification task where the model learns to discriminate questionnaire response categories from naturalistic table tennis EEG patterns. The 2s window length and 0.5 overlap are SKILL defaults for naturalistic/continuous data, marked as inferred.

### Potential Task 10: Questionnaire Response Pattern Classification (Q4)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Question4`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question4 | a | 0 | Response category a |
  | Question4 | b | 1 | Response category b |
  | Question4 | c | 2 | Response category c |
  | Question4 | d | 3 | Response category d |
- **Evidence**:
  - participants.tsv — Question4 column is complete with 4 categorical response classes (a, b, c, d) across all 25 subjects; sample values confirm distribution includes all four categories
- **Notes**: Archetype C with segmentation approach: continuous EEG is segmented into 2-second windows with 50% overlap. Each subject receives a single label from their Question4 response, creating a subject-level classification task. The kernel does not need to derive any channels since Question4 is a native participants.tsv info field. All epochs from a given subject share the same label, enabling subject-level pattern classification across the naturalistic table tennis viewing paradigm.

### Potential Task 11: Questionnaire Response Pattern Classification (Q5)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question5`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question5 | a | 0 | Response category a |
  | Question5 | b | 1 | Response category b |
  | Question5 | c | 2 | Response category c |
  | Question5 | d | 3 | Response category d |
- **Evidence**:
  - participants.tsv — Question5 column is complete with categorical values {a, b, c, d} across all 25 subjects
- **Notes**: Archetype C with segmentation-based epoching. Since this is a subject-level classification using info route with native participants.tsv column, Meta Level is raw. The 2-second window length with 50% overlap is a SKILL default for naturalistic/continuous EEG data, marked as inferred. Each subject's entire recording is segmented into overlapping windows, all assigned the same label from that subject's Question5 response. This creates a subject-level stratification task where the model must learn to distinguish response patterns from continuous table tennis gameplay EEG.

### Potential Task 12: Questionnaire Response Pattern Classification (Q6)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Question6`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question6 | a | 0 | Response option a |
  | Question6 | b | 1 | Response option b |
  | Question6 | c | 2 | Response option c |
  | Question6 | d | 3 | Response option d |
- **Evidence**:
  - participants.tsv — Question6 column present with categorical responses (a, b, c, d), completeness=complete, N=25
- **Notes**: Archetype C with segmentation-based epoching. Since the task uses info-native label (Question6 from participants.tsv), Meta Level is raw. The 2-second window length with 50% overlap follows SKILL defaults for naturalistic/continuous EEG data where no event-locked epochs are available. Each subject is assigned a single class label based on their questionnaire response, and classification is performed across subjects using segmented EEG features. The encoding a=0, b=1, c=2, d=3 preserves 0-based sequential integers as required.

### Potential Task 13: Questionnaire Response Pattern Classification (Q7)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question7`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question7 | a | 0 | Response category a |
  | Question7 | b | 1 | Response category b |
  | Question7 | c | 2 | Response category c |
  | Question7 | d | 3 | Response category d |
- **Evidence**:
  - participants.tsv — Question7 column is complete (N=25) with categorical values {a, b, c, d}; sample values include [d, b, c]
- **Notes**: Archetype C with segmentation-based epoching. Since this is a subject-level classification using info route with native participants.tsv column, Meta Level is raw (no kernel derivation needed). The 2-second windows with 50% overlap are SKILL defaults for naturalistic/continuous EEG data, applied here because the dataset contains 60 minutes of continuous table tennis play without trial-structured event boundaries suitable for epoching. Classification predicts which questionnaire response category (a/b/c/d) a subject gave, with all epochs from a given subject receiving the same label.

### Potential Task 14: Questionnaire Response Pattern Classification (Q8)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Question8`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question8 | a | 0 | Response option a |
  | Question8 | b | 1 | Response option b |
  | Question8 | c | 2 | Response option c |
  | Question8 | d | 3 | Response option d |
- **Evidence**:
- **Notes**: Archetype C with segmentation and info-native label. The 2-second windows with 50% overlap are SKILL defaults for naturalistic/continuous data (inferred). Since this is a subject-level classification task, all epochs from a given subject share the same Question8 label. The classifier must learn to distinguish between subjects based on their neural activity patterns during table tennis, where the grouping is determined by their response to Question8 (a/b/c/d). The participants.tsv shows Question8 is complete with values {a, b, c, d} across all 25 subjects, mapped to 0-based sequential integers.

### Potential Task 15: Questionnaire Response Pattern Classification (Q9)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Question9`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Question9 | a | 0 | Response category a |
  | Question9 | b | 1 | Response category b |
  | Question9 | c | 2 | Response category c |
- **Evidence**:
  - participants.tsv — Question9 column with complete categorical responses (a, b, c) for all 25 subjects
- **Notes**: Archetype C with segmentation-based epoching. The 2-second window length with 50% overlap is inferred from SKILL defaults for naturalistic/continuous EEG data. Each subject receives a single label from their Question9 response, and all 2-second segments from that subject share this label. This creates a subject-level classification task predicting questionnaire response category from resting/naturalistic EEG patterns.

## Data Quality Notes

- Mobile EEG during physical sports activity introduces substantial motion artifacts; extended ICA cleaning or artifact rejection pipelines likely required.
- Large class imbalance in `Subject_hit` (37,556) vs `Subject_receive` (19,097) events (~2:1 ratio) for Potential Task 1.
- Very small sample sizes for serve events (`Serve_res_competitive`: 20, `Serve_sub_competitive`: 16) make serve-related tasks marginal for reliable ML.
- Hardware sync markers (`M  1`, `Master/M  1`) and system sync markers (`System/In sync`, `System/Out of sync`) are present in large numbers and should be excluded from epoching.
- `boundary` events (403 total) indicate data segmentation and should be filtered before epoching.
- Discrepancy between metadata fields: `subject_age` and `subject_sex` are missing in BIDS sidecar, but `Age` and `Gender` are complete in participants.tsv with 25 subjects; only 19 files completed suggests partial file availability vs. full participant enrollment.
- Questionnaire constructs (Q1–Q9) are undocumented in available metadata; psychological meaning of response categories is unknown.
- No super meta required; all tasks use raw event or info-native labels.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
