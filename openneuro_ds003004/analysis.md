# Imagined Emotion Study

**Dataset**: `openneuro_ds003004` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 34 | **Channels**: 219 | **Sampling Rate**: 256 Hz
**Manual Review**: Pending

## Paradigm

Participants used voice-guided imagery to induce and sustain 15 distinct emotional states (awe, anger, compassion, content, disgust, excitement, fear, frustration, grief, happiness, jealousy, joy, love, relief, relaxation, sadness), using button presses to indicate the onset and offset of each imagined emotion. The paradigm includes pre-baseline and post-baseline recording periods, with initial instructions and imagination suggestions provided throughout the session. High-density EEG recordings were collected using a 256-channel system.

## File Scan Result

> **Kernel SHA256**: `ccceb38156c8ce81c8bdba2548fa2c15b964a79fb5314b0b5c6d739bd09667a8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ExitThankYou` | 34 | event | raw | Exit thank you screen |
| `FeelingItInstructionsButton` | 18 | event | raw | Instructions for feeling with button |
| `FeelingItInstructionsNoButton` | 19 | event | raw | Instructions for feeling without button |
| `ImaginationSuggestions` | 34 | event | raw | Imagination suggestions |
| `InitialInstructions` | 31 | event | raw | Initial instructions |
| `InstructionsForEnding` | 34 | event | raw | Instructions for ending |
| `anger` | 34 | event | raw | Anger emotion period |
| `awe` | 35 | event | raw | Awe emotion period |
| `compassion` | 34 | event | raw | Compassion emotion period |
| `content` | 34 | event | raw | Content emotion period |
| `disgust` | 34 | event | raw | Disgust emotion period |
| `enter` | 508 | event | raw | Enter |
| `excite` | 34 | event | raw | Excitement emotion period |
| `exit` | 558 | event | raw | Exit |
| `fear` | 34 | event | raw | Fear emotion period |
| `frustration` | 34 | event | raw | Frustration emotion period |
| `grief` | 34 | event | raw | Grief emotion period |
| `happy` | 34 | event | raw | Happiness emotion period |
| `jealousy` | 34 | event | raw | Jealousy emotion period |
| `joy` | 34 | event | raw | Joy emotion period |
| `love` | 34 | event | raw | Love emotion period |
| `postbase` | 34 | event | raw | Post-baseline period |
| `postbase_instruct` | 34 | event | raw | Post-baseline instruction |
| `prebase` | 34 | event | raw | Pre-baseline period |
| `prebase_instruct` | 33 | event | raw | Pre-baseline instruction |
| `press` | 703 | event | raw | Button press (onset/offset marker) |
| `press1` | 492 | event | raw | Secondary button press marker |
| `relax` | 34 | event | raw | Relax emotion period |
| `relief` | 34 | event | raw | Relief emotion period |
| `sad` | 34 | event | raw | Sadness emotion period |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Subject metadata not available in BIDS files |
| `subject_sex` | missing | Subject metadata not available in BIDS files |
| `device` | missing | Recording device metadata not available in BIDS files |

## Tasks

### Classical Task 1: 2-class Binary Valence Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = null, overlap = 0.75, segment_length = 2.0 s
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `love` | 0 | positive valence |
  | `joy` | 0 | positive valence |
  | `happy` | 0 | positive valence |
  | `relief` | 0 | positive valence |
  | `compassion` | 0 | positive valence |
  | `content` | 0 | positive valence |
  | `excite` | 0 | positive valence |
  | `awe` | 0 | positive valence |
  | `anger` | 1 | negative valence |
  | `jealousy` | 1 | negative valence |
  | `disgust` | 1 | negative valence |
  | `frustration` | 1 | negative valence |
  | `fear` | 1 | negative valence |
  | `sad` | 1 | negative valence |
  | `grief` | 1 | negative valence |
- **Kernel Notes**: Group the 15 emotion label events into binary valence categories. Use 2-s overlapping Hanning windows for spectral decomposition within each emotion period (43s-12min), following FBCSP approach from ACII 2013. The `press`/`press1` events (703/492 counts) likely mark button-press onsets but their mapping to emotion labels requires verification from behavioral logs.
- **Evidence**:
  - DOI: 10.1109/ACII.2013.160 — Emotion recognition from EEG during self-paced emotional imagery using Filter-Bank Common Spatial Pattern (FBCSP) with binary valence classification (positive vs negative), achieving 71.3% accuracy on 12 subjects.

### Potential Task 1: 15-class Imagined Emotion Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 218.0 s, overlap = 0.75, target_events = [`press`, `press1`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `press` | 0 | awe |
  | `press` | 1 | anger |
  | `press` | 2 | compassion |
  | `press` | 3 | content |
  | `press` | 4 | disgust |
  | `press` | 5 | excite |
  | `press` | 6 | fear |
  | `press` | 7 | frustration |
  | `press` | 8 | grief |
  | `press` | 9 | happy |
  | `press` | 10 | jealousy |
  | `press` | 11 | joy |
  | `press` | 12 | love |
  | `press` | 13 | relax |
  | `press` | 14 | relief |
  | `press` | 15 | sad |
- **Kernel Notes**: CRITICAL MAPPING ISSUE: The `press`/`press1` events (1195 total) are detected in events.tsv but their mapping to the 15 emotion labels is unresolved. Original paradigm had participants press buttons to indicate emotion onset/offset, but EEG trigger channel did not capture these presses. Verify mapping from behavioral log files or sequence alignment before epoching. If mapping cannot be verified, fall back to segment-based epoching around emotion label events (see Alternative below). Use 2-s Hanning windows with 75% overlap for spectral decomposition as per original analysis paradigm.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.118873 — Unsupervised AMICA decomposition of high-density EEG during 15 emotion imagination periods; provides paradigm validation (same dataset: 31 subjects, 15 emotion categories, 128-250 channels).

### Potential Task 2: Brain State Dynamics During Emotion Imagination
- **Task Type**: segmentation
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 218.0 s, overlap = null, target_events = [`awe`, `anger`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relax`, `relief`, `sad`]
- **Label Route**: misc
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `awe` | null | Awe emotion period |
  | `anger` | null | Anger emotion period |
  | `compassion` | null | Compassion emotion period |
  | `content` | null | Content emotion period |
  | `disgust` | null | Disgust emotion period |
  | `excite` | null | Excitement emotion period |
  | `fear` | null | Fear emotion period |
  | `frustration` | null | Frustration emotion period |
  | `grief` | null | Grief emotion period |
  | `happy` | null | Happiness emotion period |
  | `jealousy` | null | Jealousy emotion period |
  | `joy` | null | Joy emotion period |
  | `love` | null | Love emotion period |
  | `relax` | null | Relax emotion period |
  | `relief` | null | Relief emotion period |
  | `sad` | null | Sadness emotion period |
- **Kernel Notes**: Use unsupervised decomposition (AMICA/ICA) to learn brain state dynamics within each emotion period. Target events define epoch anchors; labels are null as this is segmentation/dynamics discovery rather than classification. Explore whether EEG dynamics cluster by emotion category or valence. Matches original AMICA analysis from DOI: 10.1016/j.neuroimage.2022.118873.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.118873 — Applied 20-model AMICA decomposition to high-density EEG to learn brain state dynamics during 15-class emotion imagination; explores whether EEG spectral patterns cluster by emotion category or valence (super-level analysis).
