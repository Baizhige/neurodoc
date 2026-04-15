# Social Memory cuing

**Dataset**: `openneuro_ds003702` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003702
**Category**: Complex Applied | **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A visual working memory task performed in a virtual reality environment where participants (n=47) recalled object locations and statuses following social (avatar) or non-social (stick) directional cues. The paradigm includes encoding, maintenance, and retrieval phases with stimulus markers ranging from s3001–s3048 and s3220–s3221, acquired using a 64-channel EEG system at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `296f731d3e98ba8d2cb1fb5fdada1c2eb13e4624e207477b42d089d390023df1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Marker/Impedance` | 135 | event | raw | Impedance check marker recording system contact quality |
| `New Segment/` | 20 | event | raw | Recording segment boundary marker |
| `Stimulus/s3001` | 11926 | event | raw | Primary stimulus event (cue/probe presentation) |
| `Stimulus/s3002` | 1435 | event | raw | Secondary stimulus event |
| `Stimulus/s3003` | 1410 | event | raw | Secondary stimulus event |
| `Stimulus/s3004` | 1404 | event | raw | Secondary stimulus event |
| `Stimulus/s3005` | 1438 | event | raw | Secondary stimulus event |
| `Stimulus/s3006` | 1407 | event | raw | Secondary stimulus event |
| `Stimulus/s3007` | 1418 | event | raw | Secondary stimulus event |
| `Stimulus/s3008` | 1412 | event | raw | Secondary stimulus event |
| `Stimulus/s3021` | 5653 | event | raw | Retrieval phase response event |
| `Stimulus/s3022` | 5657 | event | raw | Retrieval phase response event |
| `Stimulus/s3023` | 5657 | event | raw | Retrieval phase response event |
| `Stimulus/s3024` | 5658 | event | raw | Retrieval phase response event |
| `Stimulus/s3025` | 5659 | event | raw | Retrieval phase response event |
| `Stimulus/s3026` | 5660 | event | raw | Retrieval phase response event |
| `Stimulus/s3027` | 5661 | event | raw | Retrieval phase response event |
| `Stimulus/s3028` | 1394 | event | raw | Retrieval phase response event |
| `Stimulus/s3040` | 1412 | event | raw | Maintenance phase stimulus |
| `Stimulus/s3041` | 5681 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3042` | 5682 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3043` | 5682 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3044` | 5683 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3045` | 5685 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3046` | 5685 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3047` | 5685 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3048` | 1415 | event | raw | Object-finding phase stimulus |
| `Stimulus/s3111` | 45 | event | raw | Special event marker |
| `Stimulus/s3220` | 2241 | event | raw | Probe/cue event |
| `Stimulus/s3221` | 8121 | event | raw | Probe/cue event |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Age data not found in BIDS participants.tsv |
| `subject_sex` | missing | Sex data not found in BIDS participants.tsv |
| `device` | missing | Device information not available in metadata |

## Tasks

### Classical Task 1: Biological Sex Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, baseline = (None, 0)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/s3001` | 0 | EEG epochs from female participants (n=31) |
  | `Stimulus/s3001` | 1 | EEG epochs from male participants (n=16) |
- **Super Meta Notes**: Subject sex labels derived from participants.tsv demographic field. Kernel step: load sex column from BIDS participants.tsv, map subject IDs to binary labels (female=0, male=1), apply to all epochs from each subject. Trials from both social and non-social cue conditions are pooled per subject.
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Uses VR spatial memory EEG from openneuro_ds003702 for binary sex classification (female vs male) using spectral features from fixation, object-finding, and maintenance phases.
- **Kernel Notes**: Use s3001 as primary epoching event (highest count, ~11926 occurrences). Verify sex distribution matches paper (31 female, 16 male). Apply to all stimulus types for maximum training data.

### Classical Task 2: User Identity Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, baseline = (None, 0)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/*` | 0–46 | 47-class participant identity label per subject |
- **Super Meta Notes**: Participant identity derived from subject directory in BIDS hierarchy. Kernel step: extract subject ID from file path, convert to integer class label (0–46).
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Uses VR spatial memory EEG from openneuro_ds003702 for 47-class user identification, comparing handcrafted features (mRMR ranking) and end-to-end deep learning approaches across object-finding and maintenance phases.
- **Kernel Notes**: Cross-subject generalization challenge (47 classes). Ensure balanced epoch sampling across subjects to avoid class imbalance. Use all available stimulus events (s3001–s3048, s3220–s3221) for maximum epochs per identity class.

### Classical Task 3: Working Memory Ability Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, baseline = (None, 0)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/s3021` | continuous | Time consumption of memory recalling (seconds) |
  | `Stimulus/s3022` | continuous | Time consumption of memory recalling (seconds) |
  | `Stimulus/s3023` | continuous | Time consumption of memory recalling (seconds) |
  | `Stimulus/s3024` | continuous | Time consumption of memory recalling (seconds) |
- **Super Meta Notes**: Memory performance target derived from trial-level behavioral data (response timing). Kernel step: load timing data from BIDS events.tsv, extract response latency for retrieval phase events (s3021–s3024), use as continuous regression target.
- **Evidence**:
  - DOI: 10.3390/s23198246 — Explicitly identifies Salford/Aston/UCD dataset (openneuro_ds003702): 47 participants, 61 channels at 500Hz, uses fuzzy SVR to predict memory recalling time from EEG alpha/beta/gamma band power features across prefrontal, frontal, temporal, parietal, and occipital regions.
- **Kernel Notes**: s3021–s3028 events (~45,000 total) likely correspond to response/retrieval phase. Cross-reference events.tsv to extract actual timing values. Feature extraction focused on alpha (8–13Hz), beta (13–30Hz), gamma (30–45Hz) bands per brain region.

### Normal Task 1: Social vs Non-Social Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0, tmax = 4.0, baseline = (None, 0)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/s3001` | 0 | Epochs from social (avatar) cue trials |
  | `Stimulus/s3001` | 1 | Epochs from non-social (stick) cue trials |
- **Super Meta Notes**: Cue condition labels must be derived from BIDS JSON sidecar files containing cue_type metadata. Kernel step: parse events.tsv or JSON sidecars for cue_type field, map s3001 events to social/non-social labels based on trial-level metadata. Requires cross-referencing external labels with stimulus timestamps.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.107827 — Data descriptor for 47 participants, 64-channel EEG at 500Hz during VR working memory task with social (avatar) vs non-social (stick) directional cues. Marker codes exist for encoding, maintenance, and retrieval phases. (Partial support: describes paradigm but does not explicitly demonstrate classification task)
- **Kernel Notes**: CRITICAL: Actual stimulus events exist (s3001=11926, s3021–s3028=~45000) but mapping to social vs non-social conditions requires kernel verification of cue_type field in BIDS sidecars. Hypothesis: s3001–s3008 are cue/probe events, s3021–s3028 are response events. Verify condition assignment per stimulus code.

### Potential Task 1: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, baseline = (None, 0)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/s3001` | continuous | Participant age in years |
- **Super Meta Notes**: Subject age derived from participants.tsv demographic field. Kernel step: load age column from BIDS participants.tsv, map subject IDs to continuous age values, apply to all epochs from each subject.
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Mentions age inference task but uses binned age groups (classification), not continuous regression. True age regression requires continuous age values not explicitly validated in available references.
- **Kernel Notes**: Verify age field availability in participants.tsv (analysis.md notes `subject_age` missing in info). If age data exists, this becomes Normal Task with continuous regression target. Plausible from VR paradigm alone but requires kernel verification.