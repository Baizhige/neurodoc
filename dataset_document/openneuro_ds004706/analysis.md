# Spatial Memory and Non-Invasive Closed-Loop Stimulus Timing

**Dataset**: `openneuro_ds004706` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004706
**Category**: High-level Mental | **Subjects**: 149 | **Files (Completed)**: 298
**Channels**: 137 | **Sampling Rate**: 2048 Hz
**Manual Review**: Pending

## Paradigm

A hybrid spatial-navigation and free recall task where participants delivered items to locations in a virtual town environment, with EEG recorded during both encoding and retrieval phases. The paradigm incorporates closed-loop stimulus timing to investigate the relationship between memory encoding, theta oscillations, and stimulation-driven memory enhancement. Sessions included free recall and cued recall phases with video stimuli.

## File Scan Result

> **Kernel SHA256**: `2dbab021919d54b2e66e38e1fe87013d5d6a8568e8740b69522728dd4b08a4b3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_65536` | 1 | event | raw | Recording start marker |
| `event_65544` | 27 | event | raw | Session boundary marker |
| `event_8` | 1690758 | event | raw | Primary stimulus/response event (word encoding, recall responses) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Memory Encoding Success Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.3 s, tmax = 1.3 s, target_events = [`WORD`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `WORD` | 1 | Word subsequently remembered (encoding success) |
  | `WORD` | 0 | Word subsequently forgotten (encoding failure) |
- **Kernel Notes**: Extract epochs centered on WORD events (0.3–1.3 s post-onset) to capture encoding dynamics after word presentation ends (~2.5 s display). Labels derived by cross-event matching: if a WORD event is followed by a REC_WORD event with matching content/identifier, assign y=1 (remembered); otherwise y=0 (forgotten). Use spectral features (theta/alpha/beta/gamma bands) for L2-penalized logistic regression. Note: Verify that event IDs in analysis.md (WORD, REC_WORD) map to actual HDF5 event structures—only numeric event codes (event_8, event_65536, event_65544) were visible in file scan; string events may be stored as hierarchical fields (event.value). Downsample from 2048 Hz to 256–512 Hz for spectral feature efficiency while retaining phase information. Exclude CLASSIFIER/CLASSIFIER_WAIT events as administrative markers.
- **Evidence**: DOI: 10.1037/xlm0001341

### Normal Task 1: Memory State Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`WORD`, `REC_WORD`, `CUED_REC_CUE`, `CUED_REC_WORD`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `WORD` | 0 | Word encoding phase |
  | `REC_WORD` | 1 | Free recall response |
  | `CUED_REC_CUE` | 2 | Cued recall cue onset |
  | `CUED_REC_WORD` | 3 | Cued recall response |
- **Kernel Notes**: Four-class classification of memory states across encoding and retrieval phases. Epoch window captures pre-stimulus baseline (-200 ms) through stimulus encoding and initial retrieval response. Treat CLASSIFIER/CLASSIFIER_WAIT as administrative events—exclude from analysis epochs. Window spans 1.2 s centered on event onset. Verify event ID mapping in HDF5 (same complication as Classical Task 1). Multiclass labels enable analysis of state-dependent spectral signatures across the memory cycle.
- **Evidence**: Paradigm description; epoch alignment recommendations

### Potential Task 2: Theta Phase-Amplitude Coupling Analysis
- **Task Type**: regression / connectivity
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.5 s, segment_length = 3.0 s, target_events = [`WORD`, `EFR_MARK`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `WORD` | theta_phase | Phase of theta oscillation at word onset |
  | `EFR_MARK` | coupling_strength | Theta-gamma coupling measure at encoding marker |
- **Kernel Notes**: Extended 3 s epochs centered on WORD events needed to analyze theta-gamma coupling during memory encoding. Paradigm explicitly mentions closed-loop stimulus timing targeting theta oscillations for stimulation-driven memory enhancement. Captures pre-stimulus baseline and full encoding window for cross-frequency coupling analysis. High sampling rate (2048 Hz) preserves phase information for coupling metrics. EFR_MARK events provide orthogonal validation markers for encoding phase. Downsample to 512 Hz for efficiency while retaining theta phase accuracy. Exclude CLASSIFIER/CLASSIFIER_WAIT administrative events from coupling analysis.
- **Evidence**: Paradigm description (closed-loop theta stimulation, theta oscillations, memory enhancement)