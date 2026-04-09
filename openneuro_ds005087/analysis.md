## Paradigm

Participants viewed object and word stimuli presented at 5 Hz in rapid visual streams to the left hemifield, right hemifield, or central visual field while performing a red target detection task. Event codes `E 1`/`E 2` (184,320 each) and `E 3` (960) mark the three presentation positions (left/right/center hemifield). Numeric codes `2`/`3`/`1` (92,160/46,080/46,080) likely encode stimulus categories or object identities within each presentation stream.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 184320 | short | raw | Hemifield/position condition 1 |
| `E 2` | 184320 | short | raw | Hemifield/position condition 2 |
| `2` | 92160 | short | raw | Stimulus category/identity code 2 |
| `3` | 46080 | short | raw | Stimulus category/identity code 3 |
| `1` | 46080 | short | raw | Stimulus category/identity code 1 |
| `E 3` | 960 | short | raw | Hemifield/position condition 3 (rare) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

Dataset metadata: 80 subjects, 63 channels, 1000 Hz sampling rate.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Rsvp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005087 DOI: https://doi.org/10.31234/osf.io/a3bpd


### Normal Task 1: Visual Hemifield Presentation Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `E 3` (960) is rare - exclude or treat as separate class. 5 Hz RSVP streams; very short inter-stimulus interval. Verify code meanings from events.tsv (Robinson et al., 2025).

 | Event | y | Meaning |
 |-------|---|---------|
 | `E 1` | 0 | Hemifield/position condition 1 |
 | `E 2` | 1 | Hemifield/position condition 2 |
 | `1` | 2 | Stimulus category code 1 |
 | `2` | 3 | Stimulus category code 2 |
 | `3` | 4 | Stimulus category code 3 |

## Data Quality Notes

- Verify full event decode from events.tsv or Robinson et al., 2025.
- 5 Hz RSVP - confirm exact stimulus duration from events.tsv.
- `E 3` (960) is rare relative to E 1/E 2 (184k each); exclude or treat separately.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005087