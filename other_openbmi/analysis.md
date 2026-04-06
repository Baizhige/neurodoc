# OpenBMI Motor Imagery EEG Dataset

**Dataset**: `other_openbmi` | **Year**: 2019 | **URL**: https://gigadb.org/dataset/view/id/100542/File_page/5
**Category**: Action/Output | **Subjects**: 54 | **Files (Completed)**: 108 | **Channels**: 62 | **Sampling Rate**: 1000 Hz

## Paradigm

Fifty-four subjects (ages 19-32, mixed sex) performed two-class cued motor imagery of the left and right hand across two sessions each (Lee et al., 2019). EEG was recorded from 62 channels (BrainAmp, Brain Products; Ag/AgCl cap) at 1000 Hz. Each session contained 100 trials per class (50 left + 50 right hand MI), yielding 200 trials per session per subject. The motor imagery epoch lasts 3 seconds. Trial onset times and class labels are stored in MATLAB struct fields (`EEG_MI_train.t` for sample indices and `EEG_MI_train.y_class` for labels); the kernel extracts these and creates 3-second MNE annotations.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left hand MI` | 5400 | event | raw | Left-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |
| `right hand MI` | 5400 | event | raw | Right-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Motor imagery decoding - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`left hand MI`, `right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left hand MI` | 0 | Left-hand motor imagery |
  | `right hand MI` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1093/gigascience/giz002 — OpenBMI dataset with 54 subjects performing binary motor imagery (left vs right hand) across two sessions, using EEG epochs for CSP+LDA classification
  - DOI: 10.1016/j.neunet.2020.12.013 — Uses OpenBMI dataset for deep CNN-based transfer learning achieving 84.19% average accuracy
- **Kernel Notes**: Class labels may vary by paper; some works (e.g., Lee et al., 2019 in Neural Networks) use inverse mapping (left=1, right=0). Verify label mapping from y_class field or events.tsv. Dataset spec: 3-second MI epoch; papers analyze 1000-3500ms window for CSP features. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Subject demographics: 54 subjects, ages 19-32, mixed sex.
- Two sessions per subject enable cross-session analysis and session-to-session learning stability.
- High sampling rate (1000 Hz); consider downsampling to 250 Hz for computational efficiency.
- MATLAB struct-based event extraction; requires `EEG_MI_train` field to be present in `.mat` file.
- 62-channel standard 10-20 montage with Ag/AgCl electrodes.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review