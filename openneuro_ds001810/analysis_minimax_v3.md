# EEG study of the attentional blink; before, during, and after transcranial Direct Current Stimulation (tDCS)

**Dataset**: `openneuro_ds001810` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001810
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 527 | **Channels**: 73.0 | **Sampling Rate**: 512.0 Hz

## Paradigm

Participants performed an attentional blink (AB) task using a Rapid Serial Visual Presentation (RSVP) stream to identify two targets (T1 and T2) embedded in a stream of distractors. EEG was recorded before, during, and after receiving anodal or cathodal transcranial Direct Current Stimulation (tDCS) to study how cortical excitability modulates the attentional blink - the impaired detection of T2 when it follows T1 within ~500 ms. BioSemi STATUS channel encodes trial conditions as numeric codes.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001810

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `T1_present_T2_present_lag3` | large | short | raw | T1 and T2 both present, short lag (within AB window) |
| `T1_present_T2_absent_lag3` | large | short | raw | T1 present, T2 absent, short lag |
| `T1_absent_T2_present` | large | short | raw | T1 absent, T2 present |
| `T1_T2_lag8` | large | short | raw | T1 and T2 at long lag (outside AB window) |
| `T1_onset` | large | short | raw | T1 target onset |
| `T2_onset` | large | short | raw | T2 target onset |
| `CM_baseline` (61440) | 261 files | admin | raw | BioSemi CM_in_range baseline - exclude |
| `CM_out_of_range` (61694) | 263 files | admin | raw | BioSemi CM status - exclude |
| `stimulus_onset` (61468) | large | short | raw | General stimulus onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus_onset`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Normal Task 1: Attentional Blink Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: BioSemi STATUS codes decoded via specific kernel. `CM_baseline` (61440) and `CM_out_of_range` (61694) are admin markers excluded. Regression target: `response_time`.

 | Event | y | Meaning |
 |-------|---|-法制---|
 | `T1_present_T2_present_lag3` | 0 | T2 detected within AB window |
 | `T1_present_T2_absent_lag3` | 1 | T2 missed within AB window |
 | `T1_absent_T2_present` | 2 | T2 present without T1 |
 | `T1_T2_lag8` | 3 | T2 detected outside AB window (control) |
 | `T1_onset` | 4 | T1 target onset |
 | `T2_onset` | 5 | T2 target onset |

## Data Quality Notes

- BioSemi STATUS channel encodes all triggers numerically; specific kernel maps codes to human-readable labels.
- `61440` (CM_in_range) and `61694` (CM_out_of_range) are BioSemi hardware status codes - exclude from analysis.
- Large dataset (527 files, 40 subjects x pre/during/post x anodal/cathodal conditions).
- Verify that event code mapping is correct against the original paper before downstream use.

