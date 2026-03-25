# UC San Diego Resting State EEG Data from Patients with Parkinson's Disease

**Dataset**: `openneuro_ds002778` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002778
**Category**: Biological State | **Subjects**: N/A | **Files (Completed)**: 46 | **Channels**: 41.0 | **Sampling Rate**: 512.0 Hz

## Paradigm

Spontaneous scalp EEG recorded from patients with Parkinson's disease (PD) and healthy controls during resting-state conditions. The study investigated abnormal beta-band synchrony and beta waveform shape features (phase amplitude coupling, non-sinusoidal characteristics) as biomarkers of PD. All events in the BioSemi recording are system status markers (65536 = CM_in_range baseline, 130817 = CM status); no task events exist.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002778

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 44 (files) | admin | raw | BioSemi recording marker (onset of continuous record) - admin |
| `65536` | 43 (files) | admin | raw | BioSemi CM_in_range baseline status code - exclude |
| `2` | 1 (file) | admin | raw | BioSemi marker - sparse, likely admin |
| `130817` | 1 (file) | admin | raw | BioSemi CM status code - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Parkinson's Disease Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HC` | 0 | Healthy control subject |
  | `PD` | 1 | Parkinson's disease patient |
- **Super Meta Notes**: Labels (PD vs HC) are derived from participant metadata (participants.tsv), not from raw EEG event markers. The dataset contains only BioSemi system status markers (65536, 130817) as raw events. The kernel must read subject-level diagnosis labels from participants.tsv and apply them as segment-level labels.
- **Evidence**:
  - DOI: 10.1016/j.bspc.2022.104116 — Uses dataset-II (San Diego EEG dataset, openneuro_ds002778) for automated PD diagnosis, segmenting 3-minute resting-state EEG into 2-second non-overlapping windows and classifying PD vs HC using FAWT entropy with KNN.
  - DOI: 10.1016/j.compbiomed.2023.107031 — Segments EEG into 1-s epochs labeled as PD (medication-off) and HC groups, extracting CSP features for ensemble learning achieving 99.31% accuracy.
  - DOI: 10.1038/s41598-022-26644-7 — Classifies PD patients versus HC from resting-state EEG, segmenting into 10-second epochs and extracting DWT-based entropy features for KNN/SVM.
  - DOI: 10.3389/fnins.2022.957181 — Classifies PD patients (including PD_OFF and PD_ON) versus HC using PSD and PLV features from 3-minute resting-state EEG segments.
  - DOI: 10.1523/ENEURO.0151-19.2019 — Analyzes resting-state scalp EEG to classify PD patients on vs off medication and PD vs HC based on beta waveform shape features.
- **Kernel Notes**: (1) Read participants.tsv to obtain subject-level diagnosis (PD/HC) and medication status. (2) Apply epoch_by_segmentation_hdf5 with segment_length=2.0 s, overlap=0.0 to each subject's continuous resting-state data. (3) Assign the subject's group label (from metadata) to all segments from that subject. (4) Pool segments across subjects for training/testing.

### Primary Task 2: Medication State Classification (PD On vs Off)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PD_OFF` | 0 | Parkinson's disease patient off medication |
  | `PD_ON` | 1 | Parkinson's disease patient on medication |
- **Super Meta Notes**: Labels (on/off medication status) are derived from participant metadata and experimental design. Not from raw event markers. Only PD subjects have medication state; HC subjects excluded for this task.
- **Evidence**:
  - DOI: 10.1038/s41598-022-26644-7 — Uses SanDiego dataset for three-class classification: off-PD vs on-PD vs HC, with binary comparisons off-PD vs on-PD.
  - DOI: 10.3389/fnins.2022.957181 — Performs three-class classification: HC=0, PD_OFF=1, PD_ON=2.
  - DOI: 10.1523/ENEURO.0151-19.2019 — Classifies PD patients on vs off medication based on beta waveform shape features.
- **Kernel Notes**: (1) Read participants.tsv to identify PD subjects with medication state annotations. (2) Filter to only include PD subjects (exclude HC for this task). (3) Apply epoch_by_segmentation_hdf5 with segment_length=2.0 s, overlap=0.0. (4) Assign medication state labels (ON/OFF) from metadata to each segment.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (all events are admin; PD vs HC labels from participants.tsv))
- **Notes**: 65536 is the BioSemi CM_in_range baseline status code - a hardware marker not a task event. PD vs healthy control group labels are in participants.tsv and can be used as disease classification labels. Specific kernel adds participant group annotation.

## Data Quality Notes

- Pure resting-state dataset; all events are BioSemi hardware status codes.
- 65536 (CM_in_range) and 130817 are BioSemi system codes - do not epoch on these.
- PD vs HC group labels available in participants.tsv for disease classification.
- Verify channel count consistency across subjects before pooling.

## References

- **Paper**: Characteristics of Waveform Shape in Parkinson's Disease Detected with Scalp Electroencephalography (DOI/ref: `10.1523/ENEURO.0151-19.2019`)
