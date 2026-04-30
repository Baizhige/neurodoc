# InsurgentCivilian (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004852` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004852
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

An EEG dataset recorded during a dual-paradigm session combining N-back working memory tasks with social-cognitive threat detection (insurgent/civilian classification). The paradigm uses event codes 2090-2098 to indicate 0-back through 8-back working memory load conditions. A large number of event code 2200 occurrences (n=1627) suggests stimulus recycling or repeated display within trials, likely corresponding to individual stimulus presentations in the threat detection component.

## File Scan Result

> **Kernel SHA256**: `073b0786cca4e4167989dc5cd44ecf56e75b8fe41de5f120d497cbdef5972cff`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 195 | event | raw | Trial phase onset: task event |
| `1103` | 120 | event | raw | Trial phase onset: task event |
| `1113` | 75 | event | raw | Trial phase onset: task event |
| `2090` | 66 | event | raw | Trial phase onset: task event |
| `2091` | 114 | event | raw | Trial phase onset: task event |
| `2092` | 96 | event | raw | Trial phase onset: task event |
| `2093` | 124 | event | raw | Trial phase onset: task event |
| `2094` | 90 | event | raw | Trial phase onset: task event |
| `2095` | 86 | event | raw | Trial phase onset: task event |
| `2096` | 111 | event | raw | Trial phase onset: task event |
| `2097` | 109 | event | raw | Trial phase onset: task event |
| `2098` | 104 | event | raw | Trial phase onset: task event |
| `2200` | 1627 | event | raw | Trial phase onset: task event |
| `2201` | 173 | event | raw | Trial phase onset: task event |
| `3` | 15 | event | raw | Trial phase onset: task event |
| `307` | 1 | event | raw | Trial phase onset: task event |
| `4` | 15 | event | raw | Trial phase onset: task event |
| `5` | 32 | event | raw | Trial phase onset: task event |
| `51001` | 5 | event | raw | Participant response |
| `51011` | 170 | event | raw | Participant response |
| `51110` | 19 | event | raw | Participant response |
| `52001` | 16 | event | raw | Participant response |
| `52011` | 332 | event | raw | Participant response |
| `52100` | 1 | event | raw | Participant response |
| `52101` | 1 | event | raw | Participant response |
| `52110` | 14 | event | raw | Participant response |
| `52111` | 21 | event | raw | Participant response |
| `53001` | 34 | event | raw | Participant response |
| `53011` | 308 | event | raw | Participant response |
| `53100` | 3 | event | raw | Participant response |
| `53110` | 19 | event | raw | Participant response |
| `53111` | 16 | event | raw | Participant response |
| `54001` | 41 | event | raw | Participant response |
| `54011` | 307 | event | raw | Participant response |
| `54100` | 3 | event | raw | Participant response |
| `54101` | 2 | event | raw | Participant response |
| `54110` | 16 | event | raw | Participant response |
| `54111` | 13 | event | raw | Participant response |
| `55000` | 1 | event | raw | Participant response |
| `55001` | 36 | event | raw | Participant response |
| `55010` | 1 | event | raw | Participant response |
| `55011` | 317 | event | raw | Participant response |
| `55100` | 2 | event | raw | Participant response |
| `55101` | 3 | event | raw | Participant response |
| `55110` | 19 | event | raw | Participant response |
| `55111` | 16 | event | raw | Participant response |
| `71001` | 6 | event | raw | Participant response |
| `71011` | 174 | event | raw | Participant response |
| `71110` | 19 | event | raw | Participant response |
| `72001` | 19 | event | raw | Participant response |
| `72011` | 338 | event | raw | Participant response |
| `72100` | 1 | event | raw | Participant response |
| `72101` | 1 | event | raw | Participant response |
| `72110` | 14 | event | raw | Participant response |
| `72111` | 21 | event | raw | Participant response |
| `73001` | 38 | event | raw | Participant response |
| `73011` | 316 | event | raw | Participant response |
| `73100` | 3 | event | raw | Participant response |
| `73110` | 19 | event | raw | Participant response |
| `73111` | 16 | event | raw | Participant response |
| `74001` | 43 | event | raw | Participant response |
| `74011` | 312 | event | raw | Participant response |
| `74100` | 3 | event | raw | Participant response |
| `74101` | 2 | event | raw | Participant response |
| `74110` | 16 | event | raw | Participant response |
| `74111` | 14 | event | raw | Participant response |
| `75000` | 1 | event | raw | Participant response |
| `75001` | 40 | event | raw | Participant response |
| `75010` | 1 | event | raw | Participant response |
| `75011` | 320 | event | raw | Participant response |
| `75100` | 2 | event | raw | Participant response |
| `75101` | 3 | event | raw | Participant response |
| `75110` | 19 | event | raw | Participant response |
| `75111` | 16 | event | raw | Participant response |
| `boundary` | 8 | admin | raw | Data boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Single subject with single aggregated file prevents any cross-subject analysis or generalizability assessment.
- Very low sampling rate (128 Hz) limits temporal resolution for ERP analysis and may alias high-frequency components.
- Extremely high event count for code 2200 (n=1627) compared to other task events suggests possible stimulus recycling, re-display, or sub-trial markers that may complicate epoching strategies.
- Missing metadata for subject age, sex, and recording device limits demographic and technical documentation.
- 8 boundary markers indicate data segments were concatenated, which may introduce edge artifacts or discontinuities requiring preprocessing attention.
- Response event codes (51000-75111 range) have complex hierarchical structure with many low-count variants, suggesting a multi-factorial design that is not fully documented in available metadata.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
