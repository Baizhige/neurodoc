# CockPart Multi-Paradigm EEG Dataset

**Dataset**: `unknown_CockPartDataset` | **Year**: N/A | **URL**: N/A
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 1590 | **Channels**: 128 | **Sampling Rate**: 128 Hz (N400/Natural Speech) / 512 Hz (Speech in Noise) | **Manual Review**:

## Paradigm

A multi-paradigm EEG corpus comprising four experimental subdatasets, all recorded from a 128-channel EEG cap. The four paradigms are:

1. **N400**: Subjects read or heard sentence contexts ending in high-cloze (predictable) or low-cloze (unpredictable) words; pre-epoched EEG trials at 128 Hz stored as `eegData_hiCloze` and `eegData_loCloze` arrays (128 channels x 103 timepoints x 150 trials) for 9 subjects.

2. **Natural Speech**: Subjects listened to natural continuous speech; raw continuous EEG stored at 128 Hz for 19 subjects (multiple runs per subject, up to ~420 run files total).

3. **Natural Speech - Reverse**: Subjects listened to time-reversed (unnatural) speech as a control condition; raw continuous EEG at 128 Hz for 10 subjects (200 run files).

4. **Speech in Noise (SiN)**: Subjects listened to speech presented with background noise in audio-only (`_a_`) and video-only (`_v_`) modality conditions; raw continuous EEG at 512 Hz for 21 subjects (315 audio + 315 video files = 630 total SiN files).

The Case B kernel dispatches loading to the appropriate paradigm-specific method based on the file path.

## File Scan Result

> **Kernel SHA256**: `b0fb53a13b65ddd627a459885811c0110078172e3fe0af22802920a04880cb10`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `N400_hiCloze` | 150/subject x 9 = 1350 | long | raw | N400 paradigm: high-cloze (predictable) word epoch |
| `N400_loCloze` | 150/subject x 9 = 1350 | long | raw | N400 paradigm: low-cloze (unpredictable) word epoch |
| `NaturalSpeech` | 1/file x ~420 | long | raw | Natural speech paradigm: whole-run annotation |
| `NaturalSpeechReverse` | 1/file x ~200 | long | raw | Reversed speech paradigm: whole-run annotation |
| `SiN_audio` | 1/file x 315 | long | raw | Speech-in-Noise audio-only condition |
| `SiN_video` | 1/file x 315 | long | raw | Speech-in-Noise video-only condition |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Case B kernel: N400 epoch arrays are concatenated into a single continuous raw signal; each epoch onset is annotated individually. Natural Speech and SiN paradigms provide single whole-recording annotations per file.

### Info

Dataset origin and publication unknown. Multi-paradigm EEG corpus (CockPart Dataset). No associated publication identified.

## Tasks

### Potential Task 1: N400 Language ERP - High-Cloze vs. Low-Cloze (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.8 s (= 103/128 Hz; matches pre-epoched trial length), target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Filter to N400 paradigm files (`N400/EEG/Subject{N}.mat`). Case B kernel concatenates hiCloze (150) then loCloze (150) epochs; epoch window (0.8 s) matches the original pre-epoched length. sfreq = 128 Hz.

| Event | y | Meaning |
|-------| --- | --- |
| `N400_hiCloze` | 0 | High-cloze (predictable) word - N400 attenuated |
| `N400_loCloze` | 1 | Low-cloze (unpredictable) word - N400 enhanced |

---

### Potential Task 2: Natural Speech Auditory Processing - Speech vs. Reversed Speech (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, overlap = 0.0 s, use full recording duration from annotation, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Filter to Natural Speech and Natural Speech - Reverse paradigm files. sfreq = 128 Hz. Multiple runs per subject; run files are independent.

| Event | y | Meaning |
|-------| --- | --- |
| `NaturalSpeech` | 0 | Listening to natural (forward) speech |
| `NaturalSpeechReverse` | 1 | Listening to reversed (backward) speech |

---

### Potential Task 3: Speech-in-Noise Modality - Audio vs. Video (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, overlap = 0.0 s, use full recording duration from annotation, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Filter to Speech in Noise paradigm files. sfreq = 512 Hz. Condition (audio/video) inferred from filename suffix (`_a_` or `_v_`).

| Event | y | Meaning |
|-------| --- | --- |
| `SiN_audio` | 0 | Speech-in-Noise audio-only condition |
| `SiN_video` | 1 | Speech-in-Noise video-only condition |

---

### Potential Task 4: N400 cloze-condition decoding (high vs low cloze)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: `N400_hiCloze` vs `N400_loCloze` trial labels from the N400 subset.
- **Evidence**: Primary task inferred from internal dataset documentation only; external publication/reference is not yet available.
- **Notes**: Demoted from Primary Task because no external DOI/URL source is available.

## Data Quality Notes

- Case B kernel: `.mat` files contain pre-epoched arrays or raw continuous EEG depending on the paradigm; paradigm is inferred from the directory structure in the file path.
- Channel names in reconstructed raw are generic (`EEG001`-`EEG128`); no electrode layout metadata is provided.
- Variable sampling rates across paradigms: N400 and Natural Speech = 128 Hz; Speech in Noise = 512 Hz. Do not mix paradigms without resampling.
- Dataset origin and publication unknown; provenance requires verification before publication.
- No age or sex information available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
