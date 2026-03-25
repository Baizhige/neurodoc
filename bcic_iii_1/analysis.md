# BCI Competition III Dataset 1 (Directional Motor Imagery EEG)

**Dataset**: `bcic_iii_1` | **Year**: 2005 | **URL**: https://www.bbci.de/competition/iii/download/
**Category**: Action/Output | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

A single subject performed directional motor imagery (BCI Competition III, 2005). Visual arrow cues prompted 4-second motor imagery periods (two classes: left and right/foot). The dataset is stored in a single GDF file (`BCI2005_I.gdf`). The GDF format embeds event annotations natively; MNE reads them automatically. No age or sex information is available in the public release.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iii/download/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `768` | 377 | admin | raw | Start of a trial (pre-cue marker) |
| `769` | 138 | short | raw | Cue onset - class 1 (left hand / motor imagery direction 1) |
| `772` | 139 | short | raw | Cue onset - class 2 (right hand or foot, motor imagery direction 2) |
| `783` | 100 | admin | raw | Cue unknown (evaluation-set placeholder) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: The official BCI Competition III dataset description identifies directional motor-imagery decoding as the benchmark objective for this dataset. Source: https://www.bbci.de/competition/iii/ Official description file: `references/website_des.txt`


### Normal Task 1: Binary Motor Imagery Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Event codes follow the GDF/BCIC standard but are not renamed by the kernel; they appear as numeric strings. Event `768` is a trial-onset marker preceding the cue and should be excluded from classification targets. Event `783` (cue unknown) appears in unlabeled evaluation data and should also be excluded unless the test labels are available.

| Event | y | Meaning |
|-------|---|---------|
| `769` | 0 | Motor imagery class 1 (left-hand direction) |
| `772` | 1 | Motor imagery class 2 (right-hand or foot direction) |
## Data Quality Notes

- Single-subject dataset; results cannot be generalized across subjects.
- Very small dataset (1 file, 377 trials); statistical power is limited.
- High sampling rate (1000 Hz); consider downsampling to <=250 Hz.
- No demographic information available.
- GDF event codes are kept as numeric strings in MNE annotations; ensure correct integer parsing.

## References

- **Reference**: BCI Competition III (2005), Dataset 1 - Directionally Modulated EEG Signals. https://www.bbci.de/competition/iii/
