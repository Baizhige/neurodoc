# SKILL: Complex Applied — Mixed Paradigms, Clinical, BCI Applications

## Category Coverage
Datasets combining multiple paradigm types, clinical applications, or BCI system evaluations. Includes: hybrid BCI, clinical patient populations, disorder classification (ASD, ADHD, MCI, depression), combined MI+SSVEP, multi-task recordings.

## Epoch Method Selection
- Determine the primary paradigm type for each task independently.
- Mixed datasets may require different epoch methods for different tasks.
- Refer to action_output.md, sensory_response.md, biological_state.md, high_level_mental.md for per-paradigm rules.
- When in doubt: prefer `epoch_by_event_hdf5` for discrete events, `epoch_by_long_event_hdf5` for sustained states.

## Multi-Task Strategy
- Generate ONE task per distinct paradigm or classification target.
- Do NOT merge unrelated paradigms into a single task.
- If dataset has both MI and ERP paradigms: create separate tasks for each.

## Clinical / Disorder Classification
- Labels typically derived from subject metadata (diagnosis) — **always super meta**.
- Label Route = `info`, Meta Level = super.
- Super Meta Notes must explain: "Derived from subject metadata field [diagnosis] — kernel must load per-subject label from companion file."
- Epoch method: usually `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5` (resting-state comparison).

### Typical Clinical Parameters
| Application | Method | Parameters |
|---|---|---|
| Disorder classification (resting) | epoch_by_segmentation_hdf5 | segment_length = 4–10 s, overlap = 0.0–0.5 |
| Disorder classification (task ERP) | epoch_by_event_hdf5 | tmin = -0.2 s, tmax = 1.0 s |
| BCI evaluation (P300 speller) | epoch_by_event_hdf5 | tmin = -0.1 s, tmax = 0.8 s |
| Hybrid BCI (MI + SSVEP) | epoch_by_event_hdf5 | per-paradigm windows; separate tasks |

## Evidence Quality Notes
- Clinical papers: confirm patient vs healthy control split; confirm diagnostic criteria.
- Multi-site studies: note if different sites used different protocols — may need site-specific filtering.
- Papers evaluating a BCI system: confirm whether classification is real-time or offline.
- If paper only reports system-level accuracy (not per-class): use as Potential Task evidence with [indirect] note.

## Common Pitfalls
- Subject-level labels (disorder) vs trial-level labels (stimulus response): do not conflate.
- Medication effects in clinical populations: may confound EEG — note if paper controls for this.
- Multi-session recordings: session effects (non-stationarity) — note in Kernel Notes if paper addresses this.
- Hybrid BCI: ensure target_events lists are disjoint between tasks.
