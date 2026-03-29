# sleepdata_shhs

**Dataset**: `sleepdata_shhs` | **Year**: 1995-2003 (SHHS-1: 1995-1998; SHHS-2: 2001-2003) | **URL**: https://sleepdata.org/datasets/shhs
**Category**: Biological State | **Subjects**: 6,441 (SHHS-1); 3,295 follow-up (SHHS-2) | **Files (Completed)**: 5,793 EDF (SHHS-1) + 2,651 EDF (SHHS-2)
**Channels**: ~14 (per EDF) | **Sampling Rate**: 
- **SHHS-1**: 125 Hz (EEG/EMG/ECG), 50 Hz (EOG), 10 Hz (respiratory), 1 Hz (SpO2/HR)
- **SHHS-2**: 125 Hz (EEG/EMG), 250 Hz (ECG), 64 Hz (EOG), 8 Hz (respiratory), 1 Hz (SpO2/HR)
*(Note: exported NSRR EDF channels are often upsampled to a uniform 125 Hz, but native resolutions differ)*

**Manual Review**: Jiping Cui

## Paradigm

The Sleep Heart Health Study (SHHS) is a multi-center NIH/NHLBI cohort investigating cardiovascular and other outcomes of sleep-disordered breathing. Participants aged 40+ underwent unattended overnight home polysomnography (PSG), collected by certified technicians. SHHS-1 enrolled 6,441 participants from major epidemiological cohorts, and 3,295 participants completed a second PSG approximately 5 years later (SHHS-2). The dataset includes full-night EEG, EOG, EMG, ECG, respiratory, and oximetry signals with expert sleep-stage annotation in 30-second epochs.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
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
  - DOI: `10.5665/sleep.5774` — (Dataset & Labeling Baseline) The official NSRR resource paper validating the provision of SHHS PSG data with standardized expert sleep-stage annotations in 30-second epochs, enabling 5-class sleep staging benchmarks.
- **Kernel Notes**: Stage 4 is rare; merge Stage 3 and Stage 4 into N3/SWS class for robust modeling. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Sleep Spindle Count Regression in N2 Sleep Epochs
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stage 2|2`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stage 2|2` epochs | integer | Absolute count of distinct sleep spindles detected within the 30-second N2 epoch |
- **Super Meta Notes**: Derived from raw EEG signal in N2 epochs using automated detection algorithms (e.g., Luna). Kernel step: Apply Morlet wavelet transform (typically focusing on 11-15 Hz fast spindle band), detect events via amplitude thresholding (0.5-3.0 s duration windows), and aggregate the discrete integer count of spindles per 30-second epoch.
- **Evidence**:
  - DOI: `10.1038/ncomms15930` — Purcell et al. characterizes sleep spindles in 11,630 individuals from NSRR (including SHHS). While the paper aggregates macro-level spindle density for GWAS, the core methodology relies on precise micro-level automated spindle detection algorithms on N2 EEG, justifying epoch-level spindle quantification.
- **Kernel Notes**: Avoid confusing macro-level "density" (subject-level trait) with micro-level "count" (epoch-level trait). This benchmark task predicts the absolute spindle count per 30s epoch. Advanced regression variants can target mean amplitude or peak frequency within the epoch.

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
- Hardware/Sampling Shift: SHHS-2 employs different native sampling rates compared to SHHS-1 (e.g., ECG is 250Hz vs 125Hz; EOG is 64Hz vs 50Hz; Respiratory is 8Hz vs 10Hz). The DataLoader must dynamically check signal headers rather than hardcoding frequencies.

## References

- Quan, S.F. et al. (1997). The Sleep Heart Health Study: design, rationale, and methods. *Sleep*, 20(12), 1077-1085.
- Redline, S. et al. (1998). Methods for obtaining and analyzing unattended polysomnography data for a multicenter study. *Sleep*, 21(7), 759-767.
- Dean, D.A. et al. (2016). Scaling Up Scientific Discovery in Sleep Medicine: The National Sleep Research Resource. *Sleep*, 39(5), 1151-1164. DOI: https://doi.org/10.5665/sleep.5774
- Zhang, Y. et al. (2024). The National Sleep Research Resource: making data findable, accessible, interoperable, reusable and promoting sleep science. *Sleep*, 47(1), zsae088. DOI: https://doi.org/10.1093/sleep/zsae088
- NSRR SHHS dataset page: https://sleepdata.org/datasets/shhs
