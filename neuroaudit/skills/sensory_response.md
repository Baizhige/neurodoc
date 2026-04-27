# SKILL: Sensory/Response — ERP, P300, SSVEP, Auditory/Visual

## Category Coverage
Datasets driven by external sensory stimulation and subject responses. Includes: P300 speller, N2/N400 ERP, SSVEP, auditory oddball, visual evoked potentials, steady-state responses.

## Epoch Alignment
- **Always onset-aligned**: event marker = stimulus onset. tmin is typically slightly negative for pre-stimulus baseline.
- **P300 / oddball**: tmin = -0.1 to -0.2 s, tmax = 0.8 to 1.0 s.
- **SSVEP**: tmin = 0.0 s, tmax = 1.0–5.0 s (depends on frequency resolution needed).
- **Auditory ERP (N1/P2/N2/P3)**: tmin = -0.1 s, tmax = 0.6–1.0 s.
- **Long auditory trials** (speech-in-noise, cocktail party): use `epoch_by_long_event_hdf5`.

### Typical Epoch Windows
| Paradigm | tmin | tmax | Notes |
|---|---|---|---|
| P300 speller | -0.1 s | 0.8 s | Flash-locked, target vs non-target |
| Visual ERP / N2 | -0.2 s | 1.0 s | Stimulus-locked |
| SSVEP | 0.0 s | 2.0–5.0 s | Needs sufficient duration for frequency analysis |
| Auditory oddball | -0.1 s | 0.6 s | Standard MMN / P3 window |
| Long auditory trial | 0.0 s | trial duration | Use epoch_by_long_event_hdf5 |

## Target Events
- **P300**: binary — target flash vs non-target flash. Raw IDs often `target_flash` / `nontarget_flash`.
- **SSVEP**: frequency classes (e.g. 8 Hz, 10 Hz, 12 Hz, 15 Hz).
- **Oddball**: target tone vs standard tone, or deviant vs standard.
- Flash sequences: event per-row/column flash vs per-character target — clarify in Kernel Notes.

## Task Types
- **Classical**: N-class classification (frequency for SSVEP, target/non-target for P300).
- **Potential**: cross-subject generalization, regression on ERP amplitude.
- BCI speller accuracy tasks: classification of intended character — may be super meta.

## Evidence Quality Notes
- SSVEP papers often report ITR (information transfer rate) — confirm epoch length matches frequency resolution.
- P300 papers: confirm whether analysis is single-trial or averaged across repetitions.
- If paper uses only a subset of frequencies/stimuli, note which in evidence desc.

## Common Pitfalls
- P300: non-target count >> target count — class imbalance must be noted in Kernel Notes.
- SSVEP: epoch length determines frequency resolution (1/T Hz). Too short → cannot resolve target frequency.
- Auditory: baseline period may contain previous trial's response. Use pre-stimulus window carefully.
- Flash-based paradigms: distinguish per-flash epoch vs per-sequence epoch.
