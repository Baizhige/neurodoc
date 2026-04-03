# EEG: Continuous Gameplay of an 8-Bit Style Video Game

**Dataset**: `openneuro_ds003517` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003517
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 34
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played a continuous 8-bit style video game while EEG was recorded to study canonical neural events during naturalistic gameplay. The experiment also included a visual oddball task and a gambling task embedded within the session. Game events (shooting, collecting stars, collisions) and oddball stimuli (standard and rare tones/targets) were time-locked to EEG recordings. The study aims to identify ERP components (P300, error-related negativity) in a real-world, engaging task context.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003517

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ODDBALL STANDARD` | 17 | short | raw | Standard tone in oddball task (frequent) |
| `ODDBALL RARE` | 17 | short | raw | Rare/target tone in oddball task (infrequent) |
| `ODDBALL START` | 17 | short | raw | Oddball task block start marker |
| `ODDBALL DONE` | 17 | short | raw | Oddball task block end marker |
| `SHOOT_BUTTON` | 18 | short | raw | Player shoot button press |
| `COLLECT_STAR` | 18 | short | raw | Player collected a star (reward) |
| `PLAYER_CRASH_ENEMY` | 18 | short | raw | Player crashed into enemy |
| `MISSILE_HIT_ENEMY` | 17 | short | raw | Missile hit enemy (success) |
| `PLAYER_CRASH_WALL` | 17 | short | raw | Player crashed into wall |
| `COLLECT_AMMO` | 17 | short | raw | Player collected ammunition |
| `GAMBLING WIN` | 14 | short | raw | Gambling task win outcome |
| `GAMBLING LOSS` | 14 | short | raw | Gambling task loss outcome |
| `GAME START` | 16 | short | raw | Game session start |
| `GAME OVER` | 16 | short | raw | Game session end |
| `STATUS` | 34 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Oddball target detection (P300 classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.25 s, tmax = 0.75 s, target_events = [`ODDBALL STANDARD`, `ODDBALL RARE`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `ODDBALL STANDARD` | 0 | Standard/frequent tone |
  | `ODDBALL RARE` | 1 | Rare/target tone (P300 evoking) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2016.02.075 — Shows LASSO classifier trained on oddball target vs standard events for P300 detection
  - DOI: 10.1016/j.neuroimage.2025.121521 — Decodes naturalistic game behaviors from EEG oscillatory patterns
- **Kernel Notes**: Baseline correction: -500 to -300 ms as per paper. Downsample to 250 Hz after epoching. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Gambling outcome classification (win vs loss)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.25 s, tmax = 0.75 s, target_events = [`GAMBLING WIN`, `GAMBLING LOSS`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `GAMBLING LOSS` | 0 | Loss outcome |
  | `GAMBLING WIN` | 1 | Win outcome |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2016.02.075 — LASSO classifier on gambling wins vs losses with same epoch parameters
- **Kernel Notes**: Baseline correction: -500 to -300 ms. Only 14 files contain gambling events; small sample size warning. (replaces Normal Task 1 from original analysis.md)

### Primary Task 3: Six-class naturalistic game behavior classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`SHOOT_BUTTON`, `COLLECT_STAR`, `COLLECT_AMMO`, `PLAYER_CRASH_WALL`, `PLAYER_CRASH_ENEMY`, `MISSILE_HIT_ENEMY`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `SHOOT_BUTTON` | 1 | Missile launch button press |
  | `COLLECT_STAR` | 2 | Star collection (reward) |
  | `COLLECT_AMMO` | 3 | Ammunition box collection |
  | `PLAYER_CRASH_WALL` | 4 | Wall collision |
  | `PLAYER_CRASH_ENEMY` | 5 | Enemy collision |
  | `MISSILE_HIT_ENEMY` | 6 | Missile successfully hits enemy |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121521 — Decodes six naturalistic game behaviors from brain-wide EEG oscillatory activation patterns during continuous gameplay
- **Kernel Notes**: Epoch method inferred from paper's "segmentation" hint; parameters are estimated defaults. Uses continuous oscillatory amplitude envelope to define active/inactive states for decoding. Transfer learning approach: game events classified based on similarity to canonical oddball/gambling ERP patterns.

## Data Quality Notes

- 65-channel EEG recorded during naturalistic, continuous task; higher artifact rate expected from movement and engagement.
- Some sessions may be game-only (no oddball/gambling); verify event presence per file.

