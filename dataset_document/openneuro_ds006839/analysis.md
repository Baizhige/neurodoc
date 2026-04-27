# EEG Recordings during Sham Neurofeedback in Virtual Reality

**Dataset**: `openneuro_ds006839` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006839
**Category**: Complex Applied | **Subjects**: 144 | **Files (Completed)**: 144 | **Channels**: 29 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed an attentional task within a virtual reality environment while receiving sham neurofeedback with positive, negative, or control feedback valences. The study investigates alpha-band modulation in response to perceived performance feedback without actual neurofeedback. Numeric trigger codes mark trial onsets and feedback conditions. The paradigm examines placebo effects of neurofeedback on neural oscillations and attention.

## File Scan Result

> **Kernel SHA256**: `f8e26ffa93b8443a102db4652c8b3bb0d0593318064cc5c344e4e6cb58e2a6aa`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `control feedback` | 1357 | event | raw | Control (neutral) feedback condition |
| `negative feedback` | 6438 | event | raw | Negative feedback condition marker |
| `null/reset event` | 60 | event | raw | Null/reset event |
| `positive feedback` | 8365 | event | raw | Positive feedback condition marker |
| `trial onset` | 538 | event | raw | Trial/block onset marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

(No tasks could be synthesized.)