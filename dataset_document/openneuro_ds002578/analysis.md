# Visual Oddball Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2004/2021 | **URL**: https://openneuro.org/datasets/ds002578
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz | **Manual Review**: Jun Li

## Paradigm

A continuous visual oddball / selective-attention task recorded with 256-channel BioSemi EEG. Five empty squares were presented continuously on screen, with participants instructed to attend to one designated location and press a mouse button whenever a white disk appeared at that attended location. Event codes encode both the attended position and the cued (stimulus) position, allowing separation of target oddballs (attended location = stimulus location) from non-target distractors. The dataset contains only 2 completed files and represents a very limited subset of the original study data.

## File Scan Result

> **Kernel SHA256**: `89aaab696910b7caca856bbec641e222da1e8595c2a1c6209cb4a7ceef402a07`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `203` | 1 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `217` | 2 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `237` | 1 | admin | raw | System marker: unknown function (spurious event removed during preprocessing) |
| `31` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 1 (distractor, expected) |
| `33` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 3 (target, unexpected oddball) |
| `34` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 4 (distractor, expected) |
| `35` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 3 highlighted/cued, disc in box 5 (distractor, expected) |
| `41` | 238 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 1 (distractor, expected) |
| `42` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 2 (distractor, expected) |
| `43` | 240 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 3 (distractor, expected) |
| `44` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 4 (target, unexpected oddball) |
| `45` | 239 | event | raw | Experimental stimulus onset: five rectangular boxes, box 4 highlighted/cued, disc in box 5 (distractor, expected) |
| `Picture` | 5939 | event | raw | Experimental stimulus onset: drawing of five rectangular boxes with highlighted cue box and disc |
| `Response` | 1202 | event | raw | Participant response: keyboard key press |
| `boundary` | 58 | admin | raw | Trial phase onset: pause/discontinuous segment boundary |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: visual oddball target vs distractor
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`31`, `33`, `34`, `35`, `41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `33` | 1 | target: attend-3 cue-3, disc in cued box (unexpected oddball) |
  | `44` | 1 | target: attend-4 cue-4, disc in cued box (unexpected oddball) |
  | `31` | 0 | distractor: attend-3 cue-3, disc in box 1 (expected) |
  | `34` | 0 | distractor: attend-3 cue-3, disc in box 4 (expected) |
  | `35` | 0 | distractor: attend-3 cue-3, disc in box 5 (expected) |
  | `41` | 0 | distractor: attend-4 cue-4, disc in box 1 (expected) |
  | `42` | 0 | distractor: attend-4 cue-4, disc in box 2 (expected) |
  | `43` | 0 | distractor: attend-4 cue-4, disc in box 3 (expected) |
  | `45` | 0 | distractor: attend-4 cue-4, disc in box 5 (expected) |
- **Evidence**:
  - 10.1523/jneurosci.3477.07.2007 — Classical visual oddball task with target (attended=cued location) vs distractor (attended≠cued location). Two target events exist: 33 (attend-3 cue-3) and 44 (attend-4 cue-4). Seven distractor events exist: 31, 34, 35, 41, 42, 43, 45. Total target trials: 479; distractor trials: 1675. Epoch window tmin=-1s to tmax=2s follows the published target-locked analysis window.
- **Notes**: All nine numeric event codes (31-35, 41-45) appear in the exported EEG files as annotations, confirmed by events.tsv counts and events.json definitions. The two target conditions (33, 44) are merged to y=1; all seven distractor conditions (31, 34, 35, 41, 42, 43, 45) are merged to y=0, reflecting the core oddball manipulation of target vs non-target discrimination.

### Potential Task 1: visual oddball 9-class position decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`31`, `33`, `34`, `35`, `41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `31` | 0 | Distractor: box 3 cued, disc in position 1 |
  | `33` | 1 | Target: box 3 cued, disc in position 3 (oddball) |
  | `34` | 2 | Distractor: box 3 cued, disc in position 4 |
  | `35` | 3 | Distractor: box 3 cued, disc in position 5 |
  | `41` | 4 | Distractor: box 4 cued, disc in position 1 |
  | `42` | 5 | Distractor: box 4 cued, disc in position 2 |
  | `43` | 6 | Distractor: box 4 cued, disc in position 3 |
  | `44` | 7 | Target: box 4 cued, disc in position 4 (oddball) |
  | `45` | 8 | Distractor: box 4 cued, disc in position 5 |
- **Evidence**:
  - events.json sidecar (sub-001, sub-002) — HED tags and level descriptions confirm 31-35 and 41-45 encode box×disc position combinations; target positions (33, 44) are oddball conditions where disc appears in cued box
  - README — describes selective attention visual oddball paradigm with five rectangular boxes and target detection task
  - events.tsv counts — confirm event IDs 31, 33, 34, 35, 41, 42, 43, 44, 45 all appear in the released data
- **Notes**: 9-class classification tests spatial decodability beyond binary target/distractor. The 9 conditions are near-balanced (~238-240 trials each). y values assigned by sorting event IDs numerically: 31→0, 33→1, 34→2, 35→3, 41→4, 42→5, 43→6, 44→7, 45→8. Note that position 2 in box 3 (code 32) is absent from actual data exports. Epoch window follows the published oddball target-locked analysis style rather than a parameter explicitly specified in the BIDS metadata.

### Potential Task 2: Visual Oddball Target vs Distractor (Attend-3 Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`31`, `33`, `34`, `35`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `33` | 1 | Target: box 3 highlighted/cued, disc in box 3 (unexpected oddball) |
  | `31` | 0 | Distractor: box 3 highlighted/cued, disc in box 1 (expected) |
  | `34` | 0 | Distractor: box 3 highlighted/cued, disc in box 4 (expected) |
  | `35` | 0 | Distractor: box 3 highlighted/cued, disc in box 5 (expected) |
- **Evidence**:
  - - events.json sidecar — confirms event 33 is the attend-3 target oddball and events 31, 34, 35 are attend-3 distractors
  - - README / EEG sidecar — describe the selective-attention oddball task and target detection rule
- **Notes**: Restricted to attend-3 condition where box 3 is always highlighted/cued. Target (event 33, disc in cued box 3) is contrasted against three distractor types (events 31, 34, 35) where the disc appears in non-cued boxes 1, 4, or 5. All distractor events are merged to y=0 to test within-condition oddball detection (target probability ~25% within attend-3 trials). Epoch window matches classical oddball stimulus-locked analysis; parameters inferred from standard visual oddball ERP literature as no explicit epoch window was specified in dataset documentation.

### Potential Task 3: Visual Oddball Target vs Distractor (Attend-4 Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`41`, `42`, `43`, `44`, `45`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `44` | 1 | target (attend-4, disc in cued box 4) |
  | `41` | 0 | distractor (attend-4, disc in box 1) |
  | `42` | 0 | distractor (attend-4, disc in box 2) |
  | `43` | 0 | distractor (attend-4, disc in box 3) |
  | `45` | 0 | distractor (attend-4, disc in box 5) |
- **Evidence**:
  - - events.json sidecar — confirms event 44 is the attend-4 target oddball and events 41, 42, 43, 45 are attend-4 distractors
  - - README / EEG sidecar — describe the selective-attention oddball task and target detection rule
- **Notes**: Restricted to attend-4 condition only (cue box 4 highlighted). Target event 44 (disc in cued box 4, unexpected oddball) vs distractor events 41-43,45 (disc in non-cued boxes 1-3,5, expected). Controls for attended location to test within-condition oddball effects. All five event codes confirmed in EEG file annotations and events.json sidecar definitions. Epoch window inferred from classical oddball timing (-1 to +2 s relative to stimulus onset).

### Potential Task 4: Gender Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — N=2 subjects with gender field: 1 female (sub-001), 1 male (sub-002)
- **Notes**: Segment-based approach required since no discriminating event structure exists for this subject-level label. 10-second non-overlapping segments at 256 Hz yield 2560 samples per segment. Only 2 subjects are available, with 1 subject per class; this is an extremely weak proof-of-concept subject-trait decoding task and will likely be filtered out downstream.

### Potential Task 5: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_age` | no mapping |
- **Evidence**:
  - participants.tsv — age column present for both subjects with value 30
- **Notes**: Archetype B3: age is a native participants.tsv field (no kernel derivation needed). Segmentation-based epoching creates 10-second non-overlapping windows from continuous EEG; each segment inherits the subject's age as the regression target. However, both subjects are age 30, so this task has zero label variance and is effectively non-viable.

## Data Quality Notes

- Extremely small sample size: only 2 completed files/subjects available, severely limiting statistical power and generalizability.
- Missing device metadata in Info table; BioSemi 256-channel system inferred from dataset documentation and channel count.
- Age field shows zero variance (both subjects age 30), making age regression task non-viable; downstream pipeline should filter this task out.
- Gender classification task has only 1 sample per class (N=2 total), which is insufficient for meaningful machine learning.
- Event code 32 (distractor: attend-3 cue-2) is documented in paradigm description but absent from actual data exports; this appears to be a planned but unused condition.
- Spurious system markers (203, 217, 237) present in raw data but marked as removed during preprocessing; these should be excluded from analysis.
- High number of `Picture` events (5939) relative to trial-coded events (~2394) suggests screen refresh or frame-level triggers were logged, requiring careful event selection for epoching.
- `boundary` events (58) indicate discontinuous segments or pauses in recording; users should verify whether these affect trial integrity.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
