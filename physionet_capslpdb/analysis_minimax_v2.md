# CAP Sleep Database

**Dataset**: `physionet_capslpdb` | **Year**: 2014 | **URL**: https://physionet.org/content/capslpdb/1.0.0/
**Category**: Biological State | **Subjects**: 108 | **Files (Completed)**: 108 | **Channels**: 5-36 (variable) | **Sampling Rate**: 100-512 Hz (variable)

## Paradigm

One hundred and eight patients from the Sleep Disorders Center, Ospedale Civile di Parma, Italy, underwent overnight polysomnographic (PSG) recording with detailed expert annotations (Terzano et al., 2002). The cohort includes 16 healthy controls and 92 patients with various sleep disorders: nocturnal frontal lobe epilepsy (NFLE, n=40), REM sleep behavior disorder (RBD, n=22), periodic limb movements (PLM, n=10), insomnia (n=9), narcolepsy (n=5), sleep-disordered breathing (SDB, n=4), and bruxism (n=2). Beyond standard sleep staging (Rechtschaffen & Kales), annotations include Cyclic Alternating Pattern (CAP) subtypes: phase A1 (high-amplitude synchronized EEG activity), A2 (mixed), and A3 (desynchronized EEG). Channel count and sampling rate vary across subjects.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/capslpdb/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `SLEEP-S0` | 19495 | long | raw | Wake stage (S0 = W) |
| `SLEEP-S1` | 4642 | long | raw | NREM Stage 1 - light sleep |
| `SLEEP-S2` | 39192 | long | raw | NREM Stage 2 - sleep spindles/K-complexes |
| `SLEEP-S3` | 11953 | long | raw | NREM Stage 3 - SWS |
| `SLEEP-S4` | 13780 | long | raw | NREM Stage 4 - deep SWS |
| `SLEEP-REM` | 18935 | long | raw | REM sleep |
| `SLEEP-MT` | 11 | admin | raw | Movement time (artifact/transition) |
| `MCAP-A1` | 26788 | short | raw | CAP phase A1 onset (synchronized EEG) |
| `MCAP-A2` | 10519 | short | raw | CAP phase A2 onset (mixed pattern) |
| `MCAP-A3` | 14324 | short | raw | CAP phase A3 onset (desynchronized EEG) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`SLEEP-S0`, `SLEEP-S1`, `SLEEP-S2`, `SLEEP-S3`, `SLEEP-S4`, `SLEEP-REM`]
- **Label Route**: `Annotation`
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
  - DOI: https://doi.org/10.13026/C2VC79 — Dataset documentation confirming PSG/EEG sleep scoring with R&K stages
- **Kernel Notes**: Exclude `SLEEP-MT` epochs. Uses standard 30-second R&K epoch boundaries; tmax=30.0s matches dataset annotation granularity.

### Primary Task 2: Binary CAP A-phase detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`MCAP-A1`, `MCAP-A2`, `MCAP-A3`]
- **Label Route**: `Annotation`
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

### Primary Task 3: CAP A-phase subtype classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 3.0 s *, target_events = [`MCAP-A1`, `MCAP-A2`, `MCAP-A3`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `MCAP-A1` | 0 | CAP Phase A1 (synchronized EEG) |
  | `MCAP-A2` | 1 | CAP Phase A2 (mixed pattern) |
  | `MCAP-A3` | 2 | CAP Phase A3 (desynchronized EEG) |
- **Evidence**:
  - DOI: 10.1109/tnsre.2019.2934828 — Multi-class CAP A-phase subtype classification (A1/A2/A3), achieving F1-score 63-68%
- **Kernel Notes**: (replaces Normal Task 2 from original analysis.md)

### Normal Task 1: Sleep Stage Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: Terzano MG et al. (2002). Atlas, rules, and recording techniques for the scoring of cyclic alternating pattern (CAP) in human sleep. *Sleep Medicine*, 3(2), 187-199. Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. https://physionet.org/content/capslpdb/1.0.0/
