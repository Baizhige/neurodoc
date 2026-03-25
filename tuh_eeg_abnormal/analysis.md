# TUH EEG Abnormal Corpus

**Dataset**: `tuh_eeg_abnormal` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_abnormal/v3.0.1/
**Category**: Biological State | **Subjects**: ~2983 sessions | **Files (Completed)**: 2983 | **Channels**: 27-36 | **Sampling Rate**: 250-512 Hz

## Paradigm

The TUH EEG Abnormal Corpus (v3.0.1) is a clinically annotated subset of the TUH EEG Corpus where each recording has been classified as **normal** or **abnormal** by board-certified neurologists (Lopez et al., 2015). Recordings are routine clinical EEG sessions acquired in an outpatient setting at Temple University Hospital. The normal/abnormal label reflects the overall clinical impression of the EEG recording, not individual event annotations. The label is encoded in the directory path (`normal/` or `abnormal/`) and extracted by the kernel to create a single whole-recording annotation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_abnormal/v3.0.1/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `normal:1` | 1517 | long | raw | Normal EEG recording (full-recording label) |
| `abnormal:1` | 1466 | long | raw | Abnormal EEG recording (full-recording label) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each recording has exactly one annotation spanning its full duration. `normal:1` = one "normal" annotation. Label derived from parent directory (`normal/` or `abnormal/`).

## Tasks

### Primary Task 1: Normal vs abnormal EEG recording classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Recording-level normal/abnormal diagnostic label.
- **Evidence**: TUH Abnormal Corpus is explicitly curated for normal-versus-abnormal EEG classification. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.3389/fnins.2016.00196


### Normal Task 1: Normal vs. Abnormal EEG Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: The annotation spans the entire recording; use `epoch_by_long_event_hdf5` with sliding windows. Parse the label prefix before the colon (`:`) to extract the class name. Near-balanced classes: 1517 normal vs. 1466 abnormal.

| Event | y | Meaning |
|-------|---|---------|
| `normal:1` | 0 | Normal EEG |
| `abnormal:1` | 1 | Abnormal EEG |
## Data Quality Notes

- Sex is not reliably available in this subset.
- Variable channel count (27-36) and sampling rate (250-512 Hz) across recordings; normalize before cross-recording analysis.
- Whole-recording global labels; local event patterns within recordings are not annotated.
- Train/dev split is encoded in directory path; respect the split for proper evaluation.

## References

- **Reference**: Lopez S et al. (2015). Analysis of Factors that Affect EEG Signal Quality. *EMBC 2015*. Obeid I, Picone J (2016). The Temple University Hospital EEG Data Corpus. https://isip.piconepress.com/projects/tuh_eeg/
