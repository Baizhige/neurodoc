# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 159 | **Channels**: 5 | **Sampling Rate**: 250 Hz
**Manual Review**: Pending

## Paradigm

Naturalistic nightly sleep monitoring using ear-EEG (in-ear electrodes) and polysomnography (PSG) in an ecological home environment where participants self-applied the recording equipment. The study investigates the feasibility of home-based sleep staging using miniaturized ear-EEG compared to gold-standard PSG. The `trigger` event marks synchronization pulses between the ear-EEG and PSG systems.

## File Scan Result

> **Kernel SHA256**: `3f0177fd208e86ce5f2a0d5f70494b1417bceed402f3b9c884f60b047acceeef`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_2` | 72 | event | raw | Experimental or sleep-related marker events (origin requires BIDS sidecar investigation) |
| `trigger` | 175 | event | raw | Synchronization trigger between ear-EEG and PSG |


### MISC Label Summary
_Not applicable — no MISC channels detected in this dataset._
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
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`sleep_stage_W`, `sleep_stage_N1`, `sleep_stage_N2`, `sleep_stage_N3`, `sleep_stage_REM`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sleep_stage_W` | 0 | Wake stage |
  | `sleep_stage_N1` | 1 | Light sleep stage 1 |
  | `sleep_stage_N2` | 2 | Light sleep stage 2 |
  | `sleep_stage_N3` | 3 | Deep sleep (slow wave) |
  | `sleep_stage_REM` | 4 | Rapid eye movement sleep |
- **Evidence**:
  - DOI: 10.3389/fnins.2023.987578 — Presents EESM23 dataset with 10 subjects performing at-home sleep monitoring using ear-EEG, training a random forest classifier on 30-second epochs to classify sleep stages (N1, N2, N3, REM, wake) validated against manually scored PSG recordings
  - DOI: 10.1038/fnins.2023.987578 — Official data descriptor for EESM23 describing ear-EEG sleep recordings with manual PSG sleep stage annotations (W/N1/N2/N3/REM) scored by trained technicians following AASM standard, demonstrating automatic sleep scoring using SeqSleepNet
- **Kernel Notes**: CRITICAL: Sleep stage labels (sleep_stage_W, sleep_stage_N1, etc.) are NOT present in raw event HDF5 files. They are stored as PSG annotations in BIDS *events.tsv sidecar files. Kernel must: (1) Read sleep stage annotations from BIDS events.tsv files rather than raw trigger events, (2) Map sleep_stage_X events to 30-second epoch windows aligned to annotation onsets using tmin=0, tmax=30, (3) Exclude unscored epochs (~3% of data per dataset descriptor), (4) Verify annotation timing matches EEG start time using BIDS sidecar information. The 175 `trigger` events mark system synchronization between ear-EEG and PSG, not sleep stage boundaries. Class imbalance expected: N3 and REM are underrepresented relative to N2 and W. The 5-channel ear-EEG provides limited spatial resolution compared to full PSG.
