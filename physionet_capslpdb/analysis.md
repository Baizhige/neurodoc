# CAP Sleep Database

**Dataset**: `physionet_capslpdb` | **Year**: 2014 | **URL**: https://physionet.org/content/capslpdb/1.0.0/
**Category**: Biological State | **Subjects**: 108 | **Files (Completed)**: 108 | **Channels**: 5-36 (variable) | **Sampling Rate**: 100-512 Hz (variable)

## Paradigm

One hundred and eight patients from the Sleep Disorders Center, Ospedale Civile di Parma, Italy, underwent overnight polysomnographic (PSG) recording with detailed expert annotations (Terzano et al., 2002). The cohort includes 16 healthy controls and 92 patients with various sleep disorders: nocturnal frontal lobe epilepsy (NFLE, n=40), REM sleep behavior disorder (RBD, n=22), periodic limb movements (PLM, n=10), insomnia (n=9), narcolepsy (n=5), sleep-disordered breathing (SDB, n=4), and bruxism (n=2). Beyond standard sleep staging (Rechtschaffen & Kales), annotations include Cyclic Alternating Pattern (CAP) subtypes: phase A1 (high-amplitude synchronized EEG activity), A2 (mixed), and A3 (desynchronized EEG). Channel count and sampling rate vary across subjects.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `SLEEP-S0` | 19495 | event | raw | Wake stage (S0 = W) |
| `SLEEP-S1` | 4642 | event | raw | NREM Stage 1 - light sleep |
| `SLEEP-S2` | 39192 | event | raw | NREM Stage 2 - sleep spindles/K-complexes |
| `SLEEP-S3` | 11953 | event | raw | NREM Stage 3 - SWS |
| `SLEEP-S4` | 13780 | event | raw | NREM Stage 4 - deep SWS |
| `SLEEP-REM` | 18935 | event | raw | REM sleep |
| `SLEEP-MT` | 11 | admin | raw | Movement time (artifact/transition) |
| `MCAP-A1` | 26788 | event | raw | CAP phase A1 onset (synchronized EEG) |
| `MCAP-A2` | 10519 | event | raw | CAP phase A2 onset (mixed pattern) |
| `MCAP-A3` | 14324 | event | raw | CAP phase A3 onset (desynchronized EEG) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `SLEEP-S0` | 0 | Wake (S0) |
  | `SLEEP-S1` | 1 | NREM Stage 1 |
  | `SLEEP-S2` | 2 | NREM Stage 2 |
  | `SLEEP-S3` | 3 | NREM Stage 3 |
  | `SLEEP-S4` | 4 | NREM Stage 4 |
  | `SLEEP-REM` | 5 | REM sleep |
- **Evidence**:
  - DOI: 10.13026/C2VC79 — Dataset documentation confirming PSG/EEG sleep scoring with R&K stages
- **Kernel Notes**: Exclude `SLEEP-MT` epochs. Uses standard 30-second R&K epoch boundaries; tmax=30.0s matches dataset annotation granularity.

### Classical Task 2: Binary CAP A-phase detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`MCAP-A1`, `MCAP-A2`, `MCAP-A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `MCAP-A1` | 1 | CAP A-phase (subtype A1) |
  | `MCAP-A2` | 1 | CAP A-phase (subtype A2) |
  | `MCAP-A3` | 1 | CAP A-phase (subtype A3) |
- **Evidence**:
  - DOI: 10.1109/tnsre.2019.2934828 — LSTM-based CAP A-phase detection (binary: A-phase vs background), achieving sensitivity 76-78%
- **Kernel Notes**: Combine all CAP A-phase subtypes (A1/A2/A3) into single positive class (y=1). Background (non-CAP) epochs implicitly serve as class 0; extract negative samples from non-MCAP periods in NREM sleep. Verify event ID mapping from events.tsv.

### Classical Task 3: CAP A-phase subtype classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`MCAP-A1`, `MCAP-A2`, `MCAP-A3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `MCAP-A1` | 0 | CAP Phase A1 (synchronized EEG) |
  | `MCAP-A2` | 1 | CAP Phase A2 (mixed pattern) |
  | `MCAP-A3` | 2 | CAP Phase A3 (desynchronized EEG) |
- **Evidence**:
  - DOI: 10.1109/tnsre.2019.2934828 — Multi-class CAP A-phase subtype classification (A1/A2/A3), achieving F1-score 63-68%
- **Kernel Notes**: (replaces Potential Task 2 from original analysis.md)

### Potential Task 1: Sleep Stage Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `SLEEP-MT` epochs. R&K 30-second epoch boundaries; set tmax = 30.0 s to match.

| Event | y | Meaning |
|-------|---|---------|
| `SLEEP-S0` | 0 | Wake |
| `SLEEP-S1` | 1 | NREM Stage 1 |
| `SLEEP-S2` | 2 | NREM Stage 2 |
| `SLEEP-S3` | 3 | NREM Stage 3 |
| `SLEEP-S4` | 4 | NREM Stage 4 |
| `SLEEP-REM` | 5 | REM |

## Data Quality Notes

- Channel count and sampling rate vary substantially across subjects (5-36 channels, 100-512 Hz); normalize before cross-subject analysis.
- Mixed clinical population: NFLE, RBD, PLM, insomnia, narcolepsy, SDB, bruxism, and healthy controls; group labels are encoded in the subject metadata.
- CAP annotations are specialized biomarkers of sleep instability; fewer publications use them compared to standard staging.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review