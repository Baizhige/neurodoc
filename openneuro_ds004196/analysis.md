# Bimodal dataset on Inner speech

**Dataset**: `openneuro_ds004196` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004196
**Category**: High-level Mental | **Subjects**: 4 | **Files (Completed)**: 4 | **Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

An inner-speech production task where participants mentally vocalized eight specific words from social and numeric categories during nonsimultaneous EEG and fMRI recording. Four right-handed participants imagined speaking words without producing overt speech or movement. The paradigm followed a fixation-task-rest structure (1s fixation + 2s task + 1s rest), yielding 320 trials per subject (40 trials per word across 8 words in 2 categories).

## File Scan Result

> **Kernel SHA256**: `988afec0b6493fd2034ec9543c69e9333904ca7281a8d505b99709b43248b148`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 1282 | event | raw | Fixation onset |
| `event_111` | 160 | event | raw | Social word: child |
| `event_112` | 160 | event | raw | Social word: daughter |
| `event_113` | 160 | event | raw | Social word: father |
| `event_114` | 160 | event | raw | Social word: wife |
| `event_125` | 161 | event | raw | Numeric word: four |
| `event_126` | 161 | event | raw | Numeric word: three |
| `event_127` | 160 | event | raw | Numeric word: ten |
| `event_128` | 161 | event | raw | Numeric word: six |
| `event_2` | 1280 | event | raw | Rest onset |
| `event_65536` | 1 | admin | raw | Recording start marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Inner Speech Binary Classification (Social vs Numeric)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0, tmin = 0.0, tmax = 2.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_111` | 0 | Social word: child |
  | `event_112` | 0 | Social word: daughter |
  | `event_113` | 0 | Social word: father |
  | `event_114` | 0 | Social word: wife |
  | `event_125` | 1 | Numeric word: four |
  | `event_126` | 1 | Numeric word: three |
  | `event_127` | 1 | Numeric word: ten |
  | `event_128` | 1 | Numeric word: six |
- **Super Meta Notes**: Trial timing derived from events.tsv sidecar or experimental design metadata (1s fixation + 2s task + 1s rest per trial). 160 events per word type across 4 subjects (40 trials/word/subject). Events 111-114 map to social category; events 125-128 map to numeric category.
- **Evidence**:
  - DOI: 10.1038/s41597-023-02286.w — "Full dataset descriptor: 4 right-handed participants, 320 trials per subject, 8 words in 2 categories (social vs numeric), event markers aligned to stimulus onsets for binary classification."
  - DOI: 10.1101/2022.05.24.492109 — "Binary classification (social vs numeric) with Random Forest achieving 62.81% EEG-only accuracy (chance 50%) using 2s epoch windows around stimulus onset."
- **Kernel Notes**: Verify event-to-word mapping against events.tsv columns. Events 111-114 correspond to child/daughter/father/wife; events 125-128 correspond to four/three/ten/six. Aggregate to binary labels by collapsing events 111-114 → y=0 (social) and events 125-128 → y=1 (numeric).

### Classical Task 2: Inner Speech 8-Class Word Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0, tmin = 0.0, tmax = 2.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_111` | 0 | Social word: child |
  | `event_112` | 1 | Social word: daughter |
  | `event_113` | 2 | Social word: father |
  | `event_114` | 3 | Social word: wife |
  | `event_125` | 4 | Numeric word: four |
  | `event_126` | 5 | Numeric word: three |
  | `event_127` | 6 | Numeric word: ten |
  | `event_128` | 7 | Numeric word: six |
- **Super Meta Notes**: Eight distinct word labels from experimental paradigm. 40 trials per word per subject × 4 subjects = 160 trials per word type, 1280 total trials. Use events.tsv to extract trial timing and word identity for epoch labeling.
- **Evidence**:
  - DOI: 10.1038/s41597-023-02286.w — "Dataset contains 8 word stimuli (4 social: child, daughter, father, wife; 4 numeric: four, three, ten, six) with event markers mapped to individual word types."
  - DOI: 10.1101/2022.05.24.492109 — "8-class word classification with Random Forest achieving 22.19% accuracy (chance 12.5%) using epochs extracted around stimulus onset."
- **Kernel Notes**: Each event ID (111-114, 125-128) maps to a unique word label (y=0 through y=7). Verify counts: ~160 events per event_id confirms 40 trials × 4 subjects structure. Use 2s epochs aligned to stimulus onset for each event.