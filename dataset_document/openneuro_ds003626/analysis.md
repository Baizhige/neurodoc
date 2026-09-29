# Inner Speech BCI Dataset

**Dataset**: `openneuro_ds003626` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003626
**Category**: High-level Mental | **Subjects**: 10 | **Files (Completed)**: 30 | **Manual Review**:
**Channels**: 137 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed inner speech (imagined speech), pronounced speech, and visualization tasks involving four directional commands (Up, Down, Right, Left) and eight word stimuli (social words: child, daughter, father, wife; numerical words: four, three, ten, six) to explore the neural correlates of the 'inner voice' phenomenon for potential BCI applications. High-density EEG (137 channels) was recorded during all three modalities of speech production/imagery. No discrete event markers were captured in the EEG trigger channel; paradigm timing is encoded externally in events.tsv and behavioral log files.

## File Scan Result

> **Kernel SHA256**: `3a2955c96318a834ed012f5239431d57bff0a54cd66aa9463befcf43a547e484`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_11` | 30 | event | raw | Unknown experimental marker (30 occurrences) |
| `event_12` | 30 | event | raw | Unknown experimental marker (30 occurrences) |
| `event_13` | 30 | event | raw | Unknown experimental marker (30 occurrences) |
| `event_14` | 30 | event | raw | Unknown experimental marker (30 occurrences) |
| `event_15` | 150 | event | raw | Unknown experimental marker (150 occurrences) |
| `event_16` | 150 | event | raw | Unknown experimental marker (150 occurrences) |
| `event_17` | 379 | event | raw | Unknown experimental marker (379 occurrences) |
| `event_21` | 30 | event | raw | Unknown experimental marker (30 occurrences) |
| `event_22` | 61 | event | raw | Unknown experimental marker (61 occurrences) |
| `event_23` | 59 | event | raw | Unknown experimental marker (59 occurrences) |
| `event_31` | 1409 | event | raw | Unknown high-frequency marker (1409 occurrences) |
| `event_32` | 1410 | event | raw | Unknown high-frequency marker (1410 occurrences) |
| `event_33` | 1409 | event | raw | Unknown high-frequency marker (1409 occurrences) |
| `event_34` | 1407 | event | raw | Unknown high-frequency marker (1407 occurrences) |
| `event_42` | 5634 | event | raw | Unknown very high-frequency marker (5634 occurrences) |
| `event_44` | 5632 | event | raw | Unknown very high-frequency marker (5632 occurrences) |
| `event_45` | 5636 | event | raw | Unknown very high-frequency marker (5636 occurrences) |
| `event_46` | 5631 | event | raw | Unknown very high-frequency marker (5631 occurrences) |
| `event_51` | 120 | event | raw | Unknown experimental marker (120 occurrences) |
| `event_61` | 81 | event | raw | Unknown experimental marker (81 occurrences) |
| `event_62` | 93 | event | raw | Unknown experimental marker (93 occurrences) |
| `event_63` | 88 | event | raw | Unknown experimental marker (88 occurrences) |
| `event_64` | 116 | event | raw | Unknown experimental marker (116 occurrences) |
| `event_65536` | 1 | admin | raw | System boundary marker (single occurrence) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: 4-class directional command visualization
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`event_61`, `event_62`, `event_63`, `event_64`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_61 | 0 | Up (visualized) |
  | event_62 | 1 | Down (visualized) |
  | event_63 | 2 | Left (visualized) |
  | event_64 | 3 | Right (visualized) |
- **Evidence**:
- **Notes**: The dataset README describes "Classes = 'Ar...'" (truncated) and conditions including "Visualized Condition" with four directional commands (Up, Down, Right, Left). Event IDs 61-64 occur in a tight group with counts (81, 93, 88, 116) matching the expected ~4× structure for 4-class visualization trials across 10 subjects. No explicit event documentation exists in accessible BIDS files (events stored in binary .dat derivatives), so event-to-class mapping is inferred from count pattern consistency with described paradigm structure. The inferred timing window (-0.5 to 1.0 s) allows capture of visual imagery ERP and sustained activity typical for BCI command visualization paradigms at 1024 Hz sampling.

### Potential Task 2: 3-class speech modality classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`event_21`, `event_22`, `event_23`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_21` | 0 | Inner Speech |
  | `event_22` | 1 | Pronounced Speech |
  | `event_23` | 2 | Visualized Condition |
- **Evidence**:
- **Notes**: Event IDs 21, 22, 23 are hypothesized to mark block onsets for the three speech modalities based on their occurrence counts (30, 61, 59) matching the dataset's documented three conditions (Inner Speech, Pronounced Speech, Visualized Condition). The counts are consistent with a repeated-measures design across 10 subjects with ~3 blocks per subject for modality 1 and ~6 blocks per subject for modalities 2-3. No events.tsv or events.json files are available to confirm these mappings; all event meanings are marked 'unclear' in the locked ground truth. This task remains a potential task pending verification of event semantics.

### Potential Task 3: Rest vs Task State Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 1 s *, target_events = [`event_51`, `event_15`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_51` | 0 | Rest period / fixation cross (rest state) |
  | `event_15` | 1 | Active task period (inner speech task state) |
- **Evidence**:
  - ds003626 dataset_description.json — "Inner Speech" dataset with task 'innerspeech', conditions include Inner Speech, Pronounced Speech, Visualized Condition
  - Event count statistics — event_51 occurs 120 times; event_15 occurs 150 times, providing balanced classes for rest vs task discrimination
- **Notes**: This task uses prefix-grouped event patterns as a rest/task state discrimination problem. Event_51 is grouped in the 50s range (120 occurrences) and is interpreted as a rest/fixation marker based on its intermediate frequency consistent with block-level rest periods, while event_15 in the 10s range (150 occurrences) represents an active task condition. The 1-second epoch duration captures stable state-related EEG signatures while avoiding anticipatory responses. Both event IDs are explicitly listed in kernel_needs.must_have_events.

## Data Quality Notes

- All event meanings are marked as "Unknown" in the authoritative File Scan Result, indicating a critical lack of ground-truth event documentation.
- Event-to-condition mappings in the Tasks section are inferred from count patterns and dataset README descriptions, not from explicit BIDS event files or validated documentation.
- No events.tsv or events.json files are accessible; events appear to be stored in binary .dat derivatives, preventing direct verification of event semantics.
- Subject metadata (age, sex) and device information are completely missing from the dataset.
- High-frequency markers (event_31–event_46, thousands of occurrences) may represent continuous recording segments or data block boundaries rather than experimental events; their functional role is unclear.
- The single event_65536 admin marker suggests a system boundary or recording initialization event with no experimental relevance.
- The discrepancy between the draft analysis.md's detailed event meanings and the authoritative File Scan Result's "Unknown" labels highlights that prior event interpretations were speculative and require manual verification.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
