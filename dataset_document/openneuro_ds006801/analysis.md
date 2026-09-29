# Resting-State EEG Before and After Different Study Methods

**Dataset**: `openneuro_ds006801` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006801
**Category**: Biological State | **Subjects**: 21 | **Files (Completed)**: 42 | **Channels**: 31 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Resting-state EEG was recorded before and after an educational intervention in which participants engaged in active retrieval practice, passive review, or a control condition. The design examines how different study strategies affect resting-state neural oscillations. Each participant completed eyes-open and eyes-closed resting blocks. The 42 files correspond to pre- and post-intervention recordings for 21 subjects.

## File Scan Result

> **Kernel SHA256**: `1eb4d257b983d8fe10463b986b23ff4e8ade8bcc0682b11b349e53131f5ae6f6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Pre/Post Intervention Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| Needs verification | pre | Pre-intervention resting-state (derived from participants.tsv) |
| Needs verification | post | Post-intervention resting-state (derived from participants.tsv) |
- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: This is a resting-state dataset with no raw events. Classification labels (pre/post intervention) must be derived entirely from participants.tsv metadata. The 42 files = 21 subjects × 2 sessions (pre/post). Segment length of 4.0s with 50% overlap creates overlapping windows suitable for capturing sustained oscillatory patterns in resting-state data.

---

### Potential Task 2: Study Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| Needs verification | active_retrieval | Active retrieval practice condition (derived from participants.tsv) |
| Needs verification | passive_review | Passive review condition (derived from participants.tsv) |
| Needs verification | control | Control condition (derived from participants.tsv) |
- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: The paradigm examines how different study strategies (active retrieval practice, passive review, control) affect resting-state neural oscillations. Verify that participants.tsv contains study condition labels before kernel execution. Segment-level classification predicts which study method participants experienced based on resting-state EEG patterns. This is a 3-class classification problem requiring careful participant-level metadata mapping.

---

### Potential Task 3: Eyes-Open/Eyes-Closed Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| Needs verification | eyes_open | Eyes-open resting-state (derived from session metadata) |
| Needs verification | eyes_closed | Eyes-closed resting-state (derived from session metadata) |
- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: Each participant completed both eyes-open and eyes-closed resting blocks. However, EEG events cannot distinguish these states—labels must be inferred from session metadata or file naming conventions. If eyes-open/eyes-closed cannot be determined from metadata, this dimension should be excluded from classification or duration-based heuristics should be implemented. Standard alpha rhythm differences typically distinguish these states.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
