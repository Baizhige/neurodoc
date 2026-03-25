# Validation of Sleep Staging with Forehead EEG Patch

**Dataset**: `openneuro_ds006695` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006695
**Category**: Biological State | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 3 | **Sampling Rate**: 500 Hz

## Paradigm

This dataset validates a spectral sleep staging approach using a three-electrode forehead EEG patch against manual scoring from standard polysomnography (PSG). Overnight sleep recordings were collected using a minimally intrusive forehead device, and sleep stages (Wake, N1, N2, N3, REM) were scored both manually and algorithmically. The study examines whether simplified forehead EEG can reliably reproduce standard PSG hypnogram classifications.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006695

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous overnight EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Sleep stage labels (W/N1/N2/N3/REM; mapping dataset-specific)
- **Evidence**: Dataset and references explicitly center on PSG/EEG sleep scoring. Source: https://doi.org/10.3389/frsle.2024.1349537


### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no event markers; sleep stage labels from external PSG scoring)
- **Notes**: No EEG event markers available. Sleep stage labels (Wake/N1/N2/N3/REM) must be derived from PSG hypnogram annotations stored as separate scoring files. Very few channels (3); limited spatial resolution for advanced decoding.
## Data Quality Notes

- Only 3 channels (forehead placement); very limited spatial information.
- Overnight recordings are long (hours); memory-efficient processing needed.
- Sleep stage labels require alignment with PSG hypnogram files.

## References

- **Paper**: `Validation of spectral sleep scoring with polysomnography using forehead EEG device` (DOI: 10.3389/frsle.2024.1349537)
