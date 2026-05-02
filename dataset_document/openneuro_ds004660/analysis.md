# TNO (Military Cognitive Workload)

**Dataset**: `openneuro_ds004660` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004660
**Category**: Complex Applied| **Subjects**: 9 | **Files (Completed)**: 18 | **Channels**: 64 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from 9 military personnel performing a P300-based cognitive workload paradigm designed to assess mental workload under varying task demands. Subjects completed multiple runs of a surveillance and target detection task with hierarchically encoded event triggers marking trial phases, stimulus presentations, and responses. Data were collected with a 64-channel EEG system at 256 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `5db0f107b2be46903d445341f63b9882e524d03e7b43aa51db4839b18e728183`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `11001` | 42 | admin | raw | Trial phase onset: start |
| `11002` | 42 | admin | raw | Trial phase onset: end/task boundary |
| `12101` | 165 | admin | raw | Trial phase onset: trial/block initiation |
| `12102` | 166 | admin | raw | Trial phase onset: trial/block initiation offset |
| `12201` | 166 | admin | raw | Trial phase onset: trial/block initiation variant |
| `12202` | 168 | admin | raw | Trial phase onset: trial/block initiation variant offset |
| `13001` | 3663 | admin | raw | Trial phase onset: timing/epoch marker |
| `13002` | 3663 | admin | raw | Trial phase onset: timing/epoch marker offset |
| `14111` | 9228 | event | raw | Stimulus presentation: item pair 11 state 1 |
| `14112` | 9228 | event | raw | Stimulus presentation: item pair 11 state 2 |
| `14121` | 1680 | event | raw | Stimulus presentation: item pair 12 state 1 |
| `14122` | 1680 | event | raw | Stimulus presentation: item pair 12 state 2 |
| `14211` | 42922 | event | raw | Stimulus presentation: item pair 21 state 1 |
| `14212` | 42922 | event | raw | Stimulus presentation: item pair 21 state 2 |
| `14231` | 1115 | event | raw | Stimulus presentation: item pair 23 state 1 |
| `14232` | 1115 | event | raw | Stimulus presentation: item pair 23 state 2 |
| `15111` | 1823 | event | raw | Trial phase onset: sequence position 1 |
| `15121` | 1840 | event | raw | Trial phase onset: sequence position 1 variant |
| `15211` | 1823 | event | raw | Trial phase onset: sequence position 2 |
| `15221` | 1840 | event | raw | Trial phase onset: sequence position 2 variant |
| `15311` | 1823 | event | raw | Trial phase onset: sequence position 3 |
| `15321` | 1840 | event | raw | Trial phase onset: sequence position 3 variant |
| `15411` | 1823 | event | raw | Trial phase onset: sequence position 4 |
| `15421` | 1840 | event | raw | Trial phase onset: sequence position 4 variant |
| `15511` | 1823 | event | raw | Trial phase onset: sequence position 5 |
| `15521` | 1840 | event | raw | Trial phase onset: sequence position 5 variant |
| `15611` | 1823 | event | raw | Trial phase onset: sequence position 6 |
| `15621` | 1840 | event | raw | Trial phase onset: sequence position 6 variant |
| `16101` | 1134 | event | raw | Trial phase onset: response/feedback marker |
| `16102` | 1134 | event | raw | Trial phase onset: response/feedback marker offset |
| `16201` | 689 | event | raw | Trial phase onset: response/feedback marker variant |
| `16202` | 689 | event | raw | Trial phase onset: response/feedback marker variant offset |
| `21111` | 9228 | admin | raw | Trial phase onset: run/session end |
| `21121` | 1115 | admin | raw | Trial phase onset: run/session end variant |
| `21201` | 3663 | admin | raw | Trial phase onset: block summary |
| `21311` | 1134 | admin | raw | Trial phase onset: final marker |
| `21321` | 689 | admin | raw | Trial phase onset: final marker variant |
| `31202` | 3 | admin | raw | System marker: rare trigger |
| `31301` | 2 | admin | raw | System marker: rare trigger |
| `31302` | 2 | admin | raw | System marker: rare trigger |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus Pair Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = ['14111', '14112', '14121', '14122', '14211', '14212', '14231', '14232']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 14111, 14112 | 0 | Item pair 11 |
  | 14121, 14122 | 1 | Item pair 12 |
  | 14211, 14212 | 2 | Item pair 21 |
  | 14231, 14232 | 3 | Item pair 23 |
- **Evidence**:
  - events.json — HED tags classify 14111-14232 as "Experimental-stimulus"; Levels descriptions identify 14xxx codes as stimulus presentation events for specific item pairs
  - events.tsv samples — 14211/14212 and 14111/14112 alternate in temporal sequence confirming paired on/off structure for item pairs
  - Event counts — 14111/14112 (n=9228), 14121/14122 (n=1680), 14211/14212 (n=42922), 14231/14232 (n=1115) confirm four distinct stimulus pairs with paired state structure
- **Notes**: Two-state (on/off) event pairs are merged into single class per item pair. The event semantics "item pair XX state Y" from the locked ground truth confirm that the first four digits encode the pair identity and the final digit encodes state. This yields a 4-class classification of stimulus pair identity. Class imbalance is severe (pair 21 dominates at ~75% of events).

### Potential Task 2: Sequence Position Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`15111`, `15121`, `15211`, `15221`, `15311`, `15321`, `15411`, `15421`, `15511`, `15521`, `15611`, `15621`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 15111, 15121 | 0 | sequence position 1 |
  | 15211, 15221 | 1 | sequence position 2 |
  | 15311, 15321 | 2 | sequence position 3 |
  | 15411, 15421 | 3 | sequence position 4 |
  | 15511, 15521 | 4 | sequence position 5 |
  | 15611, 15621 | 5 | sequence position 6 |
- **Evidence**:
  - sub-001_task-P300_run-1_events.tsv — 15111 appears at onset 11.1757812500 marking sequence position 1; 14211/14212 stimulus presentations precede it, consistent with trial-start sequence marker
  - task-P300_events.json — HED tags confirm 15111-15621 as "Experimental-stimulus"; Levels descriptions identify 15111 as "sequence position 1", 15211 as "sequence position 2", etc.
  - Event counts — 15111/15121 (1823/1840), 15211/15221 (1823/1840), 15311/15321 (1823/1840), 15411/15421 (1823/1840), 15511/15521 (1823/1840), 15611/15621 (1823/1840): balanced ~1823-1840 occurrences per position across 9 subjects × 2 runs
- **Notes**: Variant codes (e.g., 15121 vs 15111) are merged per position as they represent the same sequence position with minor condition variants (on/off states). The 6-class classification targets temporal order processing and working memory load as position advances from 1 to 6 within each trial sequence.

### Potential Task 3: Trial Phase State Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.5 s *, target_events = [`12101`, `12201`, `14111`, `14211`, `16101`, `16201`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 12101, 12201 | 0 | Trial initiation phase |
  | 14111, 14211 | 1 | Stimulus presentation phase |
  | 16101, 16201 | 2 | Response/feedback phase |
- **Evidence**:
  - sub-001_task-P300_run-1_events.tsv — Shows 12101 (initiation), 14211 (stimulus), and 15111 (sequence position) co-occurring at trial start; 14111/14211 alternate as stimulus pairs; 16101/16201 mark response phases
  - task-P300_events.json — HED tags confirm 12101/12201 as "Experiment-control" (initiation), 14111/14211 as "Experimental-stimulus" (stimulus), 16101/16201 as "Experimental-stimulus" (response/feedback)
  - Event counts — 12101:165, 12201:166, 14111:9228, 14211:42922, 16101:1134, 16201:689 provide sufficient samples per class
- **Notes**: Three distinct trial phases are distinguished: initiation (12101/12201 — trial/block start markers), stimulus presentation (14111/14211 — item pair presentation markers), and response/feedback (16101/16201 — response markers). The 14xxx codes are stimulus-specific (item pair × state) but share the same trial phase semantics; similarly 12101/12201 and 16101/16201 are variants of the same phase. Merging variants into phase-level classes yields a balanced 3-class task. Epoch window [-0.2, 0.5] s captures brief phase-transition dynamics around administrative markers.

## Data Quality Notes

- Missing subject metadata: `subject_age`, `subject_sex`, and `device` fields are absent from all recordings, limiting demographic and equipment-based analyses.
- Small sample size: only 9 subjects with 18 completed files may limit generalizability of findings.
- Severe class imbalance in Task 1 (Stimulus Pair Type Classification): item pair 21 comprises approximately 75% of all stimulus events (42922/55083), which may bias classification models.
- Rare system markers (31202, 31301, 31302) have extremely low counts (2-3 occurrences), making them unsuitable for robust analysis.
- The existing draft analysis contained event type classifications (e.g., "event" vs "admin") and meanings that differed from the authoritative file scan result; the file scan result's classifications and meanings supersede the draft.
- Hierarchical 5-digit trigger coding scheme requires careful interpretation; first two digits encode broad category (11=phase onset, 12=trial initiation, 13=timing, 14=stimulus, 15=sequence, 16=response, 21=run end, 31=system), with subsequent digits encoding sub-conditions.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
