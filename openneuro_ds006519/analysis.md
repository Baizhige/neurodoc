# Dataset of Intracranial EEG during Cortical Stimulations Evoking Negative Motor Responses

**Dataset**: `openneuro_ds006519` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006519
**Category**: Action/Output | **Subjects**: 23 | **Files (Completed)**: 35 | **Channels**: 33 | **Sampling Rate**: 4096 Hz
**Manual Review**: Pending

## Paradigm

Patients undergoing presurgical evaluation for drug-resistant epilepsy received intracranial electrical stimulation to map cortical function. The stimulation protocol targeted regions that, when stimulated, evoked negative motor responses (involuntary movement inhibition or arrest). EEG was recorded from intracranial electrodes during pre-stimulation (prestim) and post-stimulation (poststim) periods to characterize neural activity changes associated with negative motor mapping.

## File Scan Result

> **Kernel SHA256**: `ef4db72c250192ddcac3bf81f87a71ba23d22ca47154bbdf66d42939b8d55087`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `poststim` | 35 | event | raw | Post-stimulation response period onset |
| `prestim` | 35 | event | raw | Pre-stimulation baseline period onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Pre- vs Post-Stimulation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = ["prestim", "poststim"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `prestim` | 0 | Pre-stimulation baseline period |
| `poststim` | 1 | Post-stimulation response period |

- **Evidence**: OpenNeuro dataset metadata and paradigm description. Source: https://openneuro.org/datasets/ds006519 DOI: https://doi.org/10.18112/openneuro.ds006519.v1.0.0
- **Kernel Notes**: Alignment is ONSET (both events are 'short' type, <2s). The tmin=-0.2s includes a brief pre-stimulus baseline window. Downsampling from 4096 Hz to ≤1000 Hz recommended before epoching due to high sampling rate. Event counts are balanced (35 each), confirming paired trial structure suitable for binary classification.

### Potential Task 1: Long-Segment Stimulation Analysis
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s*, tmax = 4.0 s*, overlap = null, target_events = ["prestim", "poststim"] (requires verification of long-event structure)
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `prestim` | 0 | Pre-stimulation baseline |
| `poststim` | 1 | Sustained post-stimulation response |

- **Evidence**: Paradigm description indicates stimulation-evoked negative motor responses with sustained cortical effects; epoch alignment recommendations suggest 4-second window for capturing full stimulation response.
- **Kernel Notes**: Verify that long-event structure exists in actual data files, or adjust to epoch_by_event_hdf5 with extended window if stimulation periods are marked as consecutive short events. Requires confirmation of stimulation duration from dataset documentation to refine tmax.

### Potential Task 2: Publisher-Defined BIDS Task (Dcs)
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `prestim` | Needs verification | BIDS task condition TBD |
| `poststim` | Needs verification | BIDS task condition TBD |

- **Evidence**: OpenNeuro metadata.tasksCompleted references a BIDS task named 'Dcs'. Source: https://openneuro.org/datasets/ds006519 DOI: https://doi.org/10.18112/openneuro.ds006519.v1.0.0
- **Kernel Notes**: No task-specific parameters provided in dataset metadata. Verify BIDS task JSON or README for event definitions and epoch parameters before implementation. Default to Normal Task 1 parameters if no additional documentation is found.