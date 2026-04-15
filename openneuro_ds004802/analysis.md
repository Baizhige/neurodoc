# Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot)

**Dataset**: `openneuro_ds004802` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004802
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 79 | **Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

A pilot EEG study investigating the neural underpinnings of loneliness by contrasting social hypersensitivity (amplified neural responses to social stimuli) and hyperalertness (heightened attention to potential social threats). Participants viewed emotional face stimuli in a roving oddball paradigm while EEG was recorded. Trigger codes encode stimulus type, valence, and repetition position (novel vs familiar). Code 20 dominates the event structure (49,566 total) and likely represents a high-frequency refresh or fixation signal.

## File Scan Result

> **Kernel SHA256**: `d898898109904120c26b0377217a76566186b703fadc598e1cc02c42afba4d01`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_100` | 5 | event | raw |  |
| `event_101` | 2 | event | raw |  |
| `event_11` | 148 | event | raw |  |
| `event_111` | 4083 | event | raw |  |
| `event_12` | 184 | event | raw |  |
| `event_127` | 135 | event | raw |  |
| `event_13` | 257 | event | raw |  |
| `event_14` | 148 | event | raw |  |
| `event_15` | 110 | event | raw |  |
| `event_16` | 258 | event | raw |  |
| `event_17` | 74 | event | raw |  |
| `event_20` | 49566 | event | raw |  |
| `event_200` | 256 | event | raw |  |
| `event_21` | 2690 | event | raw |  |
| `event_22` | 2612 | event | raw |  |
| `event_23` | 2613 | event | raw |  |
| `event_24` | 2761 | event | raw |  |
| `event_25` | 2764 | event | raw |  |
| `event_254` | 8 | event | raw |  |
| `event_255` | 1 | event | raw |  |
| `event_26` | 1955 | event | raw |  |
| `event_27` | 919 | event | raw |  |
| `event_28` | 147 | event | raw |  |
| `event_30` | 18 | event | raw |  |
| `event_31` | 220 | event | raw |  |
| `event_32` | 73 | event | raw |  |
| `event_33` | 147 | event | raw |  |
| `event_34` | 74 | event | raw |  |
| `event_35` | 219 | event | raw |  |
| `event_36` | 110 | event | raw |  |
| `event_41` | 2125 | event | raw |  |
| `event_42` | 2277 | event | raw |  |
| `event_43` | 2205 | event | raw |  |
| `event_44` | 2276 | event | raw |  |
| `event_45` | 2136 | event | raw |  |
| `event_46` | 1614 | event | raw |  |
| `event_47` | 953 | event | raw |  |
| `event_48` | 255 | event | raw |  |
| `event_51` | 37 | event | raw |  |
| `event_52` | 74 | event | raw |  |
| `event_53` | 185 | event | raw |  |
| `event_54` | 185 | event | raw |  |
| `event_55` | 74 | event | raw |  |
| `event_56` | 111 | event | raw |  |
| `event_57` | 74 | event | raw |  |
| `event_61` | 2177 | event | raw |  |
| `event_62` | 2140 | event | raw |  |
| `event_63` | 2030 | event | raw |  |
| `event_64` | 2025 | event | raw |  |
| `event_65` | 2140 | event | raw |  |
| `event_65536` | 1 | event | raw |  |
| `event_65556` | 1 | event | raw |  |
| `event_65790` | 7 | event | raw |  |
| `event_66` | 1549 | event | raw |  |
| `event_67` | 699 | event | raw |  |
| `event_68` | 294 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Age data not available in dataset |
| `subject_sex` | partial (78/79) | N/A |
| `device` | missing | Recording device not documented |

## Tasks

### Classical Task 1: Loneliness Classification

**Task Type**: binary_classification | **Epoch Method**: epoch_by_event_hdf5 | **Label Route**: misc
| **Meta Level**: super

| Epoch Parameters | Value |
|-----------------|-------|
| tmin | -0.2 |
| tmax | 2.0 |
| alignment | onset |
| baseline | pre-stimulus |

| Target Definition |  |  |
|-------------------|------|-------------|
| Event | y | Meaning |
| 21-28 (faces) | 1 | Lonely group |
| 21-28 (faces) | 0 | Non-lonely group |
| 41-48 (faces) | 1 | Lonely group |
| 41-48 (faces) | 0 | Non-lonely group |

**Evidence**: DOI: 10.31219/osf.io/j5v9b

**Kernel Notes**: Roving oddball paradigm with emotional faces. Primary classification target: distinguish lonely vs non-lonely individuals based on neural responses to social stimuli. EPOCH_BY_EVENT_HDF5 with events 21-28 and 41-48 (primary stimulus clusters). Event 20 (fixation/refresh) excluded. Labels sourced from participant metadata at super level (external group assignment). Study design: n=36 pilot already completed for channel/time window identification; planned expansion to n=50 lonely + n=50 non-lonely.

---

### Normal Task 1: Stimulus Type Classification (Valence)

**Task Type**: classification | **Epoch Method**: epoch_by_event_hdf5 | **Label Route**: event
| **Meta Level**: raw

| Epoch Parameters | Value |
|-----------------|-------|
| tmin | -0.2 |
| tmax | 2.0 |
| alignment | onset |
| baseline | pre-stimulus |

| Target Definition |  |  |
|-------------------|------|------------------------------|
| Event | y | Meaning |
| 21 | angry_face | Angry emotional face stimulus |
| 22 | angry_face | Angry emotional face stimulus |
| 23 | happy_face | Happy emotional face stimulus |
| 24 | happy_face | Happy emotional face stimulus |
| 41 | angry_face | Angry emotional face stimulus (secondary set) |
| 42 | angry_face | Angry emotional face stimulus (secondary set) |
| 43 | happy_face | Happy emotional face stimulus (secondary set) |
| 44 | happy_face | Happy emotional face stimulus (secondary set) |

**Evidence**: DOI: 10.31219/osf.io/j5v9b (pre-registration: "stimulus type (angry/happy)")

**Kernel Notes**: Emotional valence discrimination task. Event IDs 21-24 and 41-44 form paired stimulus sets (angry/happy) based on roving oddball structure. Primary ERP targets: N170 (120-170ms) for face processing, N400 (360-470ms) for semantic integration, LPP (480-600ms) for emotional processing. Angry faces represent social threat stimuli relevant to hyperalertness hypothesis.

---

### Normal Task 2: Novelty/Repetition Effect

**Task Type**: classification | **Epoch Method**: epoch_by_event_hdf5 | **Label Route**: event
| **Meta Level**: raw

| Epoch Parameters | Value |
|-----------------|-------|
| tmin | -0.2 |
| tmax | 2.0 |
| alignment | onset |
| baseline | pre-stimulus |

| Target Definition |  |  |
|-------------------|------|--------------------------|
| Event | y | Meaning |
| 21-28 | novel | First presentation (novel stimulus) |
| 21-28 | familiar | Fifth presentation (habituated stimulus) |
| 41-48 | novel | First presentation (novel stimulus) |
| 41-48 | familiar | Fifth presentation (habituated stimulus) |
| 61-68 | novel | First presentation (response condition) |
| 61-68 | familiar | Fifth presentation (response condition) |

**Evidence**: DOI: 10.31219/osf.io/j5v9b (pre-registration: "novelty (first vs fifth presentation)")

**Kernel Notes**: Roving oddball novelty effect: compare neural responses to first vs fifth presentation of identical stimuli. Key for distinguishing hypersensitivity (enhanced initial response amplitude) from hyperalertness (slower habituation). Novelty effect analysis targets N400 and LPP components. Events 21-28, 41-48, 61-68 each represent independent stimulus sets with repetition structure.

---

### Potential Task 1: Hyperalertness vs Hypersensitivity Mechanism Classification

**Task Type**: classification | **Epoch Method**: epoch_by_event_hdf5 | **Label Route**: event
| **Meta Level**: raw

| Epoch Parameters | Value |
|-----------------|-------|
| tmin | -0.2 |
| tmax | 2.0 |
| alignment | onset |
| baseline | pre-stimulus |

| Target Definition |  |  |
|-------------------|------|----------------------------------|
| Event | y | Meaning |
| 21-28 | hypersensitivity | Hyper-sensitivity related trials |
| 61-68 | hyperalertness | Hyper-alertness related trials |

**Evidence**: DOI: 10.31219/osf.io/j5v9b (conceptual support from pre-registration; primary stimuli vs response condition variants)

**Kernel Notes**: Core research question: distinguish neural signatures of hypersensitivity (amplified neural responses to social stimuli at first presentation) vs hyperalertness (heightened sustained attention to potential social threats, evidenced by slower habituation). Compare event 21-28 (primary stimuli) vs 61-68 (response condition variants). Requires longitudinal epoch analysis across stimulus repetitions to identify which mechanism better explains group differences in lonely individuals.

---

### Potential Task 2: Response-Related Processing

**Task Type**: classification | **Epoch Method**: epoch_by_event_hdf5 | **Label Route**: event
| **Meta Level**: raw

| Epoch Parameters | Value |
|-----------------|-------|
| tmin | -0.5 |
| tmax | 1.0 |
| alignment | onset |
| baseline | pre-stimulus |

| Target Definition |  |  |
|-------------------|------|--------------------------------------|
| Event | y | Meaning |
| 111 | response | Behavioral response event |

**Evidence**: DOI: 10.31219/osf.io/j5v9b (paradigm mentions response conditions; Event 111 count ~4k suggests response-locked trials)

**Kernel Notes**: Event 111 (~4k occurrences) likely encodes behavioral responses. Response-locked epochs (tmin=-0.5, tmax=1.0) capture response-locked negativity and motor-related potentials associated with social threat processing. Extended pre-stimulus window needed to capture preparation-related activity. Compare response patterns between lonely/non-lonely groups for angry vs happy faces.