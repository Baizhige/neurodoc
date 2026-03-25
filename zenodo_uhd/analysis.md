# Ultra High-Density 256-Channel EEG AAD Dataset

**Dataset**: `zenodo_uhd` | **Year**: 2021 | **URL**: N/A
**Category**: High-level Mental | **Subjects**: 13 | **Files (Completed)**: 156 | **Channels**: 256 | **Sampling Rate**: 1000 Hz

## Paradigm

Thirteen subjects listened to two simultaneously presented stories (one in each ear) and attended to one speaker while ignoring the other (auditory attention decoding, AAD). Ultra-high-density EEG was recorded from 256 channels (BioSemi ActiveTwo, Ag/AgCl) at 1000 Hz. Subjects completed multiple trials; each recording file corresponds to one trial, with the attended direction (left/right) encoded in the filename (`S{N}_AAD_{trial}{L/R}.dap`). The kernel creates a whole-trial `attend_left` or `attend_right` annotation per file. This dataset has the same structure as `zenodo_4518754` and uses an identical kernel implementation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://zenodo.org/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attend_left` | ~78 | long | raw | Subject attends to the left-ear story for the entire recording |
| `attend_right` | ~78 | long | raw | Subject attends to the right-ear story for the entire recording |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each file has exactly one annotation spanning the entire recording.

## Tasks

### Primary Task 1: Ultra-high-density auditory attention decoding (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Trial-level attended direction labels (`attend_left`/`attend_right`).
- **Evidence**: UHD EEG release documents auditory attention decoding as its central benchmark task. Source: https://zenodo.org/


### Normal Task 1: Auditory Attention Decoding - Left vs. Right (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s, overlap = 5.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only `.dap` header files are processed; `.dat` and `.rs3` auxiliary files are skipped. Numeric stimulus event codes (1000001, 100255, 800000, 800001) may also appear from the stimulus delivery system; use the whole-trial `attend_*` label for the primary target.

| Event | y | Meaning |
|-------|---|---------|
| `attend_left` | 0 | Attend to left-ear speaker |
| `attend_right` | 1 | Attend to right-ear speaker |
## Data Quality Notes

- Ultra-high-density 256-channel EEG; computationally intensive.
- High sampling rate (1000 Hz); consider downsampling to 64 or 128 Hz for typical AAD decoding.
- Same structure and kernel as `zenodo_4518754`; may be processed identically.
- No age or sex information available.

## References

- **Reference**: Ultra High-Density 256-Channel EEG Auditory Attention Decoding Dataset. Zenodo.
