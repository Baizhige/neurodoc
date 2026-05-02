# ANDI: Auditory N-back Dual-task EEG

**Dataset**: `openneuro_ds004661` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004661
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 17 | **Channels**: 64 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

A dual-task paradigm combining a guided visual search task (tracking a red annulus) with an auditory N-back working memory task to study cognitive interference. Event code `1` marks the dominant condition and `2` marks the minority condition. The large imbalance between codes (~10:1) suggests standard auditory stimuli versus N-back target matches requiring working memory retrieval. EEG was recorded with 64 channels at 128 Hz during task performance.

## File Scan Result

> **Kernel SHA256**: `8a5beca537c69800096f1175816fc9b12347611b0b81c820cbe913ed6dcc87e7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 29820 | admin | raw | Unknown system marker - not present in events.tsv files, appears only in pre-scan count |
| `2` | 2948 | admin | raw | Unknown system marker - not present in events.tsv files, appears only in pre-scan count |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Event IDs `1` and `2` are classified as `admin` type with `Unknown system marker` meaning, indicating they appear only in pre-scan counts and are not present in events.tsv files, creating uncertainty about actual event annotation availability.
- Strong class imbalance (~10:1 ratio, 29,820 vs 2,948 events) requires careful handling via undersampling or weighted loss functions for classification tasks.
- Low sampling rate (128 Hz) limits spectral resolution above 40 Hz (Nyquist frequency); appropriate anti-aliasing and bandpass filtering needed during preprocessing.
- Missing metadata fields: `age`, `sex`, and `device` information are completely absent, limiting demographic and equipment-based analyses.
- Raw event codes in files may differ from documented codes (e.g., `10`/`11` mentioned in README vs `1`/`2` found); mapping verification required against dataset README.
- Visual search task details (tracking accuracy, annulus position events) not directly captured in available event structure; requires verification from dataset supplementary files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
