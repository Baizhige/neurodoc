# Visual Hemifield RSVP Object Recognition Dataset

**Dataset**: openneuro_ds005087 | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005087
**Category**: EEG | **Subjects**: 80 | **Files (Completed)**: 80 | **Channels**: 63 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants viewed object and word stimuli presented at 5 Hz in rapid visual streams (RSVP) while performing a visual detection task. The dataset was collected to study dynamics of visual object coding within and across the hemispheres, with stimuli presented to the left hemifield, right hemifield, or both hemifields under different conditions. Event codes E 1 and E 2 mark stimulus ON and OFF markers respectively, alternating every 100 ms to create the 5 Hz presentation rate, while E 3 marks trial phase onset at sequence start.

## File Scan Result

> **Kernel SHA256**: `5e138eb3a207e9d0dcec61de127b7afcbbe8ecb2dd10353e4a650020f8d9d9c6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 184320 | event | raw | Stimulus ON marker |
| `E  2` | 184320 | event | raw | Stimulus OFF marker |
| `E  3` | 960 | event | raw | Trial phase onset: sequence start |
| `Event/E  1` | 184320 | event | raw | Stimulus ON marker |
| `Event/E  2` | 184320 | event | raw | Stimulus OFF marker |
| `Event/E  3` | 960 | event | raw | Trial phase onset: sequence start |
| `boundary` | 20 | admin | raw | Recording segment boundary |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class left vs right hemifield classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = [`E  1`, `E  2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  1` | 0 | Stimulus ON marker (left hemifield trial) |
  | `E  2` | 1 | Stimulus OFF marker (right hemifield trial) |
- **Evidence**:
  - 10.1126/sciadv.adq0889 — Robinson et al. (2025) core contrast for inter-hemispheric dynamics; left vs right hemifield lateralization effects with balanced ~184k events per class
- **Notes**: The event IDs `E  1` and `E  2` are stimulus ON/OFF markers that alternate every 100ms (100 samples at 1000Hz), matching the 100ms stimulus duration and 5Hz presentation rate. The condition labels in events.tsv (left-right, left+right) indicate hemifield presentation; E 1 and E 2 correspond to the two balanced classes for left vs right hemifield classification, with E 3 (sequence start, ~960 events) excluded to address class imbalance as per the published analysis.

### Potential Task 1: Stimulus Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`E  1`]`, `overlap = 0.5 *`
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  1` | 0 | left-only condition |
  | `E  1` | 1 | left-right condition (different objects) |
  | `E  1` | 2 | left+right condition (same object) |
- **Evidence**:
- **Notes**: Archetype B2 derived misc channel converted to event classification. The kernel must read the 'condition' column from events.tsv (values 1, 2, 3 with description '1, 2 or 3' per task-rsvp_events.json) and create a step-function misc channel named 'condition_number' that holds the condition value from stimulus onset (time_stimon) to stimulus offset (time_stimon+stimdur=0.1s) for each trial. However, since this is classification with a discrete label, we route through event IDs by assigning condition-specific event codes during kernel processing, or use the event route with E 1 as the common anchor and condition as the class-determining factor. The condition values encode the spatial configuration of stimulus presentation: 1=left visual field only, 2=left and right visual fields (different objects), 3=left and right visual fields (same object). Epoching locks to E 1 (Stimulus ON marker) to capture the evoked response to the stimulus presentation.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 17–59 (years) | Continuous subject age from participants.tsv; N=20, complete coverage. Each segment inherits the subject's age value. |
- **Evidence**:
- **Notes**: Segmentation-based regression using 2-second non-overlapping windows (50% overlap) of RSVP task EEG to predict subject age. No event structure is used for epoching since age is a subject-level continuous variable. The RSVP paradigm at 5Hz provides sufficient temporal structure for age-related EEG feature extraction. SKILL defaults applied for segmentation parameters due to null epoch_hint values.

### Potential Task 3: Handedness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Handedness | right | 0 | right-handed |
  | Handedness | left | 1 | left-handed |
  | Handedness | ambidextrous | 2 | ambidextrous |
- **Evidence**:
  - participants.tsv — `Handedness` column contains 3 categories: right (majority), left, ambidextrous; N=20 subjects
- **Notes**: Segmentation-based resting-state style task using 2-second non-overlapping segments from continuous EEG (task-rsvp recordings repurposed). Classification target is handedness from participants.tsv. Severely underpowered with only 20 subjects and 3 classes, but technically valid. No kernel derivation needed — Handedness is a native participants.tsv column.

### Potential Task 4: Handedness Inventory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Total`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Total | -20 to 100 (laterality quotient) | Edinburgh Handedness Inventory laterality quotient (R-L)/(R+L)*100 |
- **Evidence**:
- **Notes**: Standard Edinburgh Handedness Inventory laterality quotient computed from R and L scores in participants.tsv. Segmentation applied to resting-state EEG recordings (task-restclosed and task-restopen) which lack task-related event markers. Epoch parameters inferred from SKILL defaults for resting-state segmentation (2s windows, 50% overlap).

### Potential Task 5: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | F | 0 | Female |
  | gender | M | 1 | Male |
- **Evidence**:
  - participants.tsv — gender column with F (15 subjects) and M (5 subjects) values
- **Notes**: Binary classification from resting-state EEG segments using subject-level demographic label. Highly imbalanced (75% female, 25% male) with only 20 total subjects, making this severely underpowered for generalizable gender classification. Segmentation approach required since resting-state recordings (task-restclosed, task-restopen) contain no task-related event markers. SKILL default segment length of 2s with 50% overlap applied.

### Potential Task 6: ESL status classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `ESL`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | ESL | N | 0 | Native English speaker |
  | ESL | Y | 1 | English as Second Language |
- **Evidence**:
- **Notes**: Binary classification of native vs non-native English speaker status from resting-state EEG segments. The 2-second segmentation with 50% overlap is applied to continuous recordings (task-restclosed and/or task-restopen) to create samples. This is a severely underpowered task with only 20 subjects and likely very few Y (ESL) cases. The RSVP task events are not used for epoching since segmentation is employed; however, the paradigm context involves word stimuli presentation which may relate to language processing differences captured in resting-state baseline activity.

### Potential Task 7: Sequence Position Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.6 s *, target_events = [`E  1`]`, `overlap = 0.5 *`
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `E  1` | sequencenumber | Step-function channel derived from events.tsv `sequencenumber`; value held constant from stimulus onset to offset for each presentation |
- **Evidence**:
- **Notes**: Kernel derivation: Read `sequencenumber` column from events.tsv (values 0-11 indicating position within RSVP stream). Create step-function misc channel named `sequence_position` where value=sequencenumber from time_stimon to time_stimon+stimdur (100ms) for each stimulus presentation. Epoch locked to `E  1` (Stimulus ON marker). This captures temporal position effects in rapid serial visual presentation where neural responses vary with sequence position due to attentional blink and repetition suppression effects.

### Potential Task 8: Stream Identity Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`E  1`]`, `overlap = 0.5 *`
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `E  1` | streamnumber | Derived from events.tsv 'streamnumber' column; step-function misc channel holding stream number from stimulus onset to offset for each trial. Regression target treats stream identity as continuous variable to capture stream-specific adaptation/learning effects across 48 streams. |
- **Evidence**:
- **Notes**: Archetype B2 derived misc channel converted to event route. The kernel must read 'streamnumber' from events.tsv (0-47, described as 'unique stream number') and create a step-function misc channel named 'stream_number' with value=streamnumber from time_stimon to time_stimon+stimdur for each trial. The epoch is anchored to stimulus ON markers (E  1) with a [-0.2, 1.0] window to capture pre-stimulus baseline and sustained post-stimulus activity that may carry stream-specific adaptation signatures. Treating 48 streams as a continuous regression target rather than categorical avoids extreme class imbalance and allows modeling of gradual learning/adaptation effects across stream presentation order.

## Data Quality Notes

- `device` field is completely missing from dataset metadata, limiting reproducibility of equipment specifications.
- Event meaning conflict between draft and File Scan Result: draft describes E 1/E 2/E 3 as left/right/center hemifield markers, but File Scan Result identifies E 1 as Stimulus ON, E 2 as Stimulus OFF, and E 3 as sequence start. The Tasks section resolves this by using condition columns from events.tsv for hemifield classification.
- E 3 events are extremely rare (960) compared to E 1/E 2 (~184k each), which matches sequence start markers rather than trial-level events.
- Only 20 subjects have complete demographic data (age, sex, handedness, ESL) despite 80 subjects in the dataset, severely limiting subject-level classification/regression tasks.
- Boundary events (n=20) present and should be excluded during epoch extraction.
- Multiple tasks rely on kernel-derived super meta channels (condition_number, sequence_position, stream_number) requiring events.tsv parsing and misc channel creation.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
