# EEG responses to continuous naturalistic speech

**Dataset**: `openneuro_ds004408` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004408
**Category**: High-level Mental | **Subjects**: 380 | **Files (Completed)**: 380 | **Channels**: 128 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants listened to continuous segments of an audiobook version of 'The Old Man and the Sea' to record EEG responses to naturalistic narrative speech and language processing. The study investigates low-frequency cortical entrainment to speech and phoneme-level processing. No trial-level event markers are present; recordings are continuous.

## File Scan Result

> **Kernel SHA256**: `50a41743c28f917948e41ca0e067366ac93bf255dea4c0ef3c13545d639ae1d5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `continuous_speech_listening` | 380 | event | raw | Continuous EEG recording during audiobook listening (The Old Man and the Sea) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Speech Envelope and Phoneme-Level Neural Entrainment

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `misc` (external stimulus metadata)
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `continuous_speech_listening` | Speech envelope (RMS amplitude) | Low-frequency cortical entrainment to speech envelope |
| `continuous_speech_listening` | Phoneme onsets/features | Phoneme-level processing markers |

- **Notes**: The speech envelope and phoneme labels must be extracted from external stimulus audio files. Use Hilbert envelope or gammatone filterbank for envelope extraction. Phoneme timing can be derived via forced alignment (e.g., Montreal Forced Aligner) or pre-existing annotations.

- **Evidence** (DOI): 
  - 10.1016/j.cub.2015.08.030 (Low-Frequency Cortical Entrainment to Speech Reflects Phoneme-Level Processing; Lalor/Di Liberto group—same research group as this dataset)
  - 10.1523/JNEUROSCI.1828-18.2019 (Neural Speech Tracking in Theta/Delta Bands)
  - 10.3389/fnhum.2016.00604 (mTRF Toolbox)

- **Kernel Notes**: This is the primary research question of openneuro_ds004408. The 380 continuous recordings enable robust mTRF encoding models. Segment into 2-second windows for stable temporal response function estimation. Align EEG segments with extracted speech envelope to quantify cortical tracking of speech dynamics.

### Classical Task 2: Linguistic Feature Hierarchy Encoding

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `misc` (external linguistic annotations)
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `continuous_speech_listening` | Phonotactic probability | Sequential phonological constraints |
| `continuous_speech_listening` | Word surprisal | Information-theoretic predictability |
| `continuous_speech_listening` | Semantic features | Meaning-based representations |

- **Notes**: Requires external text annotations aligned to stimulus audio. Use pre-trained language models to compute word-level surprisal and entropy. Phonotactic features can be derived from probabilistic phonotactic databases.

- **Evidence** (DOI): 
  - 10.1016/j.neuroimage.2020.117586 (Neural Representation of Linguistic Feature Hierarchy; same research group methodology)
  - 10.1038/s41598-024-69602-1 (Neural Encoding of Linguistic Speech Cues; older adults, audiobook paradigm)
  - 10.1162/nol_a_00100 (Cortical Tracking Under Bimodal Divided Attention)

- **Kernel Notes**: Multi-feature mTRF models can dissociate contributions of acoustic, phonemic, and semantic processing stages. The 380-subject dataset provides exceptional statistical power for detecting subtle linguistic encoding effects.

### Classical Task 3: Acoustic Feature Encoding (Spectrogram TRF)

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `misc` (external acoustic features)
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `continuous_speech_listening` | Spectrogram (gammatone filterbank) | Time-frequency acoustic representation |
| `continuous_speech_listening` | Envelope modulation spectrum | Amplitude modulation in delta-theta range |

- **Notes**: Extract multi-channel gammatone filterbank features (4th order, 128 channels spanning 100–8000 Hz) from stimulus audio. Compute envelope via Hilbert transform or root-mean-square in 20 ms windows.

- **Evidence** (DOI): 
  - 10.1162/jocn_a_02059 (Neural Speech Tracking with Visual Speech; spectrogram mTRF)
  - 10.3390/brainsci12101320 (Cortical Tracking of Target Speech; TRF for speech envelope)
  - 10.1101/2024.04.01.587607 (Level Dependent Subcortical EEG Responses; intensity analysis)

- **Kernel Notes**: Baseline acoustic feature models establish the stimulus-response relationship before adding higher-order linguistic predictors. Essential for separating acoustic from linguistic encoding contributions.

### Potential Task 4: Deep Neural Network Speech Decoding

- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `misc` (stimulus-derived labels)
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `continuous_speech_listening` | 1 (matched) / 0 (mismatched) | Match-mismatch speech decoding |

- **Notes**: Requires creating matched/mismatched stimulus pairs or using pre-existing match-mismatch paradigms. Train neural networks (CNN, LSTM, or transformer-based) to decode speech features from EEG. This task is methodology-transfer from ICASSP Challenge datasets.

- **Evidence** (DOI): 
  - 10.1109/OJSP.2024.3378593 (Deep Neural Networks for Envelope and FFR Decoding)

- **Kernel Notes**: Deep learning approaches may capture non-linear stimulus-response relationships missed by linear mTRF models. Transfer learning from pre-trained audio encoders (e.g., wav2vec, HuBERT) to EEG domain is a promising direction.

### Potential Task 5: Cognitive Load and Attention Modulation

- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s (long segments)
- **Label Route**: `misc` (stimulus-derived)
- **Meta Level**: `raw`
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `continuous_speech_listening` | Narrative segment difficulty | Comprehension difficulty index |
| `continuous_speech_listening` | Attention lapses | Pre-processed attention estimates |

- **Notes**: Requires external annotations of narrative complexity or pre-computed attention metrics. Long-segment analysis captures sustained attention and fatigue effects not visible in short windows.

- **Evidence** (DOI): 
  - 10.1162/nol_a_00100 (Cortical Tracking Under Bimodal Divided Attention)
  - 10.1016/j.neuroimage.2018.01.033 (CCA for Stimulus-Response Mapping)

- **Kernel Notes**: While the current dataset has no explicit attention task, naturalistic listening includes implicit attention variation. This task is plausible but requires careful validation against ground truth attention measures.