# SKILL: Action/Output — Motor Imagery & Movement

## Category Coverage
Datasets where subjects perform or imagine limb movements, finger movements, speech articulation, or other voluntary motor actions. Includes: Motor Imagery (MI), Motor Movement (MM), combined MI+MM datasets.

## Epoch Alignment (CRITICAL)

### Onset vs Offset
- **Most MI datasets**: event marker = cue ONSET (e.g. BCI2000, EEGMMIDB, OpenBMI). Use tmin ≥ 0.
- **Some older datasets** (e.g. BCI Competition II/III): marker = cue OFFSET. Use tmin negative to capture the full imagery window before offset.
- **How to detect offset alignment**: Paradigm description says "marker at end of cue" or "T2 marks end of trial". If unclear, check if tmin in papers is strongly negative (e.g. -4.0s).
- **Always state the alignment assumption in Kernel Notes.**

### Typical Epoch Windows
| Paradigm | tmin | tmax | Notes |
|---|---|---|---|
| Cue-based MI (onset) | 0.0 s | 3.0–4.0 s | Standard BCI Competition / PhysioNet |
| Cue-based MI with baseline | -0.5 s | 3.0–4.0 s | When pre-cue baseline is needed |
| Finger MI (5F) | 0.0 s | 0.85–3.0 s | Shorter windows often used |
| Real movement | 0.0 s | 3.0 s | Same window as corresponding MI |
| Rest/passive state | 0.0 s | 3.0 s | Use same window as active classes |

### tmin/tmax Rules
- **tmin = 0**: epoch starts at cue onset. Most common for online BCI paradigms.
- **tmin = -0.5 to -0.2**: includes pre-stimulus baseline. Preferred for offline analysis with baseline correction.
- **tmax = 3.0 s**: conservative; avoids overlap with rest period.
- **tmax = 4.0 s**: captures full cue duration when cue lasts 4 s.
- Mark any parameter not explicitly stated in paper with `*`.

## Target Events & Label Mapping
- Use EXACT raw event ID strings from Event Structure table.
- Papers often use natural language ("left hand", "LH", "class 1") → map to raw IDs.
- Common mappings: left hand → 0, right hand → 1, feet → 2 or 3, tongue → 4.
- **Rest/T0 events**: typically EXCLUDED from target_events unless the task is rest vs. active.
- **Run-dependent meaning** (e.g. EEGMMIDB T1/T2): state filter logic in Kernel Notes.

## Task Types
- **Classical Task** (most common): N-class MI classification backed by paper evidence.
- **Binary subsets**: left vs right, fists vs feet — common Potential Tasks if no direct evidence.
- **Combined MI+MM**: pool imagery and movement events with same label → super meta, must explain derivation.
- **Resting-state baseline**: use `epoch_by_segmentation_hdf5` if no cue events present.

## Evidence Quality Notes
- Paper must **explicitly name the dataset** (not just "a public MI dataset").
- Paper must specify **number of classes** and **which classes** were used.
- If epoch window is not stated, mark with `*` and use paradigm default.
- If paper uses dataset but different subset (e.g. only CLA protocol), note in evidence desc.

## Common Pitfalls
- EEGMMIDB: T1/T2 meaning changes per run — kernel must filter by run number before epoching.
- Multi-protocol datasets (e.g. figshare_largemi CLA/HaLT/5F): each protocol may need separate task.
- Sampling rate mismatch: some datasets mix 200 Hz and 1000 Hz — note in Kernel Notes.
- Rest events between trials: exclude `Rest` / `T0` from target_events unless specifically studied.
