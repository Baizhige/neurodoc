# Visual Attention Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002578  
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz

---

## Paradigm

This dataset contains a visual stimulus–response task recorded using high-density 256-channel EEG.

Event markers are present in both EEG annotations and BIDS `events.tsv` files. However, semantic labeling is largely missing:

- `trial_type` is completely empty
- `stim_file` is empty
- `response_time` is empty

As a result, high-level experimental structure (e.g., target vs standard, oddball paradigm) cannot be directly verified from the dataset.

---

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract raw event markers from annotations and `events.tsv`
- **Type 2 (Raw + Super meta integration)**: Required for reconstructing semantic labels
- **Type 3 (Label-route orchestration)**: Route extracted labels to EEGUnity-compatible channels

> **Selected Mode**: Type 1 + Type 3  
> **Why**: Raw markers exist but lack semantic mapping  
> **Primary Label Routes**: Annotation  

---

## Event Structure

| Event ID | Count (approx) | Type | Meta Level | Meaning |
|----------|----------------|------|------------|---------|
| `Picture` | ~2970 | short | raw | Visual stimulus event |
| `Response` | ~600 | short | raw | Behavioral response |
| `31–45` | ~120 each | short | raw | Trigger codes (unknown semantics) |
| `203`, `217`, `237` | rare | short | raw | Rare trigger events |
| `boundary` | ~29 | admin | raw | Recording discontinuity |

### Notes

- Total events per file: ~4678–4679
- `trial_type`, `stim_file`, `response_time` are all empty
- `value` column contains all usable event information
- Semantic interpretation requires external mapping

---

## Tasks

### Normal Task: Continuous Segmentation

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Parameters**: segment_length = 2.0 s, overlap = 0.5

### Optional Task: Stimulus–Response Pairing (Requires Reconstruction)

- Requires:
  - pairing `Picture` → `Response`
  - decoding trigger codes (`31–45`)
- Not directly supported by dataset metadata

---

## Data Quality Notes

- Only 2 EEG files → extremely small dataset
- High-density (256 channels)
- Event markers present but **no semantic labels**
- `response_time` not recorded
- `stim_file` not recorded
- Presence of `boundary` events (discontinuities)
- Trigger codes require manual decoding

---

## References

- **Reference**: `Visual Attention Task (256 channels)`
