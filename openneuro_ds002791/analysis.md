# DataSet1 - Visual Object Naming EEG

**Dataset**: `openneuro_ds002791` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002791
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 92 | **Channels**: 256 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed and named visual objects (pictures presented as bitmap images) during high-density 256-channel EEG recording. Each event label is the filename of the presented image (e.g., GLOVE.bmp, GORILLA.bmp), corresponding to 30 distinct visual object categories. The task likely involved overt or covert naming or picture-word matching. This is DataSet1 of a paired dataset series (see also DataSet2: ds002833).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `GLOVE.bmp` | 46 (files) | event | raw | Visual object onset - glove image |
| `FEATHER.bmp` | 46 (files) | event | raw | Visual object onset - feather image |
| `GORILLA.bmp` | 46 (files) | event | raw | Visual object onset - gorilla image |
| `DUSTPAN.bmp` | 46 (files) | event | raw | Visual object onset - dustpan image |
| `COMPASS.bmp` | 46 (files) | event | raw | Visual object onset - compass image |
| `ACCORDIO.bmp` | 46 (files) | event | raw | Visual object onset - accordion image |
| `CAP.bmp` | 46 (files) | event | raw | Visual object onset - cap image |
| `BOTTLE.bmp` | 46 (files) | event | raw | Visual object onset - bottle image |
| `CROWN.bmp` | 46 (files) | event | raw | Visual object onset - crown image |
| `ANCHOR.bmp` | 46 (files) | event | raw | Visual object onset - anchor image |
| `CARROT.bmp` | 46 (files) | event | raw | Visual object onset - carrot image |
| `FORK.bmp` | 46 (files) | event | raw | Visual object onset - fork image |
| `DONKEY.bmp` | 46 (files) | event | raw | Visual object onset - donkey image |
| `EAR.bmp` | 46 (files) | event | raw | Visual object onset - ear image |
| `CLOUD.bmp` | 46 (files) | event | raw | Visual object onset - cloud image |
| `ASHTRAY.bmp` | 46 (files) | event | raw | Visual object onset - ashtray image |
| `frenchcr.bmp` | 46 (files) | event | raw | Visual object onset - french curve image |
| `FISH.bmp` | 46 (files) | event | raw | Visual object onset - fish image |
| `BIRDCAGE.bmp` | 46 (files) | event | raw | Visual object onset - birdcage image |
| `ASPARAGU.bmp` | 46 (files) | event | raw | Visual object onset - asparagus image |
| `DRESS.bmp` | 46 (files) | event | raw | Visual object onset - dress image |
| `BEE.bmp` | 46 (files) | event | raw | Visual object onset - bee image |
| `CHIMNEY.bmp` | 46 (files) | event | raw | Visual object onset - chimney image |
| `BOOT.bmp` | 46 (files) | event | raw | Visual object onset - boot image |
| `CUP.bmp` | 46 (files) | event | raw | Visual object onset - cup image |
| `APPLE.bmp` | 46 (files) | event | raw | Visual object onset - apple image |
| `CRAB.bmp` | 46 (files) | event | raw | Visual object onset - crab image |
| `CAR.bmp` | 46 (files) | event | raw | Visual object onset - car image |
| `ALLIGATO.bmp` | 46 (files) | event | raw | Visual object onset - alligator image |
| `HAMMOCK.bmp` | 46 (files) | event | raw | Visual object onset - hammock image |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Visual Object ERP / Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [see Target Definition]
- **Label Route**: `misc`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | `GLOVE.bmp` | 0 | Visual object - glove |
  | `FEATHER.bmp` | 1 | Visual object - feather |
  | `GORILLA.bmp` | 2 | Visual object - gorilla |
  | `DUSTPAN.bmp` | 3 | Visual object - dustpan |
  | `COMPASS.bmp` | 4 | Visual object - compass |
  | `ACCORDIO.bmp` | 5 | Visual object - accordion |
  | `CAP.bmp` | 6 | Visual object - cap |
  | `BOTTLE.bmp` | 7 | Visual object - bottle |
  | `CROWN.bmp` | 8 | Visual object - crown |
  | `ANCHOR.bmp` | 9 | Visual object - anchor |
  | `CARROT.bmp` | 10 | Visual object - carrot |
  | `FORK.bmp` | 11 | Visual object - fork |
  | `DONKEY.bmp` | 12 | Visual object - donkey |
  | `EAR.bmp` | 13 | Visual object - ear |
  | `CLOUD.bmp` | 14 | Visual object - cloud |
  | `ASHTRAY.bmp` | 15 | Visual object - ashtray |
  | `frenchcr.bmp` | 16 | Visual object - french curve |
  | `FISH.bmp` | 17 | Visual object - fish |
  | `BIRDCAGE.bmp` | 18 | Visual object - birdcage |
  | `ASPARAGU.bmp` | 19 | Visual object - asparagus |
  | `DRESS.bmp` | 20 | Visual object - dress |
  | `BEE.bmp` | 21 | Visual object - bee |
  | `CHIMNEY.bmp` | 22 | Visual object - chimney |
  | `BOOT.bmp` | 23 | Visual object - boot |
  | `CUP.bmp` | 24 | Visual object - cup |
  | `APPLE.bmp` | 25 | Visual object - apple |
  | `CRAB.bmp` | 26 | Visual object - crab |
  | `CAR.bmp` | 27 | Visual object - car |
  | `ALLIGATO.bmp` | 28 | Visual object - alligator |
  | `HAMMOCK.bmp` | 29 | Visual object - hammock |
- **Kernel Notes**: 30 visual object categories. For classification, consider grouping by semantic category (living/nonliving, animate/inanimate) rather than using all 30 individual object identities. High-density 256-channel EEG provides excellent spatial coverage. Regression target: `response_time` (naming latency from misc channel).
- **Notes**: The dataset contains 30 distinct object images presented during a visual object naming task.

## Data Quality Notes

- 30 distinct object images - each present in 46 files (half of 92 total files).
- High-density 256-channel EGI/HydroCell array; verify electrode positions.
- Consider semantic category grouping (animate/inanimate, living/nonliving) for classification.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review