# Poetry EEG Study

**Dataset**: `openneuro_ds006647` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006647
**Category**: High-level Mental | **Subjects**: 51 | **Files (Completed)**: 4 | **Channels**: 70 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants read and evaluated 210 short poetic (Haiku, Senryu) and non-poetic control texts on five subjective dimensions: Aesthetic Appeal, Vivid Imagery, Being Moved, Originality, and Creativity. EEG was recorded during reading using a 64-channel BioSemi system. The study investigates neural correlates of aesthetic and creative cognition during poetry processing. BioSemi EDF trigger codes (65280-65288) encode stimulus onset and condition types.

## File Scan Result

> **Kernel SHA256**: `41238c913650e8aee93c6d08a502fd173adb57ece461b45c54422e369b91fdbd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65280` | 4 | event | raw | BioSemi calibration pulse |
| `65281` | 848 | event | raw | BioSemi trigger - Haiku stimulus onset |
| `65282` | 848 | event | raw | BioSemi trigger - Senryu stimulus onset |
| `65283` | 848 | event | raw | BioSemi trigger - non-poetic control stimulus onset |
| `65284` | 852 | event | raw | BioSemi trigger - additional condition stimulus onset |
| `65285` | 4 | event | raw | BioSemi calibration pulse |
| `65286` | 4 | event | raw | BioSemi calibration pulse |
| `65287` | 4 | event | raw | BioSemi calibration pulse |
| `65288` | 4 | event | raw | BioSemi calibration pulse |
| `boundary` | 5 | admin | raw | Segment boundary marker |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `EXG1`, `EXG2`, `EXG3`, `EXG4`, `EXG7`, `EXG8`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Poetry Condition Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [65281, 65282, 65283, 65284]
- **Label Route**: Annotation
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |----|---|---|
  | 65281 | 1 | BioSemi condition code 65281 (Haiku) |
  | 65282 | 2 | BioSemi condition code 65282 (Senryu) |
  | 65283 | 3 | BioSemi condition code 65283 (non-poetic control) |
  | 65284 | 4 | BioSemi condition code 65284 (additional condition) |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-06189-w
- **Kernel Notes**: Use high-count events (65281-65284, ~848 each) for primary classification. Low-count events (65280, 65285-65288, 4 each) are likely calibration pulses—exclude from analysis. Decode condition mapping from events.tsv for definitive label assignment. The reference paper confirms 3-class paradigm (Haiku, Senryu, non-poetic control); verify if 4 event codes map to 3 conditions or represent sub-conditions.

### Potential Task 1: Aesthetic Judgment Regression
- **Task Type**: regression
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [65281, 65282, 65283, 65284]
- **Label Route**: Annotation
- **Meta Level**: super
- **Target Definition**:

  | Event | y | Meaning |
  |----|---|---|
  | 65281 | continuous | Aesthetic Appeal rating (1-7 scale) |
  | 65282 | continuous | Vivid Imagery rating (1-7 scale) |
  | 65283 | continuous | Being Moved rating (1-7 scale) |
  | 65284 | continuous | Originality/Creativity rating (1-7 scale) |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-06189-w (partial support for 5 continuous rating dimensions)
- **Kernel Notes**: Requires super-level meta integration from behavioral ratings file (events.tsv). Labels are continuous rather than categorical; use regression loss instead of classification loss. Five dimensions reported: Aesthetic Appeal, Vivid Imagery, Being Moved, Originality, Creativity. Verify exact dimension-to-event mapping in events.tsv.

### Potential Task 2: Sustained Reading Analysis
- **Task Type**: segmentation
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = null, overlap = null, segment_length = variable, target_events = [65281, 65282, 65283, 65284]
- **Label Route**: Annotation
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |----|---|---|
  | 65281 | 1 | Reading segment for Haiku stimulus |
  | 65282 | 2 | Reading segment for Senryu stimulus |
  | 65283 | 3 | Reading segment for non-poetic control |
  | 65284 | 4 | Reading segment for additional condition |

- **Evidence**: Paradigm plausibility (no reference required)
- **Kernel Notes**: Variable-length segments capture full reading period per trial. Align segments to stimulus onset markers. Use detected text offset or word count for segmentation boundaries rather than fixed duration. Exclude boundary markers (n=5 admin events).

### Normal Task 1: Neural Correlates of Aesthetic and Creative Cognition
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [65281, 65282, 65283, 65284]
- **Label Route**: Annotation
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |----|---|---|
  | 65281 | 1 | Poetry condition (aesthetic processing) |
  | 65282 | 1 | Poetry condition (aesthetic processing) |
  | 65283 | 0 | Non-poetry control condition |
  | 65284 | 1 | Poetry condition (aesthetic processing) |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-06189-w (paradigm evidence, not direct classification-relevant)
- **Kernel Notes**: Binary contrast between poetry (Haiku, Senryu, and additional conditions) and non-poetic control. Tests whether aesthetic processing during poetry reading produces distinct neural signatures. Collapse 3 poetry conditions into single class for binary analysis.