# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-2003 (SHHS-1: 1995-1998; SHHS-2: 2001-2003) | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: 6,441 (SHHS-1); 3,295 follow-up (SHHS-2) | **Files (Completed)**: 5,786 EDF (SHHS-1) + 532 EDF (SHHS-2)
**Channels**: 14 (per EDF) | **Sampling Rate**: 125 Hz (EEG/EMG/ECG primary), 50 Hz (EOG), 10 Hz (respiratory), 1 Hz (SpO2/HR); exported EDF channels are resampled to 125 Hz

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort investigating cardiovascular and other outcomes of sleep-disordered breathing. Participants aged 40+ underwent unattended overnight home polysomnography (PSG), collected by certified technicians. SHHS-1 enrolled 6,441 participants from major epidemiological cohorts, and 3,295 participants completed a second PSG approximately 5 years later (SHHS-2). The dataset includes full-night EEG, EOG, EMG, ECG, respiratory, and oximetry signals with expert sleep-stage annotation in 30-second epochs.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://sleepdata.org/datasets/shhs

## Event Structure

Annotations are available in both original Profusion XML and NSRR-processed XML (`*-nsrr.xml`). The NSRR XML files contain three high-level `EventType` groups:

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stages\|Stages` | ~100-400 annotations/file | long | raw | Sleep-stage labels in 30 s scoring epochs |
| `Arousals\|Arousals` | variable | short/long | raw | Cortical arousal events |
| `Respiratory\|Respiratory` | variable | short/long | raw | Respiratory events (apnea/hypopnea/desaturation-related) |

### Sleep Stage Labels (inside `EventConcept`)

| Event ID | Count (total) | Type | Meta Level | Meaning |
|--------|-------------|----|----------|-------|
| `Wake\|0` | frequent | long | raw | Wake |
| `Stage 1\|1` | lower frequency | long | raw | NREM Stage 1 (N1) |
| `Stage 2\|2` | high frequency | long | raw | NREM Stage 2 (N2) |
| `Stage 3\|3` | moderate | long | raw | Slow-wave sleep |
| `Stage 4\|4` | rare | long | raw | Slow-wave sleep (legacy R&K stage) |
| `REM\|5` | moderate | long | raw | REM sleep |

> **Event Type Description**:
> - `short`: brief event marker (for event-locked analysis)
> - `long`: sustained-state marker (for long-event epoching, including sleep stages)
> - `rest`: resting-state segment marker when explicitly present
> - `admin`: boundary/system marker, exclude from target labels

## Tasks

### Primary Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2|2`, `Stage 3|3`, `Stage 1|1`, `REM|5`, `Wake|0`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Wake|0` | 0 | Wake |
  | `Stage 1|1` | 1 | N1 |
  | `Stage 2|2` | 2 | N2 |
  | `Stage 3|3` or `Stage 4|4` | 3 | N3/SWS |
  | `REM|5` | 4 | REM |
- **Evidence**:
  - DOI: `10.5665/sleep.5774` — National Sleep Research Resource provides SHHS PSG data with expert sleep-stage annotations in 30-second epochs
- **Kernel Notes**: Stage 4 is rare; merge Stage 3 and Stage 4 into N3/SWS class for robust modeling. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Sleep Spindle Density Regression in N2 Sleep
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2|2`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stage 2|2` epochs | continuous | Spindle density (spindles per minute) computed from N2 sleep EEG |
- **Super Meta Notes**: Derived from raw EEG signal in N2 (`Stage 2|2`) epochs by wavelet band-pass filtering (FC=8-18 Hz) and spindle detection (0.3-3.0 s duration windows). Kernel step: Apply Morlet wavelet transform centered at 13.5 Hz, detect spindle events via amplitude thresholding, compute density = (spindle count / epoch duration in minutes).
- **Evidence**:
  - DOI: `10.1038/ncomms15930` — Characterizes sleep spindles in 11,630 individuals from NSRR including SHHS (N=5,793), analyzing spindle density, amplitude, duration and frequency during N2 sleep as heritable quantitative traits
- **Kernel Notes**: Requires EEG signal processing; compute spindle properties per N2 epoch. Spindle density is primary target; amplitude, duration, frequency are optional additional regression targets.

### Normal Task 2: Sleep vs Wake Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Useful baseline task when class granularity is reduced.

| Event | y | Meaning |
|-------|---|---------|
| `Wake|0` | 0 | Awake |
| Any sleep stage (`1/2/3/4/5`) | 1 | Asleep |

### Normal Task 3: Arousal Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` (or long-event segmentation if arousal duration labels are available)
- **Epoch Parameters**: tmin = -5.0 s, tmax = 5.0 s (event-centered), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Negative sampling strategy should be explicitly controlled to avoid label leakage.

| Event | y | Meaning |
|-------|---|---------|
| `Arousals|Arousals` | 1 | Cortical arousal |
| Background non-arousal segments | 0 | Non-arousal |

### Normal Task 4: Respiratory Event Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5` (depends on event duration granularity)
- **Epoch Parameters**: task-dependent (for example, 10-30 s windows), target_events = see Target Definition
- **Label Route**: `Annotation`
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
- SHHS-2 ECG can differ in effective native sampling relative to SHHS-1; handle ECG separately if exact spectral comparability is required.

