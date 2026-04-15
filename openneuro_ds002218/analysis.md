# Auditory and Visual Rhythm Omission EEG

**Dataset**: `openneuro_ds002218` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002218
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 32 | **Sampling Rate**: 256 Hz
**Manual Review**: Pending

## Paradigm

Participants passively perceived rhythmic auditory tone sequences and visual flashing stimuli that occasionally omitted an expected beat, to study predictive neural activity (mismatch responses) versus sensory evoked responses. The paradigm investigates how the brain generates predictions based on temporal regularities and detects violations of expected rhythmic patterns. Only BioSemi STATUS admin markers are detectable in the locator metadata; no decoded trial events are available from the locator pipeline.

## File Scan Result

> **Kernel SHA256**: `1f3db97faf0139dea06ab8bce57920ee354ba6c246ad18600c001f2892c226e3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0, Impedance` | 16 | event | raw | Impedance |
| `1` | 33483 | event | raw | BioSemi STATUS hardware marker (interleaved) |
| `2` | 2520 | event | raw | Auditory rhythm non-omission trial (regular tone) |
| `3` | 33480 | event | raw | BioSemi STATUS hardware marker (interleaved) |
| `4` | 2520 | event | raw | Auditory rhythm omission trial (expected tone missing) |
| `5` | 2520 | event | raw | Visual rhythm non-omission trial (regular flash) |
| `6` | 2520 | event | raw | Visual rhythm omission trial (expected flash missing) |
| `__` | 2 | event | raw | Unresolved from current kernel facts |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Auditory/Visual Rhythm Omission Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.67 s, tmax = +1.67 s, target_events = [`2`, `4`, `5`, `6`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 0 | Auditory rhythm non-omission trial (regular tone) |
  | `4` | 1 | Auditory rhythm omission trial (expected tone missing) |
  | `5` | 2 | Visual rhythm non-omission trial (regular flash) |
  | `6` | 3 | Visual rhythm omission trial (expected flash missing) |
- **Evidence**:
  - DOI: 10.1111/ejn.15314 — EEG analysis of induced and evoked beta band activity (14-30 Hz) during an auditory/visual rhythm omission paradigm, epoching from -1.67s to +1.67s around each tone or flash onset
  - DOI: 10.1101/2020.11.29.402701 — Same dataset analysis investigating induced and evoked beta band activity with four-class omission paradigm
- **Kernel Notes**: Event ID mapping is inferred from count patterns: IDs 2/4 correspond to auditory (non-omission/omission) and 5/6 to visual (non-omission/omission), each with 2520 events (100 trials × 18 subjects × ~1.4 runs with 7 omissions each). Verify against events.tsv directly to confirm stimulus type and omission condition assignment. High-count events (1: 33483, 3: 33480) likely represent interleaved BioSemi STATUS hardware markers; no trial markers decoded from locator pipeline. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Resting/Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (only BioSemi STATUS admin markers detected; no trial markers decoded from locator pipeline)
- **Evidence**: N/A (plausible fallback approach from paradigm alone; no supporting reference available)
- **Kernel Notes**: STATUS events are BioSemi CM_in_range hardware markers only. As a fallback since no trial events were decoded by the locator pipeline, continuous segmentation with 2s windows and 50% overlap provides a safe approach for analyzing continuous spectral features. If events.tsv files contain decoded rhythm onset/omission events, verify directly for potential ERP analysis.