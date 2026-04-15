# Resting-State EEG Before and After Different Study Methods

**Dataset**: `openneuro_ds006801` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006801
**Category**: Biological State | **Subjects**: 21 | **Files (Completed)**: 42 | **Channels**: 31 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG was recorded before and after an educational intervention in which participants engaged in active retrieval practice, passive review, or a control condition. The design examines how different study strategies affect resting-state neural oscillations. Each participant completed eyes-open and eyes-closed resting blocks. The 42 files correspond to pre- and post-intervention recordings for 21 subjects.

## File Scan Result

> **Kernel SHA256**: `6951d06471e5bde013f2b4b80f0ce484335d39c96370bfa2fb275e5f6099b072`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Pre/Post Intervention Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| participants.tsv | pre | Pre-intervention resting-state |
| participants.tsv | post | Post-intervention resting-state |

- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: This is a resting-state dataset with no raw events. Classification labels (pre/post intervention) must be derived entirely from participants.tsv metadata. The 42 files = 21 subjects × 2 sessions (pre/post). Segment length of 4.0s with 50% overlap creates overlapping windows suitable for capturing sustained oscillatory patterns in resting-state data.

### Potential Task 2: Study Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| participants.tsv | active_retrieval | Active retrieval practice condition |
| participants.tsv | passive_review | Passive review condition |
| participants.tsv | control | Control condition |

- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: The paradigm examines how different study strategies (active retrieval practice, passive review, control) affect resting-state neural oscillations. Verify that participants.tsv contains study condition labels before kernel execution. Segment-level classification predicts which study method participants experienced based on resting-state EEG patterns. This is a 3-class classification problem requiring careful participant-level metadata mapping.

### Potential Task 3: Eyes-Open/Eyes-Closed Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| session metadata | eyes_open | Eyes-open resting-state |
| session metadata | eyes_closed | Eyes-closed resting-state |

- **Evidence**: DOI — (no references provided; task is plausible from paradigm alone)
- **Kernel Notes**: Each participant completed both eyes-open and eyes-closed resting blocks. However, EEG events cannot distinguish these states—labels must be inferred from session metadata or file naming conventions. If eyes-open/eyes-closed cannot be determined from metadata, this dimension should be excluded from classification or duration-based heuristics should be implemented. Standard alpha rhythm differences typically distinguish these states.
