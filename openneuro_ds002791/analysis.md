# DataSet1 - Visual Object Naming EEG

**Dataset**: `openneuro_ds002791` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002791
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 92 | **Channels**: 256 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed and named visual objects (pictures presented as bitmap images) during high-density 256-channel EEG recording. Each event label is the filename of the presented image (e.g., GLOVE.bmp, GORILLA.bmp), corresponding to 30 distinct visual object categories. The task likely involved overt or covert naming or picture-word matching. This is DataSet1 of a paired dataset series (see also DataSet2: ds002833).

## File Scan Result

> **Kernel SHA256**: `14da52f3b53f696e39f72f6b27d5bf353f8d008c31d8053c53f4ce41b09c46ee`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger/D249` | 9855829 | event | raw | Stimulus presentation trigger (onset marker) |
| `trigger/D250` | 9844475 | event | raw | Response/completion trigger (offset marker) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Visual Object Naming — Stimulus Category Classification / Response Time Regression

- **Task Type**: classification / regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `stim` (derived from stimulus presentation timing) / `misc` (response_time)
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | Stimulus onset (derived) | category_id (0–29) | Visual object category (30 classes) |
  | Stimulus onset (derived) | response_time | Naming latency (ms) from misc channel |

- **Evidence (DOI)**: None (paradigm is plausible; however, neither partial reference explicitly cites this dataset or defines an ML-ready task with labeled epochs)
- **Kernel Notes**: 
  - **Critical**: The raw event structure contains only generic trigger markers (`trigger/D249`: ~9.86M, `trigger/D250`: ~9.84M). The 30 visual object categories (e.g., GLOVE.bmp, FEATHER.bmp, GORILLA.bmp) are NOT present as native event IDs.
  - Stimulus onset events must be **derived** from the continuous EEG stream or metadata channels before epoching; the original paradigm confirms picture stimuli were presented one per trial.
  - The `response_time` label stored via the `misc` route is available as a regression target for naming latency analysis.
  - For classification, semantic grouping (animate/inanimate or living/nonliving) is recommended over 30-way identity classification to improve model stability.
  - 256-channel EGI/HydroCell array provides high spatial resolution for ERP/source analysis.

## Data Quality Notes

- 30 distinct object images (e.g., GLOVE.bmp, CARROT.bmp, FISH.bmp, ALLIGATO.bmp) across 92 files (46 files containing stimulus events each).
- High-density 256-channel EEG; verify electrode positions and bad channel rejection per subject before pooling.
- Stimulus event derivation required prior to epoching; verify alignment between derived stimulus onsets and response_time labels.