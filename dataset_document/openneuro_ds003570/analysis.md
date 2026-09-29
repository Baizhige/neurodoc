# EEG: Improvisation and Musical Structures (Auditory Oddball Chords)

**Dataset**: `openneuro_ds003570` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003570
**Category**: Sensory/Response | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 64 | **Sampling Rate**: 2048 Hz | **Manual Review**:

## Paradigm

Participants listened to sequences of three-chord musical progressions in an oddball paradigm designed to detect functional and exemplar deviants occurring within a stream of standard chord progressions. The study investigates neural responses (mismatch negativity, P600) to harmonic violations and musical structure deviants, probing the auditory system's predictive coding of musical sequences. Participants were musicians performing a response task to chord sequences.

## File Scan Result

> **Kernel SHA256**: `840b4dd49c47b95a0b5cd8d96b712a797ad98e91995d95c848ca6207e6a5f7bc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `16128` | 263 | admin | raw | Session/block start marker |
| `16228` | 1 | admin | raw | System status code (rare occurrence) |
| `16368` | 2 | admin | raw | System status code (rare occurrence) |
| `Correct - Exemplar!` | 2499 | event | raw | Feedback: correct detection of Exemplar deviant |
| `Correct - Function!` | 2936 | event | raw | Feedback: correct detection of Function deviant |
| `Incorrect - Standard!` | 2675 | event | raw | Feedback: incorrect response to standard trial |
| `boundary` | 238 | admin | raw | Block boundary marker |
| `five6_S` | 9973 | event | raw | Trial phase onset: five6 standard chord progression (ii-V6-I) |
| `five6_Sincorrect` | 397 | event | raw | Trial phase onset: five6 standard with incorrect response |
| `five6_deviantE` | 309 | event | raw | Trial phase onset: five6 Exemplar deviant chord progression |
| `five6_deviantEcorrect_E` | 405 | event | raw | Trial phase onset: five6 Exemplar deviant with correct response |
| `five6_deviantF` | 97 | event | raw | Trial phase onset: five6 Function deviant chord progression |
| `five6_deviantFcorrect_F` | 787 | event | raw | Trial phase onset: five6 Function deviant with correct response |
| `fiveRoot_S` | 9282 | event | raw | Trial phase onset: fiveRoot standard chord progression (ii-V-I) |
| `fiveRoot_Sincorrect` | 1156 | event | raw | Trial phase onset: fiveRoot standard with incorrect response |
| `fiveRoot_deviantE` | 277 | event | raw | Trial phase onset: fiveRoot Exemplar deviant chord progression |
| `fiveRoot_deviantEcorrect_E` | 675 | event | raw | Trial phase onset: fiveRoot Exemplar deviant with correct response |
| `fiveRoot_deviantF` | 120 | event | raw | Trial phase onset: fiveRoot Function deviant chord progression |
| `fiveRoot_deviantFcorrect_F` | 764 | event | raw | Trial phase onset: fiveRoot Function deviant with correct response |
| `four6_S` | 9966 | event | raw | Trial phase onset: four6 standard chord progression (ii-IV6-I) |
| `four6_Sincorrect` | 336 | event | raw | Trial phase onset: four6 standard with incorrect response |
| `four6_deviantE` | 289 | event | raw | Trial phase onset: four6 Exemplar deviant chord progression |
| `four6_deviantEcorrect_E` | 697 | event | raw | Trial phase onset: four6 Exemplar deviant with correct response |
| `four6_deviantF` | 433 | event | raw | Trial phase onset: four6 Function deviant chord progression |
| `four6_deviantFcorrect_F` | 655 | event | raw | Trial phase onset: four6 Function deviant with correct response |
| `fourRoot_S` | 9591 | event | raw | Trial phase onset: fourRoot standard chord progression (ii-IV-I) |
| `fourRoot_Sincorrect` | 779 | event | raw | Trial phase onset: fourRoot standard with incorrect response |
| `fourRoot_deviantE` | 332 | event | raw | Trial phase onset: fourRoot Exemplar deviant chord progression |
| `fourRoot_deviantEcorrect_E` | 722 | event | raw | Trial phase onset: fourRoot Exemplar deviant with correct response |
| `fourRoot_deviantF` | 189 | event | raw | Trial phase onset: fourRoot Function deviant chord progression |
| `fourRoot_deviantFcorrect_F` | 729 | event | raw | Trial phase onset: fourRoot Function deviant with correct response |
| `one` | 48960 | event | raw | Trial phase onset: chord position one |
| `two` | 48960 | event | raw | Trial phase onset: chord position two |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-class chord deviant detection (standard vs exemplar vs function)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S`, `fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE`, `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S` | 0 | standard chord progression |
  | `fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE` | 1 | exemplar deviant (same function, different inversion) |
  | `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF` | 2 | function deviant (different functional class) |
- **Evidence**:
  - 10.1177/0305735618779444 — Goldman et al. (2020) describes the auditory oddball chord paradigm with standard, exemplar deviant, and function deviant conditions; analyzes N2c and P3b ERP components
  - 10.1016/j.neuroimage.2021.118458 — Faller et al. (2021) neuroimaging analysis using the same chord oddball dataset
- **Notes**: All four block types (fourRoot, four6, fiveRoot, five6) are collapsed across progression type. The `*_Sincorrect`, `*_deviantEcorrect_E`, `*_deviantFcorrect_F`, and feedback events (`Correct - Exemplar!`, `Correct - Function!`, `Incorrect - Standard!`) are excluded from epoching to avoid response/feedback contamination; only the trial phase onset markers for the three stimulus types are used. The `one` and `two` events mark chord positions within trials and are not used as epoch anchors.

### Classical Task 2: 2-class exemplar vs function deviant
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE`, `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  | --- | --- | --- |
  | `fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE` | 0 | Exemplar deviant (middle chord same notes, different inversion) |
  | `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF` | 1 | Function deviant (middle chord different harmonic function) |
- **Evidence**:
  - 10.1177/0305735618779444 — Core contrast between exemplar and function deviants as the primary experimental manipulation; musicians categorize musical structures based on improvisational experience
  - 10.1016/j.neuroimage.2021.118458 — Spatiospectral connectivity differences between exemplar and function deviant types; same paradigm with extended connectivity analysis
- **Notes**: All four block types (fourRoot, four6, fiveRoot, five6) are pooled within each deviant category to maximize trial count and focus on the exemplar vs function distinction. The `*_deviantEcorrect_E` and `*_deviantFcorrect_F` feedback events are excluded as they occur after the response and would confound the sensory ERP; we epoch to the trial phase onset markers (`*_deviantE`, `*_deviantF`) which mark the actual chord progression onset. The 2-class formulation excludes standard trials to focus specifically on discrimination between the two deviant categories, matching the core contrast in both cited papers.

### Classical Task 3: 2-class deviant vs standard detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S`, `fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE`, `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  | --- | --- | --- |
  | `fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S` | 0 | standard (any standard chord progression) |
  | `fourRoot_deviantE`, `four6_deviantE`, `fiveRoot_deviantE`, `five6_deviantE`, `fourRoot_deviantF`, `four6_deviantF`, `fiveRoot_deviantF`, `five6_deviantF` | 1 | deviant (any exemplar or function deviant) |
- **Evidence**:
  - 10.1177/0305735618779444 — Goldman et al. 2020 analyzes mismatch negativity and P600 responses to deviants versus standards, a classic oddball contrast. Collapses both deviant types together versus all standard trials. 2 classes: standard (y=0), deviant (y=1) combining exemplar and function deviants.
- **Notes**: Standard trials are pooled across all four chord progression types (fourRoot, four6, fiveRoot, five6) and both inversions. Deviant trials are pooled across both exemplar (E) and function (F) deviant types and all progression types. The `*_Sincorrect` variants are excluded from epoching as they represent error trials with incorrect responses, not the pure stimulus-driven standard/deviant contrast. The epoch window (-0.2 to 0.8 s) captures the MMN and early P3b components typical of auditory oddball paradigms.

### Potential Task 1: 4-class progression type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.6 s *, target_events = [`fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `fourRoot_S` | 0 | fourRoot standard chord progression (ii-IV-I) |
  | `four6_S` | 1 | four6 standard chord progression (ii-IV6-I) |
  | `fiveRoot_S` | 2 | fiveRoot standard chord progression (ii-V-I) |
  | `five6_S` | 3 | five6 standard chord progression (ii-V6-I) |
- **Evidence**:
  - Goldman et al. (2020), "Improvisation experience predicts how musicians categorize musical structures" — Four harmonic progression types (ii-IV-I, ii-IV6-I, ii-V-I, ii-V6-I) used as counterbalanced block types, each serving as standard in 180-trial blocks
  - README — "The only progressions used in the experiment were ii-IV-I, ii-V-I, ii-IV6-I and ii-V6-I. Each experimental block consisted of 180 trials. For each such block one of the four aforementioned progressions were chosen as 'standard', resulting in four types of blocks."
  - events.tsv (sub-001) — Direct observation of `fourRoot_S`, `four6_S`, `fiveRoot_S`, `five6_S` event triggers marking standard trial onsets for each progression type
- **Notes**: Epoch window spans full 1600 ms trial length plus 200 ms pre-stimulus baseline, matching the fixed trial duration described in README (three 400 ms chords + 400 ms silence = 1600 ms). Standard trials (`_S` suffix) provide cleanest signal as they lack the deviant chord manipulation that could introduce confounding ERP components. The four progression types differ in harmonic function (subdominant vs. dominant) and voicing (root position vs. first inversion), making this a harmonic structure classification task.

### Potential Task 2: 2-class correct vs incorrect behavioral response
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`fourRoot_deviantEcorrect_E`, `four6_deviantEcorrect_E`, `fiveRoot_deviantEcorrect_E`, `five6_deviantEcorrect_E`, `fourRoot_deviantFcorrect_F`, `four6_deviantFcorrect_F`, `fiveRoot_deviantFcorrect_F`, `five6_deviantFcorrect_F`, `Correct - Exemplar!`, `Correct - Function!`, `fourRoot_Sincorrect`, `four6_Sincorrect`, `fiveRoot_Sincorrect`, `five6_Sincorrect`, `Incorrect - Standard!`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | fourRoot_deviantEcorrect_E | 0 | correct detection of Exemplar deviant |
  | four6_deviantEcorrect_E | 0 | correct detection of Exemplar deviant |
  | fiveRoot_deviantEcorrect_E | 0 | correct detection of Exemplar deviant |
  | five6_deviantEcorrect_E | 0 | correct detection of Exemplar deviant |
  | fourRoot_deviantFcorrect_F | 0 | correct detection of Function deviant |
  | four6_deviantFcorrect_F | 0 | correct detection of Function deviant |
  | fiveRoot_deviantFcorrect_F | 0 | correct detection of Function deviant |
  | five6_deviantFcorrect_F | 0 | correct detection of Function deviant |
  | Correct - Exemplar! | 0 | Feedback: correct detection of Exemplar deviant |
  | Correct - Function! | 0 | Feedback: correct detection of Function deviant |
  | fourRoot_Sincorrect | 1 | incorrect response to standard trial |
  | four6_Sincorrect | 1 | incorrect response to standard trial |
  | fiveRoot_Sincorrect | 1 | incorrect response to standard trial |
  | five6_Sincorrect | 1 | incorrect response to standard trial |
  | Incorrect - Standard! | 1 | Feedback: incorrect response to standard trial |
- **Evidence**:
  - (empty — Potential task)
- **Notes**: Two distinct event types mark correct vs incorrect behavioral outcomes: (1) trial phase onsets with `correct_E`/`correct_F` suffixes for correct deviant detection and `Sincorrect` suffix for incorrect standard responses; (2) feedback text events (`Correct - Exemplar!`, `Correct - Function!`, `Incorrect - Standard!`) that appear after response trials. Both event types are included as target_events to maximize epoch yield. The epoch window is centered on these events to capture pre-response predictive activity and post-response error-related potentials (ERN/Pe). y=0 pools all correct responses across both Exemplar and Function deviant types; y=1 pools all incorrect responses. The `*_deviantE` and `*_deviantF` events without correct suffixes are excluded as they represent deviant onsets where response outcome is not yet determined.

### Potential Task 3: Chord Position Decoding (One vs Two)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.4 s *, target_events = [`one`, `two`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `one` | 0 | Chord position one (first chord in progression) |
  | `two` | 1 | Chord position two (second chord in progression) |
- **Evidence**:
- **Notes**: This task decodes which temporal position within a chord progression is being presented based on evoked EEG responses. Events 'one' and 'two' mark the onsets of the first and second chords respectively, with each occurring exactly 48960 times indicating balanced classes. The 400ms chord duration and brief -100ms prestimulus baseline are inferred from the README description of trial timing (400ms per chord, 1600ms total trial length). The third chord position is not explicitly marked with a distinct event ID in the available events, so this task is limited to discriminating positions one vs two. This is a temporal position coding paradigm rather than motor imagery.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
