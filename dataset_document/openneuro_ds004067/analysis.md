# Moral conviction and metacognitive ability shape multiple stages of information processing

**Dataset**: `openneuro_ds004067` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004067
**Category**: High-level Mental | **Subjects**: 80 | **Files (Completed)**: 83 | **Channels**: 63 | **Sampling Rate**: 2000 Hz | **Manual Review**: Pending

## Paradigm

Participants evaluated their support for sociopolitical protest photographs following social influence cues from a fictitious community to assess how moral conviction and metacognitive ability modulate information processing. EEG was recorded while participants viewed protest photos (supporting or opposing social movements), received social feedback (high/low/medium agreement), and provided attitude ratings. The study examined how moral convictions and metacognitive ability shape early and late stages of social information processing.

## File Scan Result

> **Kernel SHA256**: `2e0660a070b8e1df6267ff16adb503545053bae4750a4a167344ae026cdc849c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Response/R  1` | 14 | event | raw | Response trigger marker (unspecified) |
| `Stimulus/ClipTaskEnd` | 79 | admin | raw | Clip task block end |
| `Stimulus/ClipTaskStart` | 79 | admin | raw | Clip task block start |
| `Stimulus/Heroic6end` | 79 | admin | raw | Heroic clip 6 block end |
| `Stimulus/Heroic6start` | 79 | admin | raw | Heroic clip 6 block start |
| `Stimulus/Heroic7end` | 79 | admin | raw | Heroic clip 7 block end |
| `Stimulus/Heroic7start` | 79 | admin | raw | Heroic clip 7 block start |
| `Stimulus/Moral_Neutral` | 60 | event | raw | Moral attitude cue - neutral |
| `Stimulus/Moral_Oppose` | 3049 | event | raw | Moral attitude cue - oppose |
| `Stimulus/Moral_Support` | 3477 | event | raw | Moral attitude cue - support |
| `Stimulus/Nonmoral_Neutral` | 2132 | event | raw | Non-moral attitude cue - neutral |
| `Stimulus/Nonmoral_Oppose` | 3100 | event | raw | Non-moral attitude cue - oppose |
| `Stimulus/Nonmoral_Support` | 2307 | event | raw | Non-moral attitude cue - support |
| `Stimulus/PhotoOppose` | 7085 | event | raw | Oppose-framing sociopolitical protest photo onset |
| `Stimulus/PhotoSupport` | 7117 | event | raw | Support-framing sociopolitical protest photo onset |
| `Stimulus/ProtestEnd` | 80 | admin | raw | Protest task block end |
| `Stimulus/ProtestStart` | 80 | admin | raw | Protest task block start |
| `Stimulus/Resp1` | 2680 | event | raw | Rating response level 1 |
| `Stimulus/Resp2` | 2182 | event | raw | Rating response level 2 |
| `Stimulus/Resp3` | 1650 | event | raw | Rating response level 3 |
| `Stimulus/Resp4` | 2175 | event | raw | Rating response level 4 |
| `Stimulus/Resp5` | 2186 | event | raw | Rating response level 5 |
| `Stimulus/Resp6` | 1401 | event | raw | Rating response level 6 |
| `Stimulus/Resp7` | 1573 | event | raw | Rating response level 7 |
| `Stimulus/RestEnd` | 79 | admin | raw | Resting block end |
| `Stimulus/RestStart` | 79 | admin | raw | Resting block start |
| `Stimulus/S  1` | 57 | admin | raw | System/sync marker (unspecified) |
| `Stimulus/S  2` | 80 | admin | raw | System/sync marker |
| `Stimulus/S  4` | 1 | admin | raw | System marker (rare event) |
| `Stimulus/S  7` | 1 | admin | raw | System marker (rare event) |
| `Stimulus/S 12` | 16 | admin | raw | System marker (periodic) |
| `Stimulus/S 13` | 12 | admin | raw | System marker (periodic) |
| `Stimulus/S 14` | 140 | admin | raw | System marker (periodic) |
| `Stimulus/S 15` | 140 | admin | raw | System marker (periodic) |
| `Stimulus/SocHigh` | 4733 | event | raw | Social influence cue - high agreement |
| `Stimulus/SocLow` | 4732 | event | raw | Social influence cue - low agreement |
| `Stimulus/SocMed` | 4732 | event | raw | Social influence cue - medium agreement |
| `Stimulus/Social5end` | 79 | admin | raw | Social clip 5 block end |
| `Stimulus/Social5start` | 79 | admin | raw | Social clip 5 block start |
| `Stimulus/Social6end` | 79 | admin | raw | Social clip 6 block end |
| `Stimulus/Social6start` | 79 | admin | raw | Social clip 6 block start |
> **Event Type Description**:
> - `event`: Short stimulus onset marker (presentation duration <2 s), used for `epoch_by_event_hdf5`
> - `admin`: System/boundary marker, **not used for epoch**


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Support vs Oppose Photo Classification (binary)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["Stimulus/PhotoSupport", "Stimulus/PhotoOppose"]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---------|
| `Stimulus/PhotoSupport` | 0 | Support-framing sociopolitical protest photo |
| `Stimulus/PhotoOppose` | 1 | Oppose-framing sociopolitical protest photo |

- **Evidence**: DOI: 10.1016/j.cortex.2022.03.008
- **Kernel Notes**: Epoch window captures early visual ERP components (P1/N1) and extends through attitude formation period. Negative tmin allows baseline correction. Trigger decoding table must be versioned and auditable. Verify PhotoSupport/PhotoOppose event timing offset between BIDS sidecar and raw trigger channel.

### Normal Task 1: Moral vs Nonmoral Attitude Classification (binary)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["Stimulus/Moral_Support", "Stimulus/Moral_Oppose", "Stimulus/Nonmoral_Support", "Stimulus/Nonmoral_Oppose"]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---------|
| `Stimulus/Moral_Support` | 0 | Moral attitude cue - support |
| `Stimulus/Moral_Oppose` | 0 | Moral attitude cue - oppose |
| `Stimulus/Nonmoral_Support` | 1 | Non-moral attitude cue - support |
| `Stimulus/Nonmoral_Oppose` | 1 | Non-moral attitude cue - oppose |

- **Evidence**: DOI: 10.1016/j.cortex.2022.03.008 (study examines moral conviction as key experimental factor; partial support for classification mapping)
- **Kernel Notes**: Standard window captures early moral conviction processing and late positive complex. Note: `Moral_Neutral` (60 trials) and `Nonmoral_Neutral` (2132 trials) events are also available for 6-class or regression approaches.

### Normal Task 2: Moral Conviction Level Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["Stimulus/Moral_Support", "Stimulus/Moral_Oppose", "Stimulus/Nonmoral_Support", "Stimulus/Nonmoral_Oppose"]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---------|
| `Stimulus/Moral_Support` | 0 | Moral conviction - support framing |
| `Stimulus/Moral_Oppose` | 1 | Moral conviction - oppose framing |
| `Stimulus/Nonmoral_Support` | 2 | Non-moral attitude - support framing |
| `Stimulus/Nonmoral_Oppose` | 3 | Non-moral attitude - oppose framing |

- **Evidence**: DOI: 10.1016/j.cortex.2022.03.008 (full factorial design with moral/nonmoral × support/oppose)
- **Kernel Notes**: Tests interaction between moral conviction and protest stance. Requires larger sample for 4-class discrimination.

### Potential Task 1: Social Influence Level Classification (3-class)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = ["Stimulus/SocHigh", "Stimulus/SocMed", "Stimulus/SocLow"]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `Stimulus/SocHigh` | 0 | Social influence cue - high agreement |
| `Stimulus/SocMed` | 1 | Social influence cue - medium agreement |
| `Stimulus/SocLow` | 2 | Social influence cue - low agreement |

- **Evidence**: Paradigm description; DOI: 10.10106/j.cortex.2022.03.008 references social influence cues as experimental manipulation
- **Kernel Notes**: Slightly longer tmax (1.5 s) recommended to capture later processing stages related to social feedback integration and metacognitive evaluation. Ensure inter-stimulus intervals prevent overlap contamination with preceding photo events.

### Potential Task 2: Response Rating Regression
- **Task Type**: regression
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["Stimulus/Resp1", "Stimulus/Resp2", "Stimulus/Resp3", "Stimulus/Resp4", "Stimulus/Resp5", "Stimulus/Resp6", "Stimulus/Resp7"]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---------|
| `Stimulus/Resp1` | 1 | Rating response level 1 |
| `Stimulus/Resp2` | 2 | Rating response level 2 |
| `Stimulus/Resp3` | 3 | Rating response level 3 |
| `Stimulus/Resp4` | 4 | Rating response level 4 |
| `Stimulus/Resp5` | 5 | Rating response level 5 |
| `Stimulus/Resp6` | 6 | Rating response level 6 |
| `Stimulus/Resp7` | 7 | Rating response level 7 |

- **Evidence**: Paradigm description; DOI: 10.10106/j.cortex.2022.03.008 (perceptual confidence task for metacognition assessment)
- **Kernel Notes**: Response-locked epoching could provide alternative alignment but requires knowing response timing. The 7-point rating scale spans both attitude and confidence dimensions.

### Potential Task 3: Combined Moral Conviction × Social Influence Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: segment_length = Needs verification, overlap = Needs verification, segment_alignment = stimulus onset
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**: Combined labeling of moral conviction level and social influence condition across trial segments
- **Evidence**: Paradigm description; DOI: 10.10106/j.cortex.2022.03.008 (examined interaction between moral conviction and social influence cues)
- **Kernel Notes**: This task requires segment-level labeling to capture trial structure where photos precede social cues. Admin markers (ProtestStart/End, ClipTaskStart/End, Rest blocks) must be excluded.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
