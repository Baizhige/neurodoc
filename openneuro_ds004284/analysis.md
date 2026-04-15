# eeg-neuroforecasting

**Dataset**: `openneuro_ds004284` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004284
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 18 | **Channels**: 129 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A neuroforecasting task that utilizes EEG activity during decision-making or valuation to predict aggregate, population-level outcomes. Participants viewed Kickstarter project presentations and made individual funding decisions while EEG was recorded. The paradigm investigates whether single-trial neural responses can predict both individual choices and aggregate market outcomes (whether projects reached their funding thresholds).

## File Scan Result

> **Kernel SHA256**: `eac9d6792e51fc9ffa699dee052ecfcdd5ed454901455e689faffb72fde7ee69`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `segment` | 17009 | event | raw | Participant's funding decision during Kickstarter project presentation |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Kickstarter Funding Decision Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 4.0, target_events = ["segment"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| segment | fund | Participant chose to fund the Kickstarter project |
| segment | not_funded | Participant did not fund the project |

- **Evidence**: eeg-neuroforecasting repository (preprocessing.py, analysis notebooks) DOI: N/A; Paper: https://doi.org/10.1038/s41598-023-41613-4
- **Kernel Notes**: Segment events (n=17009) serve as epoch anchors. Individual choice labels must be derived from external Kickstarter outcome metadata or annotation channels. Apply bandpass filter (0.5-40 Hz) before epoching per data quality notes. Verify 129-channel consistency across 18 subjects.

### Classical Task 2: Aggregate Funding Outcome Prediction (Neuroforecasting)
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 4.0, target_events = ["segment"]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| segment | deal_success (continuous) | Aggregate Kickstarter funding outcome (0-1 normalized or binary threshold at funding goal) |

- **Evidence**: https://doi.org/10.1038/s41598-023-41613-4 (Single-trial VEPs predict both individual choice and market outcomes; "EEG predicts whether products reached funding threshold")
- **Kernel Notes**: Super-meta labels require derivation from external dataset documentation or aggregated Kickstarter platform data. Derive and version super-meta in kernel with reproducible schema. This task operationalizes the core neuroforecasting paradigm: using EEG activity during decision-making to predict population-level outcomes.

### Potential Task 1: Entrepreneur Fundraising Success Prediction
- **Task Type**: classification/regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 4.0, target_events = ["segment"]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| segment | deal_success | Whether the entrepreneurial pitch reached its investment/funding threshold |
| segment | investment_amount | Continuous investment amount raised |

- **Evidence**: https://doi.org/10.1371/journal.pone.0340606 (Partial support; "EEG predicts population-level investment interest and deal outcomes"; dataset from OSF, not OpenNeuro)
- **Kernel Notes**: Partial reference support only; task is plausible from paradigm alignment (neuroforecasting/fundraising domain). Requires verification of outcome labels from dataset documentation.