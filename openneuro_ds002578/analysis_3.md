# Visual Attention Task (256 channels)

**Dataset**: `openneuro_ds002578` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002578  
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2 | **Channels**: 256 | **Sampling Rate**: 256 Hz

---

## Paradigm

This dataset contains a visual attention task with stimulus presentation and behavioral responses, recorded using high-density 256-channel EEG.

Event information is present in both EEG annotations and BIDS `events.tsv` files. However, semantic labeling of events is incomplete:

- The `trial_type` column is empty
- Event meanings are not explicitly standardized
- Raw event markers include stimulus-related and response-related signals

Therefore, while the dataset supports stimulus–response paradigms, the specific classification as a "visual oddball task" is not directly verifiable from the available event annotations alone.

---

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract raw event markers from EEG annotations and `events.tsv`
- **Type 2 (Raw + Super meta integration)**: Required if semantic mapping (e.g., target vs standard) is needed
- **Type 3 (Label-route orchestration)**: Route extracted labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`)

> **Selected Mode**: Type 1 + Type 3  
> **Why**: Raw event markers are present and can be extracted; semantic mapping is not directly available  
> **Primary Label Routes**: Annotation  
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002578

---

## Event Structure

| Event ID | Count (approx) | Type | Meta Level | Meaning |
|----------|----------------|------|------------|---------|
| `Picture` | ~2300 | short | raw | Visual stimulus presentation |
| `Response` | ~2300 | short | raw | Behavioral response |
| `31–45`, `203`, `217`, `237` | multiple | short | raw | Trigger codes (semantics unknown) |
| `boundary` | few | admin | raw | Data discontinuity marker |

### Notes

- Event markers are present in both EEG annotations and `events.tsv`
- Total events per file: ~4678–4679
- `trial_type` column is empty → no high-level labels
- `value` column likely contains trigger codes
- `stim_file` contains stimulus file references
- `response_time` provides behavioral timing information

> **Event Type Definitions**  
> - `short`: discrete events (stimulus or response)  
> - `admin`: system markers (e.g., `boundary`, should be excluded from modeling)

---

## Tasks

### Primary Task 1: Stimulus–Response Reaction Time Modeling (Derived)

- **Task Type**: regression / classification (optional)
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s
- **Label Route**: Annotation
- **Meta Level**: super

#### Description

Reaction time can be derived using:

- stimulus events (`Picture`)
- response events (`Response`)
- `response_time` column (if valid)

#### Notes

- Requires mapping between stimulus and subsequent response
- Event pairing logic must be implemented explicitly
- No explicit `target` / `oddball` labels available

---

### Normal Task 1: Continuous Segmentation

- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: Annotation

#### Notes

- Suitable fallback due to lack of standardized event labels
- Can be applied across full continuous EEG recording

---

## Data Quality Notes

- Only 2 EEG files available → extremely limited dataset size
- High-density 256-channel EEG
- Event markers exist but lack semantic labeling (`trial_type` empty)
- Presence of `boundary` events indicates discontinuities in the data
- Trigger codes (`value`) require external mapping for interpretation

---

## References

- **Reference**: `Visual Attention Task (256 channels)`
