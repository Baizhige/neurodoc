# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-1998/2001-2003 | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: 6441 | **Files (Completed)**: 5786 | **Channels**: 14-16 | **Sampling Rate**: 125
**Channels**: 14 | **Sampling Rate**: 125 Hz (EEG/EMG/ECG primary), 50 Hz (EOG), 10 Hz (respiratory), 1 Hz (SpO2/HR); exported EDF channels are resampled to 125 Hz
**Manual Review**: Jiping Cui

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort study investigating the cardiovascular and other consequences of sleep-disordered breathing. Adults aged 40 years and older underwent unattended overnight home polysomnography (PSG), acquired by trained and certified technicians. SHHS-1 enrolled 6,441 participants between 1995 and 1998, and a second PSG (SHHS-2) was obtained in 3,295 participants during 2001-2003. The PSG data include full-night EEG, EOG, EMG, ECG, respiratory, oximetry, body position, and light signals, with expert sleep-stage scoring in 30-second epochs and additional arousal/respiratory event annotations.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Stages\` | Stages | event | event | raw |
| `Arousals\` | Arousals | event | event | raw |
| `Respiratory\` | Respiratory | event | event | raw |


> SHHS provides both Profusion XML and NSRR-translated XML annotation files. Stage annotations in XML may appear as merged intervals spanning multiple 30 s epochs rather than one event per epoch. Historical NSRR XML conversion fixes affected staging duration handling and inclusion of the last staging period, so derived counts may differ slightly across parsers or releases.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Need Update. |
| `subject_sex` | missing | Need Update. |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Wake`, `Stage 1 sleep`, `Stage 2 sleep`, `Stage 3 sleep`, `REM sleep`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Wake` | 0` | 0 |
  | `Stage 1 sleep` | 1` | 1 |
  | `Stage 2 sleep` | 2` | 2 |
  | `Stage 3 sleep` | 3, Stage 4 sleep | 4` |
  | `REM sleep` | 5` | 5 |
- **Evidence**:
  - DOI: 10.5665/sleep.5774 — NSRR paper states each study record minimally includes scored annotation files, raw physiological signals, and summary sleep results.
- **Kernel Notes**: 

### Classical Task 2: Sleep Spindle Density Regression in N2 Sleep
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2 sleep`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stage 2 sleep` | 2 epochs` | continuous |
- **Evidence**:
  - DOI: 10.1038/ncomms15930 — Large-scale NSRR spindle study using SHHS and other cohorts; spindle analyses were performed on N2 epochs after excluding epochs with overlapping arousals, movements, or artifacts.
- **Kernel Notes**: 

### Potential Task 1: Sleep vs Wake Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Wake`, `Stage 1 sleep`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Wake` | 0` | 0 |
  | `Stage 1 sleep` | 1, Stage 2 sleep | 2, Stage 3 sleep |
- **Evidence**:
  - DOI: **Kernel Notes**: This is a coarse — grained reduction of the native sleep-stage annotations and is suitable as a baseline task.
- **Kernel Notes**: 

### Potential Task 2: Arousal Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 5.0 s (event-centered) s, target_events = [`Arousals`, `Background non-arousal windows`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Arousals` | Arousals` | 1 |
  | `Background non-arousal windows` | 0 | Non-arousal |
- **Evidence**:
  - DOI: **Kernel Notes**: The positive class is native, but the negative class is sampling — defined rather than directly annotated. Negative windows should be sampled carefully, ideally excluding overlap with respiratory events, stage-transition boundaries, and obvious artifacts.
- **Kernel Notes**: 

### Potential Task 3: Respiratory Event Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -10.0 s, tmax = 10.0 s, target_events = [`Respiratory`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Respiratory` | Respiratory` | 1 |
- **Evidence**:
  - DOI: **Kernel Notes**: This is best treated as a coarse binary respiratory — event task unless event subtypes are explicitly parsed from `EventConcept`. As with arousal detection, negative windows are sampling-defined rather than directly annotated.
- **Kernel Notes**: 

## Data Quality Notes

- `125 Hz` is a representative rate for primary EEG/EMG channels, not a uniform sampling rate for the full dataset.
- Actual sampling rates vary by channel and SHHS hardware version; always read per-channel frequencies from EDF headers.
- SHHS-2 includes multiple hardware configurations (for example v3/v4) with different EEG, EOG, ECG, and respiratory rates.
- Channel names may vary across files, especially for airflow channels (for example `NEW AIR`, `AIRFLOW`, `AUX`); alias-robust matching is recommended.
- NSRR XML annotations have undergone historical conversion fixes, so small differences in event counts or durations may occur across derived summaries.
- Sleep staging tasks are class-imbalanced, with N2 dominant and Stage 4 rare.
- Recordings were acquired using unattended home PSG and may contain more motion or environmental artifacts than in-lab studies.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
