# Music Listening Genre EEG Dataset (MUSIN-G)

**Dataset**: `openneuro_ds003774` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003774
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 260
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Twenty participants listened to 12 music tracks spanning various genres (classical, jazz, rock, etc.) with eyes closed while high-density EEG was recorded. After each track, participants provided subjective ratings for familiarity and enjoyment. The dataset supports EEG-based music genre classification and exploration of neural correlates of music preference and familiarity. No discrete event markers were embedded in the EEG recording.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003774

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous music listening EEG |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Music Genre Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = full song duration (per annotation), overlap = 0.0, target_events = [`stm (song)`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Deep House | 1 | Genre 1 |
  | Indie | 2 | Genre 2 |
  | Electronics | 3 | Genre 3 |
  | New Age | 4 | Genre 4 |
  | Electronic Dance | 5 | Genre 5 |
  | Ambient | 6 | Genre 6 |
  | Hindustani Classical | 7 | Genre 7 |
  | Indian Semi-Classical | 8 | Genre 8 |
  | Indian Folk | 9 | Genre 9 |
  | Soft Jazz | 10 | Genre 10 |
  | Goth Rock | 11 | Genre 11 |
  | Progressive Instrumental Rock | 12 | Genre 12 |
- **Super Meta Notes**: Genre labels are derived from song metadata (file-level). Each song belongs to one of 12 genres. Epochs correspond to the entire song listening period (from 'stm' marker to 'fxnd' marker). Labels are assigned per epoch based on the associated music track's genre.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — This Data in Brief paper describes and releases the MUSIN-G EEG dataset (OpenNeuro ds003774) containing 20 participants' EEG responses to 12 songs of different genres with post-hoc behavioral ratings for familiarity and enjoyment, collected during naturalistic music listening with eyes closed.
- **Kernel Notes**: Extract epoch windows spanning entire song duration using 'stm' (song start) and 'fxnd' (song end) markers from events.tsv. Map each epoch to its genre label using the file-level genre metadata. For baseline recordings (2-min silence), label separately or exclude from genre classification task.

### Primary Task 2: Song Identification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = full song duration (per annotation), overlap = 0.0, target_events = [`stm (song)`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Song 1 (Deep House) | 1 | First song in playlist |
  | Song 2 (Indie) | 2 | Second song in playlist |
  | ... | ... | ... |
  | Song 12 (Progressive Instrumental Rock) | 12 | Twelfth song in playlist |
- **Super Meta Notes**: Each of the 12 songs is uniquely identifiable. Song identity provides finer-grained classification than genre (e.g., two songs within same genre are distinct). Labels derived from file naming convention (ses-01 to ses-12).
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — This Data in Brief paper describes and releases the MUSIN-G EEG dataset (OpenNeuro ds003774) containing 20 participants' EEG responses to 12 songs of different genres with post-hoc behavioral ratings for familiarity and enjoyment, collected during naturalistic music listening with eyes closed.
- **Kernel Notes**: Similar epoching as genre task but label each epoch by specific song ID rather than genre category. Use session numbering (ses-01 to ses-12) as song identifiers.

### Primary Task 3: Familiarity Rating Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 2.0 s *, target_events = [`fam (familiarity rating)`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | fam (familiarity rating) | 1–5 | Rating: 1=extremely familiar to 5=extremely unfamiliar |
- **Super Meta Notes**: Familiarity ratings were collected via keypress (1-5 scale) after each song listening. The 'fam' marker indicates when the rating was made. The target variable is continuous (1–5) for regression.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — This Data in Brief paper describes and releases the MUSIN-G EEG dataset (OpenNeuro ds003774) containing 20 participants' EEG responses to 12 songs of different genres with post-hoc behavioral ratings for familiarity and enjoyment, collected during naturalistic music listening with eyes closed.
- **Kernel Notes**: Epoch around the 'fam' rating marker. The EEG segment could represent the rating decision process (parameters marked with * are inferred; paper mentions ratings were collected after each song but exact epoch timing not specified).

### Primary Task 4: Enjoyment Rating Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 2.0 s *, target_events = [`enj (enjoyment rating)`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | enj (enjoyment rating) | 1–5 | Rating: 1=extremely enjoyable to 5=extremely unenjoyable |
- **Super Meta Notes**: Enjoyment ratings were collected via keypress (1-5 scale) after each song listening. The 'enj' marker indicates when the rating was made. The target variable is continuous (1–5) for regression.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — This Data in Brief paper describes and releases the MUSIN-G EEG dataset (OpenNeuro ds003774) containing 20 participants' EEG responses to 12 songs of different genres with post-hoc behavioral ratings for familiarity and enjoyment, collected during naturalistic music listening with eyes closed.
- **Kernel Notes**: Epoch around the 'enj' rating marker. The EEG segment could represent the rating decision process (parameters marked with * are inferred; paper mentions ratings were collected after each song but exact epoch timing not specified).

### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (music genre tags need to be appended after parsing from events.tsv))
- **Notes**: 260 files for 20 subjects (13 files each: 12 tracks + 1 baseline). Music genre labels are file-level metadata; apply as segment-level labels for genre classification. High-density 129-channel EEG at 1000 Hz.

## Data Quality Notes

- No EEG trigger events present; music onset timing not embedded in EEG.
- 260 files likely correspond to individual music track recordings; genre label per file.
- High-density 129-channel EEG; high computational requirements.
- Eyes-closed listening; fewer motion artifacts but possible drowsiness.

## References

- **Reference**: `Music Listening Genre EEG dataset (MUSIN-G). OpenNeuro ds003774.`
