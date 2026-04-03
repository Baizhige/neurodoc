# A Resource for Assessing Dynamic Binary Choices in the Adult Brain Using EEG and Mouse-Tracking

**Dataset**: `openneuro_ds003766` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003766
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 217
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed dynamic decision-making tasks including food preference choices and semantic judgments while high-density EEG and continuous mouse-tracking were recorded simultaneously. The study captures the real-time neural dynamics of binary choice formation, including evidence accumulation, conflict, and response selection. Numeric trigger codes (0200-0506 series) encode stimulus, response, and condition information. Boundary markers appear in some files from EEGLAB preprocessing.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003766

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0400` | 186 | short | raw | Trigger code 0400 (stimulus/task event - decode from events.tsv) |
| `0500` | 186 | short | raw | Trigger code 0500 (stimulus/task event - decode from events.tsv) |
| `0401`-`0403` | 124 each | short | raw | Stimulus variant trigger codes |
| `0503`, `0505`, `0506` | 124 each | short | raw | Response/outcome trigger codes |
| `0501` | 95 | short | raw | Trigger code 0501 |
| `0202`-`0221` | 93 each | short | raw | Trial-phase trigger codes (0200 series) |
| `0210` | 93 | short | raw | Trigger code 0210 |
| `boundary` | 97 | admin | raw | EEGLAB boundary marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Binary choice classification (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s *, target_events = [`0500`, `0501`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `0500` | 0 | Left choice (food preference task) |
  | `0501` | 1 | Right choice (food preference task) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01538-5 — SVM classification decodes left vs right choices from EEG epochs (-200ms to 800ms), achieving 67-77% accuracy across three choice tasks.
- **Kernel Notes**: Epoch from stimulus onset (tmin=-0.2s baseline) to tmax=0.8s for ERP; for decoding use tmax=1.8s since mean RT >1200ms. Response markers 0500=left, 0501=right for food choice task. Verify event ID mapping from events.tsv.

### Primary Task 2: Stimulus-locked ERP epoching (food choice)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`0400`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `0400` | 0 | Food stimulus onset (option A) |
  | `0500` | 1 | Food stimulus onset (option B) * |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01538-5 — Epochs extracted -200ms to 800ms locked to stimulus onset for ERP analysis.
- **Kernel Notes**: Stimulus markers 0400-0403 encode food stimuli (0400) and image/word semantic stimuli. Extract epochs around 0400 for stimulus-locked analysis. Verify mapping between 0400 and 0500 stimulus events from events.tsv.

### Normal Task 1: Binary choice classification (need to decode event meaning)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric trigger codes must be decoded from events.tsv. The 0200-series codes likely encode trial-phase timing; 0400/0500-series likely encode stimulus presentation. 217 files across 31 subjects (~7 sessions each). `boundary` is an EEGLAB admin marker; exclude from epoching.

| Event | y | Meaning |
|-------|---|------|
| `0400` | 0 | Stimulus/Option A (decode from events.tsv) |
| `0500` | 1 | Stimulus/Option B (decode from events.tsv) |

## Data Quality Notes

- 30+ distinct numeric event codes; decode mapping required from events.tsv or dataset paper.
- `boundary` events are EEGLAB data-continuity markers; must be excluded from epoching.
- High-density 129-channel EEG at 1000 Hz; high computational requirements.
- Multiple sessions per subject; verify session consistency before pooling.

