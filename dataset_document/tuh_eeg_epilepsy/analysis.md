# TUH EEG Epilepsy Corpus

**Dataset**: `tuh_eeg_epilepsy` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_epilepsy/v2.0.1/
**Category**: Biological State | **Subjects**: ~2298 | **Files (Completed)**: 2298 | **Channels**: 17-41 | **Sampling Rate**: 250-1000 Hz | **Manual Review**:

## Paradigm

The TUH EEG Epilepsy Corpus (v2.0.1) is a clinically labeled subset of the TUH EEG Corpus where each recording is classified as **epilepsy** or **no epilepsy** based on patients' established clinical diagnoses (not real-time EEG pattern) recorded in hospital notes. Unlike tuh_eeg_seizure, the epilepsy label reflects a patient-level diagnosis, not the presence of ictal activity in the specific recording. The label is extracted from the directory path (`00_epilepsy/` or `01_no_epilepsy/`) and assigned as a single whole-recording annotation by the kernel.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

*Placeholder: File scan results pending completion.*

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `epilepsy:1` | 1785 | long | raw | Patient has a diagnosis of epilepsy (whole-recording label) |
| `no epilepsy:1` | 513 | long | raw | Patient does not have epilepsy (whole-recording label) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each recording has exactly one annotation spanning its full duration.

### Info

- Variable channels (17-41) and sampling rates (250-1000 Hz)
- Class distribution: 1785 epilepsy vs. 513 no-epilepsy (~3.5:1 ratio)

## Tasks

### Primary Task 1: Epilepsy vs non-epilepsy classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Patient/record-level epilepsy label from TUH Epilepsy corpus metadata.
- **Evidence**: TUH Epilepsy Corpus is specifically assembled for epilepsy diagnosis classification research. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.3389/fnins.2016.00196


### Normal Task 1: Epilepsy Patient Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Parse label prefix before the colon. Class imbalance: 1785 epilepsy vs. 513 no-epilepsy (~3.5:1); apply class-balancing. Label is a **patient-level diagnosis**, not an EEG event; the EEG recording may or may not contain ictal activity.

| Event | y | Meaning |
|-------|---|--------|
| `epilepsy:1` | 1 | Epilepsy diagnosis |
| `no epilepsy:1` | 0 | No epilepsy diagnosis |

## Data Quality Notes

- Class imbalance: epilepsy (77.6%) vs. no epilepsy (22.4%); balance before training.
- **Label caveat**: The epilepsy label is a clinical diagnosis from hospital records, not annotation of seizure events within the recording; some epilepsy-labeled recordings may be interictal.
- Variable channels (17-41) and sampling rates (250-1000 Hz); normalize before cross-recording analysis.
- Sex is not reliably available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
