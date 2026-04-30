# The BMI-HDEEG dataset 1

**Dataset**: `openneuro_ds004444` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004444
**Category**: Action/Output | **Subjects**: 465 | **Files (Completed)**: 465 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Brain-computer interfacing task based on sensorimotor rhythms (SMR) using high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the first of four BMI-HDEEG datasets, enabling classification of motor imagery across all four classes.

## File Scan Result

> **Kernel SHA256**: `7099a55557381396528266b6d303f832d46976f4878c0906ade12f39be7104ff`
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



## Data Quality Notes

- No event markers detected in file scan despite motor imagery paradigm requiring cue-based events.
- Task definitions rely on segmentation-based approaches rather than event-locked epochs, which conflicts with the described SMR-BCI motor imagery paradigm.
- Subject count discrepancy: metadata claims 465 subjects but task evidence references only 30 participants in participants.tsv.
- `device` field is completely missing from info scan, limiting equipment provenance tracking.
- Event structure table is empty; no event counts or IDs available to validate motor imagery class distributions.
- Severe class imbalance noted in demographic tasks (gender: 1:5 ratio; handedness: 1:29 ratio).

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
