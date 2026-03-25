# AlphaDirection1: EEG, ECG, PPG in the resting state and working memory for sequentially and simultaneously presented digits

**Dataset**: `openneuro_ds006848` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006848/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 52
**Channels**: 65 | **Sampling Rate**: 1000 Hz

## Paradigm

This dataset studies the directional characteristics of brain alpha waves during resting state and working memory tasks. Participants completed a verbal working memory digit span task in two encoding modes: serial presentation (one digit is displayed at a time) and simultaneous presentation (an entire set of digits are displayed at once), followed by serial recall; before the experiment, a resting state (eyes open/eyes closed alternating) recording was included, and cartoon clips were used to separate different experimental segments. Data is recorded simultaneously with EEG, ECG and PPG.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006848/versions/1.0.0

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Encoding_DigitValue_0` | 3163 | short | raw | Sequence encoding: number 0 presents onset |
| `Encoding_DigitValue_1` | 3134 | short | raw | Sequence encoding: number 1 presents onset |
| `Encoding_DigitValue_2` | 3077 | short | raw | Sequence encoding: number 2 presents onset |
| `Encoding_DigitValue_3` | 3124 | short | raw | Sequence encoding: number 3 presents onset |
| `Encoding_DigitValue_4` | 3164 | short | raw | Sequence encoding: number 4 presents onset |
| `Encoding_DigitValue_5` | 3104 | short | raw | Sequence encoding: number 5 presents onset |
| `Encoding_DigitValue_6` | 3103 | short | raw | Sequence encoding: number 6 presents onset |
| `Encoding_DigitValue_7` | 3131 | short | raw | Sequence encoding: number 7 presents onset |
| `Encoding_DigitValue_8` | 3117 | short | raw | Sequence encoding: number 8 rendering onset |
| `Encoding_DigitValue_9` | 3131 | short | raw | Sequence encoding: number 9 presents onset |
| `Encoding_Set_Simultaneous` | 1495 | short | raw | Simultaneous encoding: the entire set of numbers is presented at once onset |
| `Digits_Retrieval` | 5960 | short | raw | The recall phase begins (the subject begins to report verbally) |
| `Baseline_2s` | 5956 | short | raw | 2 s before each trial, the beginning of the baseline segment |
| `Retention_Fast` | 1499 | long | raw | Fast delay hold period (sequence encoding, short delay) |
| `Retention_FastDelay` | 1499 | long | raw | Fast delay additional waiting period (sequence encoding) |
| `Retention_Slow` | 1466 | long | raw | Slow delay hold period (sequence encoding, long delay) |
| `Retention_Simultaneous` | 1495 | long | raw | Retention period after simultaneous encoding |
| `Rest` | 209 | rest | raw | Resting state segment start mark |
| `Eyes_Closed` | 87 | rest | raw | Close your eyes and start to rest |
| `Eyes_Opened` | 88 | rest | raw | Open your eyes and start to rest |
| `Boundary` | 157 | admin | raw | BIDS file boundary mark |
| `Experiment_End` | 29 | admin | raw | Experiment end mark |
| `Start_Cartoon` | 22 | admin | raw | Cartoon short film starts (intersegment interference) |
| `End_Cartoon` | 22 | admin | raw | End of cartoon short |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Working Memory Digit Recall Prediction (Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -10.0 s, tmax = 8.0 s, target_events = [`Encoding_Set_Simultaneous`, `Retention_Fast`, `Retention_Slow`, `Retention_FastDelay`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Encoding_Set_Simultaneous` | 0-7 | Simultaneous encoding: all digits presented at once, predict digits recalled (0-7) |
  | `Retention_Fast` | 0-7 | Fast encoding (400ms/digit), short delay, predict digits recalled |
  | `Retention_Slow` | 0-7 | Slow encoding (1000ms/digit), long delay, predict digits recalled |
  | `Retention_FastDelay` | 0-7 | Fast encoding with extra delay gap, predict digits recalled |
- **Evidence**:
  - DOI: 10.1101/2025.05.04.652111 — This paper analyzes EEG from OpenNeuro ds006848 to predict number of digits recalled (0-7) from EEG spectral power across four presentation modes (Simultaneous, Fast, Slow, Fast+delay) during encoding and retention periods.
- **Kernel Notes**: 
  - Paper uses analysis windows: Encoding, Retention 1 (0.6-3s), Retention 2 (3-6s), excluding first 0.6s of retention
  - Extract spectral power features (alpha, theta, beta bands) from retention onset epochs
  - Target variable: number of digits recalled (integer 0-7)
  - Presentation mode events map to: Simultaneous→`Encoding_Set_Simultaneous`, Fast→`Retention_Fast`, Slow→`Retention_Slow`, Fast+delay→`Retention_FastDelay`

### Primary Task 2: Presentation Mode Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Encoding_Set_Simultaneous`, `Retention_Fast`, `Retention_Slow`, `Retention_FastDelay`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Encoding_Set_Simultaneous` | 0 | Simultaneous presentation (entire set at once) |
  | `Retention_Fast` | 1 | Sequential fast presentation (400ms/digit) |
  | `Retention_Slow` | 2 | Sequential slow presentation (1000ms/digit) |
  | `Retention_FastDelay` | 3 | Sequential fast with additional delay gap |
- **Evidence**:
  - DOI: 10.1101/2025.05.04.652111 — The study examines alpha, theta, and beta oscillations across four digit presentation modes as experimental conditions.
- **Kernel Notes**: 
  - This is the classification variant of the same experimental paradigm
  - Balanced classes: Simultaneous ~1495, Fast ~1499, Slow ~1466, FastDelay ~1499
  - (replaces Normal Task 3 from original analysis.md - retention period type classification)

### Normal Task 1: Task 1 (main task): coding mode two classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: The categories are seriously unbalanced (sequence ~31000 times vs. simultaneous ~1495 times), downstream needs to downsample to 1:1

| Event | y | Meaning |
 |-------|---|------|
| `Encoding_DigitValue_0` | 0 | Sequence code (number 0) |
| `Encoding_DigitValue_1` | 0 | Sequence code (number 1) |
| `Encoding_DigitValue_2` | 0 | Sequence code (number 2) |
| `Encoding_DigitValue_3` | 0 | Sequence code (number 3) |
| `Encoding_DigitValue_4` | 0 | Sequence code (number 4) |
| `Encoding_DigitValue_5` | 0 | Sequence code (number 5) |
| `Encoding_DigitValue_6` | 0 | Sequence code (number 6) |
| `Encoding_DigitValue_7` | 0 | Sequence code (number 7) |
| `Encoding_DigitValue_8` | 0 | Sequence code (number 8) |
| `Encoding_DigitValue_9` | 0 | Sequence code (number 9) |
| `Encoding_Set_Simultaneous` | 1 | Simultaneous encoding (whole group) |


### Normal Task 2: Digital Identification (11-class multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Each number category ~3100 times, Encoding_Set_Simultaneous ~1495 times, the overall balance is relatively balanced; **This is the actual configuration in task_config.json**

| Event | y | Meaning |
 |-------|---|------|
| `Encoding_DigitValue_0` | 0 | Number 0 (sequence condition) |
| `Encoding_DigitValue_1` | 1 | number 1 |
 | ... | ... | ... |
| `Encoding_DigitValue_9` | 9 | Number 9 |
| `Encoding_Set_Simultaneous` | 10 | Present the entire group simultaneously |


### Normal Task 4: Resting state: open/closed eyes classification (binary, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Each file has about 1-2 switches (87/88 times in total), the amount of data is limited; `Rest` is the segment start mark and is not directly used for epoch

| Event | y | Meaning |
 |-------|---|------|
| `Eyes_Closed` | 0 | Close eyes and rest |
| `Eyes_Opened` | 1 | Rest with eyes open |


## Data Quality Notes

- The ratio of sequence encoding vs. simultaneous encoding categories is about 20:1, and downsampling is required to do a fair binary classification evaluation.
- `Boundary` is the BIDS file boundary, which will appear at the beginning of each file and must be excluded from the epoch target
- Some subjects' files lack the `Eyes_Closed`/`Eyes_Opened` mark (only 22/30 subjects have resting eye state records)
- Sampling rate 1000 Hz, stage5 will downsample to 200 Hz

## References

- **Reference**: `AlphaDirection1: EEG, ECG, PPG in the resting state and working memory for sequentially and simultaneously presented digits`
