# Human Infant EEG for 200 Object Images in Rapid Visual Streams

**Dataset**: `openneuro_ds005106` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005106
**Category**: Sensory/Response | **Subjects**: 42 | **Files (Completed)**: 42 | **Channels**: 32 | **Sampling Rate**: 500 Hz

## Paradigm

Infants viewed 200 distinct object images presented in rapid visual streams (RSVP) while EEG was recorded to study the development of visual object representations. Each numeric trigger code corresponds to one of 200 object IDs; code -1 is a baseline/inter-stimulus marker. The dataset enables decoding of object-specific neural representations in the infant brain.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005106

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `-1` | 43105 | short | raw | Baseline / inter-stimulus marker |
| `155` | 220 | short | raw | Object image 155 onset |
| `123` | 220 | short | raw | Object image 123 onset |
| `72` | 219 | short | raw | Object image 72 onset |
| `147` | 219 | short | raw | Object image 147 onset |
| `(~196 more object codes)` | ~219 each | short | raw | Individual object image onsets (IDs 1-200) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: 200-Way Object Image Classification from Infant EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [numeric codes 1-200]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Object image 1 |
  | `2` | 1 | Object image 2 |
  | ... | ... | ... |
  | `200` | 199 | Object image 200 |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04744-z — Multivariate pattern analysis decoding object identity from epochs -100 to 800ms relative to stimulus onset
  - DOI: 10.31234/osf.io.dzrkq — Time-resolved MVPA decoding object identity from infant EEG during RSVP
- **Kernel Notes**: Exclude event ID -1 (baseline/ITI marker). Object trigger codes 1-200 correspond to 200 distinct object images presented at 5Hz RSVP. (replaces Normal Task 1 from original analysis.md)


## Data Quality Notes

- ~200 unique object trigger codes - each code represents one object image.
- Code -1 is a baseline/ITI marker and should be excluded.
- Infant EEG - expect high noise and movement artifacts.

## References

- **Reference**: `Human Infant EEG Recordings for 200 Object Images Presented in Rapid Visual Streams`
