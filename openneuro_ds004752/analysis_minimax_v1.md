# Dataset of Intracranial EEG, Scalp EEG and Beamforming Sources from Epilepsy Patients - Verbal Working Memory

**Dataset**: `openneuro_ds004752` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004752
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 136
**Channels**: 64 | **Sampling Rate**: 2000 Hz

## Paradigm

Epilepsy patients performed a modified Sternberg verbal working memory task consisting of encoding, maintenance, and recall phases while simultaneous scalp and intracranial EEG were recorded. The dataset includes iEEG from depth electrodes, scalp EEG, single-unit neuron spike times, and electrode localizations, enabling multi-level analysis of memory processes. No trial-level event annotations are available in the BIDS events.tsv.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004752

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Verbal WM Phase Classification (Encoding vs Maintenance)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 0.0 s, target_events = [`encoding`, `maintenance`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `encoding` | 0 | Information flows from auditory cortex to hippocampus |
  | `maintenance` | 1 | Information flows from hippocampus to auditory cortex |
- **Super Meta Notes**: Labels derived from experimental design timing structure (fixed encoding/maintenance periods) combined with behavioral responses. Epochs aligned to stimulus onset, capturing encoding phase [-5,-3]s and maintenance phase [-3,0]s.
- **Evidence**:
  - DOI: 10.7554/eLife.78677 — Analyzes directed functional connectivity using spectral Granger causality between hippocampal LFP and EEG sources, examining information flow direction from auditory cortex to hippocampus during encoding versus hippocampus to auditory cortex during maintenance.
  - DOI: 10.1038/s41597.020.0364.3 — Describes dataset with encoding (2s), maintenance (3s), and retrieval phases; trial epochs from stimulus onset to response.
- **Kernel Notes**: Must derive phase labels from experimental design timing. The dataset contains behavioral logs with trial timing; map stimulus onset to extract encoding and maintenance windows. Focus analysis on last 2s of maintenance [-2,0]s as noted in papers.

### Primary Task 2: Verbal WM Set Size Classification (Workload)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 0.0 s, target_events = [`set_size_4`, `set_size_6`, `set_size_8`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `set_size_4` | 0 | Low memory workload (4 items) |
  | `set_size_6` | 1 | Medium memory workload (6 items) |
  | `set_size_8` | 2 | High memory workload (8 items) |
- **Super Meta Notes**: Labels derived from task parameters (set size as memory workload) recorded in per-trial data structure. Set size is a trial-level parameter provided in the dataset's behavioral records but not encoded as BIDS event markers.
- **Evidence**:
  - DOI: 10.1038/s41597.020.0364.3 — Trial-level metadata includes set size (4/6/8), match/mismatch, correct/incorrect, and response time.
- **Kernel Notes**: Must extract set size information from behavioral log files accompanying the dataset. Epoch window should capture encoding and maintenance phases where workload effects are observable.

### Primary Task 3: Verbal WM Match/Mismatch Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 2.0 s, target_events = [`match_IN`, `mismatch_OUT`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `match_IN` | 1 | Probe item was in the set (match) |
  | `mismatch_OUT` | 0 | Probe item was not in the set (mismatch) |
- **Super Meta Notes**: Labels derived from behavioral responses (match/mismatch decisions). Epoch extends through probe presentation and response.
- **Evidence**:
  - DOI: 10.1038/s41597.020.0364.3 — Trial-level metadata includes match/mismatch probe type.
- **Kernel Notes**: Match/mismatch labels available in behavioral records. Epoch should extend to include probe presentation and response period (up to 2s after probe onset).

### Primary Task 4: Verbal WM Accuracy Classification (Correct/Incorrect)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -5.0 s, tmax = 2.0 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `correct` | 1 | Participant correctly identified match/mismatch |
  | `incorrect` | 0 | Participant incorrectly identified match/mismatch |
- **Super Meta Notes**: Labels derived from behavioral responses (correct/incorrect). Includes response times for validation.
- **Evidence**:
  - DOI: 10.7554/eLife.78677 — Compares encoding vs maintenance periods in correct vs incorrect trials for classification analyses.
  - DOI: 10.1038/s41597.020.0364.3 — Trial-level metadata includes correct/incorrect responses.
- **Kernel Notes**: Must extract accuracy labels from behavioral logs. Epoch should include full trial from encoding through response.

### Normal Task 1: Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (no event tag)
- **Notes**: No trial-level events available in events.tsv. EEG is continuous during task performance. Use sliding-window segmentation. Trial timing may be available in accompanying behavioral logs not captured in BIDS events.tsv.

## Data Quality Notes

- No event markers - trial-epoch structure not available from events.tsv.
- Very high sampling rate (2000 Hz) - downsample before analysis.
- Epilepsy patients; ictal episodes should be identified and excluded.

## References

- **Reference**: `Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. DOI: 10.1038/s41597-020-0364-3`
