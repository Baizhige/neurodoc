# ERP-Based Brain-Computer Interface Recordings

**Dataset**: `physionet_erpbci` | **Year**: 2013 | **URL**: https://physionet.org/content/erpbci/1.0.0/
**Category**: Action/Output | **Subjects**: 21 | **Files (Completed)**: 245 | **Channels**: 70 | **Sampling Rate**: 2048 Hz

## Paradigm

Participants spelled characters using a standard 6x6 matrix speller while EEG was recorded with a BioSemi ActiveTwo system (64 EEG + 2 earlobe reference + 4 EOG channels) at 2048 Hz (Riccio et al., 2013). Each row and column of the 6x6 character matrix was randomly intensified for 100 ms with a 50 ms gap (150 ms SOA). Each row/column flashed approximately 20 times per trial, and participants mentally counted target character flashes to sustain attention. The kernel processes raw row/column flash events and classifies each as `seen` (target - the row or column containing the attended character flashed) or `unseen` (non-target) for both rows and columns separately.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/erpbci/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `seen (row)` | varies | short | raw | Target row flash (attended character's row lit up) |
| `seen (column)` | varies | short | raw | Target column flash (attended character's column lit up) |
| `unseen (row)` | varies | short | raw | Non-target row flash |
| `unseen (column)` | varies | short | raw | Non-target column flash |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each 6x6 speller has 6 rows + 6 columns = 12 flashes per sequence; 2 are target (1 row + 1 column), 10 are non-target.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (row)`, `seen (column)`, `unseen (row)`, `unseen (column)`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seen (row)` | 1 | P300 target - attended row flash |
  | `seen (column)` | 1 | P300 target - attended column flash |
  | `unseen (row)` | 0 | Non-target row flash |
  | `unseen (column)` | 0 | Non-target column flash |
- **Super Meta Notes**: Labels derived by matching raw row/column intensification events (#TgtP_RC01_SOA63 annotation identifies target character) against the attended character to determine target vs non-target status per flash.
- **Evidence**:
  - DOI: 10.13026/C2101S — This dataset page describes ERP-based BCI recordings from a P300 matrix speller paradigm where participants spell characters by focusing on target flashes while row/column intensifications are recorded as events that can be classified as target (attended) or non-target.
  - DOI: 10.13026/C2101S — This dataset page describes ERP-based BCI recordings where participants used a 6x6 matrix speller to spell characters, with target (attended) vs non-target row/column flashes as the primary classification targets.
- **Kernel Notes**: Epoch around each row/column intensification event from -0.1s to 0.8s. Combine `seen (row)` and `seen (column)` as positive class (y=1); `unseen (row)` and `unseen (column)` as negative class (y=0). Handle class imbalance (~1:5 ratio). Exclude EOG channels from features.

### Normal Task 1: P300 Target vs. Non-Target Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Combine `seen (row)` and `seen (column)` as the positive class (y=1); class imbalance ~1:5 (2 target vs 10 non-target per sequence). EOG channels (VEOGL, VEOGR, HEOGL, HEOGR) should be excluded from EEG features.

| Event | y | Meaning |
|-------|---|---------|
| `seen (row)` | 1 | P300 target - attended row flash |
| `seen (column)` | 1 | P300 target - attended column flash |
| `unseen (row)` | 0 | Non-target row flash |
| `unseen (column)` | 0 | Non-target column flash |


### Normal Task 2: Row vs. Column P300 Speller (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Separate row and column targets for character-level decoding. Use `seen (row)` to identify the target row and `seen (column)` to identify the target column; their intersection determines the spelled character.

## Data Quality Notes

- Very high sampling rate (2048 Hz); consider downsampling to 256 or 512 Hz for computational efficiency.
- Class imbalance: 2 target flashes vs. 10 non-target flashes per sequence (1:5 ratio); balance with oversampling or cost-sensitive learning.
- EOG channels present (4 channels); apply artifact rejection before P300 classification.
- Age and sex information are not available.

## References

- **Reference**: Riccio A et al. (2013). Interfacing Brain with Computer to Improve Communication and Rehabilitation after Spinal Cord Injury. *Frontiers in Neuroengineering*. Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. https://physionet.org/content/erpbci/1.0.0/
