# openneuro_ds003739

**Dataset**: `openneuro_ds003739` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003739
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 120 | **Channels**: 149 | **Sampling Rate**: 256 Hz | **Manual Review**: Pending

## Paradigm

Participants performed walking on a treadmill-mounted balance beam while being subjected to sensorimotor perturbations via virtual reality visual rotations and physical waist pulls. The study investigates cortical responses to balance perturbations during standing and walking, with approximately 150 perturbation events per 10-minute session (75 per direction).

## File Scan Result

> **Kernel SHA256**: `a62b9e8ca436ad0865ba816f2d70ea3d545eeb270d6af357e0cd58989812bfef`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 17739 | event | raw | Generic perturbation onset marker requiring metadata-derived labels |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `L_load_cell`, `Mocap_head_anteriorposterior`, `Mocap_head_mediolateral`, `Mocap_head_superiorinferior`, `Mocap_sacrum_anteriorposterior`, `Mocap_sacrum_mediolateral`, `Mocap_sacrum_superiorinferior`, `R_load_cell`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Perturbation Type and Posture Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`stand_pull`, `walk_pull`, `stand_rotate`, `walk_rotate`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stimulus` (stand_pull) | 0 | Physical waist pull while standing — derived from events.tsv posture='standing' & perturbation_type='pull' |
  | `stimulus` (walk_pull) | 1 | Physical waist pull while walking — derived from events.tsv posture='walking' & perturbation_type='pull' |
  | `stimulus` (stand_rotate) | 2 | Visual field rotation while standing — derived from events.tsv posture='standing' & perturbation_type='rotation' |
  | `stimulus` (walk_rotate) | 3 | Visual field rotation while walking — derived from events.tsv posture='walking' & perturbation_type='rotation' |
- **Super Meta Notes**: Derived from experimental condition combining posture (standing/walking) and perturbation type (pull/rotation) from _events.tsv into 4 categorical conditions. Kernel must reconstruct these labels from metadata fields since raw event IDs only contain generic 'stimulus' markers.
- **Evidence**:
  - DOI: 10.1523/ENEURO.0207-18.2018 — Explicitly uses ds003739, 30 participants, 4 conditions, 150 perturbation events per 10-min session, EEG epochs extracted -1s to 2s around perturbation onset.
  - DOI: 10.1016/j.dib.2021.107635 — Describes ds003739 event structure with ~18000 total perturbation events across 30 participants, pull=1s duration, rotation=0.5s duration.
- **Kernel Notes**: CRITICAL VERIFICATION REQUIRED: Original analysis.md assumed discrete event IDs (stand_pull, walk_pull, etc.) but file scan shows 'no_events' with only generic 'stimulus' markers (n=17739). Kernel must: (1) Load events.tsv to extract posture and perturbation_type columns. (2) Reconstruct 4-class labels by combining factors. (3) Map stimulus markers to derived events if needed. (4) Apply bandpass filter 0.5-40 Hz per reference specifications. (5) Document derivation logic, source fields, units, and version tags for super meta labels.

---

### Potential Task 1: Perturbation Direction Classification (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`stimulus`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|-----------------|
  | Needs verification | Direction labels (left=0, right=1) must be derived from events.tsv metadata; no MISC channels present in file scan. Consider alternative label route if events.tsv direction field can be mapped via event reconstruction. |
- **Super Meta Notes**: Direction labels (left/right) must be derived from events.tsv metadata fields. Kernel must combine direction factor with perturbation events to generate binary direction labels.
- **Evidence**:
  - DOI: 10.1016/j.dib.2021.107635 — Mentions 75 events per direction per session, confirming left/right perturbation direction is tracked in metadata.
- **Kernel Notes**: Extract direction field from events.tsv. Filter for valid perturbations only. Apply bandpass filter 0.5-40 Hz. Asymmetric durations (pull=1s vs rotation=0.5s) may require task-specific tmax adjustments.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
