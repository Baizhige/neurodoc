# Face processing EEG dataset for EEGLAB

**Dataset**: `openneuro_ds002718` | **Year**: 2015 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: High-level Mental | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 74 | **Sampling Rate**: 250 Hz | **Manual Review**: Jun Li

## Paradigm

Participants viewed famous faces, unfamiliar faces, and scrambled faces while making a left/right subjective symmetry judgment. Each image was presented twice, with the second presentation occurring either immediately (early lag) or after a delay (late lag). The EEGLAB repackaging merged the original runs, corrected event latencies, resampled the EEG to 250 Hz, and retained stimulus identity, response side/symmetry, presentation order, and repetition distance information in the event table. This is based on the SPM multimodal face dataset (ds000117).

## File Scan Result

> **Kernel SHA256**: `ba29c0f01eb87c59052deabc969c88bed8cdd501d18e42ee08c87973dfbbe9aa`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `boundary` | 90 | admin | raw | Run boundary marker indicating boundary between merged runs |
| `famous_new` | 2700 | event | raw | Initial presentation of famous face |
| `famous_second_early` | 1313 | event | raw | Immediate repeated presentation of famous face |
| `famous_second_late` | 1291 | event | raw | Delayed repeated presentation of famous face |
| `left_nonsym` | 3532 | event | raw | Left button press to indicate less symmetric face |
| `left_sym` | 3381 | event | raw | Left button press to indicate more symmetric face |
| `right_nonsym` | 3616 | event | raw | Right button press to indicate less symmetric face |
| `right_sym` | 4900 | event | raw | Right button press to indicate more symmetric face |
| `scrambled_new` | 2700 | event | raw | Initial presentation of scrambled face |
| `scrambled_second_early` | 1271 | event | raw | Immediate repeated presentation of scrambled face |
| `scrambled_second_late` | 1334 | event | raw | Delayed repeated presentation of scrambled face |
| `unfamiliar_new` | 2700 | event | raw | Initial presentation of unfamiliar face |
| `unfamiliar_second_early` | 1304 | event | raw | Immediate repeated presentation of unfamiliar face |
| `unfamiliar_second_late` | 1316 | event | raw | Delayed repeated presentation of unfamiliar face |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | partial (13/18) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 3-class face category classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `scrambled_new`, `unfamiliar_new`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Initial presentation of famous face |
  | `unfamiliar_new` | 1 | Initial presentation of unfamiliar face |
  | `scrambled_new` | 2 | Initial presentation of scrambled face |
- **Evidence**:
  - 10.1038/sdata.2015.1 — Original dataset publication describing face processing paradigm with famous, unfamiliar, and scrambled face conditions
  - 10.3389/fnins.2019.00300 — Reference describing standard ERP analysis and N170/M170 component analysis in face processing
- **Notes**: Three-category classification of initial face presentations only (excluding repeated presentations to avoid priming effects). Famous and unfamiliar faces are both intact faces, while scrambled faces serve as a low-level visual control. The N170/M170 ERP components at ~170ms are the primary neural markers distinguishing these conditions.

### Potential Task 1: 9-class face presentation type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Initial presentation of famous face |
  | `famous_second_early` | 1 | Immediate repeated presentation of famous face |
  | `famous_second_late` | 2 | Delayed repeated presentation of famous face |
  | `scrambled_new` | 3 | Initial presentation of scrambled face |
  | `scrambled_second_early` | 4 | Immediate repeated presentation of scrambled face |
  | `scrambled_second_late` | 5 | Delayed repeated presentation of scrambled face |
  | `unfamiliar_new` | 6 | Initial presentation of unfamiliar face |
  | `unfamiliar_second_early` | 7 | Immediate repeated presentation of unfamiliar face |
  | `unfamiliar_second_late` | 8 | Delayed repeated presentation of unfamiliar face |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines all 9 face presentation trial_type levels with meanings for new, second_early, and second_late presentations across famous, scrambled, and unfamiliar face categories
- **Notes**: 9-way classification distinguishing both face category (famous/scrambled/unfamiliar) and repetition status (new/immediate repeat/delayed repeat). ~2700 new presentations and ~1300 each for early/late repeats per category. Epoch window inferred from standard face ERP paradigms; repetition effects (e.g., N250r) may appear in later time windows but standard -200 to 1000 ms epoching captures the core face-evoked response.

### Potential Task 2: 3-class face repetition status classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | New face presentation (first occurrence) |
  | `unfamiliar_new` | 0 | New face presentation (first occurrence) |
  | `scrambled_new` | 0 | New face presentation (first occurrence) |
  | `famous_second_early` | 1 | Early/immediate repetition |
  | `unfamiliar_second_early` | 1 | Early/immediate repetition |
  | `scrambled_second_early` | 1 | Early/immediate repetition |
  | `famous_second_late` | 2 | Late/delayed repetition |
  | `unfamiliar_second_late` | 2 | Late/delayed repetition |
  | `scrambled_second_late` | 2 | Late/delayed repetition |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: new (famous_new/unfamiliar_new/scrambled_new), early repeat (famous_second_early/unfamiliar_second_early/scrambled_second_early), late repeat (famous_second_late/unfamiliar_second_late/scrambled_second_late) with explicit descriptions of initial, immediate repeated, and delayed repeated presentations
  - events.tsv samples — Confirm event values and face_type columns distinguish face categories; event_type='faces' for all stimulus presentations
- **Notes**: Collapses across all three face categories (famous, unfamiliar, scrambled) to isolate repetition status effects. This tests neural signatures of repetition suppression/priming independent of face familiarity. ~8100 new, ~3900 early, ~3940 late trials across 18 subjects. Epoch window (-0.2, 1.0)s captures baseline and sustained post-stimulus activity where repetition effects are expected.

### Potential Task 3: Famous vs Unfamiliar Face Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | Famous face (initial presentation) |
  | `famous_second_early` | 0 | Famous face (immediate repeat) |
  | `famous_second_late` | 0 | Famous face (delayed repeat) |
  | `unfamiliar_new` | 1 | Unfamiliar face (initial presentation) |
  | `unfamiliar_second_early` | 1 | Unfamiliar face (immediate repeat) |
  | `unfamiliar_second_late` | 1 | Unfamiliar face (delayed repeat) |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: famous_new, famous_second_early, famous_second_late as "famous face" presentations; unfamiliar_new, unfamiliar_second_early, unfamiliar_second_late as "unfamiliar face" presentations. All face presentation events have event_type='faces'.
  - events.tsv sample (sub-002) — Confirms event values: famous_new=5, unfamiliar_new=13, with face_type column distinguishing 'famous' vs 'unfamiliar'.
  - eeg.json — TaskDescription confirms famous vs unfamiliar vs scrambled face photographs presented for 800-1000 ms.
- **Notes**: Collapses repetition status (new/second_early/second_late) within each face type to create a binary famous vs unfamiliar classification. The ~5300 presentations per class provide balanced trials. The N250 and later ERP components are known to differentiate familiar from unfamiliar faces.

### Potential Task 4: 4-class symmetry judgment classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | Left button press, more symmetric |
  | `left_nonsym` | 1 | Left button press, less symmetric |
  | `right_sym` | 2 | Right button press, more symmetric |
  | `right_nonsym` | 3 | Right button press, less symmetric |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels with `left_sym`: "Left button press to indicated more symmetric face", `left_nonsym`: "Left button press to indicated less symmetric face", `right_sym`: "Right button press to indicated more symmetric face", `right_nonsym`: "Right button press to indicated less symmetric face"
  - eeg.json TaskDescription — Subjects pressed left or right key based on symmetry judgment (more/less symmetric than average), with key assignment counter-balanced across participants
  - events.tsv sample — Confirms button press events appear with trial_type values `left_sym`, `left_nonsym`, `right_sym`, `right_nonsym` and event_type='button_press'
- **Notes**: This is effectively a 4-class motor response classification task. The left/right mapping to 'more'/'less symmetric' was counterbalanced across subjects, so the semantic symmetry judgment is confounded with motor response. The task classifies the specific button press type (left/right × sym/nonsym). ~15,400 total button presses across 18 subjects. Epoch window includes pre-stimulus baseline (-0.5s) to capture readiness potential and 1.0s post-press for motor execution and post-movement rebound.

### Potential Task 5: 2-class symmetry response classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | more symmetric response |
  | `right_sym` | 0 | more symmetric response |
  | `left_nonsym` | 1 | less symmetric response |
  | `right_nonsym` | 1 | less symmetric response |
- **Evidence**:
  - task-FaceRecognition_events.json — trial_type Levels define left_sym/right_sym as "more symmetric face" and left_nonsym/right_nonsym as "less symmetric face"
  - eeg.json TaskDescription — participants pressed one of two keys based on symmetry judgment ('more' or 'less symmetric' than average), with left/right assignment counter-balanced across participants
  - README — events were renamed taking into account button assigned to each subject, confirming subject-specific counterbalancing
  - sub-002_task-FaceRecognition_events.tsv sample — shows left_nonsym (value=256) and right_sym (value=4096) co-occurring, confirming semantic labels are already remapped per subject in BIDS version
- **Notes**: This task collapses across left/right hand responses to create a binary symmetry judgment classification. The BIDS version of this dataset already has subject-specific remapping applied (per README: "Renaming events taking into account button assigned to each subject"), so left_sym/right_sym consistently mean "more symmetric" and left_nonsym/right_nonsym consistently mean "less symmetric" across all subjects. The epoch window includes a pre-stimulus baseline (-0.5s) to capture decision-related activity that may precede the motor response, with post-response window (1.0s) to capture motor execution and reafferent activity. ~8300 'more symmetric' vs ~7100 'less symmetric' responses total.

### Potential Task 6: 2-class motor response laterality
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`left_nonsym`, `left_sym`, `right_nonsym`, `right_sym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_sym` | 0 | Left hand motor response |
  | `left_nonsym` | 0 | Left hand motor response |
  | `right_sym` | 1 | Right hand motor response |
  | `right_nonsym` | 1 | Right hand motor response |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines `left_sym` and `left_nonsym` as left button presses, `right_sym` and `right_nonsym` as right button presses; all button presses use values 256 (left) and 4096 (right) with counterbalanced semantic labels across subjects.
  - events.tsv sample (sub-002) — Confirms `left_nonsym` and `right_sym` events present with value 256 and 4096 respectively, event_type='button_press'.
  - README — Describes task requiring left or right index finger key-press based on symmetry judgment, with assignment counter-balanced across participants.
- **Notes**: Motor lateralization task collapsing across the semantic judgment (symmetric vs non-symmetric). All left button presses (regardless of meaning) map to y=0, all right button presses map to y=1. This yields a pure motor response laterality classification (~6900 left vs ~8500 right responses).

### Potential Task 7: face vs scrambled classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `famous_new` | 0 | intact face (famous, first presentation) |
  | `famous_second_early` | 0 | intact face (famous, immediate repeat) |
  | `famous_second_late` | 0 | intact face (famous, delayed repeat) |
  | `unfamiliar_new` | 0 | intact face (unfamiliar, first presentation) |
  | `unfamiliar_second_early` | 0 | intact face (unfamiliar, immediate repeat) |
  | `unfamiliar_second_late` | 0 | intact face (unfamiliar, delayed repeat) |
  | `scrambled_new` | 1 | scrambled face (first presentation) |
  | `scrambled_second_early` | 1 | scrambled face (immediate repeat) |
  | `scrambled_second_late` | 1 | scrambled face (delayed repeat) |
- **Evidence**:
  - task-FaceRecognition_events.json — Defines trial_type levels: famous_new/unfamiliar_new as intact faces, scrambled_new as scrambled faces; all second_early/second_late variants are repetition conditions of same face types
  - eeg.json — TaskDescription confirms stimuli were "photographs of either a famous face or a scrambled face"
- **Notes**: All famous and unfamiliar face events (new and both repeat types) merged to y=0 (intact faces); all scrambled face events (new and both repeat types) merged to y=1 (scrambled faces). Tests configural/holistic face processing via N170 sensitivity to face vs scrambled distinction. ~10,600 intact face vs ~5,300 scrambled face presentations total across 18 subjects.

### Potential Task 8: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_age` | no mapping |
- **Evidence**:
  - participants.tsv — age column with values 23–31 years, partial completeness (13/18 subjects)
- **Notes**: Segmentation-based subject-level trait prediction. Non-overlapping 2-second windows from continuous EEG are used to predict subject age. No event alignment needed; the full continuous recording is segmented. Age is a native participants.tsv column (B3 archetype, raw meta level). Subjects with missing age data will be excluded by the kernel.

### Potential Task 9: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_sex` | F -> 0; M -> 1 |
- **Evidence**:

- **Notes**: Subject-level binary classification using 2-second non-overlapping windows of continuous EEG. Gender is a native participants.tsv column with partial coverage (13/18 subjects: 7 M, 6 F). The kernel does not need to derive any new channels; labels are read directly from the BIDS participants sidecar.

## Data Quality Notes

- `subject_sex` is only partially complete (13/18 subjects), with 5 subjects missing gender/sex information.
- `device` field is completely missing from dataset metadata, limiting hardware reproducibility.
- Event counts for `famous_second_early` (1313) and `famous_second_late` (1291) do not sum exactly to `famous_new` (2700), indicating minor data loss or exclusion during preprocessing (similar pattern for other categories).
- The `boundary` events (90 total, 5 per subject) indicate merged runs from the original acquisition; users should verify no edge artifacts at boundaries.
- Button press event counts are unbalanced (`right_sym` = 4900 vs `left_nonsym` = 3532), reflecting response bias or task design asymmetry rather than data quality issue.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
