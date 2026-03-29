# HMC Sleep Staging Database

**Dataset**: `physionet_hmcsleepstaging` | **Year**: 2022 | **URL**: https://physionet.org/content/hmc-sleep-staging/1.1/
**Category**: Biological State | **Subjects**: 151 | **Files (Completed)**: 151 | **Channels**: 8 | **Sampling Rate**: 256 Hz | **Manual Review**: Jiping Cui

## Paradigm

One hundred and fifty-one (151) overnight polysomnographic recordings from the Haaglanden Medisch Centrum (HMC) Sleep Center, Netherlands, were collected and annotated using the AASM (American Academy of Sleep Medicine) scoring rules. EEG was recorded from 4 bipolar derivations (F4-M1, C4-M1, O2-M1, C3-M2), supplemented by chin EMG, two EOG channels (E1-M2, E2-M2), and ECG, all at 256 Hz. Expert sleep technicians scored each 30-second epoch as Wake, N1, N2, N3, or REM. Light-on and light-off events mark the intended sleep period boundaries.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/hmc-sleep-staging/1.1/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage W` | 23681 | long | raw | Wake (30-second epoch) |
| `Sleep stage W,` | 5 | long | raw | Wake (Dirty data with trailing comma) |
| `Sleep stage N1` | 15548 | long | raw | NREM Stage 1 (AASM) |
| `Sleep stage N2` | 50083 | long | raw | NREM Stage 2 (AASM) |
| `Sleep stage N3` | 26671 | long | raw | NREM Stage 3 - slow-wave sleep (AASM) |
| `Sleep stage R` | 21255 | long | raw | REM sleep (AASM) |
| `Lights off` | 151 | admin | raw | Start of intended sleep period |
| `Lights on` | 151 | admin | raw | End of intended sleep period |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are exact totals across all 151 recordings. Each sleep stage annotation spans exactly 30 seconds.

## Tasks

### Primary Task 1: 5-Class Sleep Stage Classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`Sleep stage W`, `Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | NREM Stage 1 |
  | `Sleep stage N2` | 2 | NREM Stage 2 |
  | `Sleep stage N3` | 3 | NREM Stage 3 / Slow-wave sleep |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - DOI: 10.1109/embc58623.2025.11252818 — Uses HMC sleep dataset extracting C4/M1 EEG data segmented into non-overlapping 30-second epochs for 5-class classification (W/N1/N2/N3/R)
  - DOI: https://doi.org/10.1371/journal.pone.0256111 — Develops CNN and CNN-LSTM models to automatically classify sleep stages into 5 classes (Wake/N1/N2/N3/REM) using 30-second PSG epochs from HMC dataset
- **Kernel Notes**: Exclude `Lights off` and `Lights on` admin events. Epoch window must match 30 s exactly. Consider restricting to the lights-off-lights-on interval to exclude periods far from sleep onset. **Crucially, raw annotation strings must be stripped of trailing commas and whitespace (e.g., `event_str.strip(',')`) to handle the 5 anomalous `Sleep stage W,` markers.**

### Normal Task 2: Wake vs. Sleep Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|-|
| `Sleep stage W` | 0 | Wake |
| `Sleep stage N1` | 1 | Any sleep stage |
| `Sleep stage N2` | 1 | Any sleep stage |
| `Sleep stage N3` | 1 | Any sleep stage |
| `Sleep stage R` | 1 | Any sleep stage |


## Data Quality Notes

- AASM scoring (N1/N2/N3/REM/W) as opposed to R&K (S1/S2/S3/S4/REM/W) used in older datasets; not directly comparable.
- ECG channel present; exclude from EEG features.
- Aggregated demographic information is available for the cohort (85 Male / 66 Female, Mean Age 53.9 ± 15.4), but strict EDF de-identification (Header: 'X X X') means individual subject-to-demographic mapping is not provided in the public metadata.
- N1 is relatively rare; class imbalance between stages is expected.

## References

- **Reference**: Alvarez-Estevez D, Rijsman RM (2022). HMC Sleep Staging Database. PhysioNet. https://physionet.org/content/hmc-sleep-staging/1.1/
