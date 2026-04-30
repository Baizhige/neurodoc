# Illusion of Agency over Electrically-Actuated Movements

**Dataset**: `openneuro_ds004561` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004561
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**: Pending

## Paradigm

Participants experienced electrical muscle stimulation that actuated their hand movements in three conditions: stimulation (involuntary movement), pretest (voluntary movement before stimulation), and posttest (voluntary movement after stimulation). EEG was recorded to investigate illusory sense of agency over externally-driven movements. The study explores how prior voluntary movement influences agency attribution over stimulation-induced movements.

## File Scan Result

> **Kernel SHA256**: `60a5e98f949d2b8ff5248518d585d8eb27ef0b462d3274617dd5587a5695b562`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Agency Classification (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**: Binary classification of agency attribution during EMS-induced vs. voluntary movements.

| Event | y | Meaning |
|-------|---|------|
| `stimulation` | 0 | Non-agency (externally-driven movement) |
| `pretest` | 1 | Agency (voluntary pre-stimulation movement) |
| `posttest` | 1 | Agency (voluntary post-stimulation movement) |

- **Evidence**: DOI: https://doi.org/10.1523/JNEUROSCI.1116-23.2023
- **Kernel Notes**: Class 1 pools both voluntary movement conditions (pretest + posttest) as self-generated agency contrasts against externally-actuated stimulation. Verify that stimulation artifact does not bias classifier toward stimulation condition. Consider separate condition-wise analysis to check for pretest/posttest differences before pooling.

### Normal Task 1: Condition Classification (3-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset)
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: Multiclass classification distinguishing all three experimental conditions.

| Event | y | Meaning |
|-------|----|---------|
| `stimulation` | 0 | Electrical stimulation (involuntary movement) |
| `pretest` | 1 | Pre-stimulation voluntary movement |
| `posttest` | 2 | Post-stimulation voluntary movement |

- **Evidence**: Dataset readme and paradigm description. Primary paper (DOI: https://doi.org/10.1523/JNEUROSCI.1116-23.2023) supports condition-specific neural dynamics, though classification=relevant ref focuses on 2-class agency contrast.
- **Kernel Notes**: 3-class task captures condition-specific neural signatures. Use caution when interpreting stimulation condition due to EMS artifact. Pre-test and post-test voluntary movements serve as within-subject controls but may exhibit adaptation effects.

### Potential Task 1: Agency RT / Attribution Time-Course Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s (relative to event onset)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**: Sliding-window binary classification of agency vs. non-agency across the full movement epoch.

| Event | y | Meaning |
|-------|----|---------|
| `stimulation` | 0 | Non-agency (externally-driven) |
| `pretest` | 1 | Agency (voluntary) |
| `posttest` | 1 | Agency (voluntary) |

- **Evidence**: No explicit classification=relevant reference; inferred from epoch alignment recommendations supporting extended post-event window for reaction-time and agency attribution analysis.
- **Kernel Notes**: Extended window captures movement execution, sensory feedback integration, and agency-related processing. Pre-stimulus baseline window assesses motor preparation differences between voluntary and stimulation-induced movements. Require careful artifact handling for stimulation condition.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
