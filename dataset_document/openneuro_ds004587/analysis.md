# IllusionGameEEG_data

**Dataset**: `openneuro_ds004587` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004587
**Category**: Sensory/Response | **Subjects**: 103 | **Files (Completed)**: 114 | **Channels**: 64 | **Sampling Rate**: 10000 Hz | **Manual Review**:

## Paradigm

Participants performed perceptual judgements on visual targets embedded within three classic visual illusions - Ebbinghaus, Muller-Lyer, and Vertical-Horizontal - to measure individual differences in illusion sensitivity and perceptual bias. The study investigates how prior experience and personality shape perceptual decision-making. EEG was recorded at 10 kHz; actual stimulus-event markers appear not to have been stored in events.tsv.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/LostSamples: 2` | 370 | admin | raw | Lost-samples boundary marker (exclude) |
| `New Segment/` | 115 | admin | raw | BrainVision segment boundary (exclude) |
| `New Segment/LostSamples: 3` | 111 | admin | raw | Lost-samples boundary marker (exclude) |
| `New Segment/LostSamples: 4` | 6 | admin | raw | Lost-samples boundary marker (exclude) |
| `Comment/motion` | 9 | admin | raw | Motion artifact annotation (exclude) |
| `Comment/ro post` | 6 | admin | raw | Post-recording comment (exclude) |
| `Comment/error` | 3 | admin | raw | Error annotation (exclude) |
| `Comment/rc pre` | 3 | admin | raw | Pre-recording comment (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

No stimulus/response trial events captured in events.tsv. All markers are administrative or artifact annotations.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: IG
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004587 DOI: https://doi.org/10.18112/openneuro.ds004587.v1.0.0


### Normal Task 1: Continuous Task EEG (segmentation)
- **Task Type**: regression
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None
- **Notes**: All events in events.tsv are administrative markers or artifact annotations. No stimulus/response trial events were captured. Trial structure may be recoverable from separate behavioral logs. Use sliding-window segmentation.

## Data Quality Notes

- All events are admin; no stimulus-locked epochs possible from events.tsv alone.
- Very high sampling rate (10 kHz) - downsample before analysis.
- Paper reference (ARSQ 2.0) may be a metadata mismatch; verify README.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
