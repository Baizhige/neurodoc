# TUH EEG Corpus (Base)

**Dataset**: `tuh_eeg` | **Year**: 2002-2017 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 10874 | **Files (Completed)**: 69652 | **Channels**: 17-128 | **Sampling Rate**: 250-1000 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The Temple University Hospital EEG Corpus (v2.0.1) is the largest publicly available clinical EEG archive, containing approximately 69,652 EDF recordings from 10874 de-identified patients. Recordings span routine clinical EEG sessions performed for neurological evaluation (epilepsy monitoring, encephalopathy, post-operative assessment, etc.). Three standard TCP (Temporal Central Parasagittal) referential montages are used: `01_tcp_ar` (average reference), `02_tcp_le` (linked ears), and `03_tcp_ar_a` (alternating average reference). Channel counts vary (17-128) and multiple sampling rates are present (250, 256, 400, 512, 1000 Hz). No structured experiment events exist; EDF annotations are clinical technician notes in free text.

## File Scan Result

> **Kernel SHA256**: `None
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

> No structured classification annotations. The base corpus is not labeled for any specific ML task, so it generaly use for pre-training; use specialized TUH subsets (tuh_eeg_abnormal, tuh_eeg_seizure, etc.) for supervised learning.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | using NicoletOne(Natus) |


## Tasks


## Data Quality Notes
-

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed