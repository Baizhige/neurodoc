# Resting-State EEG Before and After Cognitive Activity Across the Adult Lifespan (5-Year Follow-Up)

**Dataset**: `openneuro_ds005385` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005385
**Category**: Biological State | **Subjects**: 608 | **Files (Completed)**: 3264 | **Channels**: 65 | **Sampling Rate**: 1000 Hz

## Paradigm

Resting-state EEG was recorded with eyes open and eyes closed before and after a two-hour block of cognitive tasks (working memory, attention, processing speed) across a lifespan cohort of adults. A 5-year longitudinal follow-up is included. BrainVision S-codes (S1-S207+) encode the specific resting-state condition (pre/post x eyes open/closed) and session number.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005385

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 3375 | admin | raw | BrainVision segment boundary (exclude) |
| `S 4`-`S 7` | ~207 each | long | raw | Resting-state session markers (BrainVision S-codes) |
| `S 11`-`S 19` | ~204-205 each | long | raw | Resting-state condition codes |
| `S 14`-`S 16` | 68 each | long | raw | Resting-state condition (higher count subset) |
| `S196`-`S207` | ~205-207 each | long | raw | Session/condition index codes |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 4`, `S 7`, `S 11`, `S 19`, `S 14`, `S 16`, `S196`, `S207`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Age Group Classification from Resting-State EEG Connectivity
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation` | `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `age_20_29` | 0 | Age group 20-29 years |
  | `age_30_39` | 1 | Age group 30-39 years |
  | `age_40_49` | 2 | Age group 40-49 years |
  | `age_50_59` | 3 | Age group 50-59 years |
  | `age_60_70` | 4 | Age group 60-70 years |
- **Super Meta Notes**: Derived from raw EEG by computing eLORETA-based lagged linear connectivity matrices in 7 frequency bands (delta, theta, alpha1, alpha2, beta1, beta2, gamma), then extracting small-world network metrics (clustering coefficient Cw, path length L, small-worldness SW) for hemispheric subnetworks (DMN, FN, AN). Kernel step: Bandpass filter 1-45 Hz, compute connectivity matrices, derive graph-theoretic features, classify age groups.
- **Evidence**:
  - DOI: `10.1007/s11357-025-02042-5` — This study analyzed resting-state EEG data from 539 subjects from OpenNeuro ds005385 to investigate age-related modulations of small-world network architecture across eyes-closed and eyes-open conditions.
- **Kernel Notes**: Verify subject age metadata availability in dataset. Filter to 1-45 Hz. Compute eLORETA connectivity in 7 bands. Extract small-world features per hemisphere. Map ages to 5 bins (20-29, 30-39, 40-49, 50-59, 60-70). (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: EEG Biomarker Reliability Classification (Super Meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s *, overlap = 0.0 *
- **Label Route**: `Annotation` | `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `biomarker_negative` | 0 | Below delta power threshold (non-biomarker) |
  | `biomarker_positive` | 1 | Above delta power threshold (biomarker-positive) |
- **Super Meta Notes**: Derived from raw EEG by computing right fronto-temporal delta band (1-4 Hz) power from 5-min eyes-closed and eyes-open resting recordings. Threshold applied to classify biomarker-positive vs biomarker-negative. Kernel step: Bandpass filter 1-60 Hz, compute delta band PSD, apply threshold from training data to produce binary labels.
- **Evidence**:
  - DOI: `10.64898/2026.03.03.26347351` — This study used the publicly available OpenNeuro dataset ds005385 as Healthy control dataset 2 to evaluate long-term test-retest reliability of the right fronto-temporal delta power signature across approximately 5-year intervals.
- **Kernel Notes**: Verify baseline vs 5-year follow-up session identification. Filter 1-60 Hz. Compute delta band (1-4 Hz) power from right frontal (F4, F8) and right temporal (T4, T6) electrodes. Apply classification threshold (>35% Y-BOCS reduction equivalent or feature threshold from paper). Verify event ID mapping from events.tsv if using stimulus-locked epochs.

### Normal Task 1: Resting Condition Segmentation (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `boundary` (3375) is admin - exclude. S-codes encode resting condition and session; full decode from README/events.tsv required. 3264 files = 608 subjects x multiple sessions.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S 4` | 0 | Resting condition S4 |
 | `S 5` | 1 | Resting condition S5 |
 | `S 6` | 2 | Resting condition S6 |
 | `S 7` | 3 | Resting condition S7 |

## Data Quality Notes

- boundary markers (3375) are admin - exclude.
- Full S-code decode needed from README to identify pre/post and eyes-open/closed conditions.
- Large dataset (3264 files, 608 subjects); high variability across sessions and age groups.

