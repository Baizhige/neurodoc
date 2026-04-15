# A dataset recording joint EEG-fMRI during affective music listening

**Dataset**: `openneuro_ds002725` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002725
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 105 | **Channels**: 47 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants listened to music stimuli designed to elicit emotional responses (approach/withdrawal behavior) and self-reported their felt affective states during simultaneous EEG-fMRI recording. The study investigated how EEG reflects subcortical brain activity related to emotional responses to music. Codes 1282/1285 are likely BrainVision fMRI sync codes; 34053 may be a BrainVision hardware code; 46/9/767 may be music condition/block markers.

## File Scan Result

> **Kernel SHA256**: `f7e665f220717520135490e3c5e3be337cff08091e3cbb82bc2217657bce69f1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1282` | 39 | event | raw | BrainVision fMRI sync code (start marker) |
| `event_1285` | 42 | event | raw | BrainVision fMRI sync code (stop marker) |
| `event_265` | 13654 | event | raw | Synthetic/generated music condition marker (~40s trials) |
| `event_34053` | 83 | event | raw | BrainVision hardware code |
| `event_46` | 31067 | event | raw | Music condition/block marker (type A) |
| `event_767` | 1316 | event | raw | Music condition/block marker (type B) |
| `event_9` | 28433 | event | raw | Music condition/block marker (type C) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Synthetic Music Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`265`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | 1 | Synthetic/generated music trials (~40s duration) |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — "Joint EEG-fMRI dataset (ds002725) where 21 participants listened to synthetic and classical music while reporting felt affective states via FEELTRACE. Event 265 corresponds to synthetic music condition."
  - DOI: 10.1038/s41598-022-27361-x — "Neural decoding of music from the EEG; synthetic music trials used as training/test data"
- **Kernel Notes**: Event 265 (13,654 occurrences) is the primary synthetic music condition marker. MRI gradient artifact removal required before epoching (EEG recorded in 3T MRI scanner). Verify event presence in events.tsv before kernel execution.

### Classical Task 2: Affective State Regression (Synthetic Music)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.5, target_events = [`265`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | continuous (0-1) | FEELTRACE valence/arousal ratings during synthetic music epochs |
- **Super Meta Notes**: Labels derived from continuous FEELTRACE self-report data (valence and arousal dimensions). Map continuous ratings to 40s synthetic music epochs based on timestamp alignment.
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — "continuous FEELTRACE valence/arousal labels for affective state" during music listening; Table 1 documents FEELTRACE recordings as part of dataset
- **Kernel Notes**: Requires FEELTRACE behavioral derivative files. Load CSV files from derivatives directory, interpolate valence/arousal values to epoch timestamps. Alternative: extract from raw events if behavioral files unavailable.

### Normal Task 1: Classical Music Epoch Extraction
- **Task Type**: detection
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 180.0 s, overlap = 0.0, target_events = [`768`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `768` | 1 | Classical music trials (2-3min duration) |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — "Event 768 corresponds to classical music condition" (documented in dataset descriptor but NOT FOUND in current scan)
- **Kernel Notes**: WARNING: Event 768 is missing from scan results. Verify existence in original events.tsv files before activation. If present, classical trials vary 2-3min (180s). If absent, alternative identification via block structure/timing analysis required.

### Normal Task 2: Music Piece Identification (36-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 180.0 s, overlap = 0.5, target_events = [`265`, `768`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | 0-17 | Synthetic music pieces (18 unique pieces) |
  | `768` | 18-35 | Classical music pieces (18 unique pieces) |
- **Super Meta Notes**: Music piece identity classification across 36 distinct stimuli (18 synthetic + 18 classical). Labels derived from experimental design files mapping piece IDs to epochs.
- **Evidence**:
  - DOI: 10.1038/s41598-022-27361-x — "Neural decoding of music from the EEG; 36 music pieces (both synthetic and classical) as classification targets. First dataset: 20 participants joint EEG-fMRI music listening."
- **Kernel Notes**: Requires event 768 for classical piece identification. Missing from scan—task cannot be fully executed until verification. If both events verified, segment 40s windows with 50% overlap across full trial duration.

### Potential Task 1: Synthetic vs Classical Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`265`, `768`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | 0 | Synthetic music condition |
  | `768` | 1 | Classical music condition |
- **Kernel Notes**: Binary classification between music conditions. Requires both event types present in data. Event 768 missing from scan—task status remains potential until verification. If verified, use 40s epochs for comparison (synthetic fixed; classical variable 2-3min, may require truncation or separate analysis).

### Potential Task 2: Affective State Regression (Classical Music)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 180.0 s, overlap = 0.5, target_events = [`768`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `768` | continuous (0-1) | FEELTRACE arousal ratings during classical music epochs |
- **Kernel Notes**: Requires event 768 presence and FEELTRACE behavioral data for classical music trials (2-3min duration). Segmentation into 40s windows with 50% overlap captures continuous affective state fluctuations. Event 768 missing from scan.

### Potential Task 3: Approach-Withdrawal EEG Asymmetry Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`265`, `768`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `265` | continuous | Approach-withdrawal EEG alpha asymmetry during synthetic music |
  | `768` | continuous | Approach-withdrawal EEG alpha asymmetry during classical music |
- **Evidence**:
  - DOI: 10.1038/s41598-019-45105-2 — "Electroencephalography reflects the activity of sub-cortical brain regions during approach-withdrawal behaviour while listening to music" (same paradigm as ds002725)
- **Kernel Notes**: Correlational analysis task linking EEG frontal asymmetry to subcortical fMRI activity. Requires MRI gradient artifact correction and EEG-fMRI motion regression. Short epochs (±2s) capture transient asymmetry changes. Event 768 missing from scan.