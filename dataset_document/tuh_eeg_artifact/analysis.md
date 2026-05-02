# TUH EEG Artifact Corpus

**Dataset**: `tuh_eeg_artifact` | **Year**: 2021-2020/2024 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Others | **Subjects**: 213 | **Files (Completed)**: 310 | **Channels**: 27-41 | **Sampling Rate**: 250/256/400/512 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The TUH EEG Artifact Corpus (TUAR) is a comprehensive dataset designed for the identification and evaluation of various artifacts in electroencephalogram (EEG) signals. This dataset includes EEG recordings annotated for multiple types of artifacts such as eye movements, muscle artifacts, and electrode issues, among others. The corpus has been developed to assist in the training and evaluation of artifact detection models, with its latest release (v3.0.1) offering detailed annotations for all relevant events across different channel configurations. The data is divided into files containing EEG signals, with annotations provided in CSV format to mark the start and stop times of specific artifact events. It consists of over 160,000 events from 310 EEG files, covering 213 patients and a total of nearly 100 hours of data. This dataset is particularly useful for research involving artifact detection and seizure classification in clinical EEG data. Notably, it includes specific seizure annotations alongside standard artifact labels, facilitating the analysis of co-occurring events. Researchers are encouraged to cite the corresponding publications for more details on the dataset's creation and annotation methodology.

## File Scan Result

> **Kernel SHA256**: `a76e25dadae339282ebf9cccfcc2d5d2081b8e73ccf097ad905d7e92cc8fb67e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `chew` | 6482 | event | raw | Chewing artifact period in EEG signal |
| `chew_elec` | 152 | event | raw | Concurrent chewing and electrode artifact in EEG |
| `chew_musc` | 243 | event | raw | Concurrent chewing and muscle artifact in EEG |
| `elec` | 33130 | event | raw | Electrode artifact period in EEG signal |
| `elpp` | 172 | event | raw | Electrode/potential artifact period in EEG signal |
| `eyem` | 38569 | event | raw | Eye movement artifact period in EEG signal |
| `eyem_chew` | 864 | event | raw | Concurrent eye movement and chewing artifact in EEG |
| `eyem_elec` | 2422 | event | raw | Concurrent eye movement and electrode artifact in EEG |
| `eyem_musc` | 18677 | event | raw | Concurrent eye movement and muscle artifact in EEG |
| `eyem_shiv` | 45 | event | raw | Concurrent eye movement and shivering artifact in EEG |
| `musc` | 51052 | event | raw | Muscle artifact period in EEG signal |
| `musc_elec` | 7651 | event | raw | Concurrent muscle and electrode artifact in EEG |
| `shiv` | 613 | event | raw | Shivering artifact period in EEG signal |
| `shiv_elec` | 1 | event | raw | Concurrent shivering and electrode artifact in EEG |


> [to_agent: Please check if there exist more artifact label and add background annotation for normal period?]

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Artifact Type Classification (13-class, Event-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, overlap = 0, target_events = [`chew`, `chew_elec`, `chew_musc`, `elec`, `elpp`, `eyem`, `eyem_chew`, `eyem_elec`, `eyem_musc`, `eyem_shiv`, `musc`, `musc_elec`, `shiv`, `shiv_elec`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `eyem` | 0 | Eye movement artifact |
  | `musc` | 1 | Muscle (EMG) artifact |
  | `elec` | 2 | Electrode artifact |
  | `chew` | 3 | Chewing artifact |
  | `shiv` | 4 | Shivering artifact |
  | `elpp` | 5 | Electrode pop |
  | `eyem_musc` | 6 | Combined eye movement + muscle |
  | `eyem_elec` | 7 | Combined eye movement + electrode |
  | `eyem_chew` | 8 | Combined eye movement + chewing |
  | `musc_elec` | 9 | Combined muscle + electrode |
  | `chew_elec` | 10 | Combined chewing + electrode |
  | `chew_musc` | 11 | Combined chewing + muscle |
  | `eyem_shiv` | 12 | Combined eye movement + shivering |
- **Evidence**:
  - 10.1109/EMBC48229.2022.9871413 — Achieves 93.95% accuracy with MMC on 1-second windows from artifact onset; uses FFT and DWT features on 4 temporal channels at 250 Hz
- **Notes**: the paper use 13 classes, but I think 6 classes more reasonable.

### Potential Task 1: Artifact Type Classification (13-class, Event-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, overlap = 0, target_events = [`chew`, `chew_elec`, `chew_musc`, `elec`, `elpp`, `eyem`, `eyem_chew`, `eyem_elec`, `eyem_musc`, `eyem_shiv`, `musc`, `musc_elec`, `shiv`, `shiv_elec`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `eyem` | 0 | Eye movement artifact |
  | `musc` | 1 | Muscle (EMG) artifact |
  | `elec` | 2 | Electrode artifact |
  | `chew` | 3 | Chewing artifact |
  | `shiv` | 4 | Shivering artifact |
  | `elpp` | 5 | Electrode pop |
  | `eyem_musc` | 0,1 | Combined eye movement + muscle |
  | `eyem_elec` | 0,2 | Combined eye movement + electrode |
  | `eyem_chew` | 0,3 | Combined eye movement + chewing |
  | `musc_elec` | 1,2 | Combined muscle + electrode |
  | `chew_elec` | 3,1 | Combined chewing + electrode |
  | `chew_musc` | 3,1 | Combined chewing + muscle |
  | `eyem_shiv` | 0,4 | Combined eye movement + shivering |
- **Evidence**:
  - 10.1109/EMBC48229.2022.9871413 — Achieves 93.95% accuracy with MMC on 1-second windows from artifact onset; uses FFT and DWT features on 4 temporal channels at 250 Hz
- **Notes**: Review supplement 6 classes task based on the evidence.

## Data Quality Notes

- Annotations are at the channel level; aggregate to recording level or use channel-specific labels depending on the task.
- Variable channel count and sampling rate; normalize before cross-recording analysis.
- Sex is not reliably available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
