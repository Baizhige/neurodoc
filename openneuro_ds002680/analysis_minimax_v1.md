# Go-nogo categorization and detection task

**Dataset**: `openneuro_ds002680` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002680
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 350 | **Channels**: 31.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants performed a visual go/no-go paradigm involving rapid animal categorization and image recognition tasks with brief 20 ms stimulus presentations. Go trials required a button-press response when an animal was detected (or a target category matched); no-go trials required withholding response. Each run contains approximately 100 stimulus events and ~50 response events, suggesting roughly 50% go rate. The paradigm studies rapid visual processing and response inhibition.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, reaction time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002680

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | ~35,000 (350x100) | short | raw | Visual stimulus onset (20 ms image presentation) |
| `response` | ~18,000 (350x52) | short | raw | Button-press go response |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Go/No-Go Visual Categorization Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`stimulus`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `animal target` (go) | 1 | Correct go response to animal image requiring button press |
  | `non-animal distractor` (no-go) | 0 | Correct no-go response to non-animal image requiring withholding |
- **Super Meta Notes**: N/A
- **Evidence**:
  - DOI: 10.1038/s41598.023.27528-0 — Uses the openneuro_ds002680 Go/No-go dataset to compare brain-evoked potentials between correct animal targets (go responses) and correct non-animal distractors (no-go responses) using epoch extraction from -1 to 2 seconds relative to stimulus onset.
  - DOI: 10.1016/S0925-2312(02)00415-0 — Applies ICA to EEG data from a rapid go-nogo visual categorization task with 20ms animal/no-animal image stimuli, analyzing stimulus-locked single-trial epochs to identify brain source dynamics in target vs non-target conditions.
- **Kernel Notes**: Extract epochs aligned to stimulus onset. For classification, derive labels from stimulus type: animal images = go (y=1), non-animal images = no-go (y=0). Consider also the faster processing window tmin=-0.3s tmax=0.7s mentioned in paper 1 for efficiency.

### Normal Task 1: Stimulus-Locked ERP / Reaction Time Regression (regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to stimulus onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: N/A (null (regression only; stimulus serves as epoch anchor))
- **Notes**: Go/no-go structure: ~100 stimuli per run, ~52 responses (go trials). Regression target is response_time on go trials. For classification, go vs no-go labels would need to be inferred from presence/absence of a response after each stimulus.

- **Regression target**: `response_time` (reaction time from stimulus to response, from misc channel)

## Data Quality Notes

- Large dataset: 350 runs; verify subject/session structure from BIDS metadata.
- ~50% go rate per run based on stimulus (100) vs response (52) counts.
- 1000 Hz sampling rate; consider downsampling to 250 Hz for efficiency.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Go-nogo categorization and detection task`
