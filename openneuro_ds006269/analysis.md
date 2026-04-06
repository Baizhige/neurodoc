# Tethered EEG Recordings in Syngap1 Rats

**Dataset**: `openneuro_ds006269` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006269
**Category**: Biological State | **Subjects**: 40 | **Files (Completed)**: 40 | **Channels**: 33 | **Sampling Rate**: 1000 Hz

## Paradigm

Continuous 6-hour tethered EEG recordings were collected from wildtype and Syngap1 mutant rats to monitor spontaneous brain activity and examine circadian-specific neural states. The Syngap1 gene encodes a synaptic GTPase-activating protein and its haploinsufficiency is a model of intellectual disability. The dataset examines spontaneous EEG patterns (sleep/wake states, oscillations) across genotypes.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 40 | admin | raw | Unknown system marker - not usable for classification |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Resting-state analysis baseline
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `wildtype` | 0 | Wildtype rat genotype control |
  | `Syngap1` | 1 | Syngap1 mutant haploinsufficient rat |
- **Super Meta Notes**: Derived from `participants.tsv` metadata (genotype column). Kernel step: read genotype label from subject metadata and assign to all epochs from that subject.
- **Evidence**:
  - DOI: `10.1016/j.celrep.2024.114733` — Dataset contains 6-hour tethered EEG recordings from wildtype and Syngap1 mutant rats for studying synaptic pathophysiology.
- **Kernel Notes**: Extract subject IDs from epochs, lookup genotype from participants.tsv, apply as label. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Continuous Segmentation (long_event)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: N/A (no usable event markers; target_events: null)
- **Notes**: `unknown` is an uninformative system marker. Use subject-level metadata (wildtype vs. Syngap1 mutant genotype) from participants.tsv as classification labels.

## Data Quality Notes

- Only `unknown` events present - no meaningful trial-level annotation.
- Labels must be derived from external genotype metadata (participants.tsv).
- Animal (rat) EEG data; electrode placement and artifact characteristics differ from human EEG.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review