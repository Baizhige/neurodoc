# STRONG (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004849` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004849
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

An EEG dataset recorded during a social-cognitive paradigm involving multiple hierarchically encoded stimulus conditions. The 5-digit numeric trigger codes encode stimulus type, valence, and response. The dataset contains a single aggregated file across participants; specific task details require decoding from events.tsv.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2200` | 1627 | event | raw | Dominant trigger code (primary condition) |
| `72011` | 338 | event | raw | Trigger code (category 7, type 2) |
| `52011` | 332 | event | raw | Trigger code (category 5, type 2) |
| `75011` | 320 | event | raw | Trigger code |
| `55011` | 317 | event | raw | Trigger code |
| `73011` | 316 | event | raw | Trigger code |
| `74011` | 312 | event | raw | Trigger code |
| `53011` | 308 | event | raw | Trigger code |
| `54011` | 307 | event | raw | Trigger code |
| `1` | 195 | event | raw | Trigger code 1 (sync/startx) |
| `71011` | 174 | event | raw | Trigger code |
| `2201` | 173 | event | raw | Trigger code |
| `51011` | 170 | event | raw | Trigger code |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`2200`, `72011`, `52011`, `75011`, `55011`, `73011`, `74011`, `53011`, `54011`, `71011`, `2201`, `51011`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2200` | 0 | Dominant trigger code (primary condition) |
  | `72011` | 1 | Trigger code (category 7, type 2) |
  | `52011` | 2 | Trigger code (category 5, type 2) |
  | `75011` | 3 | Trigger code |
  | `55011` | 4 | Trigger code |
  | `73011` | 5 | Trigger code |
  | `74011` | 6 | Trigger code |
  | `53011` | 7 | Trigger code |
  | `54011` | 8 | Trigger code |
  | `71011` | 9 | Trigger code |
  | `2201` | 10 | Trigger code |
  | `51011` | 11 | Trigger code |
- **Kernel Notes**: Full trigger decode needed from events.tsv. Only 1 file (single aggregated file). Event `1` (sync/startx) excluded from classification as it marks synchronization events rather than stimulus conditions.

## Data Quality Notes

- Single aggregated file; individual subject data not separable without additional metadata.
- Full trigger decode required from events.tsv.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: failed
