# EEG: Depression rest

**Dataset**: `openneuro_ds003478` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003478
**Category**: Biological State | **Subjects**: 122 | **Files (Completed)**: 243
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recording featuring alternating one-minute intervals of eyes-open and eyes-closed conditions in participants with varying scores on the Beck Depression Inventory (BDI). The study aims to identify EEG biomarkers of depression severity. Each session includes multiple alternating eyes-open and eyes-closed blocks, with `Start and Finish` markers indicating session boundaries. STATUS is a BioSemi admin marker.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003478

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Eyes Open` | 368 (files) | long | raw | Eyes-open resting state block (~1 min) |
| `Eyes Closed` | 368 (files) | long | raw | Eyes-closed resting state block (~1 min) |
| `STATUS` | 243 (files) | admin | raw | BioSemi system status marker - exclude |
| `Start and Finish` | 184 (files) | admin | raw | Session start/end boundary marker - exclude |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Depression status classification from resting-state EEG spatial correlations
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 93.68 s *, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Control` | 0 | Healthy controls (BDI≤7) |
  | `Depressive-cMDD` | 1 | Current Major Depressive Disorder (BDI≥13, clinical interview confirmed) |
  | `Depressive-pMDD` | 2 | Past Major Depressive Disorder (BDI≥13, clinical interview confirmed) |
  | `Depressive-None` | 3 | Depressive symptoms without MDD history (BDI≥13) |
- **Super Meta Notes**: Labels derived from BDI scores in participants.tsv. BDI<10=Control, BDI≥13=Depressive. Clinical interview further divided depressive group into cMDD (current MDD), pMDD (past MDD), and None (depressive symptoms but no MDD history). The paper uses binary discrimination: cMDD vs others, pMDD vs others.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Used openneuro_ds003478 to investigate spatial correlations of infraslow amplitude fluctuations (0.05-0.1Hz) of theta/alpha/beta oscillations during eyes-open and eyes-closed rest, classifying current vs past MDD patients vs controls based on BDI-derived group labels.
- **Kernel Notes**: Remove initial and final 10s of each segment as artifact cleanup. Compute spatial correlation matrices from amplitude fluctuations (0.05-0.1Hz) in theta/alpha/beta bands. Use whole segments without traditional epoching.

### Primary Task 2: Depression severity regression (BDI prediction)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 93.68 s *, overlap = 0.0, target_events = [`Eyes Open`, `Eyes Closed`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | continuous | BDI score | Beck Depression Inventory score (0-63 scale) |
- **Super Meta Notes**: Regression target is the continuous BDI score from participants.tsv. Each subject has one BDI score. Eyes-open and eyes-closed segments from same subject share the same BDI label.
- **Evidence**:
  - DOI: 10.3389/fpsyt.2023.1132996 — Study used BDI scores to define depression groups (BDI≤7 Control, BDI≥13 Depressive), confirming BDI is the primary clinical measure in this dataset.
- **Kernel Notes**: Map each segment to its subject's BDI score from participants.tsv. Features extracted from spatial correlations or band power can be used to predict continuous BDI values.

### Normal Task 1: Eyes Open vs Eyes Closed Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is BioSemi admin marker; `Start and Finish` marks session boundaries - both excluded. Eyes-open vs eyes-closed is the primary binary classification. BDI scores in participants.tsv can serve as continuous regression targets for depression severity prediction.

| Event | y | Meaning |
 |-------|---|------|
 | `Eyes Open` | 0 | Eyes-open resting state (~1 min block) |
 | `Eyes Closed` | 1 | Eyes-closed resting state (~1 min block) |

## Data Quality Notes

- `STATUS` is BioSemi hardware marker - exclude.
- `Start and Finish` marks session boundaries - admin marker, exclude.
- Large dataset: 122 subjects, 243 files; subject-level BDI scores available for depression prediction.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `EEG: Depression rest`
