# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 280 | **Files (Completed)**: 280
**Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a sensorimotor rhythm-based brain-computer interface task using high-density scalp EEG. This is the fourth BMI-HDEEG dataset with a two-class (binary) motor imagery design (left hand vs. right hand). The experimental paradigm involved motor imagery training with neurofeedback components, where subjects alternated between performing motor imagery and relaxation/rest periods.

## File Scan Result

> **Kernel SHA256**: `3fb4dbab1662d43515456d50d8df976ef4cec740fcd3d1ab962f1850c946c06c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 277 | event | raw | Motor imagery onset (unresolved class label) |
| `event_2` | 1723 | event | raw | Relaxation/rest period onset |
| `event_3` | 1875 | event | raw | Inter-trial interval or baseline period |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

(No tasks could be synthesized.)
