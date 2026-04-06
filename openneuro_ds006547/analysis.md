# Visual EEG Study (BrainVision -> BIDS)

**Dataset**: `openneuro_ds006547` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006547
**Category**: Sensory/Response | **Subjects**: 31 | **Files (Completed)**: 31 | **Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

High-density EEG recordings were collected during a visual stimulation task using a BrainVision system, subsequently converted to BIDS format. Participants viewed visual stimuli under multiple conditions encoded by numeric BrainVision trigger codes (S2 through S56). The 30 distinct stimulus codes suggest a factorial or multi-condition visual paradigm covering perceptual and attentional manipulations.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 5` | 31 | event | raw | Visual stimulus condition S5 |
| `Stimulus/S 2` | 31 | event | raw | Visual stimulus condition S2 |
| `Stimulus/S 42` | 31 | event | raw | Visual stimulus condition S42 |
| `Stimulus/S 11` | 31 | event | raw | Visual stimulus condition S11 |
| `Stimulus/S 51` | 31 | event | raw | Visual stimulus condition S51 |
| `Stimulus/S 8` | 31 | event | raw | Visual stimulus condition S8 |
| `Stimulus/S 45` | 31 | event | raw | Visual stimulus condition S45 |
| `Stimulus/S 56` | 31 | event | raw | Visual stimulus condition S56 |
| `Stimulus/S 3` | 31 | event | raw | Visual stimulus condition S3 |
| `Stimulus/S 46` | 31 | event | raw | Visual stimulus condition S46 |
| `Stimulus/S 21` | 31 | event | raw | Visual stimulus condition S21 |
| `Stimulus/S 7` | 31 | event | raw | Visual stimulus condition S7 |
| `Stimulus/S 12` | 31 | event | raw | Visual stimulus condition S12 |
| `Stimulus/S 6` | 31 | event | raw | Visual stimulus condition S6 |
| `Stimulus/S 16` | 31 | event | raw | Visual stimulus condition S16 |
| `Stimulus/S 19` | 31 | event | raw | Visual stimulus condition S19 |
| `Stimulus/S 44` | 31 | event | raw | Visual stimulus condition S44 |
| `Stimulus/S 10` | 31 | event | raw | Visual stimulus condition S10 |
| `Stimulus/S 55` | 31 | event | raw | Visual stimulus condition S55 |
| `Stimulus/S 17` | 31 | event | raw | Visual stimulus condition S17 |
| `Stimulus/S 41` | 31 | event | raw | Visual stimulus condition S41 |
| `Stimulus/S 53` | 31 | event | raw | Visual stimulus condition S53 |
| `Stimulus/S 50` | 31 | event | raw | Visual stimulus condition S50 |
| `Stimulus/S 22` | 31 | event | raw | Visual stimulus condition S22 |
| `Stimulus/S 20` | 31 | event | raw | Visual stimulus condition S20 |
| `Stimulus/S 52` | 31 | event | raw | Visual stimulus condition S52 |
| `Stimulus/S 14` | 31 | event | raw | Visual stimulus condition S14 |
| `Stimulus/S 13` | 31 | event | raw | Visual stimulus condition S13 |
| `Stimulus/S 54` | 31 | event | raw | Visual stimulus condition S54 |
| `Stimulus/S 4` | 31 | event | raw | Visual stimulus condition S4 |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 5`, `Stimulus/S 2`, `Stimulus/S 42`, `Stimulus/S 11`, `Stimulus/S 51`, `Stimulus/S 8`, `Stimulus/S 45`, `Stimulus/S 56`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Potential Task 1: Visual Condition Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30 distinct stimulus codes; decode from events.tsv to determine condition grouping. All codes appear in all 31 files (perfectly balanced). BrainVision format; verify event alignment with EEG data.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Stimulus/S 5` | 0 | Visual condition S5 |
 | `Stimulus/S 2` | 1 | Visual condition S2 |
 | `Stimulus/S 42` | 2 | Visual condition S42 |
 | `Stimulus/S 11` | 3 | Visual condition S11 |
 | `Stimulus/S 51` | 4 | Visual condition S51 |
 | `Stimulus/S 8` | 5 | Visual condition S8 |
 | `Stimulus/S 45` | 6 | Visual condition S45 |
 | `Stimulus/S 56` | 7 | Visual condition S56 |
 | `Stimulus/S 3` | 8 | Visual condition S3 |
 | `Stimulus/S 46` | 9 | Visual condition S46 |
 | `Stimulus/S 21` | 10 | Visual condition S21 |
 | `Stimulus/S 7` | 11 | Visual condition S7 |
 | `Stimulus/S 12` | 12 | Visual condition S12 |
 | `Stimulus/S 6` | 13 | Visual condition S6 |
 | `Stimulus/S 16` | 14 | Visual condition S16 |
 | `Stimulus/S 19` | 15 | Visual condition S19 |
 | `Stimulus/S 44` | 16 | Visual condition S44 |
 | `Stimulus/S 10` | 17 | Visual condition S10 |
 | `Stimulus/S 55` | 18 | Visual condition S55 |
 | `Stimulus/S 17` | 19 | Visual condition S17 |
 | `Stimulus/S 41` | 20 | Visual condition S41 |
 | `Stimulus/S 53` | 21 | Visual condition S53 |
 | `Stimulus/S 50` | 22 | Visual condition S50 |
 | `Stimulus/S 22` | 23 | Visual condition S22 |
 | `Stimulus/S 20` | 24 | Visual condition S20 |
 | `Stimulus/S 52` | 25 | Visual condition S52 |
 | `Stimulus/S 14` | 26 | Visual condition S14 |
 | `Stimulus/S 13` | 27 | Visual condition S13 |
 | `Stimulus/S 54` | 28 | Visual condition S54 |
 | `Stimulus/S 4` | 29 | Visual condition S4 |

## Data Quality Notes

- BrainVision format converted to BIDS; verify event alignment with EEG data.
- Large number of distinct event types (30); group by experimental condition before classification.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review