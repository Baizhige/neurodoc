# Delayed Auditory Feedback EEG/EGG

**Dataset**: `openneuro_ds005403` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005403
**Category**: High-level Mental | **Subjects**: 66 | **Files (Completed)**: 66 | **Channels**: 66 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants performed a speech production task while receiving delayed auditory feedback (DAF) to study neural processing of self-generated speech and auditory-motor monitoring. Three DAF conditions were used: an adaptation condition (fixed delay) and two random delay conditions (random1, random2), compared against a baseline (no delay). EEG was recorded alongside electroglottography (EGG) to capture vocal fold activity simultaneously. The event markers label continuous speech production blocks.

## File Scan Result

> **Kernel SHA256**: `4afa48fb7528750b8cf2c52fac832c22120aa5dd1a863f48d4c1bb18d10f1d3b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `adaption` | 2560 | event | raw | Trial phase onset: adaption |
| `baseline` | 640 | event | raw | Trial phase onset: baseline |
| `random1` | 1600 | event | raw | Trial phase onset: random1 |
| `random2` | 1600 | event | raw | Trial phase onset: random2 |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `audio` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `audio_envelope` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `audio_onsets` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `egg` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `egg_envelope` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `egg_onsets` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `audio`, `audio_envelope`, `audio_onsets`, `egg`, `egg_envelope`, `egg_onsets`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: EEG Encoding of Audio Envelope During DAF
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 3.5 s *, overlap = 0 *, target_events = [`baseline`, `adaption`]`
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | audio_envelope | continuous amplitude (a.u.); no mapping |
- **Evidence**:
  - 10.1523/JNEUROSCI.2294-24.2025 — Encoding model predicting continuous EEG from audio envelope during speech production with delayed auditory feedback; describes gammatone filter bank and envelope computation from raw audio channels
- **Notes**: Native misc channel 'audio_envelope' is pre-computed and available in the raw recording. The kernel does not need to derive this channel. tmax inferred from events.tsv sample showing baseline trial durations ~2.8-3.5s; overlap=0 as contiguous blocks. Only baseline and adaption events are used as target_events per the reference description; random1/random2 are excluded as they are not mentioned in the encoding model.

### Classical Task 2: EEG Encoding of Audio Onsets During DAF
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.5 s *, overlap = 0 *, target_events = [`baseline`, `adaption`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | audio_onsets | onset time (s); no mapping |
- **Evidence**:
  - 10.1523/JNEUROSCI.2294-24.2025 — Encoding model predicting continuous EEG from audio onset times during speech production; audio onsets mark speech event boundaries derived from audio envelope
- **Notes**: Native misc channel 'audio_onsets' is a pre-existing continuous channel in the raw EEG data (alongside 'audio' and 'audio_envelope'), not kernel-derived. The epoch structure follows long-event epochs anchored to trial phase onsets (baseline/adaption blocks) with tmin=0.0s and tmax=3.5s covering full block duration. tmax and overlap inferred from the epoch hint indicating full-block epochs; these are marked with * as they were not explicitly numerically specified in the reference.

### Classical Task 3: EEG encoding of EGG envelope during DAF
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3.5 s *, overlap = 0.0 *, target_events = [`baseline`, `adaption`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | egg_envelope | continuous amplitude (a.u.); no mapping |
- **Evidence**:
  - 10.1523/JNEUROSCI.2294-24.2025 — Encoding model predicting continuous EEG from electroglottography (EGG) envelope, capturing vocal fold activity during speech production under DAF
  - README — EGG minimally preprocessed with phase delay correction; audio/EGG included in EEG files as native misc channels
  - events.tsv (sub-01) — baseline trials with delay=0.004s, detected_delay=0/1; trial structure confirms DAF paradigm with per-trial delays
- **Notes**: tmax inferred from events.tsv sample showing baseline trial durations ~2.8-3.5s (mean ~3.2s); 3.5s chosen to capture full longest trial. overlap=0.0 assumed as default for non-overlapping long-event epochs. Both marked with * as inferred from data structure rather than explicitly stated in reference. The egg_envelope channel is native to the recording (continuous misc channel alongside EEG), not kernel-derived.

### Potential Task 1: DAF condition classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`baseline`, `adaption`, `random1`, `random2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `baseline` | 0 | Trial phase onset: baseline (no delay, delay=0.004s with detected_delay=0/1) |
  | `adaption` | 1 | Trial phase onset: adaption (fixed delay condition) |
  | `random1` | 2 | Trial phase onset: random1 (random delay condition 1) |
  | `random2` | 3 | Trial phase onset: random2 (random delay condition 2) |
- **Evidence**:
  - events.tsv (sub-01, sub-02, sub-16) — confirmed `baseline` trial_type with delay=0.004 and detected_delay values of 0 or 1, indicating no effective auditory feedback delay
  - pre-scan event inventory — confirmed existence of `adaption` (n=2560), `random1` (n=1600), `random2` (n=1600) as distinct trial_types alongside `baseline` (n=640)
  - README — describes delayed auditory feedback (DAF) paradigm with per-trial delays recorded in events sidecar; audio channel contains the delayed feedback the subject heard
  - dataset_description.json — "Delayed Auditory Feedback EEG/EGG" confirms experimental paradigm
- **Notes**: Trial durations from events.tsv sample range 2.7-3.5s; 4s epoch window captures full speech production block with margin. The four conditions represent different delay manipulation strategies: baseline (no effective delay), adaption (fixed delay), and two random delay conditions. All four are trial phase onset markers for distinct experimental conditions in the DAF paradigm, forming a valid 4-class classification of feedback condition types.

### Potential Task 2: DAF condition classification (2-class: baseline vs adaption)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`baseline`, `adaption`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `baseline` | 0 | Trial phase onset: baseline (no delay, 0.004s) |
  | `adaption` | 1 | Trial phase onset: adaption (fixed adaptive delay) |
- **Evidence**:
  - `sub-01_task-daf_events.tsv` — Confirmed baseline events with delay=0.004 and detected_delay=0, indicating no auditory feedback delay manipulation
  - `events.tsv` structure — Pre-scan established adaption events exist at n=2560 alongside baseline (n=640), forming the core DAF experimental contrast
  - `README` — Confirms delayed auditory feedback paradigm with per-trial delays; baseline represents the no-delay control condition
- **Notes**: This is a straightforward event-route classification using native event IDs. The two conditions represent the fundamental contrast in DAF research: normal feedback timing vs. delayed feedback. The epoch window of 4s is inferred from trial durations of ~2.7-3.5s to capture complete trial blocks. No kernel derivation needed — events are pre-existing in the recording.

### Potential Task 3: DAF condition classification (2-class: baseline vs random delays)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`baseline`, `random1`, `random2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `baseline` | 0 | Trial phase onset: baseline (no delay, delay=0.004s with detected_delay=0/1) |
  | `random1` | 1 | Trial phase onset: random1 (unpredictable delayed feedback condition) |
  | `random2` | 1 | Trial phase onset: random2 (unpredictable delayed feedback condition) |
- **Evidence**:
- **Notes**: Two-class classification pooling `random1` and `random2` into a single 'random delay' class (y=1) versus `baseline` (y=0). This tests neural discrimination between no feedback delay and unpredictable delayed feedback during speech production. The `random1` and `random2` events are distinct experimental conditions per the DAF paradigm but are merged here as they both represent random/unpredictable delay conditions compared to the baseline no-delay condition. Epoch timing inferred from trial structure; actual trial durations vary (observed ~2.7-3.5s in baseline samples) but 4s window captures full trial with margin.

### Potential Task 4: DAF condition classification (3-class: baseline vs adaption vs random pooled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`baseline`, `adaption`, `random1`, `random2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `baseline` | 0 | Trial phase onset: baseline |
  | `adaption` | 1 | Trial phase onset: adaption |
  | `random1` | 2 | Trial phase onset: random1 (pooled as 'random' class) |
  | `random2` | 2 | Trial phase onset: random2 (pooled as 'random' class) |
- **Evidence**:
  - sub-01_task-daf_events.tsv — Direct observation of baseline trial_type with delay=0.004 and detected_delay values of 0 or 1, confirming baseline condition as no-delay control
  - Pre-scan aggregate counts — Confirmed existence of adaption (2560), random1 (1600), and random2 (1600) events across dataset
  - README — Confirms delayed auditory feedback (DAF) paradigm with per-trial delays recorded in events sidecar
- **Notes**: This is a 3-way classification task where random1 and random2 are pooled into a single y=2 class representing 'random delay' conditions, versus baseline (y=0, no delay) and adaption (y=1, fixed delay). The pooling is justified by the DAF paradigm structure where both random1 and random2 represent variable/unpredictable delay regimes distinct from the fixed adaption and zero-delay baseline conditions. Epoch window inferred from standard speech production trial durations in DAF paradigms.

### Potential Task 5: Raw audio channel EEG encoding
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3.5 s *, overlap = 0 *, target_events = [`baseline`, `adaption`, `random1`, `random2`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |------------------|----------------|
  | audio | continuous (arbitrary units); no mapping |
- **Evidence**:
  - README — "The audio is the audio the subject heard, i.e. their delayed auditory feedback"
  - eeg.json — MiscChannelCount=2 confirms audio/EGG stored as native misc channels in EEG files
  - events.tsv — trial_type column confirms `baseline` events with delay=0.004 and detected_delay values, establishing DAF paradigm structure
- **Notes**: Native misc channel 'audio' is used directly as continuous regression target (archetype B1). This task tests fine-grained temporal encoding of raw waveform rather than envelope, requiring the kernel to preserve high-frequency audio content at 10kHz sampling. Long-event epochs span full trial durations (~2.8-3.5s) with overlap=0 for non-overlapping trials. tmax inferred from maximum observed baseline trial duration (~3.5s); actual trial durations vary by sentence length.

### Potential Task 6: Raw EGG channel EEG encoding
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0 s *, target_events = [`baseline`, `adaption`, `random1`, `random2`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | egg | continuous (arbitrary units); no mapping |
- **Evidence**:
- **Notes**: Archetype B1 — native misc channel 'egg' is pre-existing in the raw recording (not kernel-derived). The task tests whether raw EGG waveform (beyond derived envelope/onsets) contains predictive information for EEG during delayed auditory feedback. Long-event epochs span full speech block durations. tmax=4s is inferred from typical sentence reading durations in the events.tsv samples (2.7–3.5s) plus margin; overlap=0s for non-overlapping blocks. All four trial phase events are included as epoch anchors to maximize data coverage across experimental conditions.

## Data Quality Notes

- `subject_age` is missing for all subjects, limiting demographic analysis and age-related covariate control.
- `device` field is missing, so EEG amplifier/equipment details are not documented in structured metadata.
- `hand` field is present but encoded as numeric values (e.g., 56, 50, 100) rather than standard categorical handedness labels; these correspond to Edinburgh Handedness Inventory scores but may require interpretation.
- Event ID `adaption` appears to be a spelling variant of "adaptation" used consistently throughout the dataset; this is preserved as-is in native event labels and should not be treated as a data error.
- MISC channels (`audio`, `audio_envelope`, `audio_onsets`, `egg`, `egg_envelope`, `egg_onsets`) are native to the recording but their units and exact preprocessing provenance require verification; kernel notes flag these for manual review.
- Several epoch parameters (tmax, overlap, segment_length) are inferred from data structure rather than explicitly stated in reference materials, marked with * in task definitions.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
