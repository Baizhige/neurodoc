# BCIT Mind Wandering

**Dataset**: `openneuro_ds004121` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004121
**Category**: Complex Applied | **Subjects**: 60 | **Files (Completed)**: 60 | **Channels**: 74 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Subjects performed a long-duration simulated driving task involving lane maintenance, speed control, and a police vehicle vigilance sub-task (detecting a police car among traffic), while exposed to lateral perturbations and varying background audio conditions (silence vs. music vs. podcast). The mind wandering manipulation used periodic thought probes to assess on-task vs. off-task mental state. EEG biomarkers of mind wandering during driving were investigated.

## File Scan Result

> **Kernel SHA256**: `51c18647b8fa6328be7d9aae4b5c609c46c3537688d4e496328cdaf306bfab49`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Lateral Perturbation Direction Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [4311, 4312]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `4311` | 0 | Lateral perturbation - type 1 (e.g., leftward) |
| `4312` | 1 | Lateral perturbation - type 2 (e.g., rightward) |

- **Evidence (DOI)**: Dataset reference: https://openneuro.org/datasets/ds004121 DOI: https://doi.org/10.18112/openneuro.ds004121.v1.0.0
- **Kernel Notes**: Lateral perturbation events (4311/4312) mark directional perturbations delivered during simulated driving. Epoch at event onset with baseline window [-0.2, 0] s and post-stimulus window [0, 1.0] s captures the neural response to directional vehicle sway. Full BCIT codebook required to confirm perturbation direction encoding. Additional perturbation-related events (4210, 4220, 4230, 3111) may provide supplementary timing information.

### Normal Task 2: Mind Wandering State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.5 s, target_events = [2221, 2222]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `2221` | 0 | Thought probe cue - on-task label derived from response |
| `2221` | 1 | Thought probe cue - off-task label derived from response |
| `2222` | 0 | Thought probe cue (variant 2) - on-task |
| `2222` | 1 | Thought probe cue (variant 2) - off-task |

- **Evidence (DOI)**: Dataset reference: https://openneuro.org/datasets/ds004121 DOI: https://doi.org/10.18112/openneuro.ds004121.v1.0.0
- **Kernel Notes**: Thought probe onset events (2221/2222) mark the presentation of mind wandering probes. Label derivation requires matching probe onset events with subsequent response events (2241/2242 for response type 1, 2251/2252 for response type 2) to determine on-task (0) vs. off-task (1) state. The extended epoch window [-0.5, 3.5] s accommodates the pre-probe baseline and the full response window. Kernel must implement label routing logic to merge probe and response events into binary state labels.

### Potential Task 3: Audio Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [4621, 4622]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `4621` | 0 | Audio condition type 1 (e.g., silence) |
| `4622` | 1 | Audio condition type 2 (e.g., music/podcast) |

- **Evidence (DOI)**: Supported by dataset paradigm description (driving with varying background audio conditions)
- **Kernel Notes**: Audio condition events (4621/4622) mark transitions between silence, music, and podcast conditions. This task can serve as a between-condition variable for analyzing how background audio modulates neural activity during driving. Additional audio cue events (2811-2812) may provide supplementary auditory stimulus markers. Full codebook mapping required to confirm exact audio condition encoding.