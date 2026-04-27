# Intracranial EEG During Cortical Stimulation Evoking Visual Effects

**Dataset**: `openneuro_ds005169` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005169
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 112 | **Channels**: 82 | **Sampling Rate**: 4096 Hz
**Manual Review**: Pending

## Paradigm

Intracranial EEG was recorded from drug-resistant epilepsy patients undergoing presurgical evaluation during direct electrical stimulation (DES) of cortical sites that evoke visual hallucinations and perceptual effects. The dataset includes 112 stimulation sessions across 22 patients, with `stimulation: baseline` (112 total) marking pre-stimulation baseline periods and `stimulation: response` (111) marking post-stimulation response windows. Patient-specific clinical annotations in UUID format and stimulation parameter metadata are recorded as admin events to support effect classification.

## File Scan Result

> **Kernel SHA256**: `e9eaaa6de3c32f35b7684f29f3b93c838e3a5cc24cd30598a81c1019c73ba803`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/*poststim` | 1 | event | raw | Post-stimulation marker annotation |
| `Comment/B'03-B'04 0.75mA; Simple visual hallucinations` | 1 | event | raw | Visual hallucination description for electrode pair B'03-B'04 at 0.75mA |
| `Comment/R08-R09 2mA; puncte colorate in hemicamp vizual stg` | 1 | event | raw | Visual effect description (colored points in left visual hemifield) |
| `Comment/Z06-Z07 0.5mA; vibratii vizuale in hemicamp vizual stg (forme geometrice colorate)` | 1 | event | raw | Visual vibration description with colored geometric shapes in left visual hemifield |
| `Comment/Z08-Z09 0.5mA; visual` | 1 | event | raw | Visual effect at electrode pair Z08-Z09 |
| `Comment/Z09-Z10 0.5mA; visual` | 1 | event | raw | Visual effect at electrode pair Z09-Z10 |
| `Comment/Z10-Z11 0.75mA; visual` | 1 | event | raw | Visual effect at electrode pair Z10-Z11 |
| `Comment/Z11-Z12 1.5mA; visual` | 1 | event | raw | Visual effect at electrode pair Z11-Z12 |
| `admin: stim_param` | 105 | admin | raw | Stimulation parameter annotation (electrode pairs, current amplitude) |
| `admin: uuid_annotation` | 105 | admin | raw | Patient/trial-specific UUID annotation (exclude from epoching) |
| `stimulation: baseline` | 112 | event | raw | Pre-stimulation baseline period |
| `stimulation: response` | 111 | event | raw | Post-stimulation response window |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Clinical Effect Classification (6-class)
- **Task Type**: classification
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = -2.0 s, tmax = 0.0 s, overlap = 0.0, target_events = ["stimulation: baseline"] | tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = ["stimulation: response"]
- **Label Route**: event
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | cognitive | 0 | Cognitive effect evoked by stimulation |
  | motor | 1 | Motor effect evoked by stimulation |
  | sensory | 2 | Sensory effect evoked by stimulation |
  | autonomic | 3 | Autonomic effect evoked by stimulation |
  | visual | 4 | Visual effect evoked by stimulation |
  | language | 5 | Language effect evoked by stimulation |
- **Super Meta Notes**: Derived from raw events ["stimulation: baseline", "stimulation: response"] by mapping patient verbal reports of clinical effects during clinical interview post-stimulation. Kernel step: Extract epoch windows around stimulation onset (baseline: 2s ending 0.25s before onset; response: 2s starting 0.25s after onset), then assign clinical effect labels based on patient-reported symptoms in clinical notes/annotations.
- **Evidence**:
  - DOI: 10.1002/hbm.25749 — Analyzes intracranial EEG responses to high-frequency stimulation in patients to map effective connectivity networks, classifying evoked responses into 6 categories (cognitive, motor, sensory, autonomic, visual, language).
  - DOI: 10.1016/j.brs.2025.05.138 — Uses openneuro_ds005169 dataset to analyze functional and effective brain connectivity during high-frequency intracranial stimulation, classifying visual hallucinations elicited in 22 patients.
- **Kernel Notes**: Use epoch_by_long_event_hdf5 for both baseline (stimulation: baseline) and response (stimulation: response) windows. Labels are derived from clinical effect categories reported by patients - not directly in raw events. Requires mapping clinical notes to 6-category ILAE classification. Available admin events (admin: stim_param, admin: uuid_annotation) should be excluded from epoching.

### Classical Task 2: Visual Hallucination Subtype Classification (14-class)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -2.0 s, tmax = 3.0 s, overlap = null, target_events = ["stimulation: response"]
- **Label Route**: event
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | elementary | 0 | Elementary visual hallucination |
  | plus | 1 | Plus visual hallucination |
  | minus | 2 | Minus visual hallucination |
  | static | 3 | Static visual hallucination |
  | dynamic | 4 | Dynamic visual hallucination |
  | continuous | 5 | Continuous visual hallucination |
  | intermittent | 6 | Intermittent visual hallucination |
  | whole_visual_field | 7 | Whole visual field |
  | center | 8 | Center vision |
  | peripheric | 9 | Peripheral vision |
  | color | 10 | Color hallucination |
  | non_color | 11 | Non-color hallucination |
  | combined | 12 | Combined effects |
  | multimodal | 13 | Multimodal effects |
- **Super Meta Notes**: Derived from raw event ["stimulation: response"] by classifying patient verbal reports of visual symptoms during clinical interview post-stimulation into 14 clinical categories. Kernel step: Extract response epochs after stimulation onset with 2s baseline and 3s response to capture full visual hallucination dynamics, then apply 14-category classification based on clinical notes.
- **Evidence**:
  - DOI: 10.1016/j.brs.2025.05.138 — Uses openneuro_ds005169 dataset to analyze functional and effective brain connectivity during high-frequency intracranial stimulation, classifying visual hallucinations into 14 subtypes (elementary, plus, minus, static, dynamic, continuous, intermittent, whole_visual_field, center, peripheric, color, non_color, combined, multimodal) in 22 patients.
- **Kernel Notes**: Use epoch_by_event_hdf5 with symmetric window around stimulation: response onset. 14-class labels derived from patient-reported symptoms in clinical notes - not directly present in raw events. Requires post-hoc mapping of clinical documentation to visual hallucination taxonomy. UUID-format Comment events contain patient-specific visual descriptions that inform label mapping.