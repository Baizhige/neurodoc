# Speech-in-Noise (SiN) Auditory Attention Decoding Dataset (Zenodo Mirror)

**Dataset**: `zenodo_sin` | **Year**: 2021 | **URL**: N/A (Zenodo mirror of Mendeley SiN dataset)
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26 | **Channels**: 66 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Twenty-six normal-hearing subjects (NH_subject01-NH_subject26) participated in a cocktail-party auditory attention decoding (AAD) task in which competing speech was presented with background noise at two signal-to-noise conditions (Zenodo mirror of Mendeley SiN dataset). EEG was recorded from 64 channels plus 2 mastoid references (total 66 channels) at 256 Hz. Each subject's `.mat` file contains pre-epoched EEG data as a 3D array `(896, 66, 100)` - 896 time points x 66 channels x 100 trials - for each of two Speech-in-Noise conditions (condition 7 and condition 13). The Case B kernel concatenates the 100 trials for each condition into a single continuous raw signal and annotates each trial with its condition label.

## File Scan Result

> **Kernel SHA256**: `7d3a696f24e5987df0b75e6a3ce8ce37353d8333694d2fa915ef11b62bb099dd`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Sampled

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `SiN_condition_7` | ~1300 (~50/subject x 26) | long | raw | Speech-in-Noise condition 7 trial (one cocktail-party condition) |
| `SiN_condition_13` | ~1300 (~50/subject x 26) | long | raw | Speech-in-Noise condition 13 trial (second cocktail-party condition) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Case B kernel: pre-epoched `.mat` data; each file reconstructed into continuous raw by concatenating 100 trials per condition (~3.5 s each at 256 Hz = 896 samples per trial).

### Info

Dataset is a Zenodo mirror of the Mendeley SiN dataset. Each `.mat` file contains pre-epoched 3D arrays (896 time points x 66 channels x 100 trials) for two conditions.

## Tasks

### Classical Task 1: Speech-in-noise auditory attention decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, target_events = [Needs Verification] | tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Condition or attended-stream labels (released split commonly uses condition 7 vs 13).
- **Evidence**: Speech-in-noise AAD dataset is explicitly provided for supervised attention decoding tasks. Source: https://zenodo.org/

---

### Potential Task 1: Speech-in-Noise Condition Classification - Condition 7 vs. 13 (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.5 s (= 896/256 Hz; matches pre-epoched trial length), target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Case B kernel reconstructs continuous raw from pre-epoched data; trial boundaries are annotated. Epoch window (3.5 s) matches the original pre-epoched length; use exactly 896/256 = 3.5 s to avoid boundary effects.

| Event | y | Meaning |
|-------|---|---------|
| `SiN_condition_7` | 0 | Speech-in-Noise condition 7 |
| `SiN_condition_13` | 1 | Speech-in-Noise condition 13 |

## Data Quality Notes

- Case B kernel: original `.mat` data is pre-epoched (not continuous); reconstruction introduces trial boundary discontinuities.
- Zenodo mirror of the Mendeley SiN dataset (`mendeley_sin`); the two datasets are identical in content and structure.
- No age or sex information available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
