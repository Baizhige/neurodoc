# An EEG dataset recorded during affective music listening

**Dataset**: `openneuro_ds002721` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002721
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 185 | **Channels**: 19 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants listened to music clips from film scores while their EEG was recorded, to investigate the neural correlates of music-induced emotional states. Each music clip is marked at onset with a numeric trigger code (800-908 range encode specific music tracks; system markers such as 32768 and 257 are used for synchronization). The study is part of a a research series investigating affective processing in music, with participants reporting felt emotions across multiple affective dimensions. Emotion ratings were collected on a 9-point Likert scale across 8 affective dimensions including pleasantness.

## File Scan Result

> **Kernel SHA256**: `4e0825c4a8111a4fb1fdcf35019ac9de7d376962ac76945cda6b6fbf0f8cb727`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Music Clip Onset Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`800`, `801`, `802`, `803`, `804`, `805`, `806`, `807`, `808`, `786`, `788`, `833`, `834`, `835`, `836`, `837`, `838`, `839`, `840`, `902`, `903`, `904`, `905`, `906`, `907`, `908`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `800` | 0 | Music clip onset (track 800) |
  | `801` | 1 | Music clip onset (track 801) |
  | `802` | 2 | Music clip onset (track 802) |
  | `803` | 3 | Music clip onset (track 803) |
  | `804` | 4 | Music clip onset (track 804) |
  | `805` | 5 | Music clip onset (track 805) |
  | `806` | 6 | Music clip onset (track 806) |
  | `807` | 7 | Music clip onset (track 807) |
  | `808` | 8 | Music clip onset (track 808) |
  | `786` | 9 | Music clip onset (track 786) |
  | `788` | 10 | Music clip onset (track 788) |
  | `833` | 11 | Music clip onset (track 833) |
  | `834` | 12 | Music clip onset (track 834) |
  | `835` | 13 | Music clip onset (track 835) |
  | `836` | 14 | Music clip onset (track 836) |
  | `837` | 15 | Music clip onset (track 837) |
  | `838` | 16 | Music clip onset (track 838) |
  | `839` | 17 | Music clip onset (track 839) |
  | `840` | 18 | Music clip onset (track 840) |
  | `902` | 19 | Music clip onset (track 902) |
  | `903` | 20 | Music clip onset (track 903) |
  | `904` | 21 | Music clip onset (track 904) |
  | `905` | 22 | Music clip onset (track 905) |
  | `906` | 23 | Music clip onset (track 906) |
  | `907` | 24 | Music clip onset (track 907) |
  | `908` | 25 | Music clip onset (track 908) |
- **Kernel Notes**: System markers (32768, 1092, 257, 33575) must be excluded from target_events. Clip duration is 12 s per DOI reference. Extract 1.2 s epochs centered on each music clip onset trigger for multi-class track identification (26 unique clips). The 40 s clip duration noted in the dataset description is inconsistent with the published protocol (12 s clips); task parameters follow the DOI reference.
- **Evidence**: DOI: 10.1038/s41597-020-0507-6 — "Film Clips dataset containing EEG recorded from 31 participants listening to 12-second film music clips while reporting felt emotions across 8 affective dimensions"

### Classical Task 2: Music-Induced Pleasantness Recognition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.0 s, overlap = 0.0, target_events = [`music_onset`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `high_pleasantness` | 0 | Pleasantness rating ≥ 5 on 9-point Likert scale |
  | `low_pleasantness` | 1 | Pleasantness rating < 5 on 9-point Likert scale |
- **Super Meta Notes**: Derived from raw event(s) [`800`, `801`, `802`, `803`, `804`, `805`, `806`, `807`, `808`, `786`, `788`, `833`, `834`, `835`, `836`, `837`, `838`, `839`, `840`, `902`, `903`, `904`, `905`, `906`, `907`, `908`]. Each music clip onset timestamp is matched to corresponding self-reported pleasantness rating from behavioral logs. Binary threshold applied at scale midpoint (5) to create balanced classes. Kernel step: Load events.tsv and behavioral rating files, extract pleasantness column, compute binary labels, map to epochs via onset timestamp alignment.
- **Kernel Notes**: Requires access to behavioral log files containing emotion ratings. The DOI reference confirms 8-dimensional emotion ratings including pleasantness (1-9 scale) were collected. Duration discrepancy (40 s description vs. 12 s DOI reference) should be verified against actual behavioral log timing before epoch extraction. System markers excluded.
- **Evidence**: DOI: 10.1038/s41597-020-0507-6 — "participants listening to 12-second film music clips while reporting felt emotions across 8 affective dimensions" (includes pleasantness dimension on 1-9 Likert scale)