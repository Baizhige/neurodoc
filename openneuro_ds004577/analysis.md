# Dataset containing resting EEG for a sample of 103 normal infants in the first year of life

**Dataset**: `openneuro_ds004577` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004577
**Category**: Biological State | **Subjects**: 103 | **Files (Completed)**: 103 | **Channels**: 128 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG recordings from 103 healthy infants (aged 1-12 months) during the first year of life. Recordings were made during natural infant rest/sleep states. Eyes-open and eyes-closed state markers are present but the primary data is continuous infant resting EEG. The dataset supports developmental neuroscience research on early brain maturation.

## File Scan Result

> **Kernel SHA256**: `446d444aed1a6f5f3f5bd75eac8a086d494aabe6149cdf14a606f8bc29109a26`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Eyes-Closed vs Eyes-Open State Classification
- **Task Type**: binary_classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes_closed` | 0 | Eyes-closed resting state segment |
  | `eyes_open` | 1 | Eyes-open resting state segment |
- **Evidence (DOI)**: — (plausible from paradigm alone; no direct classification reference)
- **Kernel Notes**: Resting-state continuous EEG from infants without discrete trial structure. Apply sliding window segmentation across the recording to generate epochs. Exclude or flag segments containing or adjacent to `discontinuity` events to avoid artifact-corrupted data. Subject-level normalization may be necessary given wide age range (1-12 months). Binary classification task: eyes-open vs eyes-closed state segments. Class balance between states may vary substantially across subjects due to variable state duration; ensure balanced sampling during training. The 50% overlap increases temporal resolution for detecting developmental changes but increases computational cost; reduce overlap to 0.0 if compute-constrained.