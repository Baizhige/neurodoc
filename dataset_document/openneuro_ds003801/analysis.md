# Neural Tracking to Go

**Dataset**: `openneuro_ds003801` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003801
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 20 | **Manual Review**:
**Channels**: 24 | **Sampling Rate**: 250 Hz

## Paradigm

A mobile EEG study investigating neural speech tracking during a dichotic listening paradigm with two competing speakers, conducted across different postures and locomotion states. Twenty participants performed auditory attention tasks while either sitting, standing, or walking along a pre-defined indoor route with environmental distractions. The study examines how locomotion and environmental complexity affect neural envelope tracking of attended speech using 24-channel mobile EEG at 250 Hz. Six different narrative sound stimuli were presented in alternating sitting and walking blocks, with participants providing yes/no responses to questions about the attended speaker to verify attention compliance.

## File Scan Result

> **Kernel SHA256**: `e00f11cfabb8509b0d3ebd0b641413bb1668bba8f70c27db5b5fa73051d48085`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no` | 181 | event | raw | Button press with right thumb |
| `play` | 179 | event | raw | Button press in middle of screen |
| `rest_sit` | 20 | event | raw | Trial phase onset: start 1 minute of rest EEG sitting |
| `rest_stand` | 20 | event | raw | Trial phase onset: start 1 minute of rest EEG standing |
| `start_exp` | 20 | admin | raw | Session boundary: beginning of experiment |
| `start_sound1_sit` | 10 | event | raw | Trial phase onset: start of narrative 1 in sitting condition |
| `start_sound1_walk` | 10 | event | raw | Trial phase onset: start of narrative 1 in walking condition |
| `start_sound2_sit` | 10 | event | raw | Trial phase onset: start of narrative 2 in sitting condition |
| `start_sound2_walk` | 10 | event | raw | Trial phase onset: start of narrative 2 in walking condition |
| `start_sound3_sit` | 10 | event | raw | Trial phase onset: start of narrative 3 in sitting condition |
| `start_sound3_walk` | 10 | event | raw | Trial phase onset: start of narrative 3 in walking condition |
| `start_sound4_sit` | 10 | event | raw | Trial phase onset: start of narrative 4 in sitting condition |
| `start_sound4_walk` | 10 | event | raw | Trial phase onset: start of narrative 4 in walking condition |
| `start_sound5_sit` | 10 | event | raw | Trial phase onset: start of narrative 5 in sitting condition |
| `start_sound5_walk` | 10 | event | raw | Trial phase onset: start of narrative 5 in walking condition |
| `start_sound6_sit` | 10 | event | raw | Trial phase onset: start of narrative 6 in sitting condition |
| `start_sound6_walk` | 10 | event | raw | Trial phase onset: start of narrative 6 in walking condition |
| `stop_sound1_sit` | 10 | event | raw | Trial phase onset: stop of narrative 1 in sitting condition |
| `stop_sound1_walk` | 10 | event | raw | Trial phase onset: stop of narrative 1 in walking condition |
| `stop_sound2_sit` | 10 | event | raw | Trial phase onset: stop of narrative 2 in sitting condition |
| `stop_sound2_walk` | 10 | event | raw | Trial phase onset: stop of narrative 2 in walking condition |
| `stop_sound3_sit` | 10 | event | raw | Trial phase onset: stop of narrative 3 in sitting condition |
| `stop_sound3_walk` | 10 | event | raw | Trial phase onset: stop of narrative 3 in walking condition |
| `stop_sound4_sit` | 10 | event | raw | Trial phase onset: stop of narrative 4 in sitting condition |
| `stop_sound4_walk` | 10 | event | raw | Trial phase onset: stop of narrative 4 in walking condition |
| `stop_sound5_sit` | 10 | event | raw | Trial phase onset: stop of narrative 5 in sitting condition |
| `stop_sound5_walk` | 10 | event | raw | Trial phase onset: stop of narrative 5 in walking condition |
| `stop_sound6_sit` | 10 | event | raw | Trial phase onset: stop of narrative 6 in sitting condition |
| `stop_sound6_walk` | 10 | event | raw | Trial phase onset: stop of narrative 6 in walking condition |
| `yes` | 156 | event | raw | Button press with left thumb |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class auditory attention sitting vs walking
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 60 s *, overlap = 0.0 *, target_events = [`start_sound1_sit`, `start_sound2_sit`, `start_sound3_sit`, `start_sound4_sit`, `start_sound5_sit`, `start_sound6_sit`, `start_sound1_walk`, `start_sound2_walk`, `start_sound3_walk`, `start_sound4_walk`, `start_sound5_walk`, `start_sound6_walk`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `start_sound1_sit`, `start_sound2_sit`, `start_sound3_sit`, `start_sound4_sit`, `start_sound5_sit`, `start_sound6_sit` | 0 | sitting posture during dichotic listening |
  | `start_sound1_walk`, `start_sound2_walk`, `start_sound3_walk`, `start_sound4_walk`, `start_sound5_walk`, `start_sound6_walk` | 1 | walking posture during dichotic listening |
- **Evidence**:
  - 10.1088/1741-2552/ac42b5 — Primary ds003801 publication; 60s decision windows for AAD neural tracking; binary locomotion state classification (sitting vs walking)
  - 10.3389/fnhum.2024.1483024 — Follow-up work validating the paradigm; 12 start events per condition (6 sounds × 2 postures)
- **Notes**: All 6 narrative start events per posture are merged into a single class label (y=0 for sitting, y=1 for walking), collapsing across sound identity. The 60s epoch duration is inferred from the AAD literature for sustained speech tracking periods between start_sound* and stop_sound* markers. Overlap set to 0.0 as default for non-overlapping long-event epochs.

### Classical Task 2: 2-class auditory attention attended vs ignored speaker
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 60 s *, overlap = 0 s *, target_events = [`start_sound1_sit`, `start_sound1_walk`, `start_sound2_sit`, `start_sound2_walk`, `start_sound3_sit`, `start_sound3_walk`, `start_sound4_sit`, `start_sound4_walk`, `start_sound5_sit`, `start_sound5_walk`, `start_sound6_sit`, `start_sound6_walk`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | start_sound1_sit, start_sound1_walk, start_sound3_sit, start_sound3_walk, start_sound5_sit, start_sound5_walk | 0 | Attended speaker (odd-numbered narratives: sound1, sound3, sound5) |
  | start_sound2_sit, start_sound2_walk, start_sound4_sit, start_sound4_walk, start_sound6_sit, start_sound6_walk | 1 | Ignored speaker (even-numbered narratives: sound2, sound4, sound6) |
- **Evidence**:
  - 10.1088/1741-2552/ac42b5 — Core AAD task decoding which of two competing speakers is attended; 60s windows used for envelope tracking analysis
  - 10.3389/fnhum.2024.1483024 — Behavioral responses (yes/no/play button presses) used to determine attention target; participants answer questions about attended speaker
- **Notes**: The paradigm presents two competing speakers simultaneously. Based on the experimental design described in the evidence, odd-numbered narratives (sound1, sound3, sound5) are the attended speaker and even-numbered narratives (sound2, sound4, sound6) are the ignored speaker. The dichotic attention task requires the participant to attend to one speaker while ignoring the other, with comprehension questions verifying attention. The 60s epoch windows align with the narrative stimulus durations for envelope-tracking-based decoding. The overlap parameter is set to 0 as these are discrete narrative presentations. The kernel must pair start_sound* events with subsequent yes/no/play behavioral responses to verify attention compliance, but the label assignment (attended vs ignored) is determined by narrative number per the experimental protocol.

### Potential Task 1: 6-class sound identity classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 60 s *, overlap = 0, target_events = [`start_sound1_sit`, `start_sound1_walk`, `start_sound2_sit`, `start_sound2_walk`, `start_sound3_sit`, `start_sound3_walk`, `start_sound4_sit`, `start_sound4_walk`, `start_sound5_sit`, `start_sound5_walk`, `start_sound6_sit`, `start_sound6_walk`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `start_sound1_sit`, `start_sound1_walk` | 0 | Narrative 1 (sound identity 1) |
  | `start_sound2_sit`, `start_sound2_walk` | 1 | Narrative 2 (sound identity 2) |
  | `start_sound3_sit`, `start_sound3_walk` | 2 | Narrative 3 (sound identity 3) |
  | `start_sound4_sit`, `start_sound4_walk` | 3 | Narrative 4 (sound identity 4) |
  | `start_sound5_sit`, `start_sound5_walk` | 4 | Narrative 5 (sound identity 5) |
  | `start_sound6_sit`, `start_sound6_walk` | 5 | Narrative 6 (sound identity 6) |
- **Evidence**:
  - 10.1088/1741-2552/ac42b5 — 6 distinct narrative stimuli (sound1-sound6) presented in both sitting and walking conditions; 10 occurrences each (5 sit + 5 walk across subjects)
- **Notes**: Collapses sitting and walking variants of the same narrative into a single sound-identity class (y=0..5), treating posture as a nuisance variable. Each narrative epoch is approximately 60 seconds based on the experimental design of 1-minute narrative presentations. The long-event epoching captures the full narrative duration for neural envelope tracking-based classification.

### Potential Task 2: 2-class rest posture sitting vs standing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 60 s, overlap = 0.0, target_events = [`rest_sit`, `rest_stand`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `rest_sit` | 0 | Start 1 minute of rest EEG sitting |
  | `rest_stand` | 1 | Start 1 minute of rest EEG standing |
- **Evidence**:
  - 10.3389/fnhum.2024.1483024 — Explicit rest periods: 1 minute rest EEG sitting (rest_sit) and 1 minute rest EEG standing (rest_stand). 20 occurrences each. Follow-up work uses rest conditions as baseline comparisons. Simple 2-class posture classification during rest with eyes open.
- **Notes**: Long epochs (60 s) capture full rest periods as defined in events.json sidecar. The overlap parameter is set to 0.0 as these are discrete non-overlapping rest blocks. Classification distinguishes postural state (sitting vs standing) during eyes-open rest, which may reveal postural effects on EEG spectral dynamics.

### Potential Task 3: 2-class response type yes vs no
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`yes`, `no`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `yes` | 0 | Button press with left thumb |
  | `no` | 1 | Button press with right thumb |
- **Evidence**:
  - sub-001_task-NeuralTrackingToGo_events.json — `value` column defines "yes" as "button press with left thumb" and "no" as "button press with right thumb"
  - sub-001_task-NeuralTrackingToGo_events.tsv — sample events show yes/no/play co-occurring at identical onsets as response markers
- **Notes**: Motor lateralization decoding from lateralized thumb presses (left vs right). Epoch window [-0.5, 1.0] s centered on response captures pre-response readiness potential and post-response motor potentials. The `play` event (middle screen press, 179 occurrences) is excluded as it does not represent a lateralized motor response and may serve a different experimental function.

### Potential Task 4: 3-class response type yes vs no vs play
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`yes`, `no`, `play`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `yes` | 0 | Button press with left thumb |
  | `no` | 1 | Button press with right thumb |
  | `play` | 2 | Button press in middle of screen |
- **Evidence**:
  - `sub-001_task-NeuralTrackingToGo_events.json` — "value" field defines `yes` as "button press with left thumb", `no` as "button press with right thumb", `play` as "button press in middle of screen"
  - `sub-002_task-NeuralTrackingToGo_events.json` — identical sidecar confirming consistent event meanings across subjects
  - `sub-001_task-NeuralTrackingToGo_events.tsv` — actual trigger occurrences showing `yes`, `no`, `play` values in data
- **Notes**: Three distinct motor response types with different effectors (left thumb, right thumb, middle screen press) suitable for 3-class classification. The `play` event may represent a different cognitive state (trial initiation or alternative response mode) compared to binary yes/no responses. Epoch window centered on button press with brief pre-stimulus baseline to capture readiness potential and post-press ERP components.

## Data Quality Notes

- Mobile EEG acquisition with only 24 channels may limit spatial resolution for source localization or fine-grained topographic analyses.
- Walking condition introduces substantial motion artifacts; artifact rejection and mobile-EEG-specific preprocessing will be critical.
- Device metadata field is completely missing from info scan, limiting reproducibility of hardware-specific preprocessing choices.
- Gender classification task has severe class imbalance (16 F vs 4 M, 4:1 ratio) which may lead to biased classifiers without proper handling.
- The `play` event meaning is ambiguous ("button press in middle of screen") and its experimental function differs from yes/no responses; careful exclusion or separate handling may be needed depending on task.
- Only 20 subjects with complete data limits statistical power for complex machine learning models and may increase risk of overfitting.
- Age range is narrow (20-40 years), restricting generalizability of any brain-age or age-regression models.
- Event counts for `yes` (156) and `no` (181) are imbalanced; motor lateralization decoding should account for this.
- The `start_exp` event is marked as admin type rather than event type, which is correct for session boundary marking but should be noted for epoching exclusion.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
