# Face Recognition (EEG, ds002718)

**Dataset**: `ds002718` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002718
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 54 | **Channels**: 70 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

Eighteen healthy adults viewed photographs of famous, unfamiliar, and scrambled faces presented for 800-1000ms while EEG was recorded with a 70-channel montage at 250 Hz. Subjects performed a symmetry judgment task, pressing left or right keys to indicate whether each face was 'more' or 'less symmetric' than average. The paradigm included repetition conditions: initial presentation, immediate repetition, and delayed repetition, enabling investigation of repetition suppression and face familiarity effects.

## File Scan Result

> **Kernel SHA256**: `94d41bf8ce64ceb228bcf2b2ac4d3c31cd2a29bd0b9b98da8e406504da789cbb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `boundary` | 180 | admin | raw | Run boundary marker: indicates boundary between merged runs |
| `famous_new` | 5400 | event | raw | Stimulus onset: famous face, first presentation |
| `famous_second_early` | 2626 | event | raw | Stimulus onset: famous face, immediate repeat presentation |
| `famous_second_late` | 2582 | event | raw | Stimulus onset: famous face, delayed repeat presentation |
| `left_nonsym` | 7064 | event | raw | Response: left hand button press, 'less symmetric' judgment |
| `left_sym` | 6762 | event | raw | Response: left hand button press, 'more symmetric' judgment |
| `right_nonsym` | 7232 | event | raw | Response: right hand button press, 'less symmetric' judgment |
| `right_sym` | 9800 | event | raw | Response: right hand button press, 'more symmetric' judgment |
| `scrambled_new` | 5400 | event | raw | Stimulus onset: scrambled face, first presentation |
| `scrambled_second_early` | 2542 | event | raw | Stimulus onset: scrambled face, immediate repeat presentation |
| `scrambled_second_late` | 2668 | event | raw | Stimulus onset: scrambled face, delayed repeat presentation |
| `unfamiliar_new` | 5400 | event | raw | Stimulus onset: unfamiliar face, first presentation |
| `unfamiliar_second_early` | 2608 | event | raw | Stimulus onset: unfamiliar face, immediate repeat presentation |
| `unfamiliar_second_late` | 2632 | event | raw | Stimulus onset: unfamiliar face, delayed repeat presentation |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `MISC` | native (raw misc in EEG file) | raw | 4 native MISC channels present in EEG file; no further details provided in available evidence |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (13/18) | Ages available for 13 of 18 participants; sample values: 31, 25, 30; some entries marked n/a |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | partial (13/18) | Sex/gender available for 13 of 18 participants; values coded as male/female (M/F in participants.tsv); some entries marked n/a |

## Tasks

### Potential Task 1: 3-class face type classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `famous_new` | 0 | famous face |
  | `famous_second_early` | 0 | famous face |
  | `famous_second_late` | 0 | famous face |
  | `unfamiliar_new` | 1 | unfamiliar face |
  | `unfamiliar_second_early` | 1 | unfamiliar face |
  | `unfamiliar_second_late` | 1 | unfamiliar face |
  | `scrambled_new` | 2 | scrambled face |
  | `scrambled_second_early` | 2 | scrambled face |
  | `scrambled_second_late` | 2 | scrambled face |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv — trial_type column contains all 9 face presentation event types (famous_new, famous_second_early, famous_second_late, unfamiliar_new, unfamiliar_second_early, unfamiliar_second_late, scrambled_new, scrambled_second_early, scrambled_second_late)
  - sub-002/eeg/sub-002_task-FaceRecognition_eeg.json — task described as face viewing with photographs of famous, unfamiliar, or scrambled faces presented for 800-1000ms; subjects make symmetry judgments via button presses
  - task-FaceRecognition_events.json — trial_type levels confirm meanings: "Initial presentation of famous face", "Immediate repeated presentation of famous face", "Delayed repeated presentation of famous face", etc.
- **Notes**: All 9 face presentation events are collapsed by face_type (famous/unfamiliar/scrambled), ignoring presentation order (new/second_early/second_late). This creates a balanced 3-class classification of face type based on ERP responses to face stimuli. The epoch window from -200ms to +1000ms captures the N170 component and subsequent face-selective ERP components.

### Potential Task 2: Famous vs Unfamiliar Face Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `famous_new` | 0 | Famous face, first presentation |
  | `famous_second_early` | 0 | Famous face, immediate repeat presentation |
  | `famous_second_late` | 0 | Famous face, delayed repeat presentation |
  | `unfamiliar_new` | 1 | Unfamiliar face, first presentation |
  | `unfamiliar_second_early` | 1 | Unfamiliar face, immediate repeat presentation |
  | `unfamiliar_second_late` | 1 | Unfamiliar face, delayed repeat presentation |
- **Evidence**:
  - sub-002_task-FaceRecognition_events.tsv / sub-003_task-FaceRecognition_events.tsv — trial_type column contains event markers for famous_new, famous_second_early, famous_second_late, unfamiliar_new, unfamiliar_second_early, unfamiliar_second_late confirming event structure and repetition conditions
  - task-FaceRecognition_events.json — Defines trial_type levels: "famous_new": "Initial presentation of famous face", "famous_second_early": "Immediate repeated presentation of famous face", "famous_second_late": "Delayed repeated presentation of famous face", "unfamiliar_new": "Initial presentation of unfamiliar face", "unfamiliar_second_early": "Immediate repeated presentation of unfamiliar face", "unfamiliar_second_late": "Delayed repeated presentation of unfamiliar face"
  - eeg.json — TaskDescription confirms face viewing paradigm with famous, unfamiliar, and scrambled faces presented for 800-1000ms with symmetry judgment responses
- **Notes**: Famous faces (all repetition conditions merged to y=0) vs unfamiliar faces (all repetition conditions merged to y=1). Scrambled faces are excluded as they are structurally different control stimuli, not meaningful for the famous/unfamiliar memory distinction. The three repetition conditions (new, second_early, second_late) are collapsed within each face category to test general face familiarity recognition regardless of presentation history. Epoch window (-200ms to 1000ms) covers the N170 component (~170ms) associated with face processing and subsequent late positive components related to memory/recognition effects.

### Potential Task 3: New vs Repeated Face Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_new`, `unfamiliar_new`, `scrambled_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `famous_new` | 0 | New presentation (first occurrence of any face) |
  | `unfamiliar_new` | 0 | New presentation (first occurrence of any face) |
  | `scrambled_new` | 0 | New presentation (first occurrence of any face) |
  | `famous_second_early` | 1 | Repeated presentation (immediate or delayed repeat) |
  | `famous_second_late` | 1 | Repeated presentation (immediate or delayed repeat) |
  | `unfamiliar_second_early` | 1 | Repeated presentation (immediate or delayed repeat) |
  | `unfamiliar_second_late` | 1 | Repeated presentation (immediate or delayed repeat) |
  | `scrambled_second_early` | 1 | Repeated presentation (immediate or delayed repeat) |
  | `scrambled_second_late` | 1 | Repeated presentation (immediate or delayed repeat) |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv — trial_type column contains all nine event types with face_type, event_order, trial_dist, and time_dist columns confirming new (event_order=1) vs repeat (event_order=2) structure
  - task-FaceRecognition_events.json — Levels definitions explicitly describe "Initial presentation" vs "Immediate repeated presentation" / "Delayed repeated presentation" for each face type
  - sub-002/eeg/sub-002_task-FaceRecognition_eeg.json — TaskDescription confirms face viewing paradigm with famous/unfamiliar/scrambled stimuli and symmetry judgment responses
- **Notes**: Collapses across face type (famous/unfamiliar/scrambled) and repeat timing (early/late) to test pure repetition suppression/priming effects. All new presentations (event_order=1) map to y=0; all repeat presentations (event_order=2) map to y=1. Epoch window (-200ms to 1000ms) targets N250r and subsequent repetition-related ERP components.

### Potential Task 4: Immediate vs Delayed Repeat Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`famous_second_early`, `famous_second_late`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_second_early`, `scrambled_second_late`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | famous_second_early | 0 | Immediate repeat presentation (famous face) |
  | unfamiliar_second_early | 0 | Immediate repeat presentation (unfamiliar face) |
  | scrambled_second_early | 0 | Immediate repeat presentation (scrambled face) |
  | famous_second_late | 1 | Delayed repeat presentation (famous face) |
  | unfamiliar_second_late | 1 | Delayed repeat presentation (unfamiliar face) |
  | scrambled_second_late | 1 | Delayed repeat presentation (scrambled face) |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv, sub-003/eeg/sub-003_task-FaceRecognition_events.tsv — trial_type column contains all six target events with confirmed counts; event_order and trial_dist/time_dist columns distinguish immediate vs delayed repetitions
  - task-FaceRecognition_events.json — defines `famous_second_early` as "Immediate repeated presentation of famous face" and `famous_second_late` as "Delayed repeated presentation of famous face", with equivalent definitions for unfamiliar and scrambled variants
  - eeg.json — describes face viewing paradigm with repetition structure; events extracted from merged runs with corrected latencies
- **Notes**: Collapses across all three face types (famous, unfamiliar, scrambled) to test pure repetition lag effect. All second_early events map to y=0 (immediate repeat) and all second_late events map to y=1 (delayed repeat), yielding a balanced binary classification of temporal dynamics in repetition priming. Epoch window from -200 ms to 1000 ms captures pre-stimulus baseline and early (N250r) through sustained repetition effects.

### Potential Task 5: Symmetry Judgment Button Press Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`left_sym`, `left_nonsym`, `right_sym`, `right_nonsym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | left_sym | 0 | Left hand button press, 'more symmetric' judgment |
  | left_nonsym | 1 | Left hand button press, 'less symmetric' judgment |
  | right_sym | 2 | Right hand button press, 'more symmetric' judgment |
  | right_nonsym | 3 | Right hand button press, 'less symmetric' judgment |
- **Evidence**:
  - task-FaceRecognition_events.json — trial_type levels define left_sym, left_nonsym, right_sym, right_nonsym as button press responses for symmetry judgments
  - sub-002_task-FaceRecognition_events.tsv — actual event occurrences with trial_type column containing these four response events
  - eeg.json — TaskDescription confirms subjects pressed left or right key based on symmetry judgment ('more' or 'less symmetric' than average)
  - README — dataset derived from Wakeman & Henson (2015) face processing study with button press responses
- **Notes**: Four-class classification of button press responses by hand (left/right) and judgment type (symmetric/nonsymmetric). Alternative 2-class collapses are possible: left hand (left_sym+left_nonsym → y=0) vs right hand (right_sym+right_nonsym → y=1) for motor lateralization, or symmetric (left_sym+right_sym → y=0) vs nonsymmetric (left_nonsym+right_nonsym → y=1) for decision content. Epoch window [-0.5, 0.5]s is response-locked and inferred from typical readiness potential and motor execution timing; shorter than stimulus-locked due to variable reaction times.

### Potential Task 6: 2-class hand laterality (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`left_sym`, `left_nonsym`, `right_sym`, `right_nonsym`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_sym` | 0 | Left hand button press (more symmetric judgment) |
  | `left_nonsym` | 0 | Left hand button press (less symmetric judgment) |
  | `right_sym` | 1 | Right hand button press (more symmetric judgment) |
  | `right_nonsym` | 1 | Right hand button press (less symmetric judgment) |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv — shows trial_type values `left_sym`, `left_nonsym`, `right_sym`, `right_nonsym` with corresponding value codes 256/4096 confirming left/right hand responses
  - task-FaceRecognition_events.json — defines `left_sym` as "Left button press to indicated more symmetric face", `left_nonsym` as "Left button press to indicated less symmetric face", `right_sym` as "Right button press to indicated more symmetric face", `right_nonsym` as "Right button press to indicated less symmetric face"
  - eeg.json — describes task requiring left or right index finger key-press based on symmetry judgment, with assignment counter-balanced across participants
- **Notes**: Response-locked epoch centered on button press. The two left-hand events are merged to y=0 and two right-hand events to y=1, collapsing across the symmetry judgment content to isolate motor lateralization. The -500ms to +500ms window captures readiness potential and motor execution. Epoch timing inferred from standard motor ERP literature as response-locked analysis.

### Potential Task 7: Symmetric vs Nonsymmetric Judgment Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`left_sym`, `right_sym`, `left_nonsym`, `right_nonsym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_sym` | 0 | symmetric judgment (collapsed across left/right hand) |
  | `right_sym` | 0 | symmetric judgment (collapsed across left/right hand) |
  | `left_nonsym` | 1 | nonsymmetric judgment (collapsed across left/right hand) |
  | `right_nonsym` | 1 | nonsymmetric judgment (collapsed across left/right hand) |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv — shows trial_type column with `left_sym`, `right_sym`, `left_nonsym`, `right_nonsym` response events
  - task-FaceRecognition_events.json — defines `right_sym` as "Right button press to indicated more symmetric face", `left_nonsym` as "Left button press to indicated less symmetric face", etc.
  - eeg.json TaskDescription — describes symmetry judgment task where participants pressed left or right key based on whether face was 'more' or 'less symmetric' than average
- **Notes**: Response-locked epochs centered on button press to capture decision-related activity. Collapses across response hand to test whether EEG carries information about perceptual decision content (symmetric vs nonsymmetric judgment) independent of motor execution. The epoch window (-0.5 to +0.5 s) is inferred as a reasonable response-locked window; symmetry judgment was made during stimulus viewing so pre-response activity may contain decision evidence.

### Potential Task 8: Face vs Button Press Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`famous_new`, `famous_second_early`, `famous_second_late`, `unfamiliar_new`, `unfamiliar_second_early`, `unfamiliar_second_late`, `scrambled_new`, `scrambled_second_early`, `scrambled_second_late`, `left_sym`, `left_nonsym`, `right_sym`, `right_nonsym`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `famous_new` | 0 | Face stimulus presentation (all face types) |
  | `famous_second_early` | 0 | Face stimulus presentation (all face types) |
  | `famous_second_late` | 0 | Face stimulus presentation (all face types) |
  | `unfamiliar_new` | 0 | Face stimulus presentation (all face types) |
  | `unfamiliar_second_early` | 0 | Face stimulus presentation (all face types) |
  | `unfamiliar_second_late` | 0 | Face stimulus presentation (all face types) |
  | `scrambled_new` | 0 | Face stimulus presentation (all face types) |
  | `scrambled_second_early` | 0 | Face stimulus presentation (all face types) |
  | `scrambled_second_late` | 0 | Face stimulus presentation (all face types) |
  | `left_sym` | 1 | Button press response (all button types) |
  | `left_nonsym` | 1 | Button press response (all button types) |
  | `right_sym` | 1 | Button press response (all button types) |
  | `right_nonsym` | 1 | Button press response (all button types) |
- **Evidence**:
  - sub-002/eeg/sub-002_task-FaceRecognition_events.tsv and sub-003/eeg/sub-003_task-FaceRecognition_events.tsv — trial_type column contains all 13 event types with event_type grouping faces vs button_press
  - sub-002/eeg/sub-002_task-FaceRecognition_eeg.json — task described as face viewing with symmetry judgments via left/right button presses
  - task-FaceRecognition_events.json — event_type column explicitly defines two general types: "faces" (face image presentation) and "button_press" (button pressing indicating level of symmetry)
- **Notes**: Binary classification collapsing 9 face presentation event types (y=0) vs 4 button press event types (y=1). Epoch parameters inferred from typical event-related discrimination windows; -200ms pre-stimulus baseline to 800ms post captures visual evoked responses and motor potentials without excessive length. The event_type column in events.tsv provides direct grounding for the two-class grouping.

### Potential Task 9: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (23–31); missing for 5/18 subjects; segments from subjects with missing age are excluded from training/evaluation. |
- **Evidence**:
  - participants.tsv — age column available for 13/18 subjects (range 23–31 years); used as regression target for subject-level biomarker prediction from segmented EEG
- **Notes**: Segmentation-based approach for subject-level prediction: EEG is split into 2-second non-overlapping segments, each inheriting the subject's age as the regression target. Model learns age-correlated spectral/spatial patterns across the continuous recording without relying on event structure. Missing ages (5 subjects) handled by exclusion at sample level.

### Potential Task 10: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | gender | 0 = M (male), 1 = F (female); 5 subjects with n/a excluded |
- **Evidence**:
- **Notes**: Subject-level biomarker task using 2-second non-overlapping segments of continuous EEG. Gender labels are drawn from participants.tsv (13/18 subjects with valid M/F labels: 7 M, 6 F). No event-based segmentation needed; the kernel must filter out subjects with missing gender (n/a) during train/test splitting. Standard approach for demographic classification from resting-state or task-continuous EEG.

### Potential Task 11: Continuous Face Viewing Segmentation Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `age` | Continuous subject age in years; value used directly as regression target. Partial coverage (13/18 subjects); subjects without age entry excluded. |
- **Evidence**:
- **Notes**: Segmentation-based task with no event locking. Uses 4-second sliding windows with 50% overlap to extract samples from continuous ~7.5-minute face viewing runs. Age is a native participants.tsv column, so Meta Level = raw. The kernel does not need to derive any channels; it only needs to read the `age` field from participants.tsv and assign the same label to all segments from a given subject.

## Data Quality Notes

- Age and sex/gender metadata are incomplete: only 13 of 18 subjects have valid entries, with 5 subjects marked as n/a.
- Amplifier, cap, and handedness metadata are completely missing from dataset documentation.
- 4 native MISC channels are present in the EEG files but their specific purpose is undocumented.
- Event counts show slight imbalance across conditions (e.g., right_sym: 9800 vs left_sym: 6762), likely due to natural variation in subject responses rather than design imbalance.
- 180 boundary markers indicate merged runs; researchers should verify that event latencies were correctly adjusted post-merging.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
