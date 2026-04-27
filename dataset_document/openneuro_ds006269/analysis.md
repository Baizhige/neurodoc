# Tethered EEG Recordings in Syngap1 Rats

**Dataset**: `openneuro_ds006269` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006269
**Category**: Biological State | **Subjects**: 40 | **Files (Completed)**: 40 | **Channels**: 33 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Continuous 6-hour tethered EEG recordings were collected from wildtype and Syngap1 mutant rats to monitor spontaneous brain activity and examine circadian-specific neural states. The Syngap1 gene encodes a synaptic GTPase-activating protein and its haploinsufficiency is a model of intellectual disability. The dataset examines spontaneous EEG patterns (sleep/wake states, oscillations) across genotypes.

## File Scan Result

> **Kernel SHA256**: `b5f97ab18d9052c98c6ae7ae6f3fcdde7f3d0ac27d3737f10ac48bec1c3a6b5f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `EEG027`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Genotype classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `wildtype` | 0 | Wildtype rat genotype control |
  | `Syngap1` | 1 | Syngap1 mutant haploinsufficient rat |
- **Evidence**:
  - DOI: `10.1016/j.celrep.2024.114733` — 6-hour tethered EEG recordings from wildtype and Syngap1 mutant LE rats used to characterize neural phenotypes; supports 2-class genotype classification from spontaneous EEG.
- **Kernel Notes**: Dataset contains only `unknown` admin markers—no usable event IDs. Labels must be derived from subject-level genotype metadata in participants.tsv. Extract subject ID for each recording, lookup genotype (wildtype=0, Syngap1=1), and assign as label to all epochs from that subject. Use fixed-length segmentation (4 s, 50% overlap) for sliding window analysis across the 6-hour continuous recordings. Cross-subject split required (no within-subject mixing) to avoid data leakage given all epochs from a subject share the same label. Consider rat EEG artifact characteristics (muscle artifacts, tethered setup electrical noise) in preprocessing.