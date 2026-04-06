# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2015 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74 | **Sampling Rate**: 250 Hz
**Manual Review**: Mr.PJ

## Paradigm

Participants viewed famous faces, unfamiliar faces, and scrambled faces while making a left/right subjective symmetry judgment. Each image was presented twice, with the second presentation occurring either immediately (early lag) or after a delay (late lag). The EEGLAB repackaging merged the original runs, corrected event latencies, resampled the EEG to 250 Hz, and retained stimulus identity, response side/symmetry, presentation order, and repetition distance information in the event table. This is based on the SPM multimodal dataset (ds000117).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `famous_new` | 2700 | event | raw | Initial presentation of a famous face |
| `famous_second_early` | 1313 | event | raw | Immediate repeat of a famous face |
| `famous_second_late` | 1291 | event | raw | Delayed repeat of a famous face |
| `unfamiliar_new` | 2700 | event | raw | Initial presentation of an unfamiliar face |
| `unfamiliar_second_early` | 1304 | event | raw | Immediate repeat of an unfamiliar face |
| `unfamiliar_second_late` | 1316 | event | raw | Delayed repeat of an unfamiliar face |
| `scrambled_new` | 2700 | event | raw | Initial presentation of a scrambled face |
| `scrambled_second_early` | 1271 | event | raw | Immediate repeat of a scrambled face |
| `scrambled_second_late` | 1334 | event | raw | Delayed repeat of a scrambled face |
| `right_sym` | 4900 | event | raw | Right-button response: more symmetric than average |
| `right_nonsym` | 3616 | event | raw | Right-button response: less symmetric than average |
| `left_sym` | 3381 | event | raw | Left-button response: more symmetric than average |
| `left_nonsym` | 3532 | event | raw | Left-button response: less symmetric than average |
| `boundary` | 90 | admin | raw | Boundary marker introduced when original runs were merged; exclude |

> **Manual Review Note**: Event counts updated by human reviewer (Mr.PJ) from actual trial totals — replaced "18 (files)" placeholders with per-event counts. Kernel should verify counts against events.tsv on next scan.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Face Category Classification (famous vs unfamiliar vs scrambled)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `famous_new` | 0 | Famous face - first presentation |
  | `unfamiliar_new` | 1 | Unfamiliar face - first presentation |
  | `scrambled_new` | 2 | Scrambled face - first presentation |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — Three-class face category classification (famous/unfamiliar/scrambled) using ERP analysis (N170/N250 components) with epochs from -0.5s to +1.2s around stimulus onset
- **Kernel Notes**: Potential Task 1 from original analysis.md is subsumed by this Classical Task. Response time regression is available via misc label route but not part of this primary classification task. The paper reports mean RT ~955ms for regression targets.

### Classical Task 2: Repetition Effect Classification (first vs second presentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.2 s *, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `famous_new` | 0 | Famous face - first presentation |
  | `famous_second_early` | 1 | Famous face - second presentation (early lag) |
  | `famous_second_late` | 2 | Famous face - second presentation (late lag) |
  | `unfamiliar_new` | 3 | Unfamiliar face - first presentation |
  | `unfamiliar_second_early` | 4 | Unfamiliar face - second presentation (early lag) |
  | `unfamiliar_second_late` | 5 | Unfamiliar face - second presentation (late lag) |
  | `scrambled_new` | 6 | Scrambled face - first presentation |
  | `scrambled_second_early` | 7 | Scrambled face - second presentation (early lag) |
  | `scrambled_second_late` | 8 | Scrambled face - second presentation (late lag) |
- **Evidence**:
  - DOI: 10.1038/sdata.2015.1 — The original dataset analysis includes repetition effects (initial vs repeat presentations) with detailed timing for early vs late lag conditions
- **Kernel Notes**: This 9-class task captures both face category and presentation order/repetition timing. For simpler binary repetition analysis, collapse first presentations (y=0,3,6) vs second presentations (any second_* event). (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Symmetry Judgment Classification (response-based)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`right_sym`, `left_nonsym`, `left_sym`, `right_nonsym`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `right_sym` | 0 | Right-hand response: face judged symmetric |
  | `left_nonsym` | 1 | Left-hand response: face judged non-symmetric |
  | `left_sym` | 2 | Left-hand response: face judged symmetric |
  | `right_nonsym` | 3 | Right-hand response: face judged non-symmetric |
- **Notes**: Four-class response classification. Could be simplified to 2-class (symmetric vs non-symmetric) or 2-class (left-hand vs right-hand response). The `boundary` events should be excluded.

## Data Quality Notes

- The `response_time` column is present in the event tables but completely empty in this EEGLAB repackaging — RT regression is not a supported task for this dataset.
- `boundary` events appear because the original runs were merged during EEGLAB repackaging; do not epoch on these.
- EEG sidecars report `EEGChannelCount: 70`; channel files contain 74 channels total (70 EEG + 4 physiological: HEOG, VEOG, 2 ECG/EKG).
- One subject uses `ECG` rather than `EKG` as the channel type label — minor metadata inconsistency.
- Total event rows across subjects: 31,448.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review