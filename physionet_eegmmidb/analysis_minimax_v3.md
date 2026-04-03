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
> **Status**: wait_manual_review
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

### Primary Task 1: Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s *, target_events = [`Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Imagine Opening Both Feet Movement`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery |
  | `Imagine Opening Both Fists Movement` | 2 | Both-fists motor imagery |
  | `Imagine Opening Both Feet Movement` | 3 | Both-feet motor imagery |
- **Evidence**:
  - DOI: 10.1109/tla.2018.8291481 — 4-class MI classification (left/right fist, both fists, both feet) using PhysioNet eegmmidb
  - DOI: 10.15368/theses.2017.62 — Binary left vs right fist MI classification with tmax=4.1s on eegmmidb
- **Kernel Notes**: Filter to imagery runs only (R04, R08, R12 for left/right fist; R06, R10, 14 for both fists/feet). Exclude movement runs (R03-R05 etc.) and baseline runs (R01-R02). Use tmax=4.0 s as standard window; paper used 4.1s. (replaces Primary Task 1 from original analysis.md; replaces Normal Task 3 from original analysis.md)

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

## Data Quality Notes

- Age and sex information are not available in the public metadata.
- Known data quality issues: several subjects have noisy recordings; EEG.physionet.org community notes suggest subjects S088, S089, S092, S100, S104 may have unusual recordings.
- T1/T2 event meaning **changes by run number**; always filter by run before assigning class labels.
- `Baseline` (T0) events in task runs are rest periods and should be excluded from MI classification targets.
- Low sampling rate (160 Hz); sufficient for motor imagery but limits high-frequency analysis.

