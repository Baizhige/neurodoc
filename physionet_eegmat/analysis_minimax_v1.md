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

### Primary Task 1: Mental Arithmetic vs Baseline Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0 s *, target_events = [`BST (baseline task)`, `SRT (serial-subtraction/mental arithmetic task)`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `BST (baseline task)` | 0 | Resting-state/baseline EEG |
  | `SRT (serial-subtraction/mental arithmetic task)` | 1 | Mental arithmetic task EEG |
- **Evidence**:
  - DOI: 10.1109/indicon49873.2020.9342140 — The proposed VMD-based mental task classification method is evaluated using the EEGMAT database for classifying baseline (BST) and serial-subtraction (SRT) tasks, achieving 93% average accuracy.
- **Kernel Notes**: Parse event labels from EDF+ annotations; the prefix before semicolon indicates task type (Background EEG vs Mental Arithmetic Task EEG). Segment the 60-second recordings into 10-second windows for feature extraction.

### Primary Task 2: Good vs Poor Counters Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5 s * (5-sample sliding window at 500 Hz = 0.01 s), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor counter (subjects with lower arithmetic performance) |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good counter (subjects with higher arithmetic performance) |
- **Super Meta Notes**: Original dataset classifies subjects into 'good counters' (n=26) vs 'poor counters' (n=10) based on arithmetic task performance quality. Use only Mental Arithmetic Task EEG files for this classification.
- **Evidence**:
  - DOI: 10.1038/s41598.026.36434.0 — This paper applies PC-entropy to the physionet_eegmat mental arithmetic dataset to demonstrate that good counters show significantly increased synchronization (PC-entropy) in beta band during task vs rest, while poor counters show no significant changes.
- **Kernel Notes**: Filter to only Mental Arithmetic Task EEG files (suffix `_2.edf`). Use the Count Quality label (Good/Bad) from annotation suffix to create binary classification. 26 good vs 10 poor subjects indicates class imbalance.

### Primary Task 3: Mental Stress Classification (High vs Low)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Low-stress (poor performance cluster) |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | High-stress (good performance cluster) |
- **Super Meta Notes**: Authors applied unsupervised k-means clustering (k=2) on extracted log-band power features (delta, theta, alpha, beta) from 5-second EEG segments, then mapped clusters to binary stress labels based on posterior overlap with performance metrics.
- **Evidence**:
  - DOI: 10.1109/wccest66994_2025.11389948 — This paper uses the Neurocom EEGMAT dataset to classify mental stress levels (High-stress vs Low-stress) by segmenting EEG into 5-second epochs, applying k-means clustering on frequency band powers to derive refined stress labels, and training CNN, LSTM, and hybrid CNN-LSTM models achieving 98% accuracy.
- **Kernel Notes**: Apply bandpass filter 1-45 Hz. Extract log-band power features for delta, theta, alpha, beta bands. Use k-means clustering to derive stress labels from EEG features during mental arithmetic task.

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
