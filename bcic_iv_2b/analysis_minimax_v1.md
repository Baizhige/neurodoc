# BCI Competition IV Dataset 2b (Left/Right Hand Motor Imagery)

**Dataset**: `bcic_iv_2b` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2b.html
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 46 | **Channels**: 6 | **Sampling Rate**: 250 Hz

## Paradigm

Nine subjects (B01-B09) performed two-class cued motor imagery of the left and right hand (BCI Competition IV, 2008). Only 3 bipolar EEG channels over the sensorimotor cortex (C3, Cz, C4) and 3 EOG channels were recorded (0.5-100 Hz, notch at 50 Hz). Each subject underwent 5 sessions over two days: sessions 1-2 without feedback, sessions 3-5 with BCI feedback. Each session contained multiple runs of ~60-80 trials per class. A fixation cross preceded each trial, followed by a visual left/right arrow cue for 1.25 s, then a 4-second imagery period with optional BCI cursor feedback. Evaluation sessions (suffix `E.gdf`) have unknown cue labels that the kernel resolves from companion `.mat` files.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iv/desc_2b.html

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Start of a trial` | ~1520/subject | admin | raw | Trial-onset fixation cross (pre-cue) |
| `Cue onset left (class 1)` | ~380/subject | short | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | ~380/subject | short | raw | Right-hand motor imagery cue |
| `BCI feedback (continuous)` | ~760/subject | admin | raw | BCI feedback period (sessions 3-5 only) |
| `Idling EEG (eyes open)` | rare | admin | raw | Resting state with eyes open |
| `Idling EEG (eyes closed)` | rare | admin | raw | Resting state with eyes closed |
| `Rejected trial` | variable | admin | raw | Experimenter-rejected trial |
| `Start of a new run` | ~40/subject | admin | raw | Run boundary marker |
| `Horizontal eye movement` | rare | admin | raw | Eye artifact marker |
| `Vertical eye movement` | rare | admin | raw | Eye artifact marker |
| `Eye rotation` | rare | admin | raw | Eye artifact marker |
| `Eye blinks` | rare | admin | raw | Eye artifact marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are approximate per subject (all sessions combined). GDF numeric codes remapped to human-readable strings by kernel.

## Tasks

### Primary Task 1: Binary Left/Right Hand Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1109/tnsre.2022.3156076 — Confirms two-class motor imagery classification (left vs right hand) is the primary task for this dataset, uses event-based epochs with approximately 4s window.
  - DOI: 10.3389/fnins.2020.00918 — Uses dataset for binary motor imagery classification.
  - DOI: 10.3390/s19010210 — Uses dataset for two-class motor imagery with 4s window for augmentation.
  - DOI: 10.3390/s20164485 — Uses dataset for left/right motor imagery classification.
  - DOI: desc_2b.pdf — Official BCI Competition IV Dataset 2b description defines binary left-versus-right hand motor imagery decoding as the benchmark task (tmin=0s at cue onset).
- **Kernel Notes**: Extract epochs centered on cue onset events. EOG channels should be excluded. Apply spatial filtering (CSP recommended due to only 3 EEG channels C3, Cz, C4). Sessions 1-2 provide no-feedback baseline; sessions 3-5 include BCI feedback.

### Normal Task 1: Binary Motor Imagery Classification - Left vs. Right Hand (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude all `admin`-type events. For longitudinal analysis, separate sessions 1-2 (no feedback) from sessions 3-5 (with BCI feedback). EOG channels (`EOG:ch01`, `EOG:ch02`, `EOG:ch03`) should be excluded before analysis. With only 3 EEG channels, spatial filtering (CSP) is especially important.

| Event | y | Meaning |
|-------|---|---------|
| `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
| `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
## Data Quality Notes

- Only 3 EEG channels (C3, Cz, C4): very limited spatial resolution; spatial filtering (CSP) is critical.
- EOG channels present; apply artifact regression before MI classification.
- Feedback sessions (3-5) may show learning effects; sessions 1-2 provide cleaner baseline.
- Evaluation files use `Cue unknown (class 783)` initially; companion `.mat` files are required by the kernel to resolve labels.
- Subject demographics: B01-B09, ages 20-32, mixed sex.
- 46 files total across 9 subjects x 5 sessions; some sessions may have ext

## Data Quality Notes

- Only 3 EEG channels (C3, Cz, C4): very limited spatial resolution; spatial filtering (CSP) is critical.
- EOG channels present; apply artifact regression before MI classification.
- Feedback sessions (3-5) may show learning effects; sessions 1-2 provide cleaner baseline.
- Evaluation files use `Cue unknown (class 783)` initially; companion `.mat` files are required by the kernel to resolve labels.
- Subject demographics: B01-B09, ages 20-32, mixed sex.
- 46 files total across 9 subjects x 5 sessions; some sessions may have extra evaluation runs.

## References

- **Reference**: Leeb R, Lee F, Keinrath C, Scherer R, Bischoff H, Pfurtscheller G (2008). BCI Competition 2008 - Graz Data Set B. Institute for Knowledge Discovery, Graz University of Technology. https://www.bbci.de/competition/iv/desc_2b.html
