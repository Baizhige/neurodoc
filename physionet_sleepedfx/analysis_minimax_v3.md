# Sleep-EDF Database Expanded

**Dataset**: `physionet_sleepedfx` | **Year**: 1992/2013 | **URL**: https://physionet.org/content/sleep-edfx/1.0.0/
**Category**: Biological State | **Subjects**: 58 | **Files (Completed)**: 197 | **Channels**: 7 | **Sampling Rate**: 100 Hz

## Paradigm

The Sleep-EDF Database Expanded contains whole-night polysomnographic (PSG) sleep recordings with expert-annotated sleep stage hypnograms (Kemp et al., 2000). Two study types are included: Sleep Cassette (SC, 39 subjects, 2 nights each = 78 recordings) and Sleep Treatment (ST, 19 subjects). EEG was recorded from 2 channels (Fpz-Cz and Pz-Oz) along with a horizontal EOG, submental EMG, and event/temperature markers. Sleep stages (W, 1, 2, 3, 4, REM) were scored in 30-second epochs by sleep technicians using Rechtschaffen & Kales criteria. Hypnogram annotations are loaded by the kernel from companion `*Hypnogram.edf` files adjacent to each PSG file.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://physionet.org/content/sleep-edfx/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage W` | ~24000 | long | raw | Wake stage (30-second epoch) |
| `Sleep stage 1` | ~3000 | long | raw | NREM Stage 1 - light sleep |
| `Sleep stage 2` | ~40000 | long | raw | NREM Stage 2 - sleep spindles/K-complexes |
| `Sleep stage 3` | ~5000 | long | raw | NREM Stage 3 - slow-wave sleep (SWS) |
| `Sleep stage 4` | ~3000 | long | raw | NREM Stage 4 - deep slow-wave sleep |
| `Sleep stage R` | ~9000 | long | raw | REM sleep |
| `Movement time` | rare | admin | raw | Movement artifact period (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are approximate totals across all 197 recordings. Each stage annotation spans exactly 30 seconds.

## Tasks

### Primary Task 1: Sleep stage classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage R`, `Sleep stage 4`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 |
  | `Sleep stage 2` | 2 | NREM Stage 2 |
  | `Sleep stage 3` | 3 | NREM Stage 3 (includes S3+S4 merged per AASM) |
  | `Sleep stage 4` | 3 | NREM Stage 3 (mapped to y=3; S3 and S4 merged) |
  | `Sleep stage R` | 4 | REM |
- **Super Meta Notes**: Stage 3 and Stage 4 are merged into a single N3 class (y=3) following AASM scoring guidelines. Raw events `Sleep stage 3` and `Sleep stage 4` both map to label 3.
- **Evidence**:
  - DOI: 10.7717/peerjcs.1561_table-2 — Five-class sleep staging (W, N1, N2, N3, REM) on Sleep-EDF Expanded, 30-second epochs, AASM standard merging S3+S4 into N3
- **Kernel Notes**: Exclude `Movement time` epochs. Map both `Sleep stage 3` and `Sleep stage 4` to label 3. Use 30-second window matching annotation duration exactly. (replaces Normal Task 1 from original analysis.md)

### Normal Task 2: Wake vs. Sleep Binary Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Sleep stage W` | 0 | Wake |
| `Sleep stage 1` | 1 | Any sleep (stages 1-4 and R) |
| `Sleep stage 2` | 1 | Any sleep |
| `Sleep stage 3` | 1 | Any sleep |
| `Sleep stage 4` | 1 | Any sleep |
| `Sleep stage R` | 1 | Any sleep |

## Data Quality Notes

- Only PSG files should be processed; Hypnogram files (matched companion files) are used for annotation only and are returned unchanged by the kernel.
- Class imbalance: Stage 2 is the most frequent stage; Wake also contributes large counts from lights-on periods at start/end of recording.
- Two EEG channels only (Fpz-Cz, Pz-Oz); limited spatial resolution.
- Age range is wide (18-101 years); SC study subjects are healthy adults, ST subjects had sleep disorders.
- SC study: 2 nights per subject; subject IDs encode night number in filename.

