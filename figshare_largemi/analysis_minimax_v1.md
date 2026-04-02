# A Large EEG Motor Imagery Dataset for EEG-BCI

**Dataset**: `figshare_largemi` | **Year**: 2018 | **URL**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698
**Category**: Action/Output | **Subjects**: 13 | **Files (Completed)**: 73 | **Channels**: 22 | **Sampling Rate**: 200 or 1000 Hz (protocol-dependent)

## Paradigm

Thirteen subjects (A-M) participated in multiple EEG motor imagery sessions using five different paradigms (Kaya et al., 2018). EEG was recorded from 22 scalp channels. The paradigms are:
- **CLA**: 3-class MI - left hand, right hand, passive state.
- **HaLT**: 6-class MI - left hand, right hand, passive state, left leg, right leg, tongue.
- **FREEFORM / FREEDOM**: 2-class MI - left hand, right hand (free imagery style).
- **5F**: 5-class finger MI - thumb, index, middle, ring, and pinkie.
- **NoMT**: no-motor-task control sessions (resting state, no imagery).

Trials were cue-based with a blank screen rest period, followed by an arrow/cue presentation indicating the imagery target. Each trial lasted approximately 3 seconds of imagery. NoMT sessions serve as control recordings without motor task events.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Left hand MI` | varies by protocol | short | raw | Left-hand motor imagery cue |
| `Right hand MI` | varies by protocol | short | raw | Right-hand motor imagery cue |
| `Passive state` | varies by protocol | short | raw | Passive / idle state (CLA/HaLT) |
| `Left leg MI` | varies by protocol | short | raw | Left-leg motor imagery cue (HaLT) |
| `Right leg MI` | varies by protocol | short | raw | Right-leg motor imagery cue (HaLT) |
| `Tongue MI` | varies by protocol | short | raw | Tongue motor imagery cue (HaLT) |
| `Thumb MI` | varies by protocol | short | raw | Thumb finger imagery cue (5F) |
| `Index finger MI` | varies by protocol | short | raw | Index finger imagery cue (5F) |
| `Middle finger MI` | varies by protocol | short | raw | Middle finger imagery cue (5F) |
| `Ring finger MI` | varies by protocol | short | raw | Ring finger imagery cue (5F) |
| `Pinkie MI` | varies by protocol | short | raw | Little finger imagery cue (5F) |
| `none` | all NoMT files | admin | raw | No motor task (NoMT protocol control) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Multi-Class Motor Imagery Classification (Dataset Benchmark)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.85 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Left hand MI` | 1 | Left-hand motor imagery (CLA/HaLT/FreeForm) |
  | `Right hand MI` | 2 | Right-hand motor imagery (CLA/HaLT/FreeForm) |
  | `Passive state` | 3 | Passive/idle state (CLA/HaLT) |
  | `Left leg MI` | 4 | Left-leg motor imagery (HaLT) |
  | `Right leg MI` | 6 | Right-leg motor imagery (HaLT) |
  | `Tongue MI` | 5 | Tongue motor imagery (HaLT) |
  | `Thumb MI` | 1 | Thumb finger MI (5F) |
  | `Index finger MI` | 2 | Index finger MI (5F) |
  | `Middle finger MI` | 3 | Middle finger MI (5F) |
  | `Ring finger MI` | 4 | Ring finger MI (5F) |
  | `Pinkie MI` | 5 | Little finger MI (5F) |
- **Super Meta Notes**: (N/A - raw level)
- **Evidence**:
  - DOI: 10.1038/sdata.2018.211 — Dataset paper validates with SVM classifiers on 0.85s epoch windows (170 samples at 200Hz) extracted from stimulus onset to discriminate motor imagery classes across all paradigms.
  - DOI: 10.1109/tnsre.2022.3186442 — Uses 3-second epoch window for binary left vs right MI classification confirming event-based epoching approach.
- **Kernel Notes**: Filter files by protocol type (CLA/HaLT/5F/FREEFORM) before analysis. Use tmax=0.85s for dataset benchmark reproducibility; tmax=3.0s for full trial epochs. Marker codes: CLA/HaLT/FreeForm (1=left,2=right,3=passive,4=left leg,5=tongue,6=right leg); 5F (1=thumb,2=index,3=middle,4=ring,5=pinkie).

### Normal Task 1: Left vs. Right Hand Motor Imagery Classification - CLA/FREEFORM (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: For CLA protocol, also include `Passive state` as class 2 (3-class task). Separate files by protocol type (CLA / FREEFORM / HaLT) for consistent multi-session analysis.

| Event | y | Meaning |
|-------|---|---------|
| `Left hand MI` | 0 | Left-hand motor imagery |
| `Right hand MI` | 1 | Right-hand motor imagery |


### Normal Task 2: 6-Class Motor Imagery Classification - HaLT (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Left hand MI` | 0 | Left-hand MI |
| `Right hand MI` | 1 | Right-hand MI |
| `Passive state` | 2 | Passive/idle state |
| `Left leg MI` | 3 | Left-leg MI |
| `Right leg MI` | 4 | Right-leg MI |
| `Tongue MI` | 5 | Tongue MI |


### Normal Task 3: 5-Finger Motor Imagery Classification - 5F (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Thumb MI` | 0 | Thumb finger MI |
| `Index finger MI` | 1 | Index finger MI |
| `Middle finger MI` | 2 | Middle finger MI |
| `Ring finger MI` | 3 | Ring finger MI |
| `Pinkie MI` | 4 | Little finger MI |


### Normal Task 4: Resting-State Segmentation - NoMT Control (epoch_by_segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 3.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no events; use as unlabeled or negative class)
- **Notes**: NoMT files have event annotation `none` set by kernel; use `epoch_by_segmentation_hdf5` for these files.

## Data Quality Notes

- Multiple paradigms in one dataset; **always filter by protocol type before analysis** (use file path to identify protocol: `CLA`, `HaLT`, `FREEFORM`, `5F`, `NoMT`).
- Sampling rates differ: 200 Hz (5F protocol), 1000 Hz (CLA/HaLT/FREEFORM); process separately or resample to a common rate.
- Subject demographics: 13 subjects (A-M), 9 female / 4 male, age ranges 20-35.
- NoMT sessions have `none` annotations; exclude from MI analysis or use as rest class.

## References

- **Reference**: Kaya M, Binli MK, Ozbay E, Yanar H, Mishchenko Y (2018). A large electroencephalographic motor imagery dataset for electroencephalographic brain computer interfaces. *Scientific Data*, 5, 180211. https://doi.org/10.1038/sdata.2018.211
