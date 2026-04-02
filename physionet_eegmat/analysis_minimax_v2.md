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

### Primary Task 1: Mental Arithmetic Task vs Resting State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, overlap = 2.5 s *, target_events = [`Background EEG;Count Quality: Good`, `Background EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Background EEG;Count Quality: Good` | 0 | Resting-state EEG |
  | `Background EEG;Count Quality: Bad` | 0 | Resting-state EEG |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Mental arithmetic task |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | Mental arithmetic task |
- **Evidence**:
  - DOI: https://doi.org/10.13026/C2JQ1P — "The EEGMAT database contains 36 subjects with two 60-second EEG recordings each: background resting-state (_1.edf) and mental arithmetic task (_2.edf), with annotations encoding both condition type and count quality."
- **Kernel Notes**: Parse event annotation prefix before semicolon to extract task label (Background vs Mental Arithmetic). Each recording is 60s long; sliding window epoching extracts overlapping 5s segments. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Arithmetic Performance Quality Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, overlap = 2.5 s *, target_events = [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor arithmetic performance |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good arithmetic performance |
- **Evidence**:
  - DOI: https://doi.org/10.13026/C2JQ1P — "annotations encoding both condition type and count quality"
  - DOI: 10.1038/s41598.026.36434.0 — "good counters show significantly increased synchronization (PC-entropy) in beta band during task vs rest, while poor counters show no significant changes"
- **Kernel Notes**: Filter to Mental Arithmetic recordings only; parse suffix after semicolon for Count Quality label. Class imbalance expected (27 Good vs 9 Bad from dataset). (replaces Normal Task 2 from original analysis.md)

### Primary Task 3: Mental Stress Classification During Arithmetic Task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0 *, target_events = [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Super Meta Notes**: Derived from raw events [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`] by k-means clustering on log-band power features (delta, theta, alpha, beta). Kernel step: Extract log-band power features from 5s EEG segments, apply k-means (k=2), map clusters to High-stress/Low-stress labels based on posterior overlap with Count Quality. See DOI: 10.1109/wccest66994_2025.11389948.
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 0 | Low-stress (good performers) |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | High-stress (poor performers) |
- **Evidence**:
  - DOI: 10.1109/wccest66994_2025.11389948 — "classify mental stress levels (High-stress vs Low-stress) by segmenting EEG into 5-second epochs, applying k-means clustering on frequency band powers"
- **Kernel Notes**: Segment Mental Arithmetic recordings into 5s non-overlapping windows; compute log-band power in delta, theta, alpha, beta bands; apply k-means clustering to derive stress labels.


## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.

## References

- **Reference**: Zyma I, Tukaev S, Seleznov I, Kiyono K, Popov A, Chernykh M, Shpenkov O (2019). Electroencephalograms during mental arithmetic task performance. *Data*, 4(1), 14. https://physionet.org/content/eegmat/1.0.0/
