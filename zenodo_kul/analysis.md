# KU Leuven Auditory Attention Decoding Dataset

**Dataset**: `zenodo_kul` | **Year**: 2020 | **URL**: https://zenodo.org/records/4004271
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 15 (Case B kernel) | **Channels**: 64 | **Sampling Rate**: 128 Hz

## Paradigm

Fifteen subjects performed a dichotic listening auditory attention decoding (AAD) task (Biesmans et al., 2017). Two competing story narratives were presented simultaneously, one to each ear, and subjects were instructed to attend to one. EEG was recorded from 64 channels (BioSemi ActiveTwo, standard 10-20 layout) at 128 Hz. Each MATLAB `.mat` file contains 20 trials (10 attended-left + 10 attended-right), stored as a Python list of trial dictionaries. The Case B kernel concatenates all 20 trials from each file into a single continuous raw signal and creates per-trial annotations indicating the attended ear.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://zenodo.org/records/4004271

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `attended_left` | 150 (10/subject x 15 subjects) | long | raw | Subject attends to the left-ear speaker |
| `attended_right` | 150 (10/subject x 15 subjects) | long | raw | Subject attends to the right-ear speaker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Case B kernel: 20 trials (each ~62.5 s at 128 Hz) concatenated into one continuous raw per file.

## Tasks

### Primary Task 1: Dichotic auditory attention decoding (left vs right ear)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Attended ear/speaker label in dichotic listening trials.
- **Evidence**: KUL AAD dataset is designed for supervised decoding of attended speech stream. Source: https://zenodo.org/records/4004271 DOI: https://doi.org/10.5281/zenodo.4004271


### Normal Task 1: Auditory Attention Decoding - Left vs. Right Ear (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, use trial duration from annotation, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Case B kernel uses `scipy.io.loadmat(simplify_cells=True)` and a custom `load()` method. Annotation durations match individual trial lengths. Balanced design: 10 trials per class per subject.

| Event | y | Meaning |
|-------|---|---------|
| `attended_left` | 0 | Attended ear: left |
| `attended_right` | 1 | Attended ear: right |
## Data Quality Notes

- Low sampling rate (128 Hz); limits high-frequency analysis but is standard for EEG-AAD.
- 15 subjects only; relatively small cohort for robust model evaluation.
- No age or sex information available in the public release.
- Each file contains 20 trials; the Case B kernel creates discontinuities at trial boundaries (artificial concatenation).

## References

- **Reference**: Biesmans W et al. (2017). Auditory-Inspired Speech Envelope Extraction Methods for Auditory Attention Detection in N-of-1 Trials. *IEEE Trans. Neural Syst. Rehabil. Eng.*, 25(5), 428-437. https://zenodo.org/records/4004271
