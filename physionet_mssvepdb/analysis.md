# Multi-Stimulus SSVEP Database

**Dataset**: `physionet_mssvepdb` | **Year**: 2021 | **URL**: N/A
**Category**: Sensory/Response | **Subjects**: 11 | **Files (Completed)**: 235 | **Channels**: 14 (Emotiv) or 256 (BrainProducts) | **Sampling Rate**: 128 Hz (dataset3) or 250 Hz (datasets 1-2)

## Paradigm

Eleven subjects performed steady-state visual evoked potential (SSVEP) tasks across three recording datasets with different EEG hardware (Nakanishi et al., 2018). Subjects fixated on flickering visual stimuli at different frequencies while EEG was recorded. Datasets 1 and 2 used a BrainProducts system (256 channels, 250 Hz); dataset 3 used an Emotiv EPOC (14 channels, 128 Hz). Each recording corresponds to one SSVEP stimulus condition (frequency). The kernel creates a single whole-recording `SSVEP` annotation for each file; the stimulus frequency is encoded in the filename/subdirectory.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.physionet.org/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `SSVEP` | 235 | long | raw | SSVEP stimulus period (spans entire recording); frequency encoded in filename |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Stimulus frequency information must be parsed from the filename or subdirectory (e.g., frequency in Hz). Each file corresponds to one stimulus frequency condition.

## Tasks

### Primary Task 1: SSVEP target/frequency decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `stim` or `Annotation`
- **Target Definition**: Stimulus frequency or target index
- **Evidence**: SSVEP paradigm is explicitly stated in dataset metadata/reference. Source: https://www.physionet.org/ DOI: https://doi.org/10.1109/tbme.2017.2694818


### Normal Task 1: SSVEP Frequency Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 2.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Frequency label derived from filename; e.g., map each stimulus frequency to a class index.
- **Notes**: Stimulus frequencies and their mapping to class indices must be parsed from file paths or metadata. Process datasets 1/2 (BrainProducts, 256ch, 250Hz) and dataset 3 (Emotiv, 14ch, 128Hz) **separately** due to different channel counts and sampling rates.
## Data Quality Notes

- Hardware differences across datasets: datasets 1-2 (BrainProducts, 256 channels, 250 Hz) vs. dataset 3 (Emotiv EPOC, 14 channels, 128 Hz); do not mix datasets in cross-subject analysis without normalization.
- Frequency labels are encoded in filenames, not event annotations; parse filenames to obtain classification targets.
- Age range: 24-39 years; sex: ~171 male / 64 female recording sessions.
- For SSVEP analysis, focus on occipital channels (Oz, O1, O2, POz) from the BrainProducts recordings.

## References

- **Reference**: Nakanishi M et al. (2018). Enhancing Detection of SSVEPs for a High-Speed Brain Speller Using Task-Related Component Analysis. *IEEE Trans. Biomed. Eng.* https://www.physionet.org/
