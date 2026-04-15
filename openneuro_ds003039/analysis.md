# Free Walking Study

**Dataset**: `openneuro_ds003039` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003039
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 67 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants walked two different outdoor routes while performing a self-paced button-pressing task, with gait events (heel strikes, toe-offs, steps) recorded alongside button-press responses. This is a mobile EEG study capturing brain activity during naturalistic free-walking gait. The experimental design includes multiple conditions: standing still, walking initiation, easy/difficult button-pressing tasks, and 10-fast/10-own pacing conditions.

## File Scan Result

> **Kernel SHA256**: `cd20c72721b598aab62e0aa414bd3357bf3f38c5a7883c58865976101da78f48`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LeftButtonPress` | 5263 | event | raw | Left-hand button press during task |
| `LeftHS` | 16018 | event | raw | Left heel strike (gait event) |
| `LeftStep` | 4832 | event | raw | Left foot step |
| `LeftTO` | 15632 | event | raw | Left toe-off (gait event) |
| `MissLeftButtonPress` | 502 | event | raw | Missed left button press |
| `MissRightButtonPress` | 840 | event | raw | Missed right button press |
| `Play` | 2049 | event | raw | Audio playback/cue event |
| `RightButtonPress` | 5459 | event | raw | Right-hand button press during task |
| `RightHS` | 16217 | event | raw | Right heel strike (gait event) |
| `RightStep` | 4716 | event | raw | Right foot step |
| `RightTO` | 16186 | event | raw | Right toe-off (gait event) |
| `boundary` | 2 | admin | raw | Data file boundary marker |
| `difficult` | 19 | event | raw | Difficult walking condition marker |
| `easy` | 19 | event | raw | Easy walking condition marker |
| `end_10fast` | 19 | event | raw | End of 10-fast pacing condition |
| `end_10own` | 23 | event | raw | End of 10-own pacing condition |
| `end_difficult` | 19 | event | raw | End of difficult button task |
| `end_difficult_button` | 19 | event | raw | End of difficult button condition |
| `end_easy` | 19 | event | raw | End of easy button task |
| `end_easy_button` | 19 | event | raw | End of easy button condition |
| `end_experiment` | 11 | event | raw | End of experiment |
| `end_initiation` | 19 | event | raw | End of walking initiation phase |
| `end_restEEG` | 19 | event | raw | End of resting EEG recording |
| `end_standing` | 19 | event | raw | End of standing still period |
| `initiation` | 1881 | event | raw | Walking initiation phase |
| `initiationHeadLeft` | 825 | event | raw | Head turned left during initiation |
| `initiationHeadRight` | 1030 | event | raw | Head turned right during initiation |
| `initiationLeft` | 825 | event | raw | Left-side initiation movement |
| `initiationRight` | 1031 | event | raw | Right-side initiation movement |
| `instruct_10fast` | 19 | event | raw | Instruction for 10-fast pacing condition |
| `instruct_10own` | 23 | event | raw | Instruction for 10-own pacing condition |
| `instruct_difficult` | 19 | event | raw | Instruction for difficult button task |
| `instruct_difficult_button` | 19 | event | raw | Instruction for difficult button condition |
| `instruct_easy` | 19 | event | raw | Instruction for easy button task |
| `instruct_easy_button` | 19 | event | raw | Instruction for easy button condition |
| `instruct_restEEG` | 19 | event | raw | Instruction for resting EEG |
| `instruct_standing` | 19 | event | raw | Instruction for standing still |
| `standingStill` | 1856 | event | raw | Standing still period |
| `start_10fast` | 19 | event | raw | Start of 10-fast pacing condition |
| `start_10own` | 23 | event | raw | Start of 10-own pacing condition |
| `start_difficult` | 19 | event | raw | Start of difficult button task |
| `start_difficult_button` | 19 | event | raw | Start of difficult button condition |
| `start_easy` | 19 | event | raw | Start of easy button task |
| `start_easy_button` | 19 | event | raw | Start of easy button condition |
| `start_experiment` | 19 | event | raw | Start of experiment |
| `start_initiation` | 19 | event | raw | Start of walking initiation phase |
| `start_pause` | 38 | event | raw | Start of pause period |
| `start_restEEG` | 19 | event | raw | Start of resting EEG recording |
| `start_standing` | 19 | event | raw | Start of standing still period |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels (likely head/position direction)
- **Candidate Labels**: `x_dir`, `y_dir`, `z_dir`
- **Kernel Note**: Verify channel roles and units. These likely represent directional/head orientation channels from the mobile EEG system.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | Not available in dataset metadata |
| `subject_sex` | complete | Not available in dataset metadata |
| `device` | missing | Not available in dataset metadata |

## Tasks

(No tasks could be synthesized.)