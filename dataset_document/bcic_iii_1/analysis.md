# BCI Competition III Dataset 1 (Directional Motor Imagery EEG)

**Dataset**: `bcic_iii_1` | **Year**: 2005 | **URL**: https://www.bbci.de/competition/iii/download/
**Category**: Action/Output | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

A single subject performed directional motor imagery (BCI Competition III, 2005). Visual arrow cues prompted 4-second motor imagery periods (two classes: left and right/foot). The dataset is stored in a single GDF file (`BCI2005_I.gdf`). The GDF format embeds event annotations natively; MNE reads them automatically. No age or sex information is available in the public release.

## File Scan Result

> **Kernel SHA256**: `0c3d0c93040028190511ea41a99743313b965b932a8f604a46dc9b38b7dc3634`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `768` | 377 | event | raw | Annotation code 768 |
| `769` | 138 | event | raw | Annotation code 769 |
| `772` | 139 | event | raw | Annotation code 772 |
| `783` | 100 | event | raw | Annotation code 783 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class motor imagery (left vs right/foot)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [769, 772]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | 769 | 0 | Annotation code 769 |
  | 772 | 1 | Annotation code 772 |
- **Evidence**:
  - https://www.bbci.de/competition/iii/ — BCI Competition III official dataset page
  - https://www.bbci.de/competition/iii/download/ — Official dataset download and documentation
- **Notes**: This is a classical 2-class motor imagery benchmark from BCI Competition III. The event codes 769 and 772 serve as class-specific cue onsets for two motor imagery conditions. Despite the competition description mentioning left pinky vs tongue imagery, the dataset documentation and analysis notes reference left hand vs right hand/foot as class labels. Event 768 (trial start) and 783 (unknown/evaluation placeholder) are excluded from classification. Epoch window parameters are inferred from competition structure (4-second imagery periods from cue onset) following SKILL defaults for cue-onset BCI paradigms.

### Classical Task 2: 2-class motor imagery with baseline (left vs right/foot)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`769`, `772`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---|
| 769 | 0 | Annotation code 769 |
| 772 | 1 | Annotation code 772 |

- **Evidence**:
  - https://www.bbci.de/competition/iii/ — BCI Competition III official website describing the dataset and competition tasks
  - https://www.bbci.de/competition/iii/download/ — Dataset download page confirming event structure with codes 769 (138 trials) and 772 (139 trials)
- **Notes**: This task uses a -0.5s pre-stimulus baseline to capture preparatory activity and enable baseline correction, a common preprocessing step in offline BCI motor imagery analysis. The two event codes (769, 772) represent the two motor imagery classes in this variant of the primary task. Event 768 trial-start markers are available for potential baseline extraction anchoring but are not used as class labels.

### Potential Task 1: trial phase detection (trial-start vs cue-onset)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`768`, `769`, `772`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | 768 | 0 | trial-start |
  | 769 | 1 | cue-onset |
  | 772 | 1 | cue-onset |
- **Evidence**:
- **Notes**: Events 769 and 772 are merged into a single cue-onset class (y=1) versus 768 as trial-start (y=0). This tests whether EEG contains discriminable patterns between pre-cue readiness and active cued-imagery periods. All event codes are annotation descriptions from the GDF file header with unknown semantic meaning due to lack of documentation; the phase interpretation is inferred from the candidate's evidence summary based on typical BCI competition paradigms where 768 commonly marks trial onset and 769/772 mark cue presentations.

### Potential Task 2: Known vs Unknown Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [769, 772, 783]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | 769 | 0 | Annotation code 769 (known class cue) |
  | 772 | 0 | Annotation code 772 (known class cue) |
  | 783 | 1 | Annotation code 783 (unknown/evaluation cue) |
- **Evidence**:
- **Notes**: This task tests for potential data leakage or distribution shift between the training-known cues (769, 772) and the evaluation-set placeholder cue (783). The 783 event is explicitly described in the candidate's evidence summary as 'Cue unknown (evaluation-set placeholder)' and occurs in 100 trials versus 277 combined trials for 769/772. Both known-class cues are merged to y=0 since they share the same functional status as training-visible class labels, while 783 forms the distinct y=1 class. The epoch window [0, 4]s is inferred from the competition structure to match the primary MI task timing for direct comparability. Event meanings are locked to the grounded annotation codes since no semantic documentation was available.

## Data Quality Notes

- Single-subject dataset; results cannot be generalized across subjects.
- Very small dataset (1 file, 377 trials); statistical power is limited.
- High sampling rate (1000 Hz); consider downsampling to <=250 Hz.
- No demographic information available.
- GDF event codes are kept as numeric strings in MNE annotations; ensure correct integer parsing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
