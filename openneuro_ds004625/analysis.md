# Mind in Motion: Young Adults Walking Over Uneven Terrain

**Dataset**: `openneuro_ds004625` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004625
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 543 | **Channels**: 284 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants walked over uneven terrain at different speeds while high-density EEG, EMG, and kinematic data were simultaneously recorded, with a seated resting condition also included. The study examines neural correlates of locomotor control and gait adaptation during ambulatory tasks. Gait events (heel-strikes, toe-offs) were synchronized with EEG via force-sensitive insoles.

## File Scan Result

> **Kernel SHA256**: `680cdbe8db183b77f33afade3ed9395baea89227f8c7c39f872a35a969dec9d0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CGY-M  1` | 676 | event | raw | Gait measurement marker |
| `CGY-T  1` | 2786 | event | raw | Terrain change trigger |
| `CWR-M  1` | 269 | event | raw | Cobblestone walk marker |
| `CWR-T  1` | 3 | event | raw | Cobblestone terrain marker |
| `LHS` | 65124 | event | raw | Left heel strike |
| `LS-Sync` | 536 | admin | raw | Insole sync pulse (exclude) |
| `LTO` | 65105 | event | raw | Left toe off |
| `NGY-M  1` | 10 | event | raw | Measurement marker |
| `RHS` | 63800 | event | raw | Right heel strike |
| `RTO` | 63792 | event | raw | Right toe off |
| `TrialEnd` | 543 | event | raw | Trial end marker |
| `TrialStart` | 543 | event | raw | Trial start marker |
| `boundary` | 543 | admin | raw | Segment boundary (exclude) |
| `spare-M  1` | 635 | event | raw | Spare measurement marker |
| `spare-T  1` | 14 | event | raw | Spare terrain marker |
| `spare-boundary` | 3 | admin | raw | Spare boundary (exclude) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Gait Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|  
  | `LHS` | 0 | Left heel strike |
  | `LTO` | 1 | Left toe off |
  | `RHS` | 2 | Right heel strike |
  | `RTO` | 3 | Right toe off |
- **Evidence**:
  - DOI: 10.1162/imag.a.1039 — Age differences in electrocortical dynamics during uneven terrain walking; uses EEG spectral analysis aligned to gait cycle events (LHS, RHS, LTO, RTO)
  - DOI: 10.1371/journal.pone.0278646 — Uneven terrain treadmill walking study; validates gait event detection methodology as part of Mind in Motion parent study
- **Kernel Notes**: High-density 284-channel EEG during walking requires ICA-based artifact correction for motion artifacts. Exclude administrative events (`boundary`, `LS-Sync`, `spare-boundary`). Restrict epochs to walking bouts using TrialStart/TrialEnd markers. Verify no epoch overlap contamination given high event counts (~65,000 gait events per type). Onset alignment at heel-strike/toe-off captures neural activity preceding and following each step.

### Classical Task 2: Terrain Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`CGY-T 1`, `CWR-M 1`, `CGY-M 1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|  
  | `CGY-T 1` | 0 | Terrain change trigger |
  | `CGY-M 1` | 1 | Gait measurement marker (terrain segment) |
  | `CWR-M 1` | 2 | Cobblestone walk marker |
- **Evidence**:
  - DOI: 10.1162/imag.a.1039 — Examines EEG alpha/beta band power changes across terrain unevenness levels (flat, low, medium, high)
  - DOI: 10.3389/fnagi.2025.1644741 — Measures walking speed across four terrain conditions; terrain condition labels derive from experimental design markers
- **Kernel Notes**: Extended tmax of 4.0s accommodates neural processing of terrain transitions during gait. Verify terrain type mapping from events.tsv — `CGY-T 1` indicates transition to specific terrain, `CWR-M 1` indicates cobblestone condition. Additional terrain labels may require derivation from trial metadata. Onset alignment captures pre-transition baseline through adaptation period. Use `spare-M 1` sparingly (n=635) as supplementary terrain markers.

### Classical Task 3: Gait Speed Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 7.0 s, overlap = 0.86 (approximately 6s overlap for 1s slide)
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|  
  | Segment within TrialStart/TrialEnd | Continuous speed (m/s) | Walking speed extracted from force-sensitive insole kinematic data |
- **Evidence**:
  - DOI: 10.3389/fnagi.2025.1644741 — Walking speed extracted across terrain conditions (flat, low, medium, high) as continuous regression target
  - DOI: 10.1371/journal.pone.0278646 — Validates gait variability methodology; step kinematics extracted during uneven terrain walking as part of Mind in Motion study
- **Kernel Notes**: Speed values require fusion of force-sensitive insole kinematic data synchronized with EEG timestamps. Apply segmentation within TrialStart/TrialEnd boundaries only. Window length of 7.0s with 0.86 overlap per validated methodology extracts speed estimates from kinematic channels. Additional regression targets potentially derivable: step duration variability, sacral excursion (per DOI: 10.1371/journal.pone.0278646). Exclude administrative markers from segmentation boundaries.