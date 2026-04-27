# SKILL: High-level Mental — Emotion, Workload, Cognitive State

## Category Coverage
Datasets capturing internal cognitive or affective states not directly tied to discrete motor/sensory events. Includes: emotion recognition (valence/arousal), mental workload, cognitive load, attention, stress, fatigue (cognitive), meditation.

## Epoch Method Selection
- **Trial-based with cue events**: `epoch_by_event_hdf5` — stimulus onset marks trial start.
  - tmin = 0.0 s (or small negative for baseline), tmax = trial duration (often 3–60 s for emotion).
- **Long sustained states with annotation**: `epoch_by_long_event_hdf5`
  - tmin = 0 s, tmax = 4–30 s, overlap = 0.0–0.5
- **No clear events, continuous recording**: `epoch_by_segmentation_hdf5`
  - segment_length = 4–10 s, overlap = 0.0–0.5

### Typical Parameters
| Paradigm | Method | tmin | tmax / length | Notes |
|---|---|---|---|---|
| Emotion (video/music cue) | epoch_by_long_event_hdf5 | 0 s | 4–60 s | Sliding window through trial |
| Workload (N-back, driving) | epoch_by_long_event_hdf5 | 0 s | 4–30 s | Overlap 0.0–0.5 |
| Attention (sustained) | epoch_by_segmentation_hdf5 | — | 4–10 s | No discrete events |
| SEED / DEAP style | epoch_by_long_event_hdf5 | 0 s | 4 s | Standard for SEED-series |

## Target Events & Label Derivation
- Emotion datasets: labels (valence/arousal) often come from self-report ratings — **super meta** if rating not directly embedded as annotation.
- Workload: task difficulty level (low/medium/high) often from experimental design file — **super meta**.
- If labels come from companion CSV/metadata file (not EEG annotations): Label Route = `info`, super meta = Yes.
- If labels are embedded as EEG annotations: Label Route = `event` or `misc`, meta level = raw.

## Task Types
- **Classical**: binary or multi-class emotion classification (valence, arousal, dominance).
- **Classical**: workload level classification (2 or 3 levels).
- **Potential**: regression on continuous valence/arousal scores.
- **Potential**: cross-subject generalization benchmarks.

## Evidence Quality Notes
- Emotion papers: confirm which label dimension (valence / arousal / dominance / discrete category).
- Confirm whether labels are binary (H/L threshold) or continuous regression target.
- SEED-series: standard epoch is 4 s sliding window — if paper uses different, note deviation.
- Subject-dependent vs subject-independent split: note in evidence desc if specified.

## Common Pitfalls
- Self-report ratings may not align with EEG recording timestamps — super meta derivation required.
- Long video/music trials: first N seconds often discarded (habituation) — check paper for onset offset.
- Imbalanced classes: some emotion datasets have unequal trial counts per class — note in Kernel Notes.
- DEAP dataset: pre-processed version differs from raw — confirm which version the paper uses.
