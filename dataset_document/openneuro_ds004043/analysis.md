# The time-course of feature-based attention effects dissociated from temporal expectation and target-related processes

**Dataset**: `openneuro_ds004043` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004043
**Category**: Sensory/Response | **Subjects**: 20 | **Files (Completed)**: 40 | **Channels**: 63 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

Participants viewed rapid sequences of overlaid oriented grating pairs (presented at ~10 Hz) and detected a target orientation while attention was cued to different feature dimensions (orientation or color). The study dissociates the time-course of feature-based attention effects from temporal expectation and target-detection processes using EEG frequency-tagging and ERP methods.

## File Scan Result

> **Kernel SHA256**: `cf2c5c509c449ae0372c32ce812ec51bb50af363fbd45dab2b23ba5b98ee3f99`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E  1` | 174080 | event | raw | Stimulus onset |
| `E  2` | 174080 | event | raw | Stimulus offset |
| `E  3` | 1280 | event | raw | Trial phase onset: block start |
| `Event/E  1` | 174080 | event | raw | Stimulus onset |
| `Event/E  2` | 174080 | event | raw | Stimulus offset |
| `Event/E  3` | 1280 | event | raw | Trial phase onset: block start |
| `boundary` | 20 | admin | raw | Subject boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class cued vs uncued attention
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`E  1`, `E  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `E  1` | 0 | Cued / attended stimulus onset |
  | `E  2` | 1 | Uncued / ignored stimulus offset |
- **Evidence**:
  - 10.1038/s41598-022-10687-x — Peer-reviewed MVPA study using LDA classifiers to decode cued vs uncued orientation from EEG epochs; E 1 marks stimulus onset (cued/attended), E 2 marks stimulus offset (uncued/ignored); analysis restricted to non-target trials; attention effect emerged ~230ms post-stimulus; epochs from -100ms to 800ms
  - 10.1101/2021.05.24.445376 — Preprint describing same paradigm with identical epoch parameters for MVPA classification
- **Notes**: The two event codes E 1 and E 2 alternate with ~100ms intervals matching stimulus duration, forming a natural cued/uncued pairing. E 3 block-start trials and boundary markers are excluded. The classification directly uses the event identity as the class label (archetype A, raw meta level).

## Data Quality Notes

- Event meanings in the scan result (stimulus onset/offset/block start) differ from the original paper's interpretation (attended feature dimension / non-attended feature dimension / target/distractor trials), creating ambiguity in event labeling that requires manual verification against the original study documentation.
- `E  2` is labeled as "stimulus offset" in the scan but used as "uncued/ignored" in the task definition; this semantic mismatch needs resolution before analysis.
- `E  3` has substantially lower count (1280 vs ~174K) and is labeled as "block start" rather than target/distractor trials, conflicting with prior draft interpretation.
- Duplicated event markers exist with `Event/E  1`, `Event/E  2`, `Event/E  3` prefixes (EEGLAB-style variants) that are exact duplicates of base events and should be deduplicated during preprocessing.
- Subject demographic fields (`age`, `sex`) are missing from dataset metadata.
- Recording device information is missing from dataset metadata.
- `boundary` markers are classified as `admin` type rather than `event` type, which is correct for segment boundaries but should be verified they represent subject-level boundaries (20 count matches 20 subjects).
- Very high event counts per file (~174K per condition) will produce large epoch sets requiring memory-efficient processing pipelines.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
