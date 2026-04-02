# Intracranial EEG During Cortical Stimulation Evoking Visual Effects

**Dataset**: `openneuro_ds005169` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005169
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 112 | **Channels**: 82 | **Sampling Rate**: 4096 Hz

## Paradigm

Intracranial EEG was recorded from drug-resistant epilepsy patients undergoing presurgical evaluation during direct electrical stimulation (DES) of cortical sites that evoke visual hallucinations and perceptual effects. `Comment/prestim` (112 total) marks pre-stimulation baseline periods and `Comment/poststim` (111) marks post-stimulation response windows. UUID-format Comment events (2-10 per file) are patient-specific or trial-specific annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005169

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/prestim` | 112 | long | raw | Pre-stimulation baseline period |
| `Comment/poststim` | 111 | long | raw | Post-stimulation response window |
| `Comment/[UUID]` | 2-10/file | admin | raw | Patient/trial-specific annotation (UUID format, exclude) |
| `Comment/[electrode] [mA] SYM` | ~2/file | admin | raw | Stimulation parameter annotation (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Comment/prestim`, `Comment/poststim`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Clinical Effect Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 0.0 s (baseline), tmin = 0.0 s, tmax = 2.0 s (response), overlap = 0.0, target_events = [`cognitive`, `motor`, `sensory`, `autonomic`, `visual`, `language`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `cognitive` | 0 | Cognitive effect evoked by stimulation |
  | `motor` | 1 | Motor effect evoked by stimulation |
  | `sensory` | 2 | Sensory effect evoked by stimulation |
  | `autonomic` | 3 | Autonomic effect evoked by stimulation |
  | `visual` | 4 | Visual effect evoked by stimulation |
  | `language` | 5 | Language effect evoked by stimulation |
- **Evidence**:
  - DOI: `10.1002/hbm.25749` — This paper analyzes intracranial EEG responses to high-frequency stimulation in 26 patients to map effective connectivity networks associated with clinical effects, classifying evoked responses into 6 categories (cognitive, motor, sensory, autonomic, visual, language).
- **Kernel Notes**: Baseline epochs: 2s ending 0.25s before stimulation onset. Response epochs: 2s starting 0.25s after stimulation onset. Labels derived from patient clinical effects reported during stimulation, categorized per ILAE classification.

### Primary Task 2: Visual Hallucination Subtype Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, target_events = [`visual_hallucination`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `elementary` | 0 | Elementary visual hallucination |
  | `plus` | 1 | Plus visual hallucination |
  | `minus` | 2 | Minus visual hallucination |
  | `static` | 3 | Static visual hallucination |
  | `dynamic` | 4 | Dynamic visual hallucination |
  | `continuous` | 5 | Continuous visual hallucination |
  | `intermittent` | 6 | Intermittent visual hallucination |
  | `whole_visual_field` | 7 | Whole visual field hallucination |
  | `center` | 8 | Center vision hallucination |
  | `peripheric` | 9 | Peripheral vision hallucination |
  | `color` | 10 | Color visual hallucination |
  | `non_color` | 11 | Non-color visual hallucination |
  | `combined` | 12 | Combined visual hallucination |
  | `multimodal` | 13 | Multimodal hallucination |
- **Super Meta Notes**: Labels are derived from patient verbal reports of visual symptoms during clinical interview post-stimulation, classified into 14 clinical categories by the researchers. Requires extracting UUID-comment events containing clinical effect descriptions, then mapping to these categories.
- **Evidence**:
  - DOI: `10.1016/j.brs.2025.05.138` — This study uses the openneuro_ds005169 dataset to analyze functional and effective brain connectivity during high-frequency intracranial stimulation, classifying 130 visual hallucinations elicited in 22 patients into 14 clinical categories including elementary, plus, minus, static, dynamic, continuous, intermittent, color, and non-color types.
- **Kernel Notes**: Stimulation: 5s train at 43.2Hz. HFA/PLV analysis uses 0.2s windows with 50% overlap over 2s. Requires parsing patient-specific UUID-comment events for visual effect descriptions. The dataset contains 130 visual hallucinations across 22 patients.

### Normal Task 1: Pre vs Post Stimulation (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: UUID-format and electrode/mA Comment events are admin - exclude. Very high sampling rate (4096 Hz) - downsample before processing. iEEG data; stimulation artifact present in poststim windows.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/prestim` | 0 | Pre-stimulation baseline |
 | `Comment/poststim` | 1 | Post-stimulation response |

## Data Quality Notes

- Very high sampling rate (4096 Hz) - downsample to <=1000 Hz before analysis.
- Intracranial EEG - different noise profile from scalp EEG; stimulation artifacts expected.
- UUID-format Comment events are patient-specific annotations - exclude from epoching.

## References

- **Reference**: `Imaging the effective networks associated with cortical function through intracranial high-frequency stimulation. DOI: 10.1002/hbm.25749`
