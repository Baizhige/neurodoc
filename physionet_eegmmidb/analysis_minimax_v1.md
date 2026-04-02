# EEG Motor Movement/Imagery Database

**Dataset**: `physionet_eegmmidb` | **Year**: 2009 | **URL**: https://physionet.org/content/eegmmidb/1.0.0/
**Category**: Action/Output | **Subjects**: 109 | **Files (Completed)**: 1526 | **Channels**: 64 | **Sampling Rate**: 160 Hz

## Paradigm

One hundred and nine volunteers performed a series of motor movement and motor imagery tasks, recorded with 64 EEG electrodes (international 10-10 system) at 160 Hz using the BCI2000 system (Schalk et al., 2004). Each subject completed 14 runs (R01-R14): two baseline runs (eyes open and eyes closed), and twelve task runs organized in three repeating cycles of four run types. Task runs alternate between real movements and mental imagery of the same movements. Two movement classes are used: left/right fist, and both fists/both feet. Events T0 (rest), T1, and T2 are annotated within each run; T1/T2 meanings differ by run number.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/eegmmidb/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `eyes open` | 109 | rest | raw | Baseline recording with eyes open (R01) |
| `eyes closed` | 109 | rest | raw | Baseline recording with eyes closed (R02) |
| `Baseline` | ~1200 | rest | raw | Rest/inter-trial interval in task runs (T0) |
| `Open Left Fist Movement` | ~327 | short | raw | Real left-fist movement onset (R03/07/11 T1) |
| `Open Right Fist Movement` | ~327 | short | raw | Real right-fist movement onset (R03/07/11 T2) |
| `Imagine Opening Left Fist Movement` | ~327 | short | raw | Left-fist motor imagery onset (R04/08/12 T1) |
| `Imagine Opening Right Fist Movement` | ~327 | short | raw | Right-fist motor imagery onset (R04/08/12 T2) |
| `Open Both Fists Movement` | ~327 | short | raw | Real both-fists movement onset (R05/09/13 T1) |
| `Open Both Feet Movement` | ~327 | short | raw | Real both-feet movement onset (R05/09/13 T2) |
| `Imagine Opening Both Fists Movement` | ~327 | short | raw | Both-fists motor imagery onset (R06/10/14 T1) |
| `Imagine Opening Both Feet Movement` | ~327 | short | raw | Both-feet motor imagery onset (R06/10/14 T2) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Total counts are approximate across all 109 subjects x 3 repetition cycles. Per-subject per-run counts: ~20 T1 + 20 T2 per task run.

## Tasks

### Primary Task 1: 5-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s *, tmax = 4.0 s *, target_events = [`eyes closed`, `Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Imagine Opening Both Feet Movement`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes closed` | 0 | Baseline eyes closed |
  | `Imagine Opening Left Fist Movement` | 1 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 2 | Right-fist motor imagery |
  | `Imagine Opening Both Fists Movement` | 3 | Both-fists motor imagery |
  | `Imagine Opening Both Feet Movement` | 4 | Both-feet motor imagery |
- **Evidence**:
  - DOI: 10.1109/embc.2018.8512590 — 5-class motor imagery classification (eye closed, both feet, both fists, left fist, right fist) using 7-fold cross-validation on first 12 subjects, with epoch length ~4s (651 time steps at 160Hz)
- **Kernel Notes**: Use only imagery runs (R04, R08, R12) plus baseline eyes-closed run (R02). Filter epochs to 0.5-40Hz bandpass. Apply CSP or filter-bank CSP for feature extraction.

### Primary Task 2: Binary Motor Task vs. Resting State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -3.0 s, tmax = 4.0 s, target_events = [`Open Left Fist Movement`, `Open Right Fist Movement`, `Open Both Fists Movement`, `Open Both Feet Movement`, `Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Imagine Opening Both Feet Movement`, `Baseline`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Baseline` | 0 | Resting state (neutral) |
  | `Open Left Fist Movement` | 1 | Any motor execution or imagery task |
  | `Open Right Fist Movement` | 1 | Any motor execution or imagery task |
  | `Open Both Fists Movement` | 1 | Any motor execution or imagery task |
  | `Open Both Feet Movement` | 1 | Any motor execution or imagery task |
  | `Imagine Opening Left Fist Movement` | 1 | Any motor execution or imagery task |
  | `Imagine Opening Right Fist Movement` | 1 | Any motor execution or imagery task |
  | `Imagine Opening Both Fists Movement` | 1 | Any motor execution or imagery task |
  | `Imagine Opening Both Feet Movement` | 1 | Any motor execution or imagery task |
- **Evidence**:
  - DOI: 10.3389/fnins.2021.660032 — Binary classification of motor execution and motor imagery tasks vs. resting state using DFA-derived Hurst exponent features, achieving 70-76% accuracy with LDA classifier
- **Kernel Notes**: Use motor runs (R03-R06, R07-R10, R11-R14). Extract features from 2s sliding windows with 100ms shift. Use channels C3, Cz, C4 (motor cortex). Combine all movement and imagery events into class 1.

### Primary Task 3: Readiness Potential Detection
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s, overlap = 0.0 *, target_events = N/A (continuous segmentation)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | TP | 1 | Detected RP midpoint falls within -2s to 200ms around movement onset |
  | FP | 0 | Detected RP in rest intervals |
- **Super Meta Notes**: Labels derived from movement onset markers; TP defined as detection window midpoint within -2s to 200ms of movement onset. Binary detection: presence/absence of readiness potential.
- **Evidence**:
  - DOI: 10.1016/j.cmpbup.2021.100027 — Readiness potential (RP) detection from single-channel EEG using PhysioNet R03 movement dataset (real movement intention), achieving 85.4% accuracy, 76.5% sensitivity
- **Kernel Notes**: Use movement runs (R03, R07, R11) for real movement onset detection. Bandpass filter 1-30Hz. Apply lowpass 5Hz for RP detection. Evaluate detection within -2s to 200ms window around movement onset.

### Normal Task 1: Left vs. Right Fist Motor Imagery (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Use only runs R04, R08, R12 (imagery sessions). Run numbers are encoded in the filename (positions 5-7, e.g., `S001R04.edf`). Exclude baseline runs (R01, R02) and movement runs (R03, R07, R11) for pure imagery analysis.

| Event | y | Meaning |
|-------|---|---------|
| `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery (R04/08/12) |
| `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery (R04/08/12) |


### Normal Task 2: Both Fists vs. Both Feet Motor Imagery (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Imagine Opening Both Fists Movement` | 0 | Both-fists motor imagery (R06/10/14) |
| `Imagine Opening Both Feet Movement` | 1 | Both-feet motor imagery (R06/10/14) |


### Normal Task 3: 4-Class Motor Imagery (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Imagine Opening Left Fist Movement` | 0 | Left-fist MI |
| `Imagine Opening Right Fist Movement` | 1 | Right-fist MI |
| `Imagine Opening Both Fists Movement` | 2 | Both-fists MI |
| `Imagine Opening Both Feet Movement` | 3 | Both-feet MI |

## Data Quality Notes

- Age and sex information are not available in the public metadata.
- Known data quality issues: several subjects have noisy recordings; EEG.physionet.org community notes suggest subjects S088, S089, S092, S100, S104 may have unusual recordings.
- T1/T2 event meaning **changes by run number**; always filter by run before assigning class labels.
- `Baseline` (T0) events in task runs are rest periods and should be excluded from MI classification targets.
- Low sampling rate (160 Hz); sufficient for motor imagery but limits high-frequency analysis.

## References

- **Reference**: Schalk G, McFarland DJ, Hinterberger T, Birbaumer N, Wolpaw JR (2004). BCI2000: A general-purpose brain-computer interface (BCI) system. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034-1043. https://physionet.org/content/eegmmidb/1.0.0/
