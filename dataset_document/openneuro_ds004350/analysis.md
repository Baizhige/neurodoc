# Executive Functioning Study for Assessing the Effect of Neurofeedback

**Dataset**: `openneuro_ds004350` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004350
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 479 | **Channels**: 64 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Participants performed a battery of executive function tasks including visual N-back working memory tasks (NB1/NB2/NB3 with stimuli A/B/C/D), a Sustained Attention to Response Task (SART with target/nontarget conditions), and a Local-Global hierarchical stimulus task (largeH/largeT x smallH/smallT). The study assessed the effect of neurofeedback training on executive function performance using 64-channel EEG recordings at 256 Hz.

## File Scan Result

> **Kernel SHA256**: `501d793b25ca88ef80c9b8a931334af12c80b53bc63adbc68e9732530e5e2b25`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LG: largeHSmallH` | 9123 | event | raw | Stimulus onset: large H composed of small H letters (congruent) |
| `LG: largeHSmallT` | 9120 | event | raw | Stimulus onset: large H composed of small T letters (incongruent) |
| `LG: largeTSmallH` | 9130 | event | raw | Stimulus onset: large T composed of small H letters (incongruent) |
| `LG: largeTSmallT` | 9134 | event | raw | Stimulus onset: large T composed of small T letters (congruent) |
| `LG: responseLargeH` | 9035 | event | raw | Response: participant identified large letter as H |
| `LG: responseLargeT` | 9272 | event | raw | Response: participant identified large letter as T |
| `LG: responseSmallH` | 9230 | event | raw | Response: participant identified small letter as H |
| `LG: responseSmallT` | 8957 | event | raw | Response: participant identified small letter as T |
| `NB1: 12` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB1 |
| `NB1: 5` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB1 |
| `NB1: 6` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB1 |
| `NB1: 9` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB1 |
| `NB1: A` | 3341 | event | raw | Stimulus onset: letter A presented |
| `NB1: B` | 3348 | event | raw | Stimulus onset: letter B presented |
| `NB1: C` | 3408 | event | raw | Stimulus onset: letter C presented |
| `NB1: D` | 3251 | event | raw | Stimulus onset: letter D presented |
| `NB1: rt` | 3323 | event | raw | Response onset: participant button press (spacebar) |
| `NB2: 10` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB2 |
| `NB2: 11` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB2 |
| `NB2: 255` | 1 | admin | raw | System marker: likely trigger reset or synchronization code |
| `NB2: 5` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB2 |
| `NB2: 6` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB2 |
| `NB2: 9` | 1 | event | raw | Unclear: numeric trigger code with single occurrence in NB2 |
| `NB2: A` | 3334 | event | raw | Stimulus onset: letter A presented |
| `NB2: B` | 3363 | event | raw | Stimulus onset: letter B presented |
| `NB2: C` | 3316 | event | raw | Stimulus onset: letter C presented |
| `NB2: D` | 3325 | event | raw | Stimulus onset: letter D presented |
| `NB2: rt` | 2827 | event | raw | Response onset: participant button press (spacebar) |
| `NB3: A` | 3289 | event | raw | Stimulus onset: letter A presented |
| `NB3: B` | 3363 | event | raw | Stimulus onset: letter B presented |
| `NB3: C` | 3257 | event | raw | Stimulus onset: letter C presented |
| `NB3: D` | 3410 | event | raw | Stimulus onset: letter D presented |
| `NB3: rt` | 2405 | event | raw | Response onset: participant button press (spacebar) |
| `SART: nontarget` | 11833 | event | raw | Stimulus onset: non-target digit (all digits except 3), requires spacebar response |
| `SART: rt` | 12092 | event | raw | Response onset: participant button press (spacebar) to nontarget digit |
| `SART: target` | 1499 | event | raw | Stimulus onset: target digit 3, requires withholding response |
| `event_1` | 22536 | event | raw | Raw trigger code: bit 1 = large H made of small H (LG task stimulus) |
| `event_10` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger or error |
| `event_11` | 1 | event | raw | Unclear: raw trigger code with single occurrence, possibly combined trigger or error |
| `event_12` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger or error |
| `event_128` | 9622 | event | raw | Raw trigger code: bit 8 = response to large T (LG task response) |
| `event_129` | 9482 | event | raw | Raw trigger code: combined bits 1+8 = large H small H stimulus + response to large T, possibly overlapping triggers |
| `event_131` | 1 | event | raw | Unclear: raw trigger code with single occurrence, possibly combined trigger |
| `event_132` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger |
| `event_133` | 1 | event | raw | Unclear: raw trigger code with single occurrence, possibly combined trigger |
| `event_136` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 4+8+128=136? inconsistent) |
| `event_145` | 5 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger |
| `event_16` | 9598 | event | raw | Raw trigger code: bit 5 = response to small H (LG task response) |
| `event_161` | 2 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger |
| `event_18` | 4 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 2+16=18) |
| `event_193` | 4 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger |
| `event_2` | 21099 | event | raw | Raw trigger code: bit 2 = large H made of small T (LG task stimulus) |
| `event_20` | 9 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 4+16=20) |
| `event_24` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 4+8+16? inconsistent with 24=8+16) |
| `event_255` | 1 | admin | raw | System marker: all bits set, likely trigger reset or synchronization code |
| `event_3` | 9924 | event | raw | Raw trigger code: combined bits 1+2 = large H small H + large H small T stimuli simultaneously, likely overlapping triggers |
| `event_32` | 9309 | event | raw | Raw trigger code: bit 6 = response to small T (LG task response) |
| `event_34` | 9 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 2+32=34) |
| `event_36` | 1 | event | raw | Unclear: raw trigger code with single occurrence, possibly combined trigger (bits 4+32=36) |
| `event_4` | 19408 | event | raw | Raw trigger code: bit 3 = large T made of small H (LG task stimulus) |
| `event_40` | 4 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 8+32=40) |
| `event_5` | 2 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 1+4=5) |
| `event_6` | 3 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 2+4=6) |
| `event_64` | 9403 | event | raw | Raw trigger code: bit 7 = response to large H (LG task response) |
| `event_65536` | 9 | admin | raw | System marker: boundary or discontinuity indicator (2^16, typical Biosemi overflow/reset code) |
| `event_65537` | 1 | admin | raw | System marker: boundary with bit 1 set, possibly status code with overflow indicator |
| `event_65539` | 1 | admin | raw | System marker: boundary with bits 1+2 set, possibly status code with overflow indicator |
| `event_65600` | 2 | admin | raw | System marker: boundary with bits 6+7+8 set (64+128+65536=65600? check: 65536+64=65600), status code with overflow |
| `event_65665` | 2 | admin | raw | System marker: boundary with bits 1+7+8 set (1+64+128+65536=65729? inconsistent), status code with overflow |
| `event_66` | 4 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 2+64=66) |
| `event_68` | 1 | event | raw | Unclear: raw trigger code with single occurrence, possibly combined trigger (bits 4+64=68) |
| `event_72` | 2 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 8+64=72) |
| `event_8` | 30903 | event | raw | Raw trigger code: bit 4 = large T made of small T (LG task stimulus) |
| `event_9` | 8 | event | raw | Unclear: raw trigger code with minimal occurrences, possibly combined trigger (bits 1+8=9) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: N-back stimulus classification (1-back)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`NB1: A`, `NB1: B`, `NB1: C`, `NB1: D`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `NB1: A` | 0 | Stimulus onset: letter A presented |
  | `NB1: B` | 1 | Stimulus onset: letter B presented |
  | `NB1: C` | 2 | Stimulus onset: letter C presented |
  | `NB1: D` | 3 | Stimulus onset: letter D presented |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Original study describing N-back working memory paradigm with letters A-D as stimuli and 1-back/2-back/3-back conditions; stimulus-locked EEG analysis
  - 10.1016/j.neuroimage.2026.121820 — Reference explicitly describing stimulus-locked epochs around n-back stimuli with letter identity as condition label for 4-class classification
  - README — Confirms 1-back condition with letters A, B, C, D presented for 1s with 500ms fixation; target is letter identical to immediately preceding trial
  - events.tsv (sub-001_ses-post_task-NB1_events.tsv) — Confirmed event values `A`, `B`, `C`, `D` with stimulus column documenting letter identity
- **Notes**: All four event IDs (`NB1: A`, `NB1: B`, `NB1: C`, `NB1: D`) are confirmed stimulus onset markers for the 1-back condition. Epoch window (-0.2 to 1.5s) covers pre-stimulus baseline and full stimulus duration plus response window per README (stimulus 1s, fixation 500ms, 1500ms response deadline). Classes are well-balanced with ~3300 occurrences each.

---

### Classical Task 2: N-back stimulus classification (2-back)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`NB2: A`, `NB2: B`, `NB2: C`, `NB2: D`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `NB2: A` | 0 | Stimulus onset: letter A presented |
  | `NB2: B` | 1 | Stimulus onset: letter B presented |
  | `NB2: C` | 2 | Stimulus onset: letter C presented |
  | `NB2: D` | 3 | Stimulus onset: letter D presented |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Original study describing N-back working memory paradigm with letters A-D and 1/2/3-back conditions
  - 10.1016/j.neuroimage.2026.121820 — EEG classification analysis of N-back stimuli; 2-back condition with balanced classes A/B/C/D
- **Notes**: 4-class classification of stimulus identity in the 2-back working memory condition. All four letter classes are well-balanced (~3300 trials each). The epoch window captures pre-stimulus baseline (-200 ms) and extended post-stimulus period (1500 ms) to account for longer processing demands of 2-back maintenance. Target detection in 2-back requires comparing current stimulus to the item presented two trials back, increasing working memory load relative to 1-back.

---

### Classical Task 3: N-back stimulus classification (3-back)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`NB3: A`, `NB3: B`, `NB3: C`, `NB3: D`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `NB3: A` | 0 | Stimulus onset: letter A presented (3-back condition) |
  | `NB3: B` | 1 | Stimulus onset: letter B presented (3-back condition) |
  | `NB3: C` | 2 | Stimulus onset: letter C presented (3-back condition) |
  | `NB3: D` | 3 | Stimulus onset: letter D presented (3-back condition) |
- **Evidence**:
  - `10.3389/fnhum.2020.00246` — Original study describing executive functioning battery with N-back working memory task (1/2/3-back), letters A-D as stimuli, 1s presentation + 500ms fixation
  - `10.1016/j.neuroimage.2026.121820` — 4-class classification of N-back stimuli; 3-back condition maximizes working memory demand and frontal-midline theta engagement
- **Notes**: Balanced classes with ~3300 trials each. All four event IDs confirmed in events.tsv with stimulus onset meanings. 3-back condition represents highest working memory load in the N-back paradigm.

---

### Classical Task 4: N-back load level classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`NB1: A`, `NB1: B`, `NB1: C`, `NB1: D`, `NB2: A`, `NB2: B`, `NB2: C`, `NB2: D`, `NB3: A`, `NB3: B`, `NB3: C`, `NB3: D`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `NB1: A`, `NB1: B`, `NB1: C`, `NB1: D` | 0 | 1-back working memory load |
  | `NB2: A`, `NB2: B`, `NB2: C`, `NB2: D` | 1 | 2-back working memory load |
  | `NB3: A`, `NB3: B`, `NB3: C`, `NB3: D` | 2 | 3-back working memory load |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Dataset reference describing N-back paradigm with 1/2/3-back load levels using letters A-D as stimuli
  - 10.1016/j.neuroimage.2026.121820 — Reference explicitly mentions 'n-back load level (1/2/3)' as condition label for classification
- **Notes**: All four letter stimuli (A/B/C/D) within each n-back load level are merged into a single class y=0,1,2. This many-to-one mapping is justified because the task is to classify working memory load level, not individual stimulus identity. The stimulus-locked epoch window (-0.2 to 1.5 s) captures the sustained theta dynamics critical for load discrimination.

---

### Classical Task 5: Local-Global congruence classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`LG: largeHSmallH`, `LG: largeHSmallT`, `LG: largeTSmallH`, `LG: largeTSmallT`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | LG: largeHSmallH | 0 | Congruent: large H composed of small H letters |
  | LG: largeTSmallT | 0 | Congruent: large T composed of small T letters |
  | LG: largeHSmallT | 1 | Incongruent: large H composed of small T letters |
  | LG: largeTSmallH | 1 | Incongruent: large T composed of small H letters |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Reference explicitly mentions 'congruent/incongruent for Local-Global' as condition label; 2-class classification of congruent vs incongruent trials with balanced classes (~18,257 vs ~18,250)
- **Notes**: Congruent trials (y=0) merge largeHSmallH (9123) and largeTSmallT (9134). Incongruent trials (y=1) merge largeHSmallT (9120) and largeTSmallH (9130). Response events are excluded from epoching; only stimulus onset events are used. Epoch window [-0.2, 1.0] s captures pre-stimulus baseline and early ERP components associated with global-local integration and congruence effects.

---

### Classical Task 6: Local-Global 4-class stimulus identity
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`LG: largeHSmallH`, `LG: largeHSmallT`, `LG: largeTSmallH`, `LG: largeTSmallT`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `LG: largeHSmallH` | 0 | large H composed of small H letters (congruent) |
  | `LG: largeHSmallT` | 1 | large H composed of small T letters (incongruent) |
  | `LG: largeTSmallH` | 2 | large T composed of small H letters (incongruent) |
  | `LG: largeTSmallT` | 3 | large T composed of small T letters (congruent) |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Dataset publication describing Local-Global attention task with four stimulus combinations formed by crossing global letter (H/T) and local letter (H/T)
  - events.tsv (task-LG) — Contains `value` column with exact event names `largeHSmallH`, `largeHSmallT`, `largeTSmallH`, `largeTSmallT` and columns `largeletter`/`smallletter` confirming the 2×2 factorial structure
  - code/tasks/localGlobalAttention.m — Documents bit-to-meaning mapping: bit1=largeHSmallH, bit2=largeHSmallT, bit3=largeTSmallH, bit4=largeTSmallT
- **Notes**: 4-class classification of all stimulus identity combinations in the Local-Global paradigm. Tests hierarchical stimulus processing by requiring the classifier to distinguish both global letter identity (H vs T) and local letter identity (H vs T) simultaneously. Classes are well-balanced (~9,120-9,134 trials each). The event route uses native stimulus onset markers directly from the BIDS events.tsv files.

---

### Classical Task 7: SART target detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`SART: target`, `SART: nontarget`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `SART: target` | 0 | Target digit 3 requiring response withholding (NoGo) |
  | `SART: nontarget` | 1 | Non-target digit requiring spacebar response (Go) |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — SART paradigm with target (digit 3, NoGo) vs nontarget (all other digits, Go) conditions; 1499 target and 11833 nontarget trials across 24 participants
- **Notes**: Standard sustained attention classification. The epoch window (-0.2 to 1.5 s) captures the pre-stimulus baseline and the decision/inhibition process following digit onset. Stimulus duration is ~1s with 500ms fixation, making 1.5s sufficient to capture Go/NoGo ERP components (N2, P3) associated with response inhibition.

---

### Classical Task 8: Neurofeedback group classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | group | FB -> 0 (Feedback group, real-time neurofeedback); S -> 1 (Sham/control group, sham feedback). Derived from participants.tsv `group` column. Needs verification: exact values in Info fields. |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Pre/post neurofeedback design comparing feedback vs sham neurofeedback groups on executive function tasks (N-Back, SART, Local-Global)
  - 10.1016/j.neuroimage.2026.121820 — Neurofeedback training study with feedback and sham/control group comparison
- **Notes**: Segmentation-based approach required because no event in the recording discriminates neurofeedback group assignment; group membership is a between-subjects variable stored in participants.tsv. The 2-second segments with 50% overlap allow sufficient samples for subject-level group classification while capturing task-related EEG dynamics across the continuous recordings. Both sessions (pre and post neurofeedback) are available per participant, enabling potential within-subject or cross-session analyses.

---

### Classical Task 9: Cross-task executive function segmentation with group label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | group | FB -> 0 (Neurofeedback group, real feedback); S -> 1 (Sham group, control). Derived from participants.tsv `group` column. Needs verification: exact values in Info fields. |
- **Evidence**:
  - 10.3389/fnhum.2020.00246 — Neurofeedback study design with FB (feedback) vs S (sham) group randomization; participants.tsv confirms group assignment with complete coverage across N=24 participants
- **Notes**: Segmentation-based approach enables cross-task generalization by treating 2-second EEG windows as samples from a common executive function state space, regardless of whether the underlying task is N-Back, SART, or Local-Global. The group label is a native participants.tsv column requiring no kernel derivation.

---

### Potential Task 1: SART Response Commission Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`SART: target`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `SART: target` (no `SART: rt` within response window) | 0 | Correct withholding — participant correctly did not respond to target digit 3 |
  | `SART: target` (with `SART: rt` within response window) | 1 | Commission error — participant incorrectly pressed spacebar to target digit 3 |
- **Evidence**:
  - `events.tsv` (task-SART) — Shows `SART: target` events (digit 3 requiring no response) and `SART: rt` response events; target events have 1,499 occurrences with expected ~5-10% commission error rate typical for SART paradigms
  - `README` — Describes SART task: "target digit 3, requires withholding response" vs non-target digits requiring spacebar response
- **Notes**: The label is derived by checking whether a `SART: rt` event occurs within a reasonable response window (e.g., 0-1500 ms) following each `SART: target` event. The kernel must pair target events with subsequent response events to determine commission errors. This is a standard Go/NoGo inhibition failure measure with characteristic ERN/Pe ERP components. Epochs are time-locked to the target onset (`SART: target`) to capture both pre-stimulus baseline and post-error neural dynamics.

---

### Potential Task 2: Local-Global response identity classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`LG: responseLargeH`, `LG: responseLargeT`, `LG: responseSmallH`, `LG: responseSmallT`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `LG: responseLargeH` | 0 | Response: participant identified large letter as H |
  | `LG: responseLargeT` | 1 | Response: participant identified large letter as T |
  | `LG: responseSmallH` | 2 | Response: participant identified small letter as H |
  | `LG: responseSmallT` | 3 | Response: participant identified small letter as T |
- **Evidence**:
  - events.tsv (task-LG) — Response events with four distinct response types: responseLargeH, responseLargeT, responseSmallH, responseSmallT
  - events.json / README — Local-Global task documentation confirming hierarchical stimulus-response paradigm with large/small letter identification
  - code/tasks/localGlobalAttention.m — Bit-to-meaning mapping confirming response event codes (bit5=responseSmallH, bit6=responseSmallT, bit7=responseLargeH, bit8=responseLargeT)
- **Notes**: Response-locked epochs with extended pre-response window to capture readiness potential (BP) and lateralized readiness potential (LRP). All four response identities are well-balanced (~8,957-9,272 occurrences each). This is a 4-class motor response decoding task testing whether EEG can discriminate which of four possible responses was executed based on pre-response and post-response neural activity.

---

### Potential Task 3: Local-Global global letter classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`LG: largeHSmallH`, `LG: largeHSmallT`, `LG: largeTSmallH`, `LG: largeTSmallT`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `LG: largeHSmallH` | 0 | Global letter H (congruent: large H, small H) |
  | `LG: largeHSmallT` | 0 | Global letter H (incongruent: large H, small T) |
  | `LG: largeTSmallH` | 1 | Global letter T (incongruent: large T, small H) |
  | `LG: largeTSmallT` | 1 | Global letter T (congruent: large T, small T) |
- **Evidence**:
  - events.tsv (task-LG) — Stimulus onset events with `largeletter` column (H/T) confirming global letter identity; `value` column contains descriptive event names `largeHSmallH`, `largeHSmallT`, `largeTSmallH`, `largeTSmallT`
  - code/tasks/localGlobalAttention.m — Bit-to-meaning mapping: bit1=largeHSmallH, bit2=largeHSmallT, bit3=largeTSmallH, bit4=largeTSmallT
  - README — Describes LG (Local Global) task as part of executive functioning battery
- **Notes**: Two-class classification of global letter identity (H vs T) by merging congruent and incongruent trials within each global letter category. This tests global precedence effect and attentional selection at the global level. Trial counts from evidence summary: Global H ≈18,243 trials, Global T ≈18,264 trials (nearly perfectly balanced).

---

### Potential Task 4: Local-Global Local Letter Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`LG: largeHSmallH`, `LG: largeHSmallT`, `LG: largeTSmallH`, `LG: largeTSmallT`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `LG: largeHSmallH` | 0 | Local letter H (congruent: large H, small H) |
  | `LG: largeHSmallT` | 1 | Local letter T (incongruent: large H, small T) |
  | `LG: largeTSmallH` | 0 | Local letter H (incongruent: large T, small H) |
  | `LG: largeTSmallT` | 1 | Local letter T (congruent: large T, small T) |
- **Evidence**:
  - events.tsv (task-LG) — Stimulus onset events with largeletter/smallletter columns confirming local letter identity independent of global letter
  - code/tasks/localGlobalAttention.m — Bit-to-meaning mapping: bit1=largeHSmallH, bit2=largeHSmallT, bit3=largeTSmallH, bit4=largeTSmallT
  - README — Describes Local Global task as part of executive functioning battery
- **Notes**: Two-class classification based on the identity of the local (small) letter: H vs T. The four event types are merged by local letter identity, collapsing across global letter and congruency. This tests local-level visual processing and attentional selection in the context of hierarchical stimuli. Epoch window inferred from typical visual ERP studies with slight pre-stimulus baseline and covers P1/N1/P2 complex through early decision-related activity.

## Data Quality Notes

- Multiple raw trigger code events (event_1 through event_65565) indicate potential trigger bit overlap/overflow issues, particularly event_65536 and related high-value codes typical of Biosemi 24-bit trigger overflow.
- Combined trigger codes (e.g., event_3, event_129) suggest simultaneous or overlapping stimulus and response triggers in the Local-Global task, which may cause event miscounting if not properly decomposed.
- Subject age and sex metadata are completely missing from the dataset, limiting demographic analyses and potential stratification.
- Device information is missing, though 64-channel EEG at 256 Hz is documented.
- Isolated single-occurrence numeric trigger codes in N-back tasks (NB1: 5/6/9/12, NB2: 5/6/9/10/11) may represent synchronization errors, practice trials, or undeclared system markers; their meaning is unclear.
- SART task has highly imbalanced classes (11833 nontarget vs 1499 target, ~7.9:1 ratio), which may require class weighting or resampling for classification tasks.
- N-back reaction time markers (NB1: rt, NB2: rt, NB3: rt) show decreasing counts with increasing working memory load (3323 → 2827 → 2405), consistent with expected higher omission/error rates under increased cognitive load, but this may indicate missing responses rather than task design.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
