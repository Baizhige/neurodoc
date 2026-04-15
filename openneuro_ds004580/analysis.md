# Simon-conflict Task

**Dataset**: `openneuro_ds004580` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004580
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants performed the Simon conflict task in which stimulus location (left/right) could be congruent or incongruent with the required response direction. S 1 and S 2 encode congruent and incongruent trial types respectively; S 3 marks rare/catch trials. The study investigates conflict monitoring and executive control neural signatures (N2, P3 ERP components).

## File Scan Result

> **Kernel SHA256**: `0c5e640c70eceb34113cef4014f0b613acace1cf0752e233facc12fafc52723d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 55922 | event | raw | Congruent trial (stimulus location matches response side) |
| `S  2` | 54800 | event | raw | Incongruent trial (stimulus location conflicts with response side) |
| `S  3` | 1 | event | raw | Rare/catch trial |
| `S255` | 6 | event | raw | BrainVision overflow/system marker |
| `boundary` | 156 | event | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Congruent vs Incongruent Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = ["S  1", "S  2"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-------|--------|
| `S  1` | 0 | Congruent trial (stimulus location matches response side) |
| `S  2` | 1 | Incongruent trial (stimulus location conflicts with response side) |

- **Evidence**: Paradigm documentation (Simon conflict task investigating N2/P3 ERP components); epoch alignment recommendations confirm S 1, S 2 stimulus markers with duration <2s are optimal for epoch_by_event_hdf5. DOI: https://doi.org/10.1101/2022.07.26.22278079
- **Kernel Notes**: Subject-level processing should verify event counts (~1864 S 1/subject, ~1827 S 2/subject). Balanced design supports binary classification without resampling. Use Annotation channel for labels: S  1 → 0 (congruent), S 2 → 1 (incongruent). Exclude S255 (BrainVision overflow/admin, 6 total), boundary (156 total), and S 3 (only 1 occurrence, too sparse).

### Potential Task 1: ERP Component Analysis (N2/P3 Conflict Effects)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.8 s, overlap = null, target_events = ["S  1", "S  2"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-------|--------|
| `S  1` | 0 | Congruent trial |
| `S  2` | 1 | Incongruent trial |

- **Evidence**: Paradigm description explicitly states "study investigates conflict monitoring and executive control neural signatures (N2, P3 ERP components)". Extended window (-0.3s to 0.8s) recommended for classic N2 (~200-350ms) and P3 (~300-600ms) component extraction.
- **Kernel Notes**: Baseline correction at -300 to -100ms recommended for ERP analysis. N2 amplitude differences between S 1 vs S 2 expected at fronto-central sites; P3 differences expected at parietal sites. Channel-level averaging should preserve 64-channel montage for topographic analysis.

### Normal Task 1: Rare/Catch Trial Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = ["S  3"]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|-------|--------|
| `S  3` | 2 | Rare/catch trial |

- **Evidence**: Paradigm documents S 3 as "rare/catch trials", suggesting deviant detection paradigm embedded within Simon task. Epoch alignment recommendations note S 3 is too sparse for meaningful comparison (only 1 total across all subjects).
- **Kernel Notes**: Cannot perform meaningful binary or multi-class classification due to extreme class imbalance (S  3: 1 occurrence vs S  1: 55922, S  2: 54800). Task documented for completeness; not recommended for primary analysis.