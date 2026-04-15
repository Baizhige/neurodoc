# EEG: Improvisation and Musical Structures (Auditory Oddball Chords)

**Dataset**: `openneuro_ds003570` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003570
**Category**: Sensory/Response | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 64 | **Sampling Rate**: 2048 Hz
**Manual Review**: Pending

## Paradigm

Participants listened to sequences of three-chord musical progressions in an oddball paradigm designed to detect functional and exemplar deviants occurring within a stream of standard chord progressions. The study investigates neural responses (mismatch negativity, P600) to harmonic violations and musical structure deviants, probing the auditory system's predictive coding of musical sequences. Participants were musicians performing a response task to chord sequences.

## File Scan Result

> **Kernel SHA256**: `6767399ca6f7140b4c0e724c6f6e1549b9309e6db25bed8c2a88035c1384462e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `16128` | 263 | admin | raw | System status marker (rare admin code) |
| `16228` | 1 | admin | raw | System status marker (rare admin code) |
| `16368` | 2 | admin | raw | System status marker (rare admin code) |
| `Correct - Exemplar!` | 2499 | event | raw | Correct behavioral response to exemplar deviant chord |
| `Correct - Function!` | 2936 | event | raw | Correct behavioral response to function deviant chord |
| `Incorrect - Standard!` | 2675 | event | raw | Incorrect behavioral response to standard chord |
| `boundary` | 238 | event | raw | EEG recording boundary artifact marker |
| `five6_S` | 9973 | event | raw | Standard chord (five6 root, correctly responded or not) |
| `five6_Sincorrect` | 397 | event | raw | Standard chord (five6 root) with incorrect response |
| `five6_deviantE` | 309 | event | raw | Exemplar deviant chord (five6 root, same function, different inversion) |
| `five6_deviantEcorrect_E` | 405 | event | raw | Exemplar deviant chord (five6 root) with correct response |
| `five6_deviantF` | 97 | event | raw | Function deviant chord (five6 root, different functional class) |
| `five6_deviantFcorrect_F` | 787 | event | raw | Function deviant chord (five6 root) with correct response |
| `fiveRoot_S` | 9282 | event | raw | Standard chord (fiveRoot root, correctly responded or not) |
| `fiveRoot_Sincorrect` | 1156 | event | raw | Standard chord (fiveRoot root) with incorrect response |
| `fiveRoot_deviantE` | 277 | event | raw | Exemplar deviant chord (fiveRoot root, same function, different inversion) |
| `fiveRoot_deviantEcorrect_E` | 675 | event | raw | Exemplar deviant chord (fiveRoot root) with correct response |
| `fiveRoot_deviantF` | 120 | event | raw | Function deviant chord (fiveRoot root, different functional class) |
| `fiveRoot_deviantFcorrect_F` | 764 | event | raw | Function deviant chord (fiveRoot root) with correct response |
| `four6_S` | 9966 | event | raw | Standard chord (four6 root, correctly responded or not) |
| `four6_Sincorrect` | 336 | event | raw | Standard chord (four6 root) with incorrect response |
| `four6_deviantE` | 289 | event | raw | Exemplar deviant chord (four6 root, same function, different inversion) |
| `four6_deviantEcorrect_E` | 697 | event | raw | Exemplar deviant chord (four6 root) with correct response |
| `four6_deviantF` | 433 | event | raw | Function deviant chord (four6 root, different functional class) |
| `four6_deviantFcorrect_F` | 655 | event | raw | Function deviant chord (four6 root) with correct response |
| `fourRoot_S` | 9591 | event | raw | Standard chord (fourRoot root, correctly responded or not) |
| `fourRoot_Sincorrect` | 779 | event | raw | Standard chord (fourRoot root) with incorrect response |
| `fourRoot_deviantE` | 332 | event | raw | Exemplar deviant chord (fourRoot root, same function, different inversion) |
| `fourRoot_deviantEcorrect_E` | 722 | event | raw | Exemplar deviant chord (fourRoot root) with correct response |
| `fourRoot_deviantF` | 189 | event | raw | Function deviant chord (fourRoot root, different functional class) |
| `fourRoot_deviantFcorrect_F` | 729 | event | raw | Function deviant chord (fourRoot root) with correct response |
| `one` | 48960 | event | raw | First chord onset trigger in three-chord sequence |
| `two` | 48960 | event | raw | Second chord onset trigger in three-chord sequence (primary epoching reference) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Brain connectivity regression for musical training prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 1.2 s, target_events = [`two`], reject = [`boundary`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `*_S` | `standard` | standard chord (correctly responded or not) |
  | `*_deviantE*` | `exemplar_deviant` | exemplar deviant chord (same functional class, different inversion) |
  | `*_deviantF*` | `function_deviant` | function deviant chord (different functional class) |
- **Super Meta Notes**: Labels derived from experimental paradigm conditions embedded in event names. Each chord root (five6, fiveRoot, four6, fourRoot) has three condition types. Labels map to condition identifiers used to compute brain connectivity predictors: Psi(Ex) - Psi(Fu) and log.BP(Ex) - log.BP(Fu). These super-level connectivity features predict weekly improvisation hours, weekly classical hours, and dIES behavioral metrics via regression.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2021.118458 — Explicitly uses OpenNeuro ds003570 EEG data; phase slope index and alpha-band inter-network connectivity as features; 34 musicians performing auditory oddball task; predicts self-reported improvisation and classical training hours via regression; analysis uses three temporal windows: pre-response (-400 to 0ms), inter-chord (0-400ms), post-response (0-400ms).
- **Kernel Notes**: Use `two` events (48960) as primary epoching trigger aligned to second chord onset. Condition labels encoded in event names: `_S` = standard, `_deviantE` = exemplar deviant, `_deviantF` = function deviant. Numeric codes (16128, 16228, 16368) are rare admin markers—ignore. Decode events.tsv to map condition labels to `two` onset events for full trial classification. High sampling rate (2048 Hz); decimate to 500-1000 Hz after anti-aliasing filtering before connectivity computation.

### Classical Task 2: Mismatch negativity response classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`two`], reject = [`boundary`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|--------|
  | `*_S` | `standard` | standard chord |
  | `*_deviantE*` | `exemplar_deviant` | exemplar deviant (same function, different inversion) |
  | `*_deviantF*` | `function_deviant` | function deviant (different function) |
- **Evidence**:
  - DOI: 10.1177/0305735618779444 — ERP study examining N2c and P3b components discriminating exemplar from function deviants; behavioral discrimination predicted by neural discriminability; improvisation experience modulates condition discrimination.
- **Kernel Notes**: Three-class classification of chord type conditions. ERPs should show standard vs. deviant mismatches (MMN/N2c effects) and function vs. exemplar differences (P3b effects). Epoch parameters match recommended -0.2 to 0.8s window for chord onset analysis. Improvisation experience may serve as group variable for cross-subject analysis.

### Normal Task 1: Response accuracy classification for P600 validation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 0.8 s, target_events = [`Correct - Exemplar!`, `Correct - Function!`, `Incorrect - Standard!`], reject = [`boundary`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|--------|
  | `Correct - Exemplar!` | correct_exemplar | correct response to exemplar deviant (2499) |
  | `Correct - Function!` | correct_function | correct response to function deviant (2936) |
  | `Incorrect - Standard!` | incorrect_standard | incorrect response to standard chord (2675) |
- **Evidence**:
  - DOI: 10.1177/0305735618779444 — P600 effects reported for musical violations; response-accuracy events available for validation of syntactic processing.
- **Kernel Notes**: Response events have lower counts than `one`/`two` (48960), indicating not all trials received recorded responses. P600 expected 500-700ms post-stimulus for error detection. Two-class contrast (correct vs. incorrect) or three-class analysis possible. Compare with epochs from Task 1 epoched by condition to validate response-accuracy mapping.

### Potential Task 1: Continuous EEG connectivity segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, segment_length = 2.0 s
- **Label Route**: `event`
- **Target Definition**: N/A (null labels; unsupervised analysis)
- **Notes**: For exploratory connectivity or time-frequency decomposition when trial-level condition labels are unavailable. Two-second windows capture one full chord presentation cycle. Fifty percent overlap enables sliding-window connectivity estimates. High sampling rate (2048 Hz) provides fine temporal resolution for frequency-domain analysis.
- **Kernel Notes**: No condition labels required for unsupervised segmentation; suitable for resting-state-like connectivity baselines or data quality checks before condition-specific analysis.