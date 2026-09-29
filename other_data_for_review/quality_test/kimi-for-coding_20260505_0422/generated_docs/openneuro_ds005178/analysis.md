# Ear-EEG Sleep Monitoring 2023 (EESM23)

**Dataset**: `openneuro_ds005178` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds005178
**Category**: Biological State | **Subjects**: 10 | **Files (Completed)**: 40 | **Channels**: 14 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

This dataset contains ear-EEG and scalp PSG recordings from 10 healthy subjects during combined video-watching and overnight sleep sessions. Each recording consists of a video sequence followed by a sleep sequence, with triggers marking the boundary between the two. Sleep stages were manually scored by experts in 30-second epochs according to AASM guidelines, with annotations provided for Wake, REM, N1, N2, N3, and Artefact classes. Data were collected using an ear-EEG device with 14 channels at 250 Hz sampling rate, with PSG recordings serving as reference for the first two sessions.

## File Scan Result

> **Kernel SHA256**: `dab6346754952b383c26ffd3a42b63abdc0ed8bade3a05f650229f3968495735`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `error -10` | 5723 | event | raw |  |
| `error -100` | 62 | event | raw |  |
| `event` | 6223 | event | raw |  |
| `event_2` | 72 | event | raw | Sleep scoring epoch onset (30-second sleep stage annotation) |
| `oLED` | 1 | event | raw |  |
| `trigger` | 175 | event | raw | Trial phase onset: trigger (video/sleep sequence boundary marker) |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | complete | ear-EEG |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Classical Task 1: 5-class sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 30 s, target_events = [event_2]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_2` | 0 | Wake |
  | `event_2` | 1 | REM |
  | `event_2` | 2 | N1 |
  | `event_2` | 3 | N2 |
  | `event_2` | 4 | N3 |
- **Evidence**:
  - 10.3389/fnins.2023.987578 — Primary task of the EESM23 dataset: 5-class sleep stage classification using 30-second non-overlapping epochs aligned with PSG manual scoring
  - 10.1038/s41597-025-04579-8 — Confirms 5-class sleep stage paradigm (Wake, N1, N2, N3, REM) with 30-second epoch duration
  - 10.1109/embc58623.2025.11252780 — Reports Cohen's kappa of 0.71 for automatic scoring vs PSG; confirms 5-class classification excluding Artefact epochs
- **Notes**: The scoring_idx column in events.tsv provides labels 1-6 where 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact. For standard 5-class classification, Artefact epochs (y=6) are excluded from training/evaluation. The mapping follows standard AASM sleep staging with y values remapped to 0-based sequential integers: Wake→0, REM→1, N1→2, N2→3, N3→4.

### Potential Task 1: 6-class sleep stage with artefact detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 30 s, target_events = [event_2]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 | 0 | Wake |
  | event_2 | 1 | REM |
  | event_2 | 2 | N1 |
  | event_2 | 3 | N2 |
  | event_2 | 4 | N3 |
  | event_2 | 5 | Artefact |
- **Evidence**:
  - task-sleep_acq-scoring_events.json — Defines `scoring_idx` levels: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact; duration confirms 30-second epochs
  - README — Confirms sleep scoring annotations present in first two PSG recordings (ses-001/ses-002)
- **Notes**: The 6-class variant preserves the full annotation granularity including Artefact (scoring_idx=6) for artefact-aware modeling. The 0-based y mapping follows standard sleep stage ordering: Wake(0), REM(1), N1(2), N2(3), N3(4), Artefact(5). This differs from the 1-based scoring_idx in the source data. The Artefact class represents epochs with signal quality too poor for scoring, enabling joint sleep staging and quality assessment.

### Potential Task 2: 2-class wake vs sleep detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 30 s *, target_events = [event_2]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 (scoring_idx=1) | 0 | Wake |
  | event_2 (scoring_idx=2,3,4,5) | 1 | Sleep (REM/N1/N2/N3 combined) |
- **Evidence**:
  - task-sleep_acq-scoring_events.json — scoring_idx levels: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact; confirms 30-second epoch sleep scoring annotations
  - README — confirms sleep recordings with PSG and ear-EEG, scoring files in ses-001/ses-002
- **Notes**: Binary collapse of 5-class sleep staging into wake vs sleep detection. Artefact epochs (scoring_idx=6) are excluded from both classes. The 30-second epoch length is standard for sleep scoring (AASM guidelines). Event_2 provides epoch onset markers with scoring_idx values in events.tsv files.

### Potential Task 3: 3-class wake-NREM-REM classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 30 s *, target_events = [event_2]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_2` | 0 | Wake (scoring_idx=1) |
  | `event_2` | 1 | NREM (scoring_idx=3,4,5 combined: N1+N2+N3) |
  | `event_2` | 2 | REM (scoring_idx=2) |
- **Evidence**:
  - task-sleep_acq-scoring_events.json — Defines scoring_idx levels: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact; 30-second epoch annotations for sleep scoring
  - README — Confirms sleep recordings with PSG scoring for first two sessions, video then sleep sequences with triggers separating them
- **Notes**: Artefact epochs (scoring_idx=6) are excluded. The 3-class collapse (Wake/NREM/REM) follows clinical R&K simplified scoring conventions and consumer sleep device granularity. N1, N2, and N3 are merged into a single NREM class (y=1) as is standard in reduced-complexity sleep staging. Epoch timing inferred from standard 30-second sleep scoring epoch duration.

### Potential Task 4: 4-class sleep stage without N1
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 30 s *, target_events = [event_2]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 | 0 | Wake |
  | event_2 | 1 | REM |
  | event_2 | 2 | N2 |
  | event_2 | 3 | N3 |
- **Evidence**:
- **Notes**: The scoring_idx values in events.tsv map to: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact. This task excludes N1 (scoring_idx=3) and Artefact (scoring_idx=6) epochs, keeping only Wake (y=0), REM (y=1), N2 (y=2), and N3 (y=3). N1 exclusion is common practice in sleep scoring due to its poor inter-rater reliability and known difficulty in ear-EEG classification. The kernel must filter epochs based on the scoring_idx column value associated with each event_2 onset.

### Potential Task 5: video-sleep sequence boundary detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = -30 s *, tmax = 30 s *, overlap = 0.0 *, target_events = [trigger]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | trigger | 0 | pre-trigger video epoch (30s before boundary) |
  | trigger | 1 | post-trigger sleep epoch (30s after boundary) |
- **Evidence**:
  - README — "Each file consists of a video sequence followed by a sleep sequence. After the video sequence, the subject sent triggers to distinguish between the two sequences."
  - sub-001_ses-001_task-sleep_acq-PSGtrigger_events.tsv — trigger events at onset=9664, 69123, 172979, 6079358 with duration=0, confirming sparse boundary markers in PSG sessions
  - task-sleep_acq-PSGtrigger_events.json scope — triggers limited to ses-001/ses-002 PSG sessions
- **Notes**: The trigger event marks the boundary between video-watching and sleep recording sequences. Using long-event epoching with symmetric 30-second windows before and after each trigger creates two classes: y=0 captures the pre-sleep video-watching brain state, while y=1 captures the post-trigger sleep-recording state. The 0-duration triggers require long-event epoching since they are sparse temporal boundaries rather than repeated trial markers. Overlap set to 0.0 as default for non-overlapping boundary epochs; tmin/tmax inferred from paradigm rationale (state change windows around transition point).

## Data Quality Notes

- Missing demographic metadata: age, handedness, and sex fields are absent from all recordings, limiting population-level analysis and generalizability assessments.
- Limited sleep scoring coverage: manual PSG-based sleep stage annotations (event_2) are only available for the first two sessions (ses-001/ses-002), not for later sessions.
- Sparse event_2 markers: only 72 event_2 annotations across the entire dataset, suggesting very limited scored sleep data relative to total recording duration.
- High count of error events: 5,723 `error -10` and 62 `error -100` events indicate potential hardware or synchronization issues during acquisition that may affect signal quality.
- Single oLED event: only 1 `oLED` event present, suggesting this marker is non-functional or irrelevant for analysis.
- Trigger events limited to PSG sessions: the 175 trigger events for video/sleep boundary detection are confined to ses-001/ses-002, matching the PSG scoring availability.
- No amplifier metadata recorded: equipment details are missing, preventing reproducibility checks and hardware-specific quality assessments.
- Potential class imbalance in sleep stages: with only 72 scored epochs across all subjects, some sleep stages may be severely underrepresented.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
