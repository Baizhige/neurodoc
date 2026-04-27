# ToonFaces

**Dataset**: `openneuro_ds004324` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004324
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26 | **Channels**: 38 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of three types of face images - real photographs (img), stylized toon faces (toon), and schematic stick-figure faces (sf) - each shown at different emotional intensity levels (0-4). Subjects evaluated emotion detection and affective states, allowing ERP-based comparison across face types and intensity levels.

## File Scan Result

> **Kernel SHA256**: `b27f860326399603255ab4e132a51767467fbcd872d7fea6715716fab9f46af7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `BlockEnd` | 78 | event | raw | End of block marker |
| `Instructions1` | 25 | event | raw | Instructions screen 1 |
| `Instructions2` | 25 | event | raw | Instructions screen 2 |
| `Instructions3` | 25 | event | raw | Instructions screen 3 |
| `Intro` | 22 | event | raw | Introduction screen marker |
| `PracticeInstructions` | 25 | event | raw | Practice instructions marker |
| `block1` | 26 | event | raw | Block 1 start marker |
| `block2` | 26 | event | raw | Block 2 start marker |
| `block3` | 26 | event | raw | Block 3 start marker |
| `img/0` | 1170 | event | raw | Real photograph face, intensity 0 (neutral) |
| `img/1` | 5070 | event | raw | Real photograph face, intensity 1 |
| `img/2` | 390 | event | raw | Real photograph face, intensity 2 |
| `img/3` | 390 | event | raw | Real photograph face, intensity 3 |
| `img/4` | 780 | event | raw | Real photograph face, intensity 4 (most intense) |
| `sf/0` | 1170 | event | raw | Schematic stick-figure face, intensity 0 (neutral) |
| `sf/1` | 5070 | event | raw | Schematic stick-figure face, intensity 1 |
| `sf/2` | 390 | event | raw | Schematic stick-figure face, intensity 2 |
| `sf/3` | 390 | event | raw | Schematic stick-figure face, intensity 3 |
| `sf/4` | 780 | event | raw | Schematic stick-figure face, intensity 4 |
| `toon/0` | 1170 | event | raw | Stylized toon face, intensity 0 (neutral) |
| `toon/1` | 5070 | event | raw | Stylized toon face, intensity 1 |
| `toon/2` | 390 | event | raw | Stylized toon face, intensity 2 |
| `toon/3` | 390 | event | raw | Stylized toon face, intensity 3 |
| `toon/4` | 780 | event | raw | Stylized toon face, intensity 4 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Three-class Face Type Classification (IMG vs TOON vs SF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`img/0`, `img/1`, `img/2`, `img/3`, `img/4`, `toon/0`, `toon/1`, `toon/2`, `toon/3`, `toon/4`, `sf/0`, `sf/1`, `sf/2`, `sf/3`, `sf/4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `img/0`, `img/1`, `img/2`, `img/3`, `img/4` | 0 | Real photograph face (IMG) |
  | `toon/0`, `toon/1`, `toon/2`, `toon/3`, `toon/4` | 1 | Stylized toon face (TOON) |
  | `sf/0`, `sf/1`, `sf/2`, `sf/3`, `sf/4` | 2 | Schematic stick-figure face (SF) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2023.1160800 — Official publication for the ToonFaces dataset; analyzes N170, LCP, and differential entropy ERP features across three face type categories using event-based epoching.
  - DOI: 10.21203/rs.3.rs-1886096/v1 — Uses RSVP paradigm with this dataset to present IMG/TOON/SF categories and demonstrates enhanced ERP features for emotion detection across face types.
- **Kernel Notes**: Apply baseline correction from -200ms to 0ms. Intensity sub-levels (0-4) are grouped by face type for three-class classification. Exclude admin events (block1/2/3, BlockEnd, Instructions*, Intro, PracticeInstructions) from epoching. Handle significant class imbalance (intensity 1: 5070 trials vs intensities 2/3: 390 trials per face type) via stratified sampling or weighted loss.

### Potential Task 1: Binary Emotion Detection (Emotional vs Neutral)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`img/0`, `img/1`, `img/2`, `img/3`, `img/4`, `toon/0`, `toon/1`, `toon/2`, `toon/3`, `toon/4`, `sf/0`, `sf/1`, `sf/2`, `sf/3`, `sf/4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `img/0`, `toon/0`, `sf/0` | 0 | Neutral face (intensity 0) |
  | `img/1`, `img/2`, `img/3`, `img/4`, `toon/1`, `toon/2`, `toon/3`, `toon/4`, `sf/1`, `sf/2`, `sf/3`, `sf/4` | 1 | Emotional face (intensity 1-4) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2023.1160800 — Paradigm includes emotion detection evaluation; ERP responses analyzed for affective state discrimination across emotional intensity levels.
  - DOI: 10.21203/rs.3.rs-1886096/v1 — Emotion detection is the stated task; differential entropy features analyzed to distinguish emotional from non-emotional responses.
- **Kernel Notes**: Collapse face types and pool all emotional intensities (1-4) vs neutral (0). This creates a more balanced binary problem than multi-level intensity classification. Baseline correction from -200ms to 0ms. Exclude all admin events from epoching.