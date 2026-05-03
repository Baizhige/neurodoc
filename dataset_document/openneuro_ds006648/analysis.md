# Poetry Aesthetic and Creative Cognition EEG Dataset (ds006648)

**Dataset**: `openneuro_ds006648` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006648
**Category**: High-level Mental| **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 70 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants read and evaluated 210 short English-language texts including Haikus and Senryus on five subjective dimensions related to aesthetic and creative cognition: Aesthetic Appeal, Vivid Imagery, Being Moved, Originality, and Creativity. EEG was recorded during reading using a 64-channel BioSemi system (70 channels total including references). This is the first of two poetry datasets (companion to ds006647) with full N=47 subject coverage.

## File Scan Result

> **Kernel SHA256**: `e7354a297c789d42ee955002f45fa14dd3a935b5bc5c5fdb52fe0ffbccbee404`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65280` | 18 | admin | raw | Session/recording start marker |
| `65281` | 9964 | event | raw | Trial phase onset: fixation cross |
| `65282` | 9964 | event | raw | Trial phase onset: poem presentation |
| `65283` | 9964 | event | raw | Trial phase onset: poem contemplation |
| `65284` | 9993 | event | raw | Trial phase onset: poem rating |
| `65285` | 46 | event | raw | Trial phase onset: resting state 1 |
| `65286` | 47 | event | raw | Trial phase end: resting state 1 |
| `65287` | 47 | event | raw | Trial phase onset: resting state 2 (defined but not observed) |
| `65288` | 47 | event | raw | Trial phase end: resting state 2 (defined but not observed) |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `EXG1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG3` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG4` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG7` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `EXG8` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `EXG1`, `EXG2`, `EXG3`, `EXG4`, `EXG7`, `EXG8`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 4-class trial phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`65281`, `65282`, `65283`, `65284`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65281 | 0 | Trial phase onset: fixation cross |
  | 65282 | 1 | Trial phase onset: poem presentation |
  | 65283 | 2 | Trial phase onset: poem contemplation |
  | 65284 | 3 | Trial phase onset: poem rating |
- **Evidence**:
  - 10.1038/s41597-025-06189-w — Primary trial structure consists of four sequential phases: fixation cross (65281), poem presentation (65282), contemplation (65283), and rating (65284). These occur in ~9964-9993 repetitions each across 47 subjects. The data descriptor paper confirms these as the main experimental conditions for classification by cognitive phase during poetry reading.
- **Notes**: None

---

### Classical Task 2: 3-class text type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`65281`, `65282`, `65283`, `65284`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65281 | 0 | Haiku text (fixation cross onset, trial phase anchor) |
  | 65282 | 1 | Senryu text (poem presentation onset, trial phase anchor) |
  | 65283 | 2 | Control text (poem contemplation onset, trial phase anchor) |
  | 65284 | 0 | Haiku text (poem rating onset, trial phase anchor — merged to y=0) |
- **Evidence**:
  - 10.1038/s41597-025-06189-w — Data descriptor describes 210 texts: 70 Haiku, 70 Senryu, and 70 non-poetic Control texts mapped to conditions A-D (triggers 65281-65284) with text type information decoded from events.tsv trial_type or stim_file columns; 3-class classification by text type (Haiku/Senryu/Control) is explicitly supported.
- **Notes**: The four trial phase markers (65281-65284) each correspond to one of three text types in the experimental design. Per the evidence summary, conditions A-D map to text types requiring metadata lookup from events.tsv columns (trial_type or stim_file). The mapping from event IDs to y labels is many-to-one: 65281 and 65284 both anchor Haiku trials (different phases of the same trial), 65282 anchors Senryu trials, and 65283 anchors Control trials. This many-to-one merging is justified by the paradigm structure where all four phase markers belong to the same trial and share the same underlying text type. The kernel must resolve text type from events.tsv metadata and assign the appropriate class label to all epochs anchored by any of the four event IDs.

---

### Potential Task 1: 2-class rest vs task state
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`65285`, `65281`, `65282`, `65283`, `65284`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65285 | 0 | resting state 1 onset |
  | 65281 | 1 | fixation cross onset (task) |
  | 65282 | 1 | poem presentation onset (task) |
  | 65283 | 1 | poem contemplation onset (task) |
  | 65284 | 1 | poem rating onset (task) |
- **Evidence**:
  - task-readpoetry_events.json — Event value levels confirm 65285 as "Resting State 1 onset" and 65281-65284 as task phase onsets (fixation, poem, contemplation, rating)
  - events.tsv samples — Sub-001 shows 65285 at 18.25s followed by 65286 at 318.25s (300s rest period), then task cycle 65281→65282→65283→65284 repeats
- **Notes**: Rest state epochs are anchored to 65285 onset markers (46 occurrences). Task state epochs are drawn from four distinct task phase onsets (65281-65284, ~9964-9993 occurrences each) to avoid class imbalance and capture active cognitive engagement. Event 65286 (rest end) is excluded as anchor to prevent overlap with subsequent task phases. The 0.2s pre-stimulus window allows baseline correction; 1.0s post-stimulus captures initial evoked responses. Events 65287/65288 (resting state 2) are defined but not observed in data per evidence summary.

---

### Potential Task 2: EXG1-4 EOG regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`65281`, `65282`, `65283`, `65284`]
- **Label Route**: `misc`
- **Label Field**: `EXG1`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | EXG1 | Continuous voltage (μV) regression target; native BioSemi external channel. EXG2-EXG4 also available as alternative targets. |
- **Evidence**:
  - BioSemi ActiveTwo system with 64-channel Easycap and external EXG channels (EXG1-EXG8) — EXG1-EXG4 are continuous non-EEG channels suitable for EOG monitoring
  - channels.tsv and eeg.json confirm EXG1-EXG4 are native misc channels on the raw recordings
- **Notes**: This is a native misc channel regression task (archetype B1). EXG1 serves as the primary regression target representing EOG activity; epochs are aligned to trial phase onsets (fixation, poem, contemplation, rating) for concurrent EEG-EOG analysis. The epoch window [-0.2, 1.0] s captures pre-stimulus baseline and early EOG response. EXG2-EXG4 provide additional EOG derivations if needed. No kernel derivation is required as EXG1 is a native continuous channel.

---

### Potential Task 3: EXG7-8 EMG/regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`65282`]
- **Label Route**: `misc`
- **Label Field**: `EXG7`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | EXG7 | Continuous voltage (µV) regression target; native BioSemi external channel likely EMG or auxiliary physiological signal. EXG8 also available as alternative target. |
- **Evidence**:
- **Notes**: This task uses native continuous misc channel EXG7 as a regression target, epoched around poem presentation onset (65282). The epoch window [-0.2, 1.0] s captures pre-stimulus baseline and early post-stimulus peripheral physiological response. EXG8 is also available as an alternative or supplementary channel. The target is the continuous voltage signal itself, making this a direct physiological regression task rather than a derived feature. For multi-target regression, EXG8 could be added; single-channel regression uses EXG7 as the primary target due to its first listing in kernel_needs.

---

### Potential Task 4: Subject Identification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `participant_original_id`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | participant_original_id | 47-class subject identification (y=0..46) mapping P101-P147 from participants.tsv. Needs verification: exact ID range and sequential ordering should be confirmed against actual participants.tsv. |
- **Evidence**:
  - participants.tsv — Maps 47 subjects (sub-001 to sub-047) to original participant IDs P101-P151, providing complete subject labels for brainprint identification
  - README — Confirms 47 participants with continuous EEG recordings in this dataset; original IDs preserved in participants.tsv
- **Notes**: Segmentation-based subject identification task using 10-second overlapping windows (50% overlap, SKILL default) from continuous EEG. The 47-class classification uses native participant_original_id from participants.tsv (info route, Meta=raw). All 47 original IDs (P101-P147 contiguous) are mapped to sequential y=0..46. No event structure is used for segmentation; this is a pure "brainprint" paradigm where subject identity is inferred from spontaneous/continuous EEG characteristics. The asterisks indicate inferred parameters from SKILL defaults due to absent epoch hints in the source data.

---

### Potential Task 5: 2-class contemplation vs rating phase
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`65283`, `65284`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65283 | 0 | poem contemplation onset |
  | 65284 | 1 | poem rating onset |
- **Evidence**:
  - task-readpoetry_events.json — "x65283": "Poem contemplation onset  ", "x65284": "Poem rating onset  "
  - events.tsv samples — confirmed trigger values 65283 and 65284 appear in actual data with ~9964 occurrences each
  - README — describes trial structure with contemplation and rating as distinct consecutive phases in poetry evaluation task
- **Notes**: This task contrasts two adjacent cognitive phases within each trial: passive aesthetic contemplation (receptive processing) versus active evaluative judgment (rating). Both are task-relevant cognitive states. The epoch parameters are inferred from the primary task structure, using a short pre-stimulus baseline (-0.2s) and 1.0s post-onset window to capture phase-specific neural signatures before the next phase begins. The approximately equal occurrence counts (~9964 each) support balanced classification.

---

### Potential Task 6: 2-class fixation vs poem presentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`65281`, `65282`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65281 | 0 | fixation cross |
  | 65282 | 1 | poem presentation |
- **Evidence**:
  - task-readpoetry_events.json — "x65281": "Fixation cross onset", "x65282": "Poem onset  "
  - sub-001_task-readpoetry_events.tsv — actual trigger values 65281 and 65282 observed in data
  - EEG file header — annotations confirm events 65281 and 65282 are present in recordings
- **Notes**: Standard ERP-style contrast between neutral fixation baseline and meaningful linguistic stimulus onset. Both events occur ~9964 times each, providing balanced classes. The epoch window (-0.2 to 1.0 s) captures the visual evoked potential and early attentional modulation following fixation-to-poem transition.

## Data Quality Notes

- `age` and `sex` fields are missing from dataset metadata.
- `device` field is missing from dataset metadata; equipment inferred from README and data descriptor as BioSemi ActiveTwo.
- Events 65285-65288 and 65280 are rare events with severe class imbalance relative to main task events; consider exclusion or special handling in classification.
- Events 65287 and 65288 (resting state 2 onset/end) are defined in event metadata but not observed in actual recordings.
- EXG1-EXG4 and EXG7-EXG8 channels require role verification; native misc channels may contain EOG, EMG, or other auxiliary signals.
- Text type classification (Classical Task 2) requires external metadata lookup from events.tsv columns (trial_type or stim_file) to resolve many-to-one event-to-label mapping.
- No known data quality issues with the continuous EEG recordings or main task event structure.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
