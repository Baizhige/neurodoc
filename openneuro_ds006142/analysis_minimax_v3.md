# Essex EEG Movie Memory dataset

**Dataset**: `openneuro_ds006142` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006142
**Category**: High-level Mental | **Subjects**: 27 | **Files (Completed)**: 27 | **Channels**: 64 | **Sampling Rate**: 2048 Hz

## Paradigm

Memory recognition task where participants watched 10-second movie clips and identified whether they remembered them from previous viewings, including time-stamping recognition instants. Clips were shown twice; the first watch (`startOfRememberedClipFirstWatch`, `startOfRecognisedClipFirstWatch`) established encoding, while the second watch (`startOfSecondWatch`) tested recognition. Participants clicked when they recognized clips (`firstRecognitionClick`, `recognitionClick`).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006142

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `recognitionClick` | 6675 | short | raw | Participant clicks upon recognition |
| `endOfClip` | 6094 | short | raw | Movie clip ends |
| `trialStart` | 4153 | long | raw | Trial onset |
| `trialEnd` | 4153 | long | raw | Trial offset |
| `startOfNotRecognisedClip` | 2212 | long | raw | Clip onset - not recognized |
| `startOfSecondWatch` | 1941 | long | raw | Second viewing onset |
| `firstRecognitionClick` | 1881 | short | raw | First recognition click in second watch |
| `startOfRememberedClipFirstWatch` | 1426 | long | raw | First viewing onset - later remembered |
| `startOfRecognisedClipFirstWatch` | 515 | long | raw | First viewing onset - later recognized |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Three-class Movie Memory Recognition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`startOfRememberedClipFirstWatch`, `startOfRecognisedClipFirstWatch`, `startOfNotRecognisedClip`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `startOfNotRecognisedClip` | 0 | Clip not recognized during second viewing |
  | `startOfRecognisedClipFirstWatch` | 1 | Clip recognized during second viewing |
  | `startOfRememberedClipFirstWatch` | 2 | Clip remembered with detail during second viewing |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06203-1 — Three-class memory recognition: not-recognised vs recognised vs remembered movie clips using ERP analysis (tmin=-0.2s, tmax=1.0s) on EEG during first watch onset events.
- **Kernel Notes**: ERP epoching around first-watch clip onsets. For ERP: tmin=-0.2s, tmax=1.0s. For PSD analysis: tmin=-1.0s, tmax=10.0s. Downsample to 512 Hz, apply bandpass 1-30 Hz. (replaces Primary Task 1 from original analysis.md)

### Normal Task 1: Movie Memory Recognition (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Key contrast is remembered vs not-recognized clips at first watch onset. High sampling rate (2048 Hz); consider downsampling.

 | Event | y | Meaning |
 |-------|---|---------|
 | `endOfClip` | 0 | Clip end |
 | `trialStart` | 1 | Trial start |
 | `trialEnd` | 2 | Trial end |
 | `recognitionClick` | 3 | Recognition response |
 | `startOfNotRecognisedClip` | 4 | Not-recognized clip onset |
 | `startOfSecondWatch` | 5 | Second viewing onset |
 | `firstRecognitionClick` | 6 | First recognition click |
 | `startOfRememberedClipFirstWatch` | 7 | First watch - remembered |
 | `startOfRecognisedClipFirstWatch` | 8 | First watch - recognized |

## Data Quality Notes

- High sampling rate (2048 Hz); downsample to 512 Hz for standard ERP analysis.
- Small dataset (27 subjects); limited statistical power.
- Apply bandpass filter (0.1-40 Hz) and artifact rejection prior to epoching.

