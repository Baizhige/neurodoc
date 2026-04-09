# SHU Motor Imagery EEG Dataset

**Dataset**: `figshare_shudb` | **Year**: 2022 | **URL**: https://figshare.com/articles/software/shu_dataset/19228725/1
**Category**: Action/Output | **Subjects**: 25 | **Files (Completed)**: 232 | **Channels**: 32 | **Sampling Rate**: 250 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

The MI experiment was divided into three stages. In the first stage, 0-2s was the rest preparation period, during which subjects can rest, have small body movements, and blink. The second stage, 2-4s, was the prompt stage. In this stage, the left-hand or right-hand movement animation will appear on the monitor to remind subjects of the hand task next. The third stage, 4-8s, was the process of MI. During this period, subjects perform MI tasks of hand movement in the corresponding direction according to the arrow prompt in the monitor. The EEG equipment collected and stored signals at this stage. 100 trials were obtained after completing a session. In the experiment, we carried out five independent sessions with 2 to 3 days interval on each subject so that each subject had 500 trials in 5 sessions eventually.


## File Scan Result

> **Kernel SHA256**: `46de3ffd3595c45676c1f946231a2d77261dff068879f2299d056429a7aa3fea`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Sampled (2/856 files)

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `left` | ~70 | event | raw | Left-hand motor imagery cue onset |
| `right` | ~78 | event | raw | Right-hand motor imagery cue onset |


> > **Note**: The paper reports a trial structure of 2 + 2 + 4 = 8 seconds (cue + preparation + motor imagery). However, in the raw `.tsv` event files, each trial shows approximately 1000 onset entries, which — at a 250 Hz sampling rate — corresponds to 4 seconds. This discrepancy suggests that the events recorded in the TSV files may capture only the motor imagery (MI) window (i.e., the 4-second imagery phase), rather than the full 8-second trial epoch as described in the paper. The precise mapping of which trial phase each event marker corresponds to (cue onset, preparation offset, or MI start) has not been independently verified from the raw data and should be treated as **Needs verification**. Users are advised to cross-check against the original trial timing logs or the companion documentation before finalizing epoch windows.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 3.5 s, target_events = [`left`, `right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left` | 0 | Left-hand motor imagery |
  | `right` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1016/j.heliyon.2024.e37343 — Validates multi-session left vs right hand motor imagery classification using CNN-based feature extraction with 3s MI window (offset is 0.5)
  - DOI: 10.1016/j.jneumeth.2025.110483 — Validates on SHU dataset achieving 87.2% within-session and 67.2% cross-session accuracy for left/right hand MI
  - DOI: 10.1109/jbhi.2024.3467090 — Evaluates binary motor imagery classification on SHU dataset achieving 69.3% accuracy
- **Kernel Notes**: 

## Data Quality Notes

- Conflict exist on event label but dataset can be classified

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
