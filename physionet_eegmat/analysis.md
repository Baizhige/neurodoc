# EEG During Mental Arithmetic Task

**Dataset**: `physionet_eegmat` | **Year**: 2020 | **URL**: https://physionet.org/content/eegmat/1.0.0/
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 21 | **Sampling Rate**: 500 Hz

## Paradigm

Thirty-six healthy subjects (Subject00-Subject35, ages 16-26, predominantly female) completed a mental arithmetic task while EEG was recorded from 21 channels using a Neurocom 23-channel system with Ag/AgCl electrodes (Zyma et al., 2019). Each subject contributed two files: a background resting-state recording (suffix `_1.edf`) and a mental arithmetic task recording (suffix `_2.edf`). During the mental arithmetic task, subjects performed serial subtraction (e.g., counting backwards by 7s) while EEG was recorded. A separate `Count quality` field in `subject-info.csv` rates the subject's arithmetic performance as Good or Bad, providing a behavioral quality label.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/eegmat/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Background EEG;Count Quality: Good` | 27 | long | raw | Resting-state recording, subject's arithmetic quality was Good |
| `Background EEG;Count Quality: Bad` | 9 | long | raw | Resting-state recording, subject's arithmetic quality was Bad |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 27 | long | raw | Mental arithmetic recording, quality Good |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 9 | long | raw | Mental arithmetic recording, quality Bad |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each annotation spans the entire recording. Counts are approximate (36 subjects x 2 files = 72 total; Good/Bad split estimated from subject distribution).

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://physionet.org/content/eegmat/1.0.0/ DOI: https://doi.org/10.13026/C2JQ1P


### Normal Task 1: Mental Arithmetic vs. Resting State (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Annotation spans the entire recording - use `epoch_by_long_event_hdf5` with sliding window. The event description encodes both task type and count quality; parse the prefix before the semicolon to extract the task label.

| Event | y | Meaning |
|-------|---|---------|
| `Background EEG;Count Quality: Good` | 0 | Resting-state EEG (good quality) |
| `Background EEG;Count Quality: Bad` | 0 | Resting-state EEG (poor quality) |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Mental arithmetic EEG (good quality) |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | Mental arithmetic EEG (poor quality) |


### Normal Task 2: Mental Arithmetic Quality Prediction (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use only arithmetic task files (`Mental Arithmetic Task EEG;*`); separate by `Count Quality: Good` (y=1) vs `Count Quality: Bad` (y=0).
- **Notes**: Predicts arithmetic performance quality from EEG. Class imbalance likely (more Good than Bad performers).
## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.

## References

- **Reference**: Zyma I, Tukaev S, Seleznov I, Kiyono K, Popov A, Chernykh M, Shpenkov O (2019). Electroencephalograms during mental arithmetic task performance. *Data*, 4(1), 14. https://physionet.org/content/eegmat/1.0.0/
