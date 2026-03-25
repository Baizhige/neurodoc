# TUH EEG Corpus (Base)

**Dataset**: `tuh_eeg` | **Year**: 2020 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg/v2.0.1/
**Category**: Biological State | **Subjects**: ~14987 | **Files (Completed)**: 69652 | **Channels**: 17-128 | **Sampling Rate**: 250-1000 Hz

## Paradigm

The Temple University Hospital EEG Corpus (v2.0.1) is the largest publicly available clinical EEG archive, containing approximately 69,652 EDF recordings from ~14,987 de-identified patients (Obeid & Picone, 2016). Recordings span routine clinical EEG sessions performed for neurological evaluation (epilepsy monitoring, encephalopathy, post-operative assessment, etc.). Three standard TCP (Temporal Central Parasagittal) referential montages are used: `01_tcp_ar` (average reference), `02_tcp_le` (linked ears), and `03_tcp_ar_a` (alternating average reference). Channel counts vary (17-128) and multiple sampling rates are present (250, 256, 400, 512, 1000 Hz). No structured experiment events exist; EDF annotations are clinical technician notes in free text.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg/v2.0.1/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 69652 | admin | raw | Clinical EEG with unstructured technician annotations; no ML-ready event labels |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> No structured classification annotations. The base corpus is not labeled for any specific ML task; use specialized TUH subsets (tuh_eeg_abnormal, tuh_eeg_seizure, etc.) for supervised learning.

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.3389/fnins.2016.00196


### Normal Task 1: Resting-State Segmentation (epoch_by_segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 5.0 s, overlap = 2.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no labels; use for pretraining / unsupervised learning)
- **Notes**: The base corpus is best used for self-supervised pretraining or large-scale representation learning. Labels (patient age, sex, montage type) can be derived from the EDF header or `eegunity_description` field parsed by the kernel. Ensure montage consistency before cross-recording analysis: process each montage type (01_tcp_ar, 02_tcp_le, 03_tcp_ar_a) separately or re-reference uniformly.
## Data Quality Notes

- No structured ML annotations; this corpus is used as a pretraining source, not for supervised classification.
- Three TCP montages with differing channel layouts; normalize before cross-recording analysis.
- Clinical recordings: variable length, variable channel count, variable sampling rate.
- Sex available from EDF header (M/F/unknown).
- Age is not reliably available in the public release.
- Very large dataset (70k files): batch-processing and memory management are critical.

## References

- **Reference**: Obeid I, Picone J (2016). The Temple University Hospital EEG Data Corpus. *Frontiers in Neuroscience*, 10, 196. https://isip.piconepress.com/projects/tuh_eeg/
