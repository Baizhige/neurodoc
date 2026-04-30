# A high-quality EEG dataset for studying visual touch perception

**Dataset**: `openneuro_ds005662` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005662
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 65 | **Sampling Rate**: 2048 Hz | **Manual Review**: Pending

## Paradigm

Participants viewed rapid streams of videos depicting touch to a hand or an object to investigate visual touch perception. The experiment used target and non-target trials to measure brain responses to observed touch. EEG recordings were captured continuously at 2048 Hz, with discrete event markers (event_40708 and event_40704) indicating stimulus onsets for epoch segmentation.

## File Scan Result

> **Kernel SHA256**: `ae6939484ae682db3726c4e319b9322ca64e4283bd38ac5c8be8b4302f28db0e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_106240` | 1 | event | raw | Unclassified event marker |
| `event_106244` | 1 | event | raw | Unclassified event marker |
| `event_260` | 1 | event | raw | Unclassified event marker |
| `event_27652` | 2 | event | raw | Unclassified event marker |
| `event_32516` | 118 | event | raw | Rare stimulus or response event |
| `event_32772` | 1 | event | raw | Unclassified event marker |
| `event_36100` | 1 | event | raw | Unclassified event marker |
| `event_40704` | 9130 | event | raw | Secondary stimulus onset (lower-frequency marker) |
| `event_40708` | 235546 | event | raw | Primary stimulus onset (high-frequency marker) |
| `event_512` | 3 | event | raw | Unclassified event marker |
| `event_516` | 36 | event | raw | Unclassified event marker |
| `event_57092` | 4 | event | raw | Unclassified event marker |
| `event_65280` | 1 | event | raw | Unclassified event marker |
| `event_65284` | 67 | event | raw | Unclassified event marker |
| `event_66052` | 3 | event | raw | Unclassified event marker |
| `event_98052` | 5 | event | raw | Unclassified event marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
