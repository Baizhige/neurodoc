# Social Memory cuing

**Dataset**: `openneuro_ds003702` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003702
**Category**: Complex Applied | **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A visual working memory task performed in a virtual reality environment where participants (n=47) recalled object locations and statuses following social (avatar) or non-social (stick) directional cues. The paradigm includes encoding, maintenance, and retrieval phases with stimulus markers ranging from s3001–s3048 and s3220–s3221, acquired using a 64-channel EEG system at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `30af305b674c30fb3f41993aea08b9a9fffbb55d51e94e5b94a9f5638c611c63`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Marker/Impedance` | 135 | admin | raw | System: Impedance check marker |
| `New Segment/` | 20 | admin | raw | System: Recording segment boundary |
| `Stimulus/s3001` | 11926 | event | raw | Trial phase marker: Generic trial event marker (appears with responses and trial boundaries) |
| `Stimulus/s3002` | 1435 | event | raw | Trial phase onset: Trial boundary/condition marker (avatar trial end observed) |
| `Stimulus/s3003` | 1410 | event | raw | Trial phase onset: Trial boundary/condition marker (stick trial end and avatar trial start observed) |
| `Stimulus/s3004` | 1404 | event | raw | Trial phase onset: Trial boundary/condition marker (stick trial start observed) |
| `Stimulus/s3005` | 1438 | event | raw | Trial phase onset: Trial boundary/condition marker (stick trial start and end observed) |
| `Stimulus/s3006` | 1407 | event | raw | Trial phase onset: Trial boundary/condition marker (stick and avatar trial starts observed) |
| `Stimulus/s3007` | 1418 | event | raw | Trial phase onset: Trial boundary/condition marker (avatar trial start observed) |
| `Stimulus/s3008` | 1412 | event | raw | Trial phase onset: Trial boundary/condition marker (stick and avatar trial starts observed) |
| `Stimulus/s3021` | 5653 | event | raw | Trial phase onset: Avatar character shown (cue onset) |
| `Stimulus/s3022` | 5657 | event | raw | Trial phase onset: Memory objects shown (encoding onset) |
| `Stimulus/s3023` | 5657 | event | raw | Trial phase onset: Maintenance interval onset (objects leave screen) |
| `Stimulus/s3024` | 5658 | event | raw | Trial phase onset: Probe object shown (location probe onset) |
| `Stimulus/s3025` | 5659 | event | raw | Trial phase onset: Response 1 made (location probe response) |
| `Stimulus/s3026` | 5660 | event | raw | Trial phase onset: Question 2 shown (status probe onset) |
| `Stimulus/s3027` | 5661 | event | raw | Trial phase onset: Response 2 made (status probe response) |
| `Stimulus/s3028` | 1394 | event | raw | Trial phase onset: Avatar trial end marker |
| `Stimulus/s3040` | 1412 | event | raw | Trial phase onset: Stick trial start marker (appears with condition markers) |
| `Stimulus/s3041` | 5681 | event | raw | Trial phase onset: Stick shown (cue onset) |
| `Stimulus/s3042` | 5682 | event | raw | Trial phase onset: Memory objects shown (encoding onset) |
| `Stimulus/s3043` | 5682 | event | raw | Trial phase onset: Maintenance interval onset (objects leave screen) |
| `Stimulus/s3044` | 5683 | event | raw | Trial phase onset: Probe object shown (location probe onset) |
| `Stimulus/s3045` | 5685 | event | raw | Trial phase onset: Response 1 made (location probe response) |
| `Stimulus/s3046` | 5685 | event | raw | Trial phase onset: Question 2 shown (status probe onset) |
| `Stimulus/s3047` | 5685 | event | raw | Trial phase onset: Response 2 made (status probe response) |
| `Stimulus/s3048` | 1415 | event | raw | Trial phase onset: Stick trial end marker |
| `Stimulus/s3111` | 45 | event | raw | Trial phase onset: Block or session transition marker |
| `Stimulus/s3220` | 2241 | event | raw | Trial phase marker: Incorrect response |
| `Stimulus/s3221` | 8121 | event | raw | Trial phase marker: Correct response |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: social vs non-social cue classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`Stimulus/s3021`, `Stimulus/s3041`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3021` | 0 | social cue (avatar character shown) |
  | `Stimulus/s3041` | 1 | non-social cue (stick shown) |
- **Evidence**:
  - https://doi.org/10.1016/j.dib.2022.107827 — Data descriptor paper confirming 112 trials per condition with blocked counterbalanced design for social (avatar) vs non-social (stick) cue working memory paradigm
  - 10.1109/SMC58881.2025.11343511 — EEG classification study using this dataset with cue-locked epochs for social vs non-social condition decoding
- **Notes**: Epoch window from -0.2 to 2.0 seconds covers the initial cue processing period; encoding phase continues until object offset but this window captures the critical cue-driven attentional orienting period. Both event IDs are confirmed in the dataset's event code documentation (s3021 = avatar shown, s3041 = stick shown).

### Classical Task 2: Valid vs Invalid Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`Stimulus/s3001`, `Stimulus/s3002`, `Stimulus/s3003`, `Stimulus/s3004`, `Stimulus/s3005`, `Stimulus/s3006`, `Stimulus/s3007`, `Stimulus/s3008`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Stimulus/s3001 | 0 | Valid cue (co-occurrence pattern: valid trial boundary) |
  | Stimulus/s3002 | 0 | Valid cue (co-occurrence pattern: valid trial boundary) |
  | Stimulus/s3003 | 1 | Invalid cue (co-occurrence pattern: invalid trial boundary) |
  | Stimulus/s3004 | 1 | Invalid cue (co-occurrence pattern: invalid trial boundary) |
  | Stimulus/s3005 | 0 | Valid cue (co-occurrence pattern: valid trial boundary) |
  | Stimulus/s3006 | 1 | Invalid cue (co-occurrence pattern: invalid trial boundary) |
  | Stimulus/s3007 | 0 | Valid cue (co-occurrence pattern: valid trial boundary) |
  | Stimulus/s3008 | 1 | Invalid cue (co-occurrence pattern: invalid trial boundary) |
- **Evidence**:
  - https://doi.org/10.1016/j.dib.2022.107827 — Data descriptor paper explicitly mentions valid vs. invalid cued location as experimental factor in the visual working memory paradigm with social and non-social cues.
- **Notes**: The s3001-s3008 markers are trial boundary/condition markers that encode experimental parameters including cue validity. Based on the evidence summary, these markers co-occur with condition information and their bit-pattern encodes cue type × validity × position. The exact mapping of which specific s3001-s3008 codes correspond to valid vs invalid trials requires kernel-level disambiguation by examining co-occurrence patterns with s3021-s3027 (avatar) and s3041-s3047 (stick) phase markers. The y=0/1 assignment above represents the valid/invalid split with the specific event-to-validity mapping to be resolved by the kernel examining trial structure. The task uses event route with raw meta level as these are native event markers present in the recording.

### Classical Task 3: Location vs Status Retrieval Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`Stimulus/s3024`, `Stimulus/s3044`, `Stimulus/s3026`, `Stimulus/s3046`]``
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3024` | 0 | Location probe onset (avatar cue condition) |
  | `Stimulus/s3044` | 0 | Location probe onset (stick cue condition) |
  | `Stimulus/s3026` | 1 | Status probe onset (avatar cue condition) |
  | `Stimulus/s3046` | 1 | Status probe onset (stick cue condition) |
- **Evidence**:
  - https://doi.org/10.1016/j.dib.2022.107827 — Data descriptor paper lists location vs status retrieval probes as experimental factor; s3024/s3044 are location probes, s3026/s3046 are status probes
  - README / Event codes — s3024: "Probe object shown - i.e. moment that participant is presented with location probe"; s3026: "Question 2 shown (status probe onset)"; s3044/s3046 are stick-cue equivalents
- **Notes**: Classification task distinguishes between two retrieval types within the visual working memory paradigm: location memory retrieval (y=0, probed first in each trial) versus status memory retrieval (y=1, probed second in each trial). Both cue conditions (avatar/social and stick/non-social) are merged within each class to increase trial count and test generalization across social vs non-social cueing. The 3-second epoch window captures the probe presentation, decision, and response period.

### Classical Task 4: Biological Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | Female | 0 | Female subject |
  | Gender | Male | 1 | Male subject |
- **Evidence**:
  - 10.1109/SMC58881.2025.11343511 — Binary classification of biological sex (Female/Male) from EEG; reference paper explicitly uses this as demonstration task for privacy attack with 31 females and 16 males
- **Notes**: Subject-level biomarker task using segmentation-based epochs since biological sex is a constant per-subject attribute. The 4s non-overlapping segments allow the model to learn sustained EEG patterns that carry sex-related information, consistent with the spectral power features used in the reference paper.

### Potential Task 1: Correct vs Incorrect Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s *, tmax = 1.0 s *, target_events = [`Stimulus/s3220`, `Stimulus/s3221`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3220` | 0 | Incorrect response |
  | `Stimulus/s3221` | 1 | Correct response |
- **Evidence**:
  - `Stimulus/s3220` (n=2241) and `Stimulus/s3221` (n=8121) — Response accuracy markers with ~78% overall accuracy, confirmed by co-occurrence with response events (s3025/s3045) and count ratios consistent with error-related potential paradigms
  - Event code documentation from README and code files — s3220/s3221 explicitly designated as response accuracy markers in trial function
  - Gregory, S., Wang, H., & Kessler, K. (2021) — Visual working memory with social/non-social cuing; response-locked ERN/Pe analysis feasible given response timing markers
- **Notes**: Response-locked epoch window selected to capture error-related negativity (ERN, ~0-100 ms post-response) and error positivity (Pe, ~200-400 ms post-response). The s3220/s3221 markers co-occur with behavioral responses (s3025/s3045 for location probe responses), enabling standard ERN analysis. Class imbalance (~78% correct) is typical for working memory tasks and should be considered in model evaluation.

### Potential Task 2: Encoding vs Maintenance vs Retrieval Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 1 s *, target_events = [`Stimulus/s3022`, `Stimulus/s3023`, `Stimulus/s3024`, `Stimulus/s3042`, `Stimulus/s3043`, `Stimulus/s3044`]``
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3022`, `Stimulus/s3042` | 0 | Encoding phase (memory objects shown) |
  | `Stimulus/s3023`, `Stimulus/s3043` | 1 | Maintenance phase (blank interval) |
  | `Stimulus/s3024`, `Stimulus/s3044` | 2 | Retrieval phase (probe object shown) |
- **Evidence**:
  - 10.1109/SMC58881.2025.11343511 — Three-class classification of working memory phases with spectral power features per phase; explicitly mentions encoding (objects shown), maintenance (blank interval), and retrieval (probe shown) as temporally segmented phases
- **Notes**: Avatar (s3022/s3023/s3024) and stick (s3042/s3043/s3044) cue conditions are merged within each phase to create a balanced three-class phase discrimination task. The 1-second epoch duration is chosen to capture phase-locked neural signatures while avoiding contamination across phases, particularly given the brief maintenance period.

### Potential Task 3: Avatar Trial Phase Progression
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Stimulus/s3021`, `Stimulus/s3022`, `Stimulus/s3023`, `Stimulus/s3024`, `Stimulus/s3025`, `Stimulus/s3026`, `Stimulus/s3027`, `Stimulus/s3028`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3021` | 0 | Avatar character shown (cue onset) |
  | `Stimulus/s3022` | 1 | Memory objects shown (encoding onset) |
  | `Stimulus/s3023` | 2 | Maintenance interval onset (objects leave screen) |
  | `Stimulus/s3024` | 3 | Probe object shown (location probe onset) |
  | `Stimulus/s3025` | 4 | Response 1 made (location probe response) |
  | `Stimulus/s3026` | 5 | Question 2 shown (status probe onset) |
  | `Stimulus/s3027` | 6 | Response 2 made (status probe response) |
  | `Stimulus/s3028` | 7 | Avatar trial end marker |
- **Evidence**:
- **Notes**: 8-class classification of sequential trial phases within avatar-cued working memory trials. Each phase has distinct cognitive demands: cue processing, encoding, maintenance, location probe/response, status probe/response, and trial termination. Short epoch window (-0.2 to 1.0 s) avoids overlap with subsequent phases in rapid trial structure. All event IDs confirmed in dataset with high counts (5653-5661 occurrences except s3028 with 1394). Suitable for temporal generalization or phase decoding analyses.

### Potential Task 4: Stick Trial Phase Progression
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`Stimulus/s3040`, `Stimulus/s3041`, `Stimulus/s3042`, `Stimulus/s3043`, `Stimulus/s3044`, `Stimulus/s3045`, `Stimulus/s3046`, `Stimulus/s3047`, `Stimulus/s3048`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/s3040` | 0 | Stick trial start marker |
  | `Stimulus/s3041` | 1 | Stick shown (cue onset) |
  | `Stimulus/s3042` | 2 | Memory objects shown (encoding onset) |
  | `Stimulus/s3043` | 3 | Maintenance interval onset |
  | `Stimulus/s3044` | 4 | Probe object shown (location probe onset) |
  | `Stimulus/s3045` | 5 | Response 1 made (location probe response) |
  | `Stimulus/s3046` | 6 | Question 2 shown (status probe onset) |
  | `Stimulus/s3047` | 7 | Response 2 made (status probe response) |
  | `Stimulus/s3048` | 8 | Stick trial end marker |
- **Evidence**:
  - README — Event codes list: s3041-s3047 define stick cue phases (character shown, objects shown, maintenance, probe, response, question 2, response 2)
  - events.tsv ground truth — `Stimulus/s3040` and `Stimulus/s3048` appear as stick trial start/end markers with s3041-s3047 as intermediate phase markers
- **Notes**: 9-class sequential phase classification within stick-cued trials. The explicit start marker s3040 (not present in avatar trials) enables trial-anchored epoching. All phase markers are confirmed trial phase onsets from the dataset's event documentation. Epoch parameters inferred from standard phase-locked ERP analysis windows for cognitive state transitions.

### Potential Task 5: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 18–27 (years) | Subject chronological age; complete for all 47 subjects (mean ~20–21). Each segment inherits the subject's age as the regression target. |
- **Evidence**:
  - 10.1109/SMC58881.2025.11343511 — Reference paper explicitly mentions age as prediction task alongside biological sex and user identity from EEG features.
- **Notes**: Segmentation-based approach appropriate for subject-level biomarker regression where no discriminating event exists. 4-second non-overlapping segments provide sufficient samples per subject while maintaining computational tractability. Age range 18–27 years is narrow but non-zero variance; task viability depends on whether EEG contains sufficient age-correlated signal in this young adult sample.

### Potential Task 6: Handedness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Handedness | Left | 0 | Left-handed |
  | Handedness | Right | 1 | Right-handed |
- **Evidence**:
- **Notes**: Subject-level biomarker classification using handedness as a binary label. Segmentation-based approach with 4-second non-overlapping windows treats each segment as a sample with the same subject-level label. Highly imbalanced (46 Right vs 1 Left in sample) but technically valid with ≥2 classes. y values mapped to 0-based sequential integers {0,1}.

### Potential Task 7: Brain-Age Estimation from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 18–27 (years) | Subject chronological age for brain-age regression; derived from participants.tsv |
- **Evidence**:
- **Notes**: Segmentation-based regression using full continuous EEG recordings with 10-second windows (50% overlap) to predict subject age. No event structure is used; the kernel segments the continuous recording and assigns each segment the subject's age from participants.tsv. This provides a context-independent brain-age estimation task complementary to the event-based working memory tasks in this dataset. The segment length of 10s is inferred from Category SKILL defaults for resting-state biomarker paradigms, as no specific value was provided in the candidate hint.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
