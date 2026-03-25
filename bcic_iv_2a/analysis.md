# BCI Competition IV Dataset 2a (4-Class Motor Imagery)

**Dataset**: `bcic_iv_2a` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2a.html
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 18 | **Channels**: 25 | **Sampling Rate**: 250 Hz

## Paradigm

Nine subjects (A01-A09) performed four-class cued motor imagery (BCI Competition IV, 2008): left hand, right hand, feet, and tongue. Each session contained 6 runs of 48 trials each (288 trials per session), balanced across 4 classes (72 trials per class). A fixation cross preceded each trial, followed by a visual arrow cue indicating the imagery class, and a 4-second imagery period. Short resting intervals separated trials. Each subject was recorded in two sessions: a training session (suffix `T.gdf`) with event labels, and an evaluation session (suffix `E.gdf`) with initially unknown labels replaced by kernel-loaded `.mat` companion files. EEG was recorded from 22 channels (standard 10-20, sensorimotor focus) plus 3 bipolar EOG channels (filtered 0.5-100 Hz, notch at 50 Hz).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iv/desc_2a.html

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Start of a trial` | ~576/subject | admin | raw | Trial-onset fixation cross (pre-cue marker) |
| `Cue onset left (class 1)` | ~144/subject | short | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | ~144/subject | short | raw | Right-hand motor imagery cue |
| `Cue onset foot (class 3)` | ~144/subject | short | raw | Feet motor imagery cue |
| `Cue onset tongue (class 4)` | ~144/subject | short | raw | Tongue motor imagery cue |
| `Idling EEG (eyes open)` | ~9/subject | admin | raw | Resting state with eyes open |
| `Idling EEG (eyes closed)` | ~9/subject | admin | raw | Resting state with eyes closed |
| `Rejected trial` | variable | admin | raw | Trial rejected by experimenter |
| `Start of a new run` | ~12/subject | admin | raw | Run boundary marker |
| `Eye movements` | rare | admin | raw | Artifactual eye movement event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are approximate per subject (Training + Evaluation combined). The kernel remaps all GDF numeric codes to human-readable strings.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: The official BCI Competition IV Dataset 2a description defines four-class motor imagery decoding (left hand, right hand, feet, tongue) as the benchmark task. Source: https://www.bbci.de/competition/iv/desc_2a.html Official description PDF: `references/desc_2a.pdf`


### Normal Task 1: 4-Class Motor Imagery Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Use only the 4 cue-onset events as classification targets. The 4-second imagery window begins at cue onset. Evaluation sessions (E files) have cue labels resolved by the kernel from companion `.mat` files. Exclude all `admin`-type events. EOG channels (`EOG-left`, `EOG-central`, `EOG-right`) should be excluded before analysis.

| Event | y | Meaning |
|-------|---|---------|
| `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
| `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
| `Cue onset foot (class 3)` | 2 | Feet motor imagery |
| `Cue onset tongue (class 4)` | 3 | Tongue motor imagery |


### Normal Task 2: Binary Motor Imagery - Left vs. Right Hand (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Subset of Task 1. Discard feet and tongue trials.

| Event | y | Meaning |
|-------|---|---------|
| `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
| `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
## Data Quality Notes

- Rejected trials (variable per subject/session) should be excluded from analysis.
- EOG channels present; apply artifact rejection or regression before motor imagery classification.
- Evaluation files initially contain `Cue unknown (class 783)` entries that the kernel replaces with proper class labels from `.mat` companion files; verify companion file presence.
- Class balance is enforced by design (72 trials per class per session); minor imbalance may arise from rejected trials.
- Subject age range: 17-26 years; 7 female, 2 male subjects.

## References

- **Reference**: Brunner C, Leeb R, Muller-Putz G, Schlogl A, Pfurtscheller G (2008). BCI Competition 2008 - Graz Data Set A. Institute for Knowledge Discovery, Graz University of Technology. https://www.bbci.de/competition/iv/desc_2a.html
