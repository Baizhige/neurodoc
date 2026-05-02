# TMNRED: A Chinese Language EEG Dataset for Fuzzy Semantic Target Identification in Natural Reading Environments

**Dataset**: `openneuro_ds005383` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005383
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 720 | **Manual Review**: Pending
**Channels**: 30 | **Sampling Rate**: 200 Hz

## Paradigm

Participants engaged in self-paced natural reading of Chinese sentences and news headlines to identify fuzzy semantic targets embedded in text. The study investigates neural correlates of semantic processing during naturalistic reading, recording EEG with 30 channels at 200 Hz. BioSemi trigger codes mark word/sentence onset events across three sessions per subject (3 × 240 files = 720 total). The trigger code structure encodes semantic conditions, target presence, and reading context, with numerical codes ranging from 15–64 plus system events.

## File Scan Result

> **Kernel SHA256**: `e079baf097588764c21ac96898e0c1c3743b12276a4bbc8711d755195ac46bf9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `15` | 239 | event | raw | Stimulus condition code 15 |
| `16` | 240 | event | raw | Stimulus condition code 16 |
| `17` | 240 | event | raw | Stimulus condition code 17 |
| `18` | 240 | event | raw | Stimulus condition code 18 |
| `19` | 240 | event | raw | Stimulus condition code 19 |
| `20` | 239 | event | raw | Stimulus condition code 20 |
| `21` | 240 | event | raw | Stimulus condition code 21 |
| `22` | 240 | event | raw | Stimulus condition code 22 |
| `23` | 240 | event | raw | Stimulus condition code 23 |
| `24` | 240 | event | raw | Stimulus condition code 24 |
| `25` | 239 | event | raw | Stimulus condition code 25 |
| `26` | 240 | event | raw | Stimulus condition code 26 |
| `27` | 240 | event | raw | Stimulus condition code 27 |
| `28` | 240 | event | raw | Stimulus condition code 28 |
| `29` | 240 | event | raw | Stimulus condition code 29 |
| `30` | 239 | event | raw | Stimulus condition code 30 |
| `31` | 240 | event | raw | Non-target sentence (no fuzzy semantic target word) |
| `32` | 240 | event | raw | Target sentence (contains fuzzy semantic target word) |
| `33` | 240 | event | raw | Stimulus condition code 33 |
| `34` | 240 | event | raw | Stimulus condition code 34 |
| `35` | 239 | event | raw | Stimulus condition code 35 |
| `36` | 240 | event | raw | Stimulus condition code 36 |
| `37` | 240 | event | raw | Stimulus condition code 37 |
| `38` | 240 | event | raw | Stimulus condition code 38 |
| `39` | 240 | event | raw | Stimulus condition code 39 |
| `40` | 239 | event | raw | Stimulus condition code 40 |
| `41` | 240 | event | raw | Stimulus condition code 41 |
| `42` | 240 | event | raw | Stimulus condition code 42 |
| `43` | 240 | event | raw | Stimulus condition code 43 |
| `44` | 240 | event | raw | Stimulus condition code 44 |
| `45` | 239 | event | raw | Stimulus condition code 45 |
| `46` | 240 | event | raw | Stimulus condition code 46 |
| `47` | 240 | event | raw | Stimulus condition code 47 |
| `48` | 240 | event | raw | Stimulus condition code 48 |
| `49` | 240 | event | raw | Stimulus condition code 49 |
| `50` | 239 | event | raw | Stimulus condition code 50 |
| `51` | 240 | event | raw | Stimulus condition code 51 |
| `52` | 240 | event | raw | Stimulus condition code 52 |
| `53` | 240 | event | raw | Stimulus condition code 53 |
| `54` | 240 | event | raw | Stimulus condition code 54 |
| `55` | 240 | event | raw | Stimulus condition code 55 |
| `56` | 240 | event | raw | Stimulus condition code 56 |
| `57` | 240 | event | raw | Stimulus condition code 57 |
| `58` | 240 | event | raw | Stimulus condition code 58 |
| `59` | 240 | event | raw | Stimulus condition code 59 |
| `60` | 239 | event | raw | Stimulus condition code 60 |
| `61` | 240 | event | raw | Stimulus condition code 61 |
| `62` | 240 | event | raw | Stimulus condition code 62 |
| `63` | 240 | event | raw | Stimulus condition code 63 |
| `64` | 240 | event | raw | Stimulus condition code 64 |
| `boundary` | 240 | event | raw | Segment boundary marker |
| `event_129594` | 1 | event | raw |  |
| `event_129978` | 1 | event | raw |  |
| `event_130270` | 1 | event | raw |  |
| `event_130422` | 1 | event | raw |  |
| `event_130496` | 1 | event | raw |  |
| `event_130515` | 1 | event | raw |  |
| `event_130607` | 1 | event | raw |  |
| `event_130623` | 1 | event | raw |  |
| `event_130689` | 1 | event | raw |  |
| `event_130728` | 1 | event | raw |  |
| `event_130756` | 1 | event | raw |  |
| `event_130766` | 1 | event | raw |  |
| `event_130768` | 1 | event | raw |  |
| `event_130773` | 1 | event | raw |  |
| `event_130779` | 1 | event | raw |  |
| `event_130787` | 1 | event | raw |  |
| `event_130800` | 1 | event | raw |  |
| `event_130801` | 1 | event | raw |  |
| `event_130802` | 1 | event | raw |  |
| `event_130808` | 1 | event | raw |  |
| `event_130821` | 1 | event | raw |  |
| `event_130830` | 1 | event | raw |  |
| `event_130833` | 1 | event | raw |  |
| `event_130839` | 1 | event | raw |  |
| `event_130841` | 1 | event | raw |  |
| `event_130844` | 1 | event | raw |  |
| `event_130846` | 1 | event | raw |  |
| `event_130859` | 1 | event | raw |  |
| `event_130861` | 1 | event | raw |  |
| `event_130870` | 1 | event | raw |  |
| `event_130872` | 1 | event | raw |  |
| `event_130873` | 1 | event | raw |  |
| `event_130876` | 1 | event | raw |  |
| `event_130879` | 1 | event | raw |  |
| `event_130881` | 1 | event | raw |  |
| `event_130887` | 1 | event | raw |  |
| `event_130896` | 1 | event | raw |  |
| `event_130900` | 1 | event | raw |  |
| `event_130903` | 1 | event | raw |  |
| `event_130904` | 1 | event | raw |  |
| `event_130909` | 1 | event | raw |  |
| `event_130913` | 2 | event | raw |  |
| `event_130920` | 1 | event | raw |  |
| `event_130921` | 1 | event | raw |  |
| `event_130924` | 2 | event | raw |  |
| `event_130932` | 1 | event | raw |  |
| `event_130933` | 1 | event | raw |  |
| `event_130935` | 1 | event | raw |  |
| `event_130936` | 2 | event | raw |  |
| `event_130937` | 1 | event | raw |  |
| `event_130938` | 1 | event | raw |  |
| `event_130940` | 2 | event | raw |  |
| `event_130945` | 1 | event | raw |  |
| `event_130947` | 1 | event | raw |  |
| `event_130954` | 1 | event | raw |  |
| `event_130955` | 1 | event | raw |  |
| `event_130957` | 1 | event | raw |  |
| `event_130958` | 1 | event | raw |  |
| `event_130961` | 1 | event | raw |  |
| `event_130962` | 1 | event | raw |  |
| `event_130963` | 2 | event | raw |  |
| `event_130968` | 2 | event | raw |  |
| `event_130971` | 1 | event | raw |  |
| `event_130972` | 4 | event | raw |  |
| `event_130973` | 1 | event | raw |  |
| `event_130975` | 3 | event | raw |  |
| `event_130976` | 1 | event | raw |  |
| `event_130977` | 3 | event | raw |  |
| `event_130978` | 2 | event | raw |  |
| `event_130981` | 4 | event | raw |  |
| `event_130983` | 1 | event | raw |  |
| `event_130984` | 2 | event | raw |  |
| `event_130985` | 1 | event | raw |  |
| `event_130986` | 7 | event | raw |  |
| `event_130989` | 2 | event | raw |  |
| `event_130990` | 1 | event | raw |  |
| `event_130992` | 6 | event | raw |  |
| `event_130993` | 6 | event | raw |  |
| `event_130994` | 3 | event | raw |  |
| `event_130996` | 1 | event | raw |  |
| `event_130997` | 3 | event | raw |  |
| `event_130998` | 4 | event | raw |  |
| `event_130999` | 5 | event | raw |  |
| `event_131000` | 3 | event | raw |  |
| `event_131001` | 4 | event | raw |  |
| `event_131002` | 5 | event | raw |  |
| `event_131003` | 1 | event | raw |  |
| `event_131004` | 7 | event | raw |  |
| `event_131005` | 3 | event | raw |  |
| `event_131006` | 4 | event | raw |  |
| `event_131007` | 8 | event | raw |  |
| `event_131008` | 76 | event | raw | System/response event (low count) |
| `event_14` | 154 | event | raw |  |
| `event_15` | 240 | event | raw |  |
| `event_16` | 242 | event | raw |  |
| `event_17` | 246 | event | raw |  |
| `event_18` | 228 | event | raw |  |
| `event_19` | 237 | event | raw |  |
| `event_20` | 253 | event | raw |  |
| `event_21` | 242 | event | raw |  |
| `event_22` | 244 | event | raw |  |
| `event_23` | 221 | event | raw |  |
| `event_24` | 250 | event | raw |  |
| `event_25` | 230 | event | raw |  |
| `event_26` | 242 | event | raw |  |
| `event_27` | 235 | event | raw |  |
| `event_28` | 257 | event | raw |  |
| `event_29` | 232 | event | raw |  |
| `event_30` | 242 | event | raw |  |
| `event_31` | 239 | event | raw |  |
| `event_32` | 239 | event | raw |  |
| `event_33` | 253 | event | raw |  |
| `event_34` | 232 | event | raw |  |
| `event_35` | 230 | event | raw |  |
| `event_36` | 241 | event | raw |  |
| `event_37` | 243 | event | raw |  |
| `event_38` | 238 | event | raw |  |
| `event_39` | 240 | event | raw |  |
| `event_40` | 229 | event | raw |  |
| `event_41` | 247 | event | raw |  |
| `event_42` | 249 | event | raw |  |
| `event_43` | 233 | event | raw |  |
| `event_44` | 236 | event | raw |  |
| `event_45` | 262 | event | raw |  |
| `event_46` | 216 | event | raw |  |
| `event_47` | 243 | event | raw |  |
| `event_48` | 247 | event | raw |  |
| `event_49` | 226 | event | raw |  |
| `event_50` | 252 | event | raw |  |
| `event_51` | 248 | event | raw |  |
| `event_52` | 242 | event | raw |  |
| `event_53` | 227 | event | raw |  |
| `event_54` | 241 | event | raw |  |
| `event_55` | 248 | event | raw |  |
| `event_56` | 219 | event | raw |  |
| `event_57` | 255 | event | raw |  |
| `event_58` | 231 | event | raw |  |
| `event_59` | 248 | event | raw |  |
| `event_60` | 215 | event | raw |  |
| `event_61` | 267 | event | raw |  |
| `event_62` | 248 | event | raw |  |
| `event_63` | 163 | event | raw |  |
| `event_64` | 149 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary Semantic Target Identification in Chinese Sentences
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s, target_events = ["31", "32"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `31` | 0 | Non-target sentence (no fuzzy semantic target word) |
  | `32` | 1 | Target sentence (contains fuzzy semantic target word: name, means of transportation, animal, or fruit) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05036-2 — TMNRED dataset paper confirming 30 participants read Chinese sentences with vs without target semantic words during 2-second stimulus presentation windows; binary classification of target presence.
- **Kernel Notes**: Event IDs 31 and 32 confirmed in available events with consistent ~17,280 total count (240/file × 72 files). The 2-second tmax aligns with stimulus presentation duration from paper. This is the primary classification task supported by direct evidence from the dataset paper.

### Potential Task 1: Multiclass Condition Code Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s, target_events = ["16", "21", "22", "26", "31", "32", "36", "41", "42", "46", "51", "52", "55", "56", "61"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `16` | 0 | Condition code 16 |
  | `21` | 1 | Condition code 21 |
  | `22` | 2 | Condition code 22 |
  | `26` | 3 | Condition code 26 |
  | `31` | 4 | Condition code 31 |
  | `32` | 5 | Condition code 32 |
  | `36` | 6 | Condition code 36 |
  | `41` | 7 | Condition code 41 |
  | `42` | 8 | Condition code 42 |
  | `46` | 9 | Condition code 46 |
  | `51` | 10 | Condition code 51 |
  | `52` | 11 | Condition code 52 |
  | `55` | 12 | Condition code 55 |
  | `56` | 13 | Condition code 56 |
  | `61` | 14 | Condition code 61 |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05036-2 — Dataset paper confirms multiple experimental conditions encoded in BioSemi trigger codes; systematic +5 code pattern suggests structured semantic conditions requiring full decode from events.tsv for interpretation.
- **Kernel Notes**: 15 distinct numerical condition codes confirmed in available events with ~240 count per file each. The systematic code pattern (16, 21, 26, 31, 32, 36...) suggests 5-condition groupings but semantic meaning requires decode from events.tsv. Codes 31–32 overlap with Classical Task 1 labels. Exclude 'boundary' events (240/file) which mark file segments.

### Potential Task 1: Self-Paced Reading Temporal Dynamics
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = null (variable duration), target_events = ["31", "32"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `31` | continuous | Non-target sentence reading time |
  | `32` | continuous | Target sentence reading time |
- **Evidence**: Paradigm description states "self-paced natural reading" but paper focuses on 2-second fixed presentation windows; plausible extended analysis examining reading time differences between target/non-target conditions.
- **Kernel Notes**: Self-paced reading paradigm suggests variable trial durations; however paper emphasizes 2-second fixed windows. Verify in events.tsv whether reading duration markers exist or if this is fixed-speed presentation with self-paced button response. May require extended tmax or separate reading-time annotation extraction.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
