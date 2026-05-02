# Audiocue walking study

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 273 | **Channels**: 115 | **Sampling Rate**: 512 Hz | **Manual Review**: Mingze Tang

## Paradigm

A mobile brain-body imaging (MoBI) study where participants walked on a treadmill and adapted their gait to auditory tone sequences. Participants walked at their preferred cadence, uncued, or responded to tempo shifts (delay or advance) in an auditory metronome. The study investigated the neural dynamics of gait adaptation and rhythm entrainment during real-world locomotion. Each walking condition is a sustained state lasting multiple seconds.

## File Scan Result

> **Kernel SHA256**: `bf6afb20ba0f289e8b0f43351389a5321c89541b2830d440cf66e7336e918cd8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `AdvanceTempo` | 1154 | event | raw | Trial phase onset: AdvanceTempo (step advance pacing tempo condition) |
| `AdvanceTempo_stream2` | 1154 | event | raw | Trial phase onset: AdvanceTempo stream 2 (step advance pacing tempo condition, auxiliary event stream) |
| `DelayTempo` | 2368 | event | raw | Trial phase onset: DelayTempo (step delay pacing tempo condition) |
| `DelayTempo_stream2` | 2368 | event | raw | Trial phase onset: DelayTempo stream 2 (step delay pacing tempo condition, auxiliary event stream) |
| `PreferredCadence` | 32100 | event | raw | Trial phase onset: PreferredCadence (preferred cadence walking condition) |
| `PreferredCadence_stream2` | 26354 | event | raw | Trial phase onset: PreferredCadence stream 2 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream3` | 20237 | event | raw | Trial phase onset: PreferredCadence stream 3 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream4` | 20692 | event | raw | Trial phase onset: PreferredCadence stream 4 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream5` | 34011 | event | raw | Trial phase onset: PreferredCadence stream 5 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream6` | 28708 | event | raw | Trial phase onset: PreferredCadence stream 6 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream7` | 20365 | event | raw | Trial phase onset: PreferredCadence stream 7 (preferred cadence walking condition, auxiliary event stream) |
| `PreferredCadence_stream8` | 21070 | event | raw | Trial phase onset: PreferredCadence stream 8 (preferred cadence walking condition, auxiliary event stream) |
| `UncuedWalking` | 1154 | event | raw | Trial phase onset: UncuedWalking (uncued walking condition with right/left heel strikes) |
| `UncuedWalking_stream2` | 26402 | event | raw | Trial phase onset: UncuedWalking stream 2 (uncued walking condition, auxiliary event stream) |
| `UncuedWalking_stream3` | 20441 | event | raw | Trial phase onset: UncuedWalking stream 3 (uncued walking condition, auxiliary event stream) |
| `UncuedWalking_stream4` | 20635 | event | raw | Trial phase onset: UncuedWalking stream 4 (uncued walking condition, auxiliary event stream) |
| `UncuedWalking_stream5` | 28730 | event | raw | Trial phase onset: UncuedWalking stream 5 (uncued walking condition, auxiliary event stream) |
| `UncuedWalking_stream6` | 20482 | event | raw | Trial phase onset: UncuedWalking stream 6 (uncued walking condition, auxiliary event stream) |
| `UncuedWalking_stream7` | 20683 | event | raw | Trial phase onset: UncuedWalking stream 7 (uncued walking condition, auxiliary event stream) |
| `Walking_event_171` | 5715 | event | raw | Cue during standing previously associated with right heel strike |
| `Walking_event_271` | 5678 | event | raw | Cue during standing previously associated with left heel strike |
| `admin: marker-999` | 1153 | admin | raw | First auditory cue marking step delay tempo shift |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 3-class gait tempo condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 10 s, overlap = 0.5, target_events = [`AdvanceTempo`, `DelayTempo`, `PreferredCadence`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `AdvanceTempo` | 0 | Advance tempo shift (step shortening) |
  | `DelayTempo` | 1 | Delay tempo shift (step lengthening) |
  | `PreferredCadence` | 2 | Preferred cadence baseline walking |
- **Evidence**:
  - 10.1038/s41597-019-0223-2 — Data descriptor explicitly describes 3-class classification of gait conditions: advance tempo shift, delay tempo shift, and preferred cadence baseline
  - 10.1523/jneurosci.3543.15.2016 — Primary research paper analyzes β-band modulations during gait adaptation to auditory metronome shifts, with sustained walking conditions lasting multiple seconds
- **Notes**: All three event IDs (`AdvanceTempo`, `DelayTempo`, `PreferredCadence`) are trial phase onset markers directly from the BIDS events.tsv files. The `_streamN` auxiliary variants are parallel data stream duplicates and are excluded to avoid epoch duplication. The 10s window with 50% overlap is chosen to capture sustained adaptation dynamics while maintaining sufficient epoch count, given that walking conditions span multiple seconds per the data descriptor. Overlap value of 0.5 is inferred from standard practice for sustained-state EEG analysis when exact trial durations are variable.

### Classical Task 2: 2-class tempo shift direction classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -2 s, tmax = 8 s, overlap = 0.0, target_events = [`AdvanceTempo`, `DelayTempo`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `AdvanceTempo` | 0 | Step advance pacing tempo condition (faster tempo, step shortening) |
  | `DelayTempo` | 1 | Step delay pacing tempo condition (slower tempo, step lengthening) |
- **Evidence**:
  - 10.1523/jneurosci.3543.15.2016 — Primary research paper specifically contrasts advance vs delay tempo shifts as the core experimental manipulation, analyzing β-band power changes time-locked to these tempo shift events. Step shortening (advance) and step lengthening (delay) represent opposing motor adaptations with different cognitive demands.
- **Notes**: The task excludes PreferredCadence baseline and UncuedWalking conditions to focus purely on directional adaptation. The _stream2 auxiliary variants of AdvanceTempo and DelayTempo represent parallel event streams from the original EEGLAB format and are not needed since the primary event IDs capture all tempo shift onsets. The epoch window (-2s to +8s) captures the pre-shift baseline and the main adaptation window based on motor learning literature cited in the source paper.

### Potential Task 1: Cued vs Uncued Walking Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 10 s, overlap = 0.5, target_events = [`PreferredCadence`, `UncuedWalking`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `PreferredCadence` | 0 | Cued walking at preferred cadence with auditory metronome |
  | `UncuedWalking` | 1 | Uncued self-paced walking without auditory pacing |
- **Evidence**:
  - task-AudioCueWalkingStudy_events.json — Defines value codes: 101/201 = right/left cued heel strikes during preferred cadence walking; 100/200 = right/left heel strikes during uncued walking
  - events.tsv (sub-001 run-01) — Confirms `PreferredCadence` and `UncuedWalking` as trial_type values marking distinct walking conditions
  - README — Describes auditory tone sequence pacing paradigm with shifts to faster/slower tempo, confirming externally-paced vs self-paced locomotion contrast
  - EEG header — Shows annotations including cued (114, 444, 101, 201, 151, 251) and uncued (100, 200) event codes present in raw data
- **Notes**: The `PreferredCadence` condition represents cued walking with auditory metronome pacing at the participant's preferred cadence, while `UncuedWalking` represents self-paced walking without external auditory cues. This contrast isolates the neural effects of auditory-motor entrainment during locomotion. The 10-second window captures sustained gait dynamics; overlap=0.5 is set to increase usable epochs given the substantial event count imbalance (32100 vs 1154 primary events). The `_streamN` auxiliary variants are inferred parallel data streams from the original EEGLAB format and are not required for this task.

### Potential Task 2: Standing Cue Lateralization Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Walking_event_171`, `Walking_event_271`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Walking_event_171` | 0 | Cue during standing previously associated with right heel strike |
  | `Walking_event_271` | 1 | Cue during standing previously associated with left heel strike |
- **Evidence**:

- **Notes**: This task uses discrete auditory cue events (171/271) delivered during standing periods, not during active walking. The lateralized association comes from prior walking experience where these cues were paired with right/left heel strikes. The epoch window captures auditory evoked responses and early post-cue processing. Values marked with * are inferred from standard ERP paradigms for auditory cue processing.

### Potential Task 3: Heel Strike Lateralization During Uncued Walking
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`UncuedWalking`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `UncuedWalking` | 0 | Right heel strike (Value 100) |
  | `UncuedWalking` | 1 | Left heel strike (Value 200) |
- **Evidence**:

- **Notes**: The `UncuedWalking` trial_type events contain embedded trigger values. The kernel must extract the `value` column from events.tsv within `UncuedWalking` segments: value 100 -> y=0 (Right), value 200 -> y=1 (Left). This matches the structural parent ID `UncuedWalking` present in the Event Structure.

### Potential Task 4: Sex Classification from Walking EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - participants.tsv — 20 subjects with complete sex information (F: 9, M: 11)
- **Notes**: Binary classification of biological sex from EEG recorded during treadmill walking with auditory pacing. The 10-second non-overlapping segmentation provides multiple samples per subject while capturing locomotor dynamics. This is a B3 archetype using native participants.tsv column; no kernel derivation needed. The MoBI context with real-world movement may reveal sex differences in neural gait control.

### Potential Task 5: Age Regression from Walking EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — 20 subjects with age values (effective range 23–38 years); some entries are ranges (e.g., '18-38') requiring midpoint imputation or exclusion
- **Notes**: Subject-level continuous regression task using segmentation to create multiple samples per participant. Age is a native participants.tsv column (archetype B3, Meta Level = raw). The 10-second window length is standard for Complex Applied biological state tasks with continuous EEG; overlap is 0 to ensure independent segments. Some entries encoded as ranges limit granularity but the 23-38 year span provides sufficient variability for regression analysis of neural correlates of gait control across young adulthood.

### Potential Task 6: Segmented Walking State with Sex Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:

- **Notes**: Archetype C with native info label (sex). The continuous walking recordings contain mixed event structures with multiple condition types and auxiliary streams, making a naturalistic segmentation approach appropriate. Arbitrary 4-second EEG segments are classified by subject-level sex, treating the entire walking session as a continuous brain state. The segment_length and overlap values are inferred from the candidate's epoch_hint as no canonical trial structure exists for this continuous MoBI paradigm.

### Potential Task 7: Segmented Walking State with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - participants.tsv — N=20, age=23.0–38.0, with some range entries (e.g., '18-38')
- **Notes**: Archetype C with info-native label (age from participants.tsv). Segmentation is required because the walking protocol produces continuous, mixed-condition recordings without clean trial boundaries suitable for event-based epoching. The 4-second windows with 50% overlap maximize the number of segments per subject for robust age regression from locomotor EEG dynamics. Age serves as a biomarker target: neural signatures of gait adaptability and sensorimotor integration across the complex multi-condition protocol (cued/uncued walking, tempo shifts) may correlate with age-related differences in young adults (23–38 years). The kernel does not need to derive any channels; age is read directly from participants.tsv.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
