# EEG: Amphetamine trials 5CCPT and Probabilistic Learning

**Dataset**: `openneuro_ds003987` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003987
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 69 | **Channels**: 71 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A double-blind, crossover pharmacological study investigating the effects of d-amphetamine on cognitive performance using two tasks: the 5-Choice Continuous Performance Task (5CCPT), which assesses sustained attention and impulsivity, and a Probabilistic Selection Task (PST), which measures reinforcement learning. EEG was recorded from 23 subjects across three drug sessions (placebo, low-dose, high-dose amphetamine), with recordings obtained using a 71-channel system at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `8688900cc33559d58e37be1e6e7711980833e883ddd87a743f0e6a5e3d26213f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `21 5CCPT` | 16558 | event | raw | Task event marker: 5CCPT response code 21 |
| `22 5CCPT` | 9811 | event | raw | Task event marker: 5CCPT response code 22 |
| `23 5CCPT` | 9547 | event | raw | Task event marker: 5CCPT response code 23 |
| `25 5CCPT` | 4442 | event | raw | Task event marker: 5CCPT response code 25 |
| `unknown_1` | 263 | event | raw | Unmapped task event marker |
| `unknown_10` | 4130 | event | raw | Unmapped task event marker |
| `unknown_11` | 2388 | event | raw | Unmapped task event marker |
| `unknown_12` | 2290 | event | raw | Unmapped task event marker |
| `unknown_13` | 2378 | event | raw | Unmapped task event marker |
| `unknown_14` | 2369 | event | raw | Unmapped task event marker |
| `unknown_15` | 2389 | event | raw | Unmapped task event marker |
| `unknown_16` | 3459 | event | raw | Unmapped task event marker |
| `unknown_17` | 7445 | event | raw | Unmapped task event marker |
| `unknown_18` | 5055 | event | raw | Unmapped task event marker |
| `unknown_19` | 3745 | event | raw | Unmapped task event marker |
| `unknown_2` | 2482 | event | raw | Unmapped task event marker |
| `unknown_20` | 2383 | event | raw | Unmapped task event marker |
| `unknown_24` | 4804 | event | raw | Unmapped task event marker |
| `unknown_26` | 2094 | event | raw | Unmapped task event marker |
| `unknown_27` | 536 | event | raw | Unmapped task event marker |
| `unknown_28` | 888 | event | raw | Unmapped task event marker |
| `unknown_29` | 1643 | event | raw | Unmapped task event marker |
| `unknown_3` | 2481 | event | raw | Unmapped task event marker |
| `unknown_30` | 1905 | event | raw | Unmapped task event marker |
| `unknown_31` | 1534 | event | raw | Unmapped task event marker |
| `unknown_32` | 3526 | event | raw | Unmapped task event marker |
| `unknown_33` | 5216 | event | raw | Unmapped task event marker |
| `unknown_34` | 4554 | event | raw | Unmapped task event marker |
| `unknown_35` | 8011 | event | raw | Unmapped task event marker |
| `unknown_36` | 12776 | event | raw | Unmapped task event marker |
| `unknown_37` | 13916 | event | raw | Unmapped task event marker |
| `unknown_38` | 9213 | event | raw | Unmapped task event marker |
| `unknown_39` | 9749 | event | raw | Unmapped task event marker |
| `unknown_4` | 2481 | event | raw | Unmapped task event marker |
| `unknown_40` | 12868 | event | raw | Unmapped task event marker |
| `unknown_41` | 7943 | event | raw | Unmapped task event marker |
| `unknown_42` | 2919 | event | raw | Unmapped task event marker |
| `unknown_43` | 1022 | event | raw | Unmapped task event marker |
| `unknown_44` | 279 | event | raw | Unmapped task event marker |
| `unknown_45` | 199 | event | raw | Unmapped task event marker |
| `unknown_46` | 89 | event | raw | Unmapped task event marker |
| `unknown_47` | 29 | event | raw | Unmapped task event marker |
| `unknown_48` | 7 | event | raw | Unmapped task event marker |
| `unknown_5` | 2482 | event | raw | Unmapped task event marker |
| `unknown_6` | 2484 | event | raw | Unmapped task event marker |
| `unknown_7` | 2484 | event | raw | Unmapped task event marker |
| `unknown_8` | 7245 | event | raw | Unmapped task event marker |
| `unknown_9` | 4049 | event | raw | Unmapped task event marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- The vast majority of event markers (44 of 48 event types) are unmapped/unknown task event codes, severely limiting event-based epoching for task conditions.
- Only four 5CCPT event codes (21, 22, 23, 25) are identified, with no PST event markers explicitly mapped.
- The `device` info field is completely missing from metadata, preventing equipment verification.
- Events.tsv files reportedly contain untranslated trigger codes (65535, 65289) rather than the actual task condition markers, indicating a BIDS conversion or recording issue.
- Small sample size (N=23) limits statistical power for subject-level classification tasks.
- Counterbalanced drug design across sessions means session number and drug condition are confounded at the group level but decoupled within subjects.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
