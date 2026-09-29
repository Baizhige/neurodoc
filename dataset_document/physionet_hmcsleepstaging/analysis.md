# HMC Sleep Staging Database

**Dataset**: `physionet_hmcsleepstaging` | **Year**: 2021-2022 | **URL**: https://physionet.org/content/hmc-sleep-staging/1.1/
**Category**: Biological State | **Subjects**: 151 | **Files (Completed)**: 151 | **Channels**: 8 | **Sampling Rate**: 256 Hz | **Manual Review**: anonymous for review

## Paradigm

One hundred and fifty-one (151) overnight polysomnographic recordings from the Haaglanden Medisch Centrum (HMC) Sleep Center, Netherlands, were collected and annotated using the AASM (American Academy of Sleep Medicine) scoring rules. EEG was recorded from 4 bipolar derivations (F4-M1, C4-M1, O2-M1, C3-M2), supplemented by chin EMG, two EOG channels (E1-M2, E2-M2), and ECG, all at 256 Hz. Expert sleep technicians scored each 30-second epoch as Wake, N1, N2, N3, or REM. Light-on and light-off events mark the intended sleep period boundaries.

## File Scan Result

> **Kernel SHA256**: `c64f05a92bbd474b29e1b669b21059d23994732634081f3cf43a6f989b7ff3a3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Sleep stage N1` | 8103 | event | raw | AASM NREM Stage N1 sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage N2` | 24969 | event | raw | AASM NREM Stage N2 sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage N3` | 13243 | event | raw | AASM NREM Stage N3 / slow-wave sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage R` | 10974 | event | raw | AASM REM sleep, scored as a 30-second sleep-stage annotation |
| `Sleep stage W` | 12217 | event | raw | Wake, scored as a 30-second sleep-stage annotation |


> The source scoring files also include `Lights off` and `Lights on` markers, but they are not listed in the current scanned Event Structure. Sleep-stage annotations use 30-second epochs according to AASM scoring.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | [To Agent: Dataset-level aggregate age is 53.9 ± 15.4 years.] |
| `sex` | missing | [To Agent: Dataset-level aggregate sex distribution is 85 M / 66 F.] |
| `device` | missing | [To Agent: Dataset documentation states recordings used SOMNOscreen PSG, PSG+, and EEG 10-20 recorders from SOMNOmedics, Germany, with AgAgCl electrodes.] |


## Tasks

### Classical Task 1: 5-Class Sleep Stage Classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | NREM Stage 1 |
  | `Sleep stage N2` | 2 | NREM Stage 2 |
  | `Sleep stage N3` | 3 | NREM Stage 3 / Slow-wave sleep |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.1109/embc58623.2025.11252818 — 5-class sleep stage classification (W/N1/N2/N3/R) using C4/M1 EEG channel with non-overlapping 30-second epochs, tmin=0s, tmax=30s; explicitly uses HMC dataset
  - 10.3390/s23052458 — 5-class sleep staging (Wake/N1/N2/N3/REM) using ECG from HMC database with 30-s epochs; confirms dataset and 5-class structure (uses 22.5-s overlap for ECG-specific augmentation)
  - 10.1371/journal.pone.0256111 — CNN and CNN-LSTM models for 5-class sleep stage classification (Wake/N1/N2/N3/REM) using 30-second PSG epochs from HMC dataset
- **Notes**: Primary AASM sleep staging task. Exclude 'Lights off' and 'Lights on' admin events from target_events. Implement annotation string cleaning to strip trailing commas before event matching. Consider optional interval restriction to lights-off-lights-on bounds to exclude wake periods far from sleep onset. Class imbalance expected (N1 rare). ECG channel present but should be excluded from EEG feature extraction.

### Classical Task 2: Wake vs. Sleep Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | Sleep (any stage) |
  | `Sleep stage N2` | 1 | Sleep (any stage) |
  | `Sleep stage N3` | 1 | Sleep (any stage) |
  | `Sleep stage R` | 1 | Sleep (any stage) |
- **Evidence**:
  - 10.1109/embc58623.2025.11252818 — Binary collapse of 5-class task is standard derived analysis; same epoch parameters apply
  - 10.1371/journal.pone.0256111 — Binary sleep/wake discrimination is common simplification of the same 5-class HMC staging paradigm
- **Notes**: Binary remapping of Classical Task 1. Same epoching parameters; labels collapsed W→0, all sleep stages→1. Same preprocessing considerations apply (exclude admin events, comma cleaning, lights-off/on interval restriction).

### Potential Task 1: Sliding-Window Sleep Staging with Overlap (ECG-based Augmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 22.5, target_events = [`Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`, `Sleep stage W`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | NREM Stage 1 |
  | `Sleep stage N2` | 2 | NREM Stage 2 |
  | `Sleep stage N3` | 3 | NREM Stage 3 / Slow-wave sleep |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.3390/s23052458 — ECG-based sleep staging with 75% overlap (22.5s) for data augmentation; deviates from standard AASM non-overlapping protocol. ECG-specific, not EEG-primary.
- **Notes**: Secondary augmentation configuration derived from one paper. 22.5-s overlap creates 4× epoch count increase. Originally developed for ECG signal analysis; applicability to pure EEG staging is experimental. Not standard clinical practice. Same target_events and label mapping as Classical Task 1.

## Data Quality Notes

- AASM scoring (N1/N2/N3/REM/W) as opposed to R&K (S1/S2/S3/S4/REM/W) used in older datasets; not directly comparable.
- ECG channel present; exclude from EEG features.
- Aggregated demographics: 85 Male / 66 Female, Mean Age 53.9 ± 15.4. Individual subject-to-demographic mapping is not in public metadata due to strict EDF de-identification (Header: 'X X X').
- N1 is relatively rare; class imbalance between stages is expected.
- Five annotations carry a trailing comma (`Sleep stage W,`); strip commas from annotation strings before processing.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
