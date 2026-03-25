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

### Primary Task 1: Publisher-defined BIDS task: Movie Memory
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006142 DOI: https://doi.org/10.18112/openneuro.ds006142.v1.0.2


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

## References

- **Paper**: `Annotating, Understanding, and Predicting Long-term Video Memorability`
