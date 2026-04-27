# Neuma (Neuromarketing)

**Dataset**: `openneuro_ds004588` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004588
**Category**: Complex Applied | **Subjects**: 42 | **Files (Completed)**: 84 | **Channels**: 6 | **Sampling Rate**: 300 Hz
**Manual Review**: Pending

## Paradigm

A multimodal neuromarketing study where 42 participants browsed supermarket product brochures displayed on screen and selected items they intended to purchase by clicking the left mouse button. EEG was recorded alongside mouse interaction data to identify neural correlates of consumer purchase decisions during free-browsing. Each session involved scrolling through 6 product leaflet images (FYLLADIO_1.tif through FYLLADIO_6.tif) presented in a sequential format, with a fixation cross marking trial start and end-of-experiment markers signaling session completion.

## File Scan Result

> **Kernel SHA256**: `ed1d082a45a87a71d0c3b10c1e2c9c35ec765c84e5f403e02f68b2c91509ac7a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Category:IMG=ID:FYLLADIO_1.tif=Type:Leaflet_Images_1` | 268 | event | raw | Product leaflet image 1 onset |
| `Category:IMG=ID:FYLLADIO_2.tif=Type:Leaflet_Images_1` | 138 | event | raw | Product leaflet image 2 onset |
| `Category:IMG=ID:FYLLADIO_3.tif=Type:Leaflet_Images_1` | 124 | event | raw | Product leaflet image 3 onset |
| `Category:IMG=ID:FYLLADIO_4.tif=Type:Leaflet_Images_1` | 128 | event | raw | Product leaflet image 4 onset |
| `Category:IMG=ID:FYLLADIO_5.tif=Type:Leaflet_Images_1` | 124 | event | raw | Product leaflet image 5 onset |
| `Category:IMG=ID:FYLLADIO_6.tif=Type:Leaflet_Images_1` | 120 | event | raw | Product leaflet image 6 onset |
| `EOE` | 84 | event | raw | End-of-experiment marker |
| `MouseButt` | 1 | event | raw |  |
| `MouseButtonLeft pressed` | 1734 | event | raw | Left mouse button press (product selection) |
| `MouseButtonLeft released` | 1712 | event | raw | Left mouse button release |
| `MouseButtonMiddle pressed` | 2 | event | raw | Middle mouse button press |
| `MouseButtonMiddle released` | 2 | event | raw | Middle mouse button release |
| `MouseButtonRight pressed` | 2 | event | raw | Right mouse button press |
| `MouseButtonRight released` | 2 | event | raw | Right mouse button release |
| `MouseButt�>�` | 1 | event | raw |  |
| `MouseWheelDown120 pressed` | 210 | admin | raw | Scroll-down wheel event |
| `MouseWheelUp120 pressed` | 76 | admin | raw | Scroll-up wheel event |
| `fixation_cross` | 84 | event | raw | Fixation cross onset (trial start) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Consumer Intent Classification (Buy vs NoBuy)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Category:IMG=ID:FYLLADIO_1.tif=Type:Leaflet_Images_1`, `Category:IMG=ID:FYLLADIO_2.tif=Type:Leaflet_Images_1`, `Category:IMG=ID:FYLLADIO_3.tif=Type:Leaflet_Images_1`, `Category:IMG=ID:FYLLADIO_4.tif=Type:Leaflet_Images_1`, `Category:IMG=ID:FYLLADIO_5.tif=Type:Leaflet_Images_1`, `Category:IMG=ID:FYLLADIO_6.tif=Type:Leaflet_Images_1`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Buy` | 0 | Product selected via left mouse click (purchase intent) |
  | `NoBuy` | 1 | Product viewed but not selected |
- **Super Meta Notes**: Labels derived from raw events. Kernel must: (1) segment epochs around all 6 product leaflet image onsets (FYLLADIO_1-6.tif, aggregated as Leaflet_Images_1 category); (2) check for occurrence of `MouseButtonLeft pressed` within the 4-second epoch window; (3) assign Buy label if click present, NoBuy otherwise. On average ~18 products clicked and ~126 not clicked per subject across 144 total products. Exclude `MouseWheelDown120 pressed` and `MouseWheelUp120 pressed` as admin events.
- **Evidence**:
  - DOI: 10.1186/s40708-025-00272-z — Hybrid neuromarketing approach combining EEG graph signal processing with gaze dynamic patterning for Buy vs NoBuy classification. Uses 4.0s epoch window around product image onsets, labels derived from mouse click presence. Preprocessing: 0.5–45 Hz bandpass (3rd-order Butterworth), ASR and FORCe artifact removal. Reports kappa improvements of 0.08–0.30 and F1 improvements of 0.06–0.23 over baselines.
  - DOI: 10.1038/s41597-023-02392-9 — NeuMa dataset descriptor. 42 subjects, 19 EEG channels (10–20 system), eye-tracking, mouse clicks. Paradigm: free browsing of 144 products across 6 brochure pages. Buy/NoBuy labels confirmed as primary classification target.
  - DOI: 10.21203/rs.3.rs-8736773.v1 — Wide & Deep multimodal framework for consumer preference using EEG (19 channels) and eye-tracking (6 channels). Achieves 77.51% accuracy (±0.49%) and 74.60% weighted F1-score (±0.21%). Confirms epoch-based segmentation around product image onsets with click-derived labels.
- **Kernel Notes**: Only 6 EEG channels available (dataset documentation indicates 19 channels originally). Limited spatial resolution restricts topographical analysis; focus on temporal features. Product category events embed full image filenames—aggregate all FYLLADIO_1-6.tif events as Leaflet_Images_1 category. Preprocessing per reference papers: 0.5–45 Hz bandpass filter, ASR and FORCe artifact removal. Exclude epochs <0.5s duration.

### Potential Task 1: Mouse Click Neural Correlates
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`MouseButtonLeft pressed`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `MouseButtonLeft pressed` | 0 | Left mouse button press (product selection action) |
- **Evidence**: None — task inferred from paradigm. Left mouse button presses (1734 total) indicate product selection moments during free browsing. The -0.2 to 1.0s window captures motor preparation and execution phases of the click action. While no published paper explicitly analyzes EEG around click events separately from product viewing, this represents a plausible motor-related potential analysis.
- **Kernel Notes**: Scroll wheel events (`MouseWheelDown120 pressed`, `MouseWheelUp120 pressed`) are admin data—exclude from analysis. Very limited spatial resolution with 6 EEG channels. Mouse clicks occur asynchronously relative to image onsets; variable timing within product viewing windows may introduce latency confounds. Consider aligning epochs by click onset rather than image onset for this task.