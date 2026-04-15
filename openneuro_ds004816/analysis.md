# EEG Attention RSVP Experiment 1

**Dataset**: `openneuro_ds004816` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004816
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 40 | **Channels**: 63 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task investigating the neural dynamics of prioritizing task-relevant information using stimuli composed of small letters on large objects. The experiment employs a two-back target detection paradigm where participants attend to either letter streams or object streams while EEG is recorded. Event codes mark the two primary attention conditions (E 1 for object-prioritized, E 2 for letter-prioritized), with additional markers for target presence (1) and absence (0). The dataset contains 69,120 epochs per primary condition across 40 completed recording files.

## File Scan Result

> **Kernel SHA256**: `0f5e918023267688d096a4308751be2f43eb946e2080075df7a39ad2085a8f65`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 69120 | event | raw |  |
| `E  2` | 69120 | event | raw |  |
| `E  3` | 1920 | event | raw |  |
| `Event/E  1` | 69120 | event | raw |  |
| `Event/E  2` | 69120 | event | raw |  |
| `Event/E  3` | 1920 | event | raw |  |
| `boundary` | 20 | event | raw | Data segment boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: RSVP Stimulus Decoding (Object vs Letter Attention Condition)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `E 1` | 0 | Object task condition (attend to objects in RSVP stream) |
  | `E 2` | 1 | Letter task condition (attend to letters in RSVP stream) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding of 16 object images and 16 letters from epochs time-locked to stimulus onset (tmin=-0.1s, tmax=1.0s), comparing decoding accuracy between object-task (E 1) and letter-task (E 2) conditions. Paper explicitly describes EEG RSVP experiment with two-back task on overlaid objects/letters; data deposited at OSF matching OpenNeuro ds004816.
- **Kernel Notes**: The dataset contains 69,120 events each for `E 1` and `E 2`, representing the two primary attention conditions. Stimulus-level labels (16 objects in 4 categories + 16 letters) can be derived for fine-grained MVPA. Merge `Event/E 1`/`Event/E 2` variants with primary codes before epoching. RSVP runs at ~5 Hz (200ms per item); verify stimulus duration from events.tsv.

### Classical Task 2: RSVP Stimulus Identity Decoding (32-class Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `E 1` | 0–15 | Object task condition with stimulus identity labels (16 object classes in 4 categories) |
  | `E 2` | 16–31 | Letter task condition with stimulus identity labels (16 letter classes) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Full paper confirms MVPA classification of stimulus identity with 32 classes: 16 objects (4 categories: animals, vehicles, tools, furniture) + 16 letters. Analysis epochs non-target stimuli in RSVP streams at stimulus onset. Superordinate animacy categories (animals vs vehicles) also available as intermediate-level labels.
- **Kernel Notes**: Requires extraction of stimulus-specific markers from events.tsv to derive individual stimulus identity labels within each condition. Stimulus-level epochs should exclude target trials (marked by `1`/`0` events) to focus on non-target processing. Verify events.tsv contains stimulus-specific markers beyond condition labels.

### Potential Task 1: RSVP Target Detection (Target-present vs Target-absent)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1`, `0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1` | 0 | Target-present trial (target detected in RSVP stream) |
  | `0` | 1 | Target-absent trial (no target in RSVP stream) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Dataset description indicates two-back task requiring target detection; target-present vs target-absent markers present in event stream.
- **Kernel Notes**: The `1` and `0` markers (31,104 each) indicate target presence status in the RSVP stream. Can be used for P300/oddball ERP analysis to detect neural responses to target stimuli. Extended baseline (tmin=-0.2s) accommodates pre-stimulus baseline correction for P300 analysis. Note: Paper focuses on stimulus decoding from non-target trials; target detection task derives from paradigm description rather than primary analysis approach.

### Potential Task 2: RSVP Multiclass Condition Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `1`, `0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `E 1` | 0 | RSVP condition 1 (object task) |
  | `E 2` | 1 | RSVP condition 2 (letter task) |
  | `1` | 2 | Target-present within RSVP stream |
  | `0` | 3 | Target-absent within RSVP stream |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — RSVP paradigm with two attention conditions (E 1/E 2) and two-back target detection (1/0 markers) enables multiclass classification of both condition and target presence.
- **Kernel Notes**: Merge `Event/E x` variants with primary `E x` codes before epoching to avoid duplicate events. Exclude rare `E 3` and `Event/E 3` codes (1,920–2,000 total) from primary analyses. Extremely high epoch counts (~69,120 per condition) require careful overlap handling if epoching at stimulus-locked rate. This task combines orthogonal dimensions (attention condition × target presence) into a 4-class problem.

### Normal Task 1: RSVP Category-Level Decoding (Animacy/Basic-Level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `E 1` | 0 | Object task condition (category labels: animal/vehicle/tool/furniture) |
  | `E 2` | 1 | Letter task condition (no category structure) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Paper mentions 4 object categories (animals, vehicles, tools, furniture) and superordinate animacy distinctions (animals vs vehicles) as intermediate classification levels.
- **Kernel Notes**: Requires extraction of category-level labels from events.tsv stimulus markers. Animacy effects are robust in EEG and typically emerge earlier than exemplar-specific patterns. Category decoding may be more robust than 32-class stimulus decoding for smaller datasets.

### Normal Task 2: RSVP Condition × Target Interaction Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `1`, `0`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `E 1` + `1` | 0 | Object task, target-present |
  | `E 1` + `0` | 1 | Object task, target-absent |
  | `E 2` + `1` | 2 | Letter task, target-present |
  | `E 2` + `0` | 3 | Letter task, target-absent |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Paradigm enables investigation of how attention condition modulates target processing; interaction effects expected in P300 amplitude or stimulus decoding accuracy.
- **Kernel Notes**: Requires creating interaction labels by combining condition and target presence. Super-level meta analysis can test whether target-related neural signals differ between object-task and letter-task contexts. High trial counts provide power for interaction analysis.