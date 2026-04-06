# Mendeley Speech-in-Noise (SiN) Auditory Attention Decoding Dataset

**Dataset**: `mendeley_sin` | **Year**: 2021 | **URL**: https://data.mendeley.com/datasets/jyvythkz5y/2
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26 | **Channels**: 66 | **Sampling Rate**: 256 Hz

## Paradigm

Twenty-six normal-hearing subjects (NH_subject01-NH_subject26) participated in a cocktail-party auditory attention decoding (AAD) task in which competing speech was presented with background noise at two signal-to-noise conditions. EEG was recorded from 64 channels plus 2 mastoid references (total 66 channels) at 256 Hz. Each subject's `.mat` file contains pre-epoched EEG data as a 3D array `(896, 66, 100)` - 896 time points x 66 channels x 100 trials - for each of two Speech-in-Noise conditions (condition 7 and condition 13). The Case B kernel concatenates the 100 trials for each condition into a single continuous raw signal and annotates each trial with its condition label. This dataset is identical in content and structure to `zenodo_sin` (which is a Zenodo mirror of this Mendeley original).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://data.mendeley.com/datasets/jyvythkz5y/2

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `SiN_condition_7` | ~1300 (~50/subject x 26) | long | raw | Speech-in-Noise condition 7 trial (one cocktail-party condition) |
| `SiN_condition_13` | ~1300 (~50/subject x 26) | long | raw | Speech-in-Noise condition 13 trial (second cocktail-party condition) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Case B kernel: pre-epoched `.mat` data; each file reconstructed into continuous raw by concatenating 100 trials per condition (~3.5 s each at 256 Hz = 896 samples per trial).

## Tasks

### Primary Task 1: Speech-in-noise auditory attention decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Condition or attended-stream labels (released split commonly uses condition 7 vs 13).
- **Evidence**: Dataset documentation describes cocktail-party speech-in-noise auditory attention decoding. Source: https://data.mendeley.com/datasets/jyvythkz5y/2 DOI: https://doi.org/10.17632/jyvythkz5y


### Normal Task 1: Speech-in-Noise Condition Classification - Condition 7 vs. 13 (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.5 s (= 896/256 Hz; matches pre-epoched trial length), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Case B kernel reconstructs continuous raw from pre-epoched data; trial boundaries are annotated. Epoch window (3.5 s) matches the original pre-epoched length; use exactly 896/256 = 3.5 s to avoid boundary effects. sfreq is derived from the `tE` time axis in the `.mat` file (~ 256 Hz). Channel names are generic (`EEG001`-`EEG066`); no channel label metadata is provided.

| Event | y | Meaning |
|-------|---|---------|
| `SiN_condition_7` | 0 | Speech-in-Noise condition 7 |
| `SiN_condition_13` | 1 | Speech-in-Noise condition 13 |
## Data Quality Notes

- Case B kernel: original `.mat` data is pre-epoched (not continuous); reconstruction introduces trial boundary discontinuities.
- Identical content to `zenodo_sin`; the two datasets can be treated as interchangeable.
- Channel names in the reconstructed raw are generic (`EEG001`-`EEG066`); actual electrode layout is 64 EEG + 2 mastoid references.
- No age or sex information available.

## References

- **Reference**: Speech-in-Noise Auditory Attention Decoding Dataset. Mendeley Data. https://data.mendeley.com/datasets/jyvythkz5y/2. See also `zenodo_sin`.
