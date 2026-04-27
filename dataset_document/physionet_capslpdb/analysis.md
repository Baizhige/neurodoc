# CAP Sleep Database

**Dataset**: `physionet_capslpdb` | **Year**: 2012 | **URL**: https://physionet.org/content/capslpdb/1.0.0/
**Category**: Biological State | **Subjects**: 108 | **Files (Completed)**: 108 | **Channels**: 5-36 | **Sampling Rate**: 100-512 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

The CAP Sleep Database comprises 108 overnight polysomnographic (PSG) recordings collected at the Sleep Disorders Center of the Ospedale Maggiore of Parma, Italy. The cohort includes 16 healthy controls and 92 patients with sleep disorders, including nocturnal frontal lobe epilepsy (NFLE, n=40), REM sleep behavior disorder (RBD, n=22), periodic leg movements (PLM, n=10), insomnia (n=9), narcolepsy (n=5), sleep-disordered breathing (SDB, n=4), and bruxism (n=2). Expert neurologists annotated both sleep macrostructure according to Rechtschaffen & Kales rules and CAP events according to Terzano’s atlas. CAP phase A events are further divided into subtypes A1, A2, and A3, corresponding respectively to predominantly synchronized EEG patterns with low autonomic/somatomotor impact, mixed synchronized–desynchronized patterns with intermediate impact, and predominantly desynchronized patterns with stronger autonomic/somatomotor effects. The recordings include at least three EEG channels, along with EOG, submental EMG, bilateral anterior tibial EMG, respiratory signals, and EKG; some recordings also contain additional bipolar EEG traces.

## File Scan Result

> **Kernel SHA256**: `54f7bb12ca8e1497115f3bfc72b778ac0c2156309ded3fcdfb420ac50661c4e2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `A1` | 26788 | event | raw | CAP phase A1: high-amplitude synchronized EEG |
| `A2` | 10519 | event | raw | CAP phase A2: mixed synchronization EEG |
| `A3` | 14324 | event | raw | CAP phase A3: desynchronized EEG |
| `B` | 51737 | event | raw | Non-CAP EEG period (baseline interval) |
| `SLEEP-MT` | 11 | admin | raw | Movement time boundary marker |
| `SLEEP-REM` | 18935 | event | raw | REM sleep stage epoch marker |
| `SLEEP-S0` | 19495 | event | raw | Wakefulness stage epoch marker |
| `SLEEP-S1` | 4642 | event | raw | NREM Sleep stage 1 epoch marker |
| `SLEEP-S2` | 39192 | event | raw | NREM Sleep stage 2 epoch marker |
| `SLEEP-S3` | 11953 | event | raw | NREM Sleep stage 3 epoch marker |
| `SLEEP-S4` | 13780 | event | raw | NREM Sleep stage 4 epoch marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 1, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `SLEEP-S0` | 0 | Wake (S0) |
  | `SLEEP-S1` | 1 | NREM Stage 1 |
  | `SLEEP-S2` | 2 | NREM Stage 2 |
  | `SLEEP-S3` | 3 | NREM Stage 3 |
  | `SLEEP-S4` | 4 | NREM Stage 4 |
  | `SLEEP-REM` | 5 | REM sleep |
- **Evidence**:
  - 10.13026/C2VC79 — Dataset documentation confirming PSG/EEG sleep scoring with R&K stages
  - 10.1109/tnsre.2019.2934828 — The classification is typically performed on thirty-seconds windows of the electroencephalography (EEG) recording.
- **Notes**: 

### Classical Task 2: CAP A-phase detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 14 s, overlap = 1, target_events = [`A1`, `A2`, `A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `A1` | 0 | CAP A-phase (subtype A1) |
  | `A2` | 1 | CAP A-phase (subtype A2) |
  | `A3` | 2 | CAP A-phase (subtype A3) |
- **Evidence**:
  - 10.1109/tnsre.2019.2934828 — CAP A-phase detection is performed at 1 Hz resolution using feature vectors extracted from short overlapping windows, with an LSTM operating on 14-second temporal contexts centered at each time step.
- **Notes**: 

### Potential Task 1: CAP A-phase subtype classification (4 seconds)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 1, target_events = [`A1`, `A2`, `A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `A1` | 0 | CAP Phase A1 (synchronized EEG) |
  | `A2` | 1 | CAP Phase A2 (mixed pattern) |
  | `A3` | 2 | CAP Phase A3 (desynchronized EEG) |
- **Evidence**:

- **Notes**: 

### Potential Task 2: NREM classification (4-second)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 1.0, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `SLEEP-S0` | 0 | Wake (S0) |
  | `SLEEP-S1` | 1 | NREM Stage 1 |
  | `SLEEP-S2` | 2 | NREM Stage 2 |
  | `SLEEP-S3` | 3 | NREM Stage 3 |
  | `SLEEP-S4` | 4 | NREM Stage 4 |
  | `SLEEP-REM` | 5 | REM sleep |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

- Channel count and sampling rate vary substantially across subjects; normalize before cross-subject analysis.
- Mixed clinical population: NFLE, RBD, PLM, insomnia, narcolepsy, SDB, bruxism, and healthy controls; group labels are encoded in the subject metadata. May be update kernel if more tasks are needed

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
