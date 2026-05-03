# EEG during Near-Threshold Visual Detection Tasks (No-Cue, 50%-Cue, 100%-Cue)

**Dataset**: `openneuro_ds006171` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006171
**Category**: Sensory/Response | **Subjects**: 26 | **Files (Completed)**: 104 | **Channels**: 144 | **Sampling Rate**: 1024 Hz | **Manual Review**: Pending

## Paradigm

Participants performed near-threshold visual detection tasks across three cueing conditions: no-cue (0% validity), noninformative cue (50% validity), and informative cue (100% validity). The study examines how spatial attention modulates near-threshold detection performance and associated EEG signatures. Stimuli were brief visual Gabor patches presented at or near detection threshold, and participants reported detection via button press. Behavioral columns (gabor_contrast, subjective_r, objective_r, response_time) stored in events.tsv enable regression analyses.

## File Scan Result

> **Kernel SHA256**: `381e414604cb6acd819041e926bfee9c690c53bcd0d53f4d8c584953860a01ea`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 13390 | event | raw |  |
| `event_101` | 1440 | event | raw |  |
| `event_102` | 1438 | event | raw |  |
| `event_103` | 1439 | event | raw |  |
| `event_104` | 1439 | event | raw |  |
| `event_11` | 6116 | event | raw |  |
| `event_111` | 1439 | event | raw |  |
| `event_112` | 1439 | event | raw |  |
| `event_113` | 1439 | event | raw |  |
| `event_114` | 1439 | event | raw |  |
| `event_12` | 6115 | event | raw |  |
| `event_121` | 2538 | event | raw |  |
| `event_122` | 2654 | event | raw |  |
| `event_124` | 17559 | event | raw |  |
| `event_125` | 22331 | event | raw |  |
| `event_128` | 67228 | event | raw |  |
| `event_2` | 13393 | event | raw |  |
| `event_21` | 6118 | event | raw |  |
| `event_22` | 6119 | event | raw |  |
| `event_255` | 1 | event | raw |  |
| `event_31` | 1360 | event | raw |  |
| `event_32` | 1358 | event | raw |  |
| `event_65536` | 5 | event | raw |  |
| `event_65547` | 1 | event | raw |  |
| `event_65557` | 1 | event | raw |  |
| `event_65639` | 1 | event | raw |  |
| `event_65660` | 3 | event | raw |  |
| `event_65664` | 3 | event | raw |  |
| `event_98` | 640 | event | raw |  |
| `event_99` | 640 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Near-Threshold Detection Outcome Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [1, 2, 11, 12, 21, 22, 101, 102, 103, 104, 111, 112, 113, 114, 121, 122, 124, 125]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| 1 | 1 | Trial start |
| 2 | 2 | Response (detection report) |
| 11 | 3 | No-cue condition, stimulus A |
| 12 | 4 | No-cue condition, stimulus B |
| 21 | 5 | 50%-validity cue, stimulus A |
| 22 | 6 | 50%-validity cue, stimulus B |
| 101 | 7 | No-cue - hit (nocue_hit) |
| 102 | 8 | No-cue - miss (nocue_miss) |
| 103 | 9 | No-cue - false alarm (nocue_FA) |
| 104 | 10 | No-cue - correct rejection (nocue_CR) |
| 111 | 11 | 50%-validity cue - hit (50pct_hit) |
| 112 | 12 | 50%-validity cue - miss (50pct_miss) |
| 113 | 13 | 50%-validity cue - false alarm (50pct_FA) |
| 114 | 14 | 50%-validity cue - correct rejection (50pct_CR) |
| 121 | 11 | 50%-validity cue - hit (50pct_hit, run 2) |
| 122 | 12 | 50%-validity cue - miss (50pct_miss, run 2) |
| 124 | 15 | 100%-validity cue - false alarm (100pct_FA) |
| 125 | 16 | 100%-validity cue - correct rejection (100pct_CR) |
- **Evidence**: DOI: https://doi.org/10.1111/psyp.14525 (Perception of near-threshold visual stimuli is influenced by prestimulus alpha-band amplitude but not by alpha phase; supports classification of detection outcomes across cueing conditions)
- **Kernel Notes**: BioSemi code 128 is boundary marker (admin; exclude). Preserve continuous behavioral regressors (gabor_contrast, subjective_r, objective_r, response_time) from events.tsv for regression-based analyses. Event codes 111/121 both encode 50pct_hit—may reflect separate recording runs; preserve source metadata.

---

### Classical Task 2: Cue Validity Effect on Detection Performance
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.5 s, overlap = null, segment_length = 3.0 s, target_events = [11, 12, 21, 22]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| 11 | 1 | No-cue condition (0% validity) |
| 21 | 2 | 50%-validity cue condition |
| 22 | 2 | 50%-validity cue condition (alternate marker) |
- **Evidence**: DOI: https://doi.org/10.1111/psyp.14525 (paradigm explicitly examines spatial attention modulation via cue validity; epoch window -0.5s to 1.0s captures pre-stimulus alpha and post-stimulus perception)
- **Kernel Notes**: Extract cue_validity metadata per segment for classification. Target comparison: hit vs miss rate as function of cue validity (0%, 50%, 100%). Segment length 3.0s accommodates baseline, stimulus, and response periods. Exclude event 128 (BioSemi boundary).

---

### Potential Task 1: Perceptual Outcome vs. Sensory Uncertainty
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, overlap = null, target_events = [11, 12, 21, 22, 101, 111, 121, 122]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| 101 | 1 | Hit (detected) |
| 122 | 0 | Miss (not detected) |
| 111 | 1 | Hit under 50% cue |
| 121 | 1 | Hit under 50% cue (run 2) |
- **Evidence**: Partial support from DOI: https://doi.org/10.1111/psyp.14525 (examines perceptual outcome modulated by pre-stimulus alpha; partial evidence since reference emphasizes alpha analysis rather than sensory uncertainty stratification)
- **Kernel Notes**: Stratify epochs by gabor_contrast from events.tsv into threshold/super-threshold bins. Continuous regressor (gabor_contrast) available for regression-based modeling. Binary label: hit (detected) vs miss (not detected). Preserve source metadata for contrast derivation.

---

### Potential Task 1: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, overlap = null, target_events = [1, 2, 11, 12, 21, 22]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:

| MISC Channel Name | Y Mapping Notes |
|---|---|
| Needs verification | Response time regression target derived from events.tsv `response_time` column (continuous, seconds); no MISC channels present in dataset. Consider using `info` route with events.tsv field or custom extraction pipeline. |
- **Evidence**: Paradigm description indicates response_time stored in events.tsv; plausible from experimental design (reaction time is standard dependent variable in detection tasks)
- **Kernel Notes**: Preserve response_time derivation source (events.tsv column), unit (seconds), and version metadata. Use response-aligned epoching (tmax=0.5s captures early motor response; exclude trials with response_time > 2.0s as outliers). Continuous predictors available: gabor_contrast, subjective_r, objective_r.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
