# Audiocue walking study

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 273 | **Channels**: 115 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

A mobile brain-body imaging (MoBI) study where participants walked on a treadmill and adapted their gait to auditory tone sequences. Participants walked at their preferred cadence, uncued, or responded to tempo shifts (delay or advance) in an auditory metronome. The study investigated the neural dynamics of gait adaptation and rhythm entrainment during real-world locomotion. Each walking condition is a sustained state lasting multiple seconds.

## File Scan Result

> **Kernel SHA256**: `81bfb772f153e718e8aeaef593be73e7a95425f13a58ce43a6a1411dd56d50c4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `AdvanceTempo` | 1154 | event | raw | Step shortening response cue (faster tempo) |
| `AdvanceTempo_stream2` | 1154 | event | raw | Step shortening response cue (faster tempo, block 2) |
| `DelayTempo` | 2368 | event | raw | Step lengthening response cue (slower tempo) |
| `DelayTempo_stream2` | 2368 | event | raw | Step lengthening response cue (slower tempo, block 2) |
| `PreferredCadence` | 32100 | event | raw | Walking at preferred self-selected cadence |
| `PreferredCadence_stream2` | 26354 | event | raw | Preferred cadence walking (block 2) |
| `PreferredCadence_stream3` | 20237 | event | raw | Preferred cadence walking (block 3) |
| `PreferredCadence_stream4` | 20692 | event | raw | Preferred cadence walking (block 4) |
| `PreferredCadence_stream5` | 34011 | event | raw | Preferred cadence walking (block 5) |
| `PreferredCadence_stream6` | 28708 | event | raw | Preferred cadence walking (block 6) |
| `PreferredCadence_stream7` | 20365 | event | raw | Preferred cadence walking (block 7) |
| `PreferredCadence_stream8` | 21070 | event | raw | Preferred cadence walking (block 8) |
| `UncuedWalking` | 1154 | event | raw | Uncued walking without tempo guidance |
| `UncuedWalking_stream2` | 26402 | event | raw | Uncued walking (block 2) |
| `UncuedWalking_stream3` | 20441 | event | raw | Uncued walking (block 3) |
| `UncuedWalking_stream4` | 20635 | event | raw | Uncued walking (block 4) |
| `UncuedWalking_stream5` | 28730 | event | raw | Uncued walking (block 5) |
| `UncuedWalking_stream6` | 20482 | event | raw | Uncued walking (block 6) |
| `UncuedWalking_stream7` | 20683 | event | raw | Uncued walking (block 7) |
| `Walking_event_171` | 5715 | event | raw | Gait cycle marker (phase A) |
| `Walking_event_271` | 5678 | event | raw | Gait cycle marker (phase B) |
| `admin: marker-999` | 1153 | event | raw | BioSemi system status marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Tempo-shift gait adaptation (AdvanceTempo vs DelayTempo)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`AdvanceTempo`, `DelayTempo`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AdvanceTempo` | 0 | Step shortening response to faster tempo cue |
  | `DelayTempo` | 1 | Step lengthening response to slower tempo cue |
- **Evidence**:
  - DOI: 10.1038/s41597-019-0223-2 — Data descriptor for openneuro_ds001971 confirming step-locked epoching from -1s to 3s around heel strikes for tempo shift analysis
  - DOI: 10.1523/jneurosci.3543.15.2016 — EEG analysis of tempo shifts comparing beta band oscillatory networks between step-advance and step-delay adaptation in same 18-subject cohort
- **Kernel Notes**: Extract epochs time-locked to tempo shift onset events. `AdvanceTempo` marks cue shifts to faster tempo (step shortening); `DelayTempo` marks cue shifts to slower tempo (step lengthening). Exclude `STATUS` and `admin` markers from analysis. ICA recommended for motion artifact removal from treadmill walking.

### Potential Task 1: Four-class gait condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`PreferredCadence`, `PreferredCadence_stream2`, `PreferredCadence_stream3`, `PreferredCadence_stream4`, `PreferredCadence_stream5`, `PreferredCadence_stream6`, `PreferredCadence_stream7`, `PreferredCadence_stream8`, `UncuedWalking`, `UncuedWalking_stream2`, `UncuedWalking_stream3`, `UncuedWalking_stream4`, `UncuedWalking_stream5`, `UncuedWalking_stream6`, `UncuedWalking_stream7`, `AdvanceTempo`, `AdvanceTempo_stream2`, `DelayTempo`, `DelayTempo_stream2`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PreferredCadence`, `PreferredCadence_stream2-8` | 0 | Walking at preferred self-selected cadence |
  | `UncuedWalking`, `UncuedWalking_stream2-7` | 1 | Uncued walking without tempo guidance |
  | `DelayTempo`, `DelayTempo_stream2` | 2 | Step lengthening response to slower tempo cue |
  | `AdvanceTempo`, `AdvanceTempo_stream2` | 3 | Step shortening response to faster tempo cue |
- **Evidence**: Supported by paradigm structure from DOI: 10.1038/s41597-019-0223-2 describing the four walking conditions. The stream variants represent different experimental blocks with matching event counts.
- **Kernel Notes**: Include all stream variants to maximize data utilization across experimental blocks. Exclude `admin: marker-999` (BioSemi system marker) and `Walking_event_171/271` (gait cycle markers, not primary classification targets). Verify consistent channel selection across 273 files before pooling.

### Potential Task 2: Sustained walking state analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, segment_length = 4.0 s, overlap = 0.0, target_events = [`PreferredCadence`, `PreferredCadence_stream2`, `PreferredCadence_stream3`, `PreferredCadence_stream4`, `PreferredCadence_stream5`, `PreferredCadence_stream6`, `PreferredCadence_stream7`, `PreferredCadence_stream8`, `UncuedWalking`, `UncuedWalking_stream2`, `UncuedWalking_stream3`, `UncuedWalking_stream4`, `UncuedWalking_stream5`, `UncuedWalking_stream6`, `UncuedWalking_stream7`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PreferredCadence`, `PreferredCadence_stream2-8` | 0 | Sustained walking at preferred self-selected cadence |
  | `UncuedWalking`, `UncuedWalking_stream2-7` | 1 | Sustained uncued walking without tempo guidance |
- **Evidence**: Supported by epoch alignment recommendation for sustained walking analysis. High event counts (20k-34k per condition stream) confirm long-duration walking epochs suitable for 4-second segment extraction.
- **Kernel Notes**: Use epoch_by_long_event_hdf5 to capture sustained neural dynamics during steady-state locomotion. Focus on baseline walking conditions without tempo modifications to study intrinsic gait-related neural oscillations. ICA recommended for artifact removal from treadmill walking. The misc/response_time label (derived data) should preserve metadata during extraction.