# HID (High-Density EEG Operational Dataset)

**Dataset**: `openneuro_ds004851` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004851
**Category**: Complex Applied | **Subjects**: 65 | **Files (Completed)**: 65 | **Channels**: 72 | **Sampling Rate**: 2048 Hz

## Paradigm

High-density EEG recorded in an operational context involving multiple conditions encoded as 4-digit numeric trigger codes. The code structure suggests stimulus classes (1xxx: classical task events, 7xxx/8xxx: secondary stimulus categories) within a cognitive workload or situational awareness paradigm.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004851.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `8364b7e6f39f75020f9874996e6c688f0a33df4fdd7045cbd00f346c1e91f832`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1010` | 2181 | event | raw | Unresolved from current kernel facts |
| `1011` | 2179 | event | raw | Unresolved from current kernel facts |
| `1020` | 1970 | event | raw | Unresolved from current kernel facts |
| `1021` | 1970 | event | raw | Unresolved from current kernel facts |
| `1040` | 1912 | event | raw | Unresolved from current kernel facts |
| `1041` | 1912 | event | raw | Unresolved from current kernel facts |
| `8100` | 973 | event | raw | Unresolved from current kernel facts |
| `8101` | 973 | event | raw | Unresolved from current kernel facts |
| `1060` | 469 | event | raw | Unresolved from current kernel facts |
| `1061` | 469 | event | raw | Unresolved from current kernel facts |
| `1030` | 204 | event | raw | Unresolved from current kernel facts |
| `1031` | 204 | event | raw | Unresolved from current kernel facts |
| `8010` | 195 | event | raw | Unresolved from current kernel facts |
| `8011` | 195 | event | raw | Unresolved from current kernel facts |
| `8020` | 194 | event | raw | Unresolved from current kernel facts |
| `8021` | 194 | event | raw | Unresolved from current kernel facts |
| `7001` | 65 | event | raw | Unresolved from current kernel facts |
| `7002` | 65 | event | raw | Unresolved from current kernel facts |
| `7003` | 65 | event | raw | Unresolved from current kernel facts |
| `7004` | 65 | event | raw | Unresolved from current kernel facts |
| `7005` | 65 | event | raw | Unresolved from current kernel facts |
| `7006` | 65 | event | raw | Unresolved from current kernel facts |
| `7007` | 65 | event | raw | Unresolved from current kernel facts |
| `7008` | 65 | event | raw | Unresolved from current kernel facts |
| `7009` | 65 | event | raw | Unresolved from current kernel facts |
| `7011` | 65 | event | raw | Unresolved from current kernel facts |
| `7012` | 65 | event | raw | Unresolved from current kernel facts |
| `7013` | 65 | event | raw | Unresolved from current kernel facts |
| `7014` | 65 | event | raw | Unresolved from current kernel facts |
| `8000` | 65 | event | raw | Unresolved from current kernel facts |
| `7010` | 64 | event | raw | Unresolved from current kernel facts |
| `8001` | 64 | event | raw | Unresolved from current kernel facts |
| `7015` | 63 | event | raw | Unresolved from current kernel facts |
| `7016` | 63 | event | raw | Unresolved from current kernel facts |
| `7017` | 63 | event | raw | Unresolved from current kernel facts |
| `7018` | 62 | event | raw | Unresolved from current kernel facts |
| `7019` | 62 | event | raw | Unresolved from current kernel facts |
| `1050` | 15 | event | raw | Unresolved from current kernel facts |
| `1051` | 15 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Publisher-defined BIDS task: HID
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`1010`, `1011`, `1020`, `1021`, `1040`, `1041`, `8100`, `8101`, `1060`, `1061`, `8010`, `8011`, `8020`, `8021`, `7001`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1010` | 0 | Primary event type A |
  | `1011` | 1 | Primary event type A variant |
  | `1020` | 2 | Primary event type B |
  | `1021` | 3 | Primary event type B variant |
  | `1040` | 4 | Primary event type D |
  | `1041` | 5 | Primary event type D variant |
  | `1060` | 6 | Primary event type F |
  | `1061` | 7 | Primary event type F variant |
  | `8100` | 8 | Secondary stimulus category 8, type 1 |
  | `8101` | 9 | Secondary stimulus category 8, type 1 variant |
  | `8010` | 10 | Secondary stimulus |
  | `8011` | 11 | Secondary stimulus |
  | `8020` | 12 | Secondary stimulus |
  | `8021` | 13 | Secondary stimulus |
  | `7001` | 14 | Tertiary stimulus |
- **Evidence**:
  - DOI: 10.18112/openneuro.ds004851.v2.1.0 — OpenNeuro metadata confirms HID task with multi-condition trigger codes
- **Kernel Notes**: Extract epochs aligned to trigger codes. Downsample from 2048 Hz for efficiency. Verify exact epoch timing from dataset README. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very high sampling rate (2048 Hz) - downsample before analysis. Full decode table required from dataset README.


 | Event | y | Meaning |
 |-------|---|---------|
 | `1010` | 0 | Primary event type A |
 | `1011` | 1 | Primary event type A variant |
 | `1020` | 2 | Primary event type B |
 | `1021` | 3 | Primary event type B variant |
 | `1040` | 4 | Primary event type D |
 | `1041` | 5 | Primary event type D variant |
 | `8100` | 6 | Secondary stimulus |
 | `8101` | 7 | Secondary stimulus variant |

## Data Quality Notes

- Very high sampling rate (2048 Hz) - downsample for efficiency.
- 30+ distinct codes; grouping by prefix category recommended.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update