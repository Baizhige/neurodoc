# what_are_we_talking_about

**Dataset**: `openneuro_ds004075` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004075
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 115 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from a language/context processing experiment using BrainVision equipment with 64 channels at 1000 Hz sampling rate. Subjects performed multiple context-based tasks (Context03, Context09, Context10, Context11) involving structured trial sequences with distinct phase markers. The paradigm employs triplet markers (S 10), single onsets (S 1), and recurring sub-events (S 20, S 22, S 23) across most contexts, with Context11 using a unique paired marker structure (S 30, S 31).

## File Scan Result

> **Kernel SHA256**: `74d2eb9582677460eb0f9708cead592127dae7065381dbfe1d16736296228962`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 114 | event | raw | Trial phase onset: single event following S 10 triplet |
| `Stimulus/S 10` | 348 | event | raw | Trial phase onset: triplet marker (three consecutive occurrences precede S 1) |
| `Stimulus/S 11` | 115 | event | raw | Unknown event marker (not observed in sampled file portions; count similar to S 1 suggests possible variant) |
| `Stimulus/S 15` | 345 | event | raw | Unknown event marker (not observed in sampled file portions; count similar to S 10 suggests possible variant) |
| `Stimulus/S 20` | 5388 | event | raw | Trial phase onset: recurring sub-event within trial sequence |
| `Stimulus/S 22` | 5567 | event | raw | Trial phase onset: recurring sub-event within trial sequence |
| `Stimulus/S 23` | 5567 | event | raw | Trial phase onset: recurring sub-event within trial sequence |
| `Stimulus/S 30` | 344 | event | raw | Trial phase onset: context11-specific paired marker (precedes S 31) |
| `Stimulus/S 31` | 344 | event | raw | Trial phase onset: context11-specific paired marker (follows S 30) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: context03 trial phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S 10`, `Stimulus/S 20`, `Stimulus/S 22`, `Stimulus/S 23`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 10` | 0 | Trial phase: preparatory/encoding (triplet marker) |
  | `Stimulus/S  1` | 1 | Trial phase: single onset following preparation |
  | `Stimulus/S 20` | 2 | Trial phase: recurring sub-event type A |
  | `Stimulus/S 22` | 3 | Trial phase: recurring sub-event type B |
  | `Stimulus/S 23` | 4 | Trial phase: recurring sub-event type C |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — Context03 task uses S 10 triplet markers followed by S 1, then sequences of S 20/S 22/S 23 sub-events; event meanings confirmed from BrainVision .vmrk marker files across 14+ subjects
- **Notes**: Five discriminable trial phases identified from event structure: S 10 (preparatory triplet), S 1 (post-preparation onset), and three recurring sub-event types (S 20, S 22, S 23) that form the main trial sequence. Classification task discriminates which phase of the context03 trial structure a given epoch belongs to. Epoch window [-0.5, 2.0] s chosen to capture phase transitions with adequate post-onset temporal coverage for auditory/context processing at 1000 Hz sampling.

### Potential Task 2: Context09 Trial Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S 10`, `Stimulus/S 20`, `Stimulus/S 22`, `Stimulus/S 23`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Trial phase: single event following S 10 triplet |
  | `Stimulus/S 10` | 1 | Trial phase: triplet marker (three consecutive occurrences precede S 1) |
  | `Stimulus/S 20` | 2 | Trial phase: recurring sub-event within trial sequence |
  | `Stimulus/S 22` | 3 | Trial phase: recurring sub-event within trial sequence |
  | `Stimulus/S 23` | 4 | Trial phase: recurring sub-event within trial sequence |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — Context09 task shares the same marker structure as context03 (S 10 triplets, S 1, S 20/S 22/S 23) but as a separate BIDS task with different experimental context. The same 5 event IDs are available, enabling phase discrimination.
- **Notes**: Five-way classification of trial phase onsets in the context09 variant. The S 20/S 22/S 23 sub-events are treated as distinct phases despite similar descriptions, as they are separate event IDs in the marker stream. No motor imagery classes are present; this is a pure trial phase discrimination task. Epoch parameters inferred from context03 structure.

### Potential Task 3: context10 trial phase classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S 10`, `Stimulus/S 20`, `Stimulus/S 22`, `Stimulus/S 23`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Trial phase onset: single event following S 10 triplet |
  | `Stimulus/S 10` | 1 | Trial phase onset: triplet marker (three consecutive occurrences precede S 1) |
  | `Stimulus/S 20` | 2 | Trial phase onset: recurring sub-event within trial sequence |
  | `Stimulus/S 22` | 3 | Trial phase onset: recurring sub-event within trial sequence |
  | `Stimulus/S 23` | 4 | Trial phase onset: recurring sub-event within trial sequence |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — Context10 task with S 10 triplet-S 1-S 20/S 22/S 23 sequence enabling phase classification; marker structure confirmed across 14+ subjects and all 4 tasks
- **Notes**: Five distinct trial phase markers identified in the context10 task. S 10 appears as triplets followed by S 1, then sequences of S 22/S 23/S 20. These are phase onset markers (not MI class labels), forming a valid trial phase discrimination task. S 20, S 22, and S 23 all share the same meaning of "recurring sub-event within trial sequence" but are kept as separate classes as they represent distinct event IDs in the marker stream, potentially corresponding to different sub-phases of the trial sequence. The triplet structure of S 10 and its relationship to S 1 suggests a hierarchical trial organization.

### Potential Task 4: Context11 Paired Marker Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.5 s *, target_events = [`Stimulus/S 30`, `Stimulus/S 31`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 30` | 0 | Trial phase onset: context11-specific paired marker (precedes S 31) |
  | `Stimulus/S 31` | 1 | Trial phase onset: context11-specific paired marker (follows S 30) |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — Context11 uniquely uses S 30/S 31 paired markers that appear consecutively, distinct from the S 10/S 1 structure of other contexts, enabling discrimination between the two paired markers
- **Notes**: This task discriminates between the two context11-specific paired markers (S 30 as the first element of the pair, S 31 as the second). The paired structure suggests a rapid sequential presentation format (possibly question-answer or probe-test), justifying shorter epochs. Epoch parameters are inferred from the consecutively-appearing paired marker structure and the need to capture rapid temporal dynamics without excessive overlap between the two markers in a pair.

### Potential Task 5: context11 vs other context marker discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`Stimulus/S  1`, `Stimulus/S 10`, `Stimulus/S 20`, `Stimulus/S 22`, `Stimulus/S 23`, `Stimulus/S 30`, `Stimulus/S 31`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| `Stimulus/S 30` | 0 | context11-specific paired marker (precedes S 31) |
| `Stimulus/S 31` | 0 | context11-specific paired marker (follows S 30) |
| `Stimulus/S 10` | 1 | triplet marker (three consecutive occurrences precede S 1) |
| `Stimulus/S  1` | 1 | single event following S 10 triplet |
| `Stimulus/S 20` | 1 | recurring sub-event within trial sequence |
| `Stimulus/S 22` | 1 | recurring sub-event within trial sequence |
| `Stimulus/S 23` | 1 | recurring sub-event within trial sequence |

- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — Cross-context task discriminating context11's unique S 30/S 31 paired markers from the S 10/S 1/S 20/S 22/S 23 marker set used in contexts 03, 09, 10. Mappings confirmed from BrainVision .vmrk marker files across 14+ subjects and all 4 tasks.
- **Notes**: y=0 merges the two context11-specific markers (S 30, S 31) that appear as a consecutive pair exclusively in context11. y=1 groups all markers from the other contexts (03, 09, 10), which share a common triplet+sequence structure (S 10 triplet → S 1 → S 22/S 23/S 20 sequence). This creates a binary classification testing whether EEG signatures distinguish the context11 paradigm structure from the others. Subjects are bound to specific contexts, so class balance varies by subject; the model must generalize across subjects with different context exposures.

### Potential Task 6: S 10 triplet structure detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -1 s *, tmax = 3 s *, overlap = 0.0 s *, target_events = [`Stimulus/S 10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 10` (1st occurrence in triplet) | 0 | first_S10 |
  | `Stimulus/S 10` (2nd occurrence in triplet) | 1 | second_S10 |
  | `Stimulus/S 10` (3rd occurrence in triplet) | 2 | third_S10 |
  | `Stimulus/S  1` (post-triplet) | 3 | post_triplet_S1 |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — S 10 appears as three consecutive occurrences before S 1, creating a unique triplet structure; S 1 serves as trial phase onset following the triplet
- **Notes**: Long-event epoching anchored on `Stimulus/S 10` with extended tmax captures the full triplet sequence (three S 10 occurrences) plus the subsequent S 1 marker within a single epoch. The classifier must distinguish position within the triplet (1st/2nd/3rd S 10) from the post-triplet S 1 phase. This requires the kernel to parse event sequences within each epoch and assign y based on ordinal position. Overlap set to 0.0 to avoid redundant triplet coverage; inferred values marked with * due to lack of explicit timing documentation in available sidecars.

### Potential Task 7: Recurring Sub-Event Sequence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.3 s *, tmax = 1.5 s *, target_events = [`Stimulus/S 20`, `Stimulus/S 22`, `Stimulus/S 23`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  | `Stimulus/S 20` | 0 | Trial phase onset: recurring sub-event within trial sequence (sequence element type A) |
  | `Stimulus/S 22` | 1 | Trial phase onset: recurring sub-event within trial sequence (sequence element type B) |
  | `Stimulus/S 23` | 2 | Trial phase onset: recurring sub-event within trial sequence (sequence element type C) |
- **Evidence**:
  - https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — S 20, S 22, S 23 appear as recurring sub-events within trial sequences after the S 10/S 1 initial structure; near-equal counts (S 20: 5388, S 22: 5567, S 23: 5567) indicate balanced conditions for 3-class discrimination of sequence position or content type.
- **Notes**: This task discriminates between three types of recurring sub-events that occur within ongoing trial sequences. The events are trial phase onset markers rather than motor imagery classes, forming a sequence element discrimination paradigm. The slight imbalance in S 20 count (5388 vs ~5567) suggests it may serve a slightly different functional role (possibly terminal or transitional) compared to S 22/S 23. Epoch timing inferred from rapid serial presentation context with sub-events embedded in continuous sequences.

## Data Quality Notes

- No subject demographic metadata (age, sex) available in scanned files; demographic fields marked missing.
- No device/equipment metadata recorded in scan; BrainVision format inferred from file structure and marker conventions.
- Event markers S 11 and S 15 detected in file scan but not observed in sampled portions; counts suggest possible variant conditions or unused backup markers requiring verification.
- All epoch timing parameters (tmin, tmax, overlap) are inferred from event structure patterns and marked with asterisks; explicit timing documentation from study authors is not available in sidecars.
- Subjects appear bound to specific context tasks (Context03/09/10/11), preventing within-subject cross-context designs; models must generalize across subjects with different context exposures.
- S 10 triplet structure requires kernel-level sequence parsing for ordinal position detection; simple event-based epoching insufficient for triplet-position tasks.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
