# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-2003 | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: 6441 | **Files (Completed)**: 5786 | **Manual Review**:
**Channels**: 14 | **Sampling Rate**: 125 Hz (EEG/EMG/ECG primary), 50 Hz (EOG), 10 Hz (respiratory), 1 Hz (SpO2/HR); exported EDF channels are resampled to 125 Hz

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort investigating cardiovascular and other outcomes of sleep-disordered breathing. Participants aged 40+ underwent unattended overnight home polysomnography (PSG), collected by certified technicians. SHHS-1 enrolled 6,441 participants from major epidemiological cohorts, and 3,295 participants completed a second PSG approximately 5 years later (SHHS-2). The dataset includes full-night EEG, EOG, EMG, ECG, respiratory, and oximetry signals with expert sleep-stage annotation in 30-second epochs.

## File Scan Result

> **Kernel SHA256**: `c07e572c2097434833f230846d58e8f32f84e4ba8d6e0f09d9f4c921560f6771`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `ASDA arousal\|Arousal (ASDA)` | 3429 | event | raw |  |
| `Arousal resulting from Chin EMG\|Arousal (CHESHIRE)` | 980 | event | raw |  |
| `Arousal resulting from Chin EMG\|Arousal (Cheshire)` | 1 | event | raw |  |
| `Arousal resulting from respiratory effort\|Arousal (ARO RES)` | 111 | event | raw |  |
| `Arousal\|Arousal ()` | 1072561 | event | raw |  |
| `Arousal\|Arousal (STANDARD)` | 12345 | event | raw |  |
| `Arousal\|Arousal (Standard)` | 1103 | event | raw |  |
| `Central apnea\|Central Apnea` | 38217 | event | raw |  |
| `External arousal\|Arousal (External Arousal)` | 120 | event | raw |  |
| `Hypopnea\|Hypopnea` | 1588062 | event | raw |  |
| `Mixed apnea\|Mixed Apnea` | 530 | event | raw |  |
| `Movement\|6` | 2 | event | raw |  |
| `Obstructive apnea\|Obstructive Apnea` | 238656 | event | raw |  |
| `Periodic breathing\|Periodic Breathing` | 1 | event | raw |  |
| `REM sleep\|5` | 77963 | event | raw |  |
| `Recording Start Time` | 8444 | event | raw |  |
| `Respiratory artifact\|Respiratory artifact` | 7 | event | raw |  |
| `SpO2 artifact\|SpO2 artifact` | 286898 | event | raw |  |
| `SpO2 desaturation\|SpO2 desaturation` | 1151606 | event | raw |  |
| `Stage 1 sleep\|1` | 159595 | event | raw |  |
| `Stage 2 sleep\|2` | 391562 | event | raw |  |
| `Stage 3 sleep\|3` | 229582 | event | raw |  |
| `Stage 4 sleep\|4` | 22813 | event | raw |  |
| `Unscored\|9` | 198 | event | raw |  |
| `Unsure\|Unsure` | 1219 | event | raw |  |
| `Wake\|0` | 260624 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ABDO RES` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `AIRFLOW` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `H.R.` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `LIGHT` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `NEW AIR` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `OX stat` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `POSITION` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `SaO2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `THOR RES` | native (raw misc in EEG file) | raw | Verify channel role and unit |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | partial (8444/8571) | N/A |
| `subject_sex` | partial (8444/8571) | N/A |
| `device` | complete | N/A |
| `amplifier` | complete | e.g. Compumedics |
| `cap` | complete | e.g. minimal PSG montage (C3/C4, A1/A2 referential) |
| `bmi` | partial (8377/8571) | e.g. 21.777553339, 32.950680272, 24.114149822 |
| `height` | partial (5751/8571) | e.g. 178, 168, 145 |
| `race` | partial (8444/8571) | e.g. 1, 2, 3 |
| `weight` | partial (5680/8571) | e.g. 65, 93, 51 |

## Tasks

### Classical Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2|2`, `Stage 3|3`, `Stage 1|1`, `REM|5`, `Wake|0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Wake\|0` | 0 | Wake |
  | `Stage 1\|1` | 1 | N1 |
  | `Stage 2\|2` | 2 | N2 |
  | `Stage 3\|3` or `Stage 4\|4` | 3 | N3/SWS |
  | `REM\|5` | 4 | REM |
- **Evidence**:
  - DOI: `10.5665/sleep.5774` — National Sleep Research Resource provides SHHS PSG data with expert sleep-stage annotations in 30-second epochs
- **Kernel Notes**: Stage 4 is rare; merge Stage 3 and Stage 4 into N3/SWS class for robust modeling. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Sleep Spindle Density Regression in N2 Sleep
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2|2`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stage 2|2` epochs | continuous | Spindle density (spindles per minute) computed from N2 sleep EEG |
- **Super Meta Notes**: Derived from raw EEG signal in N2 (`Stage 2|2`) epochs by wavelet band-pass filtering (FC=8-18 Hz) and spindle detection (0.3-3.0 s duration windows). Kernel step: Apply Morlet wavelet transform centered at 13.5 Hz, detect spindle events via amplitude thresholding, compute density = (spindle count / epoch duration in minutes).
- **Evidence**:
  - DOI: `10.1038/ncomms15930` — Characterizes sleep spindles in 11,630 individuals from NSRR including SHHS (N=5,793), analyzing spindle density, amplitude, duration and frequency during N2 sleep as heritable quantitative traits
- **Kernel Notes**: Requires EEG signal processing; compute spindle properties per N2 epoch. Spindle density is primary target; amplitude, duration, frequency are optional additional regression targets.

### Potential Task 2: Sleep vs Wake Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Useful baseline task when class granularity is reduced.

| Event | y | Meaning |
|-------|---|---------|
| `Wake\|0` | 0 | Awake |
| Any sleep stage (`1/2/3/4/5`) | 1 | Asleep |

### Potential Task 3: Arousal Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` (or long-event segmentation if arousal duration labels are available)
- **Epoch Parameters**: tmin = -5.0 s, tmax = 5.0 s (event-centered), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Negative sampling strategy should be explicitly controlled to avoid label leakage.

| Event | y | Meaning |
|-------|---|---------|
| `Arousals|Arousals` | 1 | Cortical arousal |
| Background non-arousal segments | 0 | Non-arousal |

### Potential Task 4: Respiratory Event Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5` (depends on event duration granularity)
- **Epoch Parameters**: task-dependent (for example, 10-30 s windows), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Respiratory subtype definitions should be verified per XML file and NSRR conversion version.

| Event | y | Meaning |
|-------|---|---------|
| `Respiratory|Respiratory` (event windows) | 1 | Respiratory event |
| Non-event windows | 0 | Normal breathing/no event |

## Data Quality Notes

- Mixed-rate channels are exported at 125 Hz in EDF; originally low-rate channels (EOG/respiratory/SpO2/HR) are upsampled during export.
- Channel naming may vary across files (`NEW AIR` vs `AIRFLOW`), so channel selection should be robust to aliases.
- Annotation counts can differ between XML-derived event totals and summary CSV fields due to historical software conversion effects.
- Desaturation labels may be missing or partially inconsistent in some files; consider deriving desaturation from raw `SaO2` traces when needed.
- Class imbalance is expected (N2 dominant; Wake/N1 relatively sparse; Stage 4 rare).
- Recordings are unattended home PSG and therefore may have higher motion/environmental artifact than in-lab PSG.
- Hardware/Sampling Shift between cohorts: SHHS-1 (1995-1998) and SHHS-2 (2001-2003) use different native sampling rates — SHHS-2 ECG is 250 Hz (vs 125 Hz), EOG is 64 Hz (vs 50 Hz), Respiratory is 8 Hz (vs 10 Hz). DataLoader must check signal headers dynamically rather than hardcoding frequencies.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
