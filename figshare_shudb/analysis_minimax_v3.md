# SHU Motor Imagery EEG Dataset

**Dataset**: `figshare_shudb` | **Year**: 2022 | **URL**: https://figshare.com/articles/software/shu_dataset/19228725/1
**Category**: Action/Output | **Subjects**: 21 | **Files (Completed)**: 232 | **Channels**: 32 | **Sampling Rate**: 250 Hz

## Paradigm

Twenty-one subjects (sub-001 to sub-021) performed cued left/right hand motor imagery across 4-5 sessions each (SHU dataset). EEG was recorded from 32 channels using a BrainAmp MR plus amplifier with Ag/AgCl cap (standard 10-20 system). Each session contained approximately 44-50 trials per class (left hand MI and right hand MI). Events are stored in TSV files following a BIDS-like structure and loaded by the kernel from adjacent `events/` directories. The dataset is well-suited for studying longitudinal motor imagery performance and cross-session transfer.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://figshare.com/articles/software/shu_dataset/19228725/1

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left` | ~10900 (total) | short | raw | Left-hand motor imagery cue onset |
| `right` | ~10900 (total) | short | raw | Right-hand motor imagery cue onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Total counts estimated as 232 files x ~47 trials per class. Exact per-session counts vary slightly (44-50 per class).

## Tasks

### Primary Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.0 s, target_events = [`left`, `right`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left` | 0 | Left-hand motor imagery |
  | `right` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01647-1 — Uses 4-second EEG epochs extracted from 7.5s trials for binary classification between left and right hand motor imagery
  - DOI: 10.1016/j.heliyon.2024.e37343 — Validates multi-session left vs right hand motor imagery classification using CNN-based feature extraction with 4s MI window
  - DOI: 10.1016/j.jneumeth.2025.110483 — Validates on SHU dataset achieving 87.2% within-session and 67.2% cross-session accuracy for left/right hand MI
  - DOI: 10.1109/jbhi.2024.3467090 — Evaluates binary motor imagery classification on SHU dataset achieving 69.3% accuracy
  - DOI: 10.31083/j.jin2308153 — Evaluates 3D-CNN models for two-class motor imagery classification on SHU dataset
- **Kernel Notes**: Extract epochs from 0 to 4 seconds after cue onset. Apply band-pass filtering (0.5-40 Hz) as standard preprocessing. (replaces Normal Task 1 from original analysis.md)

## Data Quality Notes

- Age and sex information are not available in this dataset.
- 4-5 sessions per subject; slight trial count variation per session (44-50 per class) may introduce minor class imbalance within a session.
- BrainAmp MR plus amplifier with Ag/AgCl cap; standard 32-channel 10-20 montage.
- BIDS-like event structure; kernel reads TSV files from the `events/` subdirectory.

