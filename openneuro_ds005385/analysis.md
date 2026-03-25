# Resting-State EEG Before and After Cognitive Activity Across the Adult Lifespan (5-Year Follow-Up)

**Dataset**: `openneuro_ds005385` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005385
**Category**: Biological State | **Subjects**: 608 | **Files (Completed)**: 3264 | **Channels**: 65 | **Sampling Rate**: 1000 Hz

## Paradigm

Resting-state EEG was recorded with eyes open and eyes closed before and after a two-hour block of cognitive tasks (working memory, attention, processing speed) across a lifespan cohort of adults. A 5-year longitudinal follow-up is included. BrainVision S-codes (S1-S207+) encode the specific resting-state condition (pre/post x eyes open/closed) and session number.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005385

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 3375 | admin | raw | BrainVision segment boundary (exclude) |
| `S 4`-`S 7` | ~207 each | long | raw | Resting-state session markers (BrainVision S-codes) |
| `S 11`-`S 19` | ~204-205 each | long | raw | Resting-state condition codes |
| `S 14`-`S 16` | 68 each | long | raw | Resting-state condition (higher count subset) |
| `S196`-`S207` | ~205-207 each | long | raw | Session/condition index codes |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 4`, `S 7`, `S 11`, `S 19`, `S 14`, `S 16`, `S196`, `S207`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://doi.org/10.2196/32352


### Normal Task 1: Resting Condition Segmentation (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `boundary` (3375) is admin - exclude. S-codes encode resting condition and session; full decode from README/events.tsv required. 3264 files = 608 subjects x multiple sessions.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S 4` | 0 | Resting condition S4 |
 | `S 5` | 1 | Resting condition S5 |
 | `S 6` | 2 | Resting condition S6 |
 | `S 7` | 3 | Resting condition S7 |
## Data Quality Notes

- boundary markers (3375) are admin - exclude.
- Full S-code decode needed from README to identify pre/post and eyes-open/closed conditions.
- Large dataset (3264 files, 608 subjects); high variability across sessions and age groups.

## References

- **Reference**: `Gajewski et al., 2022, doi: 10.2196/32352`
