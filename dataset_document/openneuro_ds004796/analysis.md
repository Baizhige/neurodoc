# PEARL-Neuro Database (Alzheimer's Risk Genes, Lifestyle, Neuroimaging)

**Dataset**: `openneuro_ds004796` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004796
**Category**: Clinical / Cognitive Neuroscience | **Subjects**: 192 | **Files (Completed)**: 192 | **Channels**: 64 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

The PEARL-Neuro database comprises EEG recordings from 192 middle-aged participants (ages 50–63) enriched for Alzheimer's disease risk factors. Participants completed three EEG paradigms: a Multi-Source Interference Task (MSIT) measuring cognitive control, a Sternberg working memory task with varying cognitive load, and resting-state recordings with alternating eyes-open and eyes-closed conditions. EEG was recorded with 64 channels at 1000 Hz sampling rate using a BioSemi ActiveTwo system. The dataset is uniquely characterized by extensive phenotypic data including APOE and PICALM genotyping, neuropsychological assessments (CVLT, Raven's matrices, NEO-FFI), lifestyle factors, and blood biochemistry markers.

## File Scan Result

> **Kernel SHA256**: `ba07d441d2fd6b98482c167468aa53b755b27a14dca38795653deb08fd2ab380`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 7 | admin | raw | Data segment boundary marker |
| `Stimulus/S  1` | 10282 | event | raw | Response: button no. 1 (MSIT); Eyes-open condition start (rest); Response: not true (sternberg) |
| `Stimulus/S  2` | 9918 | event | raw | Response: button no. 2 (MSIT); Eyes-open condition start (rest); Response: true (sternberg) |
| `Stimulus/S  3` | 6246 | event | raw | Response: button no. 3 (MSIT); Low-demanding condition trial (sternberg) |
| `Stimulus/S  4` | 8495 | event | raw | Trial from FS condition (MSIT); Eyes-closed condition start (rest); High-demanding condition trial (sternberg) |
| `Stimulus/S  5` | 6564 | event | raw | Trial from 00 condition (MSIT) |
| `Stimulus/S 10` | 706 | event | raw | Start of a break (MSIT, sternberg); Unlabeled rest period marker (rest) |
| `Stimulus/S 11` | 3821 | event | raw | Retention period onset (sternberg); Unlabeled rest period marker (rest) |
| `Stimulus/S 12` | 11237 | event | raw | Probe stimulus onset (sternberg) |
| `Time 0/` | 1 | admin | raw | Recording time zero reference marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: APOE4 Genetic Status Classification (MSIT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 0.84 s, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`]`
- **Label Route**: `info`
- **Label Field**: `APOE_haplotype`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  | --- | --- | --- | --- |
  | `APOE_haplotype` | e3/e3, e3/e2, e2/e2 | 0 | APOE4- (non-carrier) |
  | `APOE_haplotype` | e2/e4, e3/e4, e4/e4 | 1 | APOE4+ (carrier) |
- **Evidence**:
  - 10.3389/fnins.2025.1579329 — MSIT theta oscillation propagation features (LPG length) from frontal midline electrodes used for APOE4+ vs APOE4- classification; epoch window 0 to 0.84 s captures stimulus onset to average response time
  - 10.1038/s41597-024-03106-5 — Dataset descriptor for PEARL-Neuro database with MSIT cognitive control paradigm, APOE genotyping, and EEG recordings
- **Notes**: All five MSIT event types (S 1-3 responses, S 4-5 conditions) serve as trial anchors. The classification is performed at the participant level: each trial's label is determined by the participant's APOE haplotype (e4/e4, e3/e4, e2/e4 → APOE4+; e3/e3, e3/e2, e2/e2 → APOE4-). The kernel must map from participants.tsv APOE_haplotype to per-trial binary labels. **REWRITTEN**: Changed from event route to info route with Label Field APOE_haplotype, since APOE4 status is a participant-level variable not encoded in event IDs. Meta Level changed to super because the kernel must derive the binary label from the multi-valued APOE_haplotype field.

### Potential Task 1: MSIT condition classification (FS vs 00)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 0.84 s *, target_events = [`Stimulus/S  4`, `Stimulus/S  5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  4` | 0 | Trial from FS condition (MSIT) |
  | `Stimulus/S  5` | 1 | Trial from 00 condition (MSIT) |
- **Evidence**:
- **Notes**: 2-class classification of MSIT trial conditions using the intrinsic task structure. S 4 (FS condition) and S 5 (00 condition) are the actual experimental condition markers per task-msit_events.json. S 1-3 are response buttons, not conditions. Epoch window of 0-0.84s covers the stimulus-response interval for condition-level decoding. Inferred parameters marked with * due to lack of explicit reference for condition-specific classification timing.

### Potential Task 2: MSIT Response Button Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| `Stimulus/S  1` | 0 | Response: button no. 1 (MSIT) |
| `Stimulus/S  2` | 1 | Response: button no. 2 (MSIT) |
| `Stimulus/S  3` | 2 | Response: button no. 3 (MSIT) |

- **Evidence**:
  - task-msit_events.json — "S  1": "Response: button no. 1", "S  2": "Response: button no. 2", "S  3": "Response: button no. 3"
  - sub-01_task-msit_events.tsv — Confirms event_type values S  1, S  2, S  3 appear with trial_type="response" in actual recordings
  - eeg.json / README — MSIT task description: participants identify the deviant digit among three digits and respond with button press 1, 2, or 3
- **Notes**: Response-locked epoch window inferred from stimulus-locked documentation. The -0.5 to +0.5s window captures pre-response motor preparation (readiness potential) and post-response motor execution/feedback. Event IDs correspond to actual button responses in the MSIT paradigm, making this a motor response classification task rather than stimulus classification. The three response buttons are equiprobable motor outputs that may be discriminable by response-locked EEG signatures.

### Potential Task 3: Sternberg demand level classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 12.36 s *, target_events = [`Stimulus/S  3`, `Stimulus/S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  3` | 0 | Low-demanding condition trial (sternberg) |
  | `Stimulus/S  4` | 1 | High-demanding condition trial (sternberg) |
- **Evidence**:
  - task-sternberg_events.json — Defines S 3 as "Low-demanding condition trial" and S 4 as "High-demanding condition trial"
  - sub-01_task-sternberg_events.tsv — Contains actual occurrences of S 3 and S 4 events with trial_type="stimulus"
  - EVENT MEANINGS — LOCKED GROUND TRUTH — Confirms scope=task-sternberg for both events
- **Notes**: The 12.36 s epoch duration is inferred from the candidate's epoch_hint to capture the full Sternberg trial structure including encoding, retention (S 11), and probe (S 12) phases. This allows decoding of working memory load from the complete trial period. The two demand conditions (S 3 vs S 4) represent the experimental manipulation of cognitive load in the Sternberg working memory paradigm.

### Potential Task 4: Sternberg response type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Response: not true (sternberg) |
  | `Stimulus/S  2` | 1 | Response: true (sternberg) |
- **Evidence**:
  - task-sternberg_events.json — defines S 1 as "Response: not true" and S 2 as "Response: true"
  - sub-01_task-sternberg_events.tsv — shows S 1 and S 2 events occur as response events following probe (S 12) stimuli
- **Notes**: Response-locked epochs centered on participant responses during Sternberg working memory probe phase. The 1-second window (-0.5 to +0.5 s) captures pre-response decision buildup and post-response motor execution. Both response types have high event counts (>9900 each), supporting robust binary classification of memory retrieval confidence/decision outcomes.

### Potential Task 5: Sternberg phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 3 s *, target_events = [`Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 10` | 0 | Break start (inter-trial interval) |
  | `Stimulus/S 11` | 1 | Retention period onset |
  | `Stimulus/S 12` | 2 | Probe stimulus onset |
- **Evidence**:
  - task-sternberg_events.json — Defines S 11 as "Retention" and S 12 as "Probe"; S 10 as "Start of a break"
  - sub-01_task-sternberg_events.tsv — Contains actual occurrences of S 3 (stimulus), S 11, S 12 (stimulus), S 1 (response) confirming the phase sequence in Sternberg task
  - EVENT MEANINGS locked ground truth — Confirms S 11: "Retention period onset (sternberg)", S 12: "Probe stimulus onset (sternberg)", S 10: "Start of a break (MSIT, sternberg)"
- **Notes**: Three-class classification of Sternberg working memory task phases. S 10 serves as break/interval baseline, S 11 marks retention period where memory maintenance occurs, and S 12 marks probe presentation requiring retrieval and response. Note that S 10 is shared with MSIT task as break start; the task context (sternberg) distinguishes its usage here. Epoch timing inferred from standard working memory phase durations.

### Potential Task 6: Resting-state eyes-open vs eyes-closed classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`Stimulus/S  2`, `Stimulus/S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  2` | 0 | Eyes-open condition start (rest) |
  | `Stimulus/S  4` | 1 | Eyes-closed condition start (rest) |
- **Evidence**:
  - 10.1109/ICDMW69685.2025.00218 — Uses resting-state EEG with spectral analysis for dementia risk stratification; alpha power modulation between eyes-open and eyes-closed conditions is a classical biomarker.
- **Notes**: The task-rest_events.json explicitly defines S 2 as "Eyes-open condition start" and S 4 as "Eyes-closed condition start". The 4-second epoch length is inferred from spectral analysis conventions in resting-state EEG literature and is appropriate given that eyes-open/closed blocks are typically 30-120 seconds long, allowing multiple epochs per condition. Both events are confirmed present in the rest task recordings with substantial counts (S 2: 9918, S 4: 8495 across the dataset).

### Potential Task 7: Age regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 50–63 (years) | Chronological age from participants.tsv; continuous regression target for brain-age prediction paradigm |
- **Evidence**:
- **Notes**: Archetype C with info-native label (age from participants.tsv). Segmentation-based epoching with no event dependence; 4s segments with 50% overlap (2s) are standard defaults for resting-state spectral feature extraction when no reference specifies otherwise. The kernel does not need to derive any misc channel—age is directly available as a native participants.tsv column.

### Potential Task 8: Age regression from task EEG (MSIT)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 0.84 s *, overlap = 0.42 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 50–63 (years) | Chronological age from participants.tsv; continuous regression target across middle-aged cohort |
- **Evidence**:
- **Notes**: Segmentation-based regression using fixed 0.84s windows (matching MSIT trial duration) with 50% overlap (0.42s). Task-engaged EEG from MSIT cognitive control paradigm may provide complementary age-related neural features compared to resting-state approaches for brain-age prediction. Age values are complete across N=192 participants.

### Potential Task 9: Sex classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | 0 | 0 | female |
  | sex | 1 | 1 | male |
- **Evidence**:
- **Notes**: Standard resting-state sex decoding using 4-second non-overlapping or overlapping segments from eyes-open/eyes-closed rest conditions. The sex label is drawn from participants.tsv (0=female, 1=male) with a balanced cohort (89 vs 103). No event structure is needed since this is a subject-level classification using segmentation-based epoching. The segment_length and overlap values are inferred from standard resting-state analysis practice (4s windows with 50% overlap).

### Potential Task 10: BDI Depression Score Regression from Resting-State EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `BDI`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | BDI | 0–20 (score) | Beck Depression Inventory total score; subclinical to mild depression range in this cohort (N=192, complete data) |
- **Evidence**:
  - Dzianok & Kublik (2024), Sci Data 11:276 — PEARL-Neuro database description; BDI collected as part of neuropsychological battery in dementia-risk cohort
- **Notes**: Segmentation-based epoching with 4s windows and 50% overlap (2s) for resting-state spectral feature extraction. BDI scores from participants.tsv (complete, range 0–20) serve as continuous regression targets. This is a potential task as no published EEG-ML study was found using this specific target.

### Potential Task 11: NEO neuroticism regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `NEO_NEU`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | NEO_NEU | 7–36 (score) | NEO-FFI neuroticism subscale; higher scores indicate greater emotional instability/anxiety |
- **Evidence**:
- **Notes**: Standard resting-state EEG segmentation with 4-second windows and 50% overlap (2 seconds). NEO_NEU scores are drawn from participants.tsv as a native info field. The kernel must filter to task-rest recordings and segment continuous eyes-open/eyes-closed resting data without event-based epoching. Regression target is the continuous neuroticism personality trait score.

### Potential Task 12: PICALM genotype classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PICALM_rs3851179`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | PICALM_rs3851179 | A/A | 0 | Homozygous A allele |
  | PICALM_rs3851179 | G/A | 1 | Heterozygous G/A |
  | PICALM_rs3851179 | G/G | 2 | Homozygous G allele |
- **Evidence**:
  - participants.tsv — PICALM_rs3851179 genotype complete for all 192 participants with values A/A, G/A, G/G
- **Notes**: Archetype C with segmentation + info-native. The 4-second segments with 50% overlap are standard for resting-state EEG analysis to capture spectral features while maintaining sufficient samples per participant. The PICALM rs3851179 SNP is a known Alzheimer's risk locus; classification aims to identify genotype-specific neural signatures from spontaneous EEG activity.

### Potential Task 13: Education level regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `education`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | education | 1–3 (years/category) | Partial completeness (174/192); values represent education level categories. Missing values require handling. |
- **Evidence**:
  - participants.tsv — education column: numeric, partial completeness (174/192), sample values [3, 2, 1]
- **Notes**: Standard 4-second segments with 50% overlap (2s) for resting-state EEG analysis. Education level serves as a proxy for cognitive reserve. The task uses native info field (participants.tsv column) with no kernel derivation required. Missing values in 18/192 subjects will need imputation or exclusion.

### Potential Task 14: BMI regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `BMI`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | BMI | 22.15–32.66 (kg/m²) | Body mass index from participants.tsv; complete data for all 192 participants. Range in sample approximately 22–33. Metabolic health marker relevant to dementia risk; may relate to sleep architecture or vascular contributions to resting-state EEG signals. |
- **Evidence**:
- **Notes**: Segmentation-based task using 4-second non-overlapping or overlapping windows of resting-state EEG to predict BMI. Since this is archetype C with info-native label (BMI from participants.tsv) and no derived misc channel needed, Meta Level remains raw. The epoch parameters are inferred from standard resting-state analysis conventions (4s segments with 50% overlap) as no explicit segmentation parameters are provided in dataset documentation.

### Potential Task 15: CVLT total learning regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `CVLT_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | CVLT_1 | 46–74 (score) | California Verbal Learning Test total learning score; episodic memory capacity marker |
- **Evidence**:
- **Notes**: Archetype C with info-native label (CVLT_1 from participants.tsv). Resting-state EEG segmented into 4-second non-overlapping windows with 50% overlap (2s) for feature extraction. No event anchors needed for segmentation. CVLT_1 is a complete numeric column (192/192) measuring verbal learning capacity, relevant to preclinical AD detection research.

### Potential Task 16: CVLT delayed recall regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `CVLT_9`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | CVLT_9 | 0–16 (count) | California Verbal Learning Test delayed recall score; range 0–8 observed in sample (0–16 possible). Higher scores indicate better verbal memory. |
- **Evidence**:
- **Notes**: Archetype C (segmentation + info-native). The resting-state EEG is segmented into non-overlapping/overlapping windows; no event alignment is needed. CVLT_9 is a native participants.tsv column (complete, numeric), so Meta Level = raw. The 4s segment length with 2s overlap (50%) is a standard choice for resting-state EEG feature extraction, though the specific values are inferred from common practice rather than dataset-specific documentation.

### Potential Task 17: Raven's matrices score regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `RPM`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | RPM | 50–58 (score) | Raven's Progressive Matrices total correct score; fluid intelligence measure. Complete data across N=192 participants. Higher scores indicate better fluid reasoning ability. |
- **Evidence**:
- **Notes**: Archetype C with info-native label (participants.tsv column). Segmentation-based epoching with 4-second non-overlapping or overlapping windows applied to resting-state EEG; no event anchors required. The RPM score is a per-participant scalar regressed from distributed resting-state EEG features. Standard resting-state analysis parameters (4s segments, 50% overlap) were inferred from common practice in the field.

### Potential Task 18: Handedness classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `EHI`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | EHI | < 0 | 0 | Left-handed (negative EHI lateralization quotient) |
  | EHI | >= 0 | 1 | Right-handed or ambidextrous (non-negative EHI lateralization quotient) |
- **Evidence**:
- **Notes**: EHI (Edinburgh Handedness Inventory) ranges from -100 (strongly left-handed) to +100 (strongly right-handed). The sample shows values [100, 60, 50, 100, 100, 100, 60], all non-negative, suggesting a right-handed dominant cohort. For binary classification, we threshold at 0: negative values → y=0 (left-handed), non-negative values → y=1 (right-handed/ambidextrous). This is a standard approach for handedness classification from resting-state EEG, where frontal alpha asymmetry has been associated with handedness. The epoch parameters use standard 4-second segments with 50% overlap (2s) for resting-state analysis; segment_length and overlap are inferred from the candidate's epoch_hint with inferred=true. The task uses segmentation with empty target_events as required for epoch_by_segmentation_hdf5.

### Potential Task 19: Hypertension status classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `hypertension`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | hypertension | 0 | 0 | No hypertension |
  | hypertension | 1 | 1 | Hypertension present |
- **Evidence**:
  - participants.tsv — hypertension column (complete, binary 0/1) from PEARL-Neuro health questionnaire data
- **Notes**: Segmentation-based task using 4-second non-overlapping or overlapping windows from resting-state EEG. The hypertension label is a native participants.tsv column (archetype C with info-native), so Meta Level = raw. Resting-state data is identified by task-rest files; no event-based epoching is needed. The 50% overlap (2s) with 4s segments is a standard choice for resting-state spectral analysis to increase sample count while maintaining window independence.

### Potential Task 20: Smoking status classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `smoking_status`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | smoking_status | 0 | 0 | Never smoked |
  | smoking_status | 1 | 1 | Former smoker |
  | smoking_status | 2 | 2 | Current smoker |
- **Evidence**:
- **Notes**: Archetype C with info-native label. The `smoking_status` column in participants.tsv provides complete 3-class labels (0=never, 1=former, 2=current) for all 192 participants. Resting-state EEG is segmented into non-overlapping/overlapping 4-second windows for subject-level classification. The segment_length and overlap values are inferred from standard resting-state analysis practice (50% overlap) as no explicit epoch parameters were specified in the dataset documentation.

### Potential Task 21: Coffee intake classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `coffee_status`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | coffee_status | 0 | 0 | No coffee intake |
  | coffee_status | 1 | 1 | Low coffee intake |
  | coffee_status | 2 | 2 | Moderate coffee intake |
  | coffee_status | 3 | 3 | High coffee intake |
- **Evidence**:
- **Notes**: Four-class classification of self-reported coffee intake status from resting-state EEG segments. The coffee_status field is a complete native participants.tsv column with values 0-3. Standard 4-second non-overlapping or 50%-overlapping segments are used for resting-state analysis. Caffeine is known to modulate alpha and beta EEG power, making this a plausible biomarker task. The resting-state data is identified by task-rest files with eyes-open (S 2) and eyes-closed (S 4) conditions; segmentation approach uses the continuous recording without event-locked epochs.

### Potential Task 22: Dementia parental history classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `dementia_history_parents`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | dementia_history_parents | 0 | 0 | No parental dementia history |
  | dementia_history_parents | 1 | 1 | One parent with dementia history |
  | dementia_history_parents | 2 | 2 | Both parents with dementia history |
- **Evidence**:
  - Dzianok & Kublik (2024) Sci Data 11, 276 — PEARL-Neuro database describing middle-aged participants at risk of dementia with comprehensive family history assessment including parental dementia history coded as 0/1/2
- **Notes**: This is a C-archetype task with info-native label (participants.tsv column). The epoch parameters use standard resting-state segmentation (4s windows, 50% overlap) inferred from domain conventions since the dataset does not specify exact parameters. The classification target is complete across all 192 participants with three balanced classes representing genetic/familial risk stratification for Alzheimer's disease.

### Potential Task 23: Total cholesterol regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `total_cholesterol`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | total_cholesterol | 152.9–283.1 (mg/dL) | Incomplete: 76/192 subjects with blood biochemistry data; cardiovascular risk factor |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Standard resting-state segmentation into 4s windows with 50% overlap. Total cholesterol is a blood biochemistry measure available for a substantial subset (76/192) of the PEARL-Neuro cohort, a middle-aged population at risk of dementia. The regression target is native to participants.tsv with no kernel derivation required.

### Potential Task 24: Triglycerides regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `triglycerides`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | triglycerides | 43.6–179.6 (mg/dL) | Incomplete coverage (76/192 subjects). Metabolic syndrome component associated with vascular dementia risk. |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Segmentation-based epoching (no event anchors) with 4s segments and 50% overlap for resting-state EEG analysis. Triglycerides measured from blood biochemistry panel; wide physiological range supports regression feasibility despite incomplete data.

### Potential Task 25: HSV-1 serostatus classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `HSV_r`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | HSV_r | 0 | 0 | HSV-1 seronegative |
  | HSV_r | 1 | 1 | HSV-1 seropositive |
- **Evidence**:
- **Notes**: Archetype C with info-native label (B3-style). The HSV_r field is a participants.tsv column with 76/192 completeness (binary 0/1 values), representing Herpes Simplex Virus type 1 serostatus. Resting-state EEG is segmented into 4-second non-overlapping windows (50% overlap = 2s) for biomarker exploration. The infectious hypothesis of Alzheimer's disease implicates HSV-1 in pathogenesis; this task explores whether resting-state EEG patterns can discriminate serostatus in a dementia-risk cohort. Segmentation is used because resting-state lacks event structure suitable for epoching by triggers.

## Data Quality Notes

- Event ID `Stimulus/S  1` through `Stimulus/S  5` have overloaded meanings that depend on task context (MSIT, Sternberg, or rest), requiring task-specific filtering for correct interpretation.
- The `device` field is completely missing from info metadata, preventing automated equipment verification.
- Blood biochemistry fields (leukocytes through HSV_r) have substantial missing data (76/192, ~40% missing), limiting power for tasks using these targets.
- Several psychometric and health fields show minor incompleteness: `session_order` (70/192), `education` (174/192), `learning_deficits` (175/192), `allergies` (73/192), `other_diseases` (189/192), and multiple MINI-COPE subscales (~187-190/192).
- The `APOE_rs429358` field contains a `T/?` value indicating unresolved genotype, which may require special handling in haplotype derivation.
- Event counts for `Stimulus/S 10` (706) are substantially lower than other events, reflecting its role as break marker rather than trial event.
- Resting-state event meanings for S 1, S 2, S 3, S 4, S 10, S 11 differ from their task-specific meanings and are marked as "Unlabeled rest period marker" or condition starts in the ground truth.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
