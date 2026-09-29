# Simon-conflict Task

**Dataset**: `openneuro_ds004580` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004580
**Category**: Sensory/Response | **Subjects**: 147 | **Files (Completed)**: 147 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants performed a Simon conflict task in which stimulus location (left/right) could be congruent or incongruent with the required response direction. S 1 marks visual cue onset and S 2 marks response onset; S 3 is a rare system marker. The dataset includes both Parkinson's disease (PD) patients and healthy controls, with demographic and clinical variables (AGE, GENDER, MOCA, UPDRS, GROUP, TYPE) available in participants.tsv for subject-level analyses.

## File Scan Result

> **Kernel SHA256**: `4bcfb5ffaf6e327f721c71f8fc585f2afa0042b02ffeb2f5e10193d27587cb5c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 55922 | event | raw | Visual cue onset |
| `S  2` | 54800 | event | raw | Response onset |
| `S  3` | 1 | admin | raw | Unknown system marker |
| `S255` | 6 | admin | raw | Unknown system marker |
| `boundary` | 156 | admin | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Event meanings in File Scan Result differ from original draft: S 1 is "Visual cue onset" (not "Congruent trial") and S 2 is "Response onset" (not "Incongruent trial"), indicating the event structure represents trial phase timing rather than condition labeling.
- S 3 has only 1 occurrence across all subjects, making it unsuitable for any task; previously described as "Rare/catch trial" but scan shows "Unknown system marker".
- Subject count discrepancy: original draft listed 30 subjects, but File Scan Result and Tasks indicate 147 subjects with complete data in participants.tsv.
- `age` and `sex` fields are missing from EEG metadata, but AGE and GENDER are complete in participants.tsv (147 subjects), requiring info-based label routing.
- UPDRS data is partial (99/147 subjects), requiring imputation or exclusion for regression tasks.
- `device` field is missing; equipment details unknown from scan metadata.
- 156 boundary markers present; segmentation-based approaches naturally handle these, but event-based analyses would need boundary-aware epoch rejection.
- TYPE and GROUP fields are redundant (both encode PD vs Control), providing duplicate classification targets.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
