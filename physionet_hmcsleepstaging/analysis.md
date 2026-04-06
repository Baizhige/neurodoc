# HMC Sleep Staging Database

**Dataset**: `physionet_hmcsleepstaging` | **Year**: 2022 | **URL**: https://physionet.org/content/hmc-sleep-staging/1.1/
**Category**: Biological State | **Subjects**: 151 | **Files (Completed)**: 151 | **Channels**: 8 | **Sampling Rate**: 256 Hz
**Manual Review**: Jiping Cui

## Paradigm

One hundred and fifty-one (151) overnight polysomnographic recordings from the Haaglanden Medisch Centrum (HMC) Sleep Center, Netherlands, were collected and annotated using the AASM (American Academy of Sleep Medicine) scoring rules. EEG was recorded from 4 bipolar derivations (F4-M1, C4-M1, O2-M1, C3-M2), supplemented by chin EMG, two EOG channels (E1-M2, E2-M2), and ECG, all at 256 Hz. Expert sleep technicians scored each 30-second epoch as Wake, N1, N2, N3, or REM. Light-on and light-off events mark the intended sleep period boundaries.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage W` | 23681 | event | raw | Wake (30-second epoch) |
| `Sleep stage W,` | 5 | event | raw | Wake with trailing comma (dirty data — strip before use) |
| `Sleep stage N1` | 15548 | event | raw | NREM Stage 1 (AASM) |
| `Sleep stage N2` | 50083 | event | raw | NREM Stage 2 (AASM) |
| `Sleep stage N3` | 26671 | event | raw | NREM Stage 3 - slow-wave sleep (AASM) |
| `Sleep stage R` | 21255 | event | raw | REM sleep (AASM) |
| `Lights off` | 151 | admin | raw | Start of intended sleep period |
| `Lights on` | 151 | admin | raw | End of intended sleep period |

> Counts are exact totals across all 151 recordings. Each sleep stage annotation spans exactly 30 seconds.
> **Manual Review Note**: Subject count corrected 77→151, event counts updated, REM ID corrected from `Sleep stage R (REM)` to `Sleep stage R`, and `Sleep stage W,` dirty-data entry added — all by human reviewer (Jiping Cui). Kernel should re-verify counts and REM annotation string on next scan.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: 5-Class Sleep Stage Classification (AASM)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`Sleep stage W`, `Sleep stage N1`, `Sleep stage N2`, `Sleep stage N3`, `Sleep stage R`]
- **Label Route**: `event`
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
  - DOI: 10.3390/s23052458 — Uses ECG data from HMC sleep staging database for 5-class sleep staging (Wake/N1/N2/N3/REM) using 30-s epochs with 22.5-s overlap
  - DOI: 10.1371/journal.pone.0256111 — Develops CNN and CNN-LSTM models to automatically classify sleep stages into 5 classes (Wake/N1/N2/N3/REM) using 30-second PSG epochs from HMC dataset
- **Kernel Notes**: Exclude `Lights off` and `Lights on` admin events. Epoch window must match 30 s exactly. Consider restricting to the lights-off-lights-on interval to exclude periods far from sleep onset. (replaces Potential Task 1 from original analysis.md)

### Potential Task 2: Wake vs. Sleep Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `event`
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
- Aggregated demographics: 85 Male / 66 Female, Mean Age 53.9 ± 15.4. Individual subject-to-demographic mapping is not in public metadata due to strict EDF de-identification (Header: 'X X X').
- N1 is relatively rare; class imbalance between stages is expected.
- Five annotations carry a trailing comma (`Sleep stage W,`); strip commas from annotation strings before processing.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review