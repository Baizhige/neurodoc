# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2015 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74 | **Sampling Rate**: 250 Hz
**Manual Review**: Pending

## Paradigm

Participants viewed famous faces, unfamiliar faces, and scrambled faces while making a left/right subjective symmetry judgment. Each image was presented twice, with the second presentation occurring either immediately (early lag) or after a delay (late lag). The EEGLAB repackaging merged the original runs, corrected event latencies, resampled the EEG to 250 Hz, and retained stimulus identity, response side/symmetry, presentation order, and repetition distance information in the event table. This is based on the SPM multimodal face dataset (ds000117).

## File Scan Result

> **Kernel SHA256**: `74905fa548971ba247a0f09787215d636f014d4d2810b5d55f0992cac5e11d53`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 90 | admin | raw | Boundary marker introduced when original runs were merged; exclude |
| `famous_new` | 2700 | event | raw | Initial presentation of a famous face |
| `famous_second_early` | 1313 | event | raw | Immediate repeat of a famous face |
| `famous_second_late` | 1291 | event | raw | Delayed repeat of a famous face |
| `left_nonsym` | 3532 | event | raw | Left-button response: less symmetric than average |
| `left_sym` | 3381 | event | raw | Left-button response: more symmetric than average |
| `right_nonsym` | 3616 | event | raw | Right-button response: less symmetric than average |
| `right_sym` | 4900 | event | raw | Right-button response: more symmetric than average |
| `scrambled_new` | 2700 | event | raw | Initial presentation of a scrambled face |
| `scrambled_second_early` | 1271 | event | raw | Immediate repeat of a scrambled face |
| `scrambled_second_late` | 1334 | event | raw | Delayed repeat of a scrambled face |
| `unfamiliar_new` | 2700 | event | raw | Initial presentation of an unfamiliar face |
| `unfamiliar_second_early` | 1304 | event | raw | Immediate repeat of an unfamiliar face |
| `unfamiliar_second_late` | 1316 | event | raw | Delayed repeat of an unfamiliar face |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Face Category Classification (famous vs unfamiliar vs scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `famous_new` | 0 | Famous face - first presentation |
  | `unfamiliar_new` | 1 | Unfamiliar face - first presentation |
  | `scrambled_new` | 2 | Scrambled face - first presentation |
- **Evidence**: DOI: 10.1038/sdata.2015.1 (paradigm description; no direct ML classification benchmark)
- **Kernel Notes**: Three-class face category classification. Uses first-presentation events only to avoid repetition confounds. The -0.2 to 1.0s window captures N170 and N250 ERP components. This is a Potential Task because existing references describe the paradigm but do not report classification performance benchmarks.

### Potential Task 2: Repetition Effect Classification (first vs second presentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.2 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `famous_new` | 0 | Famous face - first presentation |
  | `famous_second_early` | 1 | Famous face - second presentation (early lag) |
  | `famous_second_late` | 2 | Famous face - second presentation (late lag) |
  | `unfamiliar_new` | 3 | Unfamiliar face - first presentation |
  | `unfamiliar_second_early` | 4 | Unfamiliar face - second presentation (early lag) |
  | `unfamiliar_second_late` | 5 | Unfamiliar face - second presentation (late lag) |
  | `scrambled_new` | 6 | Scrambled face - first presentation |
  | `scrambled_second_early` | 7 | Scrambled face - second presentation (early lag) |
  | `scrambled_second_late` | 8 | Scrambled face - second presentation (late lag) |
- **Evidence**: DOI: 10.1038/sdata.2015.1 (paradigm description)
- **Kernel Notes**: Nine-class classification examining repetition effects across all stimulus types and lag conditions. The wider -0.5 to 1.2s window captures early visual components and repetition suppression effects. Could alternatively be simplified to binary (first vs second) or 3-way (new/early/late) by grouping events. This is a Potential Task.

### Potential Task 3: Response-side Classification (left vs right button press)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `left_nonsym` | 0 | Left-button response: less symmetric than average |
  | `left_sym` | 0 | Left-button response: more symmetric than average |
  | `right_nonsym` | 1 | Right-button response: less symmetric than average |
  | `right_sym` | 1 | Right-button response: more symmetric than average |
- **Evidence**: Plausible from paradigm alone; no reference required for Potential Task
- **Kernel Notes**: Binary classification of response side (left vs right). Combines sym/nonsym variants for each button side. Excludes response events overlapping with boundary markers. Could be extended to include symmetry judgment as additional factor by keeping separate labels per event type.

### Potential Task 4: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.0 s, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | All stimulus events | response_time (continuous) | Response time in milliseconds |
- **Evidence**: DOI: 10.1038/sdata.2015.1 reports mean RT ~955ms; response_time available via misc label route
- **Kernel Notes**: Regression task predicting response time from stimulus-locked epochs. Window ends at 0 (stimulus onset) to avoid contaminating with post-stimulus activity that correlates with response. Original paper reports mean RT ~955ms with substantial variance. Misc label derivation source and unit metadata must be retained.