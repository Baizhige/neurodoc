# Auditory and Visual Rhythm Omission EEG

**Dataset**: `openneuro_ds002218` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002218
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 32 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Participants passively perceived rhythmic auditory tone sequences and visual flashing stimuli that occasionally omitted an expected beat, to study predictive neural activity (mismatch responses) versus sensory evoked responses. The paradigm investigates how the brain generates predictions based on temporal regularities and detects violations of expected rhythmic patterns. Event markers distinguish between omission and non-omission conditions within both auditory and visual modalities, enabling analysis of omission-specific neural responses. The dataset contains 32-channel EEG recorded at 256 Hz using a BioSemi system.

## File Scan Result

> **Kernel SHA256**: `c321e8c16ce2439b0d7cb2735e681c043b1173f0cbf10ec93ceac6c3b3b78eb9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0, Impedance` | 16 | admin | raw | System marker: impedance check |
| `1` | 33483 | event | raw | Stimulus onset: visual flash during visual omission condition |
| `2` | 2520 | event | raw | Stimulus onset: omitted flash during visual omission condition |
| `3` | 33480 | event | raw | Stimulus onset: auditory tone during auditory omission condition |
| `4` | 2520 | event | raw | Stimulus onset: omitted tone during auditory omission condition |
| `5` | 2520 | event | raw | Stimulus onset: visual flash during visual non-omission/control condition |
| `6` | 2520 | event | raw | Stimulus onset: auditory tone during auditory non-omission/control condition |
| `__` | 2 | admin | raw | Undefined system marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 4-class auditory/visual rhythm omission
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.67 s, tmax = 1.67 s, target_events = ['2', '4', '5', '6']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `2` | 0 | Omitted flash during visual omission condition |
  | `4` | 1 | Omitted tone during auditory omission condition |
  | `5` | 2 | Visual flash during visual non-omission/control condition |
  | `6` | 3 | Auditory tone during auditory non-omission/control condition |
- **Evidence**:
  - 10.1111/ejn.15314 — Four-class classification of auditory and visual rhythm omission trials with epoch window -1.67s to +1.67s around stimulus onset; 2520 trials per class; beta band time-frequency analysis of predictive timing mechanisms
  - 10.1101/2020.11.29.402701 — Same paradigm and epoch parameters confirming event codes 2, 4, 5, 6 for omission and non-omission conditions in both modalities
- **Notes**: Event meanings confirmed by task-Experiment_events.json. The 4-class structure contrasts omission vs. non-omission within each modality (visual/auditory). Event codes 1 and 3 (present stimuli during omission conditions) are excluded as they represent the predictable rhythmic continuation rather than the critical omission/non-omission contrast. The balanced trial count (2520 per class) supports robust classification.

### Classical Task 2: 2-class auditory omission vs non-omission
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.67 s, tmax = 1.67 s, target_events = [`3`, `4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 3 | 0 | auditory tone during auditory omission condition (non-omission) |
  | 4 | 1 | omitted tone during auditory omission condition (omission) |
- **Evidence**:
  - 10.1111/ejn.15314 — Published analyses compare auditory omission and non-omission conditions for beta band induced and evoked activity differences reflecting predictive timing mechanisms
  - 10.1101/2020.11.29.402701 — Binary classification of auditory rhythm trials: non-omission (event 3) versus omission (event 4), 2520 trials each condition
  - task-Experiment_events.json — Event codes 3 and 4 defined as "Auditory tone during auditory omission condition" and "Omitted tone during auditory omission condition"
- **Notes**: The candidate's evidence summary incorrectly mapped event 2 as y=0 and event 4 as y=1; however, the EVENT MEANINGS locked ground truth clarifies that event 2 is "omitted flash during visual omission condition" (visual modality), not auditory. For the auditory omission vs non-omission comparison, the correct events are 3 (auditory tone present, y=0) and 4 (auditory tone omitted, y=1). Both have 2520 trials each. The epoch window [-1.67, 1.67] s is taken from the candidate's epoch_hint (inferred=false) matching the published analysis window for auditory condition comparisons.

### Potential Task 1: 2-class omission condition present vs absent
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.67 s *, tmax = 1.67 s *, target_events = [`1`, `2`, `3`, `4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 1 | 0 | Present stimulus: visual flash during visual omission condition |
  | 3 | 0 | Present stimulus: auditory tone during auditory omission condition |
  | 2 | 1 | Omitted stimulus: omitted flash during visual omission condition |
  | 4 | 1 | Omitted stimulus: omitted tone during auditory omission condition |
- **Evidence**:
  - task-Experiment_events.json — Event codes 1-4 define present/omitted stimuli in omission conditions; codes 1/3 = present, 2/4 = omitted
  - events.tsv samples (sub-001, sub-002) — Confirmed occurrence of events 1-6 in actual recordings
  - README — Describes omission paradigm with auditory and visual rhythms containing occasional omissions
- **Notes**: Binary classification collapsing across modality: present stimuli (events 1 and 3, y=0) versus omitted stimuli (events 2 and 4, y=1). Severe class imbalance (~13:1 present:omitted) noted; would require subsampling or balanced batch sampling. tmin/tmax inferred from classical paradigm window structure.

## Data Quality Notes

- Subject age and sex metadata are completely missing from the dataset.
- Recording device information is missing from the metadata.
- High-count events (1: 33483, 3: 33480) represent present stimuli during omission conditions and are not trial markers but rather ongoing rhythmic stimuli; these are excluded from classical tasks due to severe class imbalance against omission events.
- Two undefined system markers (`__`) were detected in the recordings.
- Event ID meanings were confirmed via task-Experiment_events.json, resolving prior ambiguity in the draft analysis about whether events 1/3 were BioSemi STATUS hardware markers.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
