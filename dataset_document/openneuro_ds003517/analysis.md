# EEG: Continuous Gameplay of an 8-Bit Style Video Game

**Dataset**: `openneuro_ds003517` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003517
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 34 | **Manual Review**: Pending
**Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played a continuous 8-bit style video game while EEG was recorded to study canonical neural events during naturalistic gameplay. The experiment also included a visual oddball task and a gambling task embedded within the session. Game events (shooting, collecting stars, collisions) and oddball stimuli (standard and rare tones/targets) were time-locked to EEG recordings. The study aims to identify ERP components (P300, error-related negativity) in a real-world, engaging task context.

## File Scan Result

> **Kernel SHA256**: `61f1ba9fb5fb093515699389d7452e5aa40118a47b7ad6c331067fbda5430ea1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 20` | 17 | event | raw | Standard/frequent tone in oddball task |
| `S 22` | 2719 | event | raw | Unidentified game event |
| `S 25` | 681 | event | raw | Unidentified game event |
| `S 29` | 17 | event | raw | Rare/target tone in oddball task |
| `S 50` | 15 | event | raw | Gambling task loss outcome |
| `S 51` | 617 | event | raw | Unidentified game event |
| `S 52` | 618 | event | raw | Unidentified game event |
| `S 53` | 16 | event | raw | Gambling task win outcome |
| `S 90` | 13562 | event | raw | Missile launch button press |
| `S 91` | 4443 | event | raw | Star collection (reward) |
| `S 92` | 1810 | event | raw | Ammunition box collection |
| `S 93` | 13776 | event | raw | Wall collision |
| `S 94` | 1103 | event | raw | Enemy collision |
| `S 97` | 6495 | event | raw | Missile successfully hits enemy |
| `S 98` | 4002 | event | raw | Unidentified game event |
| `S 99` | 68 | event | raw | Unidentified game event |
| `S100` | 16 | event | raw | Game session start marker |
| `S101` | 14 | event | raw | Unidentified low-frequency event |
| `S102` | 11 | event | raw | Unidentified low-frequency event |
| `S103` | 10 | event | raw | Unidentified low-frequency event |
| `S104` | 9 | event | raw | Unidentified low-frequency event |
| `S105` | 6 | event | raw | Unidentified low-frequency event |
| `S106` | 4 | event | raw | Unidentified low-frequency event |
| `S107` | 3 | event | raw | Unidentified low-frequency event |
| `S108` | 2 | event | raw | Unidentified low-frequency event |
| `S109` | 2 | event | raw | Unidentified low-frequency event |
| `S110` | 1 | event | raw | Unidentified low-frequency event |
| `S111` | 1 | event | raw | Unidentified low-frequency event |
| `boundary` | 34 | event | raw | Recording discontinuity marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Oddball target detection (P300 classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.25 s, tmax = 0.75 s, target_events = [`S 20`, `S 29`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 20` | 0 | Standard/frequent tone (probable) |
  | `S 29` | 1 | Rare/target tone (probable) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2016.02.075 — Origin dataset publication; LASSO classifier trained on oddball target vs standard events for P300 detection using tmin=-0.25s, tmax=0.75s, baseline=-500 to -300ms
  - DOI: 10.1016/j.neuroimage.2025.121521 — Decodes naturalistic game behaviors from EEG oscillatory patterns
- **Kernel Notes**: CRITICAL — Analysis.md references ODDBALL STANDARD and ODDBALL RARE labels, but only generic codes S 20 and S 29 appear in scan. Count of 17 matches expected oddball count. Kernel must load raw file Stim channel or annotation stream to decode label mapping before processing. Baseline correction: -500 to -300 ms if mapping confirmed.

---

### Potential Task 2: Gambling outcome classification (win vs loss)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.25 s, tmax = 0.75 s, target_events = [`S 50`, `S 53`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 50` | 0 | Loss outcome (probable, 15 occurrences) |
  | `S 53` | 1 | Win outcome (probable, 16 occurrences) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2016.02.075 — Same paper reports LASSO classifier on gambling wins vs losses with same epoch parameters; only 14 files contain gambling events (small sample warning)
- **Kernel Notes**: CRITICAL — GAMBLING WIN/LOSS labels from analysis.md not in scanned data. S 50 (15) and S 53 (16) counts approximate the 14-file gambling subset. Kernel must verify Stim channel mapping. Only 14 files contribute gambling events; expect imbalanced epochs. Baseline correction: -500 to -300 ms.

---

### Potential Task 3: Six-class naturalistic game behavior classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`S 90`, `S 91`, `S 92`, `S 93`, `S 94`, `S 97`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 90` | 1 | Missile launch button press (probable, 13562 occurrences) |
  | `S 91` | 2 | Star collection — reward (probable, 4443 occurrences) |
  | `S 92` | 3 | Ammunition box collection (probable, 1810 occurrences) |
  | `S 93` | 4 | Wall collision (probable, 13776 occurrences) |
  | `S 94` | 5 | Enemy collision (probable, 1103 occurrences) |
  | `S 97` | 6 | Missile successfully hits enemy (probable, 6495 occurrences) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121521 — Decodes six naturalistic game behaviors from brain-wide EEG oscillatory activation patterns during continuous gameplay; uses oscillatory amplitude envelopes to define active/inactive states
- **Kernel Notes**: CRITICAL — Analysis.md references SHOOT_BUTTON, COLLECT_STAR, COLLECT_AMMO, PLAYER_CRASH_WALL, PLAYER_CRASH_ENEMY, MISSILE_HIT_ENEMY but these labels not in scan. High-count events S 90–S 97 likely correspond, but mapping unverified. Kernel must decode Stim channel before processing. Paper uses continuous oscillatory amplitude approach; verify epoch window with raw file inspection. High epoch counts suggest sufficient training data.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
