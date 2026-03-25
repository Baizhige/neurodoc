# TUH EEG Events Corpus

**Dataset**: `tuh_eeg_events` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_events/v2.0.1/
**Category**: Biological State | **Subjects**: ~370 | **Files (Completed)**: 518 | **Channels**: 24-33 | **Sampling Rate**: 250 Hz

## Paradigm

The TUH EEG Events Corpus (v2.0.1) provides time-stamped annotations of neurological events in 518 clinical EEG recordings from ~370 unique patients (Shah et al., 2018). Expert neurologists annotated six event types at temporal and spatial resolution using companion `.rec` sidecar files (4-column format: channel, start_time, stop_time, label_code). Events include epileptiform discharges, background EEG, and artifact. All recordings are sampled at 250 Hz with 24-33 channels.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_events/v2.0.1/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `background` | varies | long | raw | Normal background EEG activity |
| `spike and sharp wave` | varies | short | raw | Spike or sharp wave discharge |
| `generalized periodic epileptiform discharges` | varies | short | raw | GPEDs - generalized periodic epileptiform pattern |
| `periodic lateralized epileptiform discharges` | varies | short | raw | PLEDs - lateralized epileptiform pattern |
| `eye movement` | varies | short | raw | Eye movement artifact |
| `artifact` | varies | short | raw | Non-specific artifact |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Label codes from `.rec` files: 1=spike and sharp wave, 2=generalized periodic epileptiform discharges, 3=periodic lateralized epileptiform discharges, 4=eye movement, 5=artifact, 6=background.

## Tasks

### Primary Task 1: Neurological EEG event detection/classification
- **Task Type**: classification/detection
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event classes from expert annotations (e.g., spikes, periodic discharges, artifacts, background).
- **Evidence**: TUH EEG Events Corpus provides time-stamped multi-class event annotations as the primary benchmark target. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.1109/globalsip.2013.6736803


### Normal Task 1: EEG Event Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `eye movement` and `artifact` events from classification targets. For binary detection: background (y=0) vs. any epileptiform event (y=1). `.rec` sidecar files must be present alongside `.edf` files.

| Event | y | Meaning |
|-------|---|---------|
| `background` | 0 | Normal background EEG |
| `spike and sharp wave` | 1 | Epileptiform spike/sharp wave |
| `generalized periodic epileptiform discharges` | 2 | GPEDs |
| `periodic lateralized epileptiform discharges` | 3 | PLEDs |


### Normal Task 2: Epileptiform vs. Normal EEG Detection (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `background` | 0 | Normal EEG |
| `spike and sharp wave` | 1 | Epileptiform |
| `generalized periodic epileptiform discharges` | 1 | Epileptiform |
| `periodic lateralized epileptiform discharges` | 1 | Epileptiform |
## Data Quality Notes

- `.rec` sidecar files required; if missing, no annotations are set.
- Background annotations are long events; epileptiform events are short - class length mismatch may cause imbalance.
- Uniform sampling rate (250 Hz) and consistent channel count (24-33); relatively homogeneous compared to other TUH subsets.
- Sex is not reliably available.

## References

- **Reference**: Shah V et al. (2018). The Temple University Hospital EEG Event Corpus. *Frontiers in Neuroscience*, 12, 862. https://isip.piconepress.com/projects/tuh_eeg/
