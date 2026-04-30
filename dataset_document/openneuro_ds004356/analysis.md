# Subcortical responses to music and speech are alike while cortical responses diverge

**Dataset**: `openneuro_ds004356` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004356
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 24 | **Manual Review**:
**Channels**: 34 | **Sampling Rate**: 10000 Hz

## Paradigm

The study measures subcortical Auditory Brainstem Responses (ABR) and cortical auditory evoked potentials to continuous music and speech stimuli using a deconvolution method. Participants passively listened to different audio categories while continuous EEG was recorded at 10,000 Hz from 34 channels. The paradigm compares neural encoding of music versus speech at both subcortical and cortical levels, with click trains serving as a control condition for ABR baseline measurement.

## File Scan Result

> **Kernel SHA256**: `5c95da9f7885cfea812f8e9ae73c60a937cea95a8f3a1e8669e6afc53d8ab476`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 12733 | event | raw | Stimulus onset: acoustic music |
| `Stimulus/S  2` | 10771 | event | raw | Stimulus onset: classical music |
| `Stimulus/S  4` | 69798 | event | raw | Stimulus onset: jazz music |
| `Stimulus/S  8` | 51688 | event | raw | Stimulus onset: English audio book speech |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Music vs Speech Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 12 s, overlap = 0.0, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  4`, `Stimulus/S  8`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | acoustic music |
  | `Stimulus/S  2` | 0 | classical music |
  | `Stimulus/S  4` | 0 | jazz music |
  | `Stimulus/S  8` | 1 | English audio book speech |
- **Evidence**:
  - 10.1038/s41598-023-50438-0 — Published paper explicitly describes binary classification of music vs speech from continuous 12-second stimulus blocks, with three music genres mapped to one class and English audiobook speech to the other.
  - 10.1101/2022.10.14.512309 — Preprint confirms experimental design: 12-second continuous stimulus blocks with tmin=0s, tmax=12s, no overlap, and binary music vs speech classification paradigm.
- **Notes**: All three music genres (acoustic, classical, jazz) are merged into y=0 (music class) and English audiobook speech is y=1 (speech class), reflecting the binary music vs speech classification described in the source papers. The event IDs use binary-coded trigger values (1, 2, 4, 8) as documented in the dataset's events.json sidecar.

### Potential Task 1: Music Genre 3-Class Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 12 s *, overlap = 0.0 *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | acoustic music |
  | `Stimulus/S  2` | 1 | classical music |
  | `Stimulus/S  4` | 2 | jazz music |
- **Evidence**:
  - task-MusicvsSpeech_events.json — Documents trial_type Levels: '1': 'acoustic', '2': 'classical', '4': 'jazz', with value field clarifying 'acoustic music', 'classical music', 'jazz music'
  - README — Describes 12-second stimulus clips from six music genres and six speech types, 40 trials each
  - sub-01_task-MusicvsSpeech_events.tsv — Shows consistent 12-second duration for music/speech trials with stim_file entries (e.g., 'acoustic/acoustic000.wav', 'classical/classical002.wav', 'jazz/jazz025.wav')
- **Notes**: Three music genres (acoustic, classical, jazz) selected from the broader 12-type stimulus set to form a balanced 3-class classification task. Each genre has 40 trials of 12-second continuous stimulation. Event IDs use binary-coded trigger values (1, 2, 4) corresponding to bits in the trial encoding scheme. Epoch timing inferred from stimulus duration; no explicit genre-classification paradigm found in literature, but event structure fully supports this potential task.

### Potential Task 2: age regression from auditory responses
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 19–37 (years) | Subject chronological age from participants.tsv; N=22 complete |
- **Evidence**:
- **Notes**: Continuous auditory stimulation paradigm with 12-second music/speech trials. Segmentation uses 12-second windows with 50% overlap to match stimulus block duration, providing dense coverage of auditory-evoked responses for age-related regression analysis.

### Potential Task 3: Musical Training Years Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `musical_training_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | musical_training_years | 0 – 14 (years) | Self-reported years of musical training; complete data across all 22 subjects |
- **Evidence**:
  - participants.tsv — `musical_training_years` column with complete data (range 0–14 years)
  - Shan et al. (2024) Sci Rep 14, 789 — dataset publication describing musical expertise modulation of neural responses
- **Notes**: Continuous auditory segmentation into 12-second epochs matching stimulus clip duration with 50% overlap. The regression target is a native participants.tsv column requiring no kernel derivation. The 12-second segment length aligns with the music/speech stimulus block duration described in the README and task-MusicvsSpeech_events.json.

### Potential Task 4: Formal Musical Training Years Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `formal_musical_training_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | formal_musical_training_years | 0 – 11 (years) | Complete data for all 22 subjects; distinct from total musical_training_years, capturing structured conservatory/instruction effects |
- **Evidence**:
- **Notes**: Segmentation-based regression task using 12-second epochs with 50% overlap to cover the continuous auditory stimulation period. The formal_musical_training_years variable (0–11 years, complete) is drawn directly from participants.tsv as a native info field. This targets neural plasticity effects specifically from structured musical instruction rather than informal practice. The 12-second segment length matches the stimulus clip duration described in the README (phase 2: 12 s stimuli clips, 40 trials per type, 0.5 s inter-trial pause).

### Potential Task 5: Tonal Language Speaker Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 12 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `tonal_language_speaker`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | `tonal_language_speaker` | `No` | 0 | non-tonal language speaker |
  | `tonal_language_speaker` | `Yes` | 1 | tonal language speaker |
- **Evidence**:
- **Notes**: Continuous auditory segmentation task using 12-second epochs with 50% overlap, matching the stimulus clip duration from the MusicvsSpeech paradigm. The binary classification leverages participants' tonal language background as a natural grouping variable to investigate potential differences in pitch encoding mechanisms during auditory processing. All 22 subjects have complete data for this field.

### Potential Task 6: Gender Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 12 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | Female | 0 | Female subject |
  | gender | Male | 1 | Male subject |
- **Evidence**:
- **Notes**: Continuous auditory EEG segmentation task. 12-second segments match the stimulus clip duration from the second phase of the experiment (music and speech trials). Gender is a native participants.tsv column with complete data across all 22 subjects (11 Female, 11 Male), providing balanced binary classification labels. The task leverages the continuous recording nature of the EEG data, segmenting into non-overlapping or overlapping windows to predict subject gender from brain activity patterns during auditory stimulation. The 50% overlap provides increased sample coverage for model training.

### Potential Task 7: Left Ear Hearing Threshold Regression (500 Hz)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `L_500`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | L_500 | -5 to 15 (dB HL) | Left ear hearing threshold at 500 Hz; complete across all 22 subjects. Lower values indicate better hearing sensitivity. |
- **Evidence**:
- **Notes**: Continuous auditory EEG segmentation into 12-second epochs matching stimulus block duration. The L_500 audiometric threshold is drawn from participants.tsv as a subject-level covariate. This task tests whether ABR-derived EEG features during continuous music/speech listening predict peripheral hearing sensitivity, with the hypothesis that subjects with elevated thresholds (poorer hearing) may exhibit reduced subcortical response amplitudes or altered latencies. Segmentation approach used since the paradigm involves continuous stimulation without discrete trial boundaries suitable for event-based epoching.

### Potential Task 8: Right Ear Hearing Threshold Regression (500 Hz)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 12 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `R_500`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | R_500 | 0 to 20 (dB HL) | Right ear hearing threshold at 500 Hz; complete across all 22 subjects |
- **Evidence**:
- **Notes**: Continuous auditory EEG segmentation into 12-second non-overlapping windows matching stimulus clip duration with 50% overlap for coverage. The R_500 hearing threshold from participants.tsv serves as the regression target, testing whether subcortical/cortical EEG responses to continuous music and speech predict individual hearing sensitivity. Derived from archetype B3 with native info field.

### Potential Task 9: Musical Training Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `musical_training_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | musical_training_years | 0 | 0 | untrained (0 years) |
  | musical_training_years | >0 | 1 | trained (>0 years) |
- **Evidence**:
- **Notes**: Binary classification derived from continuous auditory EEG during music and speech stimulation. The 12-second segmentation matches the stimulus block duration for the second phase of the experiment (music/speech trials). Subjects with any musical training (musical_training_years > 0) are labeled y=1, while those with no training (musical_training_years = 0) are labeled y=0. From participants.tsv: 13 subjects have some training, 9 have none. This task tests whether continuous EEG responses to auditory stimuli differ between musically trained and untrained individuals.

### Potential Task 10: Formal Musical Training Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `formal_musical_training_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | formal_musical_training_years | 0 | 0 | No formal musical training |
  | formal_musical_training_years | >0 | 1 | Has formal musical training |
- **Evidence**:
  - participants.tsv — Column `formal_musical_training_years` (dtype=numeric, complete, sample=[11, 0, 6]) provides per-subject formal training years; 0 indicates no training, >0 indicates trained
  - README — "There were two phases in this experiment... twelve types of 12 s stimuli clips were presented" confirming 12-second stimulus blocks for segmentation alignment
  - Shan et al. (2024) Sci Rep 14, 789 — Dataset publication describing continuous auditory EEG paradigm with music and speech stimuli
- **Notes**: B3 archetype using native participants.tsv column. The binary classification is derived by thresholding `formal_musical_training_years` at 0 (untrained vs trained). Segment length of 12 s matches the stimulus block duration described in the README for phase 2 of the experiment. The 50% overlap provides sufficient coverage for subject-level classification from continuous EEG. Values marked with * are inferred from epoch_hint with no explicit tmin/tmax for segmentation method.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
