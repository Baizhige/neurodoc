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

### Primary Task 1: In-Game Event Classification (Kill/Death/Game State)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`13`, `14`, `66`, `666`, `444`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `13` | 0 | Kill event (in-game kill) |
  | `14` | 1 | Death event (in-game death) |
  | `66` | 2 | Game start |
  | `666` | 3 | Game victory |
  | `444` | 4 | Game defeat |
- **Super Meta Notes**: N/A - raw event labels used directly from stimulus markers
- **Evidence**:
  - DOI: 10.1038/s41597.025.05435.5 — Paper presents the openneuro_ds005520 dataset with 64-channel EEG from 23 participants playing MOBA (Honor of Kings), containing precise timestamps for in-game kills (marker 13), deaths (marker 14), game start (66), victory (666), and defeat (444) events derived from frame-by-frame video analysis, validating data quality through ERP P300 analysis and time-frequency decomposition of epochs spanning -1000ms to +2000ms around these events.
- **Kernel Notes**: Epoch from -1.0s to +2.0s relative to each trigger event. Exclude intervals <1.0s between consecutive events to avoid epoch overlap. Map stimulus event codes 13, 14, 66, 666, 444 to binary (kill vs death) or multi-class labels as needed. Apply bandpass filter 1-40 Hz and artifact rejection.

### Normal Task 1: MOBA Game Events (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical trigger codes require mapping from events.tsv or dataset README. Very small dataset (23 subjects); low event counts for rare codes.

 | Event | y | Meaning |
 |-------|---|---------|
 | `13` | 0 | Game event 13 |
 | `14` | 1 | Game event 14 |
 | `66` | 2 | Game event 66 |
 | `666` | 3 | Game event 666 |
 | `444` | 4 | Game event 444 |
 | `-255` | 5 | System marker |
 | `4` | 6 | Game event 4 |
 | `100008` | 7 | Game event 100008 |
 | `164` | 8 | Game event 164 |
 | `244` | 9 | Game event 244 |

## Data Quality Notes

- Event codes require decoding from dataset events.tsv or README.
- Very small dataset (23 subjects, 23 files); rare codes (164, 244, -255) have <10 occurrences total.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `EEG recording during playing MOBA game`
