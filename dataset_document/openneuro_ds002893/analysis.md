# Auditory-Visual Shift Study

**Dataset**: `openneuro_ds002893` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002893
**Category**: Sensory/Response | **Subjects**: 49 | **Files (Completed)**: 52 | **Channels**: 36 | **Sampling Rate**: 250 Hz | **Manual Review**: Pending

## Paradigm

An interleaved dual-oddball task in which subjects selectively attended to either auditory or visual stimuli while switching between modalities based on spoken and printed attention cue instructions. The study investigated modality-specificity of sensory aging in vision and audition using event-related potentials. Attention states (`attend_auditory`, `attend_visual`) are sustained conditions lasting multiple trials; `shift_attention` marks the transition cue between modalities.

## File Scan Result

> **Kernel SHA256**: `62b3f85ef2c0cb23ae21218e39336513a3379d9f784bfb26e492951f28f90602`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
No MISC labels identified in current scan.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (48/52) | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: ERP Target Detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [Needs verification]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Target vs non-target stimulus events (standard/deviant classification)

| Event | y | Meaning |
|---|---|---|
| `target` | 1 | Target stimulus (oddball) |
| `standard` | 0 | Standard/background stimulus |
| `deviant` | 1 | Deviant stimulus (if distinct from target) |

- **Evidence**: DOI: https://doi.org/10.18112/openneuro.ds002893.v2.0.0 | Dual-oddball paradigm core study objective; standard P300/Oddball target detection supported by paradigm description alone.
- **Kernel Notes**: No events detected in kernel scan. Paradigm logic supports P300 target classification. Verify event IDs in accompanying *_events.tsv files. Standard oddball/P300 epoch window captures classic ERP response. Alignment to target stimulus onset.

---

### Potential Task 2: Attention Modality Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [attend_auditory, attend_visual]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: Sustained attention modality blocks

| Event | y | Meaning |
|---|---|---|
| `attend_auditory` | 0 | Sustained auditory attention block |
| `attend_visual` | 1 | Sustained visual attention block |

- **Evidence**: DOI: https://doi.org/10.18112/openneuro.ds002893.v2.0.0 | Interleaved dual-oddball with selective attention to auditory or visual modalities supported by paradigm description.
- **Kernel Notes**: Sustained `attend_*` states require overlapping sliding windows to capture extended neural states. The 0.5 overlap enables continuous modality classification. `shift_attention` is admin/transition-only; exclude from classification target. Derivation of high-level attention labels may require Type 2 super meta integration.

---

### Potential Task 3: Attention Shift Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [shift_attention]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Attention modality switch events

| Event | y | Meaning |
|---|---|---|
| `shift_attention` | 1 | Attention modality transition cue |

- **Evidence**: DOI: https://doi.org/10.18112/openneuro.ds002893.v2.0.0 | Spoken and printed attention cue instructions for modality switching supported by paradigm description.
- **Kernel Notes**: `shift_attention` is a transition cue marking the moment of modality switching. Epoching around it can reveal cue-locked ERP components (CNV, frontal midlines) associated with attention reorientation. Treat as admin event; do not include in sustained attention classification targets.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
