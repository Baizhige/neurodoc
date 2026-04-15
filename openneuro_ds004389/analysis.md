# Somatosensory Evoked Potentials in the Human Spinal Cord to Mixed and Sensory Nerve Stimulation

**Dataset**: `openneuro_ds004389` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004389
**Category**: Sensory/Response | **Subjects**: 26 | **Files (Completed)**: 259 | **Channels**: 90 | **Sampling Rate**: 10000 Hz
**Manual Review**: Pending

## Paradigm

Simultaneous EEG, epidural spinal cord (ESG), nerve conduction (ENG), and EMG recordings during resting state and various conditions of mixed and sensory nerve stimulation of the arms and legs to evoke somatosensory potentials. The study compares spinal cord vs. cortical potentials for different stimulation types and sites.

## File Scan Result

> **Kernel SHA256**: `f2113e548187a3942585127fb11d7479488553ba3568414ab9a7f87f25e0b756`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `med1` | 52001 | event | raw | Median sensory nerve stimulation (site 1) |
| `med12` | 51997 | event | raw | Median sensory nerve stimulation (combined sites 1+2) |
| `med2` | 51994 | event | raw | Median sensory nerve stimulation (site 2) |
| `medMixed` | 49996 | event | raw | Median mixed nerve stimulation (motor+sensory) |
| `tib1` | 52003 | event | raw | Tibial nerve stimulation (site 1) |
| `tib12` | 51997 | event | raw | Tibial nerve stimulation (combined sites 1+2) |
| `tib2` | 51995 | event | raw | Tibial nerve stimulation (site 2) |
| `tibMixed` | 51997 | event | raw | Tibial mixed nerve stimulation (motor+sensory) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: SEP Stimulus Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, overlap = null, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `med1` | 0 | Median sensory nerve stimulation (single site) |
| `med12` | 1 | Median sensory nerve stimulation (combined sites) |
| `med2` | 2 | Median sensory nerve stimulation (site 2) |
| `medMixed` | 3 | Median mixed nerve stimulation (motor+sensory) |
| `tib1` | 4 | Tibial nerve stimulation (single site) |
| `tib12` | 5 | Tibial nerve stimulation (combined sites) |
| `tib2` | 6 | Tibial nerve stimulation (site 2) |
| `tibMixed` | 7 | Tibial mixed nerve stimulation (motor+sensory) |

- **Evidence**: Published OpenNeuro dataset with documented paradigm. DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0
- **Kernel Notes**: Raw trigger codes (med1=52001, med2=51994, med12=51997, medMixed=49996, tib1=52003, tib2=51995, tib12=51997, tibMixed=51997) require translation to semantic labels. Note tib12 and tibMixed share code 51997—differentiate by trial timing/context. Route labels via `Annotation` channel per EEGUnity specification. Downsampling to 1000Hz recommended to preserve SEP frequency content while reducing memory footprint.

### Classical Task 2: Mediansensory Task Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, overlap = null, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `med1` | 0 | Median sensory nerve stimulation (site 1) |
| `med12` | 1 | Median sensory nerve stimulation (combined sites) |
| `med2` | 2 | Median sensory nerve stimulation (site 2) |

- **Evidence**: Published OpenNeuro dataset with documented paradigm. DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0
- **Kernel Notes**: BIDS task label = "Mediansensory". Sensory-only stimulation events (med1, med12, med2) map to cortical SEP N20-P30-N40 complex. Filter to EEG channels only; exclude ESG/ENG/EMG channels.

### Classical Task 3: Medianmixed Task Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, overlap = null, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `medMixed` | 0 | Median mixed nerve stimulation |

- **Evidence**: Published OpenNeuro dataset with documented paradigm. DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0
- **Kernel Notes**: BIDS task label = "Medianmixed". Mixed nerve stimulation combines motor and sensory fiber activation, producing larger EMG contamination requiring clean baseline window (-0.5s to 0s).

### Normal Task 1: Tibialmixed Task Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, overlap = null, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `tib1` | 0 | Tibial nerve stimulation (site 1) |
| `tib12` | 1 | Tibial nerve stimulation (combined sites) |
| `tib2` | 2 | Tibial nerve stimulation (site 2) |
| `tibMixed` | 3 | Tibial mixed nerve stimulation |

- **Meta Level**: raw
- **Evidence**: Paradigm description supports tibial nerve stimulation as primary experimental condition. DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0
- **Kernel Notes**: BIDS task label = "Tibialmixed". Longer latencies than median nerve stimulation; 2s window captures P40-N60 tibial SEP components. tib12 and tibMixed share code 51997—resolve via trial timing context.