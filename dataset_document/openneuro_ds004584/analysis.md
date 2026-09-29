# Rest Eyes Open (Parkinson's Disease)

**Dataset**: `openneuro_ds004584` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004584
**Category**: Biological State | **Subjects**: 149 | **Files (Completed)**: 149 | **Channels**: 63 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Resting-state EEG was collected from 149 participants (100 with Parkinson's disease and 49 healthy controls) who sat quietly with eyes open for approximately two minutes. The study characterizes spontaneous neural oscillatory patterns to differentiate PD patients from controls. No active task was required; participants fixated on a cross and remained still.

## File Scan Result

> **Kernel SHA256**: `b1b282208a1b00ee5dccf3fe3431a98b08f50659c99222ad514151d4f03b6485`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 149 | admin | raw | Recording boundary marker at file start |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Standard BIDS fields `age` and `sex` are missing; age and gender information is instead available as `AGE` and `GENDER` in the info fields with complete coverage.
- Device information is missing from standard BIDS fields; no equipment metadata is available in the scan.
- UPDRS scores have partial availability (100/149 subjects) due to structural missingness in healthy controls who do not have Parkinson's disease symptoms.
- Event structure contains only `boundary` markers (admin type) with no task-related events, consistent with resting-state paradigm.
- TYPE field encoding (0 vs. 1) for PD subtypes requires verification against original publication to confirm mapping to tremor-dominant vs. PIGD subtypes.
- All epoch segmentation parameters (4 s window, 0.5 overlap) are inferred from standard resting-state conventions rather than explicitly documented in dataset materials.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
