# OpenBMI Motor Imagery EEG Dataset

**Dataset**: `other_openbmi` | **Year**: 2019 | **URL**: https://gigadb.org/dataset/view/id/100542/File_page/5
**Category**: Action/Output | **Subjects**: 54 | **Files (Completed)**: 108 | **Channels**: 62 | **Sampling Rate**: 1000 Hz

## Paradigm

Fifty-four subjects (ages 19-32, mixed sex) performed two-class cued motor imagery of the left and right hand across two sessions each (Lee et al., 2019). EEG was recorded from 62 channels (BrainAmp, Brain Products; Ag/AgCl cap) at 1000 Hz. Each session contained 100 trials per class (50 left + 50 right hand MI), yielding 200 trials per session per subject. The motor imagery epoch lasts 3 seconds. Trial onset times and class labels are stored in MATLAB struct fields (`EEG_MI_train.t` for sample indices and `EEG_MI_train.y_class` for labels); the kernel extracts these and creates 3-second MNE annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://gigadb.org/dataset/view/id/100542/File_page/5

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left hand MI` | 5400 | short | raw | Left-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |
| `right hand MI` | 5400 | short | raw | Right-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Left- vs right-hand motor imagery labels (with paradigm-specific extensions where available).
- **Evidence**: OpenBMI benchmark and associated publication define MI decoding as a core supervised task. Source: https://doi.org/10.1093/gigascience/giz002


### Normal Task 1: Binary Motor Imagery Classification - Left vs. Right Hand (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: The annotation duration is set to 3.0 s by the kernel (matching the MI trial length). Balance: exactly 50 trials per class per session; perfectly balanced.

| Event | y | Meaning |
|-------|---|---------|
| `left hand MI` | 0 | Left-hand motor imagery |
| `right hand MI` | 1 | Right-hand motor imagery |
## Data Quality Notes

- Subject demographics: 54 subjects, ages 19-32, mixed sex.
- Two sessions per subject enable cross-session analysis and session-to-session learning stability.
- High sampling rate (1000 Hz); consider downsampling to 250 Hz for computational efficiency.
- MATLAB struct-based event extraction; requires `EEG_MI_train` field to be present in `.mat` file.
- 62-channel standard 10-20 montage with Ag/AgCl electrodes.

## References

- **Reference**: Lee MH et al. (2019). EEG Dataset and OpenBMI Toolbox for Three BCI Paradigms: An Investigation into BCI Illiteracy. *GigaScience*, 8(5), giz002. https://doi.org/10.1093/gigascience/giz002
