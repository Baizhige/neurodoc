# Selective Auditory Attention EEG Dataset (Normal-Hearing and Hearing-Impaired)

**Dataset**: `zenodo_3618205` | **Year**: 2020 | **URL**: https://zenodo.org/records/3618205
**Category**: High-level Mental | **Subjects**: 44 | **Files (Completed)**: 74 | **Channels**: 73 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Forty-four participants (22 normal-hearing, 22 hearing-impaired) underwent EEG recording in three tasks (Fuglsang et al., 2020): (1) **selective auditory attention** - two-talker competing speech; attend to one of two simultaneously presented speakers; (2) **MMN** - mismatch negativity; passive listening to a standard tone sequence with occasional deviant tones; (3) **resting state** - eyes open and closed. EEG was recorded with BioSemi ActiveTwo (64 channels + reference + auxiliary = ~73 total channels, 512 Hz). Nineteen of the 44 subjects also had in-ear EEG recorded. Event annotations are stored in BIDS-format `_events.tsv` sidecar files.

## File Scan Result

> **Kernel SHA256**: `26205622aa4230b9f05e23fb32ff60c01bed634764a2122da675a000bcb1a4bc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attend_left` | 1056 | event | raw | Subject attends to the left-ear speaker (selective attention trial) |
| `attend_right` | 1056 | event | raw | Subject attends to the right-ear speaker (selective attention trial) |
| `event_192` | 2567 | event | raw |  |
| `event_224` | 2577 | event | raw |  |
| `event_240` | 7560 | event | raw |  |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Auditory Attention Decoding - Left vs. Right (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 60.0 s (or full trial duration), overlap = 30.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Use only files from the selective attention task. MMN and resting state files have different event structures.

| Event | y | Meaning |
|-------|---|-|
| `attend_left` | 0 | Attend to left-ear speaker |
| `attend_right` | 1 | Attend to right-ear speaker |

---

### Potential Task 2: Normal-Hearing vs. Hearing-Impaired Group Comparison (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: As in Task 1, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Needs verification.
- **Notes**: Group labels (normal-hearing / hearing-impaired) must be derived from subject ID and companion demographics file. Primary comparison is neural tracking of attended speech across the two groups.

## Data Quality Notes

- Three distinct task types (selective attention, MMN, rest); always filter files by task type before analysis.
- 19 subjects also have in-ear EEG recordings; these appear as additional channels or separate files.
- Hearing-impaired subjects may have different audiological profiles; audiogram data is available in the dataset.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
