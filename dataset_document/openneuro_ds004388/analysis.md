# Somatosensory evoked potentials in the human spinal cord to mixed nerve stimulation

**Dataset**: `openneuro_ds004388` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004388
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 399 | **Channels**: 115 | **Sampling Rate**: 10000 Hz | **Manual Review**: Pending

## Paradigm

The dataset records somatosensory evoked potentials (SEPs) in response to mixed median and tibial nerve stimulation, alongside a resting state condition. Simultaneous EEG and epidural spinal cord recordings (ESG) were acquired to characterize the spinal and cortical processing of somatosensory signals.

## File Scan Result

> **Kernel SHA256**: `f58bbb2edf4229e8c1fa16409bacb920c3d8fa34047f95240d5d1b6f692688f3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Median - Stimulation` | 112498 | event | raw | Median nerve electrical stimulation onset (upper limb SEP) |
| `Tibial - Stimulation` | 111997 | event | raw | Tibial nerve electrical stimulation onset (lower limb SEP) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: SEP Stimulus Classification by Stimulation Site
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = [`Median - Stimulation`, `Tibial - Stimulation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Median - Stimulation` | 0 | Median nerve stimulation (upper limb SEP) |
  | `Tibial - Stimulation` | 1 | Tibial nerve stimulation (lower limb SEP) |
- **Kernel Notes**: Bimodal event distribution (112,498 median + 111,997 tibial events) enables binary classification comparing upper vs lower limb somatosensory processing. The 2.0s window captures spinal (N13-P13) and cortical (N20-P37) SEP components. Channel mix includes scalp EEG, spinal ESG, and peripheral ENG/EMG—consider channel-specific filtering. Dataset includes both stimulation and resting state conditions across 399 files/40 subjects.
- **Evidence**: Supported by dataset paradigm: mixed median and tibial nerve stimulation with simultaneous EEG and epidural spinal cord recordings (ESG) for characterizing spinal and cortical processing of somatosensory signals.

---

### Potential Task 2: Evoked Potential Averaging by Stimulation Site
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = [`Median - Stimulation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `Median - Stimulation` | 0 | Median nerve stimulation onset |
- **Kernel Notes**: Single-site SEP averaging for upper limb responses. The 10kHz sampling rate preserves fast somatosensory peak latencies; recommend downsampling to 1000Hz post-epoching for standard EEG analysis while retaining SEP fidelity. File naming conventions may encode stimulation parameters for regression targets.
- **Evidence**: Paradigm-plausible task: stimulus-locked SEP acquisition with known upper limb SEP generators (median nerve → cervicomedullary junction → primary somatosensory cortex).

---

### Potential Task 3: Evoked Potential Averaging by Stimulation Site (Tibial)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = [`Tibial - Stimulation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `Tibial - Stimulation` | 0 | Tibial nerve stimulation onset |
- **Kernel Notes**: Single-site SEP averaging for lower limb responses. Lower limb SEPs show larger spinalcord involvement (lumbar enlargement) with distinct cortical generators compared to median nerve. Same epoching rationale as median stimulation task.
- **Evidence**: Paradigm-plausible task: stimulus-locked SEP acquisition with known lower limb SEP generators (tibial nerve → lumbar spinal cord → sensorimotor cortex).

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
