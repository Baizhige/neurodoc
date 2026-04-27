# EEG During Sport-Related Motor Imagery and Observation Tasks

**Dataset**: `openneuro_ds007327` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007327
**Category**: Action/Output | **Subjects**: 35 | **Files (Completed)**: 105 | **Channels**: 88 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

EEG was recorded during two sports-related tasks (ball passing and dribbling) to study motor intention and motor observation. The paradigm uses a 2x2 design crossing motor intention (MI = motor intention, MO = motor observation) with movement execution modality, yielding four compound conditions: MIMI (imagine intention), MIMO (imagine observation), MOMI (observe intention), MOMO (observe observation). Additional single-factor conditions (MI, MO, MO_MI) and a static/rest baseline are included.

## File Scan Result

> **Kernel SHA256**: `6ba1ab7c5348ae377d6004db997113952440f2d3adfcf6435db90c82db8f1370`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `A11` | 4200 | event | raw | MO — Pure motor observation condition |
| `A22` | 4195 | event | raw | MI — Pure motor intention condition |
| `A44` | 4073 | event | raw | Rest baseline condition |
| `A66` | 4313 | event | raw | Static baseline condition |
| `A88` | 4198 | event | raw | MO_MI — Motor observation combined with motor intention |
| `A98` | 2100 | event | raw | Administrative/sub-run marker (excluded from analysis) |
| `A99` | 421 | event | raw | Administrative marker (excluded from analysis) |
| `B12` | 4196 | event | raw | MIMO — Motor imagination of observation (dribble task) |
| `B14` | 4198 | event | raw | MOMI — Motor observation of intention (dribble task) |
| `B16` | 4197 | event | raw | MOMO — Motor observation of observation (dribble task) |
| `B18` | 4197 | event | raw | MIMI — Motor imagination of intention (dribble task) |
| `B22` | 4195 | event | raw | Administrative marker |
| `B44` | 4194 | event | raw | Rest baseline (dribble task) |
| `B66` | 4194 | event | raw | Static baseline (dribble task) |
| `B88` | 4197 | event | raw | MO_MI baseline (dribble task) |
| `B96` | 2801 | event | raw | Sub-trial/segment marker (investigate before use) |
| `B98` | 2800 | event | raw | Sub-trial/segment marker (investigate before use) |
| `B99` | 19596 | event | raw | Boundary/segmentation marker (excluded from analysis) |
| `C12` | 4198 | event | raw | MIMO — Motor imagination of observation (passing task) |
| `C14` | 4198 | event | raw | MOMI — Motor observation of intention (passing task) |
| `C16` | 4197 | event | raw | MOMO — Motor observation of observation (passing task) |
| `C18` | 4138 | event | raw | MIMI — Motor imagination of intention (passing task) |
| `C22` | 4197 | event | raw | Administrative marker |
| `C44` | 4193 | event | raw | Rest baseline (passing task) |
| `C66` | 4194 | event | raw | Static baseline (passing task) |
| `C88` | 4135 | event | raw | MO_MI baseline (passing task) |
| `C96` | 2793 | event | raw | Sub-trial/segment marker (investigate before use) |
| `C98` | 2793 | event | raw | Sub-trial/segment marker (investigate before use) |
| `C99` | 19526 | event | raw | Boundary/segmentation marker (excluded from analysis) |
| `Impedance` | 912 | event | raw | Impedance check marker (administrative, excluded) |
| `boundary` | 806 | event | raw | EDF boundary marker (administrative, excluded) |


### MISC Label Summary
*MISC section not applicable — no misc channels detected in this dataset.*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

> **No Classical Tasks identified**: The reference extraction returned zero entries with `classification=relevant`. All tasks below are derived from paradigm structure and the dataset landing page.

---

### Normal Task 1: 4-Class 2×2 Motor Intention × Observation Classification

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 4.0 s`, `baseline = (-0.2, 0)`, `target_events = [B12, B14, B16, B18, C12, C14, C16, C18]`
- **Label Route**: `event`
- **Meta Level**: `raw`

#### Target Definition

| Event | y | Meaning |
|---|---|---|
| `B18` | 0 | MIMI — Motor imagination of intention (dribble task) |
| `B12` | 1 | MIMO — Motor imagination of observation (dribble task) |
| `B14` | 2 | MOMI — Motor observation of intention (dribble task) |
| `B16` | 3 | MOMO — Motor observation of observation (dribble task) |
| `C18` | 0 | MIMI — Motor imagination of intention (passing task) |
| `C12` | 1 | MIMO — Motor imagination of observation (passing task) |
| `C14` | 2 | MOMI — Motor observation of intention (passing task) |
| `C16` | 3 | MOMO — Motor observation of observation (passing task) |

#### Evidence

- https://openneuro.org/datasets/ds007327 — Dataset landing page describes a 2×2 factorial design crossing motor intention (MI) with motor observation (MO) during sport tasks (dribble, passing). The four compound conditions MIMI/MIMO/MOMI/MOMO are the primary experimental contrasts (~8300–8400 trials per condition across all files). B-series and C-series prefixes inferred to correspond to dribble and passing task files respectively based on count alignment: B18+C18 ≈ 8335 (MIMI), B12+C12 ≈ 8394 (MIMO), B14+C14 ≈ 8396 (MOMI), B16+C16 ≈ 8394 (MOMO). No peer-reviewed paper with explicit relevance classification was available at extraction time.

#### Kernel Notes

- **CRITICAL — Raw event code mapping**: The EDF files contain raw alphanumeric codes (A11, B12, …) not the semantic labels (MIMI, MIMO, MOMI, MOMO) described in the paradigm. A super-metadata mapping layer must be established before epoching. The mapping inferred here is based on count-matching between semantic totals and per-series raw counts.
- **Alignment assumption**: cue ONSET. tmin = -0.2 s captures pre-stimulus baseline; tmax = 4.0 s covers the full 3–4 s motor intention/observation window.
- **Task-series assignment**: B-series events (B12/B14/B16/B18) appear in dribble task files; C-series events (C12/C14/C16/C18) appear in passing task files. Pool both series using identical y-labels for cross-sport generalisation. Separate sport-specific models are also viable.
- **Exclude**: `B99` (~19 596), `C99` (~19 526) — high-count boundary/segmentation markers. `B96`, `B98`, `C96`, `C98` (~2 800 each) — likely sub-trial or intra-run segment markers; investigate before including. `Impedance` (912), `boundary` (806) — administrative markers, exclude.
- **Channel exclusion**: Remove all 24 BIP channels before epoching (EMG/kinematic signals, not EEG).
- **Recommended preprocessing**: bandpass 0.5–40 Hz → BIP removal → artifact rejection → epoch.
- **Label verification required**: Confirm B18↔MIMI, B12↔MIMO, B14↔MOMI, B16↔MOMO via dataset README, BIDS `events.tsv`, or author contact before releasing labels.

---

### Normal Task 2: 3-Class Single-Factor Motor Condition Classification (A-Series)

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 4.0 s`, `baseline = (-0.2, 0)`, `target_events = [A11, A22, A88]`
- **Label Route**: `event`
- **Meta Level**: `raw`

#### Target Definition

| Event | y | Meaning |
|---|---|---|
| `A22` | 0 | MI — Pure motor intention condition |
| `A11` | 1 | MO — Pure motor observation condition |
| `A88` | 2 | MO_MI — Motor observation combined with motor intention |

#### Evidence

- https://openneuro.org/datasets/ds007327 — A-series events (A11 ≈ 4 200, A22 ≈ 4 195, A88 ≈ 4 198) match the single-factor conditions MO, MI, MO_MI described in the paradigm (count-matched). A-series appears in a third sport task file (likely ball-passing baseline task). These single-factor conditions support a 3-class decoding benchmark contrasting pure motor intention, pure motor observation, and their combination.

#### Kernel Notes

- **Alignment assumption**: cue ONSET. Same epoch window as Normal Task 1 for direct comparability.
- **A66** (4 313, static baseline) and **A44** (4 073, rest) are available for baseline-vs-active contrasts but are excluded from this 3-class active-conditions task.
- **A98** (~2 100) and **A99** (~421) have atypical counts; treat as administrative/boundary markers and exclude unless confirmed as trial events.
- If sport-task identity of A-series files can be confirmed (e.g., via BIDS `task-` field), stratify by sport task as a covariate.
- Same BIP-removal and bandpass preprocessing as Normal Task 1 applies.

---

### Potential Task 1: Binary Motor Imagery vs. Motor Observation Decoding

- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s`, `tmax = 4.0 s`, `baseline = (-0.2, 0)`, `target_events = [B18, B12, C18, C12, B14, B16, C14, C16]`
- **Label Route**: `event`
- **Meta Level**: `super`

#### Target Definition

| Event | y | Meaning |
|---|---|---|
| `B18` | 0 | Motor IMAGINATION trial (MIMI — dribble) |
| `B12` | 0 | Motor IMAGINATION trial (MIMO — dribble) |
| `C18` | 0 | Motor IMAGINATION trial (MIMI — passing) |
| `C12` | 0 | Motor IMAGINATION trial (MIMO — passing) |
| `B14` | 1 | Motor OBSERVATION trial (MOMI — dribble) |
| `B16` | 1 | Motor OBSERVATION trial (MOMO — dribble) |
| `C14` | 1 | Motor OBSERVATION trial (MOMI — passing) |
| `C16` | 1 | Motor OBSERVATION trial (MOMO — passing) |

#### Evidence

- No direct paper evidence. Task is plausible from the 2×2 factorial paradigm: collapsing across the intention/observation sub-factor yields a binary imagery (MIMI + MIMO) vs. observation (MOMI + MOMO) contrast — a classical BCI-relevant decoding problem. This is a standard derived binary contrast for motor imagery datasets of this type.

#### Kernel Notes

- **Meta Level = super**: y-labels are not directly encoded in raw events; they require collapsing across the intention sub-factor. A super-metadata derivation step is mandatory. Map {B18, B12, C18, C12} → y=0 (imagination) and {B14, B16, C14, C16} → y=1 (observation).
- **Label verification**: This mapping is only valid if B18/C18 = MIMI and B12/C12 = MIMO (imagination conditions) and B14/C14 = MOMI and B16/C16 = MOMO (observation conditions). Confirm raw-to-semantic mapping before releasing super labels.
- **Class balance**: Each binary class will contain ~16 700–16 800 trials pooled across both sport tasks, yielding near-perfect balance.
- **Alternative**: A11 (MO) vs A22 (MI) from the A-series provides a clean single-factor binary MI vs. MO contrast with ~4 200 trials per class and may be preferable for a simpler benchmark.