# EEG: Three-Stimulus Auditory Oddball and Rest in Acute and Chronic TBI

**Dataset**: `openneuro_ds003522` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003522
**Category**: Sensory/Response | **Subjects**: 62 | **Files (Completed)**: 196
**Channels**: 65 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

This study investigates EEG markers in mild traumatic brain injury (mTBI) using a three-stimulus auditory oddball task and resting-state recordings. Participants (sub-acute mTBI patients, chronic mTBI patients, and healthy controls) passively listened to standard, novel, and target tones while performing a target detection task. Resting-state blocks with eyes open and eyes closed were also recorded. The P3a and P3b ERP components - reflecting bottom-up and top-down attentional processes - are the primary measures examined as TBI biomarkers.

## File Scan Result

> **Kernel SHA256**: `aa376756639f2ca95904d4b9d34917117ee655424ca06b2435883cb846f5bb2f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Eyes Closed` | 35640 | event | raw | Eyes-closed resting-state block marker |
| `Eyes Open` | 14722 | event | raw | Eyes-open resting-state block marker |
| `Novel Tone` | 11748 | event | raw | Rare novel/distractor tone eliciting P3a |
| `S  4` | 11621 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S  5` | 189 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S  6` | 198 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S  7` | 195 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S  8` | 271 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S  9` | 368 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 10` | 76 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 19` | 1 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 40` | 2 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 46` | 3 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 51` | 1 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 69` | 1 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S 99` | 76 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `S149` | 25 | event | raw | Undocumented stimulus code (requires cross-reference) |
| `Standard Tone` | 11750 | event | raw | Frequent standard auditory tone (non-target) |
| `Target Tone` | 11620 | event | raw | Rare target tone requiring button press (P3b) |
| `admin: response` | 520 | event | raw | Button press response marker |
| `boundary` | 198 | event | raw | HDF5 data boundary marker |


### MISC Label Summary
<not applicable — no MISC channels detected>
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: ERP Target Detection (P300 Binary Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Standard Tone`, `Target Tone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Standard Tone` | 0 | Non-target frequent tone |
  | `Target Tone` | 1 | Target tone requiring button press (P3b) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2019.107125` — Three-stimulus auditory oddball paradigm with P3b (target) as TBI biomarker; same paradigm as dataset, 38 sub-acute, 23 chronic TBI, 24 controls
- **Kernel Notes**: Standard vs target classification isolates P3b response (300–600 ms post-stimulus). Verify event ID mapping from events.tsv. The tmax of 0.8 s captures the full P3b window per alignment recommendations. Baseline correction window should be -0.2 to 0 s for consistent group-level comparison.

### Classical Task 2: Three-Stimulus Oddball Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Standard Tone`, `Novel Tone`, `Target Tone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Standard Tone` | 0 | Standard frequent tone (~80% of trials) |
  | `Novel Tone` | 1 | Novel distractor tone (P3a eliciting, ~10% of trials) |
  | `Target Tone` | 2 | Target tone requiring response (P3b eliciting, ~10% of trials) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2019.107125` — Three-stimulus auditory oddball examining both P3a (novel) and P3b (target) components as TBI biomarkers
- **Kernel Notes**: Class imbalance present (~80% standard, ~10% novel, ~10% target). Use weighted loss or class balancing. Captures both P3a (Novel ~250–350 ms) and P3b (Target ~300–600 ms) components.

### Potential Task 1: Resting-State Classification (Eyes Open vs Closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Eyes Open` | 0 | Eyes-open resting-state block |
  | `Eyes Closed` | 1 | Eyes-closed resting-state block |
- **Evidence**: Plausible from paradigm alone (no specific reference required for Potential classification)
- **Kernel Notes**: Resting-state blocks contain no discrete events for epoching; segmentation creates fixed-length windows. The 4 s segment length with 50% overlap balances frequency resolution (0.25 Hz) with trial count for robust classification of alpha-band differences between eyes-open and eyes-closed conditions. Verify segment boundaries align with block onsets.

### Potential Task 2: P3a Component Isolation (Novel vs Standard Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Standard Tone`, `Novel Tone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Standard Tone` | 0 | Standard frequent tone (non-target) |
  | `Novel Tone` | 1 | Novel distractor tone (P3a eliciting) |
- **Evidence**: Plausible from paradigm alone; P3a component isolation is standard in three-stimulus oddball analysis (no specific reference required for Potential classification)
- **Kernel Notes**: Novel vs standard classification isolates P3a response (~250–350 ms), complementing P3b (target) analysis. Both stimulus-evoked components can be analyzed independently or jointly in the multiclass task.

### Potential Task 3: Clinical Group Classification (TBI Stratification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Standard Tone`, `Novel Tone`, `Target Tone`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sub-acute_mTBI` | 0 | Sub-acute mild TBI patient |
  | `chronic_mTBI` | 1 | Chronic mild TBI patient |
  | `control` | 2 | Healthy control |
- **Evidence**: Supported by paradigm context and reference indicating 3-group design (38 sub-acute, 23 chronic TBI, 24 controls); clinical group labels derived from participant metadata
- **Super Meta Notes**: Clinical group labels are NOT in raw event IDs—they must be parsed from the participant TSV file and mapped to epochs based on subject ID. Verify metadata availability in dataset before implementation.
- **Kernel Notes**: Requires merging participant demographic/clinical data with EEG epochs. Clinical groups should be used as stratification variables. Verify metadata completeness (age, sex fields show as missing in dataset info—confirm available fields in BIDS sidecar).

### Verification Notes
- **Event ID Verification**: Standard Tone (11,750), Novel Tone (11,748), Target Tone (11,620) counts suggest per-subject totals across 62 subjects. Verify event structure in events.tsv to confirm trial counts align with paradigm description (~80% standard, ~10% novel, ~10% target).
- **Undocumented Codes**: The 'S  4'–'S 10' codes (11,621 total) and other S-codes require cross-referencing with stimulus timing files. Current tasks exclude these codes pending verification of their relationship to primary paradigm events.
- **Novel Tone Count Discrepancy**: Novel Tone (11,748) nearly matching Standard Tone (11,750) is atypical for oddball paradigms—verify trial structure to confirm 1:1 pairing is intentional or an artifact.