# EEG Dataset for the Study of Attention and Expectation

**Dataset**: `ds002578` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Two healthy adults (1 female, 1 male, both age 30) performed a visual spatial oddball task with selective attention. Participants attended to one of five horizontally arranged boxes and pressed a button when a disc appeared in the attended box (unexpected oddball target), while ignoring discs in non-attended boxes (expected distractors). EEG was recorded using a BioSemi ActiveTwo 256-channel system at 512 Hz. The experiment manipulated both spatial attention (which box to attend) and expectation (disc location relative to attended location), with event codes 31-45 encoding all combinations of attended box and disc position.

## File Scan Result

> **Kernel SHA256**: `68ddb2d2f301427f52658a4712872ea184d34b62eb4e090604798c7c2e200ba8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `203` | 1 | admin | raw | Spurious presentation software marker removed during preprocessing |
| `217` | 2 | admin | raw | Spurious presentation software marker removed during preprocessing |
| `237` | 1 | admin | raw | Spurious presentation software marker removed during preprocessing |
| `31` | 240 | event | raw | Trial phase onset: stimulus presentation with highlighted box 3, disc in box 1 (Attend-to X-Position/3, Cue X-Position/1, Expected, Distractor) |
| `33` | 240 | event | raw | Trial phase onset: stimulus presentation with highlighted box 3, disc in box 3 (Attend-to X-Position/3, Cue X-Position/3, Unexpected, Oddball, Target) |
| `34` | 239 | event | raw | Trial phase onset: stimulus presentation with highlighted box 3, disc in box 4 (Attend-to X-Position/3, Cue X-Position/4, Expected, Distractor) |
| `35` | 240 | event | raw | Trial phase onset: stimulus presentation with highlighted box 3, disc in box 5 (Attend-to X-Position/3, Cue X-Position/5, Expected, Distractor) |
| `41` | 238 | event | raw | Trial phase onset: stimulus presentation with highlighted box 4, disc in box 1 (Attend-to X-Position/4, Cue X-Position/1, Expected, Distractor) |
| `42` | 239 | event | raw | Trial phase onset: stimulus presentation with highlighted box 4, disc in box 2 (Attend-to X-Position/4, Cue X-Position/2, Expected, Distractor) |
| `43` | 240 | event | raw | Trial phase onset: stimulus presentation with highlighted box 4, disc in box 3 (Attend-to X-Position/4, Cue X-Position/3, Expected, Distractor) |
| `44` | 239 | event | raw | Trial phase onset: stimulus presentation with highlighted box 4, disc in box 4 (Attend-to X-Position/4, Cue X-Position/4, Unexpected, Oddball, Target) |
| `45` | 239 | event | raw | Trial phase onset: stimulus presentation with highlighted box 4, disc in box 5 (Attend-to X-Position/4, Cue X-Position/5, Expected, Distractor) |
| `Picture` | 5939 | event | raw | Trial phase onset: stimulus presentation (experimental stimulus, drawing onset) |
| `Response` | 1202 | event | raw | Participant response: keyboard key press |
| `boundary` | 58 | admin | raw | Trial phase onset: pause/discontinuity between blocks |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Age available in participants.tsv (30 for sub-001 and sub-002) |
| `amplifier` | missing | ManufacturersModelName: ActiveTwo (BioSemi) |
| `cap` | missing | 256-channel system; electrode positions scanned (from README) |
| `handedness` | missing |  |
| `sex` | missing | Gender available in participants.tsv (F/M); note column header is 'gender' not 'sex' |

## Tasks

### Classical Task 1: Visual Oddball Target vs Distractor (Attend-3)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`33`, `31`, `34`, `35`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `33` | 1 | Target: Attend-to box 3, disc in box 3 (Unexpected, Oddball) |
  | `31` | 0 | Distractor: Attend-to box 3, disc in box 1 (Expected, Distractor) |
  | `34` | 0 | Distractor: Attend-to box 3, disc in box 4 (Expected, Distractor) |
  | `35` | 0 | Distractor: Attend-to box 3, disc in box 5 (Expected, Distractor) |
- **Evidence**:
  - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6673364/ — Visual oddball paradigm with selective attention to one of five boxes; target detection requires button press when disc appears in attended box
  - 10.18112/openneuro.ds002578.v1.1.0 — BIDS dataset with HED-tagged event codes 31-45 defining Attend-to/Cue positions; codes 31,34,35,33 confirmed for Attend-3 condition
- **Notes**: Event codes 31-45 appear in raw EEG annotations but were cleaned from processed events.tsv by clean_events.m. The kernel must extract these numeric codes from the raw annotation channel. The `Picture` events in processed data are generic stimulus onsets that replaced condition-specific codes. Target (y=1) is code 33 (disc in attended box 3); distractors (y=0) are codes 31, 34, 35 (disc in non-attended boxes 1, 4, 5 while attending box 3).

### Potential Task 1: Visual Oddball 5-Class Spatial Cue Position (Attend-4)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = ['41', '42', '43', '44', '45']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `41` | 0 | Disc in box 1, highlighted box 4 (Attend-4, Expected Distractor) |
  | `42` | 1 | Disc in box 2, highlighted box 4 (Attend-4, Expected Distractor) |
  | `43` | 2 | Disc in box 3, highlighted box 4 (Attend-4, Expected Distractor) |
  | `44` | 3 | Disc in box 4, highlighted box 4 (Attend-4, Unexpected Oddball Target) |
  | `45` | 4 | Disc in box 5, highlighted box 4 (Attend-4, Expected Distractor) |
- **Evidence**:
  - sub-001_task-attention_events.json / sub-002_task-attention_events.json — HED tags and Levels define codes 41-45 as Attend-to box 4 with disc positions 1-5; code 44 is designated Target/Oddball/Unexpected, codes 41-43 and 45 are Expected Distractors
  - EEG file header samples — Raw annotations contain event codes '41', '42', '43', '44', '45' confirming these trigger values exist in the raw data
  - README — References clean_events.m preprocessing that removes spurious markers but preserves condition-specific codes in raw data; processed events.tsv replaces them with generic 'Picture' events
- **Notes**: This is a 5-class spatial cue discrimination task where participants attend to box 4 and respond when the disc appears in that box (code 44, y=3, oddball target). The other four positions (codes 41-43, 45) are expected distractors. Epoch window inferred from the Attend-3 condition for direct comparability across attention conditions. The task uses raw event annotations since the processed events.tsv only contains generic 'Picture' events without condition-specific information.

### Potential Task 2: Expected vs Unexpected Stimulus (Attend-3)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = ['33', '31', '34', '35']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `33` | 1 | Unexpected — disc in attended box 3 (oddball/target) |
  | `31` | 0 | Expected — disc in non-attended box 1 (distractor) |
  | `34` | 0 | Expected — disc in non-attended box 4 (distractor) |
  | `35` | 0 | Expected — disc in non-attended box 5 (distractor) |
- **Evidence**:
  - `events.json` (sub-001, sub-002) — HED tags and Levels define codes 31-35 as combinations of highlighted box (Attend-to position) and disc position (Cue position), with 33 being Unexpected/Oddball/Target when disc matches attended box 3, and 31/34/35 being Expected/Distractor when disc is in non-attended boxes
  - `README` — describes `clean_events.m` removing spurious markers, confirming numeric codes 31-45 are the cleaned condition-specific trial markers underlying the generic `Picture` events in processed data
- **Notes**: This task isolates the neural signature of prediction error by contrasting physically identical stimulus presentations (disc in box 3, highlighted box 3) that differ only in expectation: code 33 is unexpected because the disc appears in the attended location, while codes 31/34/35 are expected distractors in non-attended locations during Attend-3 blocks. The y=0 class merges three expected distractor types to balance against ~240 unexpected trials. Epoch window centered on stimulus onset captures mismatch negativity and early P300 components associated with expectation violation.

### Potential Task 3: Stimulus Onset vs Response Onset
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Picture`, `Response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Picture | 0 | Stimulus onset: trial phase onset for visual stimulus presentation (experimental drawing onset) |
  | Response | 1 | Response onset: participant keyboard key press |
- **Evidence**:
  - events.tsv (sub-001, sub-002) — processed data contains `Picture` (5939 occurrences) and `Response` (1202 occurrences) as sole event types besides `boundary`; numeric condition codes cleaned during preprocessing
  - sub-001_task-attention_events.json / sub-002_task-attention_events.json — HED tags confirm `Picture` = stimulus presentation onset, `Response` = keyboard key press; `value` column maps to trial_type with stimulus/response semantics
  - README — describes `clean_events.m` removing spurious markers, leaving only canonical `Picture` and `Response` events in processed data
- **Notes**: Classification distinguishes sensory-evoked (stimulus-locked) from motor-related (response-locked) neural activity. Both classes are time-locked to behaviorally relevant events with sufficient trial counts for ERP-based decoding. The `Picture` event replaces condition-specific numeric codes (31-45, x11-x55) after preprocessing, making it a generic stimulus onset marker across all trial types.

### Potential Task 4: Gender Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | `gender` | F → 0, M → 1 |
- **Evidence**:
- **Notes**: Segmentation-based subject-level decoding. Continuous EEG is sliced into 2-second half-overlapping segments; each segment inherits the participant's gender label from participants.tsv. Extremely small sample (N=2, 1F/1M) renders this exploratory only. All segments from a given subject share the same label, creating a subject-stratified classification problem.

### Potential Task 5: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | age | Continuous chronological age in years; value = 30 for all subjects in this dataset (zero variance, degenerate regression) |
- **Evidence**:
- **Notes**: Segmentation-based epochs (2 s, 50% overlap) from continuous EEG with subject-level age label from participants.tsv. Degenerate task: N=2 subjects both age=30, resulting in zero label variance. Mathematically impossible for regression; included for completeness but will be filtered by downstream degeneracy checks. No kernel derivation needed — age is a native participants.tsv column.

## Data Quality Notes

- Extremely small sample size (N=2 subjects) severely limits generalizability and statistical power for all tasks.
- Condition-specific event codes (31-45) were removed from processed events.tsv by clean_events.m; these must be extracted from raw annotation channels, creating a dependency on raw data access.
- Processed events.tsv contains only generic 'Picture' and 'Response' events, losing trial condition information critical for most cognitive analyses.
- Age field has zero variance (all subjects age 30), making age regression mathematically degenerate.
- Gender classification with N=2 (1F/1M) is severely underpowered and risks perfect separation artifacts.
- Spurious presentation software markers (codes 203, 217, 237) present in raw data but marked as removed during preprocessing; verify they do not contaminate extracted epochs.
- Electrode positions were scanned per README but cap field is missing from info metadata; 256-channel montage requires careful handling for standard analyses.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
