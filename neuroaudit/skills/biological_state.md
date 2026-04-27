# SKILL: Biological State — Sleep, Seizure, Continuous Monitoring

## Category Coverage
Datasets recording sustained biological states rather than discrete events. Includes: sleep staging, seizure detection, epilepsy monitoring, drowsiness, fatigue, continuous pathological state detection.

## Epoch Method Selection (CRITICAL)
- **Sleep staging**: `epoch_by_long_event_hdf5` — annotations mark sleep stages (W, N1, N2, N3, REM) with duration.
  - tmin = 0 s, tmax = 30 s (standard PSG epoch), overlap = 0.0
- **Seizure detection**: `epoch_by_long_event_hdf5` — seizure annotations have variable duration.
  - tmin = 0 s, tmax = full annotation duration, overlap = 0.0 (or sliding if specified)
- **Resting-state / unannotated continuous**: `epoch_by_segmentation_hdf5`
  - segment_length = 4–30 s, overlap = 0.0–0.5 depending on paper
- **Do NOT use `epoch_by_event_hdf5`** for sustained states — it is for discrete short events only.

### Typical Parameters
| Paradigm | Method | tmin | tmax / length | overlap |
|---|---|---|---|---|
| Sleep staging (PSG) | epoch_by_long_event_hdf5 | 0 s | 30 s | 0.0 |
| Seizure (ictal) | epoch_by_long_event_hdf5 | 0 s | annotation duration | 0.0 |
| Resting-state | epoch_by_segmentation_hdf5 | — | 4–10 s | 0.0–0.5 |
| Drowsiness / fatigue | epoch_by_long_event_hdf5 | 0 s | 4–30 s | 0.0–0.5 |

## Target Events
- Sleep: stage labels as annotation strings (e.g. `Sleep stage W`, `Sleep stage N2`, `Sleep stage R`).
- Seizure: `seiz` / `bckg` or dataset-specific annotation strings. Must use raw IDs exactly.
- Preictal vs ictal: time-based derivation → super meta, explain in Kernel Notes.

## Task Types
- **Classical**: sleep stage classification (5-class W/N1/N2/N3/REM, or simplified 3-class).
- **Classical**: seizure detection (ictal vs interictal).
- **Potential**: preictal prediction (super meta — needs time-windowing logic).
- **Potential**: anomaly detection on continuous EEG.

## Evidence Quality Notes
- Sleep staging papers: confirm which staging standard (AASM 2007 vs R&K) and number of classes.
- Seizure papers: confirm whether patient-specific or cross-patient; confirm ictal/interictal definition.
- If paper uses sliding window within annotations, set overlap accordingly.

## Common Pitfalls
- Sleep: class imbalance (N3 and REM are rare). Note in Kernel Notes.
- Seizure: inter-patient variability is high — note in Kernel Notes if patient-specific split required.
- Long annotations with variable duration: use full duration (tmax = annotation end), not fixed window, unless paper specifies sliding.
- Unannotated resting-state in a dataset that has some annotations: use segmentation only on unannotated portions — clarify scope in Kernel Notes.
