# Neuma (Neuromarketing)

**Dataset**: `openneuro_ds004588` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004588
**Category**: Complex Applied | **Subjects**: 42 | **Files (Completed)**: 84 | **Channels**: 6 | **Sampling Rate**: 300 Hz

## Paradigm

A multimodal neuromarketing study where 42 participants browsed supermarket product brochures displayed on screen and selected items they intended to purchase by clicking the left mouse button. EEG was recorded alongside mouse interaction data to identify neural correlates of consumer purchase decisions during free-browsing. Each session involved scrolling through product leaflet images presented in a sequential format.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004588

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `MouseButtonLeft pressed` | 1734 | short | raw | Left mouse button press (product selection / page interaction) |
| `MouseButtonLeft released` | 1712 | short | raw | Left mouse button release |
| `Category:IMG=ID:FYLLADIO_1.tif=...` | 268 | short | raw | Product leaflet image 1 onset |
| `Category:IMG=ID:FYLLADIO_2.tif=...` | 138 | short | raw | Product leaflet image 2 onset |
| `MouseWheelDown120 pressed` | 210 | admin | raw | Scroll-down wheel event (exclude) |
| `MouseWheelUp120 pressed` | 76 | admin | raw | Scroll-up wheel event (exclude) |
| `fixation_cross` | 84 | short | raw | Fixation cross onset (trial start) |
| `EOE` | 84 | short | raw | End-of-experiment marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Consumer Intent Classification (Buy vs NoBuy)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4.0 s *, target_events = [`Category:IMG=ID:FYLLADIO_1.tif=...`, `Category:IMG=ID:FYLLADIO_2.tif=...`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Buy` | 0 | Product viewed and clicked (purchase intent) |
  | `NoBuy` | 1 | Product viewed but not clicked |
- **Super Meta Notes**: Derived from raw events [`MouseButtonLeft pressed`], [`Category:IMG=ID:FYLLADIO_1.tif=...`], [`Category:IMG=ID:FYLLADIO_2.tif=...`]. Kernel step: segment epochs around product image onsets; if a mouse click occurs within the epoch window, label as Buy; otherwise label as NoBuy.
- **Evidence**:
  - DOI: 10.1186/s40708-025-00272-z — Hybrid decoding scheme for classifying consumer intent ('Buy' vs 'NoBuy') using EEG and eye-tracking data from NeuMa dataset, with epochs segmented by gaze location and labels based on mouse clicks.
- **Kernel Notes**: Preprocessing: 0.5-45 Hz bandpass filter (3rd-order Butterworth), ASR and FORCe artifact removal. Epochs <0.5s excluded. Verify event ID mapping from events.tsv for product image categories.

### Normal Task 1: Purchase Interaction Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 6 EEG channels. Category event labels embed full image filenames - aggregate by category type if needed. Scroll wheel events are admin.

 | Event | y | Meaning |
 |-------|---|---------|
 | `fixation_cross` | 0 | Trial-start fixation |
 | `MouseButtonLeft pressed` | 1 | Product purchase/page click

## Data Quality Notes

- Very limited spatial resolution: only 6 EEG channels.
- Category event labels contain full image paths; group by category type for analysis.

