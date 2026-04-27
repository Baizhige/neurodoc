# Anticipatory differences between Attention and Expectation

**Dataset**: `openneuro_ds004502` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004502
**Category**: Sensory/Response | **Subjects**: 38 | **Files (Completed)**: 38 | **Channels**: 63 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

An experimental task investigating neural mechanisms of anticipation by comparing stimulus-driven attention and predictive expectation. Participants attended to auditory or visual stimuli with varying validity cues to disentangle attention (stimulus-driven) from expectation (predictive) effects on neural anticipatory activity. The experiment uses BrainVisionRecorder with a 63-channel EEG system.

## File Scan Result

> **Kernel SHA256**: `e55fcc32f1c0c663a6e615920982c072c481c866ed5b9ccccf663fa49fbe82aa`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 1 | admin | raw | Segment boundary marker |
| `S  1` | 3510 | event | raw | Visual cue onset (cue validity level 1) |
| `S  2` | 3211 | event | raw | Visual cue onset (cue validity level 2) |
| `S  3` | 2728 | event | raw | Auditory cue onset (cue validity level 3) |
| `S  4` | 2720 | event | raw | Auditory cue onset (cue validity level 4) |
| `S  5` | 2560 | event | raw | Instruction/prompt event |
| `S  6` | 2888 | event | raw | Instruction/prompt event variant |
| `S  7` | 3361 | event | raw | Fixation cross marker |
| `S  8` | 3360 | event | raw | Fixation cross marker variant |
| `S 17` | 3802 | event | raw | Attention - Visual high valid (S1V) |
| `S 18` | 3805 | event | raw | Attention - Visual low valid (S1V variant) |
| `S 19` | 3802 | event | raw | Attention - Auditory high valid (S1A) |
| `S 20` | 3803 | event | raw | Attention - Auditory low valid (S1A variant) |
| `S 21` | 2283 | event | raw | Attention - Visual high invalid |
| `S 22` | 2281 | event | raw | Attention - Visual low invalid |
| `S 23` | 2280 | event | raw | Attention - Auditory high invalid |
| `S 24` | 2282 | event | raw | Attention - Auditory low invalid |
| `S 25` | 2560 | event | raw | Response-related marker |
| `S 26` | 2880 | event | raw | Response-related marker |
| `S 27` | 3200 | event | raw | Response-related marker |
| `S 28` | 3520 | event | raw | Response-related marker |
| `S 29` | 3520 | event | raw | Response-related marker |
| `S 30` | 3200 | event | raw | Response-related marker |
| `S 31` | 2880 | event | raw | Response-related marker |
| `S 32` | 2560 | event | raw | Response-related marker |
| `S 33` | 4104 | event | raw | Expectation - Visual valid cue (S3V) |
| `S 34` | 456 | event | raw | Expectation - Visual invalid cue (S3V invalid) |
| `S 35` | 4104 | event | raw | Expectation - Visual valid cue (S5V) |
| `S 36` | 456 | event | raw | Expectation - Visual invalid cue (S5V invalid) |
| `S 37` | 4104 | event | raw | Expectation - Auditory valid cue (S3A) |
| `S 38` | 456 | event | raw | Expectation - Auditory invalid cue (S3A invalid) |
| `S 39` | 4104 | event | raw | Expectation - Auditory valid cue (S5A) |
| `S 40` | 456 | event | raw | Expectation - Auditory invalid cue (S5A invalid) |
| `S 41` | 1368 | event | raw | Expectation - Modality cue valid |
| `S 42` | 152 | event | raw | Expectation - Modality cue invalid |
| `S 43` | 1368 | event | raw | Expectation - Modality cue valid |
| `S 44` | 190 | event | raw | Expectation - Modality cue invalid |
| `S 45` | 1368 | event | raw | Expectation - Modality cue valid |
| `S 46` | 152 | event | raw | Expectation - Modality cue invalid |
| `S 47` | 1368 | event | raw | Expectation - Modality cue valid |
| `S 48` | 114 | event | raw | Expectation - Modality cue invalid |
| `S 51` | 1732 | event | raw | Expectation - Target stimulus high freq |
| `S 52` | 41 | event | raw | Expectation - Target stimulus low freq |
| `S 53` | 608 | event | raw | Expectation - Target stimulus high freq |
| `S 54` | 610 | event | raw | Expectation - Target stimulus high freq |
| `S 55` | 608 | event | raw | Expectation - Target stimulus low freq |
| `S 56` | 609 | event | raw | Expectation - Target stimulus low freq |
| `S 57` | 609 | event | raw | Expectation - Target stimulus low freq |
| `S 58` | 38 | event | raw | Session/block marker |
| `S 59` | 38 | event | raw | Session/block marker |
| `Stimulus/S100` | 38 | event | raw | Stimulus delivery marker (auditory) |
| `Stimulus/S101` | 38 | event | raw | Stimulus delivery marker (visual) |
| `Stimulus/S102` | 38 | event | raw | Stimulus delivery marker (auditory) |
| `Stimulus/S103` | 38 | event | raw | Stimulus delivery marker (visual) |
| `Stimulus/S104` | 38 | event | raw | Stimulus delivery marker (auditory) |
| `Stimulus/S105` | 38 | event | raw | Stimulus delivery marker (visual) |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores eye movement monitoring channels for artifact rejection
- **Candidate Labels**: `EOGn`, `EOGp`
- **Kernel Note**: EOGn and EOGp channels record vertical and horizontal electrooculographic signals for detecting eye blinks and movements. Verify channel roles and units before preprocessing.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | partial (37/38) | N/A |
| `device` | missing | Device manufacturer/model not specified in metadata |

## Tasks

### Classical Task 1: Attexp BIDS Task - Attention vs Expectation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [S 17, S 18, S 19, S 20, S 21, S 22, S 23, S 24, S 33, S 34, S 35, S 36, S 37, S 38, S 39, S 40, S 41, S 42, S 43, S 44, S 45, S 46, S 47, S 48, S 51, S 52, S 53, S 54, S 55, S 56, S 57]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|--------|
| `S 17` | 0 | Attention condition |
| `S 18` | 0 | Attention condition |
| `S 19` | 0 | Attention condition |
| `S 20` | 0 | Attention condition |
| `S 21` | 0 | Attention condition |
| `S 22` | 0 | Attention condition |
| `S 23` | 0 | Attention condition |
| `S 24` | 0 | Attention condition |
| `S 33` | 1 | Expectation condition |
| `S 34` | 1 | Expectation condition |
| `S 35` | 1 | Expectation condition |
| `S 36` | 1 | Expectation condition |
| `S 37` | 1 | Expectation condition |
| `S 38` | 1 | Expectation condition |
| `S 39` | 1 | Expectation condition |
| `S 40` | 1 | Expectation condition |
| `S 41` | 1 | Expectation condition |
| `S 42` | 1 | Expectation condition |
| `S 43` | 1 | Expectation condition |
| `S 44` | 1 | Expectation condition |
| `S 45` | 1 | Expectation condition |
| `S 46` | 1 | Expectation condition |
| `S 47` | 1 | Expectation condition |
| `S 48` | 1 | Expectation condition |
| `S 51` | 1 | Expectation condition |
| `S 52` | 1 | Expectation condition |
| `S 53` | 1 | Expectation condition |
| `S 54` | 1 | Expectation condition |
| `S 55` | 1 | Expectation condition |
| `S 56` | 1 | Expectation condition |
| `S 57` | 1 | Expectation condition |

- **Evidence**: DOI: https://doi.org/10.18112/openneuro.ds004502.v1.0.1 | OpenNeuro dataset metadata defining BIDS task 'attexp'
- **Kernel Notes**: Trigger codes S 17-S 24 (~22.8k total) map to attention condition trials; trigger codes S 33-S 57 (~22k+ total) map to expectation condition trials. Count asymmetry within expectation codes (e.g., S 33 at 4104 vs S 34 at 456) indicates unequal trial probability per cue validity level. Maintain versioned trigger decoding table.

### Normal Task 1: Cue Validity Sub-condition Classification (Expectation Trials)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [S 33, S 34, S 35, S 36, S 37, S 38, S 39, S 40]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---------|
| `S 33` | 0 | High-frequency expectation (valid cue) |
| `S 35` | 0 | High-frequency expectation (valid cue) |
| `S 37` | 0 | High-frequency expectation (valid cue) |
| `S 39` | 0 | High-frequency expectation (valid cue) |
| `S 34` | 1 | Low-frequency expectation (invalid cue) |
| `S 36` | 1 | Low-frequency expectation (invalid cue) |
| `S 38` | 1 | Low-frequency expectation (invalid cue) |
| `S 40` | 1 | Low-frequency expectation (invalid cue) |

- **Evidence**: Event count patterns (S 33/S 35/S 37/S 39 at ~4104 each vs S 34/S 36/S 38/S 40 at ~456 each, ~9:1 ratio) strongly suggest validity-based trial grouping consistent with attention/expectation paradigm literature.
- **Kernel Notes**: The ~9:1 count ratio between high and low frequency events within expectation codes suggests explicit validity manipulation (valid vs invalid cues). This task requires detailed semantic mapping from events.tsv to confirm validity labels. Stimulus/S100-S105 events (38 each) appear to be stimulus delivery markers separate from cue validity markers.

### Potential Task 1: Stimulus Modality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [Stimulus/S100, Stimulus/S101, Stimulus/S102, Stimulus/S103, Stimulus/S104, Stimulus/S105]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---------|
| `Stimulus/S100` | 0 | Auditory stimulus delivery |
| `Stimulus/S101` | 1 | Visual stimulus delivery |
| `Stimulus/S102` | 0 | Auditory stimulus delivery |
| `Stimulus/S103` | 1 | Visual stimulus delivery |
| `Stimulus/S104` | 0 | Auditory stimulus delivery |
| `Stimulus/S105` | 1 | Visual stimulus delivery |

- **Evidence**: Plausible from paradigm description ("attended to auditory or visual stimuli") and consistent event counts (38 each) suggest stimulus delivery markers. Exact modality mapping requires events.tsv confirmation.
- **Kernel Notes**: Stimulus/S100-S105 events are separate from cue validity markers and appear at consistent 38 counts per subject, suggesting stimulus delivery events aligned to trial structure.