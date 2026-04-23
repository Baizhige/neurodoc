# Features-EEG

**Dataset**: `openneuro_ds004357` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004357
**Category**: Sensory/Response | **Subjects**: 16 | **Files (Completed)**: 16 | **Channels**: 127 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of Gabor-like stimuli at two presentation rates: 6.67 Hz (slow condition, 150 ms SOA) and 20 Hz (fast condition, 50 ms SOA). While maintaining fixation, participants performed an orthogonal color change detection task at the fixation point. Stimulus streams varied along four visual feature dimensions: orientation, contrast, spatial frequency, and color. EEG was recorded with 127 channels at 1000 Hz sampling rate to investigate how these visual features are dynamically encoded in neural responses.

## File Scan Result

> **Kernel SHA256**: `14f7646bb8ae9bb8b23fdb5dd31c76aa78f8ade2c82e5b066c8c4627fdadbfd5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E  1` | 322780 | event | raw | Stimulus onset: RSVP trial with speedcondition=0 (slow/6.67Hz presentation rate, soaduration=0.15s) |
| `Event/E  2` | 322781 | event | raw | Stimulus onset: RSVP trial with speedcondition=1 (fast/20Hz presentation rate, soaduration=0.05s) |
| `Event/E  3` | 1260 | event | raw | Target event: fixation color change detection trial (istarget=True) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 4-way spatial frequency classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E  1`, `Event/E  2`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0 | spatial frequency 0.01 cyc/deg (f_sf=0) |
  | `Event/E  1` | 1 | spatial frequency 0.025 cyc/deg (f_sf=1) |
  | `Event/E  1` | 2 | spatial frequency 0.04 cyc/deg (f_sf=2) |
  | `Event/E  1` | 3 | spatial frequency 0.055 cyc/deg (f_sf=3) |
  | `Event/E  2` | 0 | spatial frequency 0.01 cyc/deg (f_sf=0) |
  | `Event/E  2` | 1 | spatial frequency 0.025 cyc/deg (f_sf=1) |
  | `Event/E  2` | 2 | spatial frequency 0.04 cyc/deg (f_sf=2) |
  | `Event/E  2` | 3 | spatial frequency 0.055 cyc/deg (f_sf=3) |
- **Evidence**:
  - 10.1371/journal.pcbi.1011760 — Classical 4-way spatial frequency classification; f_sf column has 4 levels (0-3) mapped to 0.01, 0.025, 0.04, 0.055 cyc/deg; time-resolved decoding from -0.1 to 0.6s post-stimulus
  - 10.1038/s41598-025-27703-5 — Confirms 4-way classifier for spatial frequency dimension with same epoch window
- **Notes**: The kernel must derive `spatial_frequency_label` from events.tsv:f_sf (Description: 'stimulus spatial frequency condition (0-3)'). The f_sf values 0-3 directly map to y=0-3. The derived misc channel is a trial-locked step function aligned to stimulus onsets (Event/E 1 and Event/E 2). Both event types are stimulus onsets for the two speed conditions and both carry valid f_sf labels. Classification uses event route with y derived from the per-trial f_sf value at each stimulus onset.

### Classical Task 2: 4-way color classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E  1`, `Event/E  2`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0 | color condition 0 (RGB: 66, 10, 104) |
  | `Event/E  1` | 1 | color condition 1 (RGB: 147, 38, 103) |
  | `Event/E  1` | 2 | color condition 2 (RGB: 221, 81, 58) |
  | `Event/E  1` | 3 | color condition 3 (RGB: 252, 165, 10) |
  | `Event/E  2` | 0 | color condition 0 (RGB: 66, 10, 104) |
  | `Event/E  2` | 1 | color condition 1 (RGB: 147, 38, 103) |
  | `Event/E  2` | 2 | color condition 2 (RGB: 221, 81, 58) |
  | `Event/E  2` | 3 | color condition 3 (RGB: 252, 165, 10) |
- **Evidence**:
  - 10.1371/journal.pcbi.1011760 — Classical task: time-resolved 4-way classification of stimulus color from EEG; f_color column provides 4 color conditions (0-3) mapped to distinct RGB values.
  - 10.1038/s41598-025-27703-5 — Confirms separate 4-way classifiers for each visual feature dimension including color, with epoch window -0.1 to 0.6s post-stimulus.
- **Notes**: Kernel must derive `color_label` misc channel from events.tsv:f_color column. The source field f_color contains per-trial integer codes 0-3 corresponding to four distinct RGB colors. The kernel reads f_color values at each stimulus onset (Event/E 1 or Event/E 2), maps them directly to 0-3 integer classes, and creates a trial-locked step-function misc channel aligned to stimulus onset times. Classification uses event route with y derived from the per-trial f_color value at each stimulus onset.

### Classical Task 3: Binary Orientation Classification (Collapsed Levels)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E  1`, `Event/E  2`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0 | cardinal (f_ori=0,2: 22.5°, 112.5°) |
  | `Event/E  1` | 1 | oblique (f_ori=1,3: 67.5°, 157.5°) |
  | `Event/E  2` | 0 | cardinal (f_ori=0,2: 22.5°, 112.5°) |
  | `Event/E  2` | 1 | oblique (f_ori=1,3: 67.5°, 157.5°) |
- **Evidence**:
  - 10.1371/journal.pcbi.1011760 — References mention separate binary/multiclass decoders per feature; f_ori 4 levels collapsed to binary cardinal vs oblique discrimination
  - 10.1038/s41598-025-27703-5 — Binary orientation decoder paradigm providing balanced alternative to 4-way classification
- **Notes**: Derived misc channel `orientation_binary_label` must be created by the kernel: read `f_ori` from events.tsv, map levels 0,2→0 (cardinal orientations: 22.5°, 112.5°) and levels 1,3→1 (oblique orientations: 67.5°, 157.5°), then create a trial-locked step function misc channel aligned to stimulus onset events. The source field `f_ori` is grounded in events.tsv with levels 0-3 and corresponding `feature_ori` values (22.5, 67.5, 112.5, 157.5 degrees). Classification uses event route with y derived from the collapsed per-trial f_ori value at each stimulus onset.

### Potential Task 1: RSVP speed condition classification (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.6 s *, target_events = [`Event/E  1`, `Event/E  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  1` | 0 | Slow RSVP: 6.67Hz presentation rate (soaduration=0.15s) |
  | `Event/E  2` | 1 | Fast RSVP: 20Hz presentation rate (soaduration=0.05s) |
- **Evidence**:
  - sub-01_task-rsvp_events.tsv — speedcondition=0 with soaduration=0.15s (~6.67Hz) and speedcondition=1 with soaduration=0.05s (~20Hz); Event/E 1 (322780) and Event/E 2 (322781) counts match 50/50 split
  - task-rsvp_events.json — speedcondition column defined as "isi condition (0 or 1)"
  - README — "Images were presented in rapid serial visual presentation streams at 6.67Hz and 20Hz rates"
- **Notes**: Event/E 3 (istarget=True, fixation color change detection) is excluded as it represents the orthogonal target detection task, not the speed condition manipulation. The 0.6s epoch window captures temporal integration dynamics: approximately 12 stimuli at 20Hz or 4 stimuli at 6.67Hz.

### Potential Task 2: Target detection classification (target vs non-target)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Event/E  3`, `Event/E  1`, `Event/E  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Event/E  3` | 1 | Target: fixation color change detection trial (istarget=True) |
  | `Event/E  1` | 0 | Non-target: RSVP stimulus onset slow condition (speedcondition=0) |
  | `Event/E  2` | 0 | Non-target: RSVP stimulus onset fast condition (speedcondition=1) |
- **Evidence**:
- **Notes**: This task pools the two non-target stimulus onset events (E1 and E2, differing only in RSVP presentation rate) into a single non-target class (y=0) against the rare target detection event (E3, y=1). The severe class imbalance (~1:512) is theoretically motivated by the oddball/P3 paradigm. Appropriate sampling strategies (e.g., undersampling non-targets, class weights, or stratified sampling) are recommended for practical model training. The extended post-stimulus window (0.8s) captures the P3 component and decision-related activity following target detection, which requires a motor response.

### Potential Task 3: Age regression (subject-level)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 18–27 (years) | Subject chronological age from participants.tsv; N=16, mean ~21.5 |
- **Evidence**:
  - participants.tsv — Age column complete for all 16 subjects with range 18–27 years
- **Notes**: Subject-level regression using continuous 2-second EEG segments. No event structure required. Age is a native participants.tsv column (archetype B3), so Meta Level = raw. Segmentation parameters inferred from standard practice for subject-level biomarker extraction.

### Potential Task 4: Gender classification (subject-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | F | 0 | Female |
  | Gender | M | 1 | Male |
- **Evidence**:
  - participants.tsv — Gender column with values F and M for all 16 subjects; complete categorical field suitable for binary classification
- **Notes**: Subject-level demographic decoding from continuous EEG using 2-second non-overlapping segments. Small sample size (N=16) limits statistical power but task is technically groundable. Segmentation approach treats each 2s window as an independent sample with subject-level gender label.

### Potential Task 5: Handedness classification (subject-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Handedness | R | 0 | Right-handed |
  | Handedness | L | 1 | Left-handed |
- **Evidence**:
  - participants.tsv — Handedness column contains values R (right) and L (left); N=16 subjects with complete data
- **Notes**: Subject-level biomarker task using 2-second non-overlapping segments of resting/task EEG to predict handedness from participants.tsv. The sample shows predominantly R-handed subjects but the catalog confirms L values are possible in the dataset. Binary classification with y mapped to 0-based sequential integers.

### Potential Task 6: Continuous EEG Segmentation with Age Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 18–27 (years) | Subject chronological age from participants.tsv; continuous RSVP viewing periods segmented into 10s windows for sustained neural activity biomarker |
- **Evidence**:
  - (none — Potential task)
- **Notes**: Archetype C with info-native label (Age from participants.tsv). Meta Level = raw because Age is a pre-existing native column, not a kernel-derived misc channel. Segmentation approach uses 10s windows to capture sustained dynamics during rapid visual stimulation without event-locked epoching, contrasting with transient ERP approaches. No overlap specified to reduce autocorrelation at 1000Hz sampling rate. The kernel does not need to compute any derived channels for this task.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
