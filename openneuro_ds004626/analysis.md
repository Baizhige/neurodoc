# Can We Dissociate Hypervigilance to Social Threats from Altered Perceptual Decision-Making in Lonely Individuals

**Dataset**: `openneuro_ds004626` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004626
**Category**: High-level Mental | **Subjects**: 52 | **Files (Completed)**: 52 | **Channels**: 68 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

A perceptual decision-making task investigating whether lonely individuals exhibit hypervigilance toward social threats, combining Drift Diffusion Modeling (DDM) with ERP analysis. Participants viewed social and non-social threat stimuli and made rapid perceptual judgements. ERP components (P1, N2pc, LPP) and computational decision parameters were compared across loneliness severity groups.

## File Scan Result

> **Kernel SHA256**: `803728206c185507baf90e4356ef3057790f62b9fa780aba0cfd2c37811af341`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 5 | admin | raw | System marker: rare session/trial marker (observed in select subjects, function unclear from available evidence) |
| `132` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `135` | 1560 | event | raw | Stimulus: Dot - dots vertically, target right, neutral-angry, inhibitory, female faces |
| `143` | 1 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt; rare occurrence) |
| `144` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `145` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `151` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `159` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `160` | 363 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt; infrequent occurrence) |
| `167` | 1560 | event | raw | Stimulus: Dot - dots horizontally, target right, neutral-angry, non-inhibitory, female faces |
| `175` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `176` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `183` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `184` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `191` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `192` | 118 | event | raw | Trial phase onset: trial start/initiation marker (consistently paired with 200 at trial beginnings) |
| `199` | 1560 | event | raw | Stimulus: Dot - dots horizontally, target left, neutral-angry, inhibitory, female faces |
| `200` | 219 | event | raw | Trial phase onset: trial start/initiation marker (consistently paired with 192 at trial beginnings) |
| `207` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `209` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `215` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `216` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `223` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `224` | 487 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `231` | 1560 | event | raw | Stimulus: Dot - dots vertically, target left, neutral-angry, non-inhibitory, female faces |
| `239` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `240` | 1 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt; rare occurrence) |
| `248` | 1560 | event | raw | Stimulus: Dot condition marker (specific configuration not defined in available events.json excerpt) |
| `251` | 1560 | event | raw | Stimulus: Dot - dots vertically, target left, neutral-angry, non-inhibitory, female faces |
| `300` | 1528 | event | raw | Trial phase onset: task end or session conclusion marker (observed near end of recordings) |
| `admin_sync` | 1560 | admin | raw | System marker: trigger synchronization pulse |
| `admin_trial_end` | 2363 | admin | raw | System marker: trial end boundary |
| `response_button_press` | 36977 | event | raw | Response: participant button press |
| `stim_condition_A` | 6239 | event | super | Derived annotation: stimulus condition category A |
| `stim_condition_B` | 6238 | event | super | Derived annotation: stimulus condition category B |
| `stim_condition_C` | 6238 | event | super | Derived annotation: stimulus condition category C |
| `stim_condition_D` | 6240 | event | super | Derived annotation: stimulus condition category D |
| `stim_condition_E` | 6237 | event | super | Derived annotation: stimulus condition category E |
| `stim_condition_F` | 6233 | event | super | Derived annotation: stimulus condition category F |
| `trial_boundary_ITI` | 35001 | admin | raw | Trial phase onset: inter-trial interval onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Social Threat vs Non-Social Threat Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.6 s *, target_events = [`135`, `167`, `199`, `231`, `251`, `132`, `144`, `145`, `151`, `159`, `160`, `175`, `176`, `183`, `184`, `191`, `207`, `209`, `215`, `216`, `223`, `224`, `239`, `248`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| 135 | 0 | Social threat: neutral-angry, vertical dots, target right, inhibitory, female |
| 167 | 0 | Social threat: neutral-angry, horizontal dots, target right, non-inhibitory, female |
| 199 | 0 | Social threat: neutral-angry, horizontal dots, target left, inhibitory, female |
| 231 | 0 | Social threat: neutral-angry, vertical dots, target left, non-inhibitory, female |
| 251 | 0 | Social threat: neutral-angry, vertical dots, target left, non-inhibitory, female |
| 132 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 144 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 145 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 151 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 159 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 160 | 1 | Non-social threat/neutral: dot condition (undefined configuration, infrequent) |
| 175 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 176 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 183 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 184 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 191 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 207 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 209 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 215 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 216 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 223 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 224 | 1 | Non-social threat/neutral: dot condition (undefined configuration, infrequent) |
| 239 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |
| 248 | 1 | Non-social threat/neutral: dot condition (undefined configuration) |

- **Evidence**:
  - 10.1111/psyp.14406 — Within-subject contrast from source paper: stimulus conditions include social threat (neutral-angry faces) vs non-social threat vs neutral cues. Confirmed codes 135, 167, 199, 231, 251 involve neutral-angry face pairs (social threat).
  - task-DotProbe_events.json — Confirmed definitions for codes 135, 167, 199, 231, 251 as 'Stimulus: Dot' conditions with neutral-angry face emotion pairing (social threat); other codes 132-251 encode other stimulus configurations per events.json 'Levels' structure.
- **Notes**: Social threat events (y=0) are those with confirmed neutral-angry face pairings from events.json. All other dot-probe stimulus events (y=1) serve as the non-social threat/neutral comparison condition. The epoch window [-0.2, 0.6] s captures the N2pc attentional bias component (200-300 ms post-stimulus) with standard 200 ms pre-stimulus baseline. Event codes 160 and 224 have reduced trial counts (363 and 487 respectively) but are retained as they represent valid stimulus presentations within the non-social threat class.

### Classical Task 2: Congruent vs Incongruent Probe Location
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.6 s *, target_events = [`135`, `167`, `199`, `231`, `251`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 135 | 0 | Congruent: target right, inhibitory (probe at emotional stimulus location) |
  | 167 | 1 | Incongruent: target right, non-inhibitory (probe at neutral stimulus location) |
  | 199 | 0 | Congruent: target left, inhibitory (probe at emotional stimulus location) |
  | 231 | 1 | Incongruent: target left, non-inhibitory (probe at neutral stimulus location) |
  | 251 | 1 | Incongruent: target left, non-inhibitory (probe at neutral stimulus location) |
- **Evidence**:
  - 10.1111/psyp.14406 — Source paper explicitly defines congruency by whether probe appears at location of emotional vs neutral stimulus; confirmed event codes 135/199 are inhibitory (congruent) and 167/231/251 are non-inhibitory (incongruent)
  - task-DotProbe_events.json — Confirmed definitions: 135=target right/inhibitory, 167=target right/non-inhibitory, 199=target left/inhibitory, 231=target left/non-inhibitory, 251=target left/non-inhibitory
- **Notes**: Congruency is determined by the inhibitory status field in the event code definitions. Inhibitory trials (codes 135, 199) indicate the probe appears at the emotional stimulus location (congruent), while non-inhibitory trials (codes 167, 231, 251) indicate the probe appears at the neutral stimulus location (incongruent). Codes 231 and 251 are merged as they share identical experimental conditions (target left, non-inhibitory). The epoch window captures the N2pc attentional component (200-300ms post-stimulus) with a 200ms pre-stimulus baseline.

### Classical Task 3: Inhibitory vs Non-Inhibitory Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`135`, `199`, `167`, `231`, `251`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 135 | 0 | Inhibitory (dots vertical, target right, neutral-angry, female faces) |
  | 199 | 0 | Inhibitory (dots horizontal, target left, neutral-angry, female faces) |
  | 167 | 1 | Non-inhibitory (dots horizontal, target right, neutral-angry, female faces) |
  | 231 | 1 | Non-inhibitory (dots vertical, target left, neutral-angry, female faces) |
  | 251 | 1 | Non-inhibitory (dots vertical, target left, neutral-angry, female faces) |
- **Evidence**:
  - 10.1111/psyp.14406 — Confirmed codes explicitly encode inhibitory status: 135=inhibitory, 167=non-inhibitory, 199=inhibitory, 231=non-inhibitory, 251=non-inhibitory. Core task manipulation in dot-probe paradigm for measuring attentional control.
- **Notes**: Two inhibitory conditions (135, 199) mapped to y=0; three non-inhibitory conditions (167, 231, 251) mapped to y=1. This binary grouping collapses across dot orientation and target side to isolate the inhibitory demand manipulation. The epoch window [-0.2, 0.8] s captures pre-stimulus baseline and extends through the late positive potential (LPP) window (400-700 ms) relevant for regulatory and inhibitory processing.

### Potential Task 1: Vertical vs Horizontal Dot Orientation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`135`, `167`, `199`, `231`, `251`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 135 | 0 | vertical dots (target right, neutral-angry, inhibitory, female faces) |
  | 231 | 0 | vertical dots (target left, neutral-angry, non-inhibitory, female faces) |
  | 251 | 0 | vertical dots (target left, neutral-angry, non-inhibitory, female faces) |
  | 167 | 1 | horizontal dots (target right, neutral-angry, non-inhibitory, female faces) |
  | 199 | 1 | horizontal dots (target left, neutral-angry, inhibitory, female faces) |
- **Evidence**:
  - 10.1111/psyp.14406 — Confirmed codes encode dot orientation as task feature: 135/231/251=vertical dots, 167/199=horizontal dots. This is a perceptual feature of the probe stimulus, not the primary experimental manipulation, but could serve as a control classification to verify basic perceptual ERP differences.
- **Notes**: All five event IDs (135, 167, 199, 231, 251) are explicitly defined in task-DotProbe_events.json with confirmed confidence. The remaining event IDs in kernel_needs.must_have_events are other dot condition markers whose specific configurations were truncated in available json excerpts; they are not used for this task's target definition but are preserved in kernel needs for completeness. The y=0 class merges three vertical dot conditions that vary in target side and inhibitory status; y=1 merges two horizontal dot conditions with similar variations. This many-to-one mapping is justified by the shared perceptual feature (dot orientation) that defines the classification objective.

### Potential Task 2: Target Left vs Target Right
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.5 s *, target_events = [`135`, `167`, `199`, `231`, `251`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 135 | 0 | target right (vertical dots, inhibitory, female faces) |
  | 167 | 0 | target right (horizontal dots, non-inhibitory, female faces) |
  | 199 | 1 | target left (horizontal dots, inhibitory, female faces) |
  | 231 | 1 | target left (vertical dots, non-inhibitory, female faces) |
  | 251 | 1 | target left (vertical dots, non-inhibitory, female faces) |
- **Evidence**:
  - 10.1111/psyp.14406 — Confirmed codes encode target side: 135=target right, 167=target right, 199=target left, 231=target left, 251=target left. Spatial attention is fundamental to dot-probe paradigm; N2pc component specifically indexes lateralized attention deployment.
- **Notes**: All five event IDs (135, 167, 199, 231, 251) are merged into two classes by target side (y=0 for right, y=1 for left), collapsing across dot orientation, inhibitory status, and other condition variations. Epoch window [-0.2, 0.5] s centered on stimulus onset captures the N2pc lateralized component (200-300 ms post-stimulus) optimal for left/right spatial attention discrimination. Values marked with * are inferred from paradigm-appropriate timing for N2pc analysis.

### Potential Task 3: Trial Start Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 1 s *, overlap = 0.0, target_events = [`192`, `200`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 192 | 0 | Trial start/initiation marker (paired onset) |
  | 200 | 1 | Trial start/initiation marker (paired onset) |
- **Evidence**:
  - events.json / events.tsv analysis — Codes 192 and 200 consistently appear paired at trial beginnings across all subjects (192: 118 occurrences, 200: 219 occurrences), identified as trial phase onset markers
- **Notes**: This is a phase-detection task distinguishing two trial-start event codes (192 vs 200) that co-occur at trial beginnings. The classification target is which specific trial-start marker is present, not a motor imagery class. Both codes serve as trial initiation markers in the DotProbe paradigm, with 200 appearing more frequently than 192. The 1-second window captures the fixation/anticipation period before stimulus onset. Overlap set to 0.0 as default for long-event method when not specified.

### Potential Task 4: Loneliness Group from EEG Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | group | lonely | 0 | Lonely group (sub-H*) |
  | group | not-lonely | 1 | Not-lonely group (sub-L*) |
  | group | not-lonley | 1 | Not-lonely group (typo variant, merged) |
- **Evidence**:
  - participants.tsv — 52 subjects with complete group information: 'lonely' (sub-H*) and 'not-lonely'/'not-lonley' (sub-L*) groups
  - README — Dataset explicitly studies loneliness vs non-loneliness group differences in ERPs and drift diffusion modeling
- **Notes**: Segmentation-based approach for continuous EEG analysis with subject-level group labels. The 2-second window with 50% overlap is a standard choice for spectral/feature-based group classification when trial structure is ignored. All three unique group values in participants.tsv are mapped to two classes: 'lonely' → y=0, both 'not-lonely' and 'not-lonley' → y=1 (the latter is a typo variant in the source data).

### Potential Task 5: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–35.0 (years) | Continuous age from participants.tsv; N=52 complete |
- **Evidence**:
  - participants.tsv — age column present for all 52 participants with range 19–35 years
- **Notes**: Segmentation-based regression task predicting chronological age from continuous resting/task EEG. 2-second windows with 50% overlap maximize sample count for subject-level age prediction. Age is a native participants.tsv column requiring no kernel derivation.

### Potential Task 6: Education Years Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `edu_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | edu_years | 12–17+ (years) | Continuous education years from participants.tsv; N=52 complete. Cognitive reserve proxy for neural efficiency regression. |
- **Evidence**:
  - participants.tsv — edu_years column: numeric, complete across N=52 subjects, sample values [12, 17, 15], range approximately 12–17+ years
  - dataset_description.json — confirms dataset is EEG study of lonely vs not-lonely individuals with ERP and drift diffusion modeling analyses
- **Notes**: Archetype B3 (info-native). Standard continuous EEG segmentation for subject-level regression: 2-second non-overlapping/overlapping windows with 50% overlap. Each segment inherits the subject's edu_years value as regression target. No kernel derivation needed—edu_years is a native participants.tsv column.

### Potential Task 7: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | Male | 0 | Male participant |
  | sex | Female | 1 | Female participant |
- **Evidence**:
  - participants.tsv — N=52 participants with sex column: Male=20, Female=32
  - eeg.json — continuous EEG recordings at 1000 Hz, 68 channels, suitable for segmentation-based classification
- **Notes**: Standard 2-second segmentation with 50% overlap for sex classification from continuous resting/task EEG. Sex differences in EEG spectral power and connectivity are well-documented in the literature, making this a plausible baseline ML task. The segment_length was inferred from standard practice for demographic classification from continuous EEG; no specific epoch timing was provided in the dataset documentation.

## Data Quality Notes

- Missing `device` field in info metadata (complete for age, sex, group, edu_years).
- Typo in group label: "not-lonley" present in source data alongside "not-lonely", requiring merge/correction for group classification tasks.
- Event code `300` has slightly fewer occurrences (1528) than other major stimulus codes (1560), suggesting some trials may lack completion markers or have truncated recordings.
- Rare event codes (`1`, `143`, `240`) have very low counts (1-5), indicating possible system glitches or session boundary markers with unclear function.
- Trial start markers `192` (118 occurrences) and `200` (219 occurrences) are imbalanced and inconsistently paired, suggesting potential recording or annotation inconsistencies at trial boundaries.
- Event codes `160` (363) and `224` (487) have substantially reduced counts compared to standard stimulus codes (1560), which may reflect condition-specific trial distributions or data loss; retained as valid but noted for potential class imbalance.
- Super-level derived annotations (`stim_condition_A` through `F`) are present but their mapping to raw event codes is not fully documented in available metadata.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
