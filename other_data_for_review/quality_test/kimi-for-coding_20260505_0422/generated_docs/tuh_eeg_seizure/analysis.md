# TUH EEG Seizure Corpus

**Dataset**: `tuh_eeg_seizure` | **Year**: 2018 | **URL**: https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml
**Category**: Biological State | **Subjects**: 10000+ | **Files (Completed)**: 30000+ | **Channels**: 20-31 | **Sampling Rate**: 250 Hz | **Manual Review**:

## Paradigm

The Temple University Hospital (TUH) EEG Seizure Corpus is a large-scale clinical EEG dataset collected for seizure detection and epilepsy monitoring. Data was recorded from patients in hospital settings using standard 10-20 or 10-10 electrode placement systems during routine clinical monitoring. The dataset contains continuous EEG recordings with expert-annotated seizure events, designed to support automated seizure detection algorithm development and clinical decision support systems.

## File Scan Result

> **Kernel SHA256**: `09bce1c379a94956ea8b16c965bfdc144b90df401d6e607b3d396b77358560c5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `seizure_label` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks



## Data Quality Notes

- No event structure detected in scan; seizure annotations may be stored in alternative formats (e.g., CSV, EDF+ annotations, or separate label files) not captured in standard event table.
- All demographic and equipment metadata fields (age, sex, handedness, amplifier, cap) are missing from file headers; this is typical for de-identified clinical datasets.
- `seizure_label` channel present as raw MISC channel suggests binary or multi-class seizure annotations may be embedded directly in the EEG signal channels rather than as discrete events.
- Clinical EEG data exhibits high variability in recording conditions, electrode configurations, and data quality due to real-world hospital acquisition settings.
- Dataset contains substantial class imbalance typical of seizure corpora (majority non-seizure segments with rare seizure events).

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
