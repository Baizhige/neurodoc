# Dataset of Concurrent EEG, ECG, and Behavior with Multiple Doses of Transcranial Electrical Stimulation

**Dataset**: `openneuro_ds003670` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003670
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 62 | **Manual Review**: Pending
**Channels**: 35 | **Sampling Rate**: 2000 Hz

## Paradigm

Participants performed a continuous tracking task (CTT) requiring them to maintain a ball at the center of a screen to assess vigilance and sustained alertness. Simultaneously, multi-site transcranial electrical stimulation (tES) was applied at varying dose combinations (sham, low, high) to modulate arousal and attention. EEG, ECG, and behavioral tracking data were recorded concurrently. The study aims to identify optimal tES parameters for enhancing cognitive performance.

## File Scan Result

> **Kernel SHA256**: `580fa6085db72bd619171bfab71f09723c8be13475bfd248c4e2ade2b1c8b0ab`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0, Impedance` | 126 | event | raw | Impedance check marker |
| `16` | 980 | event | raw | Stimulation Start |
| `2` | 372 | event | raw | Stimulation Stop |
| `32` | 1054 | event | raw | Block Start |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: tES Stimulation Period Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Stimulation Start`, `Block Start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|--------|
  | `Stimulation Start` | 1 | Transcranial electrical stimulation ON period |
  | `Block Start` | 0 | Baseline/control task block (stimulation OFF) |
- **Evidence**:
  - DOI: 10.1038/s41597-021-01046-y — Data descriptor defining dataset structure with 30-sec stimulation epochs during CTT; confirms 5-sec ramp-up/down transitions and binary ON/OFF classification as primary analysis target.
  - DOI: 10.1016/j.brs.2024.05.009 — Uses same dataset implementing 30-sec epoch segmentation comparing stimulation effects on EEG/behavioral vigilant attention; validates epoching approach.
- **Kernel Notes**: Use `epoch_by_long_event_hdf5` to extract 30-sec windows aligned to `Stimulation Start` (y=1, stimulation ON) and `Block Start` (y=0, baseline OFF). Event codes in raw data: code 16→`Stimulation Start`, code 32→`Block Start`. Verify tmax matches actual stimulation duration per trial. Consider baseline correction window from -0.5 to 0 s to address ramp artifact.

### Classical Task 2: Frontal vs Motor 30Hz HD-tACS Comparison
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Stimulation Start`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|--------|
  | `F30` | 0 | Frontal 30Hz HD-tACS (active stimulation) |
  | `M30` | 1 | Motor 30Hz HD-tACS (active stimulation) |
- **Super Meta Notes**: Derived from raw event `Stimulation Start` combined with dose condition metadata (F0/F5/F30, M0/M5/M30) in participants.tsv or events.tsv. Kernel step: filter `Stimulation Start` events to only those where dose code contains 'F30' (label 0) or 'M30' (label 1), excluding sham and other frequency conditions.
- **Evidence**:
  - DOI: 10.1016/j.brs.2024.05.009 — Explicitly compares frontal 30Hz HD-tACS vs motor 30Hz HD-tACS effects on EEG/behavioral vigilant attention; uses 30-sec epoch partitioning by stimulation location; labels F30=frontal, M30=motor.
- **Kernel Notes**: Requires joining `Stimulation Start` event timestamps with dose condition metadata to distinguish F30 vs M30 conditions. Use 30-sec windows following `Stimulation Start` for each active 30Hz condition. Verify dose condition codes exist in events.tsv before implementation.

### Potential Task 1: Stimulation Ramp Dynamics Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`Stimulation Start`, `Stimulation Stop`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|--------|
  | `Stimulation Start` | 1 | tES ramp-ON transient period |
  | `Stimulation Stop` | 0 | tES ramp-OFF transient period |
- **Evidence**:
  - DOI: 10.1038/s41597-021-01046-y — Documents 5-sec ramp-up/down transitions during tES delivery; ramp periods provide distinct transient dynamics for analysis.
- **Kernel Notes**: Shorter 2-sec windows with 50% overlap enable detailed characterization of tES artifact and neural response during transition periods. Event codes: code 16→`Stimulation Start`, code 2→`Stimulation Stop`. Consider baseline correction using pre-onset window. High sampling rate (2000 Hz) may require downsampling to 500 Hz for memory efficiency.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
