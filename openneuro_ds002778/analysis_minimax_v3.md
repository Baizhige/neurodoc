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

### Primary Task 1: Parkinson's Disease vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PD` | 1 | Parkinson's disease patient |
  | `HC` | 0 | Healthy control subject |
- **Super Meta Notes**: Derived from participant metadata (participants.tsv). The dataset contains only BioSemi system status markers (65536, 130817) as raw events - no task-related event markers exist. Kernel must read disease status (PD vs HC) from participants.tsv and apply as segment-level labels.
- **Evidence**:
  - DOI: 10.1523/ENEURO.0151-19.2019 — Resting-state EEG classification of PD patients vs healthy controls using beta waveform shape features
  - DOI: 10.1016/j.bspc.2022.104116 — PD vs HC classification using 2-second non-overlapping windows from 3-minute recordings with FAWT entropy features
  - DOI: 10.1016/j.compbiomed.2023.107031 — PD vs HC classification using 1-s epochs with CSP features achieving 99.31% accuracy
  - DOI: 10.1038/s41598-022-26644-7 — Binary PD vs HC classification using 10-second epochs with DWT-based entropy features
  - DOI: 10.3389/fnins.2022.957181 — PD vs HC classification using 1-second segments from 3-minute recordings with PSD and PLV features
  - DOI: 10.3390/diagnostics15060773 — Binary PD vs HC classification using 1-second epochs from first 180 seconds with PSD features
- **Kernel Notes**: (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: PD Medication State Classification (PD_OFF vs PD_ON vs HC)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s *, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HC` | 0 | Healthy control subject |
  | `PD_OFF` | 1 | Parkinson's disease patient off medication |
  | `PD_ON` | 2 | Parkinson's disease patient on medication |
- **Super Meta Notes**: Derived from participant metadata (participants.tsv). Kernel must read medication status (on/off) and disease status from participants.tsv to create three-class labels. The raw events are BioSemi system codes only.
- **Evidence**:
  - DOI: 10.1523/ENEURO.0151-19.2019 — Paired PD off vs on medication comparison and unpaired PD vs control comparison
  - DOI: 10.1038/s41598-022-26644-7 — Three-class classification: off-PD vs on-PD vs HC using DWT-based entropy features
  - DOI: 10.3389/fnins.2022.957181 — Three-class classification: HC=0, PD_OFF=1, PD_ON=2
- **Kernel Notes**: Optional task. For binary PD vs HC, use Primary Task 1. For medication state analysis, extract subject-level medication status from participants.tsv and apply uniformly to all segments from that subject.

## Data Quality Notes

- Pure resting-state dataset; all events are BioSemi hardware status codes.
- 65536 (CM_in_range) and 130817 are BioSemi system codes - do not epoch on these.
- PD vs HC group labels available in participants.tsv for disease classification.
- Verify channel count consistency across subjects before pooling.

