# Ultra High-Density 256-Channel EEG AAD Dataset (Subset)

**Dataset**: `zenodo_4518754` | **Year**: 2021 | **URL**: https://zenodo.org/records/4518754
**Category**: High-level Mental | **Subjects**: 13 | **Files (Completed)**: 156 | **Channels**: 256 | **Sampling Rate**: 1000 Hz

## Paradigm

Thirteen subjects listened to two simultaneously presented Dutch stories (left vs. right ear) and were asked to attend to one speaker while ignoring the other (auditory attention decoding, AAD). EEG was recorded from 256 channels (BioSemi ActiveTwo ultra-high-density, Ag/AgCl) at 1000 Hz. Stories were presented via insert earphones at 60 dBA, with 180 deg spatial separation (left vs. right). Each subject completed multiple trials per session; each recording file corresponds to one trial labeled by attended direction (L/R) encoded in the filename (`S{N}_AAD_{trial}{L/R}.dap`). The kernel creates a single whole-trial `attend_left` or `attend_right` annotation per file.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://zenodo.org/records/4518754

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attend_left` | ~78 | long | raw | Subject attends to the left-ear story for the entire recording |
| `attend_right` | ~78 | long | raw | Subject attends to the right-ear story for the entire recording |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each file has exactly one annotation spanning the entire recording (~6 minutes per trial).

## Tasks

### Primary Task 1: Auditory attention decoding (attend left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s *, overlap = 5.0 s *, target_events = [`attend_left`, `attend_right`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attend_left` | 0 | Attend to left-ear speaker |
  | `attend_right` | 1 | Attend to right-ear speaker |
- **Evidence**:
  - DOI: 10.1088/1741-2552.ac2629 — Uses the ultra-high density 255-channel EEG-AAD dataset to study EEG miniaturization effects on auditory attention decoding, classifying whether subjects attend to the left or right speaker. Paper reports epochs of durations 60, 30, 20, 10, 5, 2 and 1 s with leave-one-epoch-out cross-validation; analysis used 10s decision windows.
- **Kernel Notes**: Uses 10-second sliding window with 5-second overlap across the full recording annotation. (replaces Normal Task 1 from original analysis.md)


## Data Quality Notes

- Ultra-high-density 256-channel EEG; spatial filtering and source analysis are computationally intensive.
- High sampling rate (1000 Hz); consider downsampling to 128 or 64 Hz for typical AAD decoding.
- Stimulus audio files are required for stimulus-reconstruction AAD methods; check availability.
- Only `.dap` files are EEG; auxiliary `.dat` / `.rs3` files are skipped by the kernel.

## References

- **Reference**: Ultra high-density 255-channel EEG-AAD dataset. Zenodo. https://zenodo.org/records/4518754
