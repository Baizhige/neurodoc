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
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 s *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seizure` | 1 | Ictal (seizure activity) |
  | (no annotation) | 0 | Interictal (seizure-free baseline) |
- **Super Meta Notes**: Labels extracted directly from seizure annotation files in CHB-MIT dataset summary files; seizure data from annotated seizure periods, non-seizure data from remaining seizure-free portions.
- **Evidence**:
  - DOI: 10.1016/j.bspc.2024.107379 — Applies OCNN to classify 2-class seizure vs non-seizure EEG data from CHB-MIT by extracting 2s seizure/non-seizure segments, achieving 96.72% average accuracy across 23 subjects
  - DOI: 10.1038/s41598.025.98389.y — Uses CHB-MIT dataset divided into 5-second fragments classified as Seizure or No Seizure based on available annotations
  - DOI: 10.1038/s41598.025.18479.9 — Uses CHB-MIT for binary classification between seizure and non-seizure EEG segments, achieving 96.94% accuracy with 1D CNN-LSTM model
- **Kernel Notes**: Parse per-subject summary text files (`chbNN-summary.txt`) to extract seizure onset/offset times. Apply sliding window segmentation to both ictal (seizure annotation present) and interictal (no annotation) segments. Ensure non-overlapping windows for binary classification. Handle class imbalance by undersampling interictal or using cost-sensitive learning.

### Primary Task 2: Three-class seizure state classification (preictal, ictal, interictal)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 3 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `preictal` | 0 | Pre-seizure state (20 min before seizure onset) * |
  | `ictal` | 1 | Seizure activity |
  | `interictal` | 2 | Seizure-free baseline (>=4 hours before/after seizure) * |
- **Super Meta Notes**: Preictal labels derived by defining a time window before each seizure onset from raw seizure annotations. Ictal labels from annotated seizure periods. Interictal from seizure-free periods. Exact preictal window duration may vary; 20 min is common in literature.
- **Evidence**:
  - DOI: 10.1088/1741-2552.ada0e5 — Uses CHB-MIT for seizure detection (ictal vs preictal) and prediction (preictal vs interictal) with 10s intervals, defining preictal as 30 min before seizure and interictal as >=4 hours before/after seizure
  - DOI: 10.54525/bbmd.1526069 — Performs three-class classification (pre-seizure/ictal/non-seizure) on CHB-MIT using 4-second EEG spectrogram windows with 1s stride, with basic labeling: 20 min before seizure = pre-ictal, seizure period = ictal, rest = interictal
- **Kernel Notes**: Requires deriving preictal labels from seizure onset times. Define preictal window (e.g., 20-30 min before seizure) and interictal periods (>=4 hours from seizure). Use segmentation with 4s window and 3s overlap (75% overlap) to capture sufficient samples across all three classes.

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

## References

- **Reference**: Shoeb AH, Guttag JV (2010). Application of machine learning to epileptic seizure detection. In *Proceedings of the 27th ICML*. Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. *Circulation*, 101(23), e215-e220. https://physionet.org/content/chbmit/1.0.0/
