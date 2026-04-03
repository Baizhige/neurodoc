# EEG Attention RSVP Experiment 1

**Dataset**: `openneuro_ds004816` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004816
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 40 | **Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task investigating the neural dynamics of prioritizing task-relevant information using stimuli composed of small letters on large objects. Event codes `E 1` and `E 2` are the dominant condition markers (69,120 each total); codes `1` and `0` appear 31,104 times each; `E 3` appears 1,920 times. The `E 1`/`E 2` pair likely marks the two main stimulus streams (letter-prioritized vs object-prioritized). Codes `1`/`0` mark target-present vs target-absent trials. `Event/E x` variants are the same conditions from different recordings.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004816

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 69120 | short | raw | RSVP condition 1 (primary stream) |
| `E 2` | 69120 | short | raw | RSVP condition 2 (secondary stream) |
| `1` | 31104 | short | raw | Target-present marker |
| `0` | 31104 | short | raw | Target-absent marker |
| `Event/E 1` | 6912 | short | raw | RSVP condition 1 (alternate format) |
| `Event/E 2` | 6912 | short | raw | RSVP condition 2 (alternate format) |
| `E 3` | 1920 | short | raw | RSVP condition 3 (rare) |
| `Event/E 3` | 192 | short | raw | RSVP condition 3 (alternate format, rare) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: RSVP Stimulus Decoding (Object vs Letter Task)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | Object task condition (attend to objects) |
  | `E 2` | 1 | Letter task condition (attend to letters) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding of 16 object images and 16 letters from epochs time-locked to stimulus onset (tmin=-0.1s, tmax=1.0s), comparing decoding accuracy between object-task and letter-task conditions.
- **Kernel Notes**: The paper epochs around stimulus onset for each RSVP trial. The dataset contains 69,120 events each for `E 1` and `E 2`, representing the two attention conditions. Stimulus-level labels (16 objects, 16 letters, 4 categories, animacy) can be derived from the raw stimulus presentation timing if events.tsv contains stimulus-specific markers. Verify event ID mapping from events.tsv to confirm whether individual stimulus events within each condition are available.

### Primary Task 2: RSVP Target Detection (Target-present vs Target-absent)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1`, `0`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Target-present trial |
  | `0` | 1 | Target-absent trial |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Dataset description indicates target-present vs target-absent markers in the event stream.
- **Kernel Notes**: The `1` and `0` markers (31,104 each) indicate whether a target was present in the RSVP stream. These epochs can be used for P300 or oddball analysis to detect neural responses to target stimuli.

### Normal Task 1: RSVP Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `1`, `0`]
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `Event/E 1` and `Event/E 2` are alternate-format versions of the same codes; merge with `E 1`/`E 2` if needed. `E 3` (1,920) and `Event/E 3` (192) are rare - exclude or treat as separate class. 5 Hz RSVP; verify stimulus duration from events.tsv.

 | Event | y | Meaning |
 |-------|---|---------|
 | `E 1` | 0 | RSVP condition 1 |
 | `E 2` | 1 | RSVP condition 2 |
 | `1` | 2 | Target-present |
 | `0` | 3 | Target-absent |

## Data Quality Notes

- `Event/E x` variants likely from different recording format; merge with `E x` before epoching.
- `E 3` and `Event/E 3` are rare codes - may represent catch trials or errors.
- High-count RSVP paradigm; very large epoch counts per subject.

