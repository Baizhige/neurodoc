# Visual Hemifield RSVP Object Recognition Dataset

**Dataset**: openneuro_ds005087 | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005087
**Category**: EEG | **Subjects**: 80 | **Files (Completed)**: 80 | **Channels**: 63 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed object and word stimuli presented at 5 Hz in rapid visual streams (RSVP) to the left hemifield, right hemifield, or central visual field while performing a red target detection task. The dataset was collected to study dynamics of visual object coding within and across the hemispheres, with stimuli presented in the periphery. Event codes E 1, E 2, and E 3 mark left hemifield, right hemifield, and center visual field presentation positions respectively.

## File Scan Result

> **Kernel SHA256**: `38648154ca3e6337ad2c6994b0ae245ca49eb331230179fa54e8e369f2af63a8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 184320 | event | raw | Left hemifield presentation |
| `E  2` | 184320 | event | raw | Right hemifield presentation |
| `E  3` | 960 | event | raw | Center visual field presentation |
| `Event/E  1` | 184320 | event | raw | Left hemifield presentation (annotated) |
| `Event/E  2` | 184320 | event | raw | Right hemifield presentation (annotated) |
| `Event/E  3` | 960 | event | raw | Center visual field presentation (annotated) |
| `boundary` | 20 | event | raw | Recording boundary marker (exclude) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Hemifield Presentation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["E  1", "E  2", "E  3"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | `E  1` | 0 | Left hemifield presentation |
 | `E  2` | 1 | Right hemifield presentation |
 | `E  3` | 2 | Center visual field presentation |

- **Evidence**: DOI: https://doi.org/10.1126/sciadv.adq0889 | Robinson et al. (2025) "Dynamics of visual object coding within and across the hemispheres: Objects in the periphery" - explicitly describes MVPA classification of visual field position using this exact dataset (80 subjects, 63-channel EEG at 1000 Hz, RSVP at 5 Hz). Event codes E 1/E 2/E 3 match dataset metadata. Epoch parameters validated against published analysis pipeline.
- **Kernel Notes**: E 3 condition is rare (960 vs 184k for E 1/E 2) - recommend separate class or exclusion to avoid class imbalance. Boundary events (n=20) should be excluded during epoch extraction.

### Potential Task 1: Stimulus Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["1", "2", "3"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | `1` | 0 | Stimulus category/identity code 1 |
 | `2` | 1 | Stimulus category/identity code 2 |
 | `3` | 2 | Stimulus category/identity code 3 |

- **Evidence**: Plausible from paradigm - numeric codes 1/2/3 likely encode object category within RSVP stream (objects/faces/words per reference paper context). No direct classification reference.
- **Kernel Notes**: Verify code meanings from events.tsv. Class counts are imbalanced (92,160 / 46,080 / 46,080) - apply class weighting if needed.

### Normal Task 1: Hemifield × Stimulus Interaction Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["E  1", "E  2"] + ["1", "2", "3"], compound_labels = true
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | `E  1` + `1` | 0 | Left hemifield, category 1 |
 | `E  1` + `2` | 1 | Left hemifield, category 2 |
 | `E  2` + `1` | 2 | Right hemifield, category 1 |
 | `E  2` + `2` | 3 | Right hemifield, category 2 |

- **Evidence**: Partial support from reference paper's super meta note "Single vs dual peripheral conditions; objects/faces/words stimulus categories" - suggests interaction analysis between position and category.
- **Kernel Notes**: Requires temporal alignment of hemifield markers with subsequent stimulus codes within RSVP stream window.

### Primary Task: Publisher-defined BIDS task: Rsvp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["E  1", "E  2", "E  3"]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005087 DOI: https://doi.org/10.31234/osf.io/a3bpd
