# Research data supporting 'EEG recording during playing MOBA game'

**Dataset**: `openneuro_ds005520` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005520
**Category**: Complex Applied | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 60 | **Sampling Rate**: 256 Hz

## Paradigm

Participants played a real MOBA (Multiplayer Online Battle Arena) game while 60-channel EEG was recorded alongside resting-state sessions. Trigger codes mark game events such as kills, deaths, and other in-game actions. The study investigates neural correlates of naturalistic gaming behavior.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005520

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `13` | 834 | long | raw | In-game event code 13 (decode from events.tsv) |
| `14` | 520 | long | raw | In-game event code 14 (decode from events.tsv) |
| `66` | 137 | long | raw | In-game event code 66 (decode from events.tsv) |
| `666` | 89 | long | raw | In-game event code 666 (decode from events.tsv) |
| `444` | 45 | long | raw | In-game event code 444 (decode from events.tsv) |
| `-255` | 9 | admin | raw | System overflow / boundary marker |
| `4` | 9 | long | raw | In-game event code 4 (decode from events.tsv) |
| `100008` | 9 | long | raw | In-game event code 100008 (decode from events.tsv) |
| `164` | 3 | long | raw | In-game event code 164 (decode from events.tsv) |
| `244` | 1 | long | raw | In-game event code 244 (decode from events.tsv) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: In-game Kill vs Death Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = +2.0 s, target_events = [`13`, `14`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `13` | 0 | In-game kill event (marker 13) |
  | `14` | 1 | In-game death event (marker 14) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05435-5 — Confirms binary classification of kill (13) vs death (14) events with epochs spanning -1000ms to +2000ms
  - DOI: 10.18112/openneuro.ds005520.v1.0.1 — Confirms segmentation of EEG epochs time-locked to kills (13) and deaths (14) with baseline correction [-0.2s, 0s]
- **Kernel Notes**: Apply baseline correction from -200ms to 0s as per paper. Exclude intervals <1000ms between consecutive events to avoid epoch overlap.

### Primary Task 2: Multi-class Game Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = +2.0 s, target_events = [`13`, `14`, `66`, `666`, `444`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `13` | 0 | In-game kill event |
  | `14` | 1 | In-game death event |
  | `66` | 2 | Game start event |
  | `666` | 3 | Game victory event |
  | `444` | 4 | Game defeat event |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05435-5 — Confirms multi-class classification including game start (66), victory (666), defeat (444) events derived from frame-by-frame video analysis
- **Kernel Notes**: Validate event ID mapping from events.tsv. Apply bandpass filter (1-40 Hz) and artifact rejection. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Resting State Eye Open
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *
- **Label Route**: `Annotation`
- **Target Definition**: N/A — unannotated resting-state segments extracted from eye-open resting recordings
- **Evidence**: OpenNeuro metadata indicates resting-state recordings were collected
- **Kernel Notes**: Verify from dataset README which runs correspond to eye-open resting. Apply preprocessing filter 1-40 Hz.

### Normal Task 2: Resting State Eye Closed
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *
- **Label Route**: `Annotation`
- **Target Definition**: N/A — unannotated resting-state segments extracted from eye-closed resting recordings
- **Evidence**: OpenNeuro metadata indicates resting-state recordings were collected
- **Kernel Notes**: Verify from dataset README which runs correspond to eye-closed resting. Apply preprocessing filter 1-40 Hz.

## Data Quality Notes

- Event codes require decoding from dataset events.tsv or README.
- Very small dataset (23 subjects, 23 files); rare codes (164, 244, -255) have <10 occurrences total.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

