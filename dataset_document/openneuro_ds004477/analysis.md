# PES - Pandemic Emergency Scenario

**Dataset**: `openneuro_ds004477` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004477
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 9 | **Channels**: 80 | **Sampling Rate**: 2048 Hz | **Manual Review**: Pending

## Paradigm

A strategic pandemic simulation task where participants allocate limited resources to cities on a map and report their decision confidence while interacting with an artificial agent. EEG was recorded to investigate neural correlates of complex decision-making, confidence estimation, and strategy formation in a realistic multi-agent scenario.

## File Scan Result

> **Kernel SHA256**: `72ef8ac0cb432e38a1247d06be053f39ec086fa91184631339cbdbd81729fee9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Decision Making (Multiclass Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| `stimulus` | 0 | Decision stimulus onset |
| `resp_hold` | 1 | Response initiation (button press start) |
| `resp_release` | 2 | Response release (button press end) |
| `confidence` | 3 | Confidence rating onset |
- **Evidence**: OpenNeuro dataset ds004477 metadata; paradigm description (strategic pandemic simulation with resource allocation decisions, multi-agent interaction, confidence reporting). Source: https://openneuro.org/datasets/ds004477
- **Kernel Notes**: High temporal resolution (2048 Hz) preserves fine-grained decision dynamics. Only 9 subjects — recommend within-subject analysis only. Behavioral data (resource allocation choices) essential for augmenting label richness. Consider confounds from multi-agent interaction timing. **CRITICAL**: File scan reports "no events detected" despite analysis.md describing clear event structure — kernel must verify raw file access and HDF5 trigger extraction before proceeding.

---

### Potential Task 1: Confidence Rating Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s (relative to confidence event onset)
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:

| MISC Channel Name | Y Mapping Notes |
|---|---|
| Needs verification | Confidence rating onset; continuous confidence values from behavioral data expected as regression target (see paradigm description). MISC channels not detected in file scan — requires verification from raw files or behavioral logs. |
- **Evidence**: Paradigm description explicitly includes "report their decision confidence" as core task component. Confidence values stored in misc labels.
- **Kernel Notes**: Shorter window (0.8 s) sufficient for confidence processing neural correlates. Confidence may be used as regression target (continuous) rather than discrete classification. Kernel must preserve derivation source, unit, and version metadata for confidence values.

---

### Potential Task 2: PES BIDS Task (Publisher-Defined)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification | segment_length = Needs Verification
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for BIDS task PES (dataset-specific mapping — requires verification from dataset readme or phenotype files)
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| Needs verification | Needs verification | Event/condition labels for BIDS task PES (dataset-specific mapping — requires verification from dataset readme or phenotype files). File scan reports no events detected; event IDs must be verified from raw file access or BIDS metadata. |

- **Evidence**: OpenNeuro metadata.tasksCompleted confirms PES as completed BIDS task. DOI cited in analysis.md (10.3389/fnhum.2019.00013) not confirmed in reference extraction as supporting this specific dataset.
- **Kernel Notes**: Verify event markers and metadata for correct tmin/tmax parameters. Publisher-defined BIDS task for PES requires long event epoching for sustained strategy periods. If events confirmed missing (per "no events detected" file scan complication), fall back to segmentation-based epoching.

---

### Potential Task 3: Strategy Formation (Sustained State)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = 0.0–0.5 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Labels derived from sustained decision phases (resource allocation strategy periods) — requires verification from behavioral logs or paradigm documentation.
- **Target Definition**:

| Event ID | y | Meaning |
|---|---|---|
| Needs verification | Needs verification | Labels derived from sustained decision phases (resource allocation strategy periods) — requires verification from behavioral logs or paradigm documentation. File scan reports no events detected; boundary markers must be verified from raw file access or behavioral state transitions. |

- **Evidence**: Paradigm description mentions "strategy formation in a realistic multi-agent scenario."
- **Kernel Notes**: Strategy periods likely span multiple trials; long event epoching appropriate. Kernel should verify boundary markers or derive from behavioral state transitions.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
