# Runabout: A Mobile EEG Study of Auditory Oddball Processing in Laboratory and Real-World Conditions

**Dataset**: `openneuro_ds003620` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003620
**Category**: Complex Applied | **Subjects**: 44 | **Files (Completed)**: 271 | **Channels**: 35 | **Sampling Rate**: 250 Hz | **Manual Review**: Pending

## Paradigm

Participants performed an auditory oddball task under three levels of environmental complexity and physical activity: sitting in a laboratory, walking on a sports field (oval), and navigating a university campus. The paradigm examined how cognitive and motor demands of real-world locomotion affect P300 oddball responses. Target tones required mental counting ("count" condition) or were simply listened to ("don't count" condition), with both counted and uncounted targets interleaved across environments.

## File Scan Result

> **Kernel SHA256**: `08529bad615403b5fdbf6115eb33b936ffbbcb1a62666710dad7b60569c62ea0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 898 | event | raw | Session/block marker |
| `Stimulus/S  1` | 88078 | event | raw | Primary stimulus marker (alternative alignment) |
| `empty` | 1 | admin | raw | Empty/padding event marker |
| `nan` | 1 | admin | raw | Invalid/missing event marker |
| `non_target` | 7208 | event | raw | Generic non-target marker |
| `ntCount_campus` | 63022 | event | raw | Non-target (standard) tone, Count condition, campus |
| `ntCount_lab` | 63040 | event | raw | Non-target (standard) tone, Count condition, laboratory |
| `ntCount_oval` | 62936 | event | raw | Non-target (standard) tone, Count condition, oval |
| `ntDontcount_campus` | 170190 | event | raw | Non-target (standard) tone, don't-count condition, campus |
| `ntDontcount_lab` | 166362 | event | raw | Non-target (standard) tone, don't-count condition, laboratory |
| `ntDontcount_oval` | 171116 | event | raw | Non-target (standard) tone, don't-count condition, oval |
| `ntcount_campus` | 107632 | event | raw | Non-target (standard) tone, count condition, campus |
| `ntcount_lab` | 107932 | event | raw | Non-target (standard) tone, count condition, laboratory |
| `ntcount_oval` | 108426 | event | raw | Non-target (standard) tone, count condition, oval |
| `t_Count_campus` | 15734 | event | raw | Target tone, Count condition (counterbalanced), campus |
| `t_Count_lab` | 15702 | event | raw | Target tone, Count condition (counterbalanced), laboratory |
| `t_Count_oval` | 15814 | event | raw | Target tone, Count condition (counterbalanced), oval |
| `t_Dontcount_campus` | 42874 | event | raw | Target tone, don't-count condition, campus |
| `t_Dontcount_lab` | 41374 | event | raw | Target tone, don't-count condition, laboratory |
| `t_Dontcount_oval` | 42622 | event | raw | Target tone, don't-count condition, oval |
| `t_count_campus` | 27368 | event | raw | Target tone, count condition, campus (outdoor navigation) |
| `t_count_lab` | 27086 | event | raw | Target tone, count condition, laboratory |
| `t_count_oval` | 26546 | event | raw | Target tone, count condition, oval (sports field walking) |
| `target` | 1800 | event | raw | Generic target marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Auditory Oddball Target vs Non-Target Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus`, `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus` | 1 | Target/deviant tone |
  | `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus` | 0 | Non-target/standard tone |
- **Evidence**:
  - DOI: 10.1038/s41598-021-01772-8 — Published Runabout study analyzing P3 and MMN components from auditory oddball paradigm across lab, oval, and campus environments with 44 participants. Epoched -200ms to 800ms relative to event markers. Direct classification: target (deviant) vs non-target (standard) tones.
  - DOI: 10.1101/2021.05.27.445993 — Preprint of the same study with identical methodology, confirming event-based epoching and oddball classification approach.
- **Kernel Notes**: Event naming encodes environment (_lab/_oval/_campus) and instruction (count/Count/Dontcount). Use `Stimulus/S  1` for primary epoch alignment when needed; detailed labels are in specific event IDs. Mobile EEG introduces motion artifacts during oval/campus walking conditions—apply robust ICA or ASR for artifact removal. Expect reduced P300 amplitude and increased variance in walking vs lab conditions.

---

### Classical Task 2: Cross-Environment Oddball Classification (Lab vs Oval vs Campus)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus`, `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `t_count_lab`, `t_Count_lab`, `t_Dontcount_lab`, `ntcount_lab`, `ntCount_lab`, `ntDontcount_lab` | 0 | Laboratory (sitting) |
  | `t_count_oval`, `t_Count_oval`, `t_Dontcount_oval`, `ntcount_oval`, `ntCount_oval`, `ntDontcount_oval` | 1 | Oval (walking on sports field) |
  | `t_count_campus`, `t_Count_campus`, `t_Dontcount_campus`, `ntcount_campus`, `ntCount_campus`, `ntDontcount_campus` | 2 | Campus (walking on university campus) |
- **Evidence**:
  - DOI: 10.1038/s41598-021-01772-8 — Analyzes how environmental context modulates P300 amplitude across laboratory sitting, oval walking, and campus navigation. Environment-specific oddball trials enable cross-condition classification to assess cognitive load effects of real-world locomotion.
  - DOI: 10.1101/2021.05.27.445993 — Confirms environment as the primary experimental manipulation for studying mobile EEG artifacts and attentional processing during walking.
- **Kernel Notes**: Environment encoded in event suffix (_lab/_oval/_campus). Pool target and non-target within each environment for 3-class environment classification. Expected: lower classification accuracy for oval/campus due to motion artifacts and cognitive-motor dual-task interference. Consider environment-specific artifact rejection thresholds.

---

### Potential Task 1: Counting Instruction Effect on Oddball Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus`, `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus` | 1 | Count instruction (active engagement) |
  | `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus` | 0 | Don't-count instruction (passive listening) |
- **Evidence**:
  - DOI: 10.1038/s41598-021-01772-8 — Uses count accuracy as a behavioral performance metric, indicating active engagement modulates P300 amplitude during oddball processing.
  - DOI: 10.1101/2021.05.27.445993 — Mentions count/ignore instructions as a key experimental manipulation affecting attentional processing during walking.
- **Kernel Notes**: The case sensitivity (t_count vs t_Count) may indicate counterbalancing across participants; pool both as 'count' condition. Compare target P300 amplitude between count vs don't-count conditions within-subject. May show enhanced P300 for count conditions due to increased attentional engagement.

---

### Potential Task 1: Motion Artifact Classification / Quality Assessment
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`t_count_lab`, `t_count_oval`, `t_count_campus`, `t_Count_lab`, `t_Count_oval`, `t_Count_campus`, `t_Dontcount_lab`, `t_Dontcount_oval`, `t_Dontcount_campus`, `ntcount_lab`, `ntcount_oval`, `ntcount_campus`, `ntCount_lab`, `ntCount_oval`, `ntCount_campus`, `ntDontcount_lab`, `ntDontcount_oval`, `ntDontcount_campus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `t_count_lab`, `t_Count_lab`, `t_Dontcount_lab`, `ntcount_lab`, `ntCount_lab`, `ntDontcount_lab` | 0 | Lab (low motion artifact) |
  | `t_count_oval`, `t_Count_oval`, `t_Dontcount_oval`, `ntcount_oval`, `ntCount_oval`, `ntDontcount_oval`, `t_count_campus`, `t_Count_campus`, `t_Dontcount_campus`, `ntcount_campus`, `ntCount_campus`, `ntDontcount_campus` | 1 | Walking conditions (high motion artifact) |
- **Evidence**:
  - DOI: 10.1038/s41598-021-01772-8 — Implicit in the study design: examines how walking introduces artifacts and reduces P300 amplitude compared to lab sitting.
- **Kernel Notes**: Motion artifact classification may help identify clean vs artifact-contaminated epochs for downstream analysis. Consider using temporal features (variance, peak-to-peak amplitude) or frequency features (muscle artifact patterns ~20-50Hz) as additional features. This task supports quality control for the cross-environment analysis.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
