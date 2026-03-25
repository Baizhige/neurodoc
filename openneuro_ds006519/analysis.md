# Dataset of Intracranial EEG during Cortical Stimulations Evoking Negative Motor Responses

**Dataset**: `openneuro_ds006519` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006519
**Category**: Action/Output | **Subjects**: 23 | **Files (Completed)**: 35 | **Channels**: 33 | **Sampling Rate**: 4096 Hz

## Paradigm

Patients undergoing presurgical evaluation for drug-resistant epilepsy received intracranial electrical stimulation to map cortical function. The stimulation protocol targeted regions that, when stimulated, evoked negative motor responses (involuntary movement inhibition or arrest). EEG was recorded from intracranial electrodes during pre-stimulation (prestim) and post-stimulation (poststim) periods to characterize neural activity changes associated with negative motor mapping.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006519

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/prestim` | 35 | short | raw | Pre-stimulation baseline period onset |
| `Comment/poststim` | 35 | short | raw | Post-stimulation period onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Comment/prestim`, `Comment/poststim`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Dcs
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006519 DOI: https://doi.org/10.18112/openneuro.ds006519.v1.0.0


### Normal Task 1: Pre- vs Post-Stimulation Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Binary classification of pre- vs post-stimulation neural states. Intracranial EEG from epilepsy patients; electrode locations vary across subjects. Very high sampling rate (4096 Hz); consider downsampling.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/prestim` | 0 | Pre-stimulation baseline period |
 | `Comment/poststim` | 1 | Post-stimulation response period |
## Data Quality Notes

- Intracranial EEG dataset; electrode montage is patient-specific and non-standard.
- Very high sampling rate (4096 Hz); downsampling to <=1000 Hz recommended.
- Small dataset (35 files, 23 subjects); limited sample size.

## References

- **Reference**: `Dataset of intracranial EEG during cortical stimulations evoking negative motor responses`
