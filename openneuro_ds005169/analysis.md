# Intracranial EEG During Cortical Stimulation Evoking Visual Effects

**Dataset**: `openneuro_ds005169` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005169
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 112 | **Channels**: 82 | **Sampling Rate**: 4096 Hz

## Paradigm

Intracranial EEG was recorded from drug-resistant epilepsy patients undergoing presurgical evaluation during direct electrical stimulation (DES) of cortical sites that evoke visual hallucinations and perceptual effects. `Comment/prestim` (112 total) marks pre-stimulation baseline periods and `Comment/poststim` (111) marks post-stimulation response windows. UUID-format Comment events (2-10 per file) are patient-specific or trial-specific annotations.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/prestim` | 112 | event | raw | Pre-stimulation baseline period |
| `Comment/poststim` | 111 | event | raw | Post-stimulation response window |
| `Comment/[UUID]` | 2-10/file | admin | raw | Patient/trial-specific annotation (UUID format, exclude) |
| `Comment/[electrode] [mA] SYM` | ~2/file | admin | raw | Stimulation parameter annotation (exclude) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Clinical Effect Classification (6-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 0.0 s, overlap = 0.0, target_events = [`Comment/prestim`] (baseline) | tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`Comment/poststim`] (response)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | cognitive | 0 | Cognitive effect evoked by stimulation |
  | motor | 1 | Motor effect evoked by stimulation |
  | sensory | 2 | Sensory effect evoked by stimulation |
  | autonomic | 3 | Autonomic effect evoked by stimulation |
  | visual | 4 | Visual effect evoked by stimulation |
  | language | 5 | Language effect evoked by stimulation |
- **Super Meta Notes**: Derived from raw events [`Comment/prestim`, `Comment/poststim`] by mapping patient verbal reports of clinical effects during clinical interview post-stimulation. Kernel step: Extract epoch windows around stimulation (baseline: 2s ending 0.25s before onset; response: 2s starting 0.25s after onset), then assign clinical effect labels based on patient-reported symptoms in clinical notes/annotations.
- **Evidence**:
  - DOI: `10.1002/hbm.25749` — Analyzes intracranial EEG responses to high-frequency stimulation in patients to map effective connectivity networks, classifying evoked responses into 6 categories (cognitive, motor, sensory, autonomic, visual, language).
  - DOI: `10.1016/j.brs.2025.05.138` — Uses openneuro_ds005169 dataset to analyze functional and effective brain connectivity during high-frequency intracranial stimulation, classifying visual hallucinations elicited in 22 patients.
- **Kernel Notes**: Use epoch_by_long_event_hdf5 for both baseline (prestim) and response (poststim) windows. Labels are derived from clinical effect categories reported by patients - not directly in raw events. Requires mapping clinical notes to 6-category ILAE classification.

### Classical Task 2: Visual Hallucination Subtype Classification (14-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 3.0 s, target_events = [`Comment/poststim`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
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
- **Super Meta Notes**: Derived from raw event [`Comment/poststim`] by classifying patient verbal reports of visual symptoms during clinical interview post-stimulation into 14 clinical categories. Kernel step: Extract response epochs after stimulation onset, then apply 14-category classification based on clinical notes.
- **Evidence**:
  - DOI: `10.1016/j.brs.2025.05.138` — Uses openneuro_ds005169 dataset to analyze functional and effective brain connectivity during high-frequency intracranial stimulation, classifying 130 visual hallucinations elicited in 22 patients into 14 clinical categories including elementary, plus, minus, static, dynamic, continuous, intermittent, color, and non-color types.
- **Kernel Notes**: Stimulus train is 5s at 43.2Hz per paper. Labels derived from clinical reports, not raw event markers. Requires clinical note extraction and mapping to 14-category schema.

### Potential Task 1: Pre vs Post Stimulation (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very high sampling rate (4096 Hz) - downsample before processing. iEEG data; stimulation artifact present in poststim windows.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/prestim` | 0 | Pre-stimulation baseline |
 | `Comment/poststim` | 1 | Post-stimulation response |

## Data Quality Notes

- Very high sampling rate (4096 Hz) - downsample to <=1000 Hz before analysis.
- Intracranial EEG - different noise profile from scalp EEG; stimulation artifacts expected.
- UUID-format Comment events are patient-specific annotations - exclude from epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review