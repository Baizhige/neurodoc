# ODE (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004850` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004850
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz
**Manual Review**: Pending

## Paradigm

An EEG dataset (ODE) recorded during a social-cognitive paradigm with hierarchically encoded stimulus conditions. Shares the identical event structure with the STRONG (ds004849) and InsurgentCivilian (ds004852) datasets, suggesting these are companion recordings from the same experimental series. The single aggregated file requires events.tsv decoding for full interpretation.

## File Scan Result

> **Kernel SHA256**: `c9fdfceea4deaccff7f35dadecdbc63acfa1d15a0a71acf757a7cea2d3f71a75`
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

### Normal Task 1: Social-Cognitive 12-Class Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [2200, 72011, 52011, 75011, 55011, 73011, 74011, 53011, 54011, 71011, 2201, 51011]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `2200` | 0 | Primary condition code (dominant) |
| `72011` | 1 | Category 7, sub-condition 10, variant 1 |
| `52011` | 2 | Category 5, sub-condition 10, variant 1 |
| `75011` | 3 | Category 7, sub-condition 50, variant 1 |
| `55011` | 4 | Category 5, sub-condition 50, variant 1 |
| `73011` | 5 | Category 7, sub-condition 30, variant 1 |
| `74011` | 6 | Category 7, sub-condition 40, variant 1 |
| `53011` | 7 | Category 5, sub-condition 30, variant 1 |
| `54011` | 8 | Category 5, sub-condition 40, variant 1 |
| `71011` | 9 | Category 7, sub-condition 10, variant 1 (duplicate check) |
| `2201` | 10 | Primary condition variant |
| `51011` | 11 | Category 5, sub-condition 10, variant 1 |

- **Evidence**: Paradigm structure derived from event scan (12 primary condition codes with consistent counts); epoch alignment recommendation confirms SocialCognitive_12class paradigm; identical structure to companion datasets ds004849 and ds004852.
- **Kernel Notes**: Single aggregated file prevents subject-level separation; XYYZZ event code format indicates hierarchical condition encoding (X=category, YY=sub-condition, ZZ=variant); nested events (X0010, X0110, X0111) may represent trial substructure/feedback markers not included in primary 12-class target; alignment: onset.

### Potential Task 1: Nback Working Memory Classification
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for Nback task (dataset-specific mapping)
- **Evidence**: Mentioned in OpenNeuro BIDS metadata as tasksCompleted; verify via dataset README for trial structure (typically 1-2s stimulus with variable ISI). Source: https://openneuro.org/datasets/ds004850 DOI: https://doi.org/10.18112/openneuro.ds004850.v1.0.0
- **Kernel Notes**: Parameters暂标记为待验证，待确认后填写。 Verify Nback trial structure and event mapping from task README before finalizing epoch extraction. Single aggregated file may limit subject-level Nback analysis.

### Potential Task 2: Trial Substructure Analysis (Nested Events)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.5 s, target_events = [51110, 52110, 52111, 53110, 53111, 54110, 54111, 55110, 55111, 71110, 72110, 72111, 73110, 73111, 74110, 74111, 75110, 75111]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: Nested variant codes (XYY10, XYY11) indicating trial substructure
- **Evidence**: XYYZZ format (category, sub-condition, variant) suggests nested experimental structure; variant codes (10/11) may indicate feedback, response, or condition subtypes not in primary 12-class mapping.
- **Kernel Notes**: 19 nested event types with consistent counts suggest structured trial sub-events; separate from primary 12-class task — verify if these represent stimulus-locked or response-locked events; may require distinct epoch windows for proper interpretation.

### Potential Task 3: Session/Sequence Marker Analysis
- **Task Type**: detection
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30.0 s, target_events = [2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: Sequence/phase marker events
- **Evidence**: 2090-2098 series (counts: 66-124) suggest session or sequence markers; distinct from stimulus events.
- **Kernel Notes**: 9 sequence marker types may indicate block structure or task phases; segment-based extraction for continuous state analysis; align with primary stimulus events for phase-dependent analysis.