# EEG Experiment measuring ERPs in VR

**Dataset**: `openneuro_ds005841` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005841
**Category**: Complex Applied | **Subjects**: 48 | **Files (Completed)**: 288 | **Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

An investigation of event-related potentials (ERPs) during visual tasks performed within a virtual reality (VR) environment. Stimuli vary along two orthogonal dimensions: lighting (DARK vs LIGHT) and reference type (RAND = random/unpredictable vs REF = reference/predictable). The 2x2 design yields four event codes measuring visual ERP responses under prediction-error conditions.

## File Scan Result

> **Kernel SHA256**: `dff9f33d6713a8cc2dce7301d67b7be99593cdbd614f1d3bc57a4b391976c202`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 1335 | event | raw | Session event (verify via events.tsv) |
| `event_11` | 2038 | event | raw | Primary stimulus condition |
| `event_12` | 2037 | event | raw | Primary stimulus condition |
| `event_13` | 2036 | event | raw | Primary stimulus condition |
| `event_14` | 2037 | event | raw | Primary stimulus condition |
| `event_15` | 1401 | event | raw | Secondary stimulus event |
| `event_16` | 1391 | event | raw | Secondary stimulus event |
| `event_17` | 1397 | event | raw | Secondary stimulus event |
| `event_18` | 1403 | event | raw | Secondary stimulus event |
| `event_2` | 1345 | event | raw | Session event (verify via events.tsv) |
| `event_3` | 1341 | event | raw | Session event (verify via events.tsv) |
| `event_4` | 1338 | event | raw | Session event (verify via events.tsv) |
| `event_5` | 1417 | event | raw | Stimulus sub-event (verify via events.tsv) |
| `event_53` | 45 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_55` | 43 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_56` | 47 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_57` | 44 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_58` | 48 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_59` | 41 | event | raw | VR stimulus onset (low-count primary condition) |
| `event_6` | 1413 | event | raw | Stimulus sub-event (verify via events.tsv) |
| `event_65536` | 2 | admin | raw | Session boundary marker |
| `event_65548` | 3 | admin | raw | Session boundary marker |
| `event_7` | 1414 | event | raw | Stimulus sub-event (verify via events.tsv) |
| `event_8` | 1416 | event | raw | Stimulus sub-event (verify via events.tsv) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: VR Visual Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_53`, `event_55`, `event_56`, `event_57`, `event_58`, `event_59`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_53` | 0 | VR stimulus condition (low-count event; verify via events.tsv) |
  | `event_55` | 1 | VR stimulus condition (low-count event; verify via events.tsv) |
  | `event_56` | 2 | VR stimulus condition (low-count event; verify via events.tsv) |
  | `event_57` | 3 | VR stimulus condition (low-count event; verify via events.tsv) |
  | `event_58` | 4 | VR stimulus condition (low-count event; verify via events.tsv) |
  | `event_59` | 5 | VR stimulus condition (low-count event; verify via events.tsv) |
- **Evidence (DOI)**: N/A — no reference papers with classification=relevant available for this dataset
- **Kernel Notes**: CRITICAL MISMATCH DETECTED between analysis.md paradigm description and actual event structure. Analysis.md describes 4 conditions (RAND_DARK, RAND_LIGHT, REF_DARK, REF_LIGHT with 288 trials each), but available event IDs show: (1) low-count events (event_53-59: 41-48 trials) likely corresponding to primary stimulus conditions, and (2) high-count events (event_1-8: 1300-2000+ trials) possibly indicating sub-stimuli, feedback, or concatenated sessions. Kernel MUST: (a) inspect BIDS events.tsv files to establish exact correspondence between analysis.md conditions and actual event codes, (b) verify session structure (48 subjects × 6 sessions = 288 files; are sessions concatenated or separate?), (c) confirm whether low-count events represent epoch-able stimulus onsets. Apply bandpass filter (1-40 Hz) and ICA for VR motion artifact removal. Do NOT assume analysis.md event names map directly to available event IDs.

### Potential Task 2: VR Prediction Error Analysis (RAND vs REF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_53`, `event_55`, `event_56`, `event_57`, `event_58`, `event_59`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_53` | 0 | Unpredictable (random) VR stimulus condition |
  | `event_55` | 1 | Unpredictable (random) VR stimulus condition |
  | `event_56` | 2 | Unpredictable (random) VR stimulus condition |
  | `event_57` | 3 | Predictable (reference) VR stimulus condition |
  | `event_58` | 4 | Predictable (reference) VR stimulus condition |
  | `event_59` | 5 | Predictable (reference) VR stimulus condition |
- **Evidence (DOI)**: N/A — no reference papers with classification=relevant available for this dataset
- **Kernel Notes**: Binary classification of prediction error ERP component (mismatch negativity / N200). This task collapses across lighting conditions (DARK/LIGHT) to isolate neural response to stimulus predictability. Kernel MUST verify which event codes correspond to RAND vs REF conditions by cross-referencing BIDS events.tsv with paradigm description. Primary contrasts: unpredictable (RAND) vs predictable (REF) stimulus presentation.

### Potential Task 3: VR Luminance Effect Analysis (DARK vs LIGHT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`event_53`, `event_55`, `event_56`, `event_57`, `event_58`, `event_59`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_53` | 0 | Dark luminance VR stimulus |
  | `event_55` | 1 | Dark luminance VR stimulus |
  | `event_56` | 2 | Light luminance VR stimulus |
  | `event_57` | 3 | Light luminance VR stimulus |
  | `event_58` | 4 | Light luminance VR stimulus |
  | `event_59` | 5 | Dark luminance VR stimulus |
- **Evidence (DOI)**: N/A — no reference papers with classification=relevant available for this dataset
- **Kernel Notes**: Binary classification of luminance-based ERP differences. Collapses across predictability conditions (RAND vs REF) to isolate neural response to lighting variation in VR environment. Kernel MUST verify event code mapping to DARK vs LIGHT conditions via BIDS events.tsv inspection.