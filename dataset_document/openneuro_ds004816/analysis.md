# EEG Attention RSVP Experiment 1

**Dataset**: `openneuro_ds004816` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004816
**Category**: Sensory/Response | **Subjects**: 15 | **Files (Completed)**: 40 | **Channels**: 63 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task investigating the neural dynamics of prioritizing task-relevant information using stimuli composed of small letters on large objects. The experiment employs a two-back target detection paradigm where participants attend to either letter streams or object streams while EEG is recorded. Event codes mark the two primary attention conditions (E 1 for object-prioritized, E 2 for letter-prioritized), with additional markers for target events (E 3). The dataset contains 69,120 epochs per primary condition across 40 completed recording files.

## File Scan Result

> **Kernel SHA256**: `0c04a21d906e0f4ac2f738ed629c51242c6563df372d0192bb7d39eafb86ec0b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 69120 | event | raw | Stimulus presentation marker: object/letter pair onset (stream 1 or primary presentation) |
| `E  2` | 69120 | event | raw | Stimulus presentation marker: object/letter pair onset (stream 2 or secondary presentation) |
| `E  3` | 1920 | event | raw | Target or response event marker (2-back target detection or button press) |
| `Event/E  1` | 69120 | event | raw | Stimulus presentation marker: object/letter pair onset (stream 1 or primary presentation) |
| `Event/E  2` | 69120 | event | raw | Stimulus presentation marker: object/letter pair onset (stream 2 or secondary presentation) |
| `Event/E  3` | 1920 | event | raw | Target or response event marker (2-back target detection or button press) |
| `boundary` | 20 | admin | raw | Data segment boundary marker (file or recording discontinuity) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: RSVP Attention Condition Decoding (Object vs Letter Task)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E  1`, `E  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  1` | 0 | Object-task condition (report objects, stream 1/primary presentation) |
  | `E  2` | 1 | Letter-task condition (report letters, stream 2/secondary presentation) |
- **Evidence**:
  - 10.51628/001c.21174 — Paper explicitly describes EEG RSVP experiment with two-back task on overlaid objects/letters; 2.5Hz RSVP (200ms on, 200ms off), 96 sequences total alternating object/letter task; tmin=-0.1s, tmax=1.0s for stimulus-locked epochs used for MVPA decoding of attention conditions.
- **Notes**: Both E 1 and E 2 mark stimulus presentation onsets for the two alternating attention conditions (object task vs letter task). The RSVP paradigm presents overlaid small letters on large objects; participants perform a 2-back task on either objects (condition=0) or letters (condition=1) in alternating sequences. E 1 and E 2 serve as the event anchors for epoching, with their event identity directly encoding the attention condition being decoded. The 69,120 epochs per condition provide substantial data for cross-validated classification of neural signatures of attentional prioritization.

### Potential Task 1: RSVP target detection (2-back target vs non-target)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`E  3`, `E  1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  3` | 0 | Target or response event marker (2-back target detection or button press) |
  | `E  1` | 1 | Non-target stimulus presentation marker (object/letter pair onset, stream 1) |
- **Evidence**:
  - events.tsv sample and events.json — `is2back` column confirms 2-back target detection component with 1 when subject was supposed to respond; event counts show E 3 (1920) as rare target events vs E 1/E 2 (69120 each) as frequent stimulus presentations
  - task-rsvp_events.json — `is2back` Description: "1 when subject was supposed to respond (2-back in the right condition)"; `objecttarget` and `lettertarget` columns separately mark 2-back occurrences per stream
  - EEG file headers — `E  3` and `E  1` appear as annotations in continuous recordings, confirming event marker availability for epoching
- **Notes**: Target vs non-target classification using rare-target oddball-like structure. E 3 marks target/response events (~2.7% of presentations) while E 1 marks standard stimulus onsets. The rapid RSVP presentation (200ms on/200ms off at 2.5Hz) creates a challenging target detection paradigm. E 2 (stream 2) excluded to avoid mixing streams; using E 1 as representative non-target baseline. Epoch window shortened to 900ms total to accommodate rapid stimulus succession while capturing early ERP components (P300) associated with target detection.

### Potential Task 2: RSVP stream identity decoding (stream 1 vs stream 2)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`E  1`, `E  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  1` | 0 | Stream 1 / primary presentation |
  | `E  2` | 1 | Stream 2 / secondary presentation |
- **Evidence**:
- **Notes**: This task decodes which physical stimulus stream was presented (stream 1 vs stream 2) based on the event markers E 1 and E 2. The two event types have identical counts (69120 each), indicating balanced presentation of both streams across the RSVP task. The epoch window matches the attention condition decoding task for fair comparison of neural signatures.

## Data Quality Notes

- `device` field is missing from metadata, limiting hardware provenance tracking.
- Duplicate event code variants exist (`E  1`/`Event/E  1`, `E  2`/`Event/E  2`, `E  3`/`Event/E  3`); these must be merged before epoching to avoid missing events.
- `boundary` markers (n=20) indicate data segment discontinuities that may affect continuous analyses.
- Subject count updated from N/A to 15 based on participants.tsv completeness in scan results.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
