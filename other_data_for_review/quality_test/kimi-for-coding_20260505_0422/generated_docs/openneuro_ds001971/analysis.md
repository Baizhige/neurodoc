# Audio-Cue Walking Study (MoBI gait adaptation)

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Action/Output | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 30 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Twenty healthy young adults (9 female, 11 male; age range 18-38 years, all right-handed) walked on a treadmill while EEG was recorded using a 30-channel EasyCap M15 system with g.USBamp amplifier at 500 Hz. Participants performed uncued walking and cued walking conditions where they synchronized their steps to an auditory metronome; the metronome occasionally shifted to faster (step advance) or slower (step delay) tempos, requiring gait adaptation. Three auxiliary channels (ANKLE, HIP, KNEE) recorded lower limb kinematics. The experiment was conducted as a Mobile Brain/Body Imaging (MoBI) study to investigate neural dynamics during continuous locomotion and tempo adaptation.

## File Scan Result

> **Kernel SHA256**: `91586ebcf2a3d4c9e3c6351416847edc5b00dc2d68765dcea0d3e7fd05e5372b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `100` | 32100 | event | raw | Right heel strike during uncued walking |
| `101` | 26354 | event | raw | Right cued heel strikes during preferred cadence |
| `103` | 20237 | event | raw | Right cued heel strikes during step advance |
| `109` | 20692 | event | raw | Right cued heel strikes during step delay |
| `113` | 1154 | event | raw | Right auditory cue during preferred cadence |
| `114` | 2368 | event | raw | Right auditory cue during step advance |
| `119` | 1154 | event | raw | Right auditory cue during step delay |
| `151` | 26402 | event | raw | Right auditory cue during preferred cadence |
| `153` | 20441 | event | raw | Right auditory cue during step advance |
| `159` | 20635 | event | raw | Right auditory cue during step delay |
| `171` | 5715 | event | raw | Right cue during standing (STATUS trial phase) |
| `200` | 34011 | event | raw | Left heel strike during uncued walking |
| `201` | 28708 | event | raw | Left cued heel strikes during preferred cadence |
| `203` | 20365 | event | raw | Left cued heel strikes during step advance |
| `209` | 21070 | event | raw | Left cued heel strikes during step delay |
| `251` | 28730 | event | raw | Left auditory cue during preferred cadence |
| `253` | 20482 | event | raw | Left auditory cue during step advance |
| `259` | 20683 | event | raw | Left auditory cue during step delay |
| `271` | 5678 | event | raw | Left cue during standing (STATUS trial phase) |
| `333` | 1154 | event | raw | Left auditory cue during preferred cadence |
| `444` | 2368 | event | raw | Left auditory cue during step advance |
| `999` | 1153 | event | raw | Left auditory cue during step delay |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ANKLE` | native (raw misc in EEG file) | raw | Lower limb joint channel, likely records ankle movement kinematics during treadmill walking task |
| `HIP` | native (raw misc in EEG file) | raw | Lower limb joint channel, likely records hip movement kinematics during treadmill walking task |
| `KNEE` | native (raw misc in EEG file) | raw | Lower limb joint channel, likely records knee movement kinematics during treadmill walking task |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Age ranges reported as '18-38' for some participants; exact ages not consistently provided in participants file |
| `amplifier` | missing | Amplifier: g.USBamp by gtec (ManufacturersModelName in eeg_json) |
| `cap` | missing | Cap: EasyCap M15 (CapManufacturer and CapManufacturersModelName in eeg_json), 10 percent system placement |
| `handedness` | missing | All sampled participants are right-handed (R) |
| `sex` | missing | Mixed sex: both female (F) and male (M) participants present in dataset |

## Tasks

### Classical Task 1: 3-class walking condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 1.0 s *, target_events = ['113', '114', '119']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `114` | 0 | preferred cadence |
  | `113` | 1 | step advance |
  | `119` | 2 | step delay |
- **Evidence**:
  - 10.1038/s41597-019-0223-2 — Three distinct walking conditions with first-heel-strike markers: 114/444 for preferred cadence, 113/333 for step advance, 119/999 for step delay; right-side first markers (114, 113, 119) used as condition onsets for 3-class classification
- **Notes**: The task uses right-side first markers (114, 113, 119) to define the three gait adaptation conditions. Left-side equivalents (444, 333, 999) are also valid per the dataset documentation but not included in the target_events list to avoid duplicate condition onsets; the kernel must extract epochs anchored at these event IDs. The epoch window (-0.5 to 1.0 s) captures preparatory activity and early gait adaptation dynamics following tempo shifts, with values inferred from the paradigm description.

### Classical Task 2: 2-class tempo shift direction classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`113`, `119`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 113 | 0 | step advance (faster tempo shift) — first right heel strike relative to step advance tempo shift |
  | 119 | 1 | step delay (slower tempo shift) — first right heel strike relative to step delay tempo shift |
- **Evidence**:
  - 10.1038/s41597-019-0223-2 — Core experimental manipulation involves tempo shifts to faster (step advance) or slower (step delay) pacing; first markers for these shifts are 113/333 (right/left for step advance) and 119/999 (right/left for step delay); using right-side markers 113 and 119 for the fundamental faster-vs-slower contrast.
- **Notes**: Right-side event codes (113, 119) selected for symmetry and balanced trial counts (1154 each). Left-side equivalents (333, 999) exist but are omitted to avoid duplicate conditions. The task captures ERP time-locked to tempo shift onset during cued walking, with an anticipatory baseline (-1 s) and post-shift adaptation window (2 s).

### Potential Task 1: 2-class standing cue laterality
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.5 s *, target_events = [`171`, `271`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 171 | 0 | Right cue during standing (STATUS trial phase) |
  | 271 | 1 | Left cue during standing (STATUS trial phase) |
- **Evidence**:
  - events.json — "171": "Cue during standing previously associated with right heel strike"; "271": "Cue during standing previously associated with left heel strike"
  - sub-001_task-AudioCueWalkingStudy_run-01_events.tsv — 171 and 271 appear in 'STATUS' trial_type, confirming standing-phase lateralized auditory cues
- **Notes**: Auditory ERP epoch window (-200 to +500 ms) inferred from standard auditory ERP analysis conventions; no explicit timing documentation in dataset. Task discriminates right vs left lateralized cues presented during standing still, forming a simple 2-class laterality classification.

### Potential Task 2: 4-class cued heel strike laterality by condition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`101`, `201`, `103`, `109`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 101 | 0 | Right cued heel strike during preferred cadence |
  | 201 | 1 | Left cued heel strike during preferred cadence |
  | 103 | 2 | Right cued heel strike during step advance |
  | 109 | 3 | Right cued heel strike during step delay |
- **Evidence**:
  - `task-AudioCueWalkingStudy_events.json` — Defines event codes 101/201 as right/left cued heel strikes during preferred cadence walking, 103/203 as right/left during step advance pacing tempo, and 109/209 as right/left during step delay pacing tempo
  - `events.tsv` samples — Confirm 100/200 (uncued) and 101/201/103/113/114/151/251/333 (cued conditions) appear in actual recordings; right/left pairing pattern confirmed across all documented codes
  - `eeg.json` — TaskDescription confirms participants stepped to auditory tones with tempo shifts (advance/delay conditions), matching the three pacing conditions in the event codes
- **Notes**: This 4-class task selects a balanced subset of cued heel strike conditions: preferred cadence (both right and left) plus right-side only for step advance and step delay. The left-side equivalents (203, 209) are excluded to avoid class imbalance since right-side events are more consistently documented. The epoch window (-0.2 to 0.8 s) is inferred from biomechanical ERP literature for heel strike responses during treadmill walking.

### Potential Task 3: 2-class sex classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `sex` | 0=F (female), 1=M (male) |
- **Evidence**:
- **Notes**: Subject-level trait classification using non-overlapping 10-second windows. The entire continuous recording is segmented and all windows from a given subject share the same label from participants.tsv `sex` column (9F, 11M). No kernel derivation needed — label is read directly from native BIDS info field.

### Potential Task 4: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | `age` | Continuous age in years. Exact values used where available (28, 32). For range entries '18-38', midpoint 28 is used as approximate age, yielding limited variance across subjects. Most subjects have age≈28; exact ages 28 and 32 provide minor spread. Small-sample regression expected. |
- **Evidence**:
  - participants.tsv — age column contains exact values (28, 32) and range '18-38' for 18 of 20 subjects; midpoint approximation yields groundable continuous target
- **Notes**: Subject-level trait regression using segmentation epochs. The age variable is native to participants.tsv (info route, Meta Level=raw). Range midpoints introduce approximation; kernel simply reads the pre-existing info field. Limited variance in age (most subjects ~28 years) makes this a challenging small-sample regression task.

### Potential Task 5: Segmented Gait Adaptation Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | sex | 0 = F (female), 1 = M (male); binary classification from participants.tsv |
- **Evidence**:
  - participants.tsv — N=20 subjects with sex field complete: F=9, M=11
  - dataset_description.json — "Audiocue walking study" with continuous treadmill walking and tempo adaptation
  - README — describes MoBI gait adaptation experiment with auditory tone sequence and tempo shifts
- **Notes**: Segmentation-based approach (archetype C) using 30-second windows with 50% overlap to capture gait cycle dynamics and tempo adaptation periods without event-locking. The sex label is drawn from the native participants.tsv info field, requiring no kernel derivation. Longer segments are chosen to encompass multiple gait cycles and potential tempo shift adaptations, allowing the model to learn whether gait-related neural dynamics carry subject trait information in a continuous walking paradigm.

### Potential Task 6: 2-class cued vs uncued walking
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`100`, `101`, `200`, `201`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 100 | 0 | Right heel strike during uncued walking |
  | 200 | 0 | Left heel strike during uncued walking |
  | 101 | 1 | Right cued heel strikes during preferred cadence |
  | 201 | 1 | Left cued heel strikes during preferred cadence |
- **Evidence**:
  - events.tsv samples (sub-001 run-01) — Shows `100`/`200` appear in `UncuedWalking` trial_type as alternating right/left heel strikes
  - task-AudioCueWalkingStudy_events.json — Defines `100` as "Right heel strikes during uncued walking", `200` as "Left heel strikes during uncued walking", `101` as "Right cued heel strikes during preferred cadence walking", `201` as "Left cued heel strikes during preferred cadence walking"
  - EEG File Header Sample — Confirms `100`, `101`, `200`, `201` all present as annotations in actual recordings
- **Notes**: Merges right/left heel strikes per condition to create a 2-class cue presence discrimination (uncued=0, cued=1), balancing limb laterality within each class. Preferred cadence (101/201) selected as the most basic cued condition among multiple cued variants (advance/delay not used). Epoch window centered on heel strike captures contact-related ERPs with pre-strike baseline.

### Potential Task 7: 3-class auditory cue condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`151`, `153`, `159`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 151 | 0 | Right auditory cue during preferred cadence walking |
  | 153 | 1 | Right auditory cue during step advance pacing tempo |
  | 159 | 2 | Right auditory cue during step delay pacing tempo |
- **Evidence**:
  - task-AudioCueWalkingStudy_events.json — Defines 151 as "Auditory cues for right step during preferred cadence walking", 153 as "Auditory cues for right heel strikes during step advance pacing tempo", 159 as "Auditory cues for right heel strikes during step delay pacing tempo"
  - events.tsv samples — Confirmed presence of event codes 151 (26402 occurrences), 153 (20441 occurrences), 159 (20635 occurrences) across dataset
  - EEG File Header Sample — Annotations include 151, demonstrating these events are present in actual recording files
  - README — Describes paradigm: participants step in time to auditory tone sequence with occasional shifts to faster (advance) or slower (delay) tempo
- **Notes**: Using right-side ongoing auditory cues (151/153/159) rather than first-markers (113/333, 114/444, 119/999) because the ongoing cues provide substantially more samples for model training. The three conditions correspond to preferred cadence (baseline), step advance (faster tempo), and step delay (slower tempo). Epoch window [-0.1, 0.5] s captures pre-stimulus baseline and early auditory ERP components (P1, N1, P2) plus attentional modulation relevant to gait adaptation processing.

## Data Quality Notes

- Motion artifacts expected due to treadmill walking paradigm; MoBI recordings inherently contain muscle, eye movement, and gait-related artifacts.
- Age information incomplete: 18 of 20 subjects have age reported as range '18-38' rather than exact values, limiting precision for age regression task.
- Small sample size (N=20) limits statistical power for subject-level classification and regression tasks.
- Event code 113 has count 1154 while code 114 has count 2368, creating imbalance for Classical Task 1 (3-class walking condition classification); preferred cadence class has twice as many trials.
- Three MISC channels (ANKLE, HIP, KNEE) contain kinematic data rather than neural signals; these should be excluded from EEG analysis or used as auxiliary predictors.
- Event counts for standing cue laterality task (171: 5715, 271: 5678) are well-balanced but substantially higher than first-marker events for tempo shifts.
- No explicit documentation found for epoch window timing parameters; all tmin/tmax values in tasks are inferred from paradigm description or standard ERP conventions.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
