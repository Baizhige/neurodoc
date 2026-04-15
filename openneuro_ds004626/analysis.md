# Can We Dissociate Hypervigilance to Social Threats from Altered Perceptual Decision-Making in Lonely Individualsx

**Dataset**: `openneuro_ds004626` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004626
**Category**: High-level Mental | **Subjects**: 52 | **Files (Completed)**: 52 | **Channels**: 68 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A perceptual decision-making task investigating whether lonely individuals exhibit hypervigilance toward social threats, combining Drift Diffusion Modeling (DDM) with ERP analysis. Participants viewed social and non-social threat stimuli and made rapid perceptual judgements. ERP components (P1, N2pc, LPP) and computational decision parameters were compared across loneliness severity groups.

## File Scan Result

> **Kernel SHA256**: `63c179bb4b542a79ddffe7b5726901bbab96bf18c5677bb5bbbbce6f6b7f5c3e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 5 | event | raw | Unknown/miscellaneous trigger |
| `132` | 1560 | event | raw | Stimulus/condition trigger code |
| `135` | 1560 | event | raw | Stimulus/condition trigger code |
| `143` | 1 | event | raw | Stimulus/condition trigger code |
| `144` | 1560 | event | raw | Stimulus/condition trigger code |
| `145` | 1560 | event | raw | Stimulus/condition trigger code |
| `151` | 1560 | event | raw | Stimulus/condition trigger code |
| `159` | 1560 | event | raw | Stimulus/condition trigger code |
| `160` | 363 | event | raw | Stimulus/condition trigger code |
| `167` | 1560 | event | raw | Stimulus/condition trigger code |
| `175` | 1560 | event | raw | Stimulus/condition trigger code |
| `176` | 1560 | event | raw | Stimulus/condition trigger code |
| `183` | 1560 | event | raw | Stimulus/condition trigger code |
| `184` | 1560 | event | raw | Stimulus/condition trigger code |
| `191` | 1560 | event | raw | Stimulus/condition trigger code |
| `192` | 118 | event | raw | Stimulus/condition trigger code |
| `199` | 1560 | event | raw | Stimulus/condition trigger code |
| `200` | 219 | event | raw | Stimulus/condition trigger code |
| `207` | 1560 | event | raw | Stimulus/condition trigger code |
| `209` | 1560 | event | raw | Stimulus/condition trigger code |
| `215` | 1560 | event | raw | Stimulus/condition trigger code |
| `216` | 1560 | event | raw | Stimulus/condition trigger code |
| `223` | 1560 | event | raw | Stimulus/condition trigger code |
| `224` | 487 | event | raw | Stimulus/condition trigger code |
| `231` | 1560 | event | raw | Stimulus/condition trigger code |
| `239` | 1560 | event | raw | Stimulus/condition trigger code |
| `240` | 1 | event | raw | Unknown/miscellaneous trigger |
| `248` | 1560 | event | raw | Stimulus/condition trigger code |
| `251` | 1560 | event | raw | Stimulus/condition trigger code |
| `300` | 1528 | event | raw | Response/completion trigger code |
| `admin_sync` | 1560 | event | raw | Sync/administrative marker (exclude from analysis) |
| `admin_trial_end` | 2363 | admin | raw | Trial-end marker (exclude) |
| `response_button_press` | 36977 | event | raw | Button press response |
| `stim_condition_A` | 6239 | event | raw | Stimulus condition A (face emotion/probe position combination) |
| `stim_condition_B` | 6238 | event | raw | Stimulus condition B (face emotion/probe position combination) |
| `stim_condition_C` | 6238 | event | raw | Stimulus condition C (face emotion/probe position combination) |
| `stim_condition_D` | 6240 | event | raw | Stimulus condition D (face emotion/probe position combination) |
| `stim_condition_E` | 6237 | event | raw | Stimulus condition E (face emotion/probe position combination) |
| `stim_condition_F` | 6233 | event | raw | Stimulus condition F (face emotion/probe position combination) |
| `trial_boundary_ITI` | 35001 | event | raw | Inter-trial interval/trial boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Loneliness Group Classification (Social Threat Hypervigilance)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`stim_condition_A`, `stim_condition_B`, `stim_condition_C`, `stim_condition_D`, `stim_condition_E`, `stim_condition_F`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | All stimulus conditions | 0 | Non-lonely control group (n=26) |
  | All stimulus conditions | 1 | Lonely group (n=26) |
- **Evidence**:
  - DOI: 10.1111/psyp.14406 — Analysis of 52 participants performing dot-probe task with angry/neutral face stimuli, comparing lonely (n=26) vs non-lonely (n=26) groups based on UCLA Loneliness Scale scores. N2pc ERP components extracted in 700ms epochs (tmin=-0.2s, tmax=0.5s) and DDM parameters (drift rate, boundary separation) used to assess social threat hypervigilance differences between groups.
- **Kernel Notes**: Super-meta labels (lonely vs non-lonely) derived from UCLA Loneliness Scale scores, not from event codes. Stimulus condition events (A-F) encode face emotion and probe position combinations—verify events.tsv for full decode table. Exclude admin_sync and admin_trial_end markers. (replaces Stimulus Trigger Classification from original analysis.md)

### Potential Task 1: Stimulus Condition Classification (Face Emotion/Probe Position)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`stim_condition_A`, `stim_condition_B`, `stim_condition_C`, `stim_condition_D`, `stim_condition_E`, `stim_condition_F`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--- |---------|
  | `stim_condition_A` | 0 | Stimulus condition A (e.g., angry face, left position) |
  | `stim_condition_B` | 1 | Stimulus condition B (e.g., angry face, right position) |
  | `stim_condition_C` | 2 | Stimulus condition C (e.g., neutral face, left position) |
  | `stim_condition_D` | 3 | Stimulus condition D (e.g., neutral face, right position) |
  | `stim_condition_E` | 4 | Stimulus condition E (e.g., congruent angry face) |
  | `stim_condition_F` | 5 | Stimulus condition F (e.g., congruent neutral face) |
- **Evidence**: Dot-probe paradigm with 6 distinct stimulus condition codes (n~37400 total). Each condition likely encodes face emotion × probe position combination. N2pc component analysis requires distinguishing congruent vs incongruent trials to assess attentional bias. Extends tmax to 0.8s for LPP component capture per epoch alignment recommendations.
- **Kernel Notes**: Full decode table mapping stimulus conditions to face emotion (angry/neutral) and probe position (left/right) requires verification from events.tsv. Condition counts are balanced (~6237-6240 each), confirming experimental design structure.

### Potential Task 2: Response-Related ERP Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`response_button_press`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--- |---------|
  | `response_button_press` | 0 | Button press response |
- **Evidence**: Response-aligned epochs (n=36977) enable RT analysis and motor response ERP components. Difference of ~400 between response count and stimulus count suggests anticipatory responses or missed trials. DDM analysis uses RT distributions to estimate drift rate and boundary separation parameters.
- **Kernel Notes**: Button press epochs allow examination of motor preparation and execution differences between loneliness groups. RT distribution analysis supports DDM parameter estimation.