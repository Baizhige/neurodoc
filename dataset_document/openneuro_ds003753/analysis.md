# EEG: Probabilistic Learning with Affective Feedback: Exp #2

**Dataset**: `openneuro_ds003753` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003753
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 66 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A reinforcement learning task involving probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to affective stimulus properties. Participants made binary choices (left/right button) between cue stimuli associated with different reinforcement probabilities and affective categories (puppy vs cow images). Following each choice, feedback was presented indicating win/lose outcomes with associated affective images. The study examines neural responses to reward value, affective valence, and reinforcement probability in a probabilistic learning framework.

## File Scan Result

> **Kernel SHA256**: `907cc31ea39c0a3db7ec13e2d99ccbb532df9b433f3107583144327a7e49d696`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 1000 | event | raw | Trial phase onset: CUE: A - EASY PUPPY |
| `S  2` | 999 | event | raw | Trial phase onset: CUE: B - HARD PUPPY |
| `S  3` | 999 | event | raw | Trial phase onset: CUE: C - EASY COW |
| `S  4` | 999 | event | raw | Trial phase onset: CUE: D - HARD COW |
| `S 10` | 1933 | event | raw | Trial phase onset: feedback (inferred: win/positive outcome) |
| `S 20` | 2064 | event | raw | Trial phase onset: feedback (inferred: lose/negative outcome) |
| `S101` | 1339 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `S102` | 660 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `S103` | 1385 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `S104` | 613 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `S110` | 573 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `S111` | 517 | event | raw | Trial phase onset: STATUS interval marker |
| `S120` | 594 | event | raw | Trial phase onset: task event (specific function unclear from available evidence) |
| `boundary` | 25 | admin | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: feedback outcome win vs lose
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 3.0 s *, target_events = [`S 10`, `S 20`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S 10` | 0 | feedback win/positive outcome |
  | `S 20` | 1 | feedback lose/negative outcome |
- **Evidence**:
  - Dataset README — "The Reward Positivity is sensitive to affective liking" confirms reinforcement learning paradigm with reward-related EEG component (RewP)
  - stimuli folder contents — P_WIN.JPG, P_LOSE.JPG, P_NULL.JPG provide stimulus labels consistent with binary outcome feedback
  - Event counts — S 10 (1933 events) and S 20 (2064 events) have comparable frequencies matching trial-level feedback structure
  - EEG header sample — both S 10 and S 20 appear as annotations in actual recordings, confirming event presence
- **Notes**: Archetype A (event route). Event meanings for S 10 and S 20 are inferred (not directly observed in sidecar columns) based on: (1) stimulus filenames indicating win/lose outcomes, (2) dataset title referencing Reward Positivity which is a feedback-locked ERP component, (3) temporal structure with cues (S 1-S 4) preceding feedback events, and (4) event counts consistent with one feedback per trial. The y=0/1 assignment is arbitrary but consistent; y=0 for win (positive outcome), y=1 for lose (negative outcome).

### Classical Task 2: Cue Stimulus Type Four-Class Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`S  1`, `S  2`, `S  3`, `S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  1` | 0 | CUE: A - EASY PUPPY |
  | `S  2` | 1 | CUE: B - HARD PUPPY |
  | `S  3` | 2 | CUE: C - EASY COW |
  | `S  4` | 3 | CUE: D - HARD COW |
- **Evidence**:
  - events.tsv samples — Direct observation of `S  1`, `S  2`, `S  3`, `S  4` as cue onset triggers with consistent labels across subjects
  - README — Dataset described as probabilistic learning task with affective feedback; cue-based trial structure inherent to paradigm
  - EVENT MEANINGS LOCKED GROUND TRUTH — `S  1`: A-EASY PUPPY, `S  2`: B-HARD PUPPY, `S  3`: C-EASY COW, `S  4`: D-HARD COW (confirmed, scope=all)
- **Notes**: Four-class classification combining reinforcement learning difficulty (easy 90% vs hard 70%) with affective category (puppy vs cow). Epoch timing inferred from cue-locked paradigm structure; decision period expected to be briefer than feedback-locked windows. No explicit reference analyzes cue-locked classification, but task design inherently supports this prediction target.

### Classical Task 3: Cue Valence Positive vs Negative
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`S  1`, `S  2`, `S  3`, `S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | S  1 | 0 | positive valence cue (easy puppy) |
  | S  2 | 0 | positive valence cue (hard puppy) |
  | S  3 | 1 | negative valence cue (easy cow) |
  | S  4 | 1 | negative valence cue (hard cow) |
- **Evidence**:
  - events.tsv sample — S 1-S 4 observed as cue onset markers with stimulus labels A-EASY PUPPY, B-HARD PUPPY, C-EASY COW, D-HARD COW across 13 subjects
  - dataset_description.json — dataset title "EEG: Probabilistic Learning with Affective Feedback: Exp #2" confirms affective paradigm with positive/negative feedback
  - README — describes RL task with affective feedback, paper title references "Reward Positivity" and "affective liking"
- **Notes**: Merges easy/hard difficulty levels within each valence category to create a cleaner binary affective contrast (positive: puppy images S 1+S 2, n=1999; negative: cow images S 3+S 4, n=1998). Both event types are trial phase onset markers for cue presentation, confirmed from events.tsv sidecar data.

### Classical Task 4: Cue Difficulty Easy vs Hard
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`S  1`, `S  2`, `S  3`, `S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `S  1` | 0 | easy cue (A - EASY PUPPY, 90% reinforcement) |
  | `S  3` | 0 | easy cue (C - EASY COW, 90% reinforcement) |
  | `S  2` | 1 | hard cue (B - HARD PUPPY, 70% reinforcement) |
  | `S  4` | 1 | hard cue (D - HARD COW, 70% reinforcement) |
- **Evidence**:
  - events.tsv samples and events.json — trigger codes S 1-S 4 observed with consistent stimulus labels across all 13 subjects
  - README — confirms RL probabilistic learning task with differential reinforcement probabilities
  - dataset_description.json — "EEG: Probabilistic Learning with Affective Feedback: Exp #2"
- **Notes**: Binary classification collapsing across stimulus valence (puppy vs cow) and merging easy cues (S 1 + S 3, both 90% reinforcement) vs hard cues (S 2 + S 4, both 70% reinforcement). Tests neural sensitivity to reinforcement probability independent of affective content. Epoch parameters inferred from typical cue-locked decision period duration.

### Potential Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–27.0 (years) | Subject chronological age from participants.tsv; N=25, continuous predictor of EEG patterns |
- **Evidence**:
  - participants.tsv — age column present and complete for all 25 subjects, range 18–27 years
  - dataset_description.json — confirms N=25 college-age participants for probabilistic learning with affective feedback study
  - README — describes "N=25 college age participants" collected circa 2019 at UNM
- **Notes**: Archetype B3 (native info field). Age is directly available from participants.tsv without any kernel derivation. Segmentation approach used since no discriminating event structure is required for this continuous regression target; 2-second segments with 50% overlap provide sufficient samples for age prediction from resting/continuous EEG dynamics while maintaining statistical power across the ~25-minute recordings.

### Potential Task 2: Subject Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Continuous EEG segmented into 2-second windows with 50% overlap for subject-level sex classification. Labels drawn from participants.tsv 'sex' column (F=19, M=6). Highly imbalanced class distribution (19:6) but technically valid with two distinct classes. Segmentation parameters inferred from Category SKILL defaults for continuous EEG classification tasks.

## Data Quality Notes

- Event meanings for S101-S120 are unclear from available evidence; these event IDs appear in recordings but their specific functional roles in the trial structure are not documented in sidecar files or README.
- `device` field is missing from info metadata, limiting hardware documentation for reproducibility.
- Boundary events (25 total, one per subject) indicate segmented recordings; continuous data processing should exclude these markers.
- Event counts for S 10 (1933) and S 20 (2064) sum to 3997, slightly exceeding the expected ~4000 trials (1000+999+999+999 cues), suggesting possible extra events or miscounts in feedback presentation.
- S110 and S111 event counts (573+517=1090) do not sum to total cue events (~3997), indicating response recording may be incomplete or filtered.
- Sex classification task has highly imbalanced classes (19 F vs 6 M), which may limit model performance and generalizability.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
