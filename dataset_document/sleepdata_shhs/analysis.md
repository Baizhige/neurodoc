# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-2003 | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: ~5804 | **Files (Completed)**: 8444 | **Channels**: 14 | **Sampling Rate**: 1-256 Hz | **Manual Review**: Jiping Cui

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort investigating cardiovascular and other outcomes of sleep-disordered breathing. Participants aged 40+ underwent unattended overnight home polysomnography (PSG), collected by certified technicians. SHHS-1 enrolled 6,441 participants from major epidemiological cohorts, and 3,295 participants completed a second PSG approximately 5 years later (SHHS-2). The dataset includes full-night EEG, EOG, EMG, ECG, respiratory, and oximetry signals with expert sleep-stage annotation in 30-second epochs.

## File Scan Result

> **Kernel SHA256**: `9b2c11591e4e2ca376b0ad5925385f0cbbe420994b5669e33c9116041ac1d96e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `ASDA arousal&#124;Arousal (ASDA)` | 3429 | event | raw | ASDA-scored arousal annotation |
| `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)` | 980 | event | raw | Chin-EMG-related arousal annotation |
| `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)` | 1 | event | raw | Chin-EMG-related arousal annotation; spelling variant |
| `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)` | 111 | event | raw | Respiratory-effort-related arousal annotation |
| `Arousal&#124;Arousal ()` | 1072561 | event | raw | Generic arousal annotation |
| `Arousal&#124;Arousal (STANDARD)` | 12345 | event | raw | Standard arousal annotation |
| `Arousal&#124;Arousal (Standard)` | 1103 | event | raw | Standard arousal annotation; spelling variant |
| `Central apnea&#124;Central Apnea` | 38217 | event | raw | Central apnea respiratory event |
| `External arousal&#124;Arousal (External Arousal)` | 120 | event | raw | Arousal attributed to external disturbance |
| `Hypopnea&#124;Hypopnea` | 1588062 | event | raw | Hypopnea respiratory event |
| `Mixed apnea&#124;Mixed Apnea` | 530 | event | raw | Mixed apnea respiratory event |
| `Movement&#124;6` | 2 | admin | raw | Movement-time / non-scorable sleep-stage marker |
| `Obstructive apnea&#124;Obstructive Apnea` | 238656 | event | raw | Obstructive apnea respiratory event |
| `Periodic breathing&#124;Periodic Breathing` | 1 | event | raw | Periodic breathing interval |
| `REM sleep&#124;5` | 77963 | event | raw | REM sleep stage |
| `Recording Start Time` | 8444 | admin | raw | Recording start boundary marker |
| `Respiratory artifact&#124;Respiratory artifact` | 7 | admin | raw | Respiratory signal artifact marker |
| `SpO2 artifact&#124;SpO2 artifact` | 286898 | admin | raw | Pulse-oximetry artifact marker |
| `SpO2 desaturation&#124;SpO2 desaturation` | 1151606 | event | raw | Oxygen desaturation event |
| `Stage 1 sleep&#124;1` | 159595 | event | raw | NREM/R&K stage 1 sleep |
| `Stage 2 sleep&#124;2` | 391562 | event | raw | NREM/R&K stage 2 sleep |
| `Stage 3 sleep&#124;3` | 229582 | event | raw | NREM/R&K stage 3 sleep |
| `Stage 4 sleep&#124;4` | 22813 | event | raw | NREM/R&K stage 4 sleep |
| `Unscored&#124;9` | 198 | admin | raw | Unscored interval; exclude from sleep-stage labels |
| `Unsure&#124;Unsure` | 1219 | admin | raw | Uncertain annotation; exclude from supervised labels |
| `Wake&#124;0` | 260624 | event | raw | Wakefulness stage |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ABDO RES` | native (raw misc in EEG file) | raw | Abdominal respiratory effort belt signal |
| `AIRFLOW` | native (raw misc in EEG file) | raw | Thermistor airflow signal; SHHS1/SHHS2 alias |
| `H.R.` | native (raw misc in EEG file) | raw | Heart rate derived from ECG/oximetry; SHHS1 label |
| `LIGHT` | native (raw misc in EEG file) | raw | Ambient light on/off sensor |
| `NEW AIR` | native (raw misc in EEG file) | raw | Alternate thermistor airflow channel used in SHHS1 |
| `OX stat` | native (raw misc in EEG file) | raw | Oximetry status channel |
| `POSITION` | native (raw misc in EEG file) | raw | Body position sensor |
| `SaO2` | native (raw misc in EEG file) | raw | Pulse oximetry oxygen saturation |
| `THOR RES` | native (raw misc in EEG file) | raw | Thoracic respiratory effort belt signal |
| `spindle_density` | derived by kernel from EEG | super | Sleep spindle count per minute computed within N2 epochs |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (8444/8571) | Available for 8444/8571 scanned records |
| `sex` | partial (8444/8571) | Available for 8444/8571 scanned records |
| `device` | complete | Compumedics P-Series Sleep Monitoring System; SHHS2 used P-series v3/v4 variants |


## Tasks

### Classical Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`REM sleep&#124;5`, `Stage 1 sleep&#124;1`, `Stage 2 sleep&#124;2`, `Stage 3 sleep&#124;3`, `Stage 4 sleep&#124;4`, `Wake&#124;0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Wake&#124;0` | 0 | Wake |
  | `Stage 1 sleep&#124;1` | 1 | N1 |
  | `Stage 2 sleep&#124;2` | 2 | N2 |
  | `Stage 3 sleep&#124;3` | 3 | N3/SWS |
  | `Stage 4 sleep&#124;4` | 3 | N3/SWS |
  | `REM sleep&#124;5` | 4 | REM |
- **Evidence**:
  - 10.5665/sleep.5774 — National Sleep Research Resource provides SHHS PSG data with expert sleep-stage annotations in 30-second epochs
- **Notes**: Stage 4 is rare; merge Stage 3 and Stage 4 into N3/SWS class for robust modeling. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Sleep Spindle Density Regression in N2 Sleep
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2 sleep&#124;2`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `spindle_density` | derived from N2 EEG epochs; y is spindle count per minute |
- **Evidence**:
  - 10.1038/ncomms15930 — Characterizes sleep spindles in 11,630 individuals from NSRR including SHHS (N=5,793), analyzing spindle density, amplitude, duration and frequency during N2 sleep as heritable quantitative traits
- **Notes**: Derived from raw EEG signal in N2 (`Stage 2 sleep&#124;2`) epochs by wavelet band-pass filtering (FC=8-18 Hz) and spindle detection (0.3-3.0 s duration windows). Kernel step: Apply Morlet wavelet transform centered at 13.5 Hz, detect spindle events via amplitude thresholding, compute density = spindle count / epoch duration in minutes. Requires EEG signal processing; spindle density is primary target, with amplitude, duration, and frequency as optional additional regression targets.

### Potential Task 1: Sleep vs Wake Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`REM sleep&#124;5`, `Stage 1 sleep&#124;1`, `Stage 2 sleep&#124;2`, `Stage 3 sleep&#124;3`, `Stage 4 sleep&#124;4`, `Wake&#124;0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Wake&#124;0` | 0 | Awake |
  | `Stage 1 sleep&#124;1` | 1 | Asleep |
  | `Stage 2 sleep&#124;2` | 1 | Asleep |
  | `Stage 3 sleep&#124;3` | 1 | Asleep |
  | `Stage 4 sleep&#124;4` | 1 | Asleep |
  | `REM sleep&#124;5` | 1 | Asleep |
- **Evidence**:

- **Notes**: Useful baseline task when class granularity is reduced.

### Potential Task 2: Arousal Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 5.0 s, target_events = [`ASDA arousal&#124;Arousal (ASDA)`, `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)`, `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)`, `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)`, `Arousal&#124;Arousal ()`, `Arousal&#124;Arousal (STANDARD)`, `Arousal&#124;Arousal (Standard)`, `External arousal&#124;Arousal (External Arousal)`, `Stage 2 sleep&#124;2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stage 2 sleep&#124;2` | 0 | Non-arousal sleep-stage anchor |
  | `Arousal&#124;Arousal ()` | 1 | Generic cortical arousal |
  | `ASDA arousal&#124;Arousal (ASDA)` | 1 | ASDA-scored arousal |
  | `Arousal&#124;Arousal (STANDARD)` | 1 | Standard arousal |
  | `Arousal&#124;Arousal (Standard)` | 1 | Standard arousal spelling variant |
  | `Arousal resulting from Chin EMG&#124;Arousal (CHESHIRE)` | 1 | Chin-EMG-related arousal |
  | `Arousal resulting from Chin EMG&#124;Arousal (Cheshire)` | 1 | Chin-EMG-related arousal spelling variant |
  | `Arousal resulting from respiratory effort&#124;Arousal (ARO RES)` | 1 | Respiratory-effort-related arousal |
  | `External arousal&#124;Arousal (External Arousal)` | 1 | External arousal |
- **Evidence**:

- **Notes**: Negative sampling strategy should exclude windows overlapping any arousal annotation to avoid label leakage.

### Potential Task 3: Respiratory Event Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Central apnea&#124;Central Apnea`, `Hypopnea&#124;Hypopnea`, `Mixed apnea&#124;Mixed Apnea`, `Obstructive apnea&#124;Obstructive Apnea`, `Periodic breathing&#124;Periodic Breathing`, `Stage 2 sleep&#124;2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stage 2 sleep&#124;2` | 0 | Non-respiratory-event sleep-stage anchor |
  | `Hypopnea&#124;Hypopnea` | 1 | Hypopnea respiratory event |
  | `Central apnea&#124;Central Apnea` | 1 | Central apnea respiratory event |
  | `Obstructive apnea&#124;Obstructive Apnea` | 1 | Obstructive apnea respiratory event |
  | `Mixed apnea&#124;Mixed Apnea` | 1 | Mixed apnea respiratory event |
  | `Periodic breathing&#124;Periodic Breathing` | 1 | Periodic breathing interval |
- **Evidence**:

- **Notes**: Respiratory subtype definitions should be verified per XML file and NSRR conversion version.

## Data Quality Notes

- EDF channels retain mixed native sampling rates; loaders must inspect per-channel EDF headers rather than assuming a single sampling rate.
- Channel naming may vary across files (`NEW AIR` vs `AIRFLOW`), so channel selection should be robust to aliases.
- Annotation counts can differ between XML-derived event totals and summary CSV fields due to historical software conversion effects.
- Desaturation labels may be missing or partially inconsistent in some files; consider deriving desaturation from raw `SaO2` traces when needed.
- Class imbalance is expected (N2 dominant; Wake/N1 relatively sparse; Stage 4 rare).
- Recordings are unattended home PSG and therefore may have higher motion/environmental artifact than in-lab PSG.
- Hardware/Sampling Shift between cohorts: SHHS-1 (1995-1998) uses EEG/EMG/ECG 125 Hz, EOG 50 Hz, respiratory 10 Hz, and SpO2/HR/position/light 1 Hz; SHHS-2 includes v3/v4 variants with ECG 250/256 Hz, EEG/EMG 125/128 Hz, EOG 50/64 Hz, respiratory 10/8 Hz, and SpO2/HR 1 Hz. DataLoader must check signal headers dynamically rather than hardcoding frequencies.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
