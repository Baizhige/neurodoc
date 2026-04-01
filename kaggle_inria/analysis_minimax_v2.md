# Kaggle BCI Challenge (INRIA) Dataset

**Dataset**: `kaggle_inria` | **Year**: 2015 | **URL**: https://www.kaggle.com/c/inria-bci-challenge
**Category**: Action/Output | **Subjects**: 26 | **Files (Completed)**: 130 | **Channels**: 56 | **Sampling Rate**: 200 Hz

## Paradigm

Twenty-six subjects (ages 20-37) performed a P300-based BCI feedback task using a 56-channel Ag/AgCl EEG cap at 200 Hz (plus 1 EOG channel and 1 FeedBackEvent channel, total 58). The task was a P300 matrix speller in which subjects attended to a target character while row/column flashes elicited P300 responses. Feedback was provided after each trial: subjects received either a correct ("good") or incorrect ("wrong") response to the P300 classifier output. Each session file (CSV format) contains one session for one subject; each subject has 5 sessions. Feedback event times are encoded in the dedicated `FeedBackEvent` channel; labels ("good" or "wrong") are sourced from a companion `TrainLabels.csv` file. Test sessions have unknown labels.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://www.kaggle.com/c/inria-bci-challenge

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `good feedback to P300` | varies (~1300) | short | raw | Feedback event: BCI output was correct |
| `wrong feedback to P300` | varies (~650) | short | raw | Feedback event: BCI output was incorrect |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Feedback events are 1 s in duration (as set in kernel annotations). Test sessions (Sess01-Sess04 for most subjects) have `unknown` labels; labeled sessions are typically Sess05. Approximately 60 feedback events per session.

## Tasks

### Primary Task 1: Feedback Error Detection (Good vs Wrong)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1.3 s, target_events = [`good feedback to P300`, `wrong feedback to P300`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 0 | 0 | Correct BCI feedback (classifier output matched user intent) |
  | 1 | 1 | Incorrect BCI feedback (classifier output differed from user intent) |
- **Evidence**:
  - DOI: 10.1109/TBCAS.2022.3215962 — Validates EEGNet accelerator on ERN dataset with epochs [0, 1.3]s post feedback for binary classification of correct vs. incorrect BCI feedback.
  - DOI: 10.1016/j.inffus.2024.102316 — Uses ERN dataset from Kaggle BCI Challenge for adversarial filtering evaluation with epochs [0, 1.3]s post feedback onset.
  - DOI: 10.1109/ACCESS.2024.3467154 — Evaluates DCAE defense on ERN dataset with tmin=0s, tmax=1.3s, bandpass [1,40]Hz.
- **Kernel Notes**: FeedBackEvent channel (column 57) encodes feedback onset times; match labels from TrainLabels.csv by feedback ID (e.g., S01_Sess01_FB001). Exclude sessions with `unknown feedback to P300` (test set). Bandpass filter 1-40Hz recommended per paper preprocessing. (replaces Normal Task 1 from original analysis.md)


## Data Quality Notes

- Data stored as CSV files (not standard EEG format); MNE loader produces unsupported-file-type warnings that are non-fatal.
- 58 channels include 56 EEG + 1 EOG + 1 FeedBackEvent auxiliary channel; remove FeedBackEvent and EOG before training.
- Many sessions have only unknown labels (test set); only sessions with known labels in TrainLabels.csv can be used for supervised learning.
- Age range 20-37 available from dataset metadata; no sex information.

## References

- **Reference**: Inria BCI Challenge. Kaggle Competition 2015. https://www.kaggle.com/c/inria-bci-challenge
- **Reference**: Margaux P, Maby E, Daligault S, Bertrand O, Mattout J. (2012). Objective and Subjective Evaluation of Online Error Correction during P300-Based Spelling. *Advances in Human-Computer Interaction*. DOI: https://doi.org/10.1155/2012/578295

## Review
| **Sampling Rate**: 200.0 Hz | **Manual Review**: Mingze Tang |
