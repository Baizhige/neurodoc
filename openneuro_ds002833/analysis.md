# DataSet2 - Visual Object Naming EEG (High-Density)

**Dataset**: `openneuro_ds002833` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002833
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 257 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

High-density 257-channel EEG recorded during a visual object naming or picture viewing task, companion to DataSet1 (ds002791). The DIN1 marker is an EGI/Geodesic system digital input trigger marking stimulus onset. The `unknown` label in 20 files indicates undecodable trigger codes for those sessions. The study likely involves the same visual object paradigm as ds002791 (30 object categories), recorded with an EGI system.

## File Scan Result

> **Kernel SHA256**: `2195a8f01eccf34bca4e9140cfb399bfea7ab97e819d918a690c17a6da4b5b1c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Stimulus-Locked Visual ERP Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [DIN1]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| DIN1 | response_time | Visual stimulus onset with associated response latency |

- **Evidence**: Paradigm description indicates visual object naming with EGI stimulus triggers; partial reference (10.1038/s41597-021-00821-1) confirms HD-EEG visual naming methodology; alignment recommendations support onset-locked analysis window.
  - DOI: 10.1038/s41597-021-00821-1
- **Kernel Notes**: DIN1 serves as epoch anchor for stimulus-locked ERP analysis. The -0.2s to 1.0s window captures N1/P1 visual components and early N400 semantic processing. Exclude `unknown` admin events (undecodable trigger codes in 20/80 files). Response time regression target stored in misc channel requires Type 2 derivation. Verify channel consistency across 257-channel EGI HydroCell array before pooling.

### Potential Task 1: Visual Object Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = [DIN1]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| DIN1 | trial_type (from events.tsv) | Object category label (30 categories per paradigm) |

- **Evidence**: Paradigm description specifies visual object naming with 30 object categories; OpenNeuro dataset metadata confirms Pictures Naming BIDS task; alignment recommendations specify post-stimulus classification window. No direct classification-relevant reference.
  - DOI: https://doi.org/10.18112/openneuro.ds002833.v1.0.0
- **Kernel Notes**: Stimulus identity (object category) must be derived from events.tsv trial_type/value columns since DIN1 only marks onset without condition encoding. Use post-stimulus window (tmin=0.0) to capture discriminative visual object-related activity. Exclude `unknown` events from target set. High-density 257-channel layout may require spatial downsampling for computational efficiency. Type 2 label integration required for BIDS task annotation route.