# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 5 | **Sampling Rate**: 250 Hz

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. The `trigger` event marks synchronization pulses between the ear-EEG and PSG systems.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005178

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger` | 175 | long | raw | Synchronization trigger between ear-EEG and PSG |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `trigger`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`sleep_stage_W`, `sleep_stage_N1`, `sleep_stage_N2`, `sleep_stage_N3`, `sleep_stage_REM`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sleep_stage_W` | 0 | Wake stage |
  | `sleep_stage_N1` | 1 | Light sleep stage 1 |
  | `sleep_stage_N2` | 2 | Light sleep stage 2 |
  | `sleep_stage_N3` | 3 | Deep sleep (slow wave) |
  | `sleep_stage_REM` | 4 | Rapid eye movement sleep |
- **Super Meta Notes**: Derived from manual PSG sleep scoring by trained sleep technicians following AASM standard. Labels stored as .tsv event files in BIDS format (e.g., sleep_stage_W, sleep_stage_N1, etc.). Epochs marked as 'unscored' by the manual scorer were disregarded in the analysis (3% unscored in EESM23). Kernel step: Read sleep stage annotations from BIDS *events.tsv files and map to 30-second epoch windows aligned with PSG scoring.
- **Evidence**:
  - DOI: 10.3389/fnins.2023.987578 — Presents EESM23 dataset with 10 subjects performing at-home sleep monitoring using ear-EEG, training a random forest classifier on 30-second epochs to classify sleep stages (N1, N2, N3, REM, wake) validated against manually scored PSG recordings
  - DOI: 10.1038/s41597-025-04579-8 — Data descriptor describing EESM23 dataset containing ear-EEG sleep recordings with manual PSG sleep stage annotations (W/N1/N2/N3/REM) scored by trained technicians, demonstrating automatic sleep scoring using SeqSleepNet
- **Kernel Notes**: Extract 30-second epochs aligned with sleep stage annotation onsets. Merge sleep stage labels from events.tsv as target y. Exclude unscored epochs. Verify annotation timing matches EEG start time using BIDS sidecar information. (replaces Normal Task 1 from original analysis.md)

## Data Quality Notes

- Only 5 channels (ear-EEG) - very limited spatial resolution.
- No sleep stage labels in events.tsv; PSG annotations needed for staging.
- Home-recorded data - subject-specific motion and environmental artifacts expected.

