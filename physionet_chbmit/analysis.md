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

### Primary Task 1: Epileptic seizure detection (ictal vs non-ictal)
- **Task Type**: classification/detection
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Seizure interval labels from annotation files (ictal) vs background/interictal segments.
- **Evidence**: CHB-MIT is widely used for seizure detection benchmarking with annotated seizure intervals. Source: https://physionet.org/content/chbmit/1.0.0/ DOI: https://doi.org/10.13026/C2K01R


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
