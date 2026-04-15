# Executive Functioning Study for Assessing the Effect of Neurofeedback

**Dataset**: `openneuro_ds004350` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004350
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 479 | **Channels**: 64 | **Sampling Rate**: 256 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a battery of executive function tasks including visual N-back working memory tasks (NB1/NB2/NB3 with stimuli A/B/C/D), a Sustained Attention to Response Task (SART with target/nontarget conditions), and a Local-Global hierarchical stimulus task (largeH/largeT x smallH/smallT). The study assessed the effect of neurofeedback training on executive function performance using 64-channel EEG recordings at 256 Hz.

## File Scan Result

> **Kernel SHA256**: `0df420088002e03fdfd16bf48035a1226360a66dd49ad5ea596f4e6c22d7f6d1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LG: largeHSmallH` | 9123 | event | raw | Congruent: Large H / Small H |
| `LG: largeHSmallT` | 9120 | event | raw | Incongruent: Large H / Small T |
| `LG: largeTSmallH` | 9130 | event | raw | Incongruent: Large T / Small H |
| `LG: largeTSmallT` | 9134 | event | raw | Congruent: Large T / Small T |
| `LG: responseLargeH` | 9035 | event | raw | Response: Large H selected |
| `LG: responseLargeT` | 9272 | event | raw | Response: Large T selected |
| `LG: responseSmallH` | 9230 | event | raw | Response: Small H selected |
| `LG: responseSmallT` | 8957 | event | raw | Response: Small T selected |
| `NB1: 12` | 1 | event | raw | System marker (isolated) |
| `NB1: 5` | 1 | event | raw | System marker (isolated) |
| `NB1: 6` | 1 | event | raw | System marker (isolated) |
| `NB1: 9` | 1 | event | raw | System marker (isolated) |
| `NB1: A` | 3341 | event | raw | N-back stimulus A (1-back) |
| `NB1: B` | 3348 | event | raw | N-back stimulus B (1-back) |
| `NB1: C` | 3408 | event | raw | N-back stimulus C (1-back) |
| `NB1: D` | 3251 | event | raw | N-back stimulus D (1-back) |
| `NB1: rt` | 3323 | event | raw | Reaction time marker (1-back) |
| `NB2: 10` | 1 | event | raw | System marker (isolated) |
| `NB2: 11` | 1 | event | raw | System marker (isolated) |
| `NB2: 255` | 1 | event | raw | System marker (isolated) |
| `NB2: 5` | 1 | event | raw | System marker (isolated) |
| `NB2: 6` | 1 | event | raw | System marker (isolated) |
| `NB2: 9` | 1 | event | raw | System marker (isolated) |
| `NB2: A` | 3334 | event | raw | N-back stimulus A (2-back) |
| `NB2: B` | 3363 | event | raw | N-back stimulus B (2-back) |
| `NB2: C` | 3316 | event | raw | N-back stimulus C (2-back) |
| `NB2: D` | 3325 | event | raw | N-back stimulus D (2-back) |
| `NB2: rt` | 2827 | event | raw | Reaction time marker (2-back) |
| `NB3: A` | 3289 | event | raw | N-back stimulus A (3-back) |
| `NB3: B` | 3363 | event | raw | N-back stimulus B (3-back) |
| `NB3: C` | 3257 | event | raw | N-back stimulus C (3-back) |
| `NB3: D` | 3410 | event | raw | N-back stimulus D (3-back) |
| `NB3: rt` | 2405 | event | raw | Reaction time marker (3-back) |
| `SART: nontarget` | 11833 | event | raw | Non-target stimulus (go response) |
| `SART: rt` | 12092 | event | raw | Reaction time marker |
| `SART: target` | 1499 | event | raw | Target stimulus (requires inhibition) |
| `event_1` | 22536 | event | raw | Raw trigger code 1 (BIDS boundary/task marker) |
| `event_10` | 3 | event | raw | Raw trigger code 10 |
| `event_11` | 1 | event | raw | Raw trigger code 11 |
| `event_12` | 3 | event | raw | Raw trigger code 12 |
| `event_128` | 9622 | event | raw | Raw trigger code 128 |
| `event_129` | 9482 | event | raw | Raw trigger code 129 |
| `event_131` | 1 | event | raw | Raw trigger code 131 |
| `event_132` | 3 | event | raw | Raw trigger code 132 |
| `event_133` | 1 | event | raw | Raw trigger code 133 |
| `event_136` | 3 | event | raw | Raw trigger code 136 |
| `event_145` | 5 | event | raw | Raw trigger code 145 |
| `event_16` | 9598 | event | raw | Raw trigger code 16 |
| `event_161` | 2 | event | raw | Raw trigger code 161 |
| `event_18` | 4 | event | raw | Raw trigger code 18 |
| `event_193` | 4 | event | raw | Raw trigger code 193 |
| `event_2` | 21099 | event | raw | Raw trigger code 2 (task block marker) |
| `event_20` | 9 | event | raw | Raw trigger code 20 |
| `event_24` | 3 | event | raw | Raw trigger code 24 |
| `event_255` | 1 | event | raw | Raw trigger code 255 |
| `event_3` | 9924 | event | raw | Raw trigger code 3 |
| `event_32` | 9309 | event | raw | Raw trigger code 32 |
| `event_34` | 9 | event | raw | Raw trigger code 34 |
| `event_36` | 1 | event | raw | Raw trigger code 36 |
| `event_4` | 19408 | event | raw | Raw trigger code 4 |
| `event_40` | 4 | event | raw | Raw trigger code 40 |
| `event_5` | 2 | event | raw | Raw trigger code 5 |
| `event_6` | 3 | event | raw | Raw trigger code 6 |
| `event_64` | 9403 | event | raw | Raw trigger code 64 |
| `event_65536` | 9 | event | raw | Raw trigger code 65536 |
| `event_65537` | 1 | event | raw | Raw trigger code 65537 |
| `event_65539` | 1 | event | raw | Raw trigger code 65539 |
| `event_65600` | 2 | event | raw | Raw trigger code 65600 |
| `event_65665` | 2 | event | raw | Raw trigger code 65665 |
| `event_66` | 4 | event | raw | Raw trigger code 66 |
| `event_68` | 1 | event | raw | Raw trigger code 68 |
| `event_72` | 2 | event | raw | Raw trigger code 72 |
| `event_8` | 30903 | event | raw | Raw trigger code 8 |
| `event_9` | 8 | event | raw | Raw trigger code 9 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: N-back NB1 Working Memory Load
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = ["NB1: A", "NB1: B", "NB1: C", "NB1: D"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `NB1: A` | 0 | N-back stimulus A |
| `NB1: B` | 1 | N-back stimulus B |
| `NB1: C` | 2 | N-back stimulus C |
| `NB1: D` | 3 | N-back stimulus D |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset README confirms NB1 as a BIDS-defined N-back task variant. Stimulus events (A/B/C/D) provide 4-class classification. Excludes system markers (NB1: 5/6/9/12 with count=1) and reaction time markers (NB1: rt) due to variable timing. Source: https://openneuro.org/datasets/ds004350
- **Kernel Notes**: Standard N-back uses variable ISI (~2000ms) with 500ms stimulus duration; epoch window accommodates full trial. Files are task-separated; use NB1-prefixed events only. The 1-back level targets working memory maintenance and updating processes.

### Classical Task 2: N-back NB3 Working Memory Load
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = ["NB3: A", "NB3: B", "NB3: C", "NB3: D"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `NB3: A` | 0 | N-back stimulus A |
| `NB3: B` | 1 | N-back stimulus B |
| `NB3: C` | 2 | N-back stimulus C |
| `NB3: D` | 3 | N-back stimulus D |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset README confirms NB3 as a BIDS-defined N-back task variant. Stimulus events (A/B/C/D) provide 4-class classification matching NB1 for cross-load comparison. Source: https://openneuro.org/datasets/ds004350
- **Kernel Notes**: Same parameters as NB1 for consistency across N-back levels. The 3-back level increases working memory load, allowing comparison of load-dependent neural signatures. Excludes reaction time markers (NB3: rt) due to variable timing.

### Classical Task 3: Local-Global Hierarchical Stimulus Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = ["LG: largeHSmallH", "LG: largeHSmallT", "LG: largeTSmallH", "LG: largeTSmallT"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `LG: largeHSmallH` | 0 | Congruent: Large H and Small H |
| `LG: largeHSmallT` | 1 | Incongruent: Large H and Small T |
| `LG: largeTSmallH` | 2 | Incongruent: Large T and Small H |
| `LG: largeTSmallT` | 3 | Congruent: Large T and Small T |

- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset README confirms LG as a BIDS-defined Local-Global hierarchical stimulus task. Four conditions support congruency classification (congruent vs incongruent) or 4-class stimulus classification. Source: https://openneuro.org/datasets/ds004350
- **Kernel Notes**: Epoch on stimulus onset captures early congruency processing (N400 component expected ~300-600ms). Excludes response events (LG: responseLargeH/T, responseSmallH/T) due to variable RT and participant-dependent timing. Extended tmax=2.0s accommodates hierarchical processing window.

### Normal Task 1: SART Target Detection (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["SART: target", "SART: nontarget"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `SART: target` | 1 | Target stimulus (requires inhibition) |
| `SART: nontarget` | 0 | Non-target stimulus (go response) |

- **Evidence**: Paradigm described in dataset documentation as Sustained Attention to Response Task. Target/nontarget markers present in event structure with clear class imbalance (~1500 target vs ~12000 nontarget). Source: https://openneuro.org/datasets/ds004350
- **Kernel Notes**: Expected class imbalance reflects SART design (rare targets, frequent nontargets). Excludes SART:rt markers due to variable timing. Task-specific event prefixes required; generic event_# codes should not be used.