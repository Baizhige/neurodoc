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

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://doi.org/10.1523/ENEURO.0151-19.2019


### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (all events are admin; PD vs HC labels from participants.tsv))
- **Notes**: 65536 is the BioSemi CM_in_range baseline status code - a hardware marker not a task event. PD vs healthy control group labels are in participants.tsv and can be used as subject-level binary labels. Specific kernel adds participant group annotation.
## Data Quality Notes

- Pure resting-state dataset; all events are BioSemi hardware status codes.
- 65536 (CM_in_range) and 130817 are BioSemi system codes - do not epoch on these.
- PD vs HC group labels available in participants.tsv for disease classification.
- Verify channel count consistency across subjects before pooling.

## References

- **Paper**: Characteristics of Waveform Shape in Parkinson's Disease Detected with Scalp Electroencephalography (DOI/ref: `10.1523/ENEURO.0151-19.2019`)
