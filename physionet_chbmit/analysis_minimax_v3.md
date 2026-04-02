# CHB-MIT Scalp EEG Database

**Dataset**: `physionet_chbmit` | **Year**: 2010 | **URL**: https://physionet.org/content/chbmit/1.0.0/
**Category**: Biological State | **Subjects**: 22 | **Files (Completed)**: 686 | **Channels**: 23 | **Sampling Rate**: 256 Hz

## Paradigm

Twenty-two pediatric patients (5 males aged 3-22; 17 females aged 1.5-19) with intractable seizures were monitored at Children's Hospital Boston following withdrawal of anti-seizure medication to evaluate surgical candidacy (Shoeb & Guttag, 2010). Long-term continuous EEG was recorded from 23 scalp channels (bipolar montage following the 10-20 system) at 256 Hz with 16-bit resolution. The dataset contains 686 EEG files and 182 seizure events in total. Seizure onset and offset times are documented in per-subject summary text files (`chbNN-summary.txt`); the kernel parses these to create `seizure` annotations spanning each ictal period.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://physionet.org/content/chbmit/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `seizure` | 182 | long | raw | Seizure period (onset to offset, variable duration) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Files without seizures have no annotations; these ictal-free recordings serve as the negative (interictal) class.
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Binary seizure detection (ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `seizure` | 1 | Ictal (seizure period) |
  | (no annotation) | 0 | Interictal (seizure-free) |
- **Evidence**:
  - DOI: 10.1016/j.bspc.2024.107379 — Uses 2-second epochs for ictal vs non-seizure classification on CHB-MIT
  - DOI: 10.1038/s41598-025-18479-9 — Binary seizure detection (ictal vs non-seizure) on CHB-MIT
  - DOI: 10.1038/s41598.025.98389.y — 5-second windows for binary seizure vs no-seizure classification
- **Kernel Notes**: Extract seizure epochs using segmentation on the raw EEG. For interictal class, use seizure-free segments from files without seizure annotations or exclude periods within 5-10 s of seizure onset/offset. Severe class imbalance — apply undersampling or class weighting.

### Primary Task 2: Seizure prediction (preictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 1.0 s (90% overlap) *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | preictal | 1 | Period 30 min before seizure onset |
  | interictal | 0 | Seizure-free period >=4 hours before/after seizure |
- **Super Meta Notes**: Derived from raw event `seizure` by defining preictal as the 30-minute window preceding each seizure onset, and interictal as periods at least 4 hours before seizure onset or 4 hours after seizure offset. Kernel step: compute time differences from seizure onset timestamps to label windows.
- **Evidence**:
  - DOI: 10.1088/1741-2552/ada0e5 — Uses 10 s intervals with 90% overlap for preictal vs interictal classification; preictal = 30 min before seizure, interictal >=4 hours away
  - DOI: 10.1109/access.2020.2976866 — Seizure prediction with preictal (30-90 min before seizure) vs interictal using 30-second STFT windows
- **Kernel Notes**: Requires precise timestamp computation. Preictal segments are the 30 minutes immediately preceding each seizure onset. Interictal segments must be at least 4 hours removed from any seizure. Exclude ictal periods entirely.

### Primary Task 3: Three-class seizure state classification (preictal vs ictal vs interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 3.0 s (stride = 1.0 s)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | ictal | 1 | Seizure period (annotated seizure interval) |
  | preictal | 0 | 20 min before seizure onset * |
  | interictal | 2 | Remaining seizure-free periods |
- **Super Meta Notes**: Derived from raw event `seizure` by defining preictal as the 20-minute window before seizure onset and interictal as all other seizure-free time. Advanced labeling may use signal features (Shannon entropy, mean voltage) to refine preictal vs interictal distinction within the 20-min window. Kernel step: segment with 4s windows, compute time-relative labels.
- **Evidence**:
  - DOI: 10.54525/bbmd.1526069 — Three-class classification (pre-seizure/ictal/non-seizure) using 4-second EEG spectrogram windows with 3-second overlap on CHB-MIT
- **Kernel Notes**: Segment all EEG into 4-second windows. Label windows overlapping seizure annotations as ictal (y=1). Label windows in the 20-minute pre-seizure window as preictal (y=0). Label remaining seizure-free windows as interictal (y=2). Consider using advanced signal features to further distinguish preictal from interictal within the 20-min window.

### Normal Task 1: Seizure Detection - Ictal vs. Interictal (epoch_by_long_event + custom)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` (for ictal files) + `epoch_by_segmentation_hdf5` (for interictal files)
- **Epoch Parameters**: For seizure epochs: tmin = 0.0 s (annotation onset), use full duration; For interictal: sliding window 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Files with no seizure annotations are entirely interictal; use `epoch_by_segmentation_hdf5` for those. Files with `seizure` annotations contain both ictal and pre/post-ictal segments; consider a buffer of 5-10 s before/after seizure onset as pre-ictal/post-ictal and exclude from clean interictal class. Severe class imbalance: seizure epochs (~182 events) vs. many hours of interictal EEG.

| Event | y | Meaning |
|-------|---|---------|
| `seizure` | 1 | Ictal activity |
| (no annotation) | 0 | Interictal (seizure-free) baseline |

### Normal Task 2: Patient-Specific Seizure Detection (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event`
- **Epoch Parameters**: Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification.
- **Notes**: Train per patient; subjects chb17 appears in three sub-cases (chb17a, chb17b, chb17c) and should be treated as a single subject.

## Data Quality Notes

- Severe class imbalance: the majority of recordings are seizure-free; balance by undersampling interictal or using cost-sensitive learning.
- Channel count varies: most files have 23 channels; some cases include 24 or 26 channels (extra ECG or vagal nerve stimulus channels); exclude non-EEG channels.
- Patient-specific model training is recommended; cross-patient generalization is difficult.
- Subject chb24 has unknown age and sex.
- Age range: 1.5-22 years (pediatric); EEG morphology differs significantly from adult norms.

