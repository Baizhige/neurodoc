# Social Observation EEG Raw Data

**Dataset**: `openneuro_ds006554` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006554
**Category**: Complex Applied | **Subjects**: 47 | **Files (Completed)**: 47 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

EEG was recorded while participants engaged in social observation tasks, likely involving ecological social stimuli such as videos or images of human social interactions. The rich numeric trigger coding (30 distinct codes) suggests a multi-factorial design with combinations of social condition, stimulus type, or response category. The paradigm examines neural correlates of social perception and mentalizing.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `60` | 47 | event | raw | Social stimulus condition 60 |
| `61` | 47 | event | raw | Social stimulus condition 61 |
| `30` | 47 | event | raw | Social stimulus condition 30 |
| `31` | 47 | event | raw | Social stimulus condition 31 |
| `62` | 47 | event | raw | Social stimulus condition 62 |
| `63` | 47 | event | raw | Social stimulus condition 63 |
| `32` | 47 | event | raw | Social stimulus condition 32 |
| `33` | 47 | event | raw | Social stimulus condition 33 |
| `21` | 47 | event | raw | Social stimulus condition 21 |
| `25` | 47 | event | raw | Social stimulus condition 25 |
| `16` | 47 | event | raw | Social stimulus condition 16 |
| `13` | 47 | event | raw | Social stimulus condition 13 |
| `12` | 47 | event | raw | Social stimulus condition 12 |
| `24` | 47 | event | raw | Social stimulus condition 24 |
| `87` | 47 | event | raw | Social stimulus condition 87 |
| `68` | 47 | event | raw | Social stimulus condition 68 |
| `11` | 47 | event | raw | Social stimulus condition 11 |
| `26` | 47 | event | raw | Social stimulus condition 26 |
| `14` | 47 | event | raw | Social stimulus condition 14 |
| `15` | 47 | event | raw | Social stimulus condition 15 |
| `22` | 47 | event | raw | Social stimulus condition 22 |
| `23` | 47 | event | raw | Social stimulus condition 23 |
| `42` | 47 | event | raw | Social stimulus condition 42 |
| `67` | 47 | event | raw | Social stimulus condition 67 |
| `88` | 47 | event | raw | Social stimulus condition 88 |
| `43` | 47 | event | raw | Social stimulus condition 43 |
| `36` | 47 | event | raw | Social stimulus condition 36 |
| `35` | 47 | event | raw | Social stimulus condition 35 |
| `48` | 47 | event | raw | Social stimulus condition 48 |
| `37` | 47 | event | raw | Social stimulus condition 37 |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Social Condition Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric trigger codes require decoding from events.tsv. All 30 event types appear in all 47 files (perfectly balanced). Group codes by tens-digit (10s, 20s, 30s, 60s, 80s) as likely condition groupings.

 | Event | y | Meaning |
 |-------|---|-|
 | `60` | 0 | Social condition 60 |
 | `61` | 1 | Social condition 61 |
 | `30` | 2 | Social condition 30 |
 | `31` | 3 | Social condition 31 |
 | `62` | 4 | Social condition 62 |
 | `63` | 5 | Social condition 63 |
 | `32` | 6 | Social condition 32 |
 | `33` | 7 | Social condition 33 |
 | `21` | 8 | Social condition 21 |
 | `25` | 9 | Social condition 25 |
 | `16` | 10 | Social condition 16 |
 | `13` | 11 | Social condition 13 |
 | `12` | 12 | Social condition 12 |
 | `24` | 13 | Social condition 24 |
 | `87` | 14 | Social condition 87 |
 | `68` | 15 | Social condition 68 |
 | `11` | 16 | Social condition 11 |
 | `26` | 17 | Social condition 26 |
 | `14` | 18 | Social condition 14 |
 | `15` | 19 | Social condition 15 |
 | `22` | 20 | Social condition 22 |
 | `23` | 21 | Social condition 23 |
 | `42` | 22 | Social condition 42 |
 | `67` | 23 | Social condition 67 |
 | `88` | 24 | Social condition 88 |
 | `43` | 25 | Social condition 43 |
 | `36` | 26 | Social condition 36 |
 | `35` | 27 | Social condition 35 |
 | `48` | 28 | Social condition 48 |
 | `37` | 29 | Social condition 37 |

## Data Quality Notes

- Numeric trigger codes need decoding from events.tsv or README.
- Large number of distinct event types (30); group codes before classification.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review